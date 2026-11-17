# -*- coding: utf-8 -*-
# R13: 장부 1.2 「뜻」 열이 라벨로 가리킨 진술(머리부터 다음 머리 전까지 + 뒤로 미룬 증명)에
#      그 행의 기호가 실제로 나오는지 본다. 안 나오면 사람이 원문으로 확인할 후보.
import re, sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
S = load('s', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_sym.py')
H = load('h', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_heads.py')
BASE = S.BASE
hs = H.heads()
text = {}
for f in H.FILES:
    L = open(BASE + '장v2/' + f + '.md', encoding='utf-8').read().split(chr(10))
    idx = [(x['line'], x['label']) for x in hs if x['file'] == f]
    for n, (ln, lab) in enumerate(idx):
        end = idx[n+1][0] - 1 if n + 1 < len(idx) else len(L)
        text[lab] = chr(10).join(L[ln-1:end])
    for i, line in enumerate(L):
        m = re.match(r'^\*\*\S+ \{\{(\d+:[^}]+)\}\}의 증명', line)
        if m:
            j = i + 1
            while j < len(L) and not re.match(r'^\*\*(정의|정리|보조정리|명제|따름정리) \{\{', L[j]) and not L[j].startswith('#'): j += 1
            text[m.group(1)] += chr(10) + chr(10).join(L[i:j])
keys = {}
for lab, t in text.items():
    ks = set()
    for seg in S.math_segments(t):
        for bs, sp, ns, sb in S.scan(seg): ks.add((bs, sp))
    keys[lab] = ks
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split(chr(10))
a, b = int(sys.argv[1]), int(sys.argv[2])
for i in range(a, b + 1):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    syms = [S.scan(s)[0] for s in S.split_top(c[0])]
    labs = list(dict.fromkeys(re.findall(r'\{\{(\d+:[^}]+)\}\}', c[2])))
    for lab in labs:
        if lab not in keys: continue
        hit = [sy for sy in syms if (sy[0], sy[1]) in keys[lab]]
        if not hit:
            m = re.search(r'.{0,60}\{\{' + re.escape(lab) + r'\}\}.{0,50}', c[2])
            print(i, c[0][:50], '| 라벨', lab, '에 이 기호 없음 | …' + (m.group(0) if m else ''))
