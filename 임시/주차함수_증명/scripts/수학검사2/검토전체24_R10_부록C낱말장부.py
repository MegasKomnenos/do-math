# 부록 C 낱말 표의 행을 장부 3절의 같은 낱말 행과 맞대어 「처음 정의된 절」이 같은지 본다(후보 찾기).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
root = r'C:/math/임시/주차함수_증명/'
L = open(root+'장부_v2.md', encoding='utf-8').read().split('\n')
C = open(root+'장v2/부록C.md', encoding='utf-8').read().split('\n')
def cells(l): return [c.strip() for c in l.strip().strip('|').split(' | ')]
i3 = next(i for i,l in enumerate(L) if l.startswith('## 3.'))
i4 = next(i for i,l in enumerate(L) if l.startswith('## 4.'))
led = {}
for i in range(i3, i4):
    if L[i].startswith('| ') and not L[i].startswith('| 낱말') and not L[i].startswith('|---'):
        c = cells(L[i])
        for t in re.split(r', |·', re.sub(r'\([^)]*\)', '', c[0])):
            led.setdefault(t.strip(), []).append((i+1, c))
a = next(i for i,l in enumerate(C) if l.startswith('### 낱말'))
b = next(i for i,l in enumerate(C) if l.startswith('### 기록이 결과에'))
for i in range(a, b):
    l = C[i]
    if not l.startswith('| ') or l.startswith('| 이 글의') or l.startswith('|---'): continue
    c = cells(l)
    terms = [t.strip() for t in re.split(r', |·', re.sub(r'\([^)]*\)', '', c[0])) if t.strip()]
    for t in terms:
        if t not in led:
            print(f'[C {i+1}] 「{t}」 장부 3절에 같은 낱말 칸 없음 (C 절: {c[2]})'); continue
        for ln, lc in led[t]:
            if lc[2].replace(' ', '') != c[2].replace(' ', ''):
                print(f'[C {i+1}/장부 {ln}] 「{t}」 절 다름: C={c[2]} / 장부={lc[2]}')
            if len(sys.argv) > 1:
                print(f'   [C {i+1}/장부 {ln}] 「{t}」\n      C 기록의 용어: {c[1][:200]}\n      장부 첫 판의 낱말: {lc[3][:200]}')
