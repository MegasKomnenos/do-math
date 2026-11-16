# -*- coding: utf-8 -*-
"""T11: 부록 A의 「처음 정의된 절」과 기호가 본문에 처음 나오는 절을 맞춘다(자리 찾기용)."""
import re, os
ROOT = r"C:\math\임시\주차함수_증명"; CH = os.path.join(ROOT, "장v2")
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
sec_re = re.compile(r'^###\s+(\d+(?:\.\d+)*)')
docs = []
for ch in order:
    sec = ch.replace('장','')+'.0'
    for i, line in enumerate(open(os.path.join(CH, ch+'.md'), encoding='utf-8'), 1):
        m = sec_re.match(line)
        if m: sec = m.group(1)
        docs.append((ch, i, sec, line))
rows = []
cur = None
for line in open(os.path.join(CH, '부록A.md'), encoding='utf-8'):
    if line.startswith('### '): cur = line.strip('# \n')
    if line.startswith('| $'):
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        if len(c) >= 3: rows.append((cur, c[0], c[2]))
def norm(s): return s.replace(' ', '')
for grp, sym, secs in rows:
    alts = re.findall(r'\$([^$]+)\$', sym)
    found = None
    for a in alts:
        a0 = norm(a)
        # 첨자 인수 제거한 핵심도 시도
        cores = [a0]
        pass
        for ch, i, sec, line in docs:
            if a0 in norm(line):
                found = (a, ch, i, sec); break
        if found: break
    exp = secs.split('(')[0].split(',')[0].strip()
    first_exp = re.findall(r'\d+\.\d+', secs)
    ok = found and (found[3] in first_exp or found[3].startswith(exp))
    if not found:
        print(f"[못찾음] {grp} | {sym[:60]} | 표 {secs}")
    elif not ok:
        print(f"[다름] {sym[:60]} | 표 {secs} | 첫 출현 {found[1]}:{found[2]} §{found[3]} (찾은 꼴 {found[0][:40]})")
