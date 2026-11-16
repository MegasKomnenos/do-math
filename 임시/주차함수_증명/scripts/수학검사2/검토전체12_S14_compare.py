# -*- coding: utf-8 -*-
"""S14: 장 파일 머리(_S14_heads.tsv) 대 대응표·의존지도 1절·장부 4절의 대조.
자리 찾기와 세기만 한다; 판정은 보고서에서 읽고 한다."""
import re, sys, io, pathlib, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
heads = {}
order = []
for line in (ROOT/"scripts/수학검사2/_S14_heads.tsv").read_text(encoding='utf-8').splitlines():
    f, ln, kind, lab, name, status, sec, num = line.split('\t')
    heads[lab] = dict(file=f, line=int(ln), kind=kind, name=name, status=status, sec=sec, num=num)
    order.append(lab)

def cells(row):
    return [c.strip() for c in row.strip().strip('|').split('|')]

# ---- 대응표
print("=== 대응표 대조")
tab = {}
for line in (ROOT/"대조v2/라벨_번호_대응표_1114.md").read_text(encoding='utf-8').splitlines():
    if not line.startswith('| `{{'): continue
    c = cells(line)
    lab = c[0].strip('`').strip('{}')
    tab[lab] = dict(kind=c[1], name=c[2], num=c[3], old=c[4], sec=c[5])
for lab in order:
    if lab not in tab: print("대응표에 없음:", lab, heads[lab]); continue
    t = tab[lab]; h = heads[lab]
    if t['kind'] != h['kind']: print("종류 다름", lab, t['kind'], h['kind'])
    hn = h['name'] or '—'
    if t['name'] != hn: print("이름 다름", lab, "| 표:", t['name'], "| 장:", hn)
    if t['num'] != h['num']: print("번호 다름", lab, t['num'], h['num'])
    if t['sec'] != '.'.join(h['sec'].split('.')[:2]): print("절 다름", lab, t['sec'], h['sec'])
for lab in tab:
    if lab not in heads: print("장 파일에 없음(대응표 행):", lab)

# ---- 의존지도 1절
print("=== 의존지도 1절 대조")
dep = {}
txt = (ROOT/"의존지도_v2.md").read_text(encoding='utf-8')
sec1 = txt.split('## 1. 진술별 입력 표')[1].split('### 1.1')[0]
for line in sec1.splitlines():
    if not line.startswith('| `{{'): continue
    c = cells(line)
    lab = c[0].strip('`').strip('{}')
    dep[lab] = dict(sec=c[1], old=c[2], name=c[3], status=c[4], inputs=c[5], rec=c[6], lit=c[7], D=c[8], note=c[9])
for lab in order:
    if lab not in dep: print("의존지도에 없음:", lab); continue
    d = dep[lab]; h = heads[lab]
    if d['sec'] != '.'.join(h['sec'].split('.')[:2]): print("절 다름", lab, d['sec'], h['sec'])
    # 지위: 머리 대괄호의 ; 앞
    st = h['status'].split(';')[0].strip() if h['status'] else ''
    if h['kind'] == '정의' and not st: st = '정의'
    if d['status'] != st: print("지위 다름", lab, "| 지도:", d['status'], "| 장:", st)
    # 요지 = 이름
    hn = h['name']
    if hn and d['name'] != hn: print("요지 다름", lab, "| 지도:", d['name'], "| 장:", hn)
    # 선언 의존
    decl = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', st))
    first = d['inputs'].split('본문 인용:')[0]
    dec2 = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', first))
    if decl != dec2: print("선언 의존 다름", lab, "| 장:", sorted(decl), "| 지도:", sorted(dec2))
    # 첫 판 번호 (old-x-y → 종류 x.y)
    m = re.match(r'\d+:old-(\d+)-(\d+)$', lab)
    if m:
        exp = f"{h['kind']} {m.group(1)}.{m.group(2)}"
        if d['old'] != exp: print("첫 판 번호 다름", lab, d['old'], exp)
    else:
        if d['old'] != '새 진술': print("첫 판 번호 다름(새)", lab, d['old'])
for lab in dep:
    if lab not in heads: print("장 파일에 없음(의존지도 행):", lab)

# ---- 본문 인용 비교 (머리부터 다음 머리 전까지 + 뒤로 미룬 증명 단락)
print("=== 본문 인용 대조(지도의 입력 열 전체 대 장 파일에서 센 것)")
FILES = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md"]
HEADRE = re.compile(r'^\*\*(정리|정의|보조정리|명제|따름정리) \{\{(\d+:[^}]+)\}\}(의 증명)?')
body = collections.defaultdict(list)
for f in FILES:
    cur = None
    for line in (ROOT/"장v2"/f).read_text(encoding='utf-8').splitlines():
        m = HEADRE.match(line)
        if m:
            cur = m.group(2)
        if cur: body[cur].append(line)
cites = {}
for lab in order:
    s = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', '\n'.join(body[lab])))
    s.discard(lab)
    s = {x for x in s if not x.startswith('D:')}
    cites[lab] = s
    d = dep.get(lab)
    if not d: continue
    ds = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', d['inputs']))
    if s != ds:
        print(lab, "| 장에만:", sorted(s-ds), "| 지도에만:", sorted(ds-s))
