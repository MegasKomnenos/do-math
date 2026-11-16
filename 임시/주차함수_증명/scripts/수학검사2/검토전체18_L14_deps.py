import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명'
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
HEAD = re.compile(r'\*\*(정의|정리|보조정리|명제|따름정리) \{\{([^}]+)\}\}(?!의 증명)(.*?)\*\*')
heads = {}
for f in files:
    with open(os.path.join(root, '장v2', f + '.md'), encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            m = HEAD.match(line)
            if m:
                rest = m.group(3)
                mb = re.search(r'\[([^\[\]]*)\]\.?\s*$', rest)
                bracket = mb.group(1) if mb else ''
                status = bracket.split(';')[0].strip()
                rec = bracket.split(';', 1)[1].strip() if ';' in bracket else ''
                labs = [L for L in re.findall(r'\{\{([^}]+)\}\}', line) if L != m.group(2)]
                name = ''
                mn = re.match(r'\s*\((.*)\)\s*\[[^\[\]]*\]\.?\s*$', rest)
                if mn:
                    name = mn.group(1)
                heads[m.group(2)] = (f, i, status, rec, labs, name, m.group(1), bracket)
rows = {}
with open(os.path.join(root, '의존지도_v2.md'), encoding='utf-8') as fh:
    for i, line in enumerate(fh, 1):
        if i > 409:
            break
        m = re.match(r'\| `\{\{([^}]+)\}\}` \| (\S+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
        if m:
            rows[m.group(1)] = (i,) + m.groups()[1:]
n = 0
for lab, (f, i, status, rec, labs, name, kind, bracket) in heads.items():
    if lab not in rows:
        continue
    r = rows[lab]
    li, sec, old, gist, st, inputs, recc, lit, appD, note = r
    if kind == '정의':
        if st != '정의':
            print(f'{lab} 의존지도 L{li} 지위 "{st}" vs head "{status}"'); n += 1
    elif st != status:
        print(f'{lab} 의존지도 L{li} 지위 "{st}" vs head "{status}" ({f}:{i})'); n += 1
    declared = inputs.split('본문 인용:')[0]
    dl = set(re.findall(r'\{\{([^}]+)\}\}', declared))
    hl = set(labs)
    if dl != hl:
        print(f'{lab} 의존지도 L{li} declared inputs {sorted(dl)} vs head-line labels {sorted(hl)} ({f}:{i})'); n += 1
    rid_head = set(re.findall(r'r[0-9a-f]{7}', rec))
    rid_row = set(re.findall(r'r[0-9a-f]{7}', recc.split('/')[0]))
    if kind != '정의' and rid_head != rid_row:
        print(f'{lab} 의존지도 L{li} 기록 {sorted(rid_row)} vs head bracket {sorted(rid_head)} ({f}:{i})'); n += 1
    if kind == '정의':
        rid_b = set(re.findall(r'r[0-9a-f]{7}', bracket))
        if rid_b != rid_row:
            print(f'{lab} 의존지도 L{li} 정의 기록 {sorted(rid_row)} vs head bracket {sorted(rid_b)} ({f}:{i})'); n += 1
    gist_norm = gist.strip()
    if name and gist_norm != name:
        print(f'{lab} 의존지도 L{li} 요지 "{gist[:70]}" vs head name "{name[:70]}"'); n += 1
    if not name and gist_norm and '요지' not in note and old != '새 진술' and False:
        pass
print('mismatches', n)
