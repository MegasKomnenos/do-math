# -*- coding: utf-8 -*-
"""(1) 11.2 '쓰인 곳' 열 대조, (2) 11.3 표의 입력 라벨이 9장·10장·7B(정리 old-6-22 증명)에서 인용되는 자리,
(3) 11.4 문헌 저자명이 나오는 자리, (4) 부록 C 둘째 표(기록 이름→라벨) 대 진술 머리 대조 (O11)."""
import re, glob, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
heads = json.load(open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_O11_heads.json", encoding='utf-8'))

def load(f):
    return open(BASE + '\\' + f, encoding='utf-8').read().split('\n')

# 각 파일의 행별 맥락: (절, 마지막 머리 라벨, 그 머리 뒤 증명이 끝났는지)
def contexts(f):
    lines = load(f)
    ctx = []
    sec = ''; last = None; ended = True
    for ln, line in enumerate(lines, 1):
        m = re.match(r'^#{2,4}\s+(\d+(?:\.\d+)*)\s', line)
        if m: sec = m.group(1)
        hm = re.search(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+:[^}]+)\}\}', line)
        if hm:
            last = hm.group(2); ended = False
        ctx.append((sec, last, ended, line))
        if '∎' in line: ended = True
    return ctx

# ---------- (1) 11.2 쓰인 곳 ----------
print("### (1) 11.2 쓰인 곳 대조")
ch11 = load('장11.md')
for l in ch11:
    if l.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
        labs = re.findall(r'\{\{(\d+:[^}]+)\}\}', cells[1])
        secs = sorted({heads[x]['sec'] for x in labs if x in heads})
        miss = [x for x in labs if x not in heads]
        flag = '' if set(secs) == set(cells[3].split('·')) else '  !!'
        print(f"{cells[0][8:-2]:40s} 표:{cells[3]:10s} 실제:{'·'.join(secs)} {miss}{flag}")

# ---------- (2) 11.3 인용 자리 ----------
print("\n### (2) 11.3 입력 라벨의 인용 자리 (9장·10장 전체, 7B의 7.7절)")
ctx9 = contexts('장9.md'); ctx10 = contexts('장10.md'); ctx7 = contexts('장7B.md')
ctx8 = contexts('장8.md'); ctx6 = contexts('장6.md')
# 11.3 표 행 수집
in113 = False; rows113 = []
for l in ch11:
    if l.startswith('### 11.3'): in113 = True
    if l.startswith('### 11.4'): in113 = False
    if in113 and l.startswith('| ') and not l.startswith('|---') and '입력' not in l.split('|')[1]:
        rows113.append(l)
labels_in_inputs = []
for r in rows113:
    cells = [c.strip() for c in r.strip().strip('|').split(' | ')]
    labs = re.findall(r'\{\{(\d+:[^}]+)\}\}', cells[0])
    labels_in_inputs.append((cells[0][:60], labs, r))

def occurrences(lab, ctx, fname, only_sec=None):
    out = []
    for ln, (sec, last, ended, line) in enumerate(ctx, 1):
        if only_sec and not sec.startswith(only_sec): continue
        if '{{'+lab+'}}' in line:
            if last == lab and not ended and ('**'+'정리' in line or re.search(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{'+re.escape(lab), line)):
                continue  # 자기 머리
            where = f"{last}{'(뒤 준비문단)' if ended else ''}" if last else '머리말'
            out.append(f"{fname}:{ln} §{sec} in {where}")
    return out

for name, labs, r in labels_in_inputs:
    print("\n--- 입력:", name)
    for lab in labs:
        occ = occurrences(lab, ctx9, '장9') + occurrences(lab, ctx10, '장10') + occurrences(lab, ctx7, '장7B', '7.7')
        print(f"  {lab}: " + ('; '.join(occ) if occ else '(9장·10장·7.7절에 인용 없음)'))

# ---------- (3) 11.4 저자명 ----------
print("\n### (3) 11.4 문헌 저자명의 자리")
authors = ['Konheim','Foata','Celano','Aguilar','Stanley','Knuth','Flajolet','Tanner','Robbins','Petersson','Janson','Ibragimov','Ahlfors','Graham','Fortuin','FKG','Jensen','Wallis','Corless','Lambert','Grimmett','Harris','Comtet','Apostol','Titchmarsh','Faà','Euler','Cayley','Lagrange','Cauchy','Borel–Tanner','편각','표준']
allf = sorted([f.split('\\')[-1] for f in glob.glob(BASE + r"\장*.md") if '부록' not in f] + ['부록D_장'+x+'.md' for x in ['2','3','4','5A','5B','6','7A','7B','8','9','10']])
ctxs = {f: contexts(f) for f in allf}
for a in authors:
    print("\n##", a)
    for f in allf:
        for ln, (sec, last, ended, line) in enumerate(ctxs[f], 1):
            if a in line:
                where = f"{last}{'(뒤)' if ended else ''}" if last else '머리말'
                # 짧은 문맥
                i = line.find(a)
                print(f"  {f}:{ln} §{sec} in {where} :: …{line[max(0,i-60):i+60]}…")

# ---------- (4) 부록 C 이름표 ----------
print("\n### (4) 부록 C 둘째 표 대 진술 머리")
appC = load('부록C.md')
rowsC = {}
for l in appC:
    if l.startswith('| 기록 [') or l.startswith('| 기록 '):
        cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
        if len(cells) == 3:
            m = re.search(r'\{\{(\d+:[^}]+)\}\}', cells[1])
            if m: rowsC[m.group(1)] = (cells[0], cells[2])
# 머리에서 '기록 [' 가 든 것
for lab, h in heads.items():
    rest = h['rest']
    m = re.match(r'\(([^)]*)\)\s*\[', rest)
    if not m: continue
    inner = m.group(1)
    if '기록 [' in inner or '기록 ' in inner and ';' in inner:
        name_part, _, rec_part = inner.partition(';')
        c = rowsC.get(lab)
        if c is None:
            print(f"  !! 부록 C에 없음: {lab} :: {inner}")
        else:
            flag = ''
            if c[0].strip() != rec_part.strip(): flag += ' [기록이름 다름]'
            if c[1].strip() != name_part.strip(): flag += ' [이름 다름]'
            if flag: print(f"  {lab}{flag}\n     머리: {inner}\n     C  : {c[0]} | {c[1]}")
for lab in rowsC:
    if lab not in heads: print("  !! 부록 C 라벨이 머리에 없음:", lab)
    else:
        rest = heads[lab]['rest']
        if '기록' not in rest.split('[')[0] if '[' in rest else '기록' not in rest:
            print(f"  !! 부록 C에는 있으나 머리에 기록 이름 없음: {lab} :: {rest[:100]}")
