# H14: 장부 1.3 국소 기호 묶음이 적은 글자가 해당 장 파일에 실제로 있는지(부분 문자열) 본다. 자리 찾기용.
import os, re, sys
root = r"C:\math\임시\주차함수_증명\장v2"
def load(*fs):
    return "\n".join(open(os.path.join(root, f), encoding='utf-8').read() for f in fs)
T = {
 "1": load("장1.md"), "2": load("장2.md"), "3": load("장3.md"), "4": load("장4.md"),
 "5A": load("장5A.md"), "5B": load("장5B.md"), "5": load("장5A.md", "장5B.md"),
 "6": load("장6.md"), "7A": load("장7A.md"), "7B": load("장7B.md"), "7": load("장7A.md", "장7B.md"),
 "8": load("장8.md"), "9": load("장9.md"), "10": load("장10.md"), "11": load("장11.md"),
 "D": load(*[f for f in os.listdir(root) if f.startswith("부록D")]),
 "ALL": load(*[f for f in os.listdir(root) if f.endswith(".md")]),
}
def norm(s):
    return re.sub(r"\s+", "", s)
TN = {k: norm(v) for k, v in T.items()}

claims = {
 "1": [r"\rho", r"w(\beta)", r"\beta"],
 "2": [r"\mathfrak n_", r"\mathfrak o_", r"\mathfrak c", r"\mathfrak u", r"\mathfrak b", r"M'", r"\varrho", r"w^y_j",
       r"\mathfrak j", r"\upsilon", r"\mathcal F_m(", r"\mathcal J_i", r"\iota", r"z_i", r"\mathcal G_{z,i,n}", r"\Phi_\sigma",
       r"\phi_{i+1}", r"\sigma_{\mathrm L}", r"\mathcal Y(x)", r"\mathfrak t_1", r"\gamma_1", r"\mathcal W_n(\gamma)", r"\Delta_r",
       r"\mathfrak q_v(d)", r"\mathcal Q_{n,r,j}", r"\mathrm{Ren}^{*3}", r"\mathfrak e_i", r"\mathfrak B_m", r"\mathfrak R_m", r"\xi_v",
       r"\mathfrak Z", r"\varphi(d)", r"\eta", r"\mathfrak r", r"\sigma'", r"\mathcal U_\ell(x)", r"V_{n,\ell}", r"\mathcal L", r"\mathcal M_n",
       r"\mathfrak p_n(\omega)", r"\mathcal E", r"\varkappa", r"\mathcal R(x)", r"\mu", r"\mathcal V", r"\psi(\varsigma)", r"\vartheta", r"\kappa"],
 "3": [r"\psi(\vartheta)", r"\mathcal B", r"\overline B", r"\mathrm B(", r"\beta'", r"\mu_\varrho", r"f_\varrho", r"\Lambda", r"\Phi(z)",
       r"\upsilon_n", r"z_\varrho", r"K_\varrho", r"\tau_\varrho", r"w_\varrho", r"Dw", r"\gamma_j", r"T_k", r"\theta_n", r"I_n", r"\rho_j",
       r"j_0", r"\gamma^{(n)}_j", r"\varsigma'", r"\iota", r"\epsilon", r"\lceil3n/4\rceil", r"\omega_n", r"\phi", r"w_n=(n+1)^{-2/3}",
       r"x_\ell", r"C_\ell", r"g_n", r"Z_n", r"z_n", r"\upsilon", r"\mathcal I", r"\mathcal J", r"z_{\max}", r"z^\circ", r"Z_\varrho", r"\bar K_\varrho", r"R=", r"E_\varrho", r"H_\varrho", r"V_\varrho"],
 "4": [r"(\star)", r"F_\ast(", r"\mathcal E_{<k}", r"\mathcal Q_k", r"\mathrm{Bor}(j;\mathfrak Z)", r"\mathfrak Z", r"\mathfrak Y", r"\mathfrak J",
       r"\mathcal W(g)", r"F_y(x)", r"U=F_y", r"C=F_y", r"L=C-He^T", r"I_1", r"D(\mathfrak Y)", r"K(\mathfrak Y)", r"\theta=k-y", r"\mathfrak x_j",
       r"\upsilon_j", r"\mathcal R(\iota)", r"\mathfrak N=n+y+1", r"\mathcal B(\mathfrak Y)", r"\mathfrak m_1", r"\mathfrak t", r"\epsilon_j",
       r"\vartheta=\mathrm{He}_n", r"\kappa=1/k", r"\mathfrak n(\kappa)", r"\mathfrak g(\kappa)", r"\mathfrak l", r"\gamma(\iota)", r"\mathcal P=",
       r"\Theta", r"\eta(v)", r"\mathfrak F(v)", r"f_k(v)", r"\chi=v^2", r"\mathfrak p(v)", r"\mathrm{Bor}^{\mathrm{ld}}", r"\mathrm{Bor}^{\mathrm{sum}}_k",
       r"\varepsilon=k^{-1/2}", r"\varkappa=1-\mathfrak Y", r"\mu=1-\rho^2", r"\beta=\rho z", r"R_{k,\omega}", r"\mathfrak M", r"\mathrm{Wi}_j",
       r"\mathfrak G", r"\mathrm{Mag}_k", r"\mathrm{Ph}_k", r"\mathrm{Pq}", r"\mathrm{Bn}_k", r"\mathrm{Am}_\rho", r"\mathrm{Mag}^{\mathrm J}_k", r"\mathrm{Ph}^{\mathrm J}_\rho",
       r"\mathcal F_0", r"\mathcal F_1", r"\mathfrak c_\rho", r"\tau", r"\Upsilon", r"\mathcal T_{\mathrm R}", r"\mathcal H_{\mathrm R}", r"\mathfrak f=1-",
       r"\mathfrak y_k", r"\mathsf b_D^{\mathrm{vert}}", r"\mathsf b_D^{\mathrm{arc}}", r"\mathfrak s=S/2^{30}", r"2918732888", r"\mathfrak r_i", r"\mathfrak A_n",
       r"\mathfrak d_n", r"\mathfrak z_n", r"\mathfrak j_n", r"\epsilon_n", r"\upsilon^\circ", r"\hat\upsilon", r"\mathfrak C_1", r"\mathfrak U", r"\mathfrak W",
       r"\mathfrak e_i", r"\mathfrak E", r"\mathfrak T", r"\mathfrak L", r"\mathfrak i", r"\tilde{\mathfrak N}", r"\mathfrak x=y/\mathfrak N^2", r"\mathfrak q=n\mathfrak x", r"\phi=-k("],
 "5A": [r"\mathrm{Nw}_{r,d}", r"\mathrm{nv}", r"\mathrm e_{15}", r"\gamma_1", r"\mathfrak d_i", r"\mathcal L(\gamma)", r"\mathrm{rq}_r", r"\mathrm{rq}_\ast",
        r"\mathrm{bv}", r"\mathrm{er}_j", r"\vartheta'_j", r"\mathrm{dc}'_j", r"\mathrm{lo}_j", r"\mathrm{up}_j", r"\mathrm{Pol}_{\mathrm E}", r"\mathcal G_{z,i,n}",
        r"\mathcal T(x)", r"\Theta(x)", r"\phi^{[k]}_m", r"\mathcal R_y", r"\mathcal Q_{<k}", r"\mathcal H", r"\mathrm{hg}_d", r"\mathrm{sd}_d", r"\mathfrak c_{n,k}",
        r"\mathrm{cr}_k", r"\mathcal V_d(", r"\mathrm{co}_", r"\mathrm{tl}", r"\mathrm{tw}_j", r"\mathfrak j", r"\mathcal J_{\mathfrak x'}", r"\mathcal T_{\mathfrak x'}", r"\mathfrak x'",
        r"\mathrm{wt}_k", r"\mathcal H_t", r"\mathfrak K_m", r"\mathfrak R_m(", r"\mathrm{fs}_m", r"\mathrm{fs}'_d", r"\mathcal A_i", r"\mathrm{wl}(", r"\mathfrak f_1",
        r"\mathcal X(x)", r"\mathcal P(x)", r"\mathcal D(x)", r"\mathcal M", r"\mathrm{rt}", r"\mathrm{Cut}", r"\mathrm{wc}(", r"\mathrm{hb}_d", r"\mathrm{bd}_d", r"\mathrm{tm}_d",
        r"\mathcal R_j", r"\mathrm{Pc}(k)", r"\mathrm{eb}", r"\mathfrak k_r", r"\mathfrak s=\sqrt r", r"\mathfrak M_i", r"\mathfrak M^{(6)}_2", r"\mathfrak M^\ast_i", r"\mathfrak C_1",
        r"\mathfrak L(r)", r"\mathfrak X_j", r"\mathfrak X'_j", r"\mathrm{bt}_j", r"\varsigma_1", r"\mathrm{Nu}", r"\mathrm{De}", r"\mathrm{st}", r"\mathfrak F", r"\mathfrak G", r"\mathfrak D",
        r"\mathrm{ic}", r"\mathcal Y_j", r"\mathrm{Wr}_j", r"\hat{\mathrm{Wr}}_j", r"\mathcal U_j(d)", r"\mathsf o", r"\mathrm{cb}_m", r"w=\sqrt{1-z}", r"C(z)",
        r"\mathrm{Ch}_j", r"\mathcal Z^{(\iota)}_j", r"z_\ast", r"\mathrm{lc}_i", r"\mathcal N(\gamma)", r"\mathrm{Rm}_j", r"\mathrm{Rm}^{(2)}_j", r"\mathcal N_j(d)", r"\mathcal O_j",
        r"\mathfrak d", r"\mathrm{Pol}_{\mathrm A}", r"\mathrm S_-", r"\mathrm S_+", r"U'", r"\mathrm{ku}", r"\mathrm{ag}", r"\hat{\mathrm{ag}}", r"\mathrm{pt}", r"\xi=\varsigma e^{1-\varsigma}",
        r"\mathrm{ct}", r"T_+", r"T_{\le k}", r"\hat\varphi", r"\mathrm{et}(", r"\mathfrak l_m", r"\hat L", r"\mathrm{lg}", r"\mathrm{nu}", r"\mathrm{qy}", r"\mathrm{Zh}",
        r"\mathfrak A(", r"\mathrm{ph}(", r"\mathrm{Bt}(", r"\mathfrak I", r"\mathfrak n_n", r"\Omega_e", r"\Omega_B", r"\hat{\mathcal I}_k", r"\mathrm{Ce}_m", r"\mathrm{Cb}", r"\mathrm{ch}_0",
        r"\Upsilon_e", r"\Upsilon_B", r"\mathrm{Tl}_j", r"\Xi", r"\mathrm{Sa}", r"\mathfrak r", r"\mathcal J", r"\mathfrak s_0", r"\mathfrak s_1", r"\mathrm{ku}_{\mathrm{top}}", r"\mathrm{far}_0", r"\mathrm{Bor}(j;\mathrm{pt}')", r"\mathfrak J"],
 "5B": [r"\mathcal C=(S_1", r"\mathfrak c_1", r"\epsilon_0", r"I_1", r"I_4", r"\mathfrak P", r"S_0=m+1", r"w=m-d", r"\varrho_0", r"S_0=Y+q+1", r"R_z", r"D'=",
        r"\mathfrak S_{\mathrm{cut}}", r"\mathrm{tgf}^-_z", r"\mathfrak W=D-z", r"\mathfrak W_0", r"\mathfrak b_z", r"\mathrm{ti}(", r"\mathfrak u(\varsigma)", r"\varsigma_z", r"\xi_1", r"\xi_2",
        r"\mathcal T_z(", r"\mathcal T_{\max}", r"\mathfrak q_z", r"\mathfrak o_{\mathrm{rig}}", r"\mathfrak o_{\mathrm{int}}", r"\mathcal F_z", r"P_{\mathrm{lo}}", r"P_{\min}", r"\tilde\psi", r"\tilde\varphi",
        r"\varkappa", r"\mathfrak b_{\min}", r"\mu(\theta,\kappa)", r"\mathfrak Q(\theta,\kappa)", r"\bar\varrho(\theta)", r"\upsilon_{\max}", r"\mathfrak c_2", r"\mathfrak c_3", r"\mathfrak O(Y)",
        r"\mathfrak y(\theta)", r"\mathfrak h_0", r"0.0342", r"\mathfrak T_1", r"\mathfrak T_2", r"U=m+1", r"\mathfrak p=i/U", r"G_1", r"u_0=\sqrt{2\varsigma}", r"\mathfrak X(\varsigma)",
        r"\theta=z/Y^{1/3}", r"\kappa=\mathfrak t\mathfrak h^2", r"\mathfrak h=Y^{-1/3}", r"\chi_{\mathrm w}", r"\chi_2", r"\mathfrak V(", r"\mathfrak V_\ast", r"\mathrm{hov}(", r"\varepsilon_{\mathrm{hov}}",
        r"\rho=Y/(m+1)", r"\rho_0=(y-1)/n", r"\mathfrak l", r"\Psi_{\mathrm R}", r"0.191", r"\tilde K", r"\mathcal W", r"\lambda_a", r"\lambda_b", r"\mathfrak c_4", r"\bar\varrho_0", r"\bar{\mathfrak c}_1", r"\bar\epsilon_0", r"\mathrm{hv}_{\chi", r"\mathcal R", r"\epsilon(", r"\mathfrak t"],
}
if len(sys.argv) > 1:
    import json
    claims = json.load(open(sys.argv[1], encoding='utf-8'))
for ch, gl in claims.items():
    missing = [g for g in gl if norm(g) not in TN[ch]]
    print(f"[{ch}] 없음 {len(missing)}/{len(gl)}: " + " | ".join(missing))
    for g in missing:
        where = [k for k in ("1","2","3","4","5A","5B","6","7A","7B","8","9","10","11","D") if norm(g) in TN[k]]
        if where: print(f"    {g} -> 다른 곳: {where}")
