# -*- coding: utf-8 -*-
"""I14: 장부 1.2 「쓰이는 장」 대조 — 의심 자리의 문맥을 출력한다."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명/장v2"
files = {'1':['장1'],'2':['장2'],'3':['장3'],'4':['장4'],'5':['장5A','장5B'],'6':['장6'],'7':['장7A','장7B'],'8':['장8'],'9':['장9'],'10':['장10'],'11':['장11']}
L = {}
for c,fs in files.items():
    for f in fs:
        L[f] = open(os.path.join(ROOT,f+'.md'),encoding='utf-8').read().split('\n')
checks = [
 ("a_i", r"a_\{?i\}?", "5 6 8 10 11"),
 ("d_i", r"d_\{?i\}?(?![a-z0-9])", "3 4 5 6 8 9 10 11"),
 ("m_1", r"m_\{?1\}?", "2 4 5 6 7 10"),
 ("m_0", r"m_\{?0\}?", "5 8 9"),
 ("n^sharp/flat/circ", r"n\^\\(sharp|flat|circ)", "4"),
 ("r_0", r"r_\{?0\}?", "8"),
 ("s^F", r"s\^\{\\mathrm F\}", "1 4 7 8 9 11"),
 ("t_v", r"t_\{?v\}?", "8"),
 ("w_m", r"w_\{?m\}?", "11"),
 ("x_t", r"x_\{?t\}?", "8"),
 ("D_k", r"D_\{?k\}?", "7"),
 ("H_k", r"H_\{?k\}?", "9"),
 ("K_n", r"K_\{?n\}?", "2 4 5 7"),
 ("R_j", r"R_\{?j\}?", "8"),
 ("alpha", r"\\alpha(?![A-Za-z])", "9"),
 ("lambda", r"\\lambda(?![A-Za-z])", "6"),
 ("Omega", r"\\Omega(?![A-Za-z])", "5 6 7"),
 ("Pi plain", r"\\Pi(?![A-Za-z_^])", "6"),
 ("pi_2", r"\\pi_\{?2\}?", "6"),
 ("Psi plain", r"\\Psi(?![A-Za-z_^])", "5 7"),
 ("psi", r"\\psi(?![A-Za-z])", "2 4 5 7 9 11"),
 ("rho_k", r"\\rho_\{?k\}?", "3"),
 ("sigma", r"\\sigma(?![A-Za-z])", "6 10"),
 ("tau", r"\\tau(?![A-Za-z])", "3 8"),
 ("Upsilon", r"\\Upsilon", "1 4 5 7 8 10"),
 ("xi", r"\\xi(?![A-Za-z])", "5 7"),
 ("zeta", r"\\zeta(?![A-Za-z])", "11"),
 ("mathcal D", r"\\mathcal D(?![A-Za-z])", "6 7 9"),
 ("mathcal G_y", r"\\mathcal G(_\{?y|\^\{?y)", "5 7"),
 ("mathcal U_k", r"\\mathcal U_\{?k", "7"),
 ("mathcal Z", r"\\mathcal Z(?![A-Za-z_^])", "5 6 11"),
 ("mathfrak D", r"\\mathfrak D(?![A-Za-z])", "5 6"),
 ("mathfrak K_N", r"\\mathfrak K", "6"),
 ("mathfrak l_m", r"\\mathfrak l(?![A-Za-z])", "5"),
 ("mathfrak m(", r"\\mathfrak m(?![A-Za-z])", "4 7 8"),
 ("mathfrak P_k", r"\\mathfrak P", "11"),
 ("mathsf P", r"\\mathsf P(?![A-Za-z_^])", "3"),
 ("mathsf u(", r"\\mathsf u(?![A-Za-z])", "7"),
 ("mathsf W", r"\\mathsf W", "7 11"),
 ("Bor", r"\\mathrm\{Bor\}", "11"),
 ("DDL", r"\\mathrm\{DDL\}", "11"),
 ("Stays", r"\\mathrm\{Stays\}", "11"),
 ("top", r"\\mathrm\{top\}", "7 9 11"),
 ("(star)", r"\(\\star\)", "4"),
 ("s^W", r"s\^\{\\mathrm W\}", "1 2 3 4 5 6 7 8 9 11"),
 ("mathfrak s^fr/up/low", r"\\mathfrak s\^\{\\mathrm\{(fr|up|low)\}\}", "1 2 3 4 5 6 7 8 9 11"),
 ("vartheta", r"\\vartheta", "2 3 4 5 6 7 8 9 11"),
 ("omega_m/y/sharp", r"\\omega(_\{?[my]|\^\\sharp)", "4 5 6 7 8 11"),
 ("mathfrak A", r"\\mathfrak A(?![A-Za-z])", "5 6 7 11"),
 ("mathfrak B", r"\\mathfrak B(?![A-Za-z])", "1 2 4 5 6 7 9 10 11"),
 ("mathfrak R^low", r"\\mathfrak R(?![A-Za-z])", "2 5 6 7 10 11"),
 ("mathfrak Q", r"\\mathfrak Q(?![A-Za-z])", "2 3 5 6 7 8 9 11"),
 ("Bd^T", r"\\mathrm\{Bd\}\^\{\\mathrm T\}", "1 4 6 7 8 9 11"),
 ("mathcal F_k", r"\\mathcal F(?![A-Za-z])", "2 4 5 6 7 8 10"),
 ("mathcal Y", r"\\mathcal Y(?![A-Za-z])", "2 5 6 7"),
 ("pi^two", r"\\pi\^\{\\mathrm\{two\}\}", "2 3 4 5 6 7 8 9 11"),
 ("mathfrak g(", r"\\mathfrak g(?![A-Za-z])", "4 6 7 8 9 10"),
 ("Pi^up", r"\\Pi\^\{\\mathrm\{up\}\}", "2 5 6"),
 ("A^diamond", r"A\^\{?\\diamond", "1 3 4 5 6 7 8 10 11"),
 ("Phi", r"\\Phi(?![A-Za-z_])", "2 3 6 8 9"),
 ("nu_min/bar nu", r"\\nu_\{\\min\}|\\bar\\nu", "3 5 6 7 8 9 11"),
 ("Bor^tail", r"\\mathrm\{Bor\}\^\{\\mathrm\{tail\}\}", "2 6 8 9 10 11"),
 ("Psi^low", r"\\Psi\^\{\\mathrm\{low\}\}", "2 5 6 7 10 11"),
 ("mathcal J_1", r"\\mathcal J_\{?[1-4]", "1 2 3 4 5 6 7 8 10 11"),
 ("mathcal A_{k,n}", r"\\mathcal A_\{k", "1 2 3 5 6 8 9 10 11"),
 ("mathcal T_k", r"\\mathcal T_\{?k|\\mathcal T_\{n,k\}", "1 2 3 4 5 6 8 9 10"),
 ("mathcal S_{n,k}", r"\\mathcal S_\{n,k\}", "1 2 3 6 7 8 9 10 11"),
 ("mathcal K_{n,k}", r"\\mathcal K_\{n", "1 3 6 8 9 10 11"),
 ("Xi", r"\\Xi(?![A-Za-z])", "1 3 5 6 7 8 9 10 11"),
 ("E_{n,k}/E2", r"\bE2?_\{n,k\}", "3 6 8 9 10 11"),
 ("B_{n,", r"(?<![A-Za-z\\])B_\{n,", "3 6 8 9 10"),
 ("C_k(/C_{n,k}", r"(?<![A-Za-z\\])C_\{?k\}?\(|(?<![A-Za-z\\])C_\{n,k\}", "1 2 3 4 5 6 8 9 10 11"),
 ("J_n(", r"(?<![A-Za-z\\])J_\{?n\}?\(", "3 6 8 9 10 11"),
 ("Conv/Kink", r"\\mathrm\{(Conv|Kink)\}", "1 2 3 4 5 6 8 9 10 11"),
 ("DD", r"\\mathrm\{DD\}(?!L)", "1 2 3 4 5 7 8 9 11"),
 ("IH", r"\\mathrm\{IH\}", "1 2 3 4 6 7 8 9 10 11"),
 ("Lc", r"\\mathrm\{Lc\}", "1 2 3 4 6 7 8 9 10 11"),
 ("nf", r"\\mathrm\{nf\}", "1 3 4 6 7 8 9 10 11"),
 ("pr_", r"\\mathrm\{pr\}", "1 2 3 4 5 6 8 9 10 11"),
 ("Pr^sigma", r"\\Pr\^\{?\\sigma|\\mathbb E\^\{?\\sigma", "1 2 3 4 5 6 9 10"),
 ("mathfrak v_k", r"\\mathfrak v", "1 3 4 5 6 8 9 10 11"),
 ("b^T", r"b\^\{?T\}?", "1 3 4 5 6 7 8 10 11"),
 ("b^circ", r"b\^\\circ", "1 2 3 4 6 7 8 9 10 11"),
 ("A^c_", r"A\^\{?c\}?_", "1 2 3 4 6 7 8 9 10 11"),
 ("L plain", r"(?<![A-Za-z\\_^{])L(?![A-Za-z_^}])", "1 4 5 8 11"),
 ("G plain", r"(?<![A-Za-z\\_^{])G(?![A-Za-z_^}(])", "4 7 11"),
 ("F plain", r"(?<![A-Za-z\\_^{])F(?![A-Za-z_^}(])", "1 3 4 8 10 11"),
 ("M(F)", r"M\(F\)", "1 3 4 5 8 10 11"),
 ("T(x)", r"(?<![A-Za-z\\_^{])T\(", "6 8 9 10"),
 ("V(", r"(?<![A-Za-z\\_^{])V\(", "1 2 3 6 8 9 10 11"),
 ("X_n", r"(?<![A-Za-z\\_^{])X_\{?n", "1 4 5 6 7 9 10 11"),
 ("P^+_t", r"P\^\{?\+\}?_", "1 2 4 5 6 7 10 11"),
 ("Z_", r"(?<![A-Za-z\\_^{])Z_", "6"),
 ("W_ 6장", r"(?<![A-Za-z\\_^{])W_\{?[a-zA-Z]\}?\(", "6"),
 ("beta 5장", r"\\beta", "5"),
 ("Bor^ 6,8,10", r"\\mathrm\{Bor\}\^", "6 8 10"),
 ("P_(k) 5장", r"P_\{?[a-z0-9+\\-]+\}?\((k|y|Y)\)", "5"),
 ("mathcal N_phi 7A 1.3?", r"\\mathcal N_\\phi", "7"),
]
for name,pat,chs in checks:
    rx=re.compile(pat)
    print(f"#### {name}")
    for c in chs.split():
        for f in files[c]:
            n=0
            for i,l in enumerate(L[f],1):
                for m in rx.finditer(l):
                    s=max(0,m.start()-60); e=min(len(l),m.end()+60)
                    print(f"  {f}:{i}: …{l[s:e]}…")
                    n+=1; break
                if n>=2: break
