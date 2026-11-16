# -*- coding: utf-8 -*-
"""N14: 뽑은 진술 머리와 대응표·장부 4절·의존지도 1절을 맞춘다."""
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
SD = os.path.join(ROOT, "scripts", "수학검사2")
heads = json.load(open(os.path.join(SD, "_N14_heads.json"), encoding='utf-8'))
H = {h['label']: h for h in heads}
order = [h['label'] for h in heads]
out = open(os.path.join(SD, "_N14_compare_out.txt"), 'w', encoding='utf-8')
def P(*a):
    print(*a, file=out)

def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]

# ---------- 대응표 ----------
P("=== 대응표 ===")
rows = []
for ln in open(os.path.join(ROOT, "대조v2", "라벨_번호_대응표_1114.md"), encoding='utf-8'):
    if ln.startswith('| `'):
        rows.append(cells(ln))
seen = set()
for r in rows:
    lab = r[0].strip('`')
    if lab.startswith('{{'):
        lab = lab[2:-2]
        seen.add(lab)
        if lab not in H:
            P("대응표 라벨 없음(장 파일에 머리 없음):", lab); continue
        h = H[lab]
        if r[1] != h['kind']:
            P("종류 다름:", lab, r[1], "| 장:", h['kind'])
        nm = h['name'] or '—'
        nm2 = nm.replace('; ', '; ')
        if r[2] != nm and not (nm == '—' and r[2] == '—'):
            P("이름 다름:", lab, "| 표:", r[2], "| 장:", nm)
        if r[3] != h['num']:
            P("번호 다름:", lab, "표:", r[3], "장:", h['num'])
        if r[5] != h['sec']:
            P("절 다름:", lab, "표:", r[5], "장:", h['sec'])
    else:
        lab2 = lab.strip('()')
        if lab2 in H:
            P("뺌 행인데 장 파일에 있음:", lab2)
missing = [l for l in order if l not in seen]
P("대응표에 없는 장 파일 라벨:", missing)
# order check
tbl_order = [r[0].strip('`')[2:-2] for r in rows if r[0].strip('`').startswith('{{')]
if tbl_order != order:
    for i,(a,b) in enumerate(zip(tbl_order, order)):
        if a != b:
            P("순서 어긋남 첫 자리:", i, a, b); break

# ---------- 장부 4절 ----------
P("\n=== 장부 4절 ===")
lines = open(os.path.join(ROOT, "장부_v2.md"), encoding='utf-8').read().split('\n')
s = lines.index("## 4. 이름 사전: 기록의 결과 이름과 이 글의 라벨")
e = lines.index("## 5. 장별 배정과 여유 글자")
seen4 = set()
for ln in lines[s:e]:
    if not ln.startswith('| ') or ln.startswith('| 첫 판') or ln.startswith('|---'):
        continue
    c = cells(ln)
    if len(c) < 6: continue
    first, kind, name, recname, sec, lab = c[:6]
    if lab.startswith('{{'):
        l = lab[2:-2]; seen4.add(l)
        if l not in H:
            P("4절 라벨 없음(장 파일에 머리 없음):", l); continue
        h = H[l]
        if kind != h['kind']:
            P("4절 종류 다름:", l, kind, "| 장:", h['kind'])
        if sec != h['sec']:
            P("4절 절 다름:", l, "장부:", sec, "장:", h['sec'])
        # name: head name is "이름; 기록 ..." — compare first part
        hn = (h['name'] or '')
        hn_main = hn.split('; 기록')[0].strip() if hn else ''
        hn_rec = hn[len(hn_main):].lstrip('; ').strip() if '; 기록' in hn else ''
        if name != hn_main and not (name == '' and hn == ''):
            P("4절 이름 다름:", l, "| 장부:", name, "| 장:", hn_main)
        if recname != hn_rec:
            P("4절 기록 이름 다름:", l, "| 장부:", recname, "| 장:", hn_rec)
    elif lab.startswith('('):
        l = lab.strip('()')
        if l in H:
            P("4절 뺌 행인데 장 파일에 있음:", l)
    elif lab == '—':
        pass
P("4절에 없는 장 파일 라벨:", [l for l in order if l not in seen4])

# ---------- 의존지도 1절 ----------
P("\n=== 의존지도 1절 ===")
dl = open(os.path.join(ROOT, "의존지도_v2.md"), encoding='utf-8').read().split('\n')
s = dl.index("## 1. 진술별 입력 표")
e = dl.index("### 1.1 뺌·대체된 라벨")
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
seenD = set()
for ln in dl[s:e]:
    if not ln.startswith('| `{{'): continue
    c = cells(ln)
    lab = c[0].strip('`')[2:-2]; seenD.add(lab)
    if lab not in H:
        P("지도 라벨 없음:", lab); continue
    h = H[lab]
    sec, first, gist, status, inputs, recs = c[1], c[2], c[3], c[4], c[5], c[6]
    if sec != h['sec']:
        P("지도 절 다름:", lab, sec, "| 장:", h['sec'])
    # status
    hs = h['status_core'] if h['status_core'] is not None else ('정의' if h['kind']=='정의' else None)
    if h['kind'] == '정의' and h['status_core'] is None:
        hs = '정의'
    hs_n = (hs or '').replace('`','')
    st_n = status.replace('`','')
    if hs_n != st_n:
        P("지도 지위 다름:", lab, "| 지도:", status, "| 장:", hs)
    # gist vs name
    hn = h['name'] or ''
    if hn and gist != hn:
        P("지도 요지 다름:", lab, "| 지도:", gist, "| 장:", hn)
    # declared deps (head labels) vs inputs before '본문 인용:'
    if '본문 인용:' in inputs:
        decl, body = inputs.split('본문 인용:')
    else:
        decl, body = inputs, ''
    decl_set = set(LAB.findall(decl))
    body_set = set(LAB.findall(body))
    hdl = set(h['head_labels'])
    if decl_set != hdl:
        P("지도 선언 의존 다름:", lab, "| 지도:", sorted(decl_set), "| 장 머리:", sorted(hdl))
    bl = set(h['body_labels']) - hdl
    if body_set != bl:
        P("지도 본문 인용 다름:", lab, "| 지도만:", sorted(body_set - bl), "| 장만:", sorted(bl - body_set))
    # recid
    rec_head = h['recid'] or ''
    rec_head_set = set(re.findall(r'r[0-9a-f]{7}', rec_head))
    rec_map_set = set(re.findall(r'r[0-9a-f]{7}', recs.split('/')[0]))
    if h['kind'] == '정의' and h['status'] and not h['recid']:
        rec_head_set = set(re.findall(r'r[0-9a-f]{7}', h['status']))
    if rec_head_set != rec_map_set:
        P("지도 기록 식별자 다름:", lab, "| 지도:", sorted(rec_map_set), "| 장:", sorted(rec_head_set), "| 머리 대괄호:", h['status'])
P("지도에 없는 장 파일 라벨:", [l for l in order if l not in seenD])
out.close()
print(open(os.path.join(SD, "_N14_compare_out.txt"), encoding='utf-8').read()[:6000])
