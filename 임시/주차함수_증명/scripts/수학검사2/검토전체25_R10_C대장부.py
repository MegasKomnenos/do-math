# 부록 C의 낱말 표·글자 표를 장부 3절·7절의 같은 행과 맞대어 다른 곳을 보여 준다(다른 행은 원문을 열어 읽는다).
import re, io, sys, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/'
def cells(ln):
    out = []; buf = ''; inm = False
    for ch in ln:
        if ch == '$': inm = not inm
        if ch == '|' and not inm: out.append(buf); buf = ''
        else: buf += ch
    out.append(buf)
    return [c.strip() for c in out[1:-1]]
def norm(s): return s.replace('`', '')
def show(tag, a, b):
    a, b = norm(a), norm(b)
    if a == b: return
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    print(tag)
    for t, i1, i2, j1, j2 in sm.get_opcodes():
        if t != 'equal': print(f'   {t}: C「{a[i1:i2][:260]}」 장부「{b[j1:j2][:260]}」')
J = open(base + '장부_v2.md', encoding='utf-8').read().split('\n')
C = open(base + '장v2/부록C.md', encoding='utf-8').read().split('\n')
i7 = [i for i, l in enumerate(J) if l.startswith('## 7.')][0]; i8 = [i for i, l in enumerate(J) if l.startswith('## 8.')][0]
i3 = [i for i, l in enumerate(J) if l.startswith('## 3.')][0]; i4 = [i for i, l in enumerate(J) if l.startswith('## 4.')][0]
# 7절
led7 = []
for i in range(i7, i8):
    if J[i].startswith('| ') and not J[i].startswith('| 이 글의 글자') and not J[i].startswith('|---'):
        c = cells(J[i])
        if len(c) == 4: led7.append((i+1, c))
        else: print('ledger7 row cells', i+1, len(c))
cs = C.index('### 기록의 글자와 이 글의 글자'); ce = C.index('### 영어를 함께 적은 낱말')
c7 = []
for i in range(cs, ce):
    if C[i].startswith('| ') and not C[i].startswith('| 이 글의 글자') and not C[i].startswith('|---'):
        c = cells(C[i])
        if len(c) == 4: c7.append((i+1, c))
        else: print('C letter row cells', i+1, len(c))
print('letters: C rows', len(c7), 'ledger rows', len(led7))
key = lambda c: (norm(c[0]), norm(c[1]))
ld = {}
for ln, c in led7: ld.setdefault(key(c), []).append((ln, c))
used = set()
for ln, c in c7:
    k = key(c)
    if k not in ld:
        # 첫 칸만 같은 행
        cand = [(l2, c2) for l2, c2 in led7 if norm(c2[0]) == norm(c[0])]
        print(f'C:{ln} NO EXACT (글자,기록) MATCH: {c[0]} | {c[1]}  — 장부 후보 {[(l2, c2[1]) for l2, c2 in cand][:4]}')
        continue
    l2, c2 = ld[k][0]; used.add(l2)
    show(f'--- C:{ln} 장부:{l2} {c[0][:60]} [기록의 글자]', c[2], c2[2])
    show(f'--- C:{ln} 장부:{l2} {c[0][:60]} [이동]', c[3], c2[3])
for ln, c in led7:
    if ln not in used: print(f'장부:{ln} NOT IN C: {c[0]} | {c[1]}')
