# -*- coding: utf-8 -*-
"""I14: 파일·행·바늘(평문)을 받아 그 행에서 바늘 둘레 문맥을 출력한다. 사용: file line needle [width]"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명/장v2"
args = sys.argv[1:]
w = 120
i = 0
while i + 2 < len(args) or i + 2 == len(args) - 0 and False:
    f, n, needle = args[i], int(args[i+1]), args[i+2]; i += 3
    lines = open(os.path.join(ROOT, f + '.md'), encoding='utf-8').read().split('\n')
    l = lines[n-1]
    p = l.find(needle)
    if p < 0:
        print(f"{f}:{n}: (없음) {l[:200]}")
    else:
        s = max(0, p - w); e = min(len(l), p + len(needle) + w)
        print(f"{f}:{n}: …{l[s:e]}…")
