# -*- coding: utf-8 -*-
"""둘째 판 장별 파견문 생성기.

사용: python _gen_장v2_파견문.py <spec.json> [--out 파견/장v2_N_파견문.md] [--check]

spec.json의 꼴:
{
  "chapter": 6, "title": "첫 층의 추정",
  "scope": "이 장이 글에서 하는 일(두세 문장)",
  "weights": "이 장 안의 무거운 것·가벼운 것(경중 배분)",
  "sections": [
    {"sec": "6.1", "title": "첫 층 생존의 상계", "intro": "(선택) 절의 특별 지시",
     "items": [
       {"label": "{{6:old-7-13}}", "kind": "정리", "name": "첫 층 생존의 상계", "record_name": "기록 [r7e03176]의 정리 F′",
        "process": "전개", "class": "고비",
        "sources": [{"record": "r7e03176", "file": "exposition.md", "sec": "8.3", "note": "정리 F′의 진술과 증명"},
                    {"record": "r1aa0be6", "file": "evidence/producer/output/critical-local-limit.md", "range": [40, 90]}],
        "first_edition": {"file": "원고.md", "range": [2483, 2487], "note": "첫 판 7.13"},
        "inputs": ["{{2:old-2-32}}"],
        "special": "..."}
     ]}
  ],
  "defines": ["이 장이 처음 정의하는 글자와 낱말(장부 v2 5절의 배정)"],
  "free_letters": ["여유 글자"],
  "refs": ["이 장이 가리킬 다른 장의 라벨"],
  "todo": [{"where": "8.2 정리 W 증명의 둘째 단계", "statement": "...", "fill": "..."}],
  "D_items": [{"label": "{{D:...}}", "for": "{{8:old-6-28}}", "sources": [...]}],
  "notes": ["특별 지시"]
}
sources의 좌표는 "range": [a, b](행) 또는 "sec": "8.3" / "2.1–2.2" / "4″.3" / "7"(절 번호; 머리 `## 7.`·`### 8.3`을 찾아
그 절의 끝(같은 급 이상의 다음 머리 전)까지로 푼다). 기록 발췌는 exposition.md(또는 지정 파일)의 행 범위를 축자로 싣는다.
first_edition의 file은 ROOT 기준 경로(`원고.md` 또는 `장/장7.md`)다.
--check는 파견문을 쓰지 않고 좌표 해소 결과만 출력한다.
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RECORDS = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
COMMON = r"C:\math\임시\주차함수_증명\파견\집필_공통지침_v2.md"


def find_record_dir(prefix):
    for name in os.listdir(RECORDS):
        if name.startswith(prefix):
            return os.path.join(RECORDS, name)
    raise FileNotFoundError(prefix)


def read_lines(path):
    return io.open(path, encoding="utf-8").read().split("\n")


HEADER_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*$")
NUM_RE = re.compile(r"^([0-9]+(?:[′″‴]?)(?:\.[0-9]+)*)[.\s)]")


def headers(lines):
    """(행, 급, 절 번호 문자열 또는 None, 제목) 목록."""
    out = []
    for i, ln in enumerate(lines, 1):
        m = HEADER_RE.match(ln)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2)
        n = NUM_RE.match(title + " ")
        num = n.group(1) if n else None
        out.append((i, level, num, title))
    return out


def norm(sec):
    return sec.replace("'", "′").replace("''", "″").strip()


def resolve_sec(lines, sec):
    """절 번호(예 '8.3', '7', '4″.3', '2.1–2.2')를 [start, end] 행으로 푼다. 실패하면 None."""
    sec = norm(sec)
    if "–" in sec or "-" in sec:
        a, b = re.split(r"[–-]", sec, 1)
        a, b = a.strip(), b.strip()
        if "." in a and "." not in b:
            b = a.rsplit(".", 1)[0] + "." + b
        ra = resolve_sec(lines, a)
        rb = resolve_sec(lines, b)
        if ra and rb:
            return [ra[0], rb[1]]
        return ra or rb
    hs = headers(lines)
    for idx, (ln, level, num, title) in enumerate(hs):
        if num is not None and norm(num) == sec:
            end = len(lines)
            for ln2, level2, num2, title2 in hs[idx + 1:]:
                if level2 <= level:
                    end = ln2 - 1
                    break
            while end > ln and not lines[end - 1].strip():
                end -= 1
            return [ln, end]
    # 굵은 글씨 머리(**3.2 …**)도 시도
    pat = re.compile(r"^\*\*" + re.escape(sec) + r"[.\s]")
    for i, ln in enumerate(lines, 1):
        if pat.match(ln):
            end = len(lines)
            for j in range(i, len(lines)):
                if HEADER_RE.match(lines[j]) or re.match(r"^\*\*[0-9]", lines[j]):
                    end = j
                    break
            return [i, end]
    return None


def excerpt(path, rng):
    lines = read_lines(path)
    a, b = rng
    a = max(1, a)
    b = min(len(lines), b)
    body = "\n".join(lines[a - 1:b])
    return a, b, body


def source_path(s):
    rdir = find_record_dir(s["record"])
    return os.path.join(rdir, s.get("file", "exposition.md"))


def source_range(s, path):
    if s.get("range"):
        return list(s["range"]), "range"
    if s.get("sec"):
        r = resolve_sec(read_lines(path), s["sec"])
        return r, ("sec" if r else "unresolved")
    return None, "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--part", help="장을 나누어 쓸 때의 조각 글자(A, B, …)")
    ap.add_argument("--sections", help="--part와 함께: 이 조각이 맡는 절 번호(쉼표 구분, 예 5.1,5.2,5.3,5.4)")
    args = ap.parse_args()
    spec = json.load(io.open(args.spec, encoding="utf-8"))
    ch = spec["chapter"]
    part = args.part or ""
    if part:
        if not args.sections:
            raise SystemExit("--part에는 --sections가 필요하다")
        wanted = [x.strip() for x in args.sections.split(",")]
        spec["sections"] = [s for s in spec["sections"] if s["sec"] in wanted]
        kept = {s["sec"] for s in spec["sections"]}
        lost = [w for w in wanted if w not in kept]
        if lost:
            raise SystemExit(f"명세에 없는 절: {lost}")
        labels_here = {it["label"] for s in spec["sections"] for it in s["items"]}
        spec["todo"] = [t for t in spec.get("todo", []) if any(l in t.get("where", "") for l in labels_here) or any(s["sec"] in t.get("where", "") for s in spec["sections"])]
        spec["D_items"] = [d for d in spec.get("D_items", []) if d.get("for") in labels_here]
    tag = f"{ch}{part}"
    out_path = args.out or os.path.join(ROOT, "파견", f"장v2_{tag}_파견문.md")

    problems = []
    if args.check:
        for sec in spec["sections"]:
            for it in sec["items"]:
                for s in it.get("sources", []):
                    if not s.get("record"):
                        problems.append(f"{it['label']}: record 없음 ({s})")
                        continue
                    try:
                        path = source_path(s)
                    except FileNotFoundError:
                        problems.append(f"{it['label']}: 기록 폴더 없음 {s['record']}")
                        continue
                    if not os.path.exists(path):
                        problems.append(f"{it['label']}: 파일 없음 {path}")
                        continue
                    rng, how = source_range(s, path)
                    print(f"{it['label']:34s} [{s['record']}] {s.get('file','exposition.md')} {s.get('sec') or s.get('range')} -> {rng} ({how})")
                    if not rng:
                        problems.append(f"{it['label']}: 좌표 미해소 {s}")
                fe = it.get("first_edition")
                if fe and fe.get("range") is None:
                    problems.append(f"{it['label']}: first_edition range 없음")
        print("\n문제:", len(problems))
        for p in problems:
            print(" -", p)
        return 0

    L = []
    if part:
        secs = ", ".join(s["sec"] for s in spec["sections"])
        L.append(f"# 파견문: 둘째 판 {ch}장 「{spec['title']}」의 집필 — 조각 {part}({secs}절)\n")
        L.append("## 임무와 목적\n")
        L.append(f"`C:\\math\\임시\\주차함수_증명\\장v2\\장{tag}.md`에 둘째 판 {ch}장 가운데 {secs}절을 쓴다. 이 장은 길어서 조각으로 나누어 쓰며, 다른 조각은 다른 에이전트가 같은 공통 계약과 같은 사전으로 쓴다. 조립 스크립트가 조각을 글자 순으로 이어 한 장으로 만든다. 장 머리 `## {ch}. {spec['title']}`는 조각 A만 적고, 다른 조각은 첫 절 머리 `### {ch}.m 제목`으로 시작한다. 같은 장의 다른 조각에 있는 진술은 라벨로 가리킨다(아래 「이 장이 가리키는 다른 장의 라벨」에 더해 이 장의 다른 조각 라벨도 쓸 수 있다). 공통 계약은 `{COMMON}`이고, 이 파견문은 이 조각의 범위·출처·발췌·특별 지시를 담는다. 둘이 충돌하면 이 파견문이 이긴다. 공통 지침을 먼저 전문으로 읽는다. 공통 지침의 산출물 이름에서 `장{ch}`를 `장{tag}`로 읽는다(`장v2/장{tag}.md`, `장v2/부록D_장{tag}.md`, `대조v2/장{tag}_집필대조.md`).\n")
    else:
        L.append(f"# 파견문: 둘째 판 {ch}장 「{spec['title']}」의 집필\n")
        L.append("## 임무와 목적\n")
        L.append(f"`C:\\math\\임시\\주차함수_증명\\장v2\\장{ch}.md`에 둘째 판 {ch}장 전체를 쓴다. 공통 계약은 `{COMMON}`이고, 이 파견문은 그 장의 범위·출처·발췌·특별 지시를 담는다. 둘이 충돌하면 이 파견문이 이긴다. 공통 지침을 먼저 전문으로 읽는다.\n")
    L.append(spec.get("scope", "") + "\n")
    L.append("## 수신 컨텍스트\n")
    L.append("파견문 밖의 대화는 전달되지 않는다. 읽을 파일은 공통 지침 3절과 아래 발췌의 좌표다. 연구 인스턴스는 읽기만 한다. `C:\\math\\CLAUDE.md`, `C:\\math\\.claude\\`, `C:\\math\\.agents\\`를 열지 않는다.\n")
    L.append("## 이 장의 경중\n")
    L.append(spec.get("weights", "") + "\n")
    L.append("## 절과 진술\n")
    L.append("처리의 낱말: 옮김(첫 판 문장을 둘째 판 규칙으로 고쳐 씀), 전개(기록에서 모든 단계를 새로 씀), 작성자 증명(기록에도 없는 증명을 씀; 지침 4.4), 부록 D(계산 명세를 부록 D 조각으로). 분류: 표준/기계적/새로운 것/고비(지침 4.8).\n")
    for sec in spec["sections"]:
        L.append(f"### {sec['sec']} {sec.get('title','')}\n")
        if sec.get("intro"):
            L.append(sec["intro"] + "\n")
        L.append("| 라벨 | 종류 | 이름(기록 이름) | 처리 | 분류 | 입력(라벨) | 출처 좌표 | 특별 지시 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for it in sec["items"]:
            name = it.get("name", "")
            if it.get("record_name"):
                name += f"; {it['record_name']}"
            coords = []
            for s in it.get("sources", []):
                coords.append(f"[{s['record']}] `{s.get('file','exposition.md')}` §{s['sec']}" if s.get("sec") else f"[{s['record']}] `{s.get('file','exposition.md')}` {s.get('range')}행")
            fe = it.get("first_edition")
            if fe and fe.get("range"):
                coords.append(f"첫 판 `{fe['file']}` {fe['range'][0]}–{fe['range'][1]}행")
            L.append(f"| `{it['label']}` | {it.get('kind','')} | {name} | {it.get('process','')} | {it.get('class','')} | {', '.join('`'+r+'`' for r in it.get('inputs', []))} | {'; '.join(coords)} | {it.get('special','')} |")
        L.append("")
    L.append("## 이 장이 정의하는 글자와 낱말(장부 v2 5절)\n")
    L.append("\n".join(f"- {d}" for d in spec.get("defines", [])) + "\n")
    L.append("## 여유 글자\n")
    L.append(", ".join(spec.get("free_letters", [])) + "\n")
    L.append("## 이 장이 가리키는 다른 장의 라벨\n")
    L.append(", ".join(f"`{r}`" for r in spec.get("refs", [])) + "\n")
    if spec.get("todo"):
        L.append("## 자리 표시자(지침 4.7)\n")
        for t in spec["todo"]:
            L.append(f"- 자리: {t['where']}. 필요한 진술: {t['statement']}. 채움 조건: {t['fill']}.")
        L.append("")
    if spec.get("D_items"):
        L.append("## 부록 D 항목(지침 4.5·7.6)\n")
        L.append("| D 라벨 | 확인하는 진술 | 명세의 출처 |")
        L.append("|---|---|---|")
        for d in spec["D_items"]:
            src = "; ".join(f"[{s['record']}] {s.get('file','')} {s.get('note','')}" for s in d.get("sources", []))
            L.append(f"| `{d['label']}` | `{d['for']}` | {src} |")
        L.append("")
    if spec.get("notes"):
        L.append("## 특별 지시\n")
        L.append("\n".join(f"- {n}" for n in spec["notes"]) + "\n")
    L.append("## 축자 발췌\n")
    L.append("아래 발췌는 좌표를 알려 주는 것이고 원문을 대신하지 않는다(공통 지침 5절). 쓰기 전에 같은 파일의 같은 행을 다시 연다. 발췌의 기호와 낱말은 기록의 것이므로 장부 v2의 사전으로 옮겨 쓴다.\n")
    for sec in spec["sections"]:
        for it in sec["items"]:
            for s in it.get("sources", []):
                path = source_path(s)
                rng, how = source_range(s, path)
                if not rng:
                    problems.append(f"{it['label']}: 좌표 미해소 {s}")
                    continue
                a, b, body = excerpt(path, rng)
                L.append(f"### `{it['label']}` ← [{s['record']}] `{s.get('file','exposition.md')}` {a}–{b}행 ({s.get('note','')})\n")
                L.append("```")
                L.append(body)
                L.append("```\n")
            fe = it.get("first_edition")
            if fe and fe.get("range"):
                path = os.path.join(ROOT, fe["file"])
                a, b, body = excerpt(path, fe["range"])
                L.append(f"### `{it['label']}` ← 첫 판 `{fe['file']}` {a}–{b}행 ({fe.get('note','')})\n")
                L.append("```")
                L.append(body)
                L.append("```\n")
    L.append("## 완료 조건과 반환\n")
    L.append(f"공통 지침 2절의 산출물 셋(`장v2/장{tag}.md`, `장v2/부록D_장{tag}.md`(해당 시), `대조v2/장{tag}_집필대조.md`)이 있고, 위 표의 모든 라벨이 장 파일의 진술 머리에 한 번씩 있으며, 전개 대상의 증명이 모든 단계를 담고, 반환이 공통 지침 11절의 서식을 따른다.\n")
    io.open(out_path, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("written", out_path, os.path.getsize(out_path), "bytes")
    if problems:
        print("문제:", len(problems))
        for p in problems:
            print(" -", p)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
