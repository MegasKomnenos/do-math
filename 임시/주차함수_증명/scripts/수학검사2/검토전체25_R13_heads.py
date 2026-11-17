# -*- coding: utf-8 -*-
# 장 파일의 진술 머리를 순서대로 뽑아 대응표와 견준다(자리 찾기·수 세기 전용).
import re, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명'
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
head_re = re.compile(r'^\*\*(\S+) \{\{([0-9A-Za-z]+):([^}]+)\}\}(.*)$')
def paren_name(rest):
    rest = rest.lstrip()
    if not rest.startswith('('):
        return None, rest
    d = 0
    for i, c in enumerate(rest):
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return rest[1:i], rest[i+1:]
    return None, rest
heads = []
for f in order:
    p = os.path.join(base, '장v2', f + '.md')
    sec = None
    for ln, line in enumerate(io.open(p, encoding='utf-8'), 1):
        m = re.match(r'^(#{2,4}) (\S+)', line)
        if m:
            if len(m.group(1)) == 3:
                sec = m.group(2)
            elif len(m.group(1)) == 2:
                sec = m.group(2).rstrip('.')
            continue
        m = head_re.match(line)
        if not m:
            continue
        kind, ch, lab, rest = m.groups()
        if rest.startswith('의 증명') or rest.startswith('의 ') or rest.startswith('에 ') or rest.startswith('과 ') or rest.startswith('와 '):
            heads.append(None) if False else None
            continue
        name, rest2 = paren_name(rest)
        st = re.match(r'\s*\[([^\]]*(?:\[[^\]]*\][^\]]*)*)\]', rest2)
        heads.append(dict(file=f, line=ln, kind=kind, ch=ch, lab=lab, name=name, sec=sec, status=st.group(1) if st else None, rest=rest[:80]))
# number
cnt = {}
for h in heads:
    chn = re.match(r'\d+', h['ch']).group(0)
    cnt[chn] = cnt.get(chn, 0) + 1
    h['num'] = '%s.%d' % (chn, cnt[chn])
json.dump(heads, io.open(os.path.join(base, 'scripts/수학검사2/검토전체25_R13_heads.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=0)
print(len(heads), cnt)
kinds = {}
for h in heads:
    kinds[h['kind']] = kinds.get(h['kind'], 0) + 1
print(kinds)
# table
rows = []
for line in io.open(os.path.join(base, '대조v2/라벨_번호_대응표_1114.md'), encoding='utf-8'):
    if line.startswith('| `{{'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        rows.append(cells)
print('table rows', len(rows))
tl = {}
for r in rows:
    m = re.match(r'`\{\{([^:]+):([^}]+)\}\}`', r[0])
    tl[(m.group(1), m.group(2))] = r
hl = {(h['ch'], h['lab']): h for h in heads}
print('in chapters not table:', [k for k in hl if k not in tl])
print('in table not chapters:', [(k, tl[k][3]) for k in tl if k not in hl])
# compare order & fields
i = 0
for h in heads:
    k = (h['ch'], h['lab'])
    if k not in tl: continue
    r = tl[k]
    diffs = []
    if r[1] != h['kind']: diffs.append('kind %s/%s' % (r[1], h['kind']))
    nm = h['name'] if h['name'] is not None else '—'
    if r[2] != nm: diffs.append('name T[%s] C[%s]' % (r[2], nm))
    if r[3] != h['num']: diffs.append('num %s/%s' % (r[3], h['num']))
    if r[5] != h['sec']: diffs.append('sec %s/%s' % (r[5], h['sec']))
    if diffs:
        print(h['file'], h['line'], k, '; '.join(diffs))
# order check
tk = [k for k in tl if k in hl]
hk = [k for k in hl if k in tl]
print('order same:', tk == hk)
