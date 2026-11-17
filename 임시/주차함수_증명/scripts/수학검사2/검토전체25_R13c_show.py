# -*- coding: utf-8 -*-
"""R13c 검산 보조: 파일의 행 범위(및 글자 범위)를 그대로 출력한다. 읽기 전용."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
path = sys.argv[1]
a = int(sys.argv[2]); b = int(sys.argv[3]) if len(sys.argv) > 3 else a
c0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
c1 = int(sys.argv[5]) if len(sys.argv) > 5 else None
L = io.open(path, encoding='utf-8', newline='').read().split('\n')
for i in range(a, b + 1):
    s = L[i - 1].rstrip('\r')
    if len(sys.argv) > 4:
        s = s[c0:c1]
    print('%d: %s' % (i, s))
