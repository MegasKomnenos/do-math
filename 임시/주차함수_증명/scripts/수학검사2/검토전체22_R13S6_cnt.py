# -*- coding: utf-8 -*-
"""고정 문자열을 장 파일별로 세고(-c), 걸린 줄의 앞뒤를 보여 준다(-s N: 문맥 글자 수).
쓰기: python -I 검토전체22_R13S6_cnt.py [-s 60] [-f 장6,장7B] [-m 5] 문자열1 문자열2 ...
문자열은 파일(-F path, 줄마다 하나)로도 줄 수 있다."""
import sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
args = sys.argv[1:]
ctx = None; only = None; mx = 8; pats = []
i = 0
while i < len(args):
    a = args[i]
    if a == '-s': ctx = int(args[i+1]); i += 2
    elif a == '-f': only = args[i+1].split(','); i += 2
    elif a == '-m': mx = int(args[i+1]); i += 2
    elif a == '-b': only = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록B','부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장7A','부록D_장7B','부록D_장8','부록D_장9']; i += 1
    elif a == '-F':
        with open(args[i+1], encoding='utf-8') as f:
            pats += [l.rstrip('\n') for l in f if l.strip()]
        i += 2
    else: pats.append(a); i += 1
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록A','부록B','부록C',
         '부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장7A','부록D_장7B','부록D_장8','부록D_장9']
files = {}
for nm in order:
    p = os.path.join(base, nm + '.md')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            files[nm] = f.read().split('\n')
for pat in pats:
    res = []
    tot = 0
    for nm in order:
        if nm not in files: continue
        if only and nm not in only: continue
        c = sum(l.count(pat) for l in files[nm])
        if c: res.append('%s:%d' % (nm, c)); tot += c
    print('[%s] 총 %d  %s' % (pat, tot, ' '.join(res)))
    if ctx is not None:
        for nm in order:
            if nm not in files: continue
            if only and nm not in only: continue
            shown = 0
            for ln, l in enumerate(files[nm], 1):
                st = 0
                while True:
                    j = l.find(pat, st)
                    if j < 0: break
                    if shown < mx:
                        print('   %s:%d: …%s…' % (nm, ln, l[max(0, j-ctx): j+len(pat)+ctx]))
                    shown += 1
                    st = j + len(pat)
            if shown > mx: print('   %s: (+%d건 더)' % (nm, shown - mx))
