# -*- coding: utf-8 -*-
"""N14: 장부 3절 낱말의 「첫 정의 절」을 장 파일에서 그 낱말이 처음 나오는 장·절과 견준다(1차 걸러내기)."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
SD = os.path.join(ROOT, "scripts", "수학검사2")
CH = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
# build (chapter-order text with section markers)
docs = []
for ch in CH:
    cur = None
    for i, ln in enumerate(open(os.path.join(ROOT, "장v2", ch + ".md"), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^(#{3,4}) (\d+(?:\.\d+)+)', ln)
        if m: cur = m.group(2)
        docs.append((ch, i, cur, ln))
def first_occ(word):
    for ch, i, sec, ln in docs:
        if word in ln:
            return ch, i, sec, ln
    return None
def sec_key(s):
    return tuple(int(x) for x in s.split('.')) if s else (999,)
lines = open(os.path.join(ROOT, "장부_v2.md"), encoding='utf-8').read().split('\n')
s = lines.index("## 3. 낱말 사전"); e = lines.index("## 4. 이름 사전: 기록의 결과 이름과 이 글의 라벨")
out = open(os.path.join(SD, "_N14_words_out.txt"), 'w', encoding='utf-8')
for ln in lines[s:e]:
    if not ln.startswith('| ') or ln.startswith('| 낱말') or ln.startswith('|---'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c) < 4: continue
    words, meaning, defsec, old = c[0], c[1], c[2], c[3]
    if defsec.startswith('—') or '부록 D' in defsec: continue
    secs = re.findall(r'\d+\.\d+', defsec)
    if not secs: continue
    earliest_claim = min(secs, key=sec_key)
    for w in [x.strip() for x in re.split(r'[,;]', words) if x.strip()]:
        w0 = re.sub(r'\(.*?\)', '', w).strip()
        w0 = w0.replace('$', '')
        if len(w0) < 2 or '\\' in w0: continue
        fo = first_occ(w0)
        if fo is None:
            out.write(f"없음: 「{w0}」 (행: {words[:30]} | 첫 정의 절 {defsec})\n"); continue
        ch, i, sec, text = fo
        if sec is None: continue
        if sec_key(sec)[:2] < sec_key(earliest_claim)[:2]:
            out.write(f"앞섬: 「{w0}」 첫 출현 {ch}:{i} ({sec}) < 장부 {defsec} | {text.strip()[:90]}\n")
out.close()
print(open(os.path.join(SD, "_N14_words_out.txt"), encoding='utf-8').read())
