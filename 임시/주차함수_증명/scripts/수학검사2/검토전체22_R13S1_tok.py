# S1 검산 도구: 고정 접두(예: 'A_', 'C_', '\mathrm{')로 시작하는 토큰의 여러 철자를 장별로 모아 센다.
# 사용: python -I 검토전체22_R13S1_tok.py [-b] [-k 뒤글자수] 접두
#  접두 뒤에 중괄호 묶음이 오면 그 묶음 전체를, 아니면 한 글자를 잡고, 그 뒤 -k 글자(기본 1)를 더 보인다.
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
FILES = [('1','장1'),('2','장2'),('2','부록D_장2'),('3','장3'),('3','부록D_장3'),('4','장4'),('4','부록D_장4'),
         ('5','장5A'),('5','장5B'),('5','부록D_장5A'),('6','장6'),('7','장7A'),('7','장7B'),('7','부록D_장7A'),('7','부록D_장7B'),
         ('8','장8'),('8','부록D_장8'),('9','장9'),('9','부록D_장9'),('10','장10')]
a = sys.argv[1:]; BARE = False; K = 1
while a and a[0] in ('-b', '-k'):
    if a[0] == '-b': BARE = True; a = a[1:]
    else: K = int(a[1]); a = a[2:]
pre = a[0]
BS = chr(92)
prevre = re.compile('(' + BS + BS + '[A-Za-z]+' + BS + 's*' + BS + '{?' + BS + 's*|[A-Za-z])$')
res = {}
for ch, fn in FILES:
    for line in io.open(os.path.join(BASE, fn + '.md'), encoding='utf-8'):
        st = 0
        while True:
            j = line.find(pre, st)
            if j < 0: break
            st = j + len(pre)
            if BARE and prevre.search(line[max(0, j-30):j]): continue
            e = st
            if e < len(line) and line[e] == '{':
                d = 0
                while e < len(line):
                    if line[e] == '{': d += 1
                    elif line[e] == '}':
                        d -= 1
                        if d == 0: e += 1; break
                    e += 1
            else:
                e += 1
            tok = line[j:e + K].replace('\n', ' ')
            res.setdefault(tok, {}).setdefault(ch, 0)
            res[tok][ch] += 1
for tok in sorted(res, key=lambda t: -sum(res[t].values())):
    print('%-40s %s' % (tok, ' '.join('%s(%d)' % (c, res[tok][c]) for c in ['1','2','3','4','5','6','7','8','9','10'] if c in res[tok])))
