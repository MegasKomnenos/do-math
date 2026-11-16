# -*- coding: utf-8 -*-
"""H14: 장부 1.2의 기호·상수 문자열을 장 파일에서 글자 그대로 찾아 첫 두 자리(절·파일:행·발췌)를 적는다."""
import io, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "장v2")
CHAPTER_RE = re.compile(r"^## (\d+)\."); SEC_RE = re.compile(r"^### (\d+\.\d+)")
def chapter_files(prefix):
    out=[]
    for i in range(1,12):
        whole=f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base,whole)): out.append(whole); continue
        out.extend(sorted(n for n in os.listdir(base) if re.fullmatch(re.escape(prefix)+str(i)+r"[A-Z]\.md",n)))
    return out
body=[]; sec="0.0"
for name in chapter_files("장"):
    for ln_no, ln in enumerate(io.open(os.path.join(base,name),encoding="utf-8").read().split("\n"),1):
        m=CHAPTER_RE.match(ln)
        if m: sec=f"{m.group(1)}.0"
        s=SEC_RE.match(ln)
        if s: sec=s.group(1)
        body.append((sec,name,ln_no,ln))
BS=chr(92)
targets = [x.replace("@",BS) for x in [
 "@mathsf j_@infty", "@mathsf r_@ast", "@mathfrak a^@circ", "@varphi^@flat", "@Psi^{@mathrm{low}}", "@mathsf s_{@mathrm B}",
 "@mathsf c_@Psi", "@mathsf m_{@mathrm S}", "@mathsf h_N", "n_{@mathrm X}", "n^@sharp_k", "s^{@mathrm F}", "q_{@max}",
 "q_{@mathrm{fb}}", "m_{@mathrm{fb}}", "@mathrm{Bor}_@le", "@mathrm{Bor}_>", "@Pi^{@mathrm{up}}", "@mathsf{SRC}", "s^T_t",
 "M^T_t", "P^@theta_t", "@beta_i", "@Gamma^@pm", "@mathfrak a^@rho", "@mathsf X'", "@mathsf X^@prime", "@mathrm{inc}^",
 "@Pr^T_t", "@mathbb E^T_t", "@mathfrak s^{@mathrm{up}}", "@mathsf f_1", "@mathsf v'_k", "@mathsf v^@prime_k", "@mathsf L_@ast",
 "n^@flat_k", "n^@circ_k", "@vartheta_{@mathrm{lb}}", "d^@star", "y_0", "@mathfrak h_y", "@mathrm{tr}_y", "@mathrm{Res}_d",
 "@mathfrak s^{@mathrm{fr}}", "@mathcal G_y", "@mathfrak A_j", "@mathfrak k_d", "k_0", "k^@ast", "@mathfrak s^{@mathrm{low}}",
 "@mathfrak Q(y", "@pi^{@mathrm{two}}", "@varkappa_m", "@mathfrak f_m", "@mathfrak T_m", "m_0", "@mathrm{Stays}", "@omega_m",
 "@nu_{@min}", "@bar@nu", "@mathfrak H_d", "s^{@mathrm W}_q", "@mathrm{Bd}^{@mathrm S}", "@mathrm{Bd}^{@mathrm T}", "@mathrm{Bd}^{@mathrm V}",
 "WIN}^{@mathrm V}", "WIN^{@mathrm V}", "@mathrm{WIN}", "@hat@Upsilon_k", "r_0(n)", "s^{@mathrm{cf}}", "@tilde s^{@mathrm{env}}", "s^{@mathrm{env}}",
 "@Omega(@xi)", "@Omega_q", "@mathfrak R_q", "@mathfrak D_q", "@mathfrak E_q", "s^{@mathrm{low}}_q", "@mathrm{Flow}_q", "@mathfrak D^{@mathrm{src}}",
 "@mathrm{km}_N", "@mathfrak B_N", "@mathfrak c_0", "@mathrm{LB}^", "@mathrm{LOW}_k", "@mathfrak R^{@mathrm{low}}_k", "@mathrm{fb}(", "@mathrm{dup}_m",
 "@mathrm{Lip}", "@zeta(", "@mathsf a_", "@mathsf n_k", "@mathsf n_@infty", "@mathsf g_k", "@mathsf b_D", "@mathsf b_J", "@mathrm{He}_", "@mathcal I_k",
 "@mathrm{Bor}^{@mathrm{tail}}", "@mathcal M_r", "@mathcal A_{k,n}", "@Phi^{@mathrm{aux}}", "@mathcal D(@beta)", "@Gamma_d(", "@mathcal S_{n,k}", "@mathsf S_R",
 "@mathsf{LH}", "@mathsf P_C", "@mathsf Q_L", "@mathsf Q(n,", "@mathcal K_{n,k}", "@Xi_{n,k}", "@bar A_n(y)", "@mathcal P_m(j)", "Q_@ell(x)", "Q_{k-1}",
 "@mathrm{tilt}_q", "@Pr^y(q", "@mathcal H_{@mathrm B}", "R_j", "@mathrm{nf}(n", "W_n(@gamma)", "@mathrm{Ren}(", "@Psi(q)", "@theta_t(k)", "P_t(k)", "P^+_t(k)",
 "@mathcal N_@ell(t)", "T_@ell(x)", "@mathcal B_@ell", "b^T_{t,", "@delta_t", "x_t(y)", "x_t(k)", "s^T_t(y)", "@pi^0_n(y)", "@pi_n(m)", "@mathrm{Bor}^{*j}",
 "@mathfrak v_k", "Z_k(@sigma)", "H_k(@sigma)", "S_1>S_2", "@Pi_j(y)", "@psi(y)", "@mathfrak X_d", "@mathfrak X^0_d", "@mathrm{DD}(m,y)", "@mathrm{DD}_m",
 "@varsigma_m(@ell)", "@mathfrak s_d(y)", "@mathrm{hz}_k(N)", "@mathfrak r_N", "@mathrm{dec}_N", "@kappa_N", "@varrho_t", "@varrho^{@mathrm H}", "@mathfrak w_n(t)",
 "D_k:=", "@mathcal U_k(m)", "@mathcal V_k(m)", "@mathfrak b_m", "@mathfrak p_m", "@mathsf v(k)", "@mathsf x_k", "@mathsf{UL}", "@mathsf V^@ast",
 "@mathcal P^{(k)}_m", "@mu_n(k)", "@mathcal T_k(@sigma)", "@mathcal T_{n,k}", "@mathrm{Conv}", "@mathrm{Kink}", "@mathsf W_L", "@mathsf W_L^@flat", "@tilde n_k", "@mathsf t_k",
 "@mathfrak P_k(n)", "@mathfrak P_k(@infty)", "@rho_k", "C_k(x)", "C_{n,k}", "@mathrm{pr}_{n,k}", "@mathrm{pr}^@circ", "@mathfrak a^@rho_", "J^{@mathrm G}_n", "@mathrm{src}_k(",
 "@chi_m(j)", "@mathrm{inh}_k(", "@mathrm{inh}^{@mathrm{lin}}", "(@star)(n)", "@mathsf Q^@star_2", "@mathsf Q^@star", "@mathcal Z", "w_m", "@mathrm{Left}_n", "@mathfrak u_n",
 "@mathrm{Quad}_n", "@mathrm{Stem}_n", "@mathsf{LRP}_2", "@mathcal R_2", "@Pi^{@mathrm{up}}_h", "@mathrm{cl}^+_m", "@mathrm{cl}^-_m", "@mathcal W^{(>102)}",
 "A^{(t)}_N", "A^@circ_N", "A^@diamond_N", "A^{@diamond,@mathrm{up}}", "A^@diamond_{@mathrm{dec}}", "@pi_n(t_1,t_2)", "@pi_2(t)", "@Theta^@circ_n", "m_1(k)", "@mathsf H^@ast",
 "K_n(m)", "@gamma_m", "@mathcal Q_m", "@mathcal C_n", "@mathsf B^+", "@mathrm{merge}", "@mathrm{OB}_m", "@mathrm{FL}^{(1)}_m", "@mathrm{Pcor}", "@mathfrak V_m", "@mathfrak d_k",
 "@mathfrak l_m(t)", "@mathrm{land}_m", "@mathsf L_@ast(k)", "@mathcal J_1(k)", "@mathrm{need}_m", "@mathfrak K_N", "@mathfrak K'_N", "@mathfrak K^@prime_N", "@mathrm{regen}_n", "@mathrm{flat}_k",
 "@mathsf{FS}(n)", "@mathcal Y_k(n)", "@mathcal Y^{@mathrm{LP}}_k", "@mathcal Y^@dagger_k", "@nu_0(k)", "@nu_1(k)", "@mathcal F_k(@nu)", "@mathcal F^+_k", "@mathcal F^{@mathrm{LP}}_k", "@mathrm{LP}_k(n)",
 "P^@theta_t(k)", "P^{@theta@dagger}", "t^@dagger", "@varrho^@dagger", "@mathcal O_n", "@mathrm{Bd}", "@mathfrak g^{@mathrm L}_m"]]
for t in targets:
    hits=[(s,n,l,ln) for (s,n,l,ln) in body if t in ln]
    if not hits:
        print(f"[없음] {t}")
    else:
        s,n,l,ln=hits[0]
        secs=sorted(set(h[0] for h in hits), key=lambda x: tuple(int(v) for v in x.split(".")))
        print(f"{t} | 첫 {s} {n}:{l} | 절 {','.join(secs[:12])}{'…' if len(secs)>12 else ''} | {ln.strip()[:170]}")
