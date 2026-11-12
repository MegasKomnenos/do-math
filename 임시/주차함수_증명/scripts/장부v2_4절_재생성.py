# -*- coding: utf-8 -*-
"""장부 v2 4절(이름 사전: 첫 판 진술 ↔ 둘째 판 라벨)을 라벨 등록부 v2 1절에서 다시 만든다.

- 행의 모집단은 파견/라벨_v2.md 1절(첫 판 진술 전부; heads.txt 누락분 포함).
- 「이 글의 이름」과 「기록의 이름」은 기존 4절 행이 있으면 그것을 유지(세션이 손질한 이름, 예 반감 경계), 없으면 등록부의 이름.
- 「둘째 판 절」은 등록부의 것(7.19·7.21은 6.2).
사용: python 장부v2_4절_재생성.py [--dry]
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "장부_v2.md")
REG = os.path.join(ROOT, "파견", "라벨_v2.md")


def parse_registry():
    s = io.open(REG, encoding="utf-8").read()
    sec = s.split("## 1. 첫 판 진술의 대응", 1)[1].split("\n## ", 1)[0]
    rows = []
    for ln in sec.split("\n"):
        if not ln.startswith("|") or ln.startswith("|---") or ln.startswith("| 첫 판 번호"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        num, line, kind_name, sec2, label = cells[0], cells[1], cells[2], cells[3], cells[4]
        m = re.match(r"(정의|정리|명제|보조정리|따름정리)\s*(.*)$", kind_name)
        kind, name = (m.group(1), m.group(2).strip()) if m else ("", kind_name)
        label = label.strip("`")
        rows.append(dict(num=num, kind=kind, name=name, sec=sec2, label=label))
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
            old[cells[0]] = dict(kind=cells[1], name=cells[2], record_name=cells[3], sec=cells[4], label=cells[5])
    head_end = body.index("| 첫 판 번호")
    head = body[:head_end]
    return i, j, head, old


def main():
    dry = "--dry" in sys.argv
    text = io.open(LEDGER, encoding="utf-8").read()
    reg = parse_registry()
    i, j, head, old = parse_old_sec4(text)
    out = [head.rstrip("\n"), "", "| 첫 판 번호 | 종류 | 이 글의 이름 | 기록의 이름 | 둘째 판 절 | 라벨 |", "|---|---|---|---|---|---|"]
    added, moved = [], []
    for r in reg:
        o = old.get(r["num"])
        kind = r["kind"] or (o["kind"] if o else "")
        name = (o["name"] if o and o["name"] else r["name"])
        rec = o["record_name"] if o else ""
        if not o:
            added.append(r["num"])
        elif o["sec"] != r["sec"]:
            moved.append((r["num"], o["sec"], r["sec"]))
        out.append(f"| {r['num']} | {kind} | {name} | {rec} | {r['sec']} | {r['label']} |")
    new_body = "\n".join(out) + "\n\n"
    print("등록부 행:", len(reg), "| 기존 4절 행:", len(old), "| 새로 더한 행:", added, "| 절이 바뀐 행:", moved)
    if dry:
        return 0
    text = text[:i] + new_body + text[j + 1:]
    io.open(LEDGER, "w", encoding="utf-8", newline="\n").write(text)
    print("written", LEDGER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
