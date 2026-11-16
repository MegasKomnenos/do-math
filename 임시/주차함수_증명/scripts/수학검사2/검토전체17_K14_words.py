# -*- coding: utf-8 -*-
"""K14: 장부 3절 낱말의 첫 출현 절을 장 파일에서 찾아 「첫 정의 절」과 견준다(후보 표시; 판단은 손으로)."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
# (절, 파일, 행, 텍스트) 순서 목록
seq = []
for c in CH:
    sec = c.replace('장','') + '.0'
    for ln, line in enumerate(open(os.path.join(ROOT, '장v2', c + '.md'), encoding='utf-8'), 1):
        m = re.match(r'^###\s+(\d+\.\d+)', line)
        if m:
            sec = m.group(1)
        m2 = re.match(r'^####\s+(\d+\.\d+)', line)
        if m2:
            sec = m2.group(1)
        seq.append((sec, c, ln, line))
def secnum(s):
    a, b = s.split('.')[:2]
    return (int(re.sub(r'[A-Z]', '', a)), int(b))
lines = open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8').read().split('\n')
s = next(i for i, l in enumerate(lines) if l.startswith('## 3.'))
e = next(i for i, l in enumerate(lines) if l.startswith('## 4.'))
out = []
for l in lines[s:e]:
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', l)
    if not m or m.group(1) in ('낱말', '---'):
        continue
    words_cell, meaning, first, old = [x.strip() for x in m.groups()]
    if first.startswith('—') or '일반어' in first or '부록' in first:
        continue
    decl = re.findall(r'\d+\.\d+', first)
    if not decl:
        out.append(('절 없음', words_cell, first)); continue
    dmin = min(secnum(x) for x in decl)
    # 낱말: 셀을 쉼표·세미콜론으로 나눈 첫 낱말(괄호 제거), 수식 제외
    w = re.split(r'[,;(（]', words_cell)[0].strip()
    w = re.sub(r'\$[^$]*\$', '', w).strip()
    if len(w) < 2:
        out.append(('짧은 낱말(손으로)', words_cell, first)); continue
    found = None
    for sec, c, ln, line in seq:
        if w in line:
            found = (sec, c, ln); break
    if not found:
        out.append(('장에 없음', w, first)); continue
    fs = secnum(found[0])
    if fs < dmin:
        out.append(('먼저 나옴', w, '장부=' + first, '첫 출현=%s(%s:%d)' % found))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_words_out.txt'), 'w', encoding='utf-8') as f:
    for o in out:
        f.write('\t'.join(o) + '\n')
print('flagged', len(out))
