# -*- coding: utf-8 -*-
"""F11: 부록 A의 식·상수 몇 개가 장 파일의 정의와 맞는지 자리를 찾아 보여 준다."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pats = [(r'3(k+1)', '장v2/장6.md'), (r'0.7654', '장v2/장6.md'), (r'50.62', '장v2/장10.md'), (r'0.35}', '장v2/장6.md'), (r'0.307', '장v2/장6.md'),
 (r'm^{3/2}+9m', '장v2/장5A.md'), (r'6Y^{2/3}', '장v2/장5B.md'), (r'16.54', '장v2/장10.md'), (r'1.15', '장v2/장10.md'), (r'6.62', '장v2/장9.md'),
 (r'47}{24k}', '장v2/장9.md'), (r'25000', '장v2/장5B.md'), (r'e^{-0.48}', '장v2/장10.md'), (r'0.6y', '장v2/장10.md'), (r'5k/4', '장v2/장8.md'),
 (r'q_{\mathrm{fb}}', '장v2/장8.md'), (r'\mathfrak c_0(N)', '장v2/장8.md'), (r'\Theta_n', '장v2/장2.md'), (r'\mathrm{nf}(n,d)', '장v2/장2.md'),
 (r'0.70836', '장v2/장10.md'), (r'2.528571', '장v2/장10.md'), (r'\mathrm{Bd}^{\mathrm V}_k', '장v2/장6.md'), (r'\hat\Upsilon_k', '장v2/장6.md'),
 (r'\pi_2(t)', '장v2/장9.md'), (r'\gamma_m', '장v2/장9.md'), (r'\varkappa_m', '장v2/장10.md'), (r'\vartheta_{\mathrm{lb}}', '장v2/장10.md'),
 (r'\Psi^{\mathrm{low}}', '장v2/장8.md'), (r'\mathfrak m(n)', '장v2/장5A.md'), (r'\mathcal R_2', '장v2/장7B.md'), (r'\mathsf Q^\star_2', '장v2/장7B.md'),
 (r'\mathrm{fb}(\lambda)', '장v2/장8.md'), (r'm_{\mathrm{fb}}', '장v2/장8.md'), (r'\bar{\mathfrak d}_k', '장v2/장9.md'), (r'\mathsf v(k)', '장v2/장6.md'),
 (r'\mathsf u(k)', '장v2/장6.md'), (r's^{\mathrm F}(k,\nu)', '장v2/장6.md'), (r'\mathrm{PM}_y(d)', '장v2/장10.md'), (r'\mathrm{DDL}(k)', '장v2/장10.md'),
 (r'\mathsf m_{\mathrm S}', '장v2/장10.md'), (r'd^\star', '장v2/장10.md'), (r'\mathsf h_N', '장v2/장9.md'), (r'K_n(m)', '장v2/장9.md'),
 (r'\mathrm{Stays}^{\mathrm{adm}}', '장v2/장10.md'), (r'\kappa_N', '장v2/장6.md'), (r'\Upsilon_k', '장v2/장6.md'), (r'\mathfrak z_m(d)', '장v2/장5B.md'),
 (r'\mathrm{Lc}(Y,q)', '장v2/장5B.md'), (r'\Lambda_{\mathrm w}(Y)', '장v2/장5B.md'), (r'\mathsf w_0', '장v2/장5B.md'), (r'r_0(n)', '장v2/장5A.md'),
 (r'\mathrm{rq}', '장v2/장5A.md'), (r'\mathsf t_k', '장v2/장7A.md'), (r'n_{\mathrm{PD}}(k)', '장v2/장7B.md'), (r'\Pi^{\mathrm{up}}_j', '장v2/장7B.md'),
 (r'\mathfrak u_n', '장v2/장7B.md'), (r'\mathcal W^{(>102)}', '장v2/장7B.md'), (r'\pi^{\mathrm{two}}_N', '장v2/장10.md'), (r'\mathsf f_1', '장v2/장10.md'),
 (r'\mathrm{km}_N', '장v2/장8.md'), (r'\mathsf c_\Psi', '장v2/장8.md'), (r'\mathsf j_\infty', '장v2/장8.md'), (r'\mathrm{Bd}^{\mathrm T}', '장v2/장10.md'),
 (r'\mathfrak B^{\mathrm{low}}', '장v2/장8.md'), (r'\mathrm{Lip}', '장v2/장8.md'), (r'\mathfrak d_k', '장v2/장9.md'), (r'\mathsf L_\ast', '장v2/장9.md'),
 (r'\nu_0(k)', '장v2/장9.md'), (r'\nu_1(k)', '장v2/장9.md'), (r'\Psi^{\mathrm{lb}}', '장v2/장9.md'), (r'm_1(k)', '장v2/장9.md'), (r'A^\diamond_N', '장v2/장9.md'),
 (r'\mathrm{DDL}_2', '장v2/장10.md'), (r'\mathrm{DDL}^\natural', '장v2/장10.md'), (r'\nu_{\min}', '장v2/장10.md'), (r'\mathsf r_\ast', '장v2/장10.md')]
for p, f in pats:
    L = open(f, encoding='utf-8').read().split('\n')
    hits = [(i, l) for i, l in enumerate(L, 1) if p in l]
    defs = [(i, l) for i, l in hits if (p + ':=') in l or (p + '=') in l or ('라 하' in l) or ('로 두' in l) or ('정의' in l)]
    pick = defs[:2] if defs else hits[:1]
    print(f'### {p} in {f}: {len(hits)} hits')
    for i, l in pick:
        j = l.find(p); print(f'   {i}: …{l[max(0, j-220):j+300]}…')
