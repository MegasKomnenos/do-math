# -*- coding: utf-8 -*-
"""F11: 11.4절 문헌 표의 「쓰인 자리」와 장 파일에서 저자명이 실제로 나오는 자리를 대조한다."""
import re, glob, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
KEYS = {'Konheim':['Konheim'], 'Foata':['Foata','Pollak'], 'Celano':['Celano'], 'Aguilar':['Aguilar'], 'Stanley-exp':['지수 공식'], 'Stanley-cayley':['Cayley 공식'], 'Stanley-lagrange':['Lagrange 역변환'], 'Knuth':['Knuth'], 'Flajolet':['Flajolet'], 'Tanner':['Tanner'], 'Robbins':['Robbins'], 'Petersson':['Petersson'], 'Janson':['Janson'], 'Ibragimov':['Ibragimov'], 'Ahlfors':['Ahlfors','Cauchy 적분 공식','편각 원리','부분분수'], 'Graham':['Euler–Maclaurin','Graham'], 'FKG':['FKG','Fortuin'], 'Jensen':['Jensen'], 'Wallis':['Wallis'], 'Corless':['Corless','Lambert'], 'Grimmett':['Grimmett'], 'Harris':['Harris'], 'Comtet':['Comtet','Faà'], 'Apostol':['Apostol','Euler 합'], 'Titchmarsh':['Titchmarsh']}
def index(f):
    L = open(f, encoding='utf-8').read().split('\n'); idx = []
    for i, l in enumerate(L, 1):
        m = re.match(r'^###\s+(\d+\.\d+)', l)
        if m: idx.append((i, '절 ' + m.group(1)))
        m = re.match(r'^### D\.\{\{D:([^}]+)\}\}', l)
        if m: idx.append((i, 'D.' + m.group(1)))
        for m in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\}', l):
            idx.append((i, f'{m.group(1)} {{{{{m.group(2)}:{m.group(3)}}}}}' + (' 의 증명' if '의 증명' in l[m.end():m.end()+8] else '')))
        if l.startswith('**증명'): idx.append((i, (idx[-1][1] if idx else '?') + ' 의 증명'))
    return L, idx
def where(idx, ln):
    cur = None
    for i, t in idx:
        if i <= ln: cur = t
        else: break
    return cur
files = sorted(glob.glob(ROOT + r'\장v2\장*.md')) + sorted(glob.glob(ROOT + r'\장v2\부록D_*.md'))
files = [f for f in files if not f.endswith('장11.md')]
for key, pats in KEYS.items():
    locs = []
    for f in files:
        L, idx = index(f)
        for i, l in enumerate(L, 1):
            if any(p in l for p in pats):
                w = f'{os.path.basename(f)}:{where(idx, i)}'
                if w not in locs: locs.append(w)
    print(f'## {key}: ' + '; '.join(locs))
