# -*- coding: utf-8 -*-
"""F11: 부록 C 「기록이 결과에 붙인 이름과 이 글의 번호」 표를 진술 머리의 괄호(이름; 기록 [r…]의 …)와 대조한다."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = {}
for l in open(ROOT + r'\대조v2\수학검사2\_F11_heads.tsv', encoding='utf-8'):
    f, ln, sec, kind, ch, lab, rest = l.rstrip('\n').split('\t')
    m = re.match(r'\s*\((.*?)\)\s*\[', rest)
    title = m.group(1) if m else ''
    heads[(kind, ch, lab)] = (f, ln, title, rest)
crows = []
for l in open(ROOT + r'\장v2\부록C.md', encoding='utf-8'):
    m = re.match(r'\| (기록 \[r[0-9a-f]{7}\].*?) \| (정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\} \| (.*?) \|\s*$', l)
    if m: crows.append(m.groups())
print('부록 C 이름 표 행 수:', len(crows))
seenC = set()
for recname, kind, ch, lab, ourname in crows:
    key = (kind, ch, lab); seenC.add((ch, lab))
    if key not in heads:
        alt = [k for k in heads if k[1:] == (ch, lab)]
        print(f'!! 머리 없음/종류 다름: C {kind} {{{{{ch}:{lab}}}}} / 실제 {[k[0] for k in alt]}'); continue
    f, ln, title, rest = heads[key]
    # 이 글의 이름 = title의 ';' 앞부분
    ourname_head = title.split(';')[0].strip()
    rec_head = title.split(';', 1)[1].strip() if ';' in title else ''
    if ourname.strip() != ourname_head:
        print(f'[이름 다름] {{{{{ch}:{lab}}}}} ({f}:{ln})\n   C : {ourname}\n   머리: {ourname_head}')
    # 기록 이름 비교(공백 정규화)
    norm = lambda s: re.sub(r'\s+', '', s)
    if norm(rec_head) != norm(recname):
        print(f'[기록 이름 다름] {{{{{ch}:{lab}}}}} ({f}:{ln})\n   C : {recname}\n   머리: {rec_head}')
# 머리에 「기록 [r…]의」가 있는데 C 표에 없는 진술
for (kind, ch, lab), (f, ln, title, rest) in heads.items():
    if '기록 [r' in title and (ch, lab) not in seenC:
        print(f'[C 표에 없음] {f}:{ln} {kind} {{{{{ch}:{lab}}}}} ({title[:120]})')
