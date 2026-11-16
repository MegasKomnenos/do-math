# -*- coding: utf-8 -*-
"""M11: 부록 A의 몇 정의식을 본문의 정의 자리와 대조하기 위해, 기호별 첫 정의 문장(':=' 또는 '라 하' 등이 있는 줄)을 뽑는다."""
import re, os
ROOT = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding="utf-8").read()
CH = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10"]
pats = {
 "s^F": r"s\^\{\\mathrm F\}", "n_X": r"n_\{\\mathrm X\}", "n_PD": r"n_\{\\mathrm\{PD\}\}", "m_fb": r"m_\{\\mathrm\{fb\}\}", "q_fb": r"q_\{\\mathrm\{fb\}\}",
 "Psi^lb": r"\\Psi\^\{\\mathrm\{lb\}\}", "u(k)": r"\\mathsf u\(k\)", "Upsilon_k": r"\\Upsilon_k", "d_k frak": r"\\mathfrak d_k", "l_m(t)": r"\\mathfrak l_m",
 "Pcor": r"\\mathrm\{Pcor\}", "gamma_m": r"\\gamma_m", "K_n(m)": r"K_n\(m\)", "pi_2": r"\\pi_2\(t\)", "P^+_t": r"P\^\+_t", "m_1(k)": r"m_1\(k\)",
 "z_m(d)": r"\\mathfrak z_m", "t_0(y)": r"t_0\(y\)", "Lambda_w": r"\\Lambda_\{\\mathrm w\}", "Lc": r"\\mathrm\{Lc\}", "q_max": r"q_\{\\max\}",
 "m(n)": r"\\mathfrak m\(n\)", "r_0(n)": r"r_0\(n\)", "rq": r"\\mathrm\{rq\}", "varkappa": r"\\varkappa_m", "f_m frak": r"\\mathfrak f_m",
 "omega_m": r"\\omega_m", "vartheta_lb": r"\\vartheta_\{\\mathrm\{lb\}\}", "r_*": r"\\mathsf r_\\ast", "d^star": r"d\^\\star", "h_y": r"\\mathfrak h_y",
 "k_d": r"\\mathfrak k_d", "inc": r"\\mathrm\{inc\}", "s^up": r"\\mathfrak s\^\{\\mathrm\{up\}\}", "m_S": r"\\mathsf m_\{\\mathrm S\}", "f_1": r"\\mathsf f_1",
 "Q(y,xi)": r"\\mathfrak Q\(y", "Bor_le": r"\\mathrm\{Bor\}_\{?\\le", "Ren": r"\\mathrm\{Ren\}\(j\)", "nf": r"\\mathrm\{nf\}", "W_n(gamma)": r"W_n\(\\gamma\)",
 "theta_t(k)": r"\\theta_t\(k\)", "Bd^V": r"\\mathrm\{Bd\}\^\{\\mathrm V\}", "cl": r"\\mathrm\{cl\}\^", "Pi^up": r"\\Pi\^\{\\mathrm\{up\}\}", "u_n frak": r"\\mathfrak u_n",
 "DDL": r"\\mathrm\{DDL\}\(k\)", "PM_y": r"\\mathrm\{PM\}_y", "nu_min": r"\\nu_\{\\min\}", "pi^two": r"\\pi\^\{\\mathrm\{two\}\}", "Stays adm": r"\\mathrm\{Stays\}\^\{\\mathrm\{adm\}\}",
 "varsigma_m": r"\\varsigma_m\(\\ell\)", "DD(m,y)": r"\\mathrm\{DD\}\(m,y\)", "x_t(y)": r"x_t\(y\)", "P_t(k)": r"P_t\(k\)", "Pi(sasl)": r"\\Pi:=|\\Pi=\\prod", "Psi(q)": r"\\Psi\(q\)",
 "c_Psi": r"\\mathsf c_\\Psi", "j_inf": r"\\mathsf j_\\infty", "km_N": r"\\mathrm\{km\}_N", "c_0 frak": r"\\mathfrak c_0", "fb(lambda)": r"\\mathrm\{fb\}\(\\lambda\)",
 "R^low": r"\\mathfrak R\^\{\\mathrm\{low\}\}_k", "tail_s": r"\\mathrm\{tail\}_s", "top": r"\\mathrm\{top\}", "WIN_0": r"\\mathrm\{WIN\}_0", "POS_0": r"\\mathrm\{POS\}_0",
 "Xi_{n,k}": r"\\Xi_\{n,k\}", "J_n(z)": r"J_n\(z\)", "Gr(x)": r"\\mathrm\{Gr\}\(x\)", "e_n": r"e_n:=|e_n=\\mathcal K", "v_k frak": r"\\mathfrak v_k\(", "Bor^tail": r"\\mathrm\{Bor\}\^\{\\mathrm\{tail\}\}",
 "g_k sf": r"\\mathsf g_k", "n_k sf": r"\\mathsf n_k", "a_j sf": r"\\mathsf a_j", "M_r": r"\\mathcal M_r", "A_{k,n}": r"\\mathcal A_\{k,n\}", "I_k": r"\\mathcal I_k:=|\\mathcal I_k=",
 "Gamma_d": r"\\Gamma_d\(", "S_{n,k}": r"\\mathcal S_\{n,k\}", "A^c": r"A\^c_\{n,\\ell\}", "a_n frak": r"\\mathfrak a_n", "b^circ": r"b\^\\circ_\{n,\\ell\}", "G_d": r"\(\\mathrm G\)_d",
 "x_hat": r"\\hat x", "zeta coord": r"\\zeta:=", "lambda": r"\\lambda:=", "k_n": r"k_n:=", "hz": r"\\mathrm\{hz\}_k", "dec": r"\\mathrm\{dec\}_N", "r_N frak": r"\\mathfrak r_N", "x_k sf": r"\\mathsf x_k",
 "varrho_t": r"\\varrho_t", "w_n frak": r"\\mathfrak w_n\(t\)", "kappa_N": r"\\kappa_N", "epsilon_N": r"\\epsilon_N", "s_d frak": r"\\mathfrak s_d\(y\)", "D_k": r"D_k:=|D_k=", "varphi^flat": r"\\varphi\^\\flat_k",
 "Pi_j(y)": r"\\Pi_j\(y\)", "psi(y)": r"\\psi\(y\)", "U_k(m)": r"\\mathcal U_k\(m\)", "V_k(m)": r"\\mathcal V_k\(m\)", "b_m frak": r"\\mathfrak b_m", "p_m frak": r"\\mathfrak p_m", "X_d frak": r"\\mathfrak X_d",
 "v(k)": r"\\mathsf v\(k\)", "s_B": r"\\mathsf s_\{\\mathrm B\}", "bar A_n": r"\\bar A_n\(y\)", "mu_n(k)": r"\\mu_n\(k\)", "T_k(sigma)": r"\\mathcal T_k\(\\sigma\)", "t_k sf": r"\\mathsf t_k",
 "n^sharp": r"n\^\\sharp_k", "n^flat": r"n\^\\flat_k", "n^circ": r"n\^\\circ_k", "C_k(x)": r"C_k\(x\)", "rho_k": r"\\rho_k", "a^circ": r"\\mathfrak a\^\\circ_n", "a^rho": r"\\mathfrak a\^\{?\\rho\}?_m", "P_k(n) frak": r"\\mathfrak P_k\(n\)",
 "pr": r"\\mathrm\{pr\}_\{n,k\}", "J^G": r"J\^\{\\mathrm G\}_n", "P^(k)_m": r"\\mathcal P\^\{\(k\)\}_m", "chi_m": r"\\chi_m\(j\)", "W^(>102)": r"\\mathcal W\^\{\(>102\)\}", "Z cal": r"\\mathcal Z", "src": r"\\mathrm\{src\}_k",
 "inh": r"\\mathrm\{inh\}_k", "star(n)": r"\(\\star\)\(n\)", "w_m": r"w_m:=|w_m=\\binom", "R_2": r"\\mathcal R_2", "Left_n": r"\\mathrm\{Left\}_n", "Quad": r"\\mathrm\{Quad\}_n", "s^low": r"s\^\{\\mathrm\{low\}\}_q",
 "Omega(xi)": r"\\Omega\(\\xi\)", "xi:=": r"\\xi:=|\\xi_q:=", "D^src": r"\\mathfrak D\^\{\\mathrm\{src\}\}_q", "D_q": r"\\mathfrak D_q", "E_q": r"\\mathfrak E_q", "R_q": r"\\mathfrak R_q", "dup": r"\\mathrm\{dup\}_m", "Flow": r"\\mathrm\{Flow\}_q",
 "s^env": r"s\^\{\\mathrm\{env\}\}\(\\xi\)", "s^cf": r"s\^\{\\mathrm\{cf\}\}", "Psi^low": r"\\Psi\^\{\\mathrm\{low\}\}", "B_N frak": r"\\mathfrak B_N", "Lip": r"\\mathrm\{Lip\}", "LB^mono": r"\\mathrm\{LB\}\^\{\\mathrm\{mono\}\}",
 "A^(t)_N": r"A\^\{\(t\)\}_N", "Theta^circ": r"\\Theta\^\\circ_n", "C_n cal": r"\\mathcal C_n", "Q_m cal": r"\\mathcal Q_m", "J_1": r"\\mathcal J_1\(k\)", "L_*": r"\\mathsf L_\\ast", "FL^(1)": r"\\mathrm\{FL\}\^\{\(1\)\}_m", "land": r"\\mathrm\{land\}_m", "OB": r"\\mathrm\{OB\}_m",
 "V_m frak": r"\\mathfrak V_m", "t^dagger": r"t\^\\dagger", "P^theta": r"P\^\{?\\theta\}?_t", "nu_0(k)": r"\\nu_0\(k\)", "nu_1(k)": r"\\nu_1\(k\)", "varrho^dagger": r"\\varrho\^\\dagger", "F_k(nu)": r"\\mathcal F_k\(\\nu\)", "O_n cal": r"\\mathcal O_n", "Y_k(n)": r"\\mathcal Y_k\(n\)",
 "FS(n)": r"\\mathsf\{FS\}\(n\)", "h_N sf": r"\\mathsf h_N", "flat_k": r"\\mathrm\{flat\}_k", "LP_k": r"\\mathrm\{LP\}_k", "regen": r"\\mathrm\{regen\}_n", "A^diamond,up": r"A\^\{\\diamond,\\mathrm\{up\}\}", "merge": r"\\mathrm\{merge\}",
 "T_m frak": r"\\mathfrak T_m", "m_0": r"m_0", "m^flat": r"m\^\\flat", "Bd^S": r"\\mathrm\{Bd\}\^\{\\mathrm S\}", "Stays": r"\\mathrm\{Stays\}", "bar nu": r"\\bar\\nu", "vartheta": r"\\vartheta:=|\\vartheta=2", "vartheta_0": r"\\vartheta_0", "s^W_q": r"s\^\{\\mathrm W\}_q",
 "Bd^T": r"\\mathrm\{Bd\}\^\{\\mathrm T\}", "y_0": r"y_0:=|y_0=k", "G_y(q)": r"\\mathcal G_y\(q\)", "A_j frak": r"\\mathfrak A_j", "H_d frak": r"\\mathfrak H_d", "s^fr": r"\\mathfrak s\^\{\\mathrm\{fr\}\}", "DDL_2": r"\\mathrm\{DDL\}_2", "Res_d": r"\\mathrm\{Res\}_d", "tr_y": r"\\mathrm\{tr\}_y",
 "k_0": r"k_0", "k^ast": r"k\^\\ast", "s^low_d": r"\\mathfrak s\^\{\\mathrm\{low\}\}_d", "Stays^up": r"\\mathrm\{Stays\}\^\{\\mathrm\{up\}\}",
}
for name, pat in pats.items():
    rx = re.compile(pat)
    found = None
    for c in CH:
        sec = ""
        for i, ln in enumerate(rd(os.path.join(ROOT, c + ".md")).splitlines(), 1):
            ms = re.match(r"^(#{2,4}) ([\d.]+[A-Z]?)\s", ln)
            if ms: sec = ms.group(2)
            m = rx.search(ln)
            if m:
                s = max(0, m.start() - 70); e = min(len(ln), m.end() + 170)
                found = (c, i, sec, ln[s:e]); break
        if found: break
    print(f"### {name}: ", f"{found[0]}:{found[1]} [{found[2]}] {found[3]}" if found else "없음")
