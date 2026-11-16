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
                mn = re.match(r'\s*\((.*)\)\s*\[[^\[\]]*\]\.?\s*$', rest)
                name = mn.group(1) if mn else ''
                heads[m.group(2)] = (f, i, name)
# 4절: 이 글의 이름 + 기록의 이름
lines = open(os.path.join(root, '장부_v2.md'), encoding='utf-8').read().split('\n')
n = 0
for i in range(743, 1197):
    line = lines[i-1]
    m = re.match(r'\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| \{\{([^}]+)\}\} \|\s*$', line)
    if not m: continue
    old, kind, name, rec, sec, lab = m.groups()
    if lab not in heads: continue
    hname = heads[lab][2]
    comb = name if not rec else (f'{name}; {rec}' if name else rec)
    if comb.strip() != hname.strip():
        print(f'4절 L{i} {lab}: 4절 "{comb}" vs head "{hname}" ({heads[lab][0]}:{heads[lab][1]})'); n += 1
# 대응표 names
with open(os.path.join(root, '대조v2', '라벨_번호_대응표_1114.md'), encoding='utf-8') as fh:
    for i, line in enumerate(fh, 1):
        m = re.match(r'\| `\{\{([^}]+)\}\}` \| (\S+) \| (.*?) \| (\S+) \| (.*?) \| (\S+) \|', line)
        if m and m.group(1) in heads:
            nm = m.group(3)
            hname = heads[m.group(1)][2]
            if nm == '—': nm = ''
            if nm.strip() != hname.strip():
                print(f'대응표 L{i} {m.group(1)}: "{nm}" vs head "{hname}"'); n += 1
print('mismatches', n)
