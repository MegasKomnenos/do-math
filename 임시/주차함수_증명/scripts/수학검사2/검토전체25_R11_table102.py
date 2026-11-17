# R11: 10.2절 표의 「재계산」 칸과 부록 D 항목 「독립 재계산」 줄의 꺾쇠가 글자까지 같은지
import re, io
t10 = io.open('장v2/장10.md', encoding='utf-8').read()
rows = {}
for line in t10.splitlines():
    m = re.match(r'\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (〔.*〕) \|$', line)
    if m: rows[m.group(1)] = m.groups()[1:]
for fn in ['부록D_장2.md', '부록D_장3.md', '부록D_장4.md', '부록D_장5A.md']:
    txt = io.open('장v2/' + fn, encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{D:([^}]+)\}\}(.*?)$(.*?)(?=^### |\Z)', txt, re.S | re.M):
        item, head, body = m.group(1), m.group(2), m.group(3)
        br = re.search(r'^\*\*독립 재계산\.\*\* (〔.*?〕)', body, re.M).group(1)
        grade = re.search(r'^\*\*산술 등급\.\*\* (.*)$', body, re.M).group(1)
        r = rows[item]
        labels_head = sorted(set(re.findall(r'\{\{([0-9A-Za-z]+:[^}]+)\}\}', head)))
        labels_row = sorted(set(re.findall(r'\{\{([0-9A-Za-z]+:[^}]+)\}\}', r[0])))
        print(item, '| bracket same:', br == r[3], '| statements same:', labels_head == labels_row, '| row grade:', r[1], '| place:', r[2])
        if labels_head != labels_row: print('   head', labels_head, 'row', labels_row)
