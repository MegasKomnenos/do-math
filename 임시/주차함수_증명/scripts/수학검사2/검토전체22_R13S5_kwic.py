# 고정 문자열의 앞뒤 문맥. 사용: python -I kwic.py <파일> <토큰> [앞] [뒤] [최대건수] [시작행] [끝행]
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
f, t = sys.argv[1], sys.argv[2]
a = int(sys.argv[3]) if len(sys.argv) > 3 else 80
b = int(sys.argv[4]) if len(sys.argv) > 4 else 160
mx = int(sys.argv[5]) if len(sys.argv) > 5 else 5
lo = int(sys.argv[6]) if len(sys.argv) > 6 else 1
hi = int(sys.argv[7]) if len(sys.argv) > 7 else 10**9
n = 0
for i, l in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
    if i < lo or i > hi: continue
    p = l.find(t)
    while p >= 0 and n < mx:
        print('L%d@%d: …%s…' % (i, p, l[max(0, p - a):p + len(t) + b])); n += 1
        p = l.find(t, p + len(t) + b)
print('(%d건 표시)' % n)
