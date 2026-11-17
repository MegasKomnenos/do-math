# -*- coding: utf-8 -*-
"""정규식으로 장 파일을 훑어 문맥을 보여 준다(자리 찾기 전용). 쓰기: python -I …_re.py [-s N] [-m N] [-a] 정규식 ...  (-a: 부록 A·C 포함)"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록B',
         '부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장7A','부록D_장7B','부록D_장8','부록D_장9']
args = sys.argv[1:]; ctx = 50; mx = 4; pats = []; i = 0
while i < len(args):
    if args[i] == '-s': ctx = int(args[i+1]); i += 2
    elif args[i] == '-m': mx = int(args[i+1]); i += 2
    elif args[i] == '-a': order += ['부록A', '부록C']; i += 1
    elif args[i] == '-f': order = args[i+1].split(','); i += 2
    else: pats.append(args[i]); i += 1
files = {nm: open(os.path.join(base, nm + '.md'), encoding='utf-8').read().split('\n') for nm in order}
for pat in pats:
    rx = re.compile(pat)
    tot = 0; out = []; per = []
    for nm in order:
        c = 0
        for ln, l in enumerate(files[nm], 1):
            for m in rx.finditer(l):
                c += 1
                if c <= mx:
                    out.append('   %s:%d: …%s…' % (nm, ln, l[max(0, m.start()-ctx): m.end()+ctx]))
        if c: per.append('%s:%d' % (nm, c)); tot += c
    print('[/%s/] 총 %d  %s' % (pat, tot, ' '.join(per)))
    for o in out: print(o)
