# -*- coding: utf-8 -*-
"""11.2 표의 각 행을 부록 D 항목과 대조한다. 또 진술 머리 목록을 뽑아 둔다."""
import re, glob, json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding='utf-8').read()

# --- 부록 D 항목 파싱 ---
D = {}
for f in sorted(glob.glob(os.path.join(BASE, "부록D_장*.md"))):
    txt = rd(f)
    parts = re.split(r'^### D\.\{\{D:([^}]+)\}\}', txt, flags=re.M)
    # parts: [pre, label1, body1, label2, body2,...]
    for i in range(1, len(parts), 2):
        lab, body = parts[i], parts[i+1]
        title = body.split('\n',1)[0]
        stmts = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', title)
        def line(name):
            m = re.search(r'\*\*'+name+r'\.\*\*\s*(.*)', body)
            return m.group(1).strip() if m else None
        D[lab] = dict(file=os.path.basename(f), title=title, stmts=stmts,
                      grade=line('산술 등급'), recomp=line('독립 재계산'), data=line('자료'))
print("부록 D 항목 수:", len(D))

# --- 11.2 표 파싱 ---
ch11 = rd(os.path.join(BASE, "장11.md"))
rows = []
for ln in ch11.split('\n'):
    if ln.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        rows.append(cells)
print("11.2 표 행 수:", len(rows))
labs_tab = [re.search(r'\{\{D:([^}]+)\}\}', r[0]).group(1) for r in rows]
print("표에 없는 D 항목:", [l for l in D if l not in labs_tab])
print("D에 없는 표 항목:", [l for l in labs_tab if l not in D])

# --- 진술 머리 파싱 ---
heads = {}
for f in sorted(glob.glob(os.path.join(BASE, "장*.md"))):
    for n, ln in enumerate(rd(f).split('\n'), 1):
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의|관찰|주장)\s+\{\{(\d+[AB]?:[^}]+)\}\}(.*?)\*\*', ln)
        if m:
            heads[m.group(2)] = dict(kind=m.group(1), rest=m.group(3), file=os.path.basename(f), line=n)
print("진술 머리 수:", len(heads))
# 절 번호: 각 장 파일에서 ### 헤더 추적
sec_of = {}
for f in sorted(glob.glob(os.path.join(BASE, "장*.md"))):
    cur = None
    for n, ln in enumerate(rd(f).split('\n'), 1):
        m = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)\s', ln)
        if m: cur = m.group(1)
        m2 = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}', ln)
        if m2: sec_of[m2.group(2)] = cur
json.dump(dict(heads=heads, sec_of=sec_of, D={k:dict(v, stmts=v['stmts']) for k,v in D.items()}),
          open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체10_P11_heads.json",'w',encoding='utf-8'), ensure_ascii=False, indent=1)

# --- 대조 ---
def norm(s): return re.sub(r'\s+', ' ', s).strip()
for cells in rows:
    lab = re.search(r'\{\{D:([^}]+)\}\}', cells[0]).group(1)
    d = D.get(lab)
    if not d: continue
    issues = []
    # 진술
    tab_stmts = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', cells[1])
    if set(tab_stmts) != set(d['stmts']):
        issues.append(f"진술 불일치: 표 {tab_stmts} / D 제목 {d['stmts']}")
    # 쓰인 곳
    secs = sorted({sec_of.get(s, '?') for s in tab_stmts})
    tab_secs = [x.strip() for x in cells[3].replace('·', ',').split(',')]
    # 절을 둘째 수준까지 줄임
    secs2 = sorted({'.'.join(s.split('.')[:2]) if s else '?' for s in secs})
    if sorted(tab_secs) != secs2:
        issues.append(f"쓰인 곳: 표 {tab_secs} / 머리 절 {secs} ")
    # 꺾쇠 괄호
    m = re.match(r'〔(.*?)〕\s*(.*)', d['recomp'] or '')
    if m:
        br_D, rest_D = m.group(1), m.group(2)
        br_T = cells[4].strip('〔〕 ')
        if norm(br_D) != norm(br_T):
            issues.append(f"꺾쇠: 표 〔{br_T}〕 / D 〔{br_D}〕")
        rest_T = cells[5]
        if norm(rest_D) != norm(rest_T):
            # 차이 위치
            a, b = norm(rest_D), norm(rest_T)
            i = next((i for i in range(min(len(a),len(b))) if a[i]!=b[i]), min(len(a),len(b)))
            issues.append(f"서술 차이(위치 {i}): D…『{a[max(0,i-40):i+80]}』 / 표…『{b[max(0,i-40):i+80]}』")
    else:
        issues.append("D 독립 재계산 줄에 꺾쇠 없음")
    # 산술 등급
    gD = d['grade'] or ''
    issues.append(f"[등급] 표: {cells[2]} | D: {gD[:160]}")
    print(f"\n=== D.{lab} ({d['file']}) ===")
    for s in issues: print("  -", s)
