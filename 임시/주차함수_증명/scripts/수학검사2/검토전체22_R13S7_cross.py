# 1.2의 「기록의 글자」 열(=부록 A의 열)과 7절(=부록 C의 글자 표)의 (기호, 기록) 쌍 맞대기 — 후보 찾기용. 판정은 행 원문으로.
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
BS = chr(92)
IDX = '[nkmtjiNqdyYrsvcLhx0-9,+' + BS + '-]|' + BS + BS + 'ell|' + BS + BS + 'nu'
def head(tok):
    t = tok.strip().replace(' ', '')
    t = re.sub(r'\^\{([^{}]*)\}', r'^\1', t)
    t = t.replace(chr(92) + 'prime', "'")
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
g12 = {}
for i in range(48, 288):
    l = L[i]
    if not l.startswith('| $'): continue
    c = l.strip().strip('|').split(' | ')
    recs = set(re.findall(r'\[(r[0-9a-f]{7})\]', c[-1]))
    for t in toks(c[0]):
        g12.setdefault(head(t), {'line': i+1, 'recs': set(), 'tok': t})['recs'] |= recs
s7 = {}
for i in range(1236, 1430):
    c = L[i].strip().strip('|').split(' | ')
    recs = set(re.findall(r'\[(r[0-9a-f]{7})\]', c[1]))
    for t in toks(c[0]):
        s7.setdefault(head(t), {'lines': [], 'recs': set()})
        s7[head(t)]['lines'].append(i+1); s7[head(t)]['recs'] |= recs
mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
print('== 1.2 열에는 있는데 7절의 같은 머리 행에 없는 (기호, 기록)')
for h, d in sorted(g12.items(), key=lambda x: x[1]['line']):
    if h in s7:
        miss = d['recs'] - s7[h]['recs']
        if miss: print(d['line'], d['tok'], '| 머리', h, '| 7절 행', s7[h]['lines'][:8], '| 7절에 없는 기록', sorted(miss))
    elif d['recs']:
        print(d['line'], d['tok'], '| 머리', h, '| 7절에 머리 없음 | 1.2 기록', sorted(d['recs']))
print('== 7절에는 있는데 1.2의 같은 머리 행 열에 없는 (기호, 기록)')
for h, d in sorted(s7.items(), key=lambda x: x[1]['lines'][0]):
    if h in g12:
        miss = d['recs'] - g12[h]['recs']
        if miss: print(d['lines'][:8], '머리', h, '| 1.2 행', g12[h]['line'], g12[h]['tok'], '| 1.2 열에 없는 기록', sorted(miss))
print('== 7절 머리 가운데 1.2에 머리가 없는 것')
for h, d in sorted(s7.items(), key=lambda x: x[1]['lines'][0]):
    if h not in g12: print(d['lines'][:6], h)
