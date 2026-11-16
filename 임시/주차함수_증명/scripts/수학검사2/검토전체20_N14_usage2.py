# -*- coding: utf-8 -*-
"""N14: 1.2 거르기에서 뜬 행을 고정 문자열 변형들로 장별 개수를 센다."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
CH = {"1":["장1"],"2":["장2"],"3":["장3"],"4":["장4"],"5":["장5A","장5B"],"6":["장6"],"7":["장7A","장7B"],"8":["장8"],"9":["장9"],"10":["장10"],"11":["장11"]}
CMDS = ["mathcal","mathfrak","mathsf","mathrm","mathbb","mathscr","tilde","hat","bar","widetilde","overline","underline","mathbf"]
def norm(s):
    s = s.replace('\\prime', "'"); s = re.sub(r'\s+', '', s)
    for c in CMDS: s = re.sub(r'\\' + c + r'([A-Za-z])', r'\\' + c + r'{\1}', s)
    return s.replace('\\,', '').replace('\\;', '').replace('\\!', '')
text = {k: norm(''.join(open(os.path.join(ROOT,"장v2",f+".md"),encoding='utf-8').read() for f in fs)) for k,fs in CH.items()}
checks = [
 ("b^T_", ["b^{T}_","b^T_"]), ("c^{(2)}", ["c^{(2)}"]), ("p_ (10장)", ["p_n","p_m","p_{"]),
 ("s^T_", ["s^{T}_","s^T_"]), ("s_·(y) 3·8장", ["s_n(","s_N(","s_m(","s_{"]),
 ("A^\\sigma", ["A^\\sigma","A^{\\sigma}"]), ("A_\\ell(x)·A_{k-1}(x)", ["A_\\ell(x)","A_{k-1}(x)","A_{\\ell}(x)","A_{k}(x)","A_k(x)"]),
 ("B_{n,", ["B_{n,","B_{m,"]), ("M^T_", ["M^{T}_","M^T_"]), ("P^\\theta_", ["P^{\\theta}_","P^\\theta_"]),
 ("Q_{k-1}(x)·Q_\\ell", ["Q_{k-1}","Q_\\ell","Q_{\\ell}"]), ("S_1", ["S_1","S_i","S_j","S_L"]), ("T_{k-1}(x)·T_\\ell", ["T_{k-1}","T_\\ell","T_{\\ell}","T_k(x)","T_k-"]),
 ("\\beta_", ["\\beta_i","\\beta_j","\\beta_1","\\beta_{"]), ("\\chi_·(j)", ["\\chi_m(","\\chi_t(","\\chi_n(","\\chi_{"]), ("\\delta_t", ["\\delta_t","\\delta_{t","\\delta_s"]),
 ("\\Gamma^\\pm", ["\\Gamma^+","\\Gamma^-","\\Gamma^{+}","\\Gamma^{-}","\\Gamma^\\pm","\\Gamma^{\\pm}"]), ("\\mu_·(k)", ["\\mu_n(","\\mu_m(","\\mu_{"]),
 ("\\pi^0_", ["\\pi^0_","\\pi^{0}_","\\pi^{0,"]), ("\\pi_·( 6·7·10", ["\\pi_n(","\\pi_N(","\\pi_m(","\\pi_t(","\\pi_{"]),
 ("\\mathcal B_", ["\\mathcal{B}_"]), ("\\mathcal P^{(k)}", ["\\mathcal{P}^{(k)}"]), ("\\mathfrak a_", ["\\mathfrak{a}_n","\\mathfrak{a}_N","\\mathfrak{a}_m","\\mathfrak{a}_{","\\mathfrak{a}_j","\\mathfrak{a}_t","\\mathfrak{a}_s"]),
 ("\\mathfrak a^\\circ", ["\\mathfrak{a}^\\circ","\\mathfrak{a}^{\\circ}"]), ("\\mathfrak a^\\rho", ["\\mathfrak{a}^\\rho","\\mathfrak{a}^{\\rho}"]),
 ("\\mathfrak r_", ["\\mathfrak{r}_N","\\mathfrak{r}_{","\\mathfrak{r}_m","\\mathfrak{r}_n","\\mathfrak{r}_t"]), ("\\mathfrak z_", ["\\mathfrak{z}_m","\\mathfrak{z}_{","\\mathfrak{z}_n"]),
 ("\\mathsf a_", ["\\mathsf{a}_0","\\mathsf{a}_1","\\mathsf{a}_j","\\mathsf{a}_"]), ("\\mathrm{Bor}^{*", ["\\mathrm{Bor}^{*","\\mathrm{Bor}^*"]), ("\\mathrm{Bor}_>", ["\\mathrm{Bor}_>","\\mathrm{Bor}_{>}"]),
 ("\\mathrm{cl}^", ["\\mathrm{cl}^"]), ("\\mathrm{inc}^", ["\\mathrm{inc}^"]), ("\\mathrm{KD}", ["\\mathrm{KD}"]), ("\\mathrm{pos}", ["\\mathrm{pos}"]), ("\\mathrm{rb}_", ["\\mathrm{rb}_"]),
 ("\\mathrm{tilt}", ["\\mathrm{tilt}"]), ("\\Pr_·", ["\\Pr_n","\\Pr_m","\\Pr_N","\\Pr_{","\\Pr_t","\\mathbb{E}_n","\\mathbb{E}_N","\\mathbb{E}_m","\\mathbb{E}_{"]), ("\\Pr^T_t", ["\\Pr^{T}_t","\\Pr^T_t","\\mathbb{E}^T_t","\\mathbb{E}^{T}_t"]),
 ("\\Pr^\\sigma", ["\\Pr^{\\sigma}","\\Pr^\\sigma","\\mathbb{E}^{\\sigma}","\\mathbb{E}^\\sigma"]), ("(P◇)", ["\\mathrm{P}\\Diamond","(\\mathrm P\\Diamond)","P\\Diamond","\\Diamond)"]),
 ("a_i", ["a_i"]), ("d_i", ["d_i","d_{\\sigma_i}"]), ("w_m", ["w_m"]), ("\\vartheta 11장", ["\\vartheta"]), ("\\mathcal Z", ["\\mathcal{Z}"]), ("\\mathfrak P_k", ["\\mathfrak{P}_k"]),
 ("\\mathsf P (맨)", ["\\mathsf{P}$","\\mathsf{P}("]), ("\\mathsf Q (맨/L/R)", ["\\mathsf{Q}$","\\mathsf{Q}_L","\\mathsf{Q}_R","\\mathsf{Q}(","\\mathsf{Q}를","\\mathsf{Q}의","\\mathsf{Q}는"]), ("\\mathsf W(맨/♯)", ["\\mathsf{W}$","\\mathsf{W}^\\sharp","\\mathsf{W}("]),
 ("\\mathrm{Bor}( 11장", ["\\mathrm{Bor}("]), ("\\mathrm{DDL}(", ["\\mathrm{DDL}(","\\mathrm{DDL}$"]), ("\\mathrm{top}", ["\\mathrm{top}"]), ("\\mathfrak P_k(\\infty)", ["\\mathfrak{P}_k(\\infty)"]),
 ("\\mathrm{Stays}^{\\mathrm{up}}", ["\\mathrm{Stays}^{\\mathrm{up}}"]), ("\\kappa_N", ["\\kappa_N","\\kappa_{N"]), ("T(x) 2장", ["T(x)"]),
]
for name, toks in checks:
    row = []
    for k in CH:
        cnt = {t: text[k].count(t) for t in toks}
        tot = sum(cnt.values())
        if tot: row.append(f"{k}:{tot}" + ("" if len(toks)==1 else "{"+",".join(f"{t}={c}" for t,c in cnt.items() if c)+"}"))
    print(name, "→", "; ".join(row))
