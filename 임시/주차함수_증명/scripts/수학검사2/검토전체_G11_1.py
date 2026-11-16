# -*- coding: utf-8 -*-
"""G11 검토 보조: 장11 표(11.2, 11.3, 11.4), 부록 B·C를 본문과 대조한다. 파일을 고치지 않는다."""
import re, sys, glob, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, "장v2")

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read().split('\n')

chapter_files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
D_files = sorted(glob.glob(os.path.join(CH, "부록D_*.md")))
head_re0 = re.compile(r"^\*\*(정리|보조정리|명제|따름정리|정의|문제|추측|관찰|사실|주장|가정)\s+\{\{([^}]+)\}\}\s*(.*?)\.?\*\*")
class _R:
    def __init__(self, g): self.g = g
    def group(self, i): return self.g[i]
class _H:
    def match(self, ln):
        m = head_re0.match(ln)
        if not m:
            return None
        kind, label, rest = m.group(1), m.group(2), m.group(3).strip()
        title = ''; status = ''
        if rest.startswith('('):
            depth = 0
            for j, ch in enumerate(rest):
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        title = rest[1:j]; rest = rest[j+1:].strip(); break
        ms = re.match(r"(\[.*\])", rest)
        if ms:
            status = ms.group(1)
        return _R([None, kind, label, title, status])
head_re = _H()
sec_re = re.compile(r"^###\s+(\d+(?:\.\d+)*)\s")

# 1. 본문 진술 색인: label -> dict(kind,title,status,file,line,section,block)
stmts = {}
sections = {}  # (file, secnum) -> text lines
for fn in chapter_files:
    lines = read(os.path.join(CH, fn))
    cur_sec = None
    cur_label = None
    for i, ln in enumerate(lines, 1):
        m = sec_re.match(ln)
        if m:
            cur_sec = m.group(1)
            sections.setdefault(cur_sec, []).append((fn, i))
            cur_label = None
        m = head_re.match(ln)
        if m:
            kind, label, title, status = m.group(1), m.group(2), m.group(3), m.group(4)
            if re.match(r"^\*\*[^{]+\{\{[^}]+\}\}의 증명", ln):
                # 뒤에 따로 둔 증명: 그 진술의 블록에 잇는다
                if label in stmts:
                    stmts[label]['block'].append(ln)
                    stmts[label]['proof_line'] = (fn, i)
                    cur_label = label
                else:
                    print("증명이 진술보다 먼저", label, fn, i)
                continue
            if label in stmts:
                print("중복 라벨", label, fn, i)
            stmts[label] = dict(kind=kind, title=title or '', status=status or '', file=fn, line=i, sec=cur_sec, block=[ln])
            cur_label = label
        elif cur_label and not ln.startswith('###') and not ln.startswith('## '):
            stmts[cur_label]['block'].append(ln)
    # attach section text
for fn in chapter_files:
    lines = read(os.path.join(CH, fn))
    cur = None
    for i, ln in enumerate(lines, 1):
        m = sec_re.match(ln)
        if m:
            cur = m.group(1)
            sections.setdefault(('text', cur), [])
        if cur is not None:
            sections[('text', cur)].append(ln)

print("진술 수", len(stmts))

# 2. 부록 D 항목
D = {}
for fn in D_files:
    lines = read(fn)
    cur = None
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^###\s+D\.\{\{D:([^}]+)\}\}\s*(.*)$", ln)
        if m:
            cur = m.group(1)
            D[cur] = dict(file=os.path.basename(fn), line=i, head=m.group(2), fields={})
            continue
        if cur:
            m = re.match(r"^\*\*([^*]+)\.\*\*\s*(.*)$", ln)
            if m:
                D[cur]['fields'][m.group(1)] = m.group(2)
print("부록 D 항목 수", len(D))

# 3. 11.2 표 대조
ch11 = read(os.path.join(CH, "장11.md"))
print("\n===== 11.2 표 대조 =====")
rows112 = []
for i, ln in enumerate(ch11, 1):
    if ln.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        rows112.append((i, cells))
print("11.2 행 수", len(rows112))
seenD = set()
for i, cells in rows112:
    if len(cells) != 6:
        print(f"[11.2 L{i}] 열 수 {len(cells)}")
        continue
    item = re.search(r"\{\{D:([^}]+)\}\}", cells[0]).group(1)
    seenD.add(item)
    if item not in D:
        print(f"[11.2 L{i}] 부록 D에 없는 항목 {item}")
        continue
    d = D[item]
    f = d['fields']
    # 확인하는 진술: 머리 괄호의 진술과 비교
    head_labels = re.findall(r"\{\{([^}]+)\}\}", d['head'])
    row_labels = re.findall(r"\{\{([^}]+)\}\}", cells[1])
    if set(head_labels) != set(row_labels):
        print(f"[11.2 L{i}] {item}: 확인하는 진술 불일치  표={row_labels}  D머리={head_labels}")
    # 진술 종류 대조
    for kind_lab in re.findall(r"(정리|보조정리|명제|따름정리|정의)\s+\{\{([^}]+)\}\}", cells[1]):
        k, lab = kind_lab
        if lab in stmts and stmts[lab]['kind'] != k:
            print(f"[11.2 L{i}] {item}: 진술 종류 불일치 {k} {lab} (본문 {stmts[lab]['kind']})")
        if lab not in stmts:
            print(f"[11.2 L{i}] {item}: 본문에 없는 라벨 {lab}")
    # 쓰인 곳(장·절) 대조
    secs = [s for s in re.findall(r"\d+\.\d+", cells[3])]
    body_secs = set()
    for lab in row_labels:
        if lab in stmts:
            body_secs.add(stmts[lab]['sec'])
    for s in secs:
        # 절 번호는 '5.2' 등 2단; 본문 절은 '5.2.3' 처럼 3단일 수도
        if not any(bs == s or (bs and bs.startswith(s + '.')) for bs in body_secs):
            print(f"[11.2 L{i}] {item}: 쓰인 곳 {s} 이 진술의 본문 절 {sorted(body_secs)} 과 다름")
    for bs in body_secs:
        if bs and not any(bs == s or bs.startswith(s + '.') for s in secs):
            print(f"[11.2 L{i}] {item}: 본문 절 {bs} 이 표의 쓰인 곳 {secs} 에 없음")
    # 산술 등급 대조
    grade = f.get('산술 등급', '')
    first = re.split(r"[(（;.]", grade)[0].strip() if grade else ''
    row_grade = cells[2]
    if first and row_grade.split(',')[0].strip() not in grade:
        print(f"[11.2 L{i}] {item}: 산술 등급 표={row_grade!r} / D={grade[:120]!r}")
    # 재계산 꺾쇠 대조
    indep = f.get('독립 재계산', '')
    mb = re.match(r"〔([^〕]*)〕\s*(.*)$", indep)
    if not mb:
        print(f"[11.2 L{i}] {item}: D 독립 재계산 줄에 꺾쇠 없음: {indep[:80]!r}")
    else:
        if cells[4] != '〔' + mb.group(1) + '〕':
            print(f"[11.2 L{i}] {item}: 재계산 꺾쇠 불일치\n   표={cells[4]}\n   D =〔{mb.group(1)}〕")
        rest = mb.group(2).strip()
        if cells[5] != rest:
            # 차이 위치
            a, b = cells[5], rest
            j = 0
            while j < min(len(a), len(b)) and a[j] == b[j]:
                j += 1
            print(f"[11.2 L{i}] {item}: 독립 재계산 서술 불일치 (첫 차이 위치 {j})\n   표…{a[max(0,j-40):j+80]}\n   D …{b[max(0,j-40):j+80]}")
for item in D:
    if item not in seenD:
        print(f"[11.2] 표에 없는 부록 D 항목 {item} ({D[item]['file']})")

# 4. 11.3 표 대조: 쓰는 자리의 진술이 입력 라벨을 인용하는지
print("\n===== 11.3 표 대조 =====")
in113 = False
for i, ln in enumerate(ch11, 1):
    if ln.startswith('### 11.3'):
        in113 = True
    if ln.startswith('### 11.4'):
        in113 = False
    if not in113 or not ln.startswith('| ') or ln.startswith('| 입력') or ln.startswith('|---'):
        continue
    cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
    input_labels = re.findall(r"\{\{([^}]+)\}\}", cells[0])
    # 종류 대조 (입력 열 + 계산 진술 열)
    for col in (0, 1):
        for k, lab in re.findall(r"(정리|보조정리|명제|따름정리|정의)\s+\{\{([^}]+)\}\}", cells[col]):
            if lab not in stmts:
                print(f"[11.3 L{i}] 본문에 없는 라벨 {lab}")
            elif stmts[lab]['kind'] != k:
                print(f"[11.3 L{i}] 종류 불일치 {k} {lab} (본문 {stmts[lab]['kind']})")
        # 같은 종류 뒤 ·로 이어진 라벨들
        for m in re.finditer(r"(정리|보조정리|명제|따름정리|정의)\s+((?:\{\{[^}]+\}\}·?)+)", cells[col]):
            k = m.group(1)
            for lab in re.findall(r"\{\{([^}]+)\}\}", m.group(2)):
                if lab in stmts and stmts[lab]['kind'] != k:
                    print(f"[11.3 L{i}] 종류 불일치(·묶음) {k} {lab} (본문 {stmts[lab]['kind']})")
    # 계산 진술 열: 그 진술의 부록 D 항목이 있는지
    for lab in re.findall(r"\{\{([^}]+)\}\}", cells[1]):
        if lab.startswith('D:'):
            continue
        has = [it for it in D if lab in re.findall(r"\{\{([^}]+)\}\}", D[it]['head'])]
        if not has:
            print(f"[11.3 L{i}] 계산 진술 {lab} 을 확인하는 부록 D 항목 없음")
    # 쓰는 자리 열들
    for col in range(2, len(cells)):
        cell = cells[col]
        # 괄호 안 지정 입력 처리: '자리(라벨들)' 구조는 복잡하므로 각 자리 진술에 대해 입력 라벨 중 하나라도 인용하는지 본다
        for m in re.finditer(r"(정리|보조정리|명제|따름정리|정의)\s+((?:\{\{[^}]+\}\}(?:·|\s*,\s*)?)+)", cell):
            k = m.group(1)
            for lab in re.findall(r"\{\{([^}]+)\}\}", m.group(2)):
                if lab not in stmts:
                    print(f"[11.3 L{i}] 쓰는 자리: 본문에 없는 라벨 {lab}")
                    continue
                if stmts[lab]['kind'] != k:
                    print(f"[11.3 L{i}] 쓰는 자리 종류 불일치 {k} {lab} (본문 {stmts[lab]['kind']})")
                blk = '\n'.join(stmts[lab]['block'])
                # 괄호로 지정된 입력이 있으면 그것만 본다
                after = cell[m.end():m.end()+400]
                spec = None
                mm = re.match(r"\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)", after)
                if mm:
                    spec = re.findall(r"\{\{([^}]+)\}\}", mm.group(1))
                targets = [t for t in (spec or input_labels) if not t.startswith('D:')]
                missing = [t for t in targets if ('{{' + t + '}}') not in blk]
                if targets and len(missing) == len(targets):
                    print(f"[11.3 L{i}] 쓰는 자리 {k} {lab}({stmts[lab]['file']} L{stmts[lab]['line']}) 블록이 입력 {targets} 어느 것도 인용하지 않음")
                elif missing and spec:
                    print(f"[11.3 L{i}] 쓰는 자리 {k} {lab}: 괄호 지정 입력 중 미인용 {missing}")

# 5. 11.4 문헌 표
print("\n===== 11.4 문헌 표 대조 =====")
authors = {
 'Konheim': ['Konheim'], 'Foata': ['Foata', 'Pollak'], 'Celano': ['Celano'], 'Aguilar': ['Aguilar'], 'Stanley': ['Stanley'],
 'Knuth, \\*The Art': ['Knuth'], 'Flajolet': ['Flajolet'], 'Robbins': ['Robbins'], 'Petersson': ['Petersson'], 'Janson': ['Janson'],
 'Ibragimov': ['Ibragimov'], 'Ahlfors': ['Ahlfors'], 'Graham': ['Graham', 'Euler–Maclaurin'], 'Fortuin': ['FKG', 'Fortuin'], 'Jensen': ['Jensen'],
 'Wallis': ['Wallis'], 'Corless': ['Corless'], 'Tanner': ['Tanner'], 'OEIS': ['OEIS', 'A078434'], 'Grimmett': ['Grimmett'], 'Harris': ['Harris'],
 'Comtet': ['Comtet', 'Faà'], 'Apostol': ['Apostol'], 'Titchmarsh': ['Titchmarsh'],
}
in114 = False
for i, ln in enumerate(ch11, 1):
    if ln.startswith('### 11.4'):
        in114 = True
    if not in114 or not ln.startswith('| ') or ln.startswith('| 문헌') or ln.startswith('|---'):
        continue
    cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
    key = None
    for a in authors:
        if re.match(a, cells[0]):
            key = a
            break
    if key is None:
        print(f"[11.4 L{i}] 저자 키 없음: {cells[0][:40]}")
        continue
    words = authors[key]
    places = cells[2]
    for k, lab in re.findall(r"(정리|보조정리|명제|따름정리|정의)\s+\{\{([^}]+)\}\}", places):
        if lab not in stmts:
            print(f"[11.4 L{i}] {key}: 본문에 없는 라벨 {lab}"); continue
        if stmts[lab]['kind'] != k:
            print(f"[11.4 L{i}] {key}: 종류 불일치 {k} {lab} (본문 {stmts[lab]['kind']})")
    for m in re.finditer(r"(정리|보조정리|명제|따름정리|정의)\s+((?:\{\{[^}]+\}\}·?)+)", places):
        for lab in re.findall(r"\{\{([^}]+)\}\}", m.group(2)):
            if lab not in stmts:
                continue
            blk = '\n'.join(stmts[lab]['block'])
            if not any(w in blk for w in words):
                print(f"[11.4 L{i}] {key}: {stmts[lab]['kind']} {lab}({stmts[lab]['file']} L{stmts[lab]['line']}) 블록에 {words} 없음")
    for s in re.findall(r"(\d+\.\d+)절", places):
        txt = '\n'.join(sections.get(('text', s), []))
        if not txt:
            print(f"[11.4 L{i}] {key}: 절 {s} 본문에 없음")
        elif not any(w in txt for w in words):
            print(f"[11.4 L{i}] {key}: 절 {s} 에 {words} 없음")
    for it in re.findall(r"D\.\{\{D:([^}]+)\}\}", places):
        if it not in D:
            print(f"[11.4 L{i}] {key}: 부록 D 항목 없음 {it}")
        else:
            txt = ' '.join(D[it]['fields'].values()) + D[it]['head']
            if not any(w in txt for w in words):
                print(f"[11.4 L{i}] {key}: 부록 D.{it} 에 {words} 없음")
# 역방향: 본문에서 저자 이름이 나오는 진술이 표에 있는지
print("-- 역방향: 본문 진술 블록에 저자명이 있으나 11.4 표의 그 문헌 행에 없는 자리")
tbl114 = '\n'.join(l for l in ch11 if l.startswith('| ') and in114)
rows114 = [l for l in ch11[ch11.index(next(l for l in ch11 if l.startswith('### 11.4'))):] if l.startswith('| ') and not l.startswith('| 문헌')]
for key, words in authors.items():
    row = next((r for r in rows114 if re.match(key, r.strip('| '))), None)
    if row is None:
        continue
    rowlabels = set(re.findall(r"\{\{([^}]+)\}\}", row))
    rowsecs = set(re.findall(r"(\d+\.\d+)절", row))
    for lab, s in stmts.items():
        blk = '\n'.join(s['block'])
        if any(re.search(r"\b" + re.escape(w) + r"\b", blk) for w in words if w not in ('Harris',)) or ('Harris 부등식' in blk and key == 'Harris'):
            if lab not in rowlabels and (s['sec'] or '') not in rowsecs and not any((s['sec'] or '').startswith(x + '.') for x in rowsecs):
                print(f"   {key}: {s['kind']} {lab} ({s['file']} L{s['line']}, 절 {s['sec']}) 블록에 {words} 있음, 표 행에 없음")

# 6. 부록 C 둘째 표: 라벨·종류·이름
print("\n===== 부록 C 둘째 표(기록 이름→진술) 대조 =====")
C = read(os.path.join(CH, "부록C.md"))
for i, ln in enumerate(C, 1):
    if not ln.startswith('| 기록 ['):
        continue
    cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
    if len(cells) != 3:
        print(f"[C L{i}] 열 수 {len(cells)}"); continue
    m = re.search(r"(정리|보조정리|명제|따름정리|정의)\s+\{\{([^}]+)\}\}", cells[1])
    if not m:
        print(f"[C L{i}] 진술 라벨 없음: {cells[1]}"); continue
    k, lab = m.group(1), m.group(2)
    if lab not in stmts:
        print(f"[C L{i}] 본문에 없는 라벨 {lab}"); continue
    s = stmts[lab]
    if s['kind'] != k:
        print(f"[C L{i}] 종류 불일치 {k} {lab} (본문 {s['kind']})")
    name = cells[2]
    title = s['title']
    # 본문 제목은 '이름; 기록 [..]의 ...' 꼴일 수 있음
    tmain = title.split(';')[0].strip()
    if name != '—' and name != tmain and name not in title:
        print(f"[C L{i}] 이름 불일치 {lab}: C={name!r} / 본문={title!r}")
    if name == '—' and tmain:
        print(f"[C L{i}] C는 이름 없음(—)인데 본문 제목 있음 {lab}: {title!r}")
    # 기록 이름이 본문 제목에 들어 있는가 (확인용)
    recname = cells[0]
    rec_ids = re.findall(r"\[(r[0-9a-f]{7})\]", recname)
    for rid in rec_ids:
        if rid not in s['status'] and rid not in title:
            print(f"[C L{i}] {lab}: 기록 {rid} 가 본문 머리(제목/표지)에 없음  머리제목={title!r} 표지={s['status']!r}")

# 7. 부록 B: 식별자 사용 대조
print("\n===== 부록 B 식별자 대조 =====")
B = read(os.path.join(CH, "부록B.md"))
Bids = []
for i, ln in enumerate(B, 1):
    m = re.match(r"^\| (r[0-9a-f]{7}) \| ([^|]+) \| ([^|]+) \| `([^`]+)` \|", ln)
    if m:
        Bids.append((m.group(1), m.group(2).strip(), m.group(4)))
        if not m.group(4).startswith(m.group(1)):
            print(f"[B L{i}] 폴더 이름이 식별자로 시작하지 않음 {m.group(1)} {m.group(4)}")
print("B 행 수", len(Bids))
# 시각 순
prev = None
for rid, t, folder in Bids:
    if prev and t < prev[1]:
        print(f"[B] 시각 순서 어긋남 {prev[0]} {prev[1]} > {rid} {t}")
    prev = (rid, t)
Bset = {b[0] for b in Bids}
used = {}
for fn in chapter_files + [os.path.basename(p) for p in D_files] + ["부록A.md", "부록C.md"]:
    for i, ln in enumerate(read(os.path.join(CH, fn)), 1):
        for rid in re.findall(r"\br([0-9a-f]{7})\b", ln):
            used.setdefault('r' + rid, []).append((fn, i))
for rid in sorted(used):
    if rid not in Bset:
        print(f"[B] 표에 없는 식별자 {rid}: {used[rid][:3]}")
for rid in Bset:
    if rid not in used:
        print(f"[B] 어디서도 인용되지 않는 표 행 {rid}")
# 기록 폴더 실제 존재 여부
recdir = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
if os.path.isdir(recdir):
    folders = set(os.listdir(recdir))
    for rid, t, folder in Bids:
        if folder not in folders:
            print(f"[B] 기록 폴더 없음 {folder}")
else:
    print("기록 폴더에 접근 불가", recdir)

# 9. 인용 폐포: 두 증명의 입력 집합을 블록 인용으로 계산해 11.3 표와 비교
print("\n===== 11.3 인용 폐포 대조 =====")
cites = {lab: set(x for x in re.findall(r"\{\{([^}]+)\}\}", '\n'.join(s['block'])) if x in stmts and x != lab) for lab, s in stmts.items()}
def closure(start):
    seen = set(); todo = [start]
    while todo:
        x = todo.pop()
        if x in seen: continue
        seen.add(x)
        todo.extend(cites.get(x, ()))
    return seen
# 10.7절 본문(정의 아닌 산문)에서 인용하는 라벨도 둘째 증명의 시작에 더한다
sec107 = '\n'.join(sections.get(('text', '10.7'), []))
start2 = set(x for x in re.findall(r"\{\{([^}]+)\}\}", sec107) if x in stmts)
C1 = closure('9:old-7-46')
C2 = set()
for x in start2 | {'10:old-8-37'}:
    C2 |= closure(x)
print("첫째 증명 폐포 크기", len(C1), " 둘째 증명 폐포 크기", len(C2), " 교집합", len(C1 & C2))
# 표의 라벨 모으기
tbl = {'shared': set(), 'first': set(), 'second': set()}
mode = None
for i, ln in enumerate(ch11, 1):
    if ln.startswith('**공유 입력'): mode = 'shared'
    elif ln.startswith('**첫째 증명의 고유 입력'): mode = 'first'
    elif ln.startswith('**둘째 증명의 고유 입력'): mode = 'second'
    elif ln.startswith('### 11.4'): mode = None
    if mode and ln.startswith('| ') and not ln.startswith('| 입력'):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        tbl[mode] |= set(x for x in re.findall(r"\{\{([^}]+)\}\}", cells[0]) if not x.startswith('D:'))
def show(title, labs):
    print(title)
    for x in sorted(labs):
        s = stmts.get(x)
        print(f"   {x} ({s['kind']} {s['title'][:30]}, {s['file']} L{s['line']}, 절 {s['sec']})" if s else f"   {x}")
show("-- 표: 첫째 고유로 적혔으나 둘째 증명 폐포에도 있음", tbl['first'] & C2)
show("-- 표: 둘째 고유로 적혔으나 첫째 증명 폐포에도 있음", tbl['second'] & C1)
show("-- 표: 공유로 적혔으나 첫째 폐포에 없음", tbl['shared'] - C1)
show("-- 표: 공유로 적혔으나 둘째 폐포에 없음", tbl['shared'] - C2)
show("-- 표: 첫째 고유로 적혔으나 첫째 폐포에 없음", tbl['first'] - C1)
show("-- 표: 둘째 고유로 적혔으나 둘째 폐포에 없음", tbl['second'] - C2)
# 폐포에 있으나 표 어디에도 없는 앞 장(2–8장) 진술 가운데 계산/문헌/의존 표지를 가진 것
flagged = lambda x: any(w in stmts[x]['status'] for w in ('계산', '문헌', '의존'))
alltbl = tbl['shared'] | tbl['first'] | tbl['second']
# 표의 행에 '그 증명이 거쳐 부르는' 식으로 묶인 라벨도 모두 alltbl에 들어 있음(cells[0]에서 뽑음)
show("-- 폐포(둘 다)에 있고 표지에 계산/문헌/의존이 있으나 표 어디에도 없음(공유 후보)", {x for x in (C1 & C2) if flagged(x) and x not in alltbl and not x.startswith(('9:', '10:', '1:'))})
show("-- 첫째 폐포에만 있고 표지에 계산/문헌/의존이 있으나 표에 없음(첫째 고유 후보)", {x for x in (C1 - C2) if flagged(x) and x not in alltbl and not x.startswith(('9:', '1:'))})
show("-- 둘째 폐포에만 있고 표지에 계산/문헌/의존이 있으나 표에 없음(둘째 고유 후보)", {x for x in (C2 - C1) if flagged(x) and x not in alltbl and not x.startswith(('10:', '1:'))})
# 9장·10장 진술 가운데 계산 표지가 있는데 표에 없는 것
show("-- 9장 진술 중 계산 표지 있으나 표에 없음", {x for x in C1 if x.startswith('9:') and '계산' in stmts[x]['status'] and x not in alltbl})
show("-- 10장 진술 중 계산 표지 있으나 표에 없음", {x for x in C2 if x.startswith('10:') and '계산' in stmts[x]['status'] and x not in alltbl})
# 각 표 행의 '쓰는 자리' 완전성: 입력을 인용하는 9·10장(및 폐포 안) 진술 가운데 행에 적히지 않은 것
print("-- 쓰는 자리 완전성(입력 라벨을 블록에서 인용하는 폐포 안 진술 가운데 행에 없는 것)")
mode = None
for i, ln in enumerate(ch11, 1):
    if ln.startswith('**공유 입력'): mode = 'shared'
    elif ln.startswith('**첫째 증명의 고유 입력'): mode = 'first'
    elif ln.startswith('**둘째 증명의 고유 입력'): mode = 'second'
    elif ln.startswith('### 11.4'): mode = None
    if mode and ln.startswith('| ') and not ln.startswith('| 입력'):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        inputs = set(x for x in re.findall(r"\{\{([^}]+)\}\}", cells[0]) if not x.startswith('D:'))
        listed = set(re.findall(r"\{\{([^}]+)\}\}", ' '.join(cells[2:])))
        pool = (C1 | C2) if mode == 'shared' else (C1 if mode == 'first' else C2)
        users = {y for y in pool if y not in inputs and (cites[y] & inputs)}
        miss = users - listed - inputs
        if miss:
            print(f"   [L{i}] {cells[0][:50]}…  행에 없는 인용자: " + ', '.join(f"{y}({stmts[y]['file']})" for y in sorted(miss)))

# 8. 부록 C 첫 표·셋째 표와 부록 A의 라벨 존재
print("\n===== 부록 A·C의 라벨 존재 =====")
for fn in ["부록A.md", "부록C.md"]:
    for i, ln in enumerate(read(os.path.join(CH, fn)), 1):
        for lab in re.findall(r"\{\{([^}]+)\}\}", ln):
            if lab not in stmts:
                print(f"[{fn} L{i}] 본문에 없는 라벨 {lab}")
