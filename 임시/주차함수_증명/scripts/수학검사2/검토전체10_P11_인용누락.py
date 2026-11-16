# -*- coding: utf-8 -*-
"""두 증명의 폐포에 든 9장·10장 진술(과 7:old-6-22)이 머리 표지·진술·증명에서 직접 인용하는 앞 장 라벨마다,
11.3 세 표의 해당 입력 행이 그 진술을 인용 자리로 적었는지 검사한다."""
import re, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
S = r"C:\math\임시\주차함수_증명\scripts\수학검사2"
cl = json.load(open(os.path.join(S,'검토전체10_P11_closure.json'),encoding='utf-8'))
C9, C10 = set(cl['C9']), set(cl['C10'])
rev = json.load(open(os.path.join(S,'검토전체10_P11_rev.json'),encoding='utf-8'))  # 앞장라벨 -> [(citing, kind, [where])]
ch11 = open(os.path.join(BASE,'장11.md'),encoding='utf-8').read()
i0 = ch11.index('**공유 입력.**'); i3 = ch11.index('### 11.4')
rows=[]
for ln in ch11[i0:i3].split('\n'):
    if ln.startswith('| ') and not ln.startswith('| 입력') and not ln.startswith('|---'):
        c=[x.strip() for x in ln.strip().strip('|').split(' | ')]; rows.append(c)
def row_for(lab):
    for c in rows:
        if lab in re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', c[0]): return c
    return None
def chap(lab): return lab.split(':')[0]
problems=[]
for lab, lst in rev.items():
    if chap(lab) in ('9','10'): continue   # 앞 장 라벨만
    r = row_for(lab)
    for citing, kind, where in lst:
        if citing.startswith('(준비문단'): continue
        if not any(w in ('표지','진술','증명') for w in where): continue   # 뒤문단만이면 제외
        inC = (citing in C9) or (citing in C10) or citing=='7:old-6-22'
        if not inC: continue
        if r is None:
            problems.append(f"[표에 행 없음] {lab} <- {citing}({kind}) {where}")
            continue
        cite_cols = ' '.join(r[2:])
        if citing not in cite_cols and not ('10.7절' in cite_cols and citing=='10:old-8-37'):
            problems.append(f"[행 있음, 인용 자리에 없음] {lab} <- {citing}({kind}) {where}   행: {r[0][:50]}")
for p in sorted(problems): print(p)
print("검사한 폐포 크기", len(C9), len(C10))
