# -*- coding: utf-8 -*-
"""장부 v2 4절(이름 사전: 첫 판 번호 ↔ 둘째 판 라벨 ↔ 기록의 이름)을 장 파일의 진술 머리에서 다시 만든다.

모집단: 장v2/장*.md의 모든 진술 머리 `**종류 {{N:라벨}} (이 글의 이름; 기록 [r…]의 이름) [지위; 식별자].**`
- 첫 판 번호는 라벨 old-A-B에서, 새 진술은 「—」.
- 「이 글의 이름」·「기록의 이름」은 기존 4절 행이 있고 비어 있지 않으면 그것을 유지(세션이 손질한 이름), 없으면 머리에서.
- 「둘째 판 절」은 머리가 놓인 `### N.m` 머리.
- 첫 판 진술 가운데 뺀 것(등록부 DELETED)은 기존 4절의 「뺌」 행을 유지한다.
사용: python 장부v2_4절_재생성2.py [--dry]
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "장부_v2.md")
CHAP = os.path.join(ROOT, "장v2")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) (\{\{(\d+):([A-Za-z0-9\-]+)\}\})")
SEC_RE = re.compile(r"^### (\d+\.\d+)")


def split_paren(rest):
    """rest는 라벨 뒤 문자열. 앞에 ' (' 괄호가 있으면 균형을 맞춰 안쪽을 돌려준다."""
    rest = rest.lstrip()
    if not rest.startswith("("):
        return ""
    depth = 0
    for i, ch in enumerate(rest):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return rest[1:i]
    return ""


def chapter_order(name):
    m = re.match(r"장(\d+)([A-Z]?)\.md", name)
    return (int(m.group(1)), m.group(2)) if m else (99, name)


def collect_heads():
    rows = []
    for p in sorted(glob.glob(os.path.join(CHAP, "장*.md")), key=lambda q: chapter_order(os.path.basename(q))):
        sec = ""
        for ln in io.open(p, encoding="utf-8").read().split("\n"):
            m = SEC_RE.match(ln)
            if m:
                sec = m.group(1)
                continue
            h = HEAD_RE.match(ln)
            if not h:
                continue
            kind, label, ch, short = h.group(1), h.group(2), h.group(3), h.group(4)
            inner = split_paren(ln[h.end():])
            name, recname = inner, ""
            if "; 기록 " in inner:
                name, recname = inner.split("; 기록 ", 1)
                recname = "기록 " + recname
            elif inner.startswith("기록 "):
                name, recname = "", inner
            mo = re.match(r"old-(\d+)-(\d+)$", short)
            num = f"{mo.group(1)}.{mo.group(2)}" if mo else "—"
            rows.append(dict(num=num, kind=kind, name=name.strip(), record_name=recname.strip(), sec=sec, label=label))
    return rows


def parse_old_sec4(text):
    i = text.index("## 4. 이름 사전")
    j = text.index("\n## 5.", i)
    body = text[i:j]
    old = {}
    for ln in body.split("\n"):
        if not ln.startswith("|") or ln.startswith("|---") or ln.startswith("| 첫 판 번호"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 6:
            old[cells[5].strip("`")] = dict(num=cells[0], kind=cells[1], name=cells[2], record_name=cells[3], sec=cells[4], label=cells[5].strip("`"))
    head_end = body.index("| 첫 판 번호")
    head = body[:head_end]
    return i, j, head, old


def main():
    dry = "--dry" in sys.argv
    text = io.open(LEDGER, encoding="utf-8").read()
    i, j, head, old = parse_old_sec4(text)
    heads = collect_heads()
    seen = set()
    out_rows = []
    for r in heads:
        o = old.get(r["label"])
        name = (o["name"] if o and o["name"] else r["name"])
        rec = (o["record_name"] if o and o["record_name"] else r["record_name"])
        out_rows.append((r["num"], r["kind"], name, rec, r["sec"], r["label"]))
        seen.add(r["label"])
    kept = []
    for lab, o in old.items():
        if lab in seen:
            continue
        if "뺌" in (o["sec"] + o["name"] + o["record_name"] + o["label"]) or o["num"] in {"7.47", "7.48", "7.49", "8.38", "8.7", "8.27", "8.29"}:
            kept.append((o["num"], o["kind"], o["name"], o["record_name"], o["sec"] if o["sec"] else "뺌", o["label"]))
        else:
            print("기존 4절 행이 본문 머리에 없음(제외):", o["num"], o["label"])
    head = re.sub(r"\(`scripts/_tmp_transcript/names_table\.md`에서 생성;", "(장 파일의 진술 머리에서 생성, `scripts/장부v2_4절_재생성2.py`;", head)
    out = [head.rstrip("\n"), "", "| 첫 판 번호 | 종류 | 이 글의 이름 | 기록의 이름 | 둘째 판 절 | 라벨 |", "|---|---|---|---|---|---|"]
    for num, kind, name, rec, sec, label in out_rows + kept:
        lab = f"{{{{{label[2:-2]}}}}}" if label.startswith("{{") and label.endswith("}}") else (label or "—")
        out.append(f"| {num} | {kind} | {name} | {rec} | {sec} | {lab} |")
    new_body = "\n".join(out) + "\n"
    new_count = sum(1 for r in out_rows if r[0] == "—")
    print(f"머리 {len(heads)}개(새 진술 {new_count}), 기존 4절 {len(old)}행, 뺌 유지 {len(kept)}행 → 새 4절 {len(out_rows)+len(kept)}행")
    if dry:
        return
    text2 = text[:i] + new_body + text[j:]
    io.open(LEDGER, "w", encoding="utf-8", newline="\n").write(text2)
    print("장부_v2.md 4절 갱신")


if __name__ == "__main__":
    main()
