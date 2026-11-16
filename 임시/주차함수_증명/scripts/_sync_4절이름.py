# -*- coding: utf-8 -*-
"""장부 4절(이름 사전)의 「종류」·「이 글의 이름」·「기록의 이름」을 진술 머리와 같게 맞춘다. 머리가 정본이다. 멱등(종류 열은 2026-11-16 15차 G6의 정리→보조정리 변경 뒤 추가).
머리 `**종류 {{라벨}} (이름; 기록 이름) [...]`에서 첫 최상위 쌍반점 앞이 이 글의 이름, 뒤가 기록의 이름이다.
괄호가 「기록 […」으로 시작하면 이 글의 이름은 없고 전체가 기록의 이름이다. 머리에 기록 이름이 없으면 그 칸은 손대지 않는다.
사용: python scripts/_sync_4절이름.py [--dry]"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv


def head_name(line):
    """(라벨, 이 글의 이름, 기록의 이름, 종류). 머리가 아니면 (None, None, None, None)."""
    m = re.match(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\} \(", line)
    if not m:
        return None, None, None, None
    i = m.end()
    depth = 1
    j = i
    while j < len(line) and depth:
        c = line[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        j += 1
    full = line[i:j - 1]
    # 첫 최상위 쌍반점
    depth = 0
    cut = None
    for k, c in enumerate(full):
        if c in "({[":
            depth += 1
        elif c in ")}]":
            depth -= 1
        elif c == ";" and depth == 0:
            cut = k
            break
    if cut is None:
        name, rec = full.strip(), ""
    else:
        name, rec = full[:cut].strip(), full[cut + 1:].strip()
    if name.startswith("기록 ["):
        # 괄호가 기록 이름만 들면 이 글의 이름은 없다(장부 4절 「이 글의 이름」 칸을 비워 둔다)
        rec, name = name, ""
    return m.group(2), name, rec, m.group(1)


def main():
    heads = {}
    for f in glob.glob(os.path.join(ROOT, "장v2", "장*.md")):
        for l in io.open(f, encoding="utf-8").read().split("\n"):
            lab, name, rec, kind = head_name(l)
            if lab:
                heads[lab] = (name, rec, kind)
    p = os.path.join(ROOT, "장부_v2.md")
    t = io.open(p, encoding="utf-8").read()
    i = t.find("## 4. 이름 사전")
    j = t.find("\n## 5", i)
    sec = t[i:j]
    lines = sec.split("\n")
    changed = 0
    for idx, l in enumerate(lines):
        if not (l.startswith("| ") and "{{" in l):
            continue
        cells = l.split("|")
        # | 첫 판 번호 | 종류 | 이 글의 이름 | 기록의 이름 | 둘째 판 절 | 라벨 |
        if len(cells) < 8:
            continue
        lab = re.search(r"\{\{([^}]+)\}\}", cells[6])
        if not lab:
            continue
        h = heads.get(lab.group(1))
        if h is None:
            continue
        name, rec, kind = h
        cur_kind = cells[2].strip()
        if kind and cur_kind != kind:
            print(f"  {cells[1].strip():>6} | 종류 | {cur_kind} → {kind}")
            cells[2] = " " + kind + " "
            changed += 1
        cur = cells[3].strip()
        if name and cur != name:  # 빈 칸도 머리의 이름으로 채운다(2026-11-15 N14-2)
            print(f"  {cells[1].strip():>6} | 이름 | {cur[:45]} → {name[:45]}")
            cells[3] = " " + name + " "
            changed += 1
        cur_rec = cells[4].strip()
        if rec and rec.startswith("기록 [") and cur_rec != rec:
            print(f"  {cells[1].strip():>6} | 기록 | {cur_rec[:45]} → {rec[:45]}")
            cells[4] = " " + rec + " "
            changed += 1
        lines[idx] = "|".join(cells)
    print("바꾼 칸", changed)
    if DRY or not changed:
        return
    t = t[:i] + "\n".join(lines) + t[j:]
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("기록함")


main()
