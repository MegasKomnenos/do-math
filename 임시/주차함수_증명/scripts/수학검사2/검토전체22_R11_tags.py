# R11 검산: 부록 D 항목(2·3·4·5A장)의 「독립 재계산」 꺾쇠 괄호와 10.2절 표의 「재계산」 열, 항목 머리의 진술과 표의 「확인하는 진술」 열을 맞춘다
import re, sys, io
base = sys.argv[1]
files = ['부록D_장2.md', '부록D_장3.md', '부록D_장4.md', '부록D_장5A.md']
items = {}
for f in files:
    txt = open(f'{base}/{f}', encoding='utf-8').read()
    parts = re.split(r'(?m)^### D\.\{\{D:([a-zA-Z0-9\-]+)\}\}', txt)
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i+1]
        head = body.split('\n', 1)[0]
        m = re.search(r'\*\*독립 재계산\.\*\* (〔[^〕]*〕)', body)
        g = re.search(r'\*\*산술 등급\.\*\* ([^\n]*)', body)
        items[name] = (head, m.group(1) if m else None, g.group(1) if g else None)
t10 = open(f'{base}/장10.md', encoding='utf-8').read()
rows = {}
for line in t10.split('\n'):
    m = re.match(r'\| 부록 D\.\{\{D:([a-zA-Z0-9\-]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (〔.*〕) \|', line)
    if m: rows[m.group(1)] = m.groups()[1:]
for name, (head, tag, grade) in items.items():
    r = rows.get(name)
    print('==', name)
    if r is None:
        print('  표에 행 없음'); continue
    print('  재계산 꺾쇠 일치:', tag == r[3])
    if tag != r[3]:
        print('   D :', tag); print('   표:', r[3])
    labs_head = sorted(set(re.findall(r'\{\{[0-9]+:[a-zA-Z0-9\-]+\}\}', head)))
    labs_row = sorted(set(re.findall(r'\{\{[0-9]+:[a-zA-Z0-9\-]+\}\}', r[0])))
    print('  머리의 진술 == 표의 진술:', labs_head == labs_row, labs_head if labs_head != labs_row else '', labs_row if labs_head != labs_row else '')
    print('  표의 산술 등급:', r[1], '| 놓인 곳:', r[2])
    print('  D의 산술 등급 줄 머리:', (grade or '')[:110])
