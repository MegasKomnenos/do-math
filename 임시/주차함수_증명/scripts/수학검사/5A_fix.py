# -*- coding: utf-8 -*-
"""수학 검사(태그 5A) 수정 스크립트. 멱등. 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.

python -I scripts/수학검사/5A_fix.py
"""
import io, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T_CH = os.path.join(ROOT, '장v2', '장5A.md')
T_AP = os.path.join(ROOT, '장v2', '부록D_장5A.md')

# (대상 파일, 앵커, 치환). 원시 문자열로 적는다.
EDITS = [
    # [1] 장5A 495행(5.2.3절, 보조정리 {{5:kernel-C-bound}} 뒤의 비고). 기준 판 478행은 「$C$의 상계」.
    # 뒤의 인증(674행)은 이 보조정리에서 $C$의 상계를, (K1)에서 $C$의 하계를 쓰므로
    # 이 보조정리의 경계 가운데 뒤의 인증에 드는 것은 상계다. 첨삭이 바꾼 「하계」를 되돌린다.
    (T_CH,
     r"$C$의 하계와 $\mathfrak E$의 양쪽 경계를 더 좁히면",
     r"$C$의 상계와 $\mathfrak E$의 양쪽 경계를 더 좁히면"),
    # [2] 부록 D.{{D:newton-m170}} 54행. 경계 응답 다항식의 인수 글자를 장부 1절(137행) $\Gamma_d(\ell;n)$으로 통일.
    #     4.2절(장4 53·55행)의 정의 재귀는 $\Gamma_d(\ell;n)=\binom nd p_d+\ell\sum\dots\Gamma_{d-1-j}(\ell;n)$.
    (T_AP,
     r"$\Gamma_d(y;n)$은 4.2절의 정의 재귀 $\Gamma_d(y;n)=\binom ndp_d+y\sum_{j=0}^{d-1}\binom{n-d+j}{j}p_j\Gamma_{d-1-j}(y;n)$, $\Gamma_0=1$로",
     r"$\Gamma_d(\ell;n)$은 4.2절의 정의 재귀 $\Gamma_d(\ell;n)=\binom ndp_d+\ell\sum_{j=0}^{d-1}\binom{n-d+j}{j}p_j\Gamma_{d-1-j}(\ell;n)$, $\Gamma_0=1$로"),
    # [3] 같은 행, 보조정리 {{5:inverse-renewal}}의 정규화 재귀 인용. 같은 항목 안에서 인수 글자를 맞춘다.
    (T_AP,
     r"$\mathrm{fs}'_d=(1+\frac y{n-d+1})\mathrm{fs}'_{d-1}+\sum_{j=2}^{d}\mathrm{tw}_j\mathrm{fs}'_{d-j}$, $\mathrm{fs}'_0=1$로 $\mathrm{fs}'_d=\Gamma_d(y;n)/(n)_d$를 구한 뒤 $\Gamma_d(y;n)=(n)_d\,\mathrm{fs}'_d$로",
     r"$\mathrm{fs}'_d=(1+\frac \ell{n-d+1})\mathrm{fs}'_{d-1}+\sum_{j=2}^{d}\mathrm{tw}_j\mathrm{fs}'_{d-j}$, $\mathrm{fs}'_0=1$로 $\mathrm{fs}'_d=\Gamma_d(\ell;n)/(n)_d$를 구한 뒤 $\Gamma_d(\ell;n)=(n)_d\,\mathrm{fs}'_d$로"),
    # [4] 부록 D.{{D:critical-window-rig}} 142행. cert/A00.json의 셀 [9.8,10] B0=[0.0060986, 0.0067870].
    #     둘러싸기의 아래 끝 0.0061은 참 둘러싸기 0.0060986보다 커서 「∈」가 성립하지 않는다. 바깥 반올림 0.0060으로.
    (T_AP,
     r"$\Upsilon_{B,0}\in[0.0061,0.0068]$",
     r"$\Upsilon_{B,0}\in[0.0060,0.0068]$"),
    # [5] 장5A 712행(5.4절 머리). 조정자 추가 과제: 5.4절의 $\mathrm{rq}:=r/n$ 정의가 5.2.3절의 $\mathrm{rq}_r=(r+3)/n$과
    #     다른 양임이 드러나게 적는다. 정의 자체는 이미 712행에 있으므로(첫 쓰임 732행보다 앞) 중복하지 않고 괄호만 덧붙인다.
    #     부록 A 159행·장부 1.3절 381행 「5.4절부터 $\mathrm{rq}:=r/n$」과 일치.
    (T_CH,
     r"이 절에서는 $\mathrm{rq}:=r/n$으로 적고, 5.2절의 $\mathfrak s=\sqrt r$과",
     r"이 절에서는 $\mathrm{rq}:=r/n$으로 적고(5.2.3절의 $\mathrm{rq}_r=(r+3)/n$과 다른 양이다), 5.2절의 $\mathfrak s=\sqrt r$과"),
]


def main():
    texts = {}
    changed = {}
    for i, (tgt, old, new) in enumerate(EDITS, 1):
        if tgt not in texts:
            texts[tgt] = io.open(tgt, encoding='utf-8').read()
            changed[tgt] = 0
        text = texts[tgt]
        n_old = text.count(old)
        n_new = text.count(new)
        if n_old == 0 and n_new == 1:
            print(f"[{i}] 이미 적용됨")
            continue
        if n_old != 1:
            print(f"[{i}] 앵커가 {n_old}번 나타남 — 건너뜀", file=sys.stderr)
            continue
        texts[tgt] = text.replace(old, new)
        changed[tgt] += 1
        print(f"[{i}] 치환함 ({os.path.basename(tgt)})")
    for tgt, text in texts.items():
        if changed[tgt]:
            io.open(tgt, 'w', encoding='utf-8', newline='\n').write(text)
        print(f"{os.path.basename(tgt)}: 치환 {changed[tgt]}건")


if __name__ == '__main__':
    main()
