# -*- coding: utf-8 -*-
"""고정 문자열로 정의 문맥을 뽑고, 계산 표지 진술 목록을 낸다 (O11)."""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = r"C:\math\임시\주차함수_증명\장v2\\"
heads = json.load(open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_O11_heads.json", encoding='utf-8'))

def show(f, needles, w=200, maxn=2):
    L = open(B + f, encoding='utf-8').read().split('\n')
    for nd in needles:
        n = 0
        for i, l in enumerate(L, 1):
            p = l.find(nd)
            while p >= 0 and n < maxn:
                print(f"[{f}:{i}] …{l[max(0,p-60):p+len(nd)+w]}…"); n += 1
                p = l.find(nd, p + 1)
            if n >= maxn: break
        if n == 0: print(f"[{f}] '{nd}' : 없음")

print("### 계산 표지 진술")
for lab, h in heads.items():
    mm = re.findall(r'\[([^\[\]]*)\]', h['rest'])
    st = mm[-1] if mm else ''
    if '계산' in st:
        print(f"  {lab:30s} {h['file']}:{h['line']} §{h['sec']} :: {st}")

print("\n### 11.3 계산 진술 열의 라벨 머리 지위")
ch11 = open(B + '장11.md', encoding='utf-8').read().split('\n')
on = False
for l in ch11:
    if l.startswith('### 11.3'): on = True
    if l.startswith('### 11.4'): on = False
    if on and l.startswith('| ') and not l.startswith('|---'):
        cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
        if len(cells) < 2 or cells[0] == '입력': continue
        for lab in re.findall(r'\{\{(\d+:[^}]+)\}\}', cells[1]):
            h = heads.get(lab)
            mm = re.findall(r'\[([^\[\]]*)\]', h['rest']) if h else []
            print(f"  {lab:30s} :: {mm[-1] if mm else '?'}")

print("\n### 문맥")
show('장2.md', [r'\mathcal W_n(\gamma)', r'W_n(\gamma):=', r'\mathcal H_{\mathrm B}', r'\Psi(q):=', r'\mathrm{Ren}(j):=', r'\mathrm{Ren}(0)', r'e_n:=', r'E2_{n,k}', r'E_{n,k}:=', r'\Pi:=', r'P_t(k):=', r'g(x):=', r'\beta', r'R_j:=', r'R_0'])
show('장6.md', [r'\mathfrak b_m:=', r'\mathfrak p_m:=', r'\mathrm{hz}_k(N):=', r'\mathrm{dec}_N:=', r'\mathfrak w_n(t):=', r'\mathfrak r_N:=', r'\mathcal U_k(m):=', r'\mathcal V_k(m):='])
show('장7A.md', [r'\mu_n(k):=', r'\mathcal T_{n,k}:='])
show('장7B.md', [r'\mathcal P^{(k)}_m(j):=', r'w_m:=', r"\mathrm{KD}'_n", r'\mathrm{KD}^\prime_n', r'\mathrm{Quad}_n', r'\mathrm{Stem}_n:='])
show('장8.md', [r'\theta_{N+1}(m)', r'\mathrm{dup}_m', r'\mathrm{Flow}_q', r'\Omega:[0,6]'])
show('장9.md', [r'\mathcal C_n:=', r'\mathcal Q_m:=', r'\mathfrak V_m:=', r'\mathrm{Pcor}_m', r'\mathrm{OB}_m', r'\mathrm{regen}_n:=', r'\mathsf{FS}(n)', r'\mathrm{LP}_k(n)', r'\nu_0(k)', r'\nu_1(k)', r'\mathcal O_n:=', r'\mathrm{merge}'])
show('장10.md', [r'\mathfrak T_m:=', r'm^\flat', r'\mathrm{Bd}^{\mathrm S}', r'\mathrm{Stays}^{\mathrm{vis}}', r'\mathrm{Stays}_{\mathrm{PM}}', r'\mathrm{Stays}_X', r'\nu_{\min}(k)', r'\bar\nu', r'\mathfrak H_d', r'\mathfrak k_d(q)', r'\mathrm{inc}^', r'\mathrm{Res}_d', r'\mathrm{tr}_y(q)', r'k_0', r'k^\ast', r'\mathfrak Q(y,\xi)', r'\mathfrak s^{\mathrm{low}}_d', r'\mathrm{Stays}^{\mathrm{up}}', r'\mathcal G_y(q)', r'\mathcal G^y(q)', r'\mathfrak A_j', r'\mathfrak A^{\mathrm{crit}}', r'\mathfrak h_y(q)', r'\mathfrak s^{\mathrm{fr}}_d', r'\mathrm{DDL}_2', r'\mathrm{DDL}^\natural', r'\omega_y(d)', r'\tilde\omega'])
show('장5B.md', [r'\mathrm{top}_\pi', r'\mathrm{WIN}^{\mathrm V}_0', r'\mathrm{POS}^{\prime-}_0', r"\mathrm{POS}'_0", r'\mathrm{POS}^\prime_0', r'\mathfrak g(\theta)', r'\mathrm{IH}(n,y)', r'\mathrm{tail}_s(y):='])
show('장5A.md', [r'b^\circ_{n,\ell}', r'\mathfrak a_n:=', r'A^c_{n,\ell}', r'A^{c}_{n,\ell}', r'(\mathrm G)_d'])
show('장3.md', [r'x_\ast', r'\ell_n'])
show('장4.md', [r'\mathsf{LH}(n)', r'\mathsf{LH}^+(n)', r'\mathsf S_R', r'\mathcal S_{n,k}', r'\mathcal D(\beta)', r'\mathsf b_D', r'\mathrm{He}_j', r'\mathrm{Bor}^{\mathrm{tail}}_k'])
show('장7A.md', [r'\mathrm{Conv}_{n,k}', r'\mathrm{Kink}_{n,k}', r'\mathsf W_L^\flat', r'\mathsf W_L', r'\mathfrak a^\circ_m', r'\rho_k'])
show('장7B.md', [r'\chi_m(j)', r'\mathrm{cl}^+_m', r'\mathrm{inh}_k(n)', r'\mathrm{inh}^{\mathrm{lin}}_k', r'\mathrm{src}_k(m)', r'(\star)(n)', r'\mathsf{SRC}^+', r'\mathcal Z', r'J^{\mathrm G}_n(z)'])
