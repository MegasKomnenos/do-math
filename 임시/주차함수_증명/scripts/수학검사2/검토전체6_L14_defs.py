# -*- coding: utf-8 -*-
"""L14: (1) 장부 1.2 「뜻」 열의 정의식을 장 파일의 정의 자리와 견주기 위해 정의 줄을 뽑는다.
(2) 6절이 예약한 글자(2–5장의 N, 1·4·11장의 t 등)가 수식 안에 낱글자로 나오는지 센다.
사용: python -I 검토전체6_L14_defs.py
"""
import re
from pathlib import Path

CH = Path(r"C:\math\임시\주차함수_증명\장v2")

DEFS = {
    "장7B": [r"\mathcal R_2", r"\mathcal W^{(>102)}", r"\mathfrak u_n", r"\Pi^{\mathrm{up}}_j"],
    "장8": [r"m_{\mathrm{fb}}", r"q_{\mathrm{fb}}", r"q^\circ_{\mathrm{fb}}", r"\mathrm{km}_N", r"\mathsf c_\Psi", r"\mathsf j_\infty", r"\mathfrak c_0"],
    "장10": [r"\mathrm{DDL}(k)", r"\mathrm{PM}_y(d)", r"\pi^{\mathrm{two}}_N", r"\mathsf r_\ast", r"d^\star", r"\mathsf f_1", r"\vartheta_0", r"m^\flat", r"\mathsf m_{\mathrm S}", r"\varkappa_m", r"\omega_m"],
    "장6": [r"\mathsf u(k)", r"\mathsf v(6667)", r"\mathsf v(6668)", r"s^{\mathrm F}(k,\nu)", r"\kappa_N", r"\mathsf s_{\mathrm B}", r"\mathrm{Bd}^{\mathrm V}_k", r"\varphi^\flat_k", r"\Upsilon_k", r"\hat\Upsilon_k", r"\mathfrak b_m", r"\mathfrak p_m", r"\mathrm{dec}_N"],
    "장9": [r"\mathsf h_N", r"\mathrm{flat}_k(t)", r"\mathsf L_\ast(6668)", r"\mathfrak d_k", r"\mathfrak l_m(t)", r"\gamma_m", r"K_n(m)", r"\nu_0(k)", r"\nu_1(k)", r"\pi_2(t)"],
    "장7A": [r"n^\sharp_k", r"\mathsf t_k", r"n_{\mathrm X}(k)", r"n^\flat_k", r"n^\circ_k", r"\mathfrak P_k(n)", r"\mathrm{pr}_{n,k}", r"\mathrm{pr}^\circ_n"],
    "장5B": [r"q_{\max}(Y)", r"\mathsf w_0", r"t_0(y)", r"\mathfrak z_m(d)"],
    "장5A": [r"r_0(n)", r"\mathfrak m(n)", r"\mathrm{rq}_r", r"\mathrm{rq}:="],
    "장4": [r"\mathsf a_j", r"\mathsf g_k", r"\mathsf n_k", r"V(x)", r"\mathcal I_k"],
    "장2": [r"\mathrm{nf}(n,d)", r"W_n(\gamma)", r"\mathrm{Ren}(j)", r"\Psi(q)", r"\theta_t(k)", r"\mathfrak v_k(Z,H)", r"\mathrm{Gr}(x)", r"J_n(z)"],
}

def main():
    for f, toks in DEFS.items():
        lines = (CH / f"{f}.md").read_text(encoding="utf-8").splitlines()
        for tok in toks:
            hit = None
            for i, ln in enumerate(lines, 1):
                j = ln.find(tok + ":=")
                if j < 0:
                    j = ln.find(tok + "=")
                if j < 0:
                    j = ln.find(tok + "\\ :=")
                if j >= 0:
                    hit = (i, ln[max(0, j - 10): j + 170])
                    break
            if hit is None:
                for i, ln in enumerate(lines, 1):
                    j = ln.find(tok)
                    if j >= 0:
                        hit = (i, "(첫 등장) " + ln[max(0, j - 30): j + 150])
                        break
            print(f"{f} | {tok} | {hit}")
    print("\n=== 예약 글자의 낱글자 사용(수식 안) ===")
    def count_plain(letter, f):
        t = (CH / f"{f}.md").read_text(encoding="utf-8")
        out = []
        for m in re.finditer(r"\$([^$]+)\$", t):
            body = m.group(1)
            for mm in re.finditer(r"(?<![A-Za-z\\])" + letter + r"(?![A-Za-z])", body):
                out.append(body[max(0, mm.start() - 25): mm.start() + 20])
        return out
    for f in ["장2", "장3", "장4", "장5A", "장5B"]:
        r = count_plain("N", f)
        print(f, "낱글자 N:", len(r), r[:4])
    for f in ["장1", "장4", "장11"]:
        r = count_plain("t", f)
        print(f, "낱글자 t:", len(r), r[:4])
    for f in ["장5A", "장5B", "장6", "장8", "장9", "장10"]:
        r = count_plain("a", f)
        print(f, "낱글자 a:", len(r), r[:4])

if __name__ == "__main__":
    main()
