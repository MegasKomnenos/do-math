# -*- coding: utf-8 -*-
"""L11 검토 보조 4: (1) 11.3 표의 「계산 진술과 산술 등급」 열을 인용 닫힘으로 대조, (2) 부록 B 시각을 events 로 대조,
(3) 부록 C 낱말 표의 「처음 정의된 절」을 첫 출현 절과 대조(참고용)."""
import sys, os, re, glob, json, importlib.util, datetime
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "검토전체6_L11_graph.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
blocks, graph, closure, LAB = g.blocks, g.graph, g.closure, g.LAB
CH = g.CH

calc = {lab for lab, b in blocks.items() if ('계산 증거' in b['head'].split('**')[1] or '계산 보조' in b['head'].split('**')[1])}
print("계산 진술 수:", len(calc))

ch11 = open(os.path.join(CH, "장11.md"), encoding='utf-8').read().split('\n')
def table_after(marker):
    rows = []; on = False
    for l in ch11:
        if l.startswith(marker): on = True; continue
        if on:
            if l.startswith('| 입력 |') or l.startswith('|---'): continue
            if l.startswith('|'): rows.append(l)
            elif rows: break
    return rows
rows = table_after('**공유 입력.**') + table_after('**첫째 증명의 고유 입력.**') + table_after('**둘째 증명의 고유 입력.**')
seen = set()
print("\n=== 11.3 표 행별: 입력 닫힘 안의 계산 진술(앞 행 제외) vs 표의 계산 진술 열 ===")
for r in rows:
    cells = [c.strip() for c in r.strip().strip('|').split(' | ')]
    inputs = LAB.findall(cells[0])
    listed = set(LAB.findall(cells[1]))
    cl = set()
    for x in inputs:
        if x in blocks:
            cl |= closure(x); cl.add(x)
    found = {x for x in cl if x in calc}
    new = found - seen
    missing_in_table = sorted(new - listed)
    extra_in_table = sorted(listed - found)
    print(f"\n[{cells[0][:60]}]")
    print("   표:", sorted(listed) if listed else "없음")
    if missing_in_table: print("   닫힘에 있으나 표에 없음(앞 행 제외):", missing_in_table)
    if extra_in_table: print("   표에 있으나 닫힘에 없음:", extra_in_table)
    seen |= listed | new

# timestamps
print("\n=== 부록 B 시각 대조 ===")
EV = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\events"
B = open(os.path.join(CH, "부록B.md"), encoding='utf-8').read().split('\n')
prev_seq = -1
for l in B:
    m = re.match(r'^\| (r[0-9a-f]{7}) \| ([^|]*) \| ([^|]*) \| `(r[0-9a-f]+)` \|$', l)
    if not m: continue
    idf, ts, title, folder = m.groups()
    p = os.path.join(EV, folder + '.json')
    if not os.path.exists(p): print("event 없음", idf); continue
    j = json.load(open(p, encoding='utf-8'))
    at = float(j['at']); seq = int(j['sequence'])
    dt = datetime.datetime.fromtimestamp(at)
    s = dt.strftime('%m-%d %H:%M')
    flag = '' if s == ts.strip() else '  <-- 다름'
    order = '' if seq > prev_seq else '  <-- 순서 역전'
    prev_seq = seq
    print(f"{idf} B={ts.strip()} ev={s} seq={seq}{flag}{order}")

# term first occurrences
print("\n=== 부록 C 낱말 표: 처음 정의된 절 vs 첫 출현 절 ===")
C = open(os.path.join(CH, "부록C.md"), encoding='utf-8').read().split('\n')
order_files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md','장11.md']
texts = []
for fn in order_files:
    cur = None
    for i, line in enumerate(open(os.path.join(CH, fn), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^###+ (\d+(?:\.\d+)*)', line)
        if m: cur = m.group(1)
        texts.append((fn, cur, i, line))
def first(term):
    for fn, sec, i, line in texts:
        if term in line: return (fn, sec, i)
    return None
on = False
for l in C:
    if l.startswith('### 낱말'): on = True; continue
    if l.startswith('### 기록이'): break
    if on and l.startswith('| ') and not l.startswith('| 이 글의 용어'):
        cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
        if len(cells) != 3: continue
        terms = [t.strip() for t in re.split(r'[,·]', cells[0]) if t.strip() and '$' not in t]
        for t in terms[:3]:
            t0 = re.sub(r'\(.*?\)', '', t).strip()
            if len(t0) < 2: continue
            f = first(t0)
            print(f"{t0!r}: C={cells[2]} | 첫 출현={f}")
