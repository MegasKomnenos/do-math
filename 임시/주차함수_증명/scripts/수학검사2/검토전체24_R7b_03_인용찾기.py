# -*- coding: utf-8 -*-
# 검토전체24 R7b: 고정 문자열이 든 자리를 앞뒤 문맥과 함께 보여 준다(자리 찾기 전용).
import sys, glob, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pat = sys.argv[1]
before = int(sys.argv[2]); after = int(sys.argv[3])
files = sys.argv[4:]
for pth in files:
    for f in sorted(glob.glob(pth)):
        with open(f, encoding='utf-8') as fh:
            for i, line in enumerate(fh, 1):
                s = 0
                while True:
                    j = line.find(pat, s)
                    if j < 0: break
                    print("%s:%d: …%s…" % (f, i, line[max(0, j-before):j+len(pat)+after].replace("\n", " ")))
                    s = j+len(pat)
