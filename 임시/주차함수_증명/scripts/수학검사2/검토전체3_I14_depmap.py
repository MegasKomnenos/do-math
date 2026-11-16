# -*- coding: utf-8 -*-
"""I14: 의존지도 1절을 현행 장 파일과 대조한다."""
import re, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}')
defer_re = re.compile(r'^\*\*(?:정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}의 증명')
sec_re = re.compile(r'^###\s+(\d+\.\d+)')
lab_re = re.compile(r'\{\{(\d+:[^}]+)\}\}')
cur = {}
for ch in order:
    sec=None; owner=None
    for i,line in enumerate(open(os.path.join(ROOT,'장v2',ch+'.md'),encoding='utf-8'),1):
        m = sec_re.match(line)
        if m: sec=m.group(1); continue
        dm = defer_re.match(line)
        if dm:
            owner = f"{dm.group(1)}:{dm.group(2)}"
            cur[owner]['body'].update(lab_re.findall(line))
            continue
        hm = head_re.match(line)
        if hm:
            lab = f"{hm.group(2)}:{hm.group(3)}"
            # bracket
            b = re.search(r'\[([^\]]*)\]\.?\*\*', line)
            br = b.group(1) if b else ''
            parts = br.rsplit(';',1)
            if len(parts)==2 and re.search(r'r[0-9a-f]{7}', parts[1]):
                status, ids = parts[0].strip(), parts[1].strip()
            else:
                status, ids = br.strip(), ''
            labs = lab_re.findall(line)
            cur[lab] = dict(sec=sec, status=status, ids=ids, head=set(labs[1:]), body=set(), file=ch, line=i)
            owner = lab
            continue
        if owner and '{{' in line:
            cur[owner]['body'].update(lab_re.findall(line))
# 의존지도 파싱
rows = {}
started=False
for line in open(os.path.join(ROOT,'의존지도_v2.md'),encoding='utf-8'):
    if line.startswith('## 1.'): started=True; continue
    if line.startswith('### 1.1'): break
    if not started: continue
    m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \|(.*)\|\s*$', line)
    if not m: continue
    cells = [c.strip() for c in m.group(2).split(' | ')]
    if len(cells)<9: cells = [c.strip() for c in m.group(2).split('|')]
    rows[m.group(1)] = cells
print("의존지도 rows", len(rows), "현행 heads", len(cur))
for lab in cur:
    if lab not in rows: print("의존지도에 없음:", lab)
for lab in rows:
    if lab not in cur: print("의존지도에 있으나 머리 없음:", lab)
for lab,c in cur.items():
    if lab not in rows: continue
    r = rows[lab]
    sec, old, gist, status, inputs, claims = r[0], r[1], r[2], r[3], r[4], r[5]
    if sec!=c['sec']: print("절 다름", lab, "지도", sec, "현행", c['sec'])
    st = status.replace('`','')
    if st!=c['status']: print("지위 다름", lab, "\n   지도:", st, "\n   현행:", c['status'])
    # inputs
    if '본문 인용:' in inputs:
        hpart, bpart = inputs.split('본문 인용:',1)
    else:
        hpart, bpart = inputs, ''
    hl = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', hpart)); bl=set(re.findall(r'\{\{(\d+:[^}]+)\}\}', bpart))
    if hl!=c['head']: print("머리 인용 다름", lab, "지도-현행", hl-c['head'], "현행-지도", c['head']-hl)
    body = c['body']-c['head']-{lab}
    if bl!=body: print("본문 인용 다름", lab, c['file'], c['line'], "\n   지도만:", sorted(bl-body), "\n   현행만:", sorted(body-bl))
    # ids
    ids_map = set(re.findall(r'r[0-9a-f]{7}', claims.split('/')[0]))
    ids_cur = set(re.findall(r'r[0-9a-f]{7}', c['ids']))
    if ids_map!=ids_cur: print("기록 식별자 다름", lab, "지도", ids_map, "현행", ids_cur)
