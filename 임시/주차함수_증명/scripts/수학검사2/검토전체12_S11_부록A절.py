# S11: 부록 A의 「처음 정의된 절」 표본 검사 — 기호 꼴의 첫 등장 장·절을 찾는다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pats = {
 'Pr^{y_0} (A: 2.11)': r'Pr\^\{y_0\}', 'y_0:=k': r'y_0\s*:=\s*k', '얼린 법칙': r'얼린 법칙',
 "KDprime_n (A: 7.7)": r"KD\}\^\\prime_n|KD\}'_n", 'Q^star_2 (A: 7.7)': r'Q\^\\star_2', 'nu_min (A: 10.3)': r'nu_\{\\min\}', 'bar nu (A: 10.6)': r'\\bar\\nu',
 'm_1(k) (A: 9.1)': r'm_1\(k\)', 'P^+_t (A: 9.1)': r'P\^\+_t', 'pi_2( (A: 9.1)': r'\\pi_2\(', 'varrho^lb (A: 9.4)': r'varrho\^\{\\mathrm\{lb\}\}',
 'k^ast (A: 10.6)': r'k\^\\ast', 'mathcal G^y (A: 10.6)': r'mathcal G\^y', 'Bor_le( (A: 6.6)': r'Bor\}_\{?\\le\}?\(',
 'D_k:= (A: 6.4)': r'D_k\s*:=', 'mathfrak c_0(N) (A: 8.3)': r'mathfrak c_0\(N\)', 'Upsilon_k (A: 6.4)': r'Upsilon_k', 'varphi^flat_k (A: 6.4)': r'varphi\^\\flat_k',
 'tilde omega (A: 10.6)': r'tilde\\omega', 'omega_y(d) (A: 10.5)': r'omega_y\(d\)', 'adm_new (A: 10.6)': r'adm\}\}_\{\\mathrm\{new\}\}', 'd^star (A: 10.6)': r'd\^\\star',
 'mathsf f_1 (A: 10.6)': r'mathsf f_1', 'Psi^lb (A: 9.5)': r'Psi\^\{\\mathrm\{lb\}\}', 'merge (A: 9.5)': r'mathrm\{merge\}', 'n_PD (A: 7.5)': r'n_\{\\mathrm\{PD\}\}',
 'cl^+_m (A: 7.5)': r'cl\}\^\+_m', 'inh^lin (A: 7.6)': r'inh\}\^\{\\mathrm\{lin\}\}', 'SRC^+ (A: 7.6)': r'mathsf\{SRC\}\^\+', 'Pi^up_j (A: 7.7)': r'Pi\^\{\\mathrm\{up\}\}_j',
 'mathfrak u_n (A: 7.7)': r'mathfrak u_n', 'Left_n (A: 7.7)': r'mathrm\{Left\}_n', 'Quad_n (A: 7.7)': r'mathrm\{Quad\}_n', 's^low_q (A: 8.1)': r's\^\{\\mathrm\{low\}\}_q',
 'Omega(xi) (A: 8.1)': r'Omega\(\\xi\)', 'dup_m (A: 8.1)': r'mathrm\{dup\}_m', 'Flow_q (A: 8.1)': r'mathrm\{Flow\}_q', 'km_N (A: 8.2)': r'mathrm\{km\}_N', 'Lip (A: 8.2)': r'mathrm\{Lip\}',
 'm_fb (A: 8.4)': r'm_\{\\mathrm\{fb\}\}', 'LB^mono (A: 8.4)': r'LB\}\^\{\\mathrm\{mono\}\}', 'x_t(y) (A: 2.9)': r'x_t\(y\)', 'P_t(k) (A: 2.9)': r'P_t\(k\)', 'theta_t(k) (A: 2.9)': r'theta_t\(k\)',
 'rb_m (A: 2.9)': r'mathrm\{rb\}_m', 'Ren(j) (A: 2.9)': r'mathrm\{Ren\}\(j\)', 'b^(2)_m (A: 2.10)': r'b\^\{\(2\)\}_m', 'nf(n,d) (A: 2.12)': r'mathrm\{nf\}\(n,d\)', 'W_n(gamma) (A: 2.12)': r'W_n\(\\gamma\)',
 'tilt_q (A: 2.11)': r'mathrm\{tilt\}_q', 'H_B (A: 2.11)': r'mathcal H_\{\\mathrm B\}', 's^T_t(y) (A: 2.6)': r's\^\{T\}_t\(y\)|s\^T_t\(y\)', 'Gr(x) (A: 2.7)': r'mathrm\{Gr\}\(x\)',
 'He_j (A: 4.3)': r'mathrm\{He\}_j', 'Bor^tail (A: 4.3)': r'Bor\}\^\{\\mathrm\{tail\}\}', 'mathsf a_0 (A: 4.3)': r'mathsf a_0', 'mathsf g_k (A: 4.3)': r'mathsf g_k', 'mathsf n_k (A: 4.3)': r'mathsf n_k',
 'x_ast (A: 3.2)': r'x_\\ast', 'rq_r (A: 5.2)': r'mathrm\{rq\}_r', 'r_0(n) (A: 5.3)': r'r_0\(n\)', 'A^c_{n,ell} (A: 5.1)': r'A\^\{?c\}?_\{n,\\ell\}', 'mathfrak m(n) (A: 5.2)': r'mathfrak m\(n\)',
 'W^sharp (A: 5.4)': r'mathsf W\^\\sharp', 'q_max (A: 5.5)': r'q_\{\\max\}', 'Lambda_w (A: 5.5)': r'Lambda_\{\\mathrm w\}', 'mathsf w_0 (A: 5.5)': r'mathsf w_0', 'IH (A: 5.5)': r'mathrm\{IH\}',
 'tail_s (A: 5.5)': r'mathrm\{tail\}_s', 'WIN_0 (A: 5.5)': r'mathrm\{WIN\}_0', 'POS_0 (A: 5.5)': r'mathrm\{POS\}_0', 's^F(k,nu) (A: 6.1)': r's\^\{\\mathrm F\}\(k,\\nu\)', 'Bor_> (A: 6.1)': r'Bor\}_\{?>\}?\(',
 'kappa_N (A: 6.2)': r'kappa_N', 'epsilon_N (A: 6.2)': r'epsilon_N', 'varrho_t (A: 6.2)': r'varrho_t', 'mathfrak r_N (A: 6.2)': r'mathfrak r_N', 'mathfrak w_n(t) (A: 6.2)': r'mathfrak w_n\(t\)',
 'mathsf x_k (A: 6.2)': r'mathsf x_k', 'dec_N (A: 6.2)': r'mathrm\{dec\}_N', 'hz_k(N) (A: 6.2)': r'mathrm\{hz\}_k\(N\)', 'varsigma_m(ell) (A: 6.3)': r'varsigma_m\(\\ell\)', 'mathfrak s_d(y) (A: 6.3)': r'mathfrak s_d\(y\)',
 'Pi_j(y) (A: 6.5)': r'Pi_j\(y\)', 'U_k(m) (A: 6.5)': r'mathcal U_k\(m\)', 'V_k(m) (A: 6.5)': r'mathcal V_k\(m\)', 'mathfrak b_m (A: 6.5)': r'mathfrak b_m', 'mathfrak p_m (A: 6.5)': r'mathfrak p_m',
 'X_d(y) (A: 6.5)': r'mathfrak X_d\(y\)', 'mathsf v(k) (A: 6.5)': r'mathsf v\(k\)', 'Bd^V_k (A: 6.5)': r'Bd\}\^\{\\mathrm V\}_k', 'DD(m,y) (A: 6.5)': r'mathrm\{DD\}\(m,y\)', 's_B (A: 6.6)': r'mathsf s_\{\\mathrm B\}',
 'bar A_n(y) (A: 7.1)': r'bar A_n\(y\)', 'mu_n(k) (A: 7.1)': r'mu_n\(k\)', 'T_k(sigma) (A: 7.1)': r'mathcal T_k\(\\sigma\)', 'mathsf t_k (A: 7.1)': r'mathsf t_k', 'Conv (A: 7.1)': r'mathrm\{Conv\}',
 'n^sharp_k (A: 7.2)': r'n\^\\sharp_k', 'n^flat_k (A: 7.2)': r'n\^\\flat_k', 'n^circ_k (A: 7.3)': r'n\^\\circ_k', 'C_k(x) (A: 7.2)': r'C_k\(x\)', 'mathfrak a^circ_n (A: 7.2)': r'mathfrak a\^\\circ_n',
 'mathfrak a^rho_m (A: 7.2)': r'mathfrak a\^\{?\\rho\}?_m', 'mathfrak P_k(n) (A: 7.2)': r'mathfrak P_k\(n\)', 'W_L (A: 7.2)': r'mathsf W_L', 'n_X(k) (A: 7.3)': r'n_\{\\mathrm X\}\(k\)', 'pr_{n,k} (A: 7.3)': r'mathrm\{pr\}_\{n,k\}',
 'J^G_n (A: 7.4)': r'J\^\{\\mathrm G\}_n', 'P^(k)_m(j) (A: 7.4)': r'mathcal P\^\{\(k\)\}_m\(j\)', 'chi_m(j) (A: 7.5)': r'chi_m\(j\)', 'W^(>102) (A: 7.5)': r'mathcal W\^\{\(>102\)\}', 'Q^star (A: 7.5)': r'mathsf Q\^\\star',
 'src_k (A: 7.5)': r'mathrm\{src\}_k', '(star)(n) (A: 7.5)': r'\(\\star\)\(n\)', 'tilde mathfrak a (A: 7.5)': r'tilde\{\\mathfrak a\}', 'b^circ_{n,ell} (A: 5.2)': r'b\^\\circ_\{n,\\ell\}', '(G)_d (A: 5.2)': r'\(\\mathrm G\)_d',
 't_0(y) (A: 5.5)': r't_0\(y\)', 'mathfrak g(theta) (A: 5.5)': r'mathfrak g\(\\theta\)', 'mathfrak z_m(d) (A: 5.5)': r'mathfrak z_m\(d\)', 'Lc(Y,q) (A: 5.5)': r'mathrm\{Lc\}\(Y,q\)', 'varkappa_m (A: 10.1)': r'varkappa_m',
 'mathfrak f_m (A: 10.1)': r'mathfrak f_m', 'mathfrak T_m (A: 10.1)': r'mathfrak T_m', 'm^flat (A: 10.2)': r'm\^\\flat', 'Bd^S (A: 10.2)': r'Bd\}\^\{\\mathrm S\}', 'Stays (A: 10.2)': r'mathrm\{Stays\}', 'FLQ (A: 10.3)': r'mathsf\{FLQ\}',
 's^W_q (A: 10.4)': r's\^\{\\mathrm W\}_q', 'pi^two (A: 10.4)': r'pi\^\{\\mathrm\{two\}\}', 'vartheta_lb (A: 10.4)': r'vartheta_\{\\mathrm\{lb\}\}', 'mathsf r_ast (A: 10.4)': r'mathsf r_\\ast', 'Bd^T (A: 10.4)': r'Bd\}\^\{\\mathrm T\}',
 'DDL(k) (A: 10.4)': r'mathrm\{DDL\}\(k\)', 'PM_y(d) (A: 10.4)': r'mathrm\{PM\}_y\(d\)', 'Stays^adm (A: 10.4)': r'Stays\}\^\{\\mathrm\{adm\}\}', 'G_y(q) (A: 10.5)': r'mathcal G_y\(q\)', 'mathfrak A_j (A: 10.5)': r'mathfrak A_j',
 'mathfrak H_d (A: 10.5)': r'mathfrak H_d', 'mathfrak h_y(q) (A: 10.5)': r'mathfrak h_y\(q\)', 'mathfrak k_d(q) (A: 10.5)': r'mathfrak k_d\(q\)', 's^fr_d (A: 10.5)': r's\}\^\{\\mathrm\{fr\}\}_d', 's^up_d (A: 10.5)': r's\}\^\{\\mathrm\{up\}\}_d',
 'mathsf m_S (A: 10.5)': r'mathsf m_\{\\mathrm S\}', 'DDL_2 (A: 10.5)': r'mathrm\{DDL\}_2', 'inc^pm (A: 10.5)': r'mathrm\{inc\}\^', 'Res_d (A: 10.5)': r'mathrm\{Res\}_d', 'tr_y(q) (A: 10.5)': r'mathrm\{tr\}_y',
 'mathfrak Q(y,xi) (A: 10.6)': r'mathfrak Q\(y,\\xi\)', 's^low_d(y) (A: 10.6)': r's\}\^\{\\mathrm\{low\}\}_d\(y\)', 'Stays^up (A: 10.6)': r'Stays\}\^\{\\mathrm\{up\}\}', 'k_0 (A: 10.6)': r'\$k_0\$|k_0\s*:=|k_0\\in',
 'cal J_1(k) (A: 9.3)': r'mathcal J_1\(k\)', 'mathfrak d_k (A: 9.3)': r'mathfrak d_k', 'mathfrak l_m(t) (A: 9.3)': r'mathfrak l_m\(t\)', 'mathfrak V_m (A: 9.3)': r'mathfrak V_m', 'L_ast(k) (A: 9.3)': r'mathsf L_\\ast\(k\)',
 'FL^(1)_m (A: 9.3)': r'FL\}\^\{\(1\)\}_m', 'land_m (A: 9.3)': r'mathrm\{land\}_m', 'OB_m (A: 9.3)': r'mathrm\{OB\}_m', 'Pcor_m (A: 9.3)': r'mathrm\{Pcor\}', 't^dagger (A: 9.4)': r't\^\\dagger',
 'nu_0(k) (A: 9.4)': r'nu_0\(k\)', 'nu_1(k) (A: 9.4)': r'nu_1\(k\)', 'mathcal F_k(nu) (A: 9.4)': r'mathcal F_k\(\\nu\)', 'mathcal O_n (A: 9.4)': r'mathcal O_n', 'mathcal Y_k(n) (A: 9.4)': r'mathcal Y_k\(n\)', 'FS(n) (A: 9.4)': r'mathsf\{FS\}\(n\)',
 'mathsf h_N (A: 9.4)': r'mathsf h_N', 'flat_k(t) (A: 9.4)': r'mathrm\{flat\}_k\(t\)', 'LP_k(n) (A: 9.4)': r'mathrm\{LP\}_k\(n\)', 'regen_n (A: 9.4)': r'mathrm\{regen\}_n', 'A^diamond,up (A: 9.5)': r'A\^\{\\diamond,\\mathrm\{up\}\}',
 'A^(t)_N (A: 9.2)': r'A\^\{\(t\)\}_N', 'K_n(m) (A: 9.2)': r'K_n\(m\)', 'gamma_m (A: 9.2)': r'\\gamma_m', 'pi_n(t_1,t_2) (A: 9.2)': r'pi_n\(t_1,t_2\)', 'Theta^circ_n (A: 9.2)': r'Theta\^\\circ_n', 'mathcal C_n (A: 9.2)': r'mathcal C_n',
 'mathcal Q_m (A: 9.2)': r'mathcal Q_m', 'mathsf B^+ (A: 9.2)': r'mathsf B\^\+', 'H^ast_+ (A: 9.1)': r'mathsf H\^\\ast_\+',
}
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
for name, pat in pats.items():
    rx = re.compile(pat); found = None
    for ch in files:
        sec = None
        for ln, line in enumerate(open(f'장v2/{ch}.md', encoding='utf-8'), 1):
            m = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)', line)
            if m: sec = m.group(2)
            if rx.search(line): found = (ch, ln, sec); break
        if found: break
    mA = re.search(r'\(A: ([\d.]+)\)', name)
    flag = ''
    if found and mA and not (found[2] or '').startswith(mA.group(1)): flag = '  <-- 부록 A와 다름'
    if not found: flag = '  <-- 없음'
    print(f'{name:32s} 첫 등장: {found}{flag}')
