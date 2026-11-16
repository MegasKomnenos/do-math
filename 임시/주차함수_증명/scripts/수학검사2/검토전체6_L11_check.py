# -*- coding: utf-8 -*-
"""L11 검토 보조: 11장·부록 A/B/C 와 장 파일·부록 D 의 대응을 기계적으로 대조한다.
자리 찾기와 문자열 대조만 한다. 판정은 보고서에서 사람이 한다."""
import re, sys, os, glob, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, "장v2")

def rd(p):
    with open(p, encoding='utf-8') as f: return f.read()

chap_files = [f for f in sorted(glob.glob(os.path.join(CH, "장*.md")))]
D_files = sorted(glob.glob(os.path.join(CH, "부록D_*.md")))

# 1. heads
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}(?= ?[(\[.])')
def parse_head(line):
    h = HEAD.match(line)
    if not h: return None
    typ, lab = h.groups()
    rest = line[h.end():]
    paren = None; status = None
    rest = rest.lstrip()
    if rest.startswith('('):
        depth = 0
        for j, ch in enumerate(rest):
            if ch == '(': depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    paren = rest[1:j]; rest = rest[j+1:].lstrip(); break
    if rest.startswith('['):
        j = rest.find(']')
        status = rest[1:j]
    return typ, lab, paren, status
heads = {}
for fp in chap_files:
    cur = None
    for i, line in enumerate(rd(fp).split('\n'), 1):
        m = re.match(r'^###+ (\d+(?:\.\d+)*)', line)
        if m: cur = m.group(1)
        m = re.match(r'^## (\d+)\.', line)
        if m: cur = m.group(1)
        h = parse_head(line)
        if h:
            typ, lab, paren, status = h
            name = recname = None
            if paren:
                parts = paren.split('; ')
                if parts[0].startswith('기록 ['):
                    recname = paren
                else:
                    name = parts[0]
                    if len(parts) > 1: recname = '; '.join(parts[1:])
            heads[lab] = dict(type=typ, name=name, recname=recname, status=status, file=os.path.basename(fp), sec=cur, line=i, raw=line)
print("heads:", len(heads))

# 2. D items
D = {}
for fp in D_files:
    txt = rd(fp)
    for blk in re.split(r'\n(?=### D\.\{\{)', txt):
        m = re.match(r'### D\.\{\{(D:[^}]+)\}\} (.*?) \(((?:정리|명제|보조정리|따름정리).*)\)\s*$', blk.split('\n')[0])
        if not m: continue
        lab, title, stm = m.groups()
        stlabels = re.findall(r'\{\{([^}]+)\}\}', stm)
        def field(name):
            mm = re.search(r'^\*\*' + name + r'\.\*\* (.*)$', blk, re.M)
            return mm.group(1).strip() if mm else None
        D[lab] = dict(title=title, stlabels=stlabels, grade=field('산술 등급'), recomp=field('독립 재계산'), file=os.path.basename(fp))
print("D items:", len(D))

# 3. 11.2 table
ch11 = rd(os.path.join(CH, "장11.md")).split('\n')
rows = [l for l in ch11 if l.startswith('| 부록 D.{{')]
print("11.2 rows:", len(rows))
print("\n=== 11.2 표 대조 ===")
seen_D = set()
for r in rows:
    cells = [c.strip() for c in r.strip().strip('|').split(' | ')]
    if len(cells) != 6:
        print("CELLS!=6", cells[0], len(cells)); continue
    dl = re.search(r'\{\{(D:[^}]+)\}\}', cells[0]).group(1)
    seen_D.add(dl)
    d = D.get(dl)
    if not d: print("NO D ITEM", dl); continue
    tl = re.findall(r'\{\{([^}]+)\}\}', cells[1])
    if tl != d['stlabels']: print(f"[{dl}] 진술 불일치: 표 {tl} vs D 제목 {d['stlabels']}")
    g = d['grade']
    g0 = re.split(r'[(（.]', g)[0].strip()
    if cells[2] != g0: print(f"[{dl}] 산술 등급: 표 「{cells[2]}」 vs D 첫 등급 「{g0}」 (D 전체: {g[:160]})")
    secs = sorted({heads[t]['sec'] for t in tl if t in heads}, key=lambda s: [int(x) for x in s.split('.')])
    tsecs = cells[3].split('·')
    secs2 = sorted({'.'.join(s.split('.')[:2]) for s in secs})
    if sorted(tsecs) != secs2: print(f"[{dl}] 쓰인 곳: 표 {tsecs} vs 진술의 절 {secs} ({[(t, heads.get(t,{}).get('sec')) for t in tl]})")
    rc = d['recomp']
    mb = re.match(r'(〔[^〕]*〕)\s*(.*)$', rc, re.S)
    if not mb: print(f"[{dl}] D 독립 재계산에 꺾쇠 없음"); continue
    br, rest = mb.groups()
    if cells[4] != br: print(f"[{dl}] 재계산 꺾쇠 불일치:\n   표 {cells[4]}\n   D  {br}")
    rest2 = rest.replace('이 문단 머리의 꺾쇠 괄호', '「재계산」 열의 꺾쇠 괄호')
    if cells[5] != rest2:
        a, b = cells[5], rest2
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]: i += 1
        print(f"[{dl}] 독립 재계산 본문 불일치 (첫 차이 위치 {i}; 길이 표 {len(a)} D {len(b)}):\n   표 …{a[max(0,i-40):i+80]}\n   D  …{b[max(0,i-40):i+80]}")
missing = set(D) - seen_D
if missing: print("표에 없는 D 항목:", missing)

# 4. labels existence in the 4 files
print("\n=== 라벨 존재 ===")
for fn in ["장11.md", "부록A.md", "부록B.md", "부록C.md"]:
    txt = rd(os.path.join(CH, fn))
    for lab in sorted(set(re.findall(r'\{\{([^}]+)\}\}', txt))):
        if lab.startswith('D:'):
            if lab not in D: print(fn, "없는 D 라벨", lab)
        elif lab not in heads: print(fn, "없는 라벨", lab)

# 5. 부록 C 표 2
print("\n=== 부록 C 기록 이름/글 이름 대조 ===")
C = rd(os.path.join(CH, "부록C.md")).split('\n')
c2 = {}
for l in C:
    m = re.match(r'^\| (기록 .*?) \| ((?:정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}) \| (.*?) \|$', l)
    if m:
        rec, st, lab, nm = m.groups()
        c2[lab] = (rec, st.split(' ')[0], nm)
for lab, (rec, typ, nm) in c2.items():
    h = heads.get(lab)
    if not h: print("C표2 없는 라벨", lab); continue
    if h['type'] != typ: print(f"[{lab}] 종류: C {typ} vs 머리 {h['type']}")
    hn = h['name'] or ''
    if nm != hn: print(f"[{lab}] 이름: C 「{nm}」 vs 머리 「{hn}」")
    hr = h['recname'] or ''
    if rec != hr: print(f"[{lab}] 기록 이름: C 「{rec}」 vs 머리 「{hr}」")
for lab, h in heads.items():
    if h['recname'] and lab not in c2: print(f"머리에 기록 이름 있으나 C표2에 없음: {lab} ({h['recname']})")

# 6. 계산 표지
print("\n=== 계산 증거/보조 표지 ===")
tbl_stmts = {}
for r in rows:
    cells = [c.strip() for c in r.strip().strip('|').split(' | ')]
    for t in re.findall(r'\{\{([^}]+)\}\}', cells[1]):
        tbl_stmts.setdefault(t, []).append((cells[0], cells[2]))
for lab, h in heads.items():
    st = h['status'] or ''
    if '계산 증거' in st or '계산 보조' in st:
        grades = re.findall(r'계산 (?:증거|보조)\(([^)]*)\)', st)
        if lab not in tbl_stmts: print(f"11.2 표에 없음: {lab} [{st}]")
        else:
            tg = sorted({g for _, g in tbl_stmts[lab]})
            print(f"{lab} ({h['file']} {h['sec']}): 머리 {grades} | 표 {tg}")
        if 'binary64' in st or '평가' in st: print("  !! 머리에 binary64/평가 등급:", lab, st)
for lab in tbl_stmts:
    h = heads.get(lab)
    if h and not ('계산 증거' in (h['status'] or '') or '계산 보조' in (h['status'] or '')):
        print(f"표에 있으나 머리에 계산 표지 없음: {lab} [{h['status']}]")

# 7. identifiers
print("\n=== 식별자 ===")
B = rd(os.path.join(CH, "부록B.md")).split('\n')
Bids = {}
for l in B:
    m = re.match(r'^\| (r[0-9a-f]{7}) \| ([^|]*) \| ([^|]*) \| `(r[0-9a-f]+)` \|$', l)
    if m: Bids[m.group(1)] = (m.group(2).strip(), m.group(3).strip(), m.group(4))
print("B rows:", len(Bids))
used = {}
for fp in sorted(glob.glob(os.path.join(CH, "*.md"))):
    if os.path.basename(fp) == '부록B.md': continue
    txt = rd(fp)
    for i, line in enumerate(txt.split('\n'), 1):
        for idf in re.findall(r'\[(r[0-9a-f]{7})\]', line):
            used.setdefault(idf, set()).add(os.path.basename(fp))
        h = parse_head(line)
        if h and h[3]:
            st = h[3]
            tail = st.split(';')[-1] if ';' in st else ''
            for idf in re.findall(r'\b(r[0-9a-f]{7})\b', tail):
                used.setdefault(idf, set()).add(os.path.basename(fp) + ':head')
for idf in sorted(used):
    if idf not in Bids: print("B에 없는 식별자", idf, sorted(used[idf]))
for idf in Bids:
    if idf not in used: print("B에만 있고 본문에 없는 식별자", idf)
    folder = Bids[idf][2]
    if not folder.startswith(idf): print("폴더 이름 접두 불일치", idf, folder)
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
if os.path.isdir(REC):
    for idf, (ts, title, folder) in Bids.items():
        p = os.path.join(REC, folder)
        if not os.path.isdir(p): print("폴더 없음", idf, folder); continue
        rj = os.path.join(p, 'record.json')
        if os.path.exists(rj):
            try:
                j = json.load(open(rj, encoding='utf-8'))
                t = j.get('title') or j.get('name')
                ct = j.get('created_at') or j.get('created') or j.get('timestamp')
                if t and t.strip() != title: print(f"제목 다름 {idf}:\n   B   {title}\n   rec {t}")
                if ct and ts not in str(ct): print(f"시각? {idf}: B {ts} rec {ct}")
            except Exception as e: print("record.json 읽기 실패", idf, e)
        if not os.path.isdir(os.path.join(p, 'review')): print("review 폴더 없음", idf)
else:
    print("records 폴더 없음:", REC)

# 8. literature
print("\n=== 문헌 언급 자리 ===")
authors = ['Robbins','Stanley','Knuth','Flajolet','Petersson','Janson','Ibragimov','Ahlfors','Graham','Fortuin','FKG','Jensen','Wallis','Corless','Lambert','Tanner','Grimmett','Harris','Comtet','Faà','Apostol','Titchmarsh','Konheim','Foata','Celano','Aguilar','Pollak','Euler–Maclaurin','Euler 합','표준']
for fp in chap_files + D_files:
    cur = None; lasthead = None
    for i, line in enumerate(rd(fp).split('\n'), 1):
        m = re.match(r'^###+ (\d+(?:\.\d+)*)', line) or re.match(r'^### D\.\{\{(D:[^}]+)\}\}', line)
        if m: cur = m.group(1); lasthead = None
        h = parse_head(line)
        if h: lasthead = h[1]
        hits = [a for a in authors if a in line]
        if hits:
            print(f"{os.path.basename(fp)} L{i} sec={cur} head={lasthead}: {hits}")
