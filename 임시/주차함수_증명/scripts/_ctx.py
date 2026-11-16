# -*- coding: utf-8 -*-
"""파일에서 부분 문자열(고정 문자열)의 출현을 줄 번호와 앞뒤 문맥으로 보여 준다. 인자: 파일 부분문자열 [폭] [최대개수]"""
import io
import sys

path, sub = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 150
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 4
lines = io.open(path, encoding="utf-8").read().split("\n")
n = 0
for i, l in enumerate(lines):
    k = l.find(sub)
    while k >= 0 and n < mx:
        print(f"[{path.split('/')[-1]}:{i+1}] …{l[max(0, k-w):k+len(sub)+w]}…")
        n += 1
        k = l.find(sub, k + 1)
if n == 0:
    print(f"[{path.split('/')[-1]}] 없음: {sub}")
