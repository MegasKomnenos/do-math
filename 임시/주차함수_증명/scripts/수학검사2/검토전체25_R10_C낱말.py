# 부록 C 낱말 표의 행을 장부 3절의 같은 낱말 행과 맞대어 「처음 정의된 절」이 다른 곳과 장부에 없는 낱말을 보여 준다.
import re, io, sys
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
J = open(base + '장부_v2.md', encoding='utf-8').read().split('\n')
C = open(base + '장v2/부록C.md', encoding='utf-8').read().split('\n')
i3 = [i for i, l in enumerate(J) if l.startswith('## 3.')][0]; i4 = [i for i, l in enumerate(J) if l.startswith('## 4.')][0]
led = {}
for i in range(i3, i4):
    if J[i].startswith('| ') and not J[i].startswith('| 낱말') and not J[i].startswith('|---'):
        c = cells(J[i])
        if len(c) >= 4:
            for w in re.split(r',\s*', c[0]): led.setdefault(w.strip(), []).append((i+1, c))
            led.setdefault(c[0], []).append((i+1, c))
print('ledger words', len(led))
cs = C.index('### 낱말: 이 글의 용어와 기록의 용어'); ce = C.index('### 기록이 결과에 붙인 이름과 이 글의 번호')
for i in range(cs, ce):
    if C[i].startswith('| ') and not C[i].startswith('| 이 글의 용어') and not C[i].startswith('|---'):
        c = cells(C[i])
        w = c[0]
        hit = led.get(w) or led.get(re.split(r',\s*', w)[0]) or led.get(re.sub(r'\(.*\)', '', w).strip())
        if not hit:
            print(f'C:{i+1} [{w}] 장부 3절에 같은 낱말 행 없음 | C절={c[2]}')
            continue
        l2, c2 = hit[0]
        if c2[2] != c[2]:
            print(f'C:{i+1} [{w}] 절 C={c[2]} 장부:{l2}={c2[2]}')
        print(f'   = C:{i+1} [{w}] C기록용어「{c[1][:150]}」 || 장부첫판「{c2[3][:150]}」') if '--v' in sys.argv else None
