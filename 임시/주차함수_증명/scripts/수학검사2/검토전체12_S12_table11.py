# S12: 부록 D 항목의 「독립 재계산」 줄과 11.2절 표의 두 열을 대조한다(자리 찾기용).
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = r"C:/math/임시/주차함수_증명/장v2/"
files = ["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]
items = {}
for f in files:
    txt = open(base+f, encoding='utf-8').read()
    for m in re.finditer(r"^### D\.\{\{D:([a-zA-Z0-9\-]+)\}\}(.*?)(?=^### D\.|\Z)", txt, re.S|re.M):
        name, body = m.group(1), m.group(2)
        mm = re.search(r"\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*?)\n", body)
        st = re.search(r"\*\*확인하는 진술\.\*\*", body)
        grade = re.search(r"\*\*산술 등급\.\*\*\s*(.*?)\n", body)
        items[name] = (mm.group(1) if mm else None, mm.group(2).strip() if mm else None, grade.group(1) if grade else None, f)
tab = open(base+"장11.md", encoding='utf-8').read()
rows = {}
for line in tab.splitlines():
    if line.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        name = re.match(r"부록 D\.\{\{D:([a-zA-Z0-9\-]+)\}\}", cells[0]).group(1)
        rows[name] = cells
for name,(brk,txt,grade,f) in items.items():
    if name not in rows:
        print("NO TABLE ROW:", name, f); continue
    cells = rows[name]
    tb, tt = cells[4], cells[5]
    adj = txt.replace("이 문단 머리의 꺾쇠 괄호", "「재계산」 열의 꺾쇠 괄호") if txt else None
    print(f"[{name}] ({f})")
    print("  꺾쇠 same:", brk == tb)
    if brk != tb: print("   D:", brk); print("   T:", tb)
    print("  서술 same:", adj == tt)
    if adj != tt and adj and tt:
        import difflib
        for d in difflib.ndiff([adj],[tt]):
            if d[0] in '+-?': print("   ", d[:400])
    print("  산술등급 D:", grade, " | 표:", cells[2])
