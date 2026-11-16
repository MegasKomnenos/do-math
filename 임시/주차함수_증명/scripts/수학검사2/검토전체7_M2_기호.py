import re
A=open('장v2/부록A.md',encoding='utf-8').read().splitlines()
B=open('장부_v2.md',encoding='utf-8').read().splitlines()
keys=[r'Bor}(j;',r'mathrm{Wi}',r'R_{k,',r'mathrm{sum}',r'mathrm{ld}',r'mathrm{Mag}',r'mathfrak G$',r'vartheta',r'mathrm{Gr}',r'mathcal E_{<k}',r'mathcal Q_k',r'mathcal K_{n,k}',r'Theta$',r'varkappa',r'upsilon_',r'mathfrak x$',r'mathrm{Pq}',r'mathrm{Bn}',r'mathfrak l$',r'mathcal T_',r'mathcal F_0',r'mathfrak s$',r'psi',r'mathcal B$',r'Lambda',r'K_\varrho',r'mu_\varrho',r'f_\varrho',r'omega_n',r'theta_n',r'varsigma',r'mathrm{Am}',r'mathrm{Ph}',r'mathfrak q',r'mathfrak U',r'hat\upsilon',r'upsilon^\circ',r'mathfrak C_1',r'mathcal P',r'mathfrak g(',r'mathfrak n(',r'mathfrak F(v)',r'f_k(v)',r'chi',r'mathcal R(',r'mathfrak t',r'epsilon_j',r'mathfrak m_',r'mathfrak c_',r'mathfrak y_k',r'mathfrak f',r'mathcal H_',r'Z_n',r'g_n',r'C_\ell',r'w_n',r'S_i',r'gamma_j',r'T_k',r'I_n',r'rho_j',r'eta(\phi)',r'eta(v)',r'mathrm{rb}',r'kappa$',r'mathfrak N',r'\varrho',r'\rho',r'\iota',r'\theta',r'\phi',r'\mu',r'\beta',r'\varepsilon']
for k in keys:
    a=[i+1 for i,l in enumerate(A) if l.startswith('|') and k in l.split('|')[1]]
    b=[i+1 for i,l in enumerate(B) if l.startswith('|') and k in l.split('|')[1]]
    print(f"{k:22s} A:{a[:5]} 장부:{b[:6]}")
