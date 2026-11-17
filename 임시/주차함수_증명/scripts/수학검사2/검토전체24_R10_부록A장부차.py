# 부록 A와 장부 1.1·1.2의 같은 글자 행에서 뜻·기록의 글자 칸이 다른 부분만 difflib으로 찍는다(후보 찾기).
import re, io, sys, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
root = r'C:/math/임시/주차함수_증명/'
L = open(root+'장부_v2.md', encoding='utf-8').read().split('\n')
A = open(root+'장v2/부록A.md', encoding='utf-8').read().split('\n')
def cells(l): return [c.strip() for c in l.strip().strip('|').split(' | ')]
def norm(s): return s.replace('`', '').replace(' ', '')
i11 = next(i for i,l in enumerate(L) if l.startswith('### 1.1'))
i12 = next(i for i,l in enumerate(L) if l.startswith('### 1.2'))
i13 = next(i for i,l in enumerate(L) if l.startswith('### 1.3'))
led = {}
for i in range(i11, i12):
    if L[i].startswith('| $'):
        c = cells(L[i]); led[norm(c[0])] = (i+1, c[1], None)
for i in range(i12, i13):
    if L[i].startswith('| $'):
        c = cells(L[i]); led[norm(c[0])] = (i+1, c[2], c[-1])
def show(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal': continue
        ctx = a[max(0,i1-25):i1]
        print(f'      …{ctx}【A:{a[i1:i2]}】【장부:{b[j1:j2]}】')
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for i, l in enumerate(A):
    if not l.startswith('| $') or not (lo <= i+1 <= hi): continue
    c = cells(l); key = norm(c[0]); ln, mean, rec = led[key]
    if norm(mean) != norm(c[1]):
        print(f'[A {i+1}/장부 {ln}] 뜻 {c[0]}'); show(c[1].replace('`',''), mean.replace('`',''))
    if rec is not None and norm(rec) != norm(c[3]):
        print(f'[A {i+1}/장부 {ln}] 기록 {c[0]}'); show(c[3].replace('`',''), rec.replace('`',''))
