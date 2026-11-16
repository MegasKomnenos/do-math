# -*- coding: utf-8 -*-
"""F14: 장부 1.1 변수 글자·몇 1.2 글자의 「쓰이는 장」 대 수식 구간 안 실제 출현(장별 건수와 보기)."""
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명\장v2'
files = [('장1','1'),('장2','2'),('장3','3'),('장4','4'),('장5A','5'),('장5B','5'),('장6','6'),('장7A','7'),('장7B','7'),('장8','8'),('장9','9'),('장10','10'),('장11','11')]
spans = {}
for f, ch in files:
    txt = open(os.path.join(ROOT, f + '.md'), encoding='utf-8').read()
    for ln, line in enumerate(txt.split('\n'), 1):
        for m in re.finditer(r'\$\$(.+?)\$\$|\$(.+?)\$', line):
            spans.setdefault(ch, []).append((f, ln, m.group(1) or m.group(2)))
L = r'(?<![A-Za-z\\])'
R = r'(?![A-Za-z])'
checks = {
 'N': (L + 'N' + R, '1,6,7,8,9,10'),
 'r': (L + 'r' + R, '1,2,4,5,9,11'),
 'q': (L + 'q' + R, '1,2,5,6,7,8,9,10,11'),
 'nu': (r'\\nu' + R, '1,4,6,7,8,9,10,11'),
 'd': (L + 'd' + R, '1,2,5,6,7,8,9,10,11'),
 'y': (L + 'y' + R, '1,2,3,4,5,6,7,8,9,10,11'),
 'Y': (L + 'Y' + R, '1,2,5,6,9'),
 'u': (L + 'u' + R, '2,5,6,7,8,9'),
 'v': (L + 'v' + R, '2,5,6,7,8,9'),
 't': (L + 't' + R, '2,3,5,6,7,8,9,10,11'),
 'm': (L + 'm' + R, '1,2,3,5,6,7,8,9,10,11'),
 'beta': (r'\\beta' + R, '2,5,6'),
 'F': (L + 'F' + R, '2,5,6,9'),
 'G': (L + 'G' + R, '2,3,5,6,8,9,10'),
 'L': (L + 'L' + R, '2,3,6,7,9,10'),
 'tau': (r'\\tau' + R, '2,5,7'),
 'xi': (r'\\xi' + R, '8,9,10,11'),
 'Pi': (r'\\Pi' + R, '2,5,7,10'),
 'Psi': (r'\\Psi' + R, '2,6,8,9,10,11'),
 'Phi': (r'\\Phi' + R, '4,5,7'),
 'vartheta': (r'\\vartheta' + R, '10'),
 'zeta': (r'\\zeta' + R, '1,8'),
 'lambda': (r'\\lambda' + R, '1,3,5,8'),
 'sigma': (r'\\sigma' + R, '2,4,5,7,8,11'),
 'f': (L + 'f' + R, '3,8'),
 'g': (L + 'g' + R, '2,5,6,7,8,9,10'),
 'x': (L + 'x' + R, '1,3,5,6,11'),
 'hatx': (r'\\hat x', '1,3,5,6,11'),
 'ell_ast': (r'\\ell\^\\ast', '1,3,4,5,6'),
 'k_n': (L + 'k_n' + R, '1,4,5,6,7'),
 'e_n': (L + 'e_n' + R, '1,2,4,5,7,11'),
 'w_m': (L + 'w_m' + R, '7,10'),
 'M': (L + 'M' + R, '1,2,3,4,5,6,7,8,9,10'),
 'X': (L + 'X' + R, '3,8'),
 'f_ast?x_ast': (L + r'x_\\ast', '1,3'),
 'E_nk': (L + r'E_\{n,k\}', '1,2,4,5,7'),
 'I_v': (L + r'I_v', '2,9'),
 'K_n': (L + r'K_n\(', '9'),
 'R_j': (L + r'R_[j0-9z]', '2,5,6'),
 'S_i': (L + r'S_[0-9ijLz]', '2,3,5,6,7,8,9,10'),
}
CTRL = re.compile(r'\\(mathcal|mathfrak|mathsf|mathrm|mathbb|mathbf|mathscr|operatorname|tilde|hat|bar|dot|vec|widetilde|underline|overline)\s*\{?\s*$')
def hit(pat, s):
    for m in re.finditer(pat, s):
        if CTRL.search(s[:m.start()]):
            continue
        return True
    return False
for name, (pat, decl) in checks.items():
    decl = set(decl.split(','))
    print('=====', name, '선언', ','.join(sorted(decl, key=int)))
    for ch in ['1','2','3','4','5','6','7','8','9','10','11']:
        hits = [(f, ln, s) for f, ln, s in spans.get(ch, []) if hit(pat, s)]
        flag = '' if (bool(hits) == (ch in decl)) else '  <-- 선언과 다름'
        print(f'  장{ch}: {len(hits)}건{flag}')
        if flag and hits:
            for f, ln, s in hits[:5]:
                print('      ', f, ln, s[:120])
