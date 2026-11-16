# -*- coding: utf-8 -*-
# 장부 1.2 「뜻」 열의 정의식을 장 파일의 정의 자리와 대조하기 위한 문맥 조회
import re, io, os, glob
base = r"C:\math\임시\주차함수_증명\장v2"
def grep(files, pat, width=150, maxhits=3):
    rx = re.compile(pat)
    print(f"=== {pat}  in {files}")
    n = 0
    for f in files:
        for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
            m = rx.search(line)
            if m:
                s = max(0, m.start()-width//3); e = min(len(line), m.end()+width)
                print(f"  {f}:{i}: …{line[s:e].strip()}…")
                n += 1
                if n >= maxhits: return
    if n == 0: print("  (없음)")

grep(['장6.md'], r's\^\{\\mathrm F\}\(k,\\nu\)\s*(:=|=)', maxhits=2)
grep(['장5B.md'], r'q_\{\\max\}\(Y\)\s*(:=|=)|q_\{\\max\}\s*(:=|=)', maxhits=3)
grep(['장8.md'], r'q_\{\\mathrm\{fb\}\}\s*(:=|=)|m_\{\\mathrm\{fb\}\}\s*(:=|=)|q\^\\circ_\{\\mathrm\{fb\}\}\s*(:=|=)', maxhits=4)
grep(['장8.md'], r'\\mathrm\{fb\}\(\\lambda\)\s*(:=|=)|\\mathrm\{fb\}\^\\circ', maxhits=3)
grep(['장10.md'], r'\\nu_\{\\min\}\(k\)\s*(:=|=)', maxhits=2)
grep(['장7B.md'], r'\\mathcal W\^\{\(>102\)\}\s*(:=|=)|\\mathcal W\^\{\(>40\)\}', maxhits=3)
grep(['장9.md'], r'\\mathsf h_N\s*(:=|=)', maxhits=2)
grep(['장6.md'], r'\\mathsf u\(k\)\s*(:=|=)', maxhits=2)
grep(['장6.md'], r"\\mathsf v'_k\s*(:=|=)|\\mathsf v\^\\prime_k\s*(:=|=)|\\mathsf v\(k\)\s*(:=|=)", maxhits=3)
grep(['장10.md'], r'\\mathrm\{DDL\}\(k\)\s*(:=|=)', maxhits=2)
grep(['장10.md'], r'\\mathrm\{PM\}_y\(d\)\s*(:=|=)', maxhits=2)
grep(['장10.md'], r'\\pi\^\{\\mathrm\{two\}\}_N\s*(:=|=)', maxhits=2)
grep(['장10.md'], r'\\vartheta_\{\\mathrm\{lb\}\}\s*(:=|=)|\\vartheta_0\s*(:=|=)', maxhits=3)
grep(['장10.md'], r'\\mathsf m_\{\\mathrm S\}', maxhits=3)
grep(['장8.md'], r'\\mathfrak c_0\(N\)\s*(:=|=)', maxhits=2)
grep(['장8.md'], r'\\mathfrak B_N\s*(:=|=)|\\mathfrak B\^\{\\mathrm\{low\}\}', maxhits=3)
grep(['장5B.md'], r'\\mathfrak z_m\(d\)\s*(:=|=)', maxhits=2)
grep(['장6.md'], r'\\mathrm\{DD\}\(m,y\)\s*(:=|=)', maxhits=2)
grep(['장6.md'], r'\\mathrm\{hz\}_k\(N\)\s*(:=|=)|\\mathrm\{dec\}_N\s*(:=|=)|\\mathfrak r_N\s*(:=|=)|\\varrho_t\s*(:=|=)', maxhits=5)
grep(['장6.md'], r'\\epsilon_N\s*(:=|=)|\\epsilon_N\\le|\\le\\epsilon_N', maxhits=3)
grep(['장6.md'], r'\\mathsf s_\{\\mathrm B\}|\\mathsf s_\{\\mathrm\{B\}\}|e/\\sqrt\{2\\pi\}', maxhits=4)
grep(['장8.md', '장10.md'], r'\\mathsf s_\{\\mathrm B\}', maxhits=3)
grep(['장9.md'], r'\\gamma_m\s*(:=|=)|K_n\(m\)\s*(:=|=)', maxhits=3)
grep(['장8.md'], r'\\mathfrak h\(k,\\nu\)\s*(:=|=)', maxhits=2)
grep(['장7A.md'], r'\\mathsf t_k\s*(:=|=)|n\^\\sharp_k\s*(:=|=)|n_\{\\mathrm X\}\(k\)\s*(:=|=)', maxhits=4)
grep(['장7B.md'], r'n_\{\\mathrm\{PD\}\}\(k\)\s*(:=|=)', maxhits=2)
grep(['장7A.md'], r'\\rho_k\s*(:=|=)|C_k\(\\rho_k\)=1', maxhits=3)
grep(['장7A.md'], r'\\mu_n\(k\)\s*(:=|=)|\\mathcal T_k\(\\sigma\)\s*(:=|=)', maxhits=3)
grep(['장7B.md'], r'w_m\s*(:=|=)\\binom|\\mathfrak u_n\s*(:=|=)|\\Pi\^\{\\mathrm\{up\}\}_j\s*(:=|=)', maxhits=4)
grep(['장9.md'], r'\\mathfrak l_m\(t\)\s*(:=|=)|\\mathfrak d_k\s*(:=|=)', maxhits=3)
grep(['장9.md'], r'\\nu_0\(k\)\s*(:=|=)|\\nu_1\(k\)\s*(:=|=)|t\^\\dagger\s*(:=|=)|P\^\\theta_t\(k\)\s*(:=|=)', maxhits=5)
grep(['장10.md'], r'\\mathfrak k_d\(q\)\s*(:=|=)|\\mathfrak h_y\(q\)\s*(:=|=)|\\mathrm\{inc\}\^\+_q\s*(:=|=)|\\mathrm\{tr\}_y\(q\)\s*(:=|=)|\\mathfrak A_j\s*(:=|=)', maxhits=6)
grep(['장10.md'], r'd\^\\star\s*(:=|=)|\\mathfrak Q\(y,\\xi\)\s*(:=|=)|\\mathrm\{Stays\}\s*(:=|=)|\\omega_m\s*(:=|=)|m\^\\flat\s*(:=|=)|\\mathrm\{Bd\}\^\{\\mathrm S\}\s*(:=|=)', maxhits=8)
grep(['장10.md'], r'\\mathcal G_y\(q\)\s*(:=|=)|\\mathfrak s\^\{\\mathrm\{fr\}\}_d\(y\)\s*(:=|=)|\\mathfrak s\^\{\\mathrm\{up\}\}_d\(y\)\s*(:=|=)', maxhits=4)
grep(['장8.md'], r'\\mathrm\{km\}_N\s*(:=|=)|\\mathfrak R_q\s*(:=|=)|\\mathfrak D_q\s*(:=|=)|\\Omega_q\s*(:=|=)|\\xi_q\s*(:=|=)', maxhits=6)
grep(['장5B.md'], r'\\mathrm\{Lc\}\(Y,q\)\s*(:=|=)|\\Lambda_\{\\mathrm w\}\(Y\)\s*(:=|=)|t_0\(y\)\s*(:=|=)', maxhits=4)
grep(['장5A.md'], r'\\mathfrak m\(n\)\s*(:=|=)|r_0\(n\)\s*(:=|=)|A\^c_\{n,\\ell\}\s*(:=|=)|b\^\\circ_\{n,\\ell\}\s*(:=|=)', maxhits=5)
grep(['장2.md'], r'\\mathrm\{nf\}\(n,d\)\s*(:=|=)|W_n\(\\gamma\)\s*(:=|=)|\\mathrm\{rb\}_m\s*(:=|=)|\\mathrm\{Ren\}\(j\)\s*(:=|=)|\\Psi\(q\)\s*(:=|=)|\\theta_t\(k\)\s*(:=|=)', maxhits=6)
grep(['장2.md'], r'\\mathfrak v_k\(Z,H\)\s*(:=|=)|J_n\(z\)\s*(:=|=)|\\mathrm\{Gr\}\(x\)\s*(:=|=)|\\Xi_\{n,k\}\s*(:=|=)|\\mathcal K_\{n,k\}\(y\)\s*(:=|=)', maxhits=6)
grep(['장4.md'], r'\\mathsf a_j\s*(:=|=)|\\mathsf n_k\s*(:=|=)|\\mathsf g_k\s*(:=|=)|\\mathcal I_k\s*(:=|=)|\\mathcal A_\{k,n\}\s*(:=|=)|V\(x\)\s*(:=|=)', maxhits=6)
grep(['장3.md'], r'X_n\s*(:=|=)|x_\\ast\s*(:=|=)|\\ell_n', maxhits=4)
grep(['장8.md'], r'되먹임', maxhits=3)
grep(['장2.md'], r'첫 층 상속', maxhits=2)
grep(['장6.md'], r'분할 무게|짝 없는|둘째 꼴|첫째 꼴', maxhits=6)
grep(['장7A.md'], r'병합|재생', maxhits=4)
grep(['장10.md'], r'첫째 꼴|둘째 꼴', maxhits=3)
