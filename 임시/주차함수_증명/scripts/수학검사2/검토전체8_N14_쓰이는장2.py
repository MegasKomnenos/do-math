# -*- coding: utf-8 -*-
"""「쓰이는 장」 불일치 후보를 장별로 부분 문자열(공백 제거)로 다시 찾아 발췌를 보인다."""
import re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
files = {1:["장1"],2:["장2"],3:["장3"],4:["장4"],5:["장5A","장5B"],6:["장6"],7:["장7A","장7B"],8:["장8"],9:["장9"],10:["장10"],11:["장11"]}
lines = {}
for ch,fs in files.items():
    lines[ch]=[]
    for f in fs:
        for i,l in enumerate(open(os.path.join(root,"장v2",f+".md"),encoding='utf-8'),1):
            lines[ch].append((f,i,l.rstrip("\n").replace(" ","")))
def show(ch, subs, label, maxn=3, regex=False):
    hits=[]
    for f,i,s in lines[ch]:
        for p in subs:
            m = re.search(p,s) if regex else (s.find(p)>=0 and re.search(re.escape(p),s))
            if m: hits.append((f,i,s,m)); break
    print(f"[{label}] 장{ch}: {len(hits)}건")
    for f,i,s,m in hits[:maxn]:
        a=max(0,m.start()-70); print(f"   {f}:{i}: …{s[a:m.end()+70]}…")
S=[
 (8,["b_{n","b_{m","b_{2k","b_{N"],"b_{n,ell} 8장"),
 (11,["n^\circ"],"n^circ_k 11장"),
 (10,["p_n","p_m","p_{"],"p_n 10장"),
 (3,["s_n(","s_m(","s_{"],"s_m(y) 3장"),(8,["s_N(","s_n(","s_m(","s_{"],"s_m(y) 8장"),
 (8,["A_{n","A_{N","A_{m"],"A_{n,ell} 8장"),
 (7,["A^\sigma"],"A^sigma 7장"),
 (7,["A_\ell(","A_{k-1}(","A_k(","A_{\ell"],"A_ell(x) 7장"),(9,["A_\ell(","A_{k-1}(","A_k(","A_{k"],"A_ell(x) 9장"),
 (7,["E_{n,k}","E2_"],"E_{n,k} 7장"),
 (6,["H_k"],"H_k 6장"),
 (2,["M^T","M^{T"],"M^T 2장"),
 (5,["P_t(","P_{t","P_s("],"P_t(k) 5장"),(6,["P_t(","P_{t","P_{2k"],"P_t(k) 6장"),
 (9,["P^\theta","P^{\theta"],"P^theta 9장"),
 (7,["Q_{k-1}","Q_\ell"],"Q_ell 7장"),
 (6,["S_1","S_i","S_j","S_L"],"S_1 사슬 6장"),(7,["S_1","S_i","S_j","S_L"],"S_1 7장"),(9,["S_1","S_i","S_j","S_L"],"S_1 9장"),(10,["S_1","S_i","S_j","S_L"],"S_1 10장"),
 (9,["T_\ell","T_k(","T_{k","T_{\ell"],"T_ell 9장"),
 (8,["X_n","X\le","X\ge","(X"],"X 8장"),
 (6,["Z_k"],"Z_k 6장"),(9,["Z_k"],"Z_k 9장"),
 (2,["\beta_i","\beta_j","\beta_{"],"beta_i 2장"),(5,["\beta_i","\beta_j","\beta_{"],"beta_i 5장"),(6,["\beta_i","\beta_j","\beta_{"],"beta_i 6장"),
 (10,["\chi_m","\chi_n","\chi_{"],"chi_m 10장"),
 (7,["\delta_t","\delta_{t","\delta_{m"],"delta_t 7장"),
 (4,["\Gamma^+","\Gamma^-","\Gamma^{\pm","\Gamma^\pm"],"Gamma^pm 4장"),(5,["\Gamma^+","\Gamma^-","\Gamma^{\pm","\Gamma^\pm"],"Gamma^pm 5장"),
 (8,["\kappa_N"],"kappa_N 8장"),
 (10,["\mu_m","\mu_n","\mu_{"],"mu_n 10장"),
 (6,["\pi^0"],"pi^0 6장"),(8,["\pi^0"],"pi^0 8장"),(10,["\pi^0"],"pi^0 10장"),
 (6,["\pi_N(","\pi_n(","\pi_m(","\pi_{"],"pi_n(m) 6장"),(7,["\pi_N(","\pi_n(","\pi_m(","\pi_{"],"pi_n(m) 7장"),(10,["\pi_N(","\pi_n(","\pi_m(","\pi_{"],"pi_n(m) 10장"),
 (8,["\theta_{N","\theta_N","\theta_t","\theta_{t"],"theta_t 8장"),
 (11,["\varrho"],"varrho 11장"),
 (8,["\mathcalB_"],"mathcal B_ell 8장"),(9,["\mathcalB_"],"mathcal B_ell 9장"),
 (7,["\mathcalN_"],"mathcal N_ell 7장"),
 (10,["\mathcalP^"],"mathcal P^(k) 10장"),
 (6,["\mathfraka_"],"frak a_n 6장"),
 (7,["\mathfraka^"],"frak a^circ/rho 7장"),(11,["\mathfraka^"],"frak a^rho 11장"),
 (7,["\mathfrakr_"],"frak r_N 7장"),(10,["\mathfrakr_"],"frak r_N 10장"),
 (10,["\mathfrakX"],"frak X_d 10장"),
 (6,["\mathfrakz_"],"frak z_m 6장"),
 (7,["\mathsfa_"],"sf a_j 7장"),
 (1,["\mathsf{UL}","\mathsfV","(V)"],"UL/V 1장"),(7,["\mathsf{UL}","\mathsfV","(V)"],"UL/V 7장"),(9,["\mathsf{UL}","\mathsfV","(V)"],"UL/V 9장"),(10,["\mathsf{UL}","\mathsfV","(V)"],"UL/V 10장"),(11,["\mathsf{UL}","\mathsfV","(V)"],"UL/V 11장"),
 (6,["\mathsfz_"],"sf z 6장"),(11,["\mathsfz_"],"sf z 11장"),
 (6,["Bor}^{*","Bor^{*"],"Bor^{*j} 6장"),(8,["Bor}^{*","Bor^{*"],"Bor^{*j} 8장"),(10,["Bor}^{*","Bor^{*"],"Bor^{*j} 10장"),
 (6,["Bor}_{>","Bor}_>"],"Bor_> 6장"),(8,["Bor}_{>","Bor}_>"],"Bor_> 8장"),
 (6,["Bor}_{\le","Bor}_\le"],"Bor_le 6장"),(11,["Bor}_{\le","Bor}_\le"],"Bor_le 11장"),
 (9,["\mathrm{cl}"],"cl 9장"),
 (11,["DDL}_2","DDL}^\natural","DDL}^{\natural"],"DDL_2 11장"),
 (10,["\mathrm{inc}"],"inc 10장"),
 (7,["\mathrm{KD}"],"KD 7장"),(10,["\mathrm{KD}"],"KD 10장"),
 (7,["\mathrm{pos}"],"pos 7장"),
 (6,["\mathrm{rb}"],"rb 6장"),
 (6,["\mathrm{tilt}"],"tilt 6장"),(10,["\mathrm{tilt}"],"tilt 10장"),
 (1,["\Pr_","\mathbbE_"],"Pr_n 1장"),(7,["\Pr_","\mathbbE_"],"Pr_n 7장"),(8,["\Pr_","\mathbbE_"],"Pr_n 8장"),(9,["\Pr_","\mathbbE_"],"Pr_n 9장"),(10,["\Pr_","\mathbbE_"],"Pr_n 10장"),
 (2,["\Pr^T","\Pr^{T","\mathbbE^T","\mathbbE^{T"],"Pr^T 2장"),(5,["\Pr^T","\Pr^{T","\mathbbE^T","\mathbbE^{T"],"Pr^T 5장"),
 (8,["\Pr^\sigma","\Pr^{\sigma","\mathbbE^\sigma","\mathbbE^{\sigma"],"Pr^sigma 8장"),(11,["\Pr^\sigma","\Pr^{\sigma","\mathbbE^\sigma","\mathbbE^{\sigma"],"Pr^sigma 11장"),
 (4,["m_1("],"m_1 4장"),(8,["m_0"],"m_0 8장"),(9,["m_0"],"m_0 9장"),(8,["r_0("],"r_0 8장"),(10,["s^{\mathrm{low}}_q"],"s^low_q 10장"),(8,["x_t("],"x_t 8장"),(7,["D_k"],"D_k 7장"),(9,["H_k"],"H_k 9장"),(8,["R_j"],"R_j 8장"),(3,["\rho_k"],"rho_k 3장"),(11,["\mathfrakP_k"],"frak P_k 11장"),(9,["\mathrm{top}"],"top 9장"),(11,["\mathrm{top}"],"top 11장"),(4,["(\star)"],"star 4장"),(5,["\zeta"],"zeta 5장"),(3,["\mathsfP"],"sf P 3장"),(11,["\mathrm{Stays}"],"Stays 11장"),(11,["\mathrm{DDL}"],"DDL 11장"),(11,["\mathrm{Bor}("],"Bor 11장"),(6,["\mathcalC_n"],"cal C_n 6장"),(7,["\mathcalG_y"],"cal G_y 7장"),(7,["\mathcalY_k"],"cal Y_k 7장"),(5,["\mathfrakc_0"],"frak c_0 5장"),(7,["\mathfrakd_k"],"frak d_k 7장"),(5,["\mathfrakl_m"],"frak l_m 5장"),
]
for ch,subs,label in S: show(ch,subs,label)
R=[(5,[r"(?<![A-Za-z\])a_i(?![A-Za-z])"],"a_i 5장"),(8,[r"(?<![A-Za-z\])a_i(?![A-Za-z])"],"a_i 8장"),(10,[r"(?<![A-Za-z\])a_i(?![A-Za-z])"],"a_i 10장"),
   (4,[r"(?<![A-Za-z\])d_i(?![A-Za-z])"],"d_i 4장"),(5,[r"(?<![A-Za-z\])d_i(?![A-Za-z])"],"d_i 5장"),(6,[r"(?<![A-Za-z\])d_i(?![A-Za-z])"],"d_i 6장"),(8,[r"(?<![A-Za-z\])d_i(?![A-Za-z])"],"d_i 8장"),(10,[r"(?<![A-Za-z\])d_i(?![A-Za-z])"],"d_i 10장")]
for ch,pats,label in R: show(ch,pats,label,regex=True)
