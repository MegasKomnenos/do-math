# -*- coding: utf-8 -*-
"""K14: 장부 1.2 「뜻」 열의 정의식·상수가 장 파일의 정의와 같은지 표본 대조(검색만; 판단은 손으로)."""
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = r'C:\math\임시\주차함수_증명\장v2'
def norm(s): return re.sub(r'[\s{}]', '', s)
checks = [
 ('장9', r'\mathsf h_N', '3/2-47/(24k)+(1-3/(2k))0.307k/(N+1)'),
 ('장6', r'\mathsf u(k)', '3/0.35 (1.35+1/k)(0.65-1/k)^{-3/2}k^{-1/2}'),
 ('장6', r"\mathsf v^\prime_k", 'max(k+1,4000)'),
 ('장5B', r'q_{\max}', '6Y^{2/3}'),
 ('장5A', r'r_0(n)', '3/4 n^{2/3}'),
 ('장5A', r'\mathfrak m(n)', '170 171 m^{3/2}+9m'),
 ('장8', r'\mathsf c_\Psi', '1.678'),
 ('장5B', r'\mathsf w_0', '0.71216'),
 ('장10', r'\mathrm{DDL}(k)', '50.62'),
 ('장10', r'\pi^{\mathrm{two}}_N', 'N-1 k^{k-1}(nu-1)^{nu-2}/N^{N-2}'),
 ('장10', r'\vartheta_0', '2e^{-0.48}-1'),
 ('장8', r'm_{\mathrm{fb}}', '5k/4'),
 ('장8', r'q_{\mathrm{fb}}', '3(k-1)/4-q_max-3)/8'),
 ('장9', r'\mathsf L_\ast(6668)', '1.206'),
 ('장6', r'\mathsf v(6667)', '0.7654'),
 ('장7B', r'\mathcal R_2', '6668 2k+103 20001 3k-1'),
 ('장7B', r'\mathcal W^{(>102)}', '2001 2k+103 20001 2k^{3/2}'),
 ('장7B', r'n_{\mathrm{PD}}(k)', '(k+1)^{4/3} +k+1'),
 ('장7A', r'n_{\mathrm X}(k)', 'k^{4/3}'),
 ('장7A', r'n^\circ_k', '2k^{3/2}'),
 ('장10', r'\nu_{\min}(k)', '103 20001-2k'),
 ('장10', r'd^\star', '0.6y'),
 ('장10', r'\mathsf m_{\mathrm S}', '1.15 1.2'),
 ('장10', r'\mathsf f_1', '4/(3 sqrt(2pi)) 0.53192'),
 ('장9', r'\Psi^{\mathrm{low}}(d)', '0.3989 1.678'),
 ('장6', r'\mathsf s_{\mathrm B}', 'e/sqrt(2pi)'),
 ('장6', r'\kappa_N', '0.307'),
 ('장7A', r'n^\sharp_k', 'k+(k+1)t_k'),
 ('장7A', r'\mathfrak P_k(n)', 'E[kH_k]/n'),
 ('장8', r'\mathfrak R_q', 'k c_{k+q}(k)'),
 ('장8', r'\mathfrak D^{\mathrm{src}}_q', 'q/(k+q) Psi(q) + k/(k+q) sum Bor(m)(1-s^low_{q-m})'),
 ('장8', r'\mathrm{fb}(\theta)', 'sum_{i<8}'),
 ('장8', r'\mathfrak B^{\mathrm{low}}', ''),
 ('장9', r'\mathfrak d_k', 'max_{k<=N<=2k-1} cl^-_N'),
 ('장9', r'\gamma_m', 'k(m+1)/(m+1-k)'),
 ('장9', r'\bar{\mathfrak d}_k', '6.62/sqrt k'),
 ('장10', r'\varkappa_m', '2 1+(n-m)/k'),
 ('장6', r'\Upsilon_k', 'k(k-1)b_{2k,k-1}/((2k+1)p_{2k})'),
 ('장6', r'\hat\Upsilon_k', '(k-1) u(k)/(2k+1)'),
 ('장6', r's^{\mathrm F}(k,\nu)', 'min(1,3(k+1)(nu-1)^{-3/2})'),
 ('장7B', r'\mathrm{cl}^-_m', 'c_m(k-1)/s_m(k)'),
 ('장7B', r'\mathfrak u_n', 'w_{n-k}s_{n-k}(k+1)'),
 ('장2', r'\mathrm{nf}(n,d)', 'e^d n!/(n-d)! (n-d)^{n-d-2}/n^{n-2}'),
 ('장2', r'\mathfrak v_k(Z,H)', '(1+1/k)^Z+(1-1/k)^{Z+H}-2'),
 ('장4', r'\mathsf n_k', 'n!/p_n e^{n+1}/(2pi k^{3/2})'),
 ('장4', r'\mathsf g_k', '2-kM_2/M_0'),
 ('장10', r'\mathrm{PM}_y(d)', '16.54(y+1+(d-1)/3)(d-1)^{-5/2}'),
 ('장10', r'\mathfrak f_m', 'varkappa_m k d_{m,k}/p_m+(2-1{m>N})c^{(2)}_m'),
 ('장10', r'\mathrm{Stays}^{\mathrm{adm}}(k,\nu)', '4-3s^F-Bd^T-DDL'),
 ('장8', r'\mathsf j_\infty', '4/3 (2pi)^{-1/2} xi^{3/2}'),
 ('장8', r's^{\mathrm{cf}}', '2.1 2 6600'),
 ('장5B', r'\Lambda_{\mathrm w}(Y)', 'sum_{r=1}^{q_max} Y/(Y+r+1) Lc(Y,r)'),
 ('장5B', r'\mathrm{top}_\pi', '(y-1)pi_n(y)'),
 ('장5B', r'\mathfrak z_m(d)', 'e^{(d-1)/w}/(w+1)+3d/(2(w+1)(m+1))'),
 ('장9', r'\mathcal O_n', 'd_{n,k}-sum binom delta_t A_{n-t,k-1}'),
 ('장9', r'\mathfrak l_m(t)', 'pi_m(t)/pi_m(k) k/t'),
 ('장9', r'K_n(m)', 'binom n{m+1}p_{n-1-m}'),
 ('장7A', r'\mathsf t_k', ''),
 ('장8', r'\Omega', '[0,6] decreasing'),
]
texts = {ch: open(os.path.join(B, ch + '.md'), encoding='utf-8').read().split('\n') for ch in set(c for c, _, _ in checks)}
for ch, g, note in checks:
    gn = norm(g)
    hits = [(i, ln) for i, ln in enumerate(texts[ch], 1) if gn in norm(ln) and (':=' in ln or '정의' in ln or '라 하' in ln or '로 둔' in ln or '두자' in ln or '두면' in ln or '=' in ln)]
    print('==', ch, g, '| 장부:', note)
    for i, ln in hits[:2]:
        pos = norm(ln).find(gn)
        # print a window around glyph in the raw line
        j = ln.find(g.split('(')[0].split('_')[0][:6])
        print('   ', i, ln[max(0, j - 40):j + 230].replace('\n', ' '))
