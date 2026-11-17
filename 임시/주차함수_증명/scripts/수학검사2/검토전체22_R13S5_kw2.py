# 토큰 파일의 각 고정 문자열에 대해 처음 n건의 문맥. 사용: python -I kw2.py <파일> <토큰파일> [앞] [뒤] [건수]
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
f = sys.argv[1]
toks = [l.rstrip('\n') for l in open(sys.argv[2], encoding='utf-8') if l.strip() and not l.startswith('#')]
a = int(sys.argv[3]) if len(sys.argv) > 3 else 60
b = int(sys.argv[4]) if len(sys.argv) > 4 else 140
mx = int(sys.argv[5]) if len(sys.argv) > 5 else 1
L = open(f, encoding='utf-8').read().split('\n')
for t in toks:
    n = 0
    for i, l in enumerate(L, 1):
        p = l.find(t)
        while p >= 0 and n < mx:
            print('[%s] L%d: …%s…' % (t, i, l[max(0, p - a):p + len(t) + b])); n += 1
            p = l.find(t, p + len(t) + b)
        if n >= mx: break
    if n == 0: print('[%s] 0건' % t)
