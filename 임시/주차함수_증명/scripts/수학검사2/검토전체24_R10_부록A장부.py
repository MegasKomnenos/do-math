# 부록 A의 행을 장부 1.1·1.2절의 같은 글자 행과 맞대어 뜻·정의 절·기록의 글자가 같은지 본다(후보 찾기; 어긋난 행은 원문을 열어 확인한다).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
root = r'C:/math/임시/주차함수_증명/'
L = open(root+'장부_v2.md', encoding='utf-8').read().split('\n')
A = open(root+'장v2/부록A.md', encoding='utf-8').read().split('\n')
def cells(l):
    return [c.strip() for c in l.strip().strip('|').split(' | ')]
def norm(s):
    return s.replace('`', '').replace(' ', '')
# 장부 1.1: 22행부터 1.2 전까지, 1.2: 1.3 전까지
i11 = next(i for i,l in enumerate(L) if l.startswith('### 1.1'))
i12 = next(i for i,l in enumerate(L) if l.startswith('### 1.2'))
i13 = next(i for i,l in enumerate(L) if l.startswith('### 1.3'))
led = {}
for i in range(i11, i12):
    if L[i].startswith('| $'):
        c = cells(L[i]); led[norm(c[0])] = ('1.1', i+1, c[1], None, None, len(c))
for i in range(i12, i13):
    if L[i].startswith('| $'):
        c = cells(L[i]); led[norm(c[0])] = ('1.2', i+1, c[2], c[3], c[-1], len(c))
print('장부 1.1+1.2 행 수', len(led))
seen = set()
mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
nrow = 0
for i, l in enumerate(A):
    if not l.startswith('| $'): continue
    nrow += 1
    c = cells(l)
    key = norm(c[0])
    if key not in led:
        print(f'[부록A {i+1}] 장부에 같은 글자 칸 없음: {c[0]}'); continue
    seen.add(key)
    src, ln, mean, sec, rec, nc = led[key]
    if src == '1.2' and nc != 7: print(f'[장부 {ln}] 칸 수 {nc} (쪼갬 주의)')
    if len(c) != 4: print(f'[부록A {i+1}] 칸 수 {len(c)} (쪼갬 주의)')
    if norm(mean) != norm(c[1]):
        print(f'[부록A {i+1} / 장부 {ln}] 뜻 다름: {c[0]}')
        if mode == 'full':
            print('   A :', c[1]); print('   장:', mean)
    if sec is not None and norm(sec) != norm(c[2]):
        print(f'[부록A {i+1} / 장부 {ln}] 정의 절 다름: {c[0]} | A: {c[2]} | 장부: {sec}')
    if rec is not None and norm(rec) != norm(c[3]):
        print(f'[부록A {i+1} / 장부 {ln}] 기록의 글자 다름: {c[0]}')
        if mode == 'full':
            print('   A :', c[3]); print('   장:', rec)
print('부록 A 행 수', nrow)
print('== 장부에 있으나 부록 A에 없는 글자')
for k, v in led.items():
    if k not in seen: print('  ', v[0], v[1], k[:80], '| 정의 절:', v[3])
