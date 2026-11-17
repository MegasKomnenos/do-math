# -*- coding: utf-8 -*-
r"""R13b 검산 보조: 장 파일에서 그리스 글자 명령과 지정한 토큰이 어느 소절(## / ### / ####)에 몇 번 나오는지 센다.
한 글자가 한 장의 여러 소절에 흩어져 있으면 두 뜻일 수 있으므로 그 자리를 열어 볼 후보를 찾는 용도다.
사용: python -I 검토전체25_R13b_greek.py <장 파일 이름(쉼표로 여럿)> [추가 토큰 ...]
"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'C:/math/임시/주차함수_증명/'
GREEK = ('alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa varkappa lambda mu nu xi '
         'rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma '
         'Upsilon Phi Psi Omega').split()
for ch in sys.argv[1].split(','):
    L = io.open(BASE + '장v2/%s.md' % ch, encoding='utf-8').read().split('\n')
    sec = []
    cur = '(머리)'
    for l in L:
        m = re.match(r'#{2,4} (\S+)', l)
        if m:
            cur = m.group(1)
        sec.append(cur)
    toks = ['\\' + g for g in GREEK] + sys.argv[2:]
    print('==', ch)
    for t in toks:
        d = {}
        pat = re.compile(re.escape(t) + (r'(?![A-Za-z])' if t.startswith('\\') else ''))
        for i, l in enumerate(L):
            n = len(pat.findall(l))
            if n:
                d[sec[i]] = d.get(sec[i], 0) + n
        if d:
            print('%-12s' % t, ' '.join('%s:%d' % kv for kv in d.items()))
