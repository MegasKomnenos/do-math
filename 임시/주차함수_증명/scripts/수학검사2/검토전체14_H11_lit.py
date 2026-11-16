# -*- coding: utf-8 -*-
"""H11: 11.4 문헌 표 대조. 장 파일에서 저자명·문헌 표지(Theorem/Corollary/§ 등)가 나오는 자리를
진술(머리 라벨)·절 단위로 모은다."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
authors = ['Konheim','Weiss','Foata','Riordan','Pollak','Celano','Aguilar','Stanley','Knuth','Flajolet','Sedgewick','Tanner','Robbins','Petersson','Janson','Ibragimov','Ahlfors','Graham','Patashnik','Fortuin','Kasteleyn','Ginibre','FKG','Jensen','Wallis','Corless','Gonnet','Lambert','Grimmett','Harris','Comtet','Faà','Apostol','Titchmarsh','Heath-Brown','Euler','Maclaurin','Cayley','Lagrange','Cauchy','Stirling','Hermite','Dawson','Borel','Bonferroni','Hausdorff','Palm','Riccati','Abel','Neumann','Laurent','Taylor','Simpson','Newton','Bernstein','Hölder','Chebyshev','Markov','Poisson','Gauss','Laplace','Fourier','Lipschitz','Riemann','Mellin','Fekete','Cox','Bernoulli','Kolmogorov','Doob','Pólya','Hardy','Littlewood','Karamata','Tauber','Fatou','Lebesgue','Fubini','Dini','Weierstrass','Rouché','Rouche','Hurwitz','Vandermonde','Minkowski','Young','Schwarz','Cantelli','Slutsky','Scheffé','Wald','Doeblin','Kemperman','Spitzer','Hoeffding','Bennett','Azuma','Chernoff','Stein','Berry','Esseen','Darboux','Hadamard','Pringsheim','Perron','Frobenius','Tchebychev','Bürmann','Jacobi','Legendre','Gamma','Beta','Theorem','Corollary','Lemma','Proposition','Conjecture','Exercise','연습문제','Chapter','arXiv','Press','Wiley','Springer','Univ','교과서','표준']
pat = re.compile('|'.join(re.escape(a) for a in authors))
for f in sorted(glob.glob(os.path.join(root, '장*.md'))):
    b = os.path.basename(f)
    cur_sec = None; cur_stmt = None; in_proof = False
    hits = {}
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^###\s+(\d+\.\d+(?:\.\d+)?)', line)
        if m: cur_sec = m.group(1); cur_stmt = None
        m2 = re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{([^}]+)\}\}', line)
        if m2: cur_stmt = f'{m2.group(1)} {{{{{m2.group(2)}}}}}'
        if re.match(r'^\*\*증명', line) or line.startswith('*증명'): pass
        found = sorted(set(pat.findall(line)))
        found = [x for x in found if x not in ('Theorem','Corollary','Lemma','Proposition','Chapter','표준') or True]
        if found:
            key = cur_stmt or f'절 {cur_sec}'
            hits.setdefault(key, []).append((ln, found, line.strip()[:0]))
    print('=====', b)
    for k, v in hits.items():
        names = sorted({n for _, fs, _ in v for n in fs})
        print(f'  {k}: ' + ', '.join(names) + f'   (행 {", ".join(str(x[0]) for x in v[:6])})')
