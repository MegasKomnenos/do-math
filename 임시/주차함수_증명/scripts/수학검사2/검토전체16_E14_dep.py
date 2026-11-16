# -*- coding: utf-8 -*-
"""E14: 의존지도 1절의 지위·입력(머리 인용) 열을 장 파일 진술 머리와 견준다."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
heads = {}
for line in open(f"{ROOT}/scripts/수학검사2/_E14_heads.tsv", encoding='utf-8'):
    f, ln, sec, kind, ch, lab, paren, status = line.rstrip("\n").split("\t")
    if status.startswith("의 증명") or (paren=="" and status.startswith("의")): continue
    heads[(ch,lab)] = dict(f=f, ln=int(ln), sec=sec, kind=kind, paren=paren, status=status)
lines = open(f"{ROOT}/의존지도_v2.md", encoding='utf-8').read().split("\n")
s = next(i for i,l in enumerate(lines) if l.startswith("## 1."))
e = next(i for i,l in enumerate(lines) if l.startswith("### 1.1"))
n=0
for l in lines[s:e]:
    if not l.startswith("| `{{"): continue
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells)!=10: print("CELLS", len(cells), l[:60]); continue
    lab, sec, old, gist, status, inputs, rec, lit, appD, note = cells
    m = re.match(r'`\{\{(\d+):([^}]+)\}\}`', lab); key=(m.group(1), m.group(2)); n+=1
    if key not in heads: print("MISSING", lab); continue
    h = heads[key]
    # 절
    hs = '.'.join(h['sec'].split('.')[:2])
    if hs != sec: print("SEC", lab, sec, h['sec'])
    # 지위: 머리 대괄호 ; 앞
    st = h['status']
    mm = re.match(r'\[(.*)\]$', st)
    if not mm:
        if h['kind']=='정의':
            hstat = "정의"
            if status != "정의": print("STATUS(정의)", lab, repr(status), repr(st))
        else:
            print("NOBRACKET", lab, repr(st))
        hstat=None
    else:
        inner = mm.group(1)
        hstat = inner.split(';')[0].strip()
        if h['kind']=='정의' and status=='정의':
            pass
        elif hstat != status:
            print("STATUS", lab, "\n   지도:", status, "\n   장  :", hstat)
    # 머리 인용 라벨
    headlabs = set(re.findall(r'\{\{(\d+):([^}]+)\}\}', st))
    first = inputs.split('본문 인용:')[0]
    deplabs = set(re.findall(r'\{\{(\d+):([^}]+)\}\}', first))
    if headlabs != deplabs:
        print("DEPS", lab, "지도:", sorted(deplabs-headlabs), "장:", sorted(headlabs-deplabs))
    # 기록 식별자
    ids_head = set(re.findall(r'r[0-9a-f]{7}', st))
    ids_dep = set(re.findall(r'r[0-9a-f]{7}', rec))
    if ids_head != ids_dep:
        print("REC", lab, "지도:", sorted(ids_dep-ids_head), "장:", sorted(ids_head-ids_dep))
    # 요지(이름)
    pn = h['paren']
    if pn and gist != pn: print("GIST", lab, repr(gist), repr(pn))
print("rows", n)
