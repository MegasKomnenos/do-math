# -*- coding: utf-8 -*-
"""R13c 검산 보조: 파일의 행 범위에서 고정 문자열 토큰의 출현 수를 센다(정규식 아님). 읽기 전용.
사용: python -I 검토전체25_R13c_count.py <파일> <첫행> <끝행> [--ctx]  (토큰은 표준입력 한 줄에 하나)
--ctx를 주면 출현마다 앞뒤 문맥(행 번호 포함)을 보인다."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')
path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ctx = '--ctx' in sys.argv
L = io.open(path, encoding='utf-8', newline='').read().split('\n')
b = min(b, len(L))
for tok in sys.stdin.read().split('\n'):
    tok = tok.rstrip('\r')
    if not tok:
        continue
    hits = []
    for i in range(a, b + 1):
        s = L[i - 1]
        p = s.find(tok)
        while p >= 0:
            hits.append((i, p))
            p = s.find(tok, p + 1)
    print('%4d  %s' % (len(hits), tok))
    if ctx:
        for (i, p) in hits[:12]:
            s = L[i - 1]
            print('        L%d: ...%s...' % (i, s[max(0, p - 45):p + len(tok) + 45]))
