# G12: 부록 D(장2~장6) 항목의 「산술 등급」·「독립 재계산」 줄을 장11.md 11.2 표의 같은 행과 대조한다.
import re, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = pathlib.Path(r"C:\math\임시\주차함수_증명\장v2")
files = ["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]
items = {}
for f in files:
    txt = (root/f).read_text(encoding='utf-8')
    parts = re.split(r'(?m)^### D\.\{\{D:([^}]+)\}\}', txt)
    for i in range(1, len(parts), 2):
        lab, body = parts[i], parts[i+1]
        d = {'file': f}
        m = re.search(r'\*\*산술 등급\.\*\*\s*(.*)', body); d['grade'] = m.group(1).strip() if m else None
        m = re.search(r'\*\*독립 재계산\.\*\*\s*(.*)', body); d['indep'] = m.group(1).strip() if m else None
        m = re.search(r'^### .*?\((.*)\)\s*$', '### '+parts[i-1].split('\n')[-1] if False else '', re.M)
        # 제목 줄의 괄호 안 진술
        head = re.search(r'(?m)^### D\.\{\{D:'+re.escape(lab)+r'\}\}(.*)$', txt).group(1)
        d['head'] = head.strip()
        items[lab] = d
ch11 = (root/"장11.md").read_text(encoding='utf-8').split('\n')
rows = {}
for line in ch11[18:64]:
    if not line.startswith('| 부록 D.{{D:'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    lab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
    rows[lab] = cells
for lab, d in items.items():
    print('='*8, lab, d['file'])
    if lab not in rows:
        print('  !! 표에 행 없음'); continue
    c = rows[lab]
    stmt, grade, where, recomp, indep = c[1], c[2], c[3], c[4], c[5]
    # 머리 진술 대조
    head_stmts = re.findall(r'(정리|명제|보조정리|따름정리) \{\{[^}]+\}\}', d['head'])
    tbl_stmts = re.findall(r'(정리|명제|보조정리|따름정리) \{\{[^}]+\}\}', stmt)
    hs = re.findall(r'\{\{[^}]+\}\}', d['head']); ts = re.findall(r'\{\{[^}]+\}\}', stmt)
    print('  진술 라벨 D   :', hs)
    print('  진술 라벨 표  :', ts, 'OK' if hs==ts else '!! 다름')
    print('  산술등급 D    :', d['grade'])
    print('  산술등급 표   :', grade)
    m = re.match(r'〔(.*?)〕\s*(.*)', d['indep'], re.S)
    br, rest = m.group(1), m.group(2)
    print('  꺾쇠 D        :', '〔'+br+'〕')
    print('  꺾쇠 표       :', recomp, 'OK' if recomp=='〔'+br+'〕' else '!! 다름')
    if rest == indep:
        print('  독립재계산 서술: 같음')
    else:
        import difflib
        print('  독립재계산 서술: !! 다름')
        sm = difflib.SequenceMatcher(None, rest, indep)
        for op,a1,a2,b1,b2 in sm.get_opcodes():
            if op!='equal':
                print(f'    {op}: D[{rest[max(0,a1-20):a2+20]!r}] / 표[{indep[max(0,b1-20):b2+20]!r}]')
