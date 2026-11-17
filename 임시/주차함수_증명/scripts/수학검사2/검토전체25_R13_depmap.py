# -*- coding: utf-8 -*-
# 의존지도 1절의 행을 장 파일에서 독립으로 다시 뽑아 견준다(자리 찾기·수 세기 전용; 판정은 원문을 읽고 한다).
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명'
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
LAB = re.compile(r'\{\{([0-9]+[A-Za-z]?):([^}]+)\}\}')
HEAD = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([0-9]+):([^}]+)\}\}(.*)$')
DEFER = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([0-9]+):([^}]+)\}\}(?:\([^)]*\))*의 증명')

def split_head(rest):
    # rest: 라벨 뒤의 문자열. (이름) [지위; 기록]. 본문
    s = rest.lstrip()
    name = None
    if s.startswith('('):
        d = 0
        for i, c in enumerate(s):
            if c == '(':
                d += 1
            elif c == ')':
                d -= 1
                if d == 0:
                    name = s[1:i]
                    s = s[i + 1:].lstrip()
                    break
    status = None
    if s.startswith('['):
        d = 0
        for i, c in enumerate(s):
            if c == '[':
                d += 1
            elif c == ']':
                d -= 1
                if d == 0:
                    status = s[1:i]
                    s = s[i + 1:]
                    break
    return name, status, s

stm = {}   # key -> dict
keys = []
owner = None
for f in order:
    sec = None
    owner = None  # 파일이 바뀌면 본문을 끊는다
    for ln, line in enumerate(io.open(os.path.join(base, '장v2', f + '.md'), encoding='utf-8'), 1):
        line = line.rstrip('\n')
        m = re.match(r'^(#{2,4}) (\S+)', line)
        if m:
            if len(m.group(1)) == 3:
                sec = m.group(2)
            continue
        md = DEFER.match(line)
        if md:
            owner = md.group(2) + ':' + md.group(3)
            stm[owner].setdefault('defer', []).append('%s:%d' % (f, ln))
            stm[owner]['body'].append(line)
            continue
        mh = HEAD.match(line)
        if mh:
            key = mh.group(2) + ':' + mh.group(3)
            name, status, tail = split_head(mh.group(4))
            hl = line.split('.**', 1)
            stm[key] = dict(file=f, line=ln, kind=mh.group(1), sec=sec, name=name, status=status, headtail=(hl[1] if len(hl) > 1 else ''), headline=hl[0], body=[])
            keys.append(key)
            owner = key
            continue
        if owner:
            stm[owner]['body'].append(line)

def labs(s):
    return [a + ':' + b for a, b in LAB.findall(s)]

for k in keys:
    s = stm[k]
    st = s['status'] or ''
    if ';' in st:
        a, b = st.split(';', 1)
    else:
        a, b = st, ''
    s['status_main'] = a.strip()
    s['records'] = sorted(set(re.findall(r'r[0-9a-f]{7}', b if b else (st if s['kind'] == '정의' else ''))))
    s['head_labs'] = [x for x in dict.fromkeys(labs(s['headline'])) if x != k]
    body = s['headtail'] + '\n' + '\n'.join(s['body'])
    s['body_labs'] = [x for x in dict.fromkeys(labs(body)) if x != k and not x.startswith('D:') and x not in s['head_labs']]
json.dump({k: {kk: vv for kk, vv in stm[k].items() if kk not in ('body', 'headtail')} for k in keys},
          io.open(os.path.join(base, 'scripts/수학검사2/검토전체25_R13_depmap.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=0)

# 의존지도 1절 표
rows = {}
L = io.open(os.path.join(base, '의존지도_v2.md'), encoding='utf-8').read().split('\n')
for i, line in enumerate(L[:283], 1):
    if line.startswith('| `{{'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        k = cells[0].strip('`{}')
        rows[k] = (i, cells)
print('rows', len(rows), 'stm', len(keys), 'missing rows', [k for k in keys if k not in rows], 'extra', [k for k in rows if k not in stm])
print('order same', list(rows) == keys)
nd = 0
for k in keys:
    i, c = rows[k]
    s = stm[k]
    if len(c) != 10:
        print('CELLS', i, k, len(c))
        continue
    diffs = []
    if c[1] != s['sec']:
        diffs.append('sec %s/%s' % (c[1], s['sec']))
    if s['name'] is not None and c[3] != s['name']:
        diffs.append('name T[%s] C[%s]' % (c[3], s['name']))
    stt = '정의' if s['kind'] == '정의' and not s['status_main'] else s['status_main']
    if s['kind'] == '정의' and s['status'] and ';' not in s['status']:
        stt = '정의'
    if c[4] != stt:
        diffs.append('status T[%s] C[%s]' % (c[4], stt))
    inp = c[5]
    if '본문 인용:' in inp:
        a, b = inp.split('본문 인용:', 1)
    else:
        a, b = inp, ''
    th, tb = labs(a), labs(b)
    if set(th) != set(s['head_labs']):
        diffs.append('headlabs T-C %s C-T %s' % (sorted(set(th) - set(s['head_labs'])), sorted(set(s['head_labs']) - set(th))))
    if set(tb) != set(s['body_labs']):
        diffs.append('bodylabs T-C %s C-T %s' % (sorted(set(tb) - set(s['body_labs'])), sorted(set(s['body_labs']) - set(tb))))
    trec = sorted(set(re.findall(r'r[0-9a-f]{7}', c[6])))
    if trec != s['records']:
        diffs.append('records T%s C%s' % (trec, s['records']))
    defer_t = re.findall(r'뒤로 미룬 증명 (\S+?\.md:\d+)', c[9])
    defer_c = [x.replace(':', '.md:') for x in s.get('defer', [])]
    if defer_t != defer_c:
        diffs.append('defer T%s C%s' % (defer_t, defer_c))
    if diffs:
        nd += 1
        print(i, k, ' || '.join(diffs))
print('rows with diffs', nd)
