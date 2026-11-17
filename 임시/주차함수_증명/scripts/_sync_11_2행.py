# -*- coding: utf-8 -*-
"""11.2 표(지금은 10.2절; 장v2/장10.md)의 여섯째 칸(독립 재계산 전문) 동기화 — 2026-11-17 결정 K5-11로 그 열이 표에서 빠졌다(부록 D
「독립 재계산」 줄의 사본이었다; 계산의 서술은 부록 D 항목에만 있다). 이 스크립트는 파이프라인(`_파이프라인_수리후_1115.sh`)이
부르던 자리를 지키기 위해 남겨 두되, 표에 여섯째 칸이 남아 있지 않은지만 검사하고 아무것도 고치지 않는다.
다섯째 칸(재계산 꺾쇠)의 동기화는 `_sync_11_2꺾쇠.py`가 맡는다.
사용: python -I scripts/_sync_11_2행.py [<라벨> ...]   (인자는 무시한다; 여섯째 칸이 있는 행이 있으면 그 이름을 적고 종료 코드 1)"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROW = re.compile(r"^\| 부록 D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\} \|")


def main():
    p = os.path.join(ROOT, "장v2", "장10.md")
    lines = io.open(p, encoding="utf-8").read().split("\n")
    bad = []
    n = 0
    for row in lines:
        m = ROW.match(row)
        if not m:
            continue
        n += 1
        # 칸 경계는 ` | `(수식 안의 세로줄은 생성기가 `\vert`로 바꾸어 둔다)
        cells = row.strip()[1:-1].split(" | ")
        if len(cells) != 5:
            bad.append((m.group(1), len(cells)))
    if bad:
        for name, k in bad:
            print(f"칸 수 {k}(다섯이어야 한다): {name}")
        print("11.2 표에 다섯 칸이 아닌 행이 있다 — `_gen_11_2표.py --fill 장v2/장10.md`로 다시 채운다(K5-11).")
        sys.exit(1)
    print(f"11.2 표 {n}행 모두 다섯 칸; 「독립 재계산」 열은 K5-11로 없어졌으므로 할 일 없음.")


if __name__ == "__main__":
    main()
