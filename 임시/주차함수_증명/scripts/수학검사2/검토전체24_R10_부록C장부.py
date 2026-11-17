# 부록 C 셋째 표(기록의 글자와 이 글의 글자)를 장부 7절의 표와 행 순서대로 맞댄다(후보 찾기).
import re, io, sys, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
root = r'C:/math/임시/주차함수_증명/'
L = open(root+'장부_v2.md', encoding='utf-8').read().split('\n')
C = open(root+'장v2/부록C.md', encoding='utf-8').read().split('\n')
def cells(l): return [c.strip() for c in l.strip().strip('|').split(' | ')]
def norm(s): return s.replace('`', '').replace(' ', '')
i7 = next(i for i,l in enumerate(L) if l.startswith('## 7.'))
i8 = next(i for i,l in enumerate(L) if l.startswith('## 8.'))
led = [(i+1, cells(L[i])) for i in range(i7, i8) if L[i].startswith('| $') or L[i].startswith('| (')]
a = next(i for i,l in enumerate(C) if l.startswith('### 기록의 글자와'))
b = next(i for i,l in enumerate(C) if l.startswith('### 영어를'))
app = [(i+1, cells(C[i])) for i in range(a, b) if C[i].startswith('| ') and not C[i].startswith('| 이 글의') and not C[i].startswith('|---')]
print('장부 7절 행', len(led), '부록 C 행', len(app))
# 장부 7절에서 표 아닌 줄 가운데 '|'로 시작하는 것 전부 세기
allrows = [i+1 for i in range(i7, i8) if L[i].startswith('|') and not L[i].startswith('|---') and not L[i].startswith('| 이 글의')]
print('장부 7절의 표 행(머리 제외) 전부', len(allrows))
keyL = [norm(c[0]) + '|' + norm(c[1]) for _, c in led]
keyA = [norm(c[0]) + '|' + norm(c[1]) for _, c in app]
sm = difflib.SequenceMatcher(None, keyL, keyA, autojunk=False)
full = len(sys.argv) > 1
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        for d in range(i2 - i1):
            ln, cl = led[i1+d]; an, ca = app[j1+d]
            if len(cl) != 4 or len(ca) != 4: print(f'칸 수: 장부 {ln}={len(cl)} 부록 {an}={len(ca)}'); continue
            if norm(cl[2]) != norm(ca[2]):
                print(f'[C {an}/장부 {ln}] 기록의 글자 다름: {ca[0]} {ca[1]}')
                if full: print('    C :', ca[2]); print('    장:', cl[2])
            if norm(cl[3]) != norm(ca[3]):
                s = difflib.SequenceMatcher(None, ca[3], cl[3], autojunk=False)
                segs = [f'【C:{ca[3][x1:x2]}】【장부:{cl[3][y1:y2]}】' for t, x1, x2, y1, y2 in s.get_opcodes() if t != 'equal']
                print(f'[C {an}/장부 {ln}] 이동 다름: {ca[0]} {ca[1][:30]} ' + ' '.join(segs)[:260])
    else:
        for d in range(i1, i2): print(f'<< 장부에만 {led[d][0]}: {led[d][1][0]} | {led[d][1][1][:60]}')
        for d in range(j1, j2): print(f'>> 부록 C에만 {app[d][0]}: {app[d][1][0]} | {app[d][1][1][:60]}')
