# -*- coding: utf-8 -*-
"""수학 검사(태그 8): 장v2/장8.md·장v2/부록D_장8.md의 틀린 토큰을 앵커 치환으로 고친다. 멱등.
각 앵커는 파일 안에서 정확히 한 번 나타날 때만 치환하고, 이미 치환된 꼴이 한 번 있으면 건너뛴다.
실행: python -I scripts/수학검사/8_fix.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (파일, 앵커(전), 치환(후), 근거)
EDITS = [
    # --- theta 기호 통일: 8장의 theta_N(m) (크기 N 숲)은 2.9절 보조정리 {{2:old-2-37}}(마)의 theta_{N+1}(m) (크기 N+1 나무) ---
    ("장v2/장8.md",
     r"$\theta_N(m):=(N+1-m)\pi_N(m)=\mathrm{Bor}(m)\mathrm{Ren}(N+1-m)/\mathrm{Bor}(N+1)$로 두면",
     r"$\theta_{N+1}(m)=(N+1-m)\pi_N(m)=\mathrm{Bor}(m)\mathrm{Ren}(N+1-m)/\mathrm{Bor}(N+1)$로 두면",
     "장부 163행·2.9절 보조정리 {{2:old-2-37}}(마): theta_t(k)=Ren(t-k)Bor(k)/Bor(t); t=N+1, k=m. 재정의(:=)가 아니라 등식(=)"),
    ("장v2/장8.md",
     r"\mathbb E_N[\mathcal A]=\sum_{j=1}^{N-y}j\,\theta_N(y+j)",
     r"\mathbb E_N[\mathcal A]=\sum_{j=1}^{N-y}j\,\theta_{N+1}(y+j)",
     "같은 통일 (8.8)"),
    ("장v2/장8.md",
     r"1-s_N(y)=\sum_{m=y+1}^N\theta_N(m)\,\frac{m-y}{m}\,s_{m-1}(y).",
     r"1-s_N(y)=\sum_{m=y+1}^N\theta_{N+1}(m)\,\frac{m-y}{m}\,s_{m-1}(y).",
     "같은 통일 (8.10)"),
    ("장v2/장8.md",
     r"그 계수가 $\theta_N(m)$이다. ∎",
     r"그 계수가 $\theta_{N+1}(m)$이다. ∎",
     "같은 통일 (8.10) 증명 끝"),
    ("장v2/장8.md",
     r"사슬 위에 있을 확률 $\theta_N(m)$,",
     r"사슬 위에 있을 확률 $\theta_{N+1}(m)$,",
     "같은 통일; 2.9절 †의 확률 해석(t<=2k)은 N+1<=2y+2<=2m에서 성립"),
    ("장v2/장8.md",
     r"$\mathfrak B_N:=\sum_{m=y+1}^N\theta_N(m)\frac{m-y}m$으로 두면",
     r"$\mathfrak B_N:=\sum_{m=y+1}^N\theta_{N+1}(m)\frac{m-y}m$으로 두면",
     "같은 통일 (명제 prop-U-apriori (가))"),
    ("장v2/장8.md",
     r"(나) $\theta_N(m)=\mathrm{Bor}(m)\mathrm{Ren}(N+1-m)/\mathrm{Bor}(N+1)\ge\mathrm{Ren}(N+1-m)$",
     r"(나) $\theta_{N+1}(m)=\mathrm{Bor}(m)\mathrm{Ren}(N+1-m)/\mathrm{Bor}(N+1)\ge\mathrm{Ren}(N+1-m)$",
     "같은 통일 (명제 prop-U-apriori 증명 (나))"),
    ("장v2/장8.md",
     r"\sum_{j=1}^{q-1}j\,\theta_{k+q}(k+1+j)$에서 $\theta_{k+q}(k+1+j)=\mathrm{Bor}(k+1+j)\mathrm{Ren}(q-j)/\mathrm{Bor}(k+1+q)$",
     r"\sum_{j=1}^{q-1}j\,\theta_{k+q+1}(k+1+j)$에서 $\theta_{k+q+1}(k+1+j)=\mathrm{Bor}(k+1+j)\mathrm{Ren}(q-j)/\mathrm{Bor}(k+1+q)$",
     "같은 통일; N=k+q이므로 첨자 N+1=k+q+1; Ren(k+q+1-(k+1+j))=Ren(q-j)"),
    # --- 숫자 토큰: 7.429e-4 * 0.0004999 = 3.71376e-7 이므로 '>3.714e-7'은 거짓, '>3.713e-7'이 참 ---
    ("장v2/장8.md",
     r"\mathsf r_{\mathrm G}\min_iw_i\ge7.429\cdot10^{-4}\cdot0.0004999>3.714\cdot10^{-7}",
     r"\mathsf r_{\mathrm G}\min_iw_i\ge7.429\cdot10^{-4}\cdot0.0004999>3.713\cdot10^{-7}",
     "직접 계산 3.7137571e-7; eta*=3.71e-7 <= 3.713e-7은 그대로 성립"),
    # --- 기호 충돌: 부록 D 꼬리 상자의 nu/k 끝점 theta_+ -> 8장의 nu/k 글자 mathfrak z (장부 406행; 충돌 표 1179행 theta' 금지) ---
    ("장v2/부록D_장8.md",
     r"$a=\theta_+/(1+\theta_+)+3/k_{\mathrm{last}}$",
     r"$a=\mathfrak z_+/(1+\mathfrak z_+)+3/k_{\mathrm{last}}$",
     "장부 406행 8장의 nu/k 글자는 mathfrak z; 1179행 theta'(nu/k) 금지; 8장의 theta는 2.9절 theta_t(k)"),
]


def main():
    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    done = skipped = 0
    for rel, old, new, why in EDITS:
        p = os.path.join(ROOT, rel)
        s = io.open(p, encoding="utf-8").read()
        c_old, c_new = s.count(old), s.count(new)
        if c_old == 0 and c_new == 1:
            skipped += 1
            print(f"[이미 적용] {rel}: {new[:60]}", file=out)
            continue
        if c_old != 1:
            print(f"[건너뜀: 앵커 {c_old}회] {rel}: {old[:80]}", file=out)
            continue
        s = s.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        done += 1
        ln = s.count("\n", 0, s.find(new)) + 1
        print(f"[적용] {rel}:{ln}  {old[:50]} -> {new[:50]}  ({why[:60]})", file=out)
    print(f"적용 {done}, 이미 적용 {skipped}, 총 {len(EDITS)}", file=out)
    out.flush()


if __name__ == "__main__":
    main()
