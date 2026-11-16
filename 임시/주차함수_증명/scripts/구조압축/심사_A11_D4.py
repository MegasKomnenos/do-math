# -*- coding: utf-8 -*-
"""D4: 11.2절 표가 부록 D를 그대로 옮긴 것인지 — 항목별 「독립 재계산」 줄과 표 행의 대조, 분량 셈."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
ch11 = open(os.path.join(ROOT,'장v2','장11.md'), encoding='utf-8').read().split('\n')
rows = {}
in_tab = False
for ln in ch11:
    if ln.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        lab = re.match(r'부록 D\.\{\{(D:[^}]+)\}\}', cells[0]).group(1)
        rows[lab] = cells
print('11.2절 표 행 수:', len(rows))
items = {}
for f in sorted(glob.glob(os.path.join(ROOT,'장v2','부록D_장*.md'))):
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{(D:[^}]+)\}\}(.*?)(?=^### D\.\{\{|\Z)', txt, re.S|re.M):
        lab = m.group(1); body = m.group(2)
        g = re.search(r'^\*\*독립 재계산\.\*\*\s*(.*)$', body, re.M)
        gr = re.search(r'^\*\*산술 등급\.\*\*\s*(.*)$', body, re.M)
        items[lab] = (os.path.basename(f), g.group(1) if g else None, gr.group(1) if gr else None, len(body.encode('utf-8')))
print('부록 D 항목 수:', len(items))
print('표에만/부록에만:', set(rows)-set(items), set(items)-set(rows))
def norm(s):
    s = re.sub(r'\s+','',s)
    return s
same = diff = 0
tab_bytes = sum(len(' | '.join(r).encode('utf-8')) for r in rows.values())
col_bytes = sum(len((r[4]+' '+r[5]).encode('utf-8')) for r in rows.values())
app_bytes = sum(len(v[1].encode('utf-8')) for v in items.values() if v[1])
print('11.2 표 전체 바이트:', tab_bytes, '/ 그중 재계산·독립 재계산 두 열:', col_bytes)
print('부록 D 「독립 재계산」 줄 합계 바이트:', app_bytes, '/ 부록 D 항목 본문 합계:', sum(v[3] for v in items.values()))
for lab, r in rows.items():
    app = items.get(lab, (None,None,None,0))[1]
    if app is None: print('부록 D에 독립 재계산 줄 없음:', lab); continue
    a = norm(r[4] + ' ' + r[5]); b = norm(app)
    if a == b: same += 1
    else:
        diff += 1
        # 차이 위치 찾기
        k = 0
        while k < min(len(a),len(b)) and a[k]==b[k]: k += 1
        print(f'다름: {lab} | 길이 표 {len(a)} 부록 {len(b)} | 첫 차이 위치 {k}: 표 …{a[max(0,k-20):k+40]}… / 부록 …{b[max(0,k-20):k+40]}…')
print('같음(공백 무시):', same, '다름:', diff)
# 산술 등급 열 대조
for lab, r in rows.items():
    gr = items.get(lab,(None,None,None,0))[2]
    if gr: print(f'{lab}: 표 등급 「{r[2]}」 / 부록 등급 줄 「{gr[:80]}」')
