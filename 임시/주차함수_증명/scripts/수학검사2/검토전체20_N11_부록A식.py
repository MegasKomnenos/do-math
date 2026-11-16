# -*- coding: utf-8 -*-
"""부록 A의 식이 든 행에 대해, 주장된 절에서 그 기호가 처음 나오는 줄의 둘레를 뽑아 식을 눈으로 견주게 한다."""
import re, io, os
ROOT = r"C:\math\임시\주차함수_증명"
OUT = os.path.join(ROOT, r"대조v2\수학검사2\_N11_부록A식_out.txt")
CH = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10"]
SEC = re.compile(r"^### (\d+\.\d+)")
sections = {}
for ch in CH:
    sec = ch + "-머리"
    for i, ln in enumerate(io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n")):
        m = SEC.match(ln)
        if m: sec = m.group(1)
        sections.setdefault(sec, []).append((i + 1, ln))
# (고정 문자열, 절, 둘레 폭)
Q = [
 (r"\theta_t(k)", "2.9"), (r"\pi^{\mathrm{two}}_N", "10.4"), (r"\mathsf u(k)", "6.4"), (r"\Psi^{\mathrm{lb}}", "9.5"),
 (r"\mathrm{DDL}(k)", "10.4"), (r"\mathsf c_\Psi", "8.2"), (r"\mathsf f_1", "10.6"), (r"\bar{\mathfrak d}_k", "9.3"),
 (r"\mathsf v(6667)", "6.5"), (r"\mathfrak c_0(N)", "8.3"), (r"q_{\mathrm{fb}}", "8.4"), (r"m_{\mathrm{fb}}", "8.4"),
 (r"\mathcal W^{(>102)}", "7.5"), (r"n_{\mathrm{PD}}(k)", "7.5"), (r"\mathfrak m(n)", "5.2"), (r"r_0(n)", "5.3"),
 (r"q_{\max}", "5.5"), (r"\mathrm{PM}_y(d)", "10.4"), (r"s^{\mathrm F}(k,\nu)", "6.1"), (r"\mathsf s_{\mathrm B}", "6.6"),
 (r"\Psi^{\mathrm{low}}", "8.2"), (r"\mathsf j_\infty", "8.2"), (r"\Lambda_{\mathrm w}(Y)", "5.5"), (r"\mathfrak z_m(d)", "5.5"),
 (r"\pi_2(t)", "9.1"), (r"\gamma_m", "9.2"), (r"K_n(m)", "9.2"), (r"\Theta_n", "2.10"), (r"\mathrm{KD}'_n", "7.7"), (r"\mathrm{KD}^\prime_n", "7.7"),
 (r"\Pi^{\mathrm{up}}_j", "7.7"), (r"\mathfrak u_n", "7.7"), (r"\varkappa_m", "10.1"), (r"\mathfrak f_m", "10.1"), (r"\omega_m", "10.2"),
 (r"\mathrm{Stays}", "10.2"), (r"\vartheta", "10.3"), (r"\vartheta_0", "10.6"), (r"\vartheta_{\mathrm{lb}}", "10.4"), (r"d^\star", "10.6"),
 (r"\mathsf x_k", "6.2"), (r"\mathrm{dec}_N", "6.2"), (r"\mathrm{hz}_k(N)", "6.2"), (r"\varsigma_m(\ell)", "6.3"), (r"D_k", "6.4"),
 (r"\Upsilon_k", "6.4"), (r"\varphi^\flat_k", "6.4"), (r"\mathrm{Bd}^{\mathrm V}_k", "6.5"), (r"\mathrm{DD}(m,y)", "6.5"),
 (r"\mathfrak R_q", "8.1"), (r"\mathfrak D^{\mathrm{src}}_q", "8.1"), (r"s^{\mathrm{cf}}", "8.2"), (r"\mathrm{km}_N", "8.2"),
 (r"\mathfrak R^{\mathrm{low}}_k", "8.4"), (r"\mathrm{fb}(\lambda)", "8.4"), (r"n^\sharp_k", "7.1"), (r"n^\sharp_k", "7.2"), (r"\mathsf t_k", "7.1"),
 (r"\mathrm{lp}_k", "7.3"), (r"n_{\mathrm X}(k)", "7.3"), (r"\mathcal P^{(k)}_m(j)", "7.4"), (r"\mathrm{cl}^+_m", "7.5"), (r"\mathrm{cl}^-_m", "7.5"),
 (r"\mathcal N_\ell(t)", "2.4"), (r"\pi_n(m)", "2.5"), (r"\mathfrak v_k", "2.5"), (r"\mathrm{Ren}(j)", "2.9"), (r"\mathrm{rb}_m", "2.9"),
 (r"P_t(k)", "2.9"), (r"x_t(y)", "2.9"), (r"\delta_t", "2.10"), (r"\mathrm{nf}(n,d)", "2.12"), (r"W_n(\gamma)", "2.12"), (r"\mathcal P_m(j)", "2.8"),
 (r"\Xi_{n,k}", "2.7"), (r"J_n(z)", "2.7"), (r"\mathrm{Gr}(x)", "2.7"), (r"\mathcal G_{z,i,n}", "2.7"), (r"\mathsf a_j", "4.3"), (r"\mathsf g_k", "4.3"),
 (r"\mathsf n_k", "4.3"), (r"\mathcal I_k", "4.3"), (r"\mathcal D(\beta)", "4.3"), (r"\mathrm{He}_j", "4.3"), (r"A^c_{n,\ell}", "5.1"), (r"\mathfrak a_n", "5.1"),
 (r"\mathrm{rq}_r", "5.2"), (r"\mathrm{rq}:=", "5.4"), (r"\mathrm{Lc}(Y,q)", "5.5"), (r"\mathrm{top}", "5.5"), (r"\mathrm{tail}_s(y)", "5.5"), (r"X_n", "3.1"),
 (r"\mathcal S_{n,k}", "4.2"), (r"\Gamma_d(y;n)", "4.2"), (r"\Gamma^", "4.2"), (r"\mathfrak X_d(y)", "6.5"), (r"\mathfrak b_m", "6.5"), (r"\mathfrak p_m", "6.5"),
 (r"\mathcal U_k(m)", "6.5"), (r"\mathcal V_k(m)", "6.5"), (r"\Pi_j(y)", "6.5"), (r"\psi(y)", "6.5"), (r"\mathfrak s_d(y)", "6.3"), (r"\epsilon_N", "6.2"), (r"\kappa_N", "6.2"),
 (r"\mathfrak r_N", "6.2"), (r"\mathfrak w_n(t)", "6.2"), (r"\varrho^{\mathrm H}", "6.2"), (r"\mathrm{Bor}_>(q)", "6.1"), (r"\mathrm{Bor}_\le", "6.6"),
 (r"\mathfrak a^\rho_m", "7.2"), (r"\mathfrak P_k(n)", "7.2"), (r"C_{n,k}", "7.2"), (r"\rho_k", "7.2"), (r"\mathrm{pr}_{n,k}", "7.3"), (r"\mathrm{pr}^\circ_n", "7.3"),
 (r"J^{\mathrm G}_n(z)", "7.4"), (r"\chi_m(j)", "7.5"), (r"\mathrm{src}_k(m)", "7.5"), (r"\mathrm{inh}_k(n)", "7.5"), (r"\mathrm{inh}^{\mathrm{lin}}_k", "7.6"), (r"w_m", "7.7"),
 (r"\mathrm{Left}_n", "7.7"), (r"\mathrm{Quad}_n", "7.7"), (r"\mathrm{Stem}_n", "7.7"), (r"s^{\mathrm{low}}_q", "8.1"), (r"\Omega(\xi)", "8.1"), (r"\xi_q", "8.1"),
 (r"\mathfrak D_q", "8.1"), (r"\mathfrak E_q", "8.1"), (r"\mathrm{dup}_m", "8.1"), (r"\mathrm{Flow}_q", "8.1"), (r"\tilde s^{\mathrm{env}}", "8.2"), (r"s^{\mathrm{env}}(\xi)", "8.2"),
 (r"\mathfrak B_N", "8.2"), (r"\mathrm{Lip}", "8.2"), (r"q^\circ_{\mathrm{fb}}", "8.4"), (r"\mathrm{LB}^{\mathrm{mono}}", "8.4"), (r"\mathrm{LOW}_k", "8.4"),
 (r"m_1(k)", "9.1"), (r"P^+_t(k)", "9.1"), (r"\mathsf H^\ast_+", "9.1"), (r"A^{(t)}_N", "9.2"), (r"A^\circ_N", "9.2"), (r"A^\diamond_N", "9.2"), (r"\pi_n(t_1,t_2)", "9.2"),
 (r"\Theta^\circ_n", "9.2"), (r"\mathcal C_n", "9.2"), (r"\mathcal Q_m", "9.2"), (r"(\mathrm P\Diamond)", "9.2"), (r"\mathfrak d_k", "9.3"), (r"\mathfrak l_m(t)", "9.3"),
 (r"\mathfrak V_m", "9.3"), (r"\mathsf L_\ast(k)", "9.3"), (r"\mathrm{FL}^{(1)}_m", "9.3"), (r"\mathrm{land}_m", "9.3"), (r"\mathrm{OB}_m", "9.3"), (r"\mathrm{Pcor}_m", "9.3"),
 (r"t^\dagger", "9.4"), (r"P^{\theta\dagger}", "9.4"), (r"P^\theta_t(k)", "9.4"), (r"\nu_0(k)", "9.4"), (r"\nu_1(k)", "9.4"), (r"\varrho^\dagger", "9.4"), (r"\mathcal F_k(\nu)", "9.4"),
 (r"\mathcal O_n", "9.4"), (r"\mathcal Y_k(n)", "9.4"), (r"\mathsf{FS}(n)", "9.4"), (r"\mathsf h_N", "9.4"), (r"\mathrm{flat}_k(t)", "9.4"), (r"\mathrm{LP}_k(n)", "9.4"), (r"\mathrm{regen}_n", "9.4"),
 (r"A^{\diamond,\mathrm{up}}", "9.5"), (r"\mathrm{merge}^{\mathrm{up}}", "9.5"), (r"\mathfrak T_m", "10.1"), (r"m_0", "10.2"), (r"m^\flat", "10.2"), (r"\mathrm{Bd}^{\mathrm S}", "10.2"),
 (r"\nu_{\min}(k)", "10.3"), (r"\bar\nu", "10.6"), (r"\mathsf{FLQ}", "10.3"), (r"s^{\mathrm W}_q(m,y)", "10.4"), (r"\mathsf r_\ast", "10.4"), (r"\mathrm{Bd}^{\mathrm T}(k,\nu)", "10.4"),
 (r"\mathrm{Stays}^{\mathrm{adm}}", "10.4"), (r"y_0", "10.5"), (r"\mathfrak M_y(q)", "10.5"), (r"\mathfrak A_j", "10.5"), (r"\mathfrak H_d", "10.5"), (r"\mathfrak h_y(q)", "10.5"),
 (r"\mathfrak k_d(q)", "10.5"), (r"\mathfrak s^{\mathrm{fr}}_d(y)", "10.5"), (r"\mathfrak s^{\mathrm{up}}_d(y)", "10.5"), (r"\mathsf m_{\mathrm S}", "10.5"), (r"\mathrm{DDL}_2(k)", "10.5"),
 (r"\mathrm{DDL}^\natural(k)", "10.5"), (r"\mathrm{inc}^", "10.5"), (r"\mathrm{Res}_d", "10.5"), (r"\mathrm{tr}_y(q)", "10.5"), (r"k_0", "10.6"), (r"k^\ast", "10.6"), (r"\mathfrak Q(y,\xi)", "10.6"),
 (r"\mathfrak s^{\mathrm{low}}_d(y)", "10.6"), (r"\mathrm{Stays}^{\mathrm{up}}", "10.6"), (r"\omega_y(d)", "10.5"), (r"\tilde\omega(d)", "10.6"), (r"\mathfrak M^y(q)", "10.6"),
 (r"\mathrm{Stays}^{\mathrm{vis}}", "10.4"), (r"\mathrm{Stays}_{\mathrm{PM}}", "10.4"), (r"\mathfrak a^\circ", "7.2"), (r"\mathsf W_L^\flat", "7.2"), (r"\mathsf Q^\star", "7.5"),
 (r"\mathcal Z", "7.5"), (r"(\star)(n)", "7.5"), (r"\mathsf{SRC}^+", "7.6"), (r"\mathcal R_2", "7.7"), (r"\mathsf{LRP}_2", "7.7"), (r"\mathsf Q^\star_2", "7.7"),
 (r"\mathrm{Conv}_{n,k}", "7.1"), (r"\mathcal T_k(\sigma)", "7.1"), (r"\mu_n(k)", "7.1"), (r"\bar A_n(y)", "7.1"), (r"C_k(x)", "7.2"), (r"\mathfrak P_k(\infty)", "7.3"), (r"\mathrm{lpr}_k", "7.3"),
]
o = io.open(OUT, "w", encoding="utf-8")
for tok, sec in Q:
    lines = sections.get(sec, [])
    hit = None
    for i, ln in lines:
        j = ln.find(tok)
        if j >= 0:
            hit = (i, ln[max(0, j - 120): j + 260]); break
    print("\n##", tok, "@", sec, "->", ("없음" if not hit else "행 %d: %s" % hit), file=o)
o.close()
