# -*- coding: utf-8 -*-
"""I14: 장 파일의 진술 머리를 추출해 대응표·의존지도 1절과 대조한다."""
import re, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측)\s+\{\{(\d+):([^}]+)\}\}\s*(?:\(([^)]*(?:\([^)]*\)[^)]*)*)\))?\s*(?:\[([^\]]*)\])?\.?\*\*')
sec_re = re.compile(r'^###\s+(\d+\.\d+)')
heads = []
counter = {}
for ch in order:
    path = os.path.join(ROOT,'장v2',ch+'.md')
    sec = None
    with open(path,encoding='utf-8') as f:
        lines = f.readlines()
    for i,line in enumerate(lines,1):
        m = sec_re.match(line)
        if m: sec = m.group(1); continue
        m = head_re.match(line)
        if m:
            kind, chap, lab, name, status = m.groups()
            counter[chap] = counter.get(chap,0)+1
            num = f"{chap}.{counter[chap]}"
            heads.append(dict(file=ch,line=i,kind=kind,chap=chap,label=f"{chap}:{lab}",name=name or '',status=status or '',sec=sec,num=num,
                              headcites=re.findall(r'\{\{(\d+:[^}]+)\}\}', line)[1:]))
        elif line.startswith('**') and re.search(r'\{\{\d+:', line[:60]) and not head_re.match(line):
            print("UNPARSED HEAD?", ch, i, line[:150])
print("total heads", len(heads))
with open(os.path.join(ROOT,'scripts','수학검사2','_I14_heads.json'),'w',encoding='utf-8') as f:
    json.dump(heads,f,ensure_ascii=False,indent=0)

# 대응표 대조
tab = {}
with open(os.path.join(ROOT,'대조v2','라벨_번호_대응표_1114.md'),encoding='utf-8') as f:
    for line in f:
        m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \| ([^|]+) \| ([^|]*) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|', line)
        if m:
            tab[m.group(1)] = dict(kind=m.group(2).strip(), name=m.group(3).strip(), num=m.group(4).strip(), old=m.group(5).strip(), sec=m.group(6).strip())
print("대응표 rows", len(tab))
hl = {h['label']:h for h in heads}
for lab,h in hl.items():
    if lab not in tab: print("대응표에 없음:", lab, h['file'], h['line'], h['num']); continue
    t = tab[lab]
    if t['kind']!=h['kind']: print("종류 다름", lab, t['kind'], h['kind'])
    if t['num']!=h['num']: print("번호 다름", lab, "표", t['num'], "현행", h['num'])
    if t['sec']!=h['sec']: print("절 다름", lab, "표", t['sec'], "현행", h['sec'])
    nm = h['name']
    tn = t['name']
    if tn=='—': tn=''
    if tn!=nm: print("이름 다름", lab, "| 표:", tn, "| 현행:", nm)
for lab in tab:
    if lab not in hl: print("표에 있으나 머리 없음:", lab, tab[lab])
# 순서 확인: 표의 행 순서가 현행 머리 순서와 같은가
