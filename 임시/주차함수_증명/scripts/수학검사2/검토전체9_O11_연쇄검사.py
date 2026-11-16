# -*- coding: utf-8 -*-
"""(A) 11.3이 '…의 증명을 거쳐'라 적은 연쇄가 실제로 그 진술의 증명 안에 있는지,
(B) 11.3 '계산 진술' 열의 진술이 머리에 계산 표지를 갖는지와 책 전체의 계산 표지 진술 목록,
(C) 부록 C 낱말 표의 '처음 정의된 절'과 낱말의 첫 출현 절,
(D) 부록 A 기호의 '처음 정의된 절'과 기호 문자열의 첫 출현 절 (O11)."""
import re, glob, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
heads = json.load(open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_O11_heads.json", encoding='utf-8'))
order = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md','장11.md']
text = {f: open(BASE+'\\'+f, encoding='utf-8').read().split('\n') for f in order}

def region(lab):
    """머리 라벨의 진술+증명 영역(머리 행부터 다음 머리 또는 ∎까지)의 행 목록"""
    h = heads[lab]; f = h['file']; lines = text[f]; i = h['line']-1
    out = []; started = False
    for j in range(i, len(lines)):
        l = lines[j]
        if j > i and re.search(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{\d+:[^}]+\}\}\s*(?!의 )', l) and not l.startswith('**증명'):
            # 다른 머리 (단, '…의 증명.' 꼴 제외)
            m = re.search(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+:[^}]+)\}\}\s*([^*]*)\*\*', l)
            if m and not m.group(3).startswith('의 '): break
        out.append((j+1, l))
        if '∎' in l and j > i: break
    return out

def cites(citing, cited):
    return [ln for ln, l in region(citing) if '{{'+cited+'}}' in l]

print("### (A) 연쇄 인용 확인: (인용하는 진술 -> 인용되는 진술): 행")
pairs = [
 ('5:old-5-18','6:cor-L'), ('6:cor-L','6:pair-rearrange'), ('6:cor-L','6:diag-first-layer'),
 ('6:lemma-Hprime','2:zeta-constants'), ('8:closed-form-envelope','2:zeta-constants'), ('8:table-tolerance','2:zeta-constants'),
 ('8:old-6-33','8:old-6-23'), ('8:old-6-33','8:old-6-30'), ('8:old-6-33','8:old-6-28'), ('8:old-6-33','8:table-tolerance'), ('8:old-6-28','8:table-tolerance'),('8:old-6-33','8:old-6-29'),
 ('8:hazard-H1','6:old-7-24'), ('7:theorem-W','6:old-7-24'), ('7:src-plus','7:theorem-W'), ('6:old-7-24','6:tilt-sum'),
 ('7:old-6-21','7:threshold-unit-ratio'), ('7:old-6-21','7:old-6-14'), ('7:old-6-15','7:old-6-14'),
 ('6:old-6-19','6:old-8-11'), ('6:D-bound','6:old-8-11'), ('6:critical-front','6:old-8-11'), ('6:V-all','6:critical-front'), ('6:V-all','6:far-window'), ('6:far-window','6:prop-R'), ('6:prop-R','6:old-8-11'),
 ('6:old-8-11','5:witness-position-bound'), ('6:small-k-bulk','5:witness-position-bound'), ('6:above-window','5:witness-position-bound'),
 ('2:b-top','2:old-2-6'), ('2:old-2-31','2:old-2-6'), ('2:old-2-13','2:old-2-6'), ('2:old-2-13','2:old-2-10'), ('2:old-2-13','2:old-2-11'), ('2:old-2-31','2:old-2-10'), ('2:old-2-31','2:old-2-11'),
 ('6:tilt-split','2:old-2-45'), ('6:path-shift','2:old-2-45'),
 ('6:old-7-21','6:old-7-20'), ('7:old-6-20','6:old-7-21'), ('7:old-6-20','7:src-plus'), ('7:old-6-20','7:old-6-15'),
 ('2:old-2-38','2:old-2-35'), ('2:old-2-38','2:old-2-36'), ('2:old-2-39','2:old-2-38'),
 ('6:old-8-13','6:same-kernel'), ('6:old-8-13','6:stay-margin-identity'), ('6:old-8-13','6:lemma-omega'), ('6:old-8-13','6:lemma-phi'),
 ('2:old-2-46','2:old-2-44'), ('7:old-6-13','4:old-4-5'), ('7:old-6-22','7:old-6-21'), ('7:old-6-22','7:old-6-20'),
 ('5:old-5-1','7:column-lemma'), ('7:qstar-implies-wlflat','7:theorem-C-moment'), ('7:qstar-implies-wlflat','7:polar-W'), ('7:theorem-C-moment','7:self-consistent-S'), ('7:theorem-C-moment','7:cor-S-prime'),('7:qstar-implies-wlflat','7:self-consistent-S'),('7:qstar-implies-wlflat','7:cor-S-prime'),
 ('7:qstar-columns','7:old-6-12'), ('7:qstar-columns','7:polar-PD'), ('7:src-plus','7:old-6-12'), ('7:src-plus','7:polar-PD'),('7:theorem-W','7:polar-PD'),('7:theorem-W','7:old-6-12'),
 ('6:V-all','6:theorem-U'), ('6:V-all','6:theorem-D'), ('6:V-all','6:v-negative'), ('6:old-6-19','6:theorem-U'),('6:old-6-19','6:theorem-D'),
 ('7:old-6-13','7:pair-check-10000'), ('7:old-6-13','7:pair-reach-table'), ('7:old-6-13','7:analytic-transfer'), ('7:old-6-13','7:integer-strips'), ('7:old-6-13','7:hermite-nu'),
 ('5:old-5-18','5:old-5-13'),('5:old-5-18','5:old-5-32'),('5:old-5-18','5:band-inequality'),('5:old-5-18','5:old-5-12'),('5:old-5-18','5:old-5-2'),('5:old-5-18','5:old-5-4'),('5:old-5-18','5:old-5-5'),('5:old-5-18','5:old-5-7'),('5:old-5-18','4:old-4-9'),('5:old-5-11','4:old-4-9'),('5:old-5-11','5:old-5-4'),('5:old-5-11','5:old-5-5'),('5:old-5-11','5:old-5-7'),('5:old-5-18','5:old-5-11'),
 ('9:old-7-16','6:old-7-13'), ('9:old-7-45','7:old-6-22'), ('10:old-8-14','7:threshold-unit-ratio'),
]
for a, b in pairs:
    if a not in heads or b not in heads:
        print(f"  !! 라벨 없음: {a} / {b}"); continue
    c = cites(a, b)
    print(f"  {a} -> {b}: {'행 '+','.join(map(str,c)) if c else '없음 !!'}   [{heads[a]['file']}:{heads[a]['line']}]")

print("
### (B) 계산 표지를 가진 진술 전부 (머리의 지위 부분)")
for lab, h in heads.items():
    mm = re.findall(r'\[([^\[\]]*)\]', h['rest'])
    st = mm[-1] if mm else ''
    if '계산' in st:
        print(f"  {lab:32s} {h['file']}:{h['line']} §{h['sec']} :: {st}")

print("\n### (B2) 11.3 '계산 진술' 열의 라벨과 그 머리의 지위")
ch11 = text['장11.md']; in113=False
for l in ch11:
    if l.startswith('### 11.3'): in113=True
    if l.startswith('### 11.4'): in113=False
    if in113 and l.startswith('| ') and not l.startswith('|---'):
        cells=[c.strip() for c in l.strip().strip('|').split(' | ')]
        if len(cells)<2 or cells[0]=='입력': continue
        for lab in re.findall(r'\{\{(\d+:[^}]+)\}\}', cells[1]):
            h = heads.get(lab)
            if not h: print("  !! 없음", lab); continue
            mm = re.findall(r'\[([^\[\]]*)\]', h['rest'])
            print(f"  {lab:32s} :: {mm[-1] if mm else h['rest'][:80]}")

print("\n### (C) 부록 C 낱말의 첫 출현 절")
appC = open(BASE+r'\부록C.md', encoding='utf-8').read().split('\n')
def first_occ(term):
    for f in order[:-1]:
        sec=''
        for ln,l in enumerate(text[f],1):
            m = re.match(r'^#{2,4}\s+(\d+(?:\.\d+)*)\s', l)
            if m: sec=m.group(1)
            if term in l: return f"{f}:{ln} §{sec}"
    return None
inC=False
for l in appC:
    if l.startswith('### 낱말'): inC=True
    if l.startswith('### 기록이'): inC=False
    if inC and l.startswith('| ') and not l.startswith('|---'):
        cells=[c.strip() for c in l.strip().strip('|').split(' | ')]
        if cells[0]=='이 글의 용어': continue
        terms=[t.strip() for t in re.split(r'[,·]', cells[0]) if t.strip() and '$' not in t]
        for t in terms[:3]:
            t2 = re.sub(r'\(.*?\)','',t).strip()
            if not t2: continue
            print(f"  {t2:14s} 표:{cells[2]:30s} 첫 출현: {first_occ(t2)}")

print("\n### (D) 부록 A 기호의 첫 출현 절 (기호 문자열 단순 검색)")
appA = open(BASE+r'\부록A.md', encoding='utf-8').read().split('\n')
for l in appA:
    if l.startswith('| $'):
        cells=[c.strip() for c in l.strip().strip('|').split(' | ')]
        sym = cells[0].split(', ')[0].strip('$')
        sym = sym.split(':=')[0].split('=')[0]
        occ = first_occ(sym)
        print(f"  {sym:40s} 표:{cells[2]:28s} 첫 출현: {occ}")
