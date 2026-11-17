# -*- coding: utf-8 -*-
"""점검 X1 — 장 파일을 바이트 예산 안에서 행 단위로 끊어 출력하는 읽기 도구(원문 전문 읽기용; 쓰지 않는다).
사용: python -I 점검_X1_읽기.py <파일> <시작 행(1부터)> [최대 바이트=27000]
출력 끝에 「NEXT: <다음 시작 행>」 또는 「END」를 찍는다.
"""
import sys
from pathlib import Path

f = Path(sys.argv[1])
start = int(sys.argv[2])
budget = int(sys.argv[3]) if len(sys.argv) > 3 else 27000
end = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
lines = f.read_text(encoding="utf-8").split("\n")
out = []
used = 0
i = start
while i <= len(lines) and i <= end:
    L = lines[i - 1]
    b = len(L.encode("utf-8")) + 8
    if out and used + b > budget:
        break
    out.append(f"{i}\t{L}")
    used += b
    i += 1
sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(out))
print("NEXT:", i if i <= len(lines) else "END", "(end 한계)" if i > end and i <= len(lines) else "")
