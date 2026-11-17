# 수리 전체24 ZL — 읽기 전용: 장부 1.2의 「기록의 글자」 열과 7절(기록 글자 대응)의 (기호, 기록) 쌍 맞대기.
# 검토전체22_R13S7_cross.py의 뒤 판: 줄 범위를 절 머리에서 찾고(고정값 없음), 1.2의 마지막 칸을 「글자 ([식별자]…)」 묶음으로 갈라
# 묶음마다 (기록 글자, 식별자)를 낸다. 한 행에 기호가 여럿이면 그 행의 기호 전부를 한 무리로 보고 7절의 같은 머리 행들의 식별자 합집합과 견준다.
# 판정은 행 원문과 기록 원문으로 한다(후보 찾기용).
# 쓰기: python -I -X utf8 수리전체24_ZL_cross.py [a|b|c]   (a: 1.2에만 있는 쌍, b: 7절에만 있는 쌍, c: 머리 없는 것; 기본 a)
import io, re, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = open(os.path.join(BASE, '장부_v2.md'), encoding='utf-8').read().split('\n')
def find(prefix):
    for i, l in enumerate(L):
        if l.startswith(prefix):
            return i
    raise SystemExit('머리 없음: ' + prefix)
a12, b12 = find('### 1.2 '), find('### 1.3 ')
a7, b7 = find('## 7. '), find('## 8. ')
BS = chr(92)
IDX = '[nkmtjiNqdyYrsvcLhx0-9,+' + BS + '-]|' + BS + BS + 'ell|' + BS + BS + 'nu'
def head(tok):
    t = tok.strip().replace(' ', '')
    t = re.sub(r'\^\{([^{}]*)\}', r'^\1', t)
    t = t.replace(BS + 'prime', "'")
    t = re.sub(r':=.*$', '', t)
    while True:
        t2 = re.sub(r'\([^()]*\)$', '', t)
        if t2 == t: break
        t = t2
    t = re.sub(r'_\{((?:%s)+)\}' % IDX, '', t)
    t = re.sub(r'_(?:%s)' % IDX, '', t)
    t = re.sub(r'\{\}', '', t)
    return t
def toks(cell):
    out = []
    for seg in re.findall(r'\$([^$]+)\$', cell):
        depth = 0; cur = ''
        for ch in seg:
            if ch in '({[': depth += 1
            if ch in ')}]': depth -= 1
            if ch == ',' and depth == 0:
                out.append(cur); cur = ''
            else: cur += ch
        out.append(cur)
    return [o.strip() for o in out if o.strip()]
def cells(l):
    # 수식 안의 세로줄은 칸 구분이 아니다
    out = []; cur = ''; inm = False; i = 0
    while i < len(l):
        ch = l[i]
        if ch == BS and i + 1 < len(l):
            cur += l[i:i+2]; i += 2; continue
        if ch == '$': inm = not inm
        if ch == '|' and not inm:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
        i += 1
    out.append(cur.strip())
    return out[1:-1]
RID = re.compile(r'\[(r[0-9a-f]{7})\]')
rows12 = []
for i in range(a12, b12):
    l = L[i]
    if not l.startswith('| $'): continue
    c = cells(l)
    heads = [head(t) for t in toks(c[0])]
    rows12.append({'line': i + 1, 'heads': heads, 'first': c[0], 'recs': set(RID.findall(c[-1])), 'last': c[-1]})
rows7 = []
for i in range(a7, b7):
    l = L[i]
    if not l.startswith('| ') or l.startswith('| 이 글의 글자') or l.startswith('|---'): continue
    c = cells(l)
    if len(c) < 3: continue
    heads = [head(t) for t in toks(c[0])]
    rows7.append({'line': i + 1, 'heads': heads, 'first': c[0], 'recs': set(RID.findall(c[1])), 'letters': c[2]})
h7 = {}
for r in rows7:
    for h in r['heads']:
        h7.setdefault(h, []).append(r)
h12 = {}
for r in rows12:
    for h in r['heads']:
        h12.setdefault(h, []).append(r)
# 7절에서 식별자가 나오는 모든 행(머리와 무관) — 그 기록의 절 묶음 행을 찾는 데 쓴다
rec7 = {}
for r in rows7:
    for x in r['recs']:
        rec7.setdefault(x, []).append(r['line'])
mode = sys.argv[1] if len(sys.argv) > 1 else 'a'
if mode == 'a':
    print('== (a) 1.2 「기록의 글자」 열에는 있는데 7절의 같은 머리 행들에 없는 (행, 기록)')
    n = 0
    for r in rows12:
        if not r['recs']: continue
        got = set(); lines = []
        for h in r['heads']:
            for s in h7.get(h, []):
                got |= s['recs']; lines.append(s['line'])
        miss = sorted(r['recs'] - got)
        if miss:
            n += 1
            print(f"{r['line']} {r['first'][:60]} | 7절 같은 머리 행 {sorted(set(lines))[:8]} | 7절에 없는 기록 {miss}")
            for x in miss:
                # 그 기록이 든 묶음 글귀
                for seg in re.split(r';\s*', r['last']):
                    if x in seg:
                        print(f"      1.2: {seg[:160]}")
                print(f"      7절에서 [{x}]가 든 행: {rec7.get(x, [])[:10]}")
    print('후보 행', n)
elif mode == 'b':
    print('== (b) 7절에는 있는데 1.2의 같은 머리 행 열에 없는 (행, 기록) — 7절 행의 머리가 모두 1.2의 한 행에 드는 것만')
    n = 0
    for s in rows7:
        tg = set()
        for h in s['heads']:
            for r in h12.get(h, []):
                tg.add(r['line'])
        if len(tg) != 1: continue
        r = [x for x in rows12 if x['line'] in tg][0]
        miss = sorted(s['recs'] - r['recs'])
        if miss:
            n += 1
            print(f"{s['line']} {s['first'][:50]} | 1.2 행 {r['line']} | 1.2 열에 없는 기록 {miss}")
    print('후보 행', n)
else:
    print('== (c) 7절 머리 가운데 1.2에 머리가 없는 것')
    for s in rows7:
        for h in s['heads']:
            if h not in h12:
                print(s['line'], h)
