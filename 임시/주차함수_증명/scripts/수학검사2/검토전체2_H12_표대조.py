# -*- coding: utf-8 -*-
"""H12: 부록 D 항목(장2~6)의 「산술 등급」·「독립 재계산」 줄과 11.2 표의 같은 행 대조."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = r"C:\math\임시\주차함수_증명"
files = ["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]
items = {}
for f in files:
    txt = open(f"{base}\장v2\{f}", encoding='utf-8').read()
    parts = re.split(r'(?m)^### D\.\{\{D:([^}]+)\}\}', txt)
    for i in range(1, len(parts), 2):
        lab = parts[i]; body = parts[i+1]
        d = {}
        for key in ["확인하는 진술","산술 등급","독립 재계산","범위","쓰인 곳"]:
            m = re.search(r'\*\*'+key+r'\.\*\*\s*(.*)', body)
            d[key] = m.group(1).strip() if m else None
        # title
        m = re.match(r'\s*(.*)', body.split('\n')[0]); d['title']=m.group(1)
        d['file']=f
        items[lab]=d
# 11.2 table
t = open(f"{base}\장v2\장11.md", encoding='utf-8').read().split('\n')
rows = {}
for ln, line in enumerate(t,1):
    m = re.match(r'\| 부록 D\.\{\{D:([^}]+)\}\} \|(.*)\|\s*$', line)
    if m:
        cells = [c.strip() for c in m.group(2).split(' | ')]
        rows[m.group(1)] = dict(line=ln, cells=cells)
for lab,d in items.items():
    print("="*80); print(lab, d['file'])
    if lab not in rows:
        print("  !! 11.2 표에 없음"); continue
    r = rows[lab]; c = r['cells']
    if len(c)!=5:
        print("  !! 칸 수", len(c), c[:2])
    stmt, grade, where, recomp, indep = c
    # 산술 등급: 부록은 괄호 설명 포함; 표는 짧음
    g_app = d['산술 등급']
    g_app_short = re.sub(r'\(.*?\)','',g_app).strip().rstrip('.')
    print("  등급 부록:", g_app[:120]); print("  등급 표  :", grade)
    # 독립 재계산: 부록 = 〔...〕 + 본문; 표 = 재계산 열 〔...〕, 독립 재계산 열 본문
    ir = d['독립 재계산']
    m = re.match(r'(〔[^〕]*〕)\s*(.*)', ir)
    br, body = (m.group(1), m.group(2)) if m else (None, ir)
    if br != recomp:
        print("  !! 꺾쇠 다름\n     부록:", br, "\n     표  :", recomp)
    else: print("  꺾쇠 같음")
    if body.strip() != indep.strip():
        print("  !! 독립 재계산 본문 다름")
        import difflib
        for op in difflib.SequenceMatcher(None, body, indep).get_opcodes():
            if op[0]!='equal':
                print("     ", op[0], repr(body[op[1]:op[2]]), "->", repr(indep[op[3]:op[4]]))
    else: print("  독립 재계산 본문 같음")
    # 진술 칸: 머리의 괄호와 비교
    tm = re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$', d['title'])
    print("  제목 괄호:", tm.group(1) if tm else None)
    print("  표 진술  :", stmt)
    print("  쓰인 곳  :", where)
