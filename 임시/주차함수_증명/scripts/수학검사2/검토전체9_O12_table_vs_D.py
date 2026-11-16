# 11.2 표의 「재계산」·「독립 재계산」 열과 부록 D 항목의 「독립 재계산」 줄을 맞세워 다른 자리를 찾는다 (자리 찾기용).
import re, sys, io, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = "C:/math/임시/주차함수_증명/장v2/"
files = ["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]
items = {}
heads = {}
for f in files:
    txt = open(base+f, encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{D:([^}]+)\}\} (.*?) \((.*)\)\s*$', txt, re.M):
        heads[m.group(1)] = (m.group(2), m.group(3), f)
    parts = re.split(r'^### D\.\{\{D:([^}]+)\}\}', txt, flags=re.M)
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i+1]
        d = {}
        for lab in ['확인하는 진술','식','알고리즘','범위','산술 등급','결과','독립 재계산','자료','출처']:
            mm = re.search(r'\*\*'+lab+r'\.\*\* (.*?)(?=\n\n\*\*|\n\n###|\Z)', body, re.S)
            d[lab] = mm.group(1).strip() if mm else None
        items[name] = d
tab = open(base+"장11.md", encoding='utf-8').read()
rows = {}
for line in tab.splitlines():
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        name = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
        rows[name] = cells
for name, d in items.items():
    print("=====", name, "| head:", heads.get(name))
    if name not in rows:
        print("  !! 11.2 표에 행 없음"); continue
    cells = rows[name]
    print("  표: 진술=", cells[1], "| 등급=", cells[2], "| 쓰인 곳=", cells[3])
    print("  D 산술 등급 줄:", d['산술 등급'])
    ir = d['독립 재계산'] or ''
    m = re.match(r'〔(.*?)〕\s*(.*)', ir, re.S)
    br, rest = (m.group(1), m.group(2)) if m else ('', ir)
    if '〔'+br+'〕' != cells[4]:
        print("  !! 꺾쇠 다름:\n    D :", br, "\n    표:", cells[4])
    rest_n = re.sub(r'\s+',' ',rest)
    cell_n = re.sub(r'\s+',' ',cells[5])
    if rest_n != cell_n:
        print("  !! 서술 다름:")
        for op in difflib.SequenceMatcher(None, rest_n, cell_n).get_opcodes():
            if op[0] != 'equal':
                print("    ", op[0], "D:", repr(rest_n[op[1]:op[2]]), "표:", repr(cell_n[op[3]:op[4]]))
