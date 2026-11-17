# -*- coding: utf-8 -*-
"""낱말마다: 장 파일별 건수, 처음 나오는 자리(절 번호), 정의 꼴(…라 부른다/한다)로 나오는 자리(절 번호)를 보여 준다.
쓰기: python -I …_first.py [-s N] 낱말 ...   (자리 찾기 전용; 판정은 원문을 읽고 한다)"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록B',
         '부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장7A','부록D_장7B','부록D_장8','부록D_장9']
ctx = 40; args = sys.argv[1:]; words = []; i = 0; nd = 3
while i < len(args):
    if args[i] == '-s': ctx = int(args[i+1]); i += 2
    elif args[i] == '-d': nd = int(args[i+1]); i += 2
    else: words.append(args[i]); i += 1
files = {}
for nm in order:
    ls = open(os.path.join(base, nm + '.md'), encoding='utf-8').read().split('\n')
    sec = '(머리)'; rows = []
    for ln, l in enumerate(ls, 1):
        m = re.match(r'^#{2,4}\s+(\d+(?:\.\d+)*)\.?\s', l)
        if m: sec = m.group(1)
        elif l.startswith('## 부록') or l.startswith('### '): sec = l.strip('# ')[:14]
        rows.append((ln, sec, l))
    files[nm] = rows
defrx = r'[^.。]{0,25}(?:라|이라|라고|이라고|로|으로)\s?(?:부르|부른|하자|한다|하고|하며|이름)'
for w in words:
    per = []; first = []; defs = []
    for nm in order:
        c = 0
        for ln, sec, l in files[nm]:
            st = 0
            while True:
                j = l.find(w, st)
                if j < 0: break
                c += 1
                if len(first) < 2:
                    first.append('   처음 %s:%d [%s절] …%s…' % (nm, ln, sec, l[max(0, j-ctx): j+len(w)+ctx]))
                tail = l[j+len(w): j+len(w)+45]
                if re.match(defrx, tail) and len(defs) < nd:
                    defs.append('   정의꼴 %s:%d [%s절] …%s…' % (nm, ln, sec, l[max(0, j-ctx): j+len(w)+45]))
                st = j + len(w)
        if c: per.append('%s:%d' % (nm, c))
    print('[%s] %s' % (w, ' '.join(per) if per else '0건'))
    for o in first + defs: print(o)
