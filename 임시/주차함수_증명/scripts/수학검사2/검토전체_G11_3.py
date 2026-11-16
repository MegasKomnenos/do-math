# -*- coding: utf-8 -*-
"""G11: (1) 10장→9장 언급 간선을 뺀 폐포로 11.3 표 재대조, (2) '에 의존' 표지 기반 쓰는 자리 완전성, (3) 문헌 결과 이름의 역방향 대조."""
import re, os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_src = open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체_G11_1.py", encoding='utf-8').read().split("# 2. 부록 D 항목")[0]
_src = _src.replace("sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')", "")
exec(_src)
ch11 = read(os.path.join(CH, "장11.md"))
cites = {lab: set(x for x in re.findall(r"\{\{([^}]+)\}\}", '\n'.join(s['block'])) if x in stmts and x != lab) for lab, s in stmts.items()}
# 언급 간선 제거: 10장→9장, 1장
for lab in cites:
    if lab.startswith('10:'):
        cites[lab] = {x for x in cites[lab] if not x.startswith('9:')}
    cites[lab] = {x for x in cites[lab] if not x.startswith('1:')}
def closure(start):
    seen = set(); todo = list(start)
    while todo:
        x = todo.pop()
        if x in seen: continue
        seen.add(x); todo.extend(cites.get(x, ()))
    return seen
C1 = closure(['9:old-7-46'])
sec107 = '\n'.join(sections.get(('text', '10.7'), []))
start2 = {x for x in re.findall(r"\{\{([^}]+)\}\}", sec107) if x in stmts and not x.startswith('9:')} | {'10:old-8-37'}
C2 = closure(start2)
print("첫째 폐포", len(C1), "둘째 폐포", len(C2), "교집합", len(C1 & C2), "첫째만", len(C1 - C2), "둘째만", len(C2 - C1))
tbl = {'shared': set(), 'first': set(), 'second': set()}; rows = []
mode = None
for i, ln in enumerate(ch11, 1):
    if ln.startswith('**공유 입력'): mode = 'shared'
    elif ln.startswith('**첫째 증명의 고유 입력'): mode = 'first'
    elif ln.startswith('**둘째 증명의 고유 입력'): mode = 'second'
    elif ln.startswith('### 11.4'): mode = None
    if mode and ln.startswith('| ') and not ln.startswith('| 입력'):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        labs = set(x for x in re.findall(r"\{\{([^}]+)\}\}", cells[0]) if not x.startswith('D:'))
        tbl[mode] |= labs; rows.append((i, mode, labs, cells))
def show(title, labs):
    print(title)
    for x in sorted(labs):
        s = stmts.get(x)
        print(f"   {x} ({s['kind']} {s['title'][:40]}; {s['file']} L{s['line']}; 절 {s['sec']}; 표지 {s['status'][:60]})" if s else f"   {x}")
show("-- 첫째 고유로 적혔으나 둘째 폐포에도 있음", tbl['first'] & C2)
show("-- 둘째 고유로 적혔으나 첫째 폐포에도 있음", tbl['second'] & C1)
show("-- 공유로 적혔으나 첫째 폐포에 없음", tbl['shared'] - C1)
show("-- 공유로 적혔으나 둘째 폐포에 없음", tbl['shared'] - C2)
show("-- 첫째 고유로 적혔으나 첫째 폐포에 없음", tbl['first'] - C1)
show("-- 둘째 고유로 적혔으나 둘째 폐포에 없음", tbl['second'] - C2)
alltbl = tbl['shared'] | tbl['first'] | tbl['second']
flagged = lambda x: any(w in stmts[x]['status'] for w in ('계산', '문헌', '의존'))
show("-- 첫째 폐포에만 있고 계산/문헌/의존 표지가 있으나 표에 없음(2–8장)", {x for x in (C1 - C2) if flagged(x) and x not in alltbl and not x.startswith(('9:',))})
show("-- 둘째 폐포에만 있고 계산/문헌/의존 표지가 있으나 표에 없음(2–8장)", {x for x in (C2 - C1) if flagged(x) and x not in alltbl and not x.startswith(('10:',))})
show("-- 9장 진술(첫째 폐포) 중 계산 표지 있으나 표에 없음", {x for x in C1 if x.startswith('9:') and '계산' in stmts[x]['status'] and x not in alltbl})
show("-- 10장 진술(둘째 폐포) 중 계산 표지 있으나 표에 없음", {x for x in C2 if x.startswith('10:') and '계산' in stmts[x]['status'] and x not in alltbl})
show("-- 9장 진술 중 문헌 인용 표지", {x for x in C1 if x.startswith('9:') and '문헌' in stmts[x]['status']})
show("-- 10장 진술 중 문헌 인용 표지", {x for x in C2 if x.startswith('10:') and '문헌' in stmts[x]['status']})
# 직접 인용 '앞 장 진술' 가운데 표에 없는 것: 9장/10장 진술이 블록에서 인용하는 2–8장 라벨
direct1 = set(); direct2 = set()
for x in C1:
    if x.startswith('9:'): direct1 |= {y for y in cites[x] if not y.startswith('9:')}
for x in C2 | start2:
    if x.startswith('10:'): direct2 |= {y for y in cites[x] if not y.startswith('10:')}
direct2 |= {x for x in start2 if not x.startswith('10:')}
show("-- 9장 진술이 직접 인용하는 앞 장 진술 가운데 표에 없음", direct1 - alltbl)
show("-- 10장 진술·10.7절이 직접 인용하는 앞 장 진술 가운데 표에 없음", direct2 - alltbl)
# 쓰는 자리 완전성: '에 의존' 표지에 입력 라벨이 있는 폐포 안 진술 가운데 행에 없는 것
print("-- 쓰는 자리 완전성(표지의 「…에 의존」에 그 입력이 적힌 진술인데 행에 없음)")
for i, mode, inputs, cells in rows:
    listed = set(re.findall(r"\{\{([^}]+)\}\}", ' '.join(cells[2:])))
    pool = (C1 | C2) if mode == 'shared' else (C1 if mode == 'first' else C2)
    miss = []
    for y in pool:
        if y in inputs: continue
        st = stmts[y]['status']
        dep = set(re.findall(r"\{\{([^}]+)\}\}", st))
        if dep & inputs and y not in listed:
            miss.append(f"{y}({stmts[y]['file']} L{stmts[y]['line']}; {sorted(dep & inputs)})")
    if miss:
        print(f"   [L{i}] {cells[0][:60]}…\n        " + '\n        '.join(sorted(miss)))
# 문헌 결과 이름의 역방향 대조
print("\n===== 11.4 결과 이름 역방향 =====")
kw = {
 'Stanley 지수': (r"지수 공식", 139), 'Stanley Cayley': (r"Cayley 공식", 140), 'Stanley Lagrange': (r"Lagrange (역변환|반전|–Bürmann)", 141),
 'Knuth 갈고리': (r"갈고리", 142), 'Flajolet': (r"T\(1/e\)=1|임계값", 143), 'Robbins': (r"Robbins|Stirling", 144),
 'Ahlfors': (r"Cauchy (적분|부등식)|편각 원리|부분분수", 148), 'Graham EM': (r"Euler–Maclaurin|Euler 합", 149), 'FKG': (r"FKG", 150),
 'Jensen': (r"Jensen 부등식", 151), 'Wallis': (r"Wallis", 152), 'Corless': (r"Lambert|Corless", 153), 'Tanner': (r"Tanner 1953|Tanner, ", 154),
 'Harris': (r"Harris 부등식", 156), 'Faà': (r"Faà|Bruno", 158), 'Apostol/Titchmarsh': (r"Apostol|Titchmarsh|Euler 합", 159),
 'Petersson': (r"Petersson", 145), 'Janson': (r"Janson", 146), 'Ibragimov': (r"Ibragimov|합성곱", 147), 'Celano': (r"Celano|2507\.07243|Conjecture 6\.5", 137), 'Aguilar': (r"Aguilar|2311\.14055", 138), 'Konheim': (r"Konheim", 135), 'Foata': (r"Foata|Pollak", 136), 'OEIS': (r"OEIS|A078434|2\.6123", 155),
}
for key, (pat, rowline) in kw.items():
    row = ch11[rowline - 1]
    rowlabels = set(re.findall(r"\{\{([^}]+)\}\}", row))
    rowsecs = set(re.findall(r"(\d+\.\d+)절", row))
    hits = []
    for fn in chapter_files[:-1]:
        cur_sec = None; cur_lab = None
        for i, ln in enumerate(read(os.path.join(CH, fn)), 1):
            m = sec_re.match(ln)
            if m: cur_sec = m.group(1); cur_lab = None
            m = head_re.match(ln)
            if m and not re.match(r"^\*\*[^{]+\{\{[^}]+\}\}의 증명", ln): cur_lab = m.group(2)
            elif m: cur_lab = m.group(2)
            if re.search(pat, ln):
                covered = (cur_lab in rowlabels) or (cur_sec in rowsecs) or any((cur_sec or '').startswith(s + '.') for s in rowsecs)
                if not covered:
                    hits.append(f"{fn} L{i} (절 {cur_sec}, 진술 {cur_lab}): …{re.search(pat, ln).group(0)}…")
    if hits:
        print(f"[{key}, 표 L{rowline}] 표에 없는 자리:")
        for h in hits: print("    ", h)
