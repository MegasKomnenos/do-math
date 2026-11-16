# -*- coding: utf-8 -*-
"""F11: 11.3절 세 입력 표의 완전성 — 9장·10장(과 정리 7-22의 증명)이 인용하는 앞 장의 진술 라벨 집합과 표의 라벨 집합을 맞춘다."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = {}
for l in open(ROOT + r'\대조v2\수학검사2\_F11_heads.tsv', encoding='utf-8'):
    f, ln, sec, kind, ch, lab, rest = l.rstrip('\n').split('\t')
    heads[(ch, lab)] = (kind, f, ln, sec)
lab_re = re.compile(r'\{\{(\w+):([^}]+)\}\}')
def cited(text):
    return {(c, l) for c, l in lab_re.findall(text) if c not in ('D',)}
ch9 = open(ROOT + r'\장v2\장9.md', encoding='utf-8').read()
ch10 = open(ROOT + r'\장v2\장10.md', encoding='utf-8').read()
L7 = open(ROOT + r'\장v2\장7B.md', encoding='utf-8').read().split('\n')
# 정리 7-22의 머리부터 다음 머리 전까지
s = next(i for i, l in enumerate(L7) if l.startswith('**정리 {{7:old-6-22}}'))
e = next(i for i in range(s + 1, len(L7)) if re.match(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{', L7[i]) or L7[i].startswith('### '))
t722 = '\n'.join(L7[s:e])
print('정리 7-22 블록 행:', s + 1, '-', e)
ch11 = open(ROOT + r'\장v2\장11.md', encoding='utf-8').read().split('\n')
tab = '\n'.join(l for l in ch11[85:130])  # 11.3 세 표
in_tab = cited(tab)
def prior(labs, chs):
    return {x for x in labs if x[0] in chs}
prev = {'1','2','3','4','5','6','7','8'}
c9 = prior(cited(ch9), prev); c10 = prior(cited(ch10), prev); c722 = prior(cited(t722), prev | {'7'})
for name, cs in [('장9', c9), ('장10', c10), ('정리 7-22 블록', c722)]:
    miss = sorted(x for x in cs if x not in in_tab)
    print(f'\n== {name}이 인용하지만 11.3 표에 없는 앞 장 라벨 ({len(miss)}):')
    for x in miss:
        h = heads.get(x, ('?', '?', '?', '?'))
        print(f'   {h[0]} {{{{{x[0]}:{x[1]}}}}} [{h[1]}:{h[2]} {h[3]}]')
# 표에 있으나 9·10장·7-22 어디서도 인용되지 않는 앞 장 라벨
allc = c9 | c10 | c722
print('\n== 11.3 표에 있으나 장9·장10·정리 7-22 블록 어디에도 인용되지 않은 앞 장 라벨:')
for x in sorted(prior(in_tab, prev)):
    if x not in allc:
        h = heads.get(x, ('?', '?', '?', '?'))
        print(f'   {h[0]} {{{{{x[0]}:{x[1]}}}}} [{h[1]}:{h[2]}]')
