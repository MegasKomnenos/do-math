# -*- coding: utf-8 -*-
"""N14: 의존지도 1절의 「문헌」·「부록 D 계산」 열을 11.4절·11.2절 표에서 다시 만들어 맞추고, 3절 낱말의 장이 5절 낱말 열에 있는지 본다."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
ch11 = open(os.path.join(ROOT, "장v2", "장11.md"), encoding='utf-8').read().split('\n')
# 11.2 table: 부록 D 항목 | 확인하는 진술 | 산술 등급 | ...
d_of = {}
lit_of = {}
sec = None
for ln in ch11:
    m = re.match(r'^### (\d+\.\d+)', ln)
    if m: sec = m.group(1)
    if not ln.startswith('| '): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    if sec == '11.2' and c[0].startswith('부록 D.'):
        item = re.search(r'\{\{(D:[^}]+)\}\}', c[0])
        for l in LAB.findall(c[1]):
            d_of.setdefault(l, set()).add(item.group(1) if item else c[0])
    if sec == '11.4' and len(c) >= 2 and not c[0].startswith('문헌') and not c[0].startswith('---'):
        # find column with labels
        labs = set()
        for cell in c:
            labs |= set(LAB.findall(cell))
        for l in labs:
            lit_of.setdefault(l, set()).add(c[0][:40])
dl = open(os.path.join(ROOT, "의존지도_v2.md"), encoding='utf-8').read().split('\n')
s = dl.index("## 1. 진술별 입력 표"); e = dl.index("### 1.1 뺌·대체된 라벨")
nd = nl = 0
for ln in dl[s:e]:
    if not ln.startswith('| `{{'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    lab = c[0].strip('`')[2:-2]
    lit, dcol = c[7], c[8]
    dset = set(re.findall(r'\{\{(D:[^}]+)\}\}', dcol))
    if dset != d_of.get(lab, set()):
        print("부록 D 열 다름:", lab, "| 지도:", sorted(dset), "| 11.2:", sorted(d_of.get(lab, set()))); nd += 1
    has_lit = lit != '—'
    if has_lit != (lab in lit_of):
        print("문헌 열 유무 다름:", lab, "| 지도:", lit[:60], "| 11.4:", sorted(lit_of.get(lab, set()))); nl += 1
print("부록 D 열 불일치:", nd, "| 문헌 열 불일치:", nl)
print("11.2 표의 라벨 가운데 지도에 부록 D가 없는 것:", [l for l in d_of if l not in {ln.split('`')[1][2:-2] for ln in dl[s:e] if ln.startswith('| `{{')}])

# 3절 낱말 vs 5절 낱말 열
lines = open(os.path.join(ROOT, "장부_v2.md"), encoding='utf-8').read().split('\n')
s3 = lines.index("## 3. 낱말 사전"); e3 = lines.index("## 4. 이름 사전: 기록의 결과 이름과 이 글의 라벨")
s5 = lines.index("## 5. 장별 배정과 여유 글자"); e5 = lines.index("## 6. 예약 글자")
words5 = {}
for ln in lines[s5:e5]:
    if not re.match(r'^\| \d+ \|', ln): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    words5[c[0]] = c[2]
miss = []
for ln in lines[s3:e3]:
    if not ln.startswith('| ') or ln.startswith('| 낱말') or ln.startswith('|---'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c) < 4: continue
    words, defsec = c[0], c[2]
    if defsec.startswith('—') or '부록 D' in defsec: continue
    secs = re.findall(r'(\d+)\.\d+', defsec)
    if not secs: continue
    chap = min(secs, key=int)
    w0 = re.sub(r'\(.*?\)', '', words).split(',')[0].strip()
    if w0 not in words5.get(chap, ''):
        miss.append((w0, defsec, chap))
print("3절 낱말이 5절 해당 장 열에 없음:", miss)
