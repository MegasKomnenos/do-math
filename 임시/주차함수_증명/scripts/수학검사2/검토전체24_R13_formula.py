# -*- coding: utf-8 -*-
# R13: 장부 1.2 「뜻」 열의 식(길이 12자 이상의 수식 조각)이 장 파일(본문+부록 D)에 같은 꼴로 있는지 본다.
#      없는 것은 사람이 원문과 맞댈 후보다(사전은 줄여 적을 수 있으므로 없음 자체는 문제가 아니다).
import re, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
BASE = r'C:/math/임시/주차함수_증명/'
def norm(s):
    s = re.sub(r'\\(,|;|!| |quad|qquad)', '', s)
    s = re.sub(r'\\(bigl|bigr|Bigl|Bigr|biggl|biggr|left|right|displaystyle)(?![A-Za-z])', '', s)
    s = s.replace('\\tfrac', '\\frac').replace('\\dfrac', '\\frac')
    s = s.replace("'", '^\\prime').replace('^{\\prime}', '^\\prime')
    s = re.sub(r'\s+', '', s)
    # {x} -> x (한 글자·한 명령)
    for _ in range(3):
        s = re.sub(r'\{([A-Za-z0-9]|\\[A-Za-z]+)\}', r'\1', s)
    s = re.sub(r'\\tag\{[^}]*\}', '', s)
    return s
corpus = ''
for f in sorted(glob.glob(BASE + '장v2/장*.md')) + sorted(glob.glob(BASE + '장v2/부록D*.md')):
    corpus += norm(open(f, encoding='utf-8').read()) + '\n'
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
a, b, col = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
minlen = int(sys.argv[4]) if len(sys.argv) > 4 else 14
nf = 0; tot = 0
for i in range(a, b + 1):
    line = L[i-1]
    if not line.startswith('|'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    if len(c) <= col: continue
    for seg in re.findall(r'\$([^$]+)\$', c[col]):
        n = norm(seg)
        if len(n) < minlen: continue
        tot += 1
        if n in corpus: continue
        # 등호·부등호에서 쪼갠 조각들로 다시
        parts = [p for p in re.split(r'(?<![<>:])=|:=|\\le(?![A-Za-z])|\\ge(?![A-Za-z])|\\to(?![A-Za-z])', n) if len(p) >= minlen]
        miss = [p for p in parts if p not in corpus]
        if parts and not miss: continue
        nf += 1
        print(i, c[0][:40], '||', seg[:200], ('|| 없는 조각: ' + ' ## '.join(m[:90] for m in miss)) if parts else '')
print('식 조각', tot, '장 파일에 같은 꼴 없음', nf)
