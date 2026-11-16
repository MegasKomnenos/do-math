# -*- coding: utf-8 -*-
"""11.2 「컴퓨터 계산의 명세」 표의 행을 부록 D 조각에서 생성한다(세션 채움).

열: 부록 D 항목 | 확인하는 진술(라벨) | 산술 등급 | 놓인 곳(장·절) | 재계산 | 독립 재계산
- 항목과 진술 라벨은 머리 `### D.{{D:이름}} 제목 (정리 {{N:라벨}}, …)`에서.
- 산술 등급은 **산술 등급.** 줄에서 네 이름만 뽑는다(설명은 뺀다).
- 놓인 곳은 진술 라벨이 놓인 장 파일의 `### N.m` 머리.
- 재계산은 **독립 재계산.** 줄 첫머리의 꺾쇠 요약 `〔구현 …; 범위 …; 산술 …; 자료 …〕`(없으면 「—」).
- 독립 재계산은 꺾쇠 요약을 뺀 **독립 재계산.** 줄의 첫 문장(80자 안).
사용: python _gen_11_2표.py [--out 대조v2/_11_2표.md] [--fill 장v2/장11.md]  (--fill이면 `<!-- 세션 채움 -->` 줄을 표 행으로 바꾼다)
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAP = os.path.join(ROOT, "장v2")
GRADES = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석", "배정밀도 평가", "40자리 평가", "30자리 평가"]
HEAD = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}\s*(.*)$")
LAB = re.compile(r"\{\{(\d+):([A-Za-z0-9\-]+)\}\}")
STMT = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) (\{\{\d+:[A-Za-z0-9\-]+\}\})")
SEC = re.compile(r"^### (\d+\.\d+)")


def chapter_order(name):
    m = re.match(r"장(\d+)([A-Z]?)\.md", name)
    return (int(m.group(1)), m.group(2)) if m else (99, name)


def label_sections():
    sec_of = {}
    for p in sorted(glob.glob(os.path.join(CHAP, "장*.md")), key=lambda q: chapter_order(os.path.basename(q))):
        sec = ""
        for ln in io.open(p, encoding="utf-8").read().split("\n"):
            m = SEC.match(ln)
            if m:
                sec = m.group(1)
                continue
            h = STMT.match(ln)
            if h:
                sec_of[h.group(2)] = sec
    return sec_of


def grades_in(text):
    # 「기록의 계산은 …」처럼 기록 쪽 산술을 적은 뒷문장은 등급으로 읽지 않는다.
    text = re.split(r"\.\s+(?=기록의 )", text, 1)[0]
    found = []
    for g in GRADES:
        if g in text and g not in found:
            found.append(g)
    return found


def rows():
    sec_of = label_sections()
    out = []
    for p in sorted(glob.glob(os.path.join(CHAP, "부록D_장*.md")), key=lambda q: chapter_order(os.path.basename(q).replace("부록D_", ""))):
        cur = None
        for ln in io.open(p, encoding="utf-8").read().split("\n"):
            m = HEAD.match(ln)
            if m:
                name, rest = m.group(1), m.group(2)
                labels = ["{{%s:%s}}" % (a, b) for a, b in LAB.findall(rest)]
                # 머리의 괄호 안 「정리 {{..}}, 보조정리 {{..}}·{{..}}·{{..}}」에서 라벨마다 가장 가까운 앞 유형 낱말을 붙인다
                # (유형 낱말 없이 이어진 라벨도 빠뜨리지 않는다 — 일관성 검토 ㄴ #16).
                pairs = []
                kind = None
                for t in re.finditer(r"(정의|정리|명제|보조정리|따름정리)|\{\{(\d+):([A-Za-z0-9\-]+)\}\}", rest):
                    if t.group(1):
                        kind = t.group(1)
                    else:
                        pairs.append((kind, "{{%s:%s}}" % (t.group(2), t.group(3))))
                stmt = ", ".join(f"{k} {l}" if k else l for k, l in pairs)
                secs = sorted({sec_of.get(l, "") for l in labels} - {""}, key=lambda s: tuple(int(x) for x in s.split(".")))
                cur = dict(name=name, stmt=stmt, secs="·".join(secs), grade="", tag="없음", recheck="")
                out.append(cur)
                continue
            if cur and ln.startswith("**산술 등급.**"):
                cur["grade"] = ", ".join(grades_in(ln)) or ln.replace("**산술 등급.**", "").strip()[:60]
            if cur and ln.startswith("**독립 재계산.**"):
                body = ln.replace("**독립 재계산.**", "").strip()
                tg = re.match(r"(〔[^〕]*〕)\s*", body)
                if tg:
                    cur["tag"] = tg.group(1)
                    body = body[tg.end():]
                first = re.split(r"(?<=다)\.\s", body, 1)[0]
                rc = first.rstrip(".") + "."
                # 이 글의 재계산 문장(「이 글을 쓰며 …다.」)이 첫 문장 뒤에 있으면 그 첫 문장도 함께 싣는다.
                sents = re.split(r"(?<=다)\.\s", body)
                ours = next((x for x in sents if "이 글을 쓰며" in x), None)
                if ours and ours.rstrip(".") not in rc:
                    rc = rc + " " + ours.rstrip(".") + "."
                cur["recheck"] = rc
    return out


def cell(s):
    """표 칸 안의 수식에 든 세로줄 `|`을 `\\vert`로 바꾼다(표 구조 보호)."""
    return re.sub(r"\$[^$]*\$", lambda m: m.group().replace("|", r"\vert "), s)


def table(rs):
    L = ["| 부록 D 항목 | 확인하는 진술 | 산술 등급 | 놓인 곳(장·절) | 재계산 | 독립 재계산 |", "|---|---|---|---|---|---|"]
    for r in rs:
        L.append(f"| 부록 D.{{{{D:{r['name']}}}}} | {cell(r['stmt'])} | {cell(r['grade'])} | {r['secs']} | {r['tag']} | {cell(r['recheck'])} |")
    return "\n".join(L) + "\n"


def main():
    rs = rows()
    t = table(rs)
    out = None
    fill = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--out":
            out = args[i + 1]
        if a == "--fill":
            fill = args[i + 1]
    print(f"항목 {len(rs)}개; 등급 비어 있음 {sum(1 for r in rs if not r['grade'])}, 놓인 곳 비어 있음 {sum(1 for r in rs if not r['secs'])}, 재계산 비어 있음 {sum(1 for r in rs if not r['recheck'])}")
    if out:
        io.open(os.path.join(ROOT, out), "w", encoding="utf-8", newline="\n").write(t)
        print("written", out)
    if fill:
        p = os.path.join(ROOT, fill)
        s = io.open(p, encoding="utf-8").read()
        if "<!-- 세션 채움 -->" not in s:
            # 이미 채운 표가 있으면 그 행들을 새 행으로 바꾼다.
            lines = s.split("\n")
            idxs = [i for i, l in enumerate(lines) if l.startswith("| 부록 D.{{D:")]
            if not idxs:
                print("채움 표지도 기존 행도 없음:", fill)
                return
            a, b = idxs[0], idxs[-1]
            lines[a:b + 1] = [l for l in t.split("\n")[2:] if l]
            io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
            print("refilled", fill, f"({b - a + 1}행 → {len(rs)}행)")
            return
        # 표지 줄 바로 위에 표 머리가 있으면 머리를 중복하지 않는다.
        lines = s.split("\n")
        idx = next(i for i, l in enumerate(lines) if "<!-- 세션 채움 -->" in l)
        body_rows = t.split("\n")[2:]
        prev = "\n".join(lines[max(0, idx - 3):idx])
        if "| 부록 D 항목 |" in prev:
            new = body_rows
        else:
            new = t.split("\n")
        lines[idx:idx + 1] = [l for l in new if l != ""]
        io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        print("filled", fill)


if __name__ == "__main__":
    main()
