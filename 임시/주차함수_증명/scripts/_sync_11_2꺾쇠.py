# -*- coding: utf-8 -*-
"""11.2 표(지금은 10.2절; 장v2/장10.md)의 다섯째 칸(재계산 꺾쇠 〔…〕)을 부록 D 조각의 **독립 재계산.** 줄 첫머리 꺾쇠와 같게 맞춘다.
여섯째 칸(독립 재계산 전문)은 2026-11-17 결정 K5-11로 표에서 빠졌다(`_sync_11_2행.py`는 그 칸이 남아 있지 않은지만 검사한다). 그래서 꺾쇠 칸이
행의 마지막 칸이고, 칸은 양 끝의 세로줄을 벗긴 뒤 ` | `로 가른다(끝 칸에 닫는 세로줄이 붙은 채 비교되어 모든 행을 갱신으로 잡고 닫는 세로줄을
잘라 내던 결함을 2026-11-17 V5가 고침). 멱등.
사용: python -I scripts/_sync_11_2꺾쇠.py [--dry] [<라벨> ...]   (라벨을 주지 않으면 표의 모든 행)"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAP = os.path.join(ROOT, "장v2")
HEAD = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
BRACKET = re.compile(r"^\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)")
ROW = re.compile(r"^\| 부록 D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\} \|")


def brackets():
    out = {}
    for p in sorted(glob.glob(os.path.join(CHAP, "부록D_*.md"))):
        name = None
        for l in io.open(p, encoding="utf-8").read().split("\n"):
            m = HEAD.match(l)
            if m:
                name = m.group(1)
                continue
            if name and l.startswith("**독립 재계산.**"):
                b = BRACKET.match(l)
                if b:
                    out[name] = b.group(1)
    return out


def main():
    dry = "--dry" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    br = brackets()
    p = os.path.join(CHAP, "장10.md")
    lines = io.open(p, encoding="utf-8").read().split("\n")
    n = 0
    for i, row in enumerate(lines):
        m = ROW.match(row)
        if not m:
            continue
        name = m.group(1)
        if names and name not in names:
            continue
        if name not in br:
            print("꺾쇠 없음(부록 D):", name)
            continue
        # 칸 경계는 ` | `(수식 안의 세로줄은 생성기가 `\vert`로 바꾸어 둔다); 양 끝의 세로줄을 벗기고 가른 뒤 같은 꼴로 되묶는다
        cells = row.strip()[1:-1].split(" | ")
        k = [j for j, c in enumerate(cells) if c.strip().startswith("〔")]
        if len(k) != 1:
            print("꺾쇠 칸을 못 찾음:", name)
            continue
        if cells[k[0]].strip() != br[name]:
            print("갱신", name)
            print("   전:", cells[k[0]].strip()[:160])
            print("   후:", br[name][:160])
            cells[k[0]] = br[name]
            lines[i] = "| " + " | ".join(c.strip() for c in cells) + " |"
            n += 1
    if not dry and n:
        io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("갱신 행", n, "(dry)" if dry else "")


if __name__ == "__main__":
    main()
