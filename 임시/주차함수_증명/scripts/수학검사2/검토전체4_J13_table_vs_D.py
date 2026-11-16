# 부록 D 항목(7A·7B·8·9·10)의 머리·산술 등급·독립 재계산 줄과 11.2절 표의 같은 행을 기계적으로 맞춘다(자리 찾기용; 판정은 손으로).
import re, io
files = ['장v2/부록D_장7A.md','장v2/부록D_장7B.md','장v2/부록D_장8.md','장v2/부록D_장9.md','장v2/부록D_장10.md']
items = {}
for f in files:
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{D:([^}]+)\}\}(.*?)(?=^### D\.|\Z)', txt, re.S|re.M):
        lab = m.group(1); body = m.group(2)
        head = body.split('\n',1)[0]
        stmts = re.findall(r'\(([^()]*\{\{[^}]+\}\}[^()]*)\)\s*$', head)
        grade = re.search(r'\*\*산술 등급\.\*\*\s*(.*)', body)
        indep = re.search(r'\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*)', body)
        items[lab] = dict(file=f, head=head.strip(), stmts=stmts[0] if stmts else '', grade=grade.group(1).strip() if grade else '', bracket=indep.group(1) if indep else '', indep=indep.group(2).strip() if indep else '')
t11 = open('장v2/장11.md', encoding='utf-8').read()
rows = {}
for line in t11.split('\n'):
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        lab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
        rows[lab] = cells
def norm(s):
    s = s.replace('이 문단 머리의 꺾쇠 괄호','「재계산」 열의 꺾쇠 괄호')
    return re.sub(r'\s+',' ',s).strip()
for lab, it in items.items():
    r = rows.get(lab)
    print('=====', lab, it['file'])
    if not r: print('  !! 11.2절에 행 없음'); continue
    print('  D 머리 진술:', it['stmts']); print('  표 진술   :', r[1])
    print('  D 등급:', it['grade']); print('  표 등급:', r[2], '| 쓰인 곳:', r[3])
    print('  괄호 같음:', norm(it['bracket']) == norm(r[4]))
    if norm(it['bracket']) != norm(r[4]): print('   D:', it['bracket']); print('   표:', r[4])
    a, b = norm(it['indep']), norm(r[5])
    print('  독립 재계산 글 같음:', a == b)
    if a != b:
        import difflib
        for op in difflib.SequenceMatcher(None, a, b).get_opcodes():
            if op[0] != 'equal': print('   ', op[0], 'D:', repr(a[op[1]:op[2]][:200]), '표:', repr(b[op[3]:op[4]][:200]))
