# -*- coding: utf-8 -*-
r"""R13b 검산 보조: 장 파일에 나오는 글자체 붙은 토큰(\mathfrak X, \mathcal X, \mathrm{..}, \mathsf X)과
그리스 글자 명령을 모아, 장부 1.3의 그 장 묶음 행들에 글자 그대로 나오지 않는 것을 찍는다
(1.1·1.2에 있는지도 함께 적는다). 자리를 찾는 용도일 뿐이고, 찍힌 것은 원문을 열어 확인한 뒤에만 판단한다.
사용: python -I 검토전체25_R13b_tokens.py <장 파일 이름(쉼표로 여럿)> <장부 시작행> <장부 끝행>
"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'C:/math/임시/주차함수_증명/'
chs, a, b = sys.argv[1].split(','), int(sys.argv[2]), int(sys.argv[3])
T = '\n'.join(io.open(BASE + '장v2/%s.md' % ch, encoding='utf-8').read() for ch in chs)
L = io.open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
rows = '\n'.join(L[a - 1:b])
glob = '\n'.join(L[21:288])
GREEK = ('alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|varkappa|lambda|mu|nu|xi|pi|varpi|'
         'rho|varrho|sigma|varsigma|tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega')
pat = re.compile(r'\\(?:mathfrak|mathcal|mathsf|mathbb)\s*\{?[A-Za-z]\}?'
                 r'|\\mathrm\s*\{[A-Za-z]+\}|\\mathrm\s+[A-Za-z]'
                 r'|\\(?:' + GREEK + r')(?![A-Za-z])')
cnt = {}
for m in pat.finditer(T):
    t = re.sub(r'\s+', ' ', m.group(0))
    cnt[t] = cnt.get(t, 0) + 1


def norm(s):
    return s.replace('{', '').replace('}', '').replace(' ', '')


rn, gn = norm(rows), norm(glob)
for t in sorted(cnt):
    k = norm(t)
    if k not in rn:
        print('%-24s 장 %4d건  1.3묶음:없음  1.1·1.2:%s' % (t, cnt[t], '있음' if k in gn else '없음'))
