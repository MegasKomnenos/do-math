# -*- coding: utf-8 -*-
"""시험 함수 Ω의 격자를 0≤i≤12927로 늘린 재실행이 통과한 뒤 적용한다. 8장과 D.37에서 상수 연장·도약·여유 문장을 걷어 내고,
격자 범위·결과·자료를 세션 재실행에 맞춘다. 멱등. 결과 수치는 실행 출력에서 읽어 인자로 받는다:
  python _fix_Omega_격자확장.py --cb-min 3.35 --cb-q 2999 --cb-x 0.919 --int-min 1.125 --int-x 0.912 --int1 1.555 --int2lo 1.83 --int2hi 2.20 --first 0.0394 --capture 0.729"""
import argparse
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
for k in ("cb_min", "cb_q", "cb_x", "int_min", "int_x", "int1", "int2lo", "int2hi", "first", "capture"):
    ap.add_argument("--" + k.replace("_", "-"), required=True)
ap.add_argument("--dry", action="store_true")
A = ap.parse_args()

SESS = "`원고_자료/세션_재계산/r030ffae_window/work/xKrig.npy`, `wKrig.npy`(격자 $0\\le i\\le12927$의 표), `NEW_cert_interval_0_16.out`, `NEW_cert_Cb_1_31.out`, `NEW_cert_Cb_31_1500.out`, `NEW_cert_Cb_1500_2250.out`, `NEW_cert_Cb_2250_3000.out`, `work/FIXED_cert_interval_result_0_16.json`, `work/FIXED_cert_Cb_result_1_31.json`, `work/FIXED_cert_Cb_result_31_1500.json`, `work/FIXED_cert_Cb_result_1500_2250.json`, `work/FIXED_cert_Cb_result_2250_3000.json`; 코드는 기록 `records/r030ffae…/evidence/peer/rerun/work/`의 사본"

EDITS = [
    # ---- 8장 본문: 격자 범위, Ω 정의(연장 없음), 도약 문장 삭제
    ("장v2/장8.md",
     r"$\mathsf K:=10^5$의 창 격자 $\xi^{\mathsf K}_i:=i/\mathsf K^{2/3}$($0\le i\le12926=\lfloor6\mathsf K^{2/3}\rfloor$)에서",
     r"$\mathsf K:=10^5$의 창 격자 $\xi^{\mathsf K}_i:=i/\mathsf K^{2/3}$($0\le i\le12927$; 마지막 점 $\xi^{\mathsf K}_{12927}=6.0002$가 $6$을 덮는다)에서", 1),
    ("장v2/장8.md",
     r"을 $[0,\xi^{\mathsf K}_{12926}]$에서 쓰고, $\xi^{\mathsf K}_{12926}=5.9997$ 오른쪽 $(5.9997,6]$에서는 마지막 표 값 $0.00229$로 상수 연장한 함수를 $\Omega$로 둔다. $\Omega$는 비증가 연속 함수이고 $5.9997$을 뺀 곳에서 $C^1$이며(그 점에서 $\Omega'$은 $-0.0020$에서 $0$으로 뛴다), $\Omega(0)=0.96$,",
     r"을 $\Omega$로 둔다. $\Omega$는 $[0,6]$에서 감소하는 $C^1$ 함수이고, $\Omega(0)=0.96$,", 1),
    ("장v2/장8.md",
     r" $5.9997$의 한 도약은 (나)의 셀 가운데 $[5.999,6]$ 하나에만 닿고, 거기서 남는 항은 도함수 경계에 $0.19$ 이하, 셀 폭 $0.001$을 곱해 $2\times10^{-4}$ 이하이며, 그 셀의 여유($2.9\times10^{-4}$ 이상)가 이를 덮는다(부록 D.{{D:window-mass-env}}).",
     r"", 1),
    # ---- D.37: 격자 범위, 연장 문장 삭제, 도약 확인 문장 삭제, 결과 수치, 자료
    ("장v2/부록D_장8.md",
     r"시험 함수 $\Omega$: $\mathsf K=10^5$의 격자 $\xi^{\mathsf K}_i=i/\mathsf K^{2/3}$($0\le i\le12926$)에서",
     r"시험 함수 $\Omega$: $\mathsf K=10^5$의 격자 $\xi^{\mathsf K}_i=i/\mathsf K^{2/3}$($0\le i\le12927$)에서", 1),
    ("장v2/부록D_장8.md",
     r"의 단조 3차 Hermite 보간으로 $[0,\xi^{\mathsf K}_{12926}]$에서 $\Omega$를 정의하고, $(\xi^{\mathsf K}_{12926},6]=(5.9997,6]$에서는 마지막 표 값으로 상수 연장한다(코드의 평가 함수가 마지막 구간의 끝값을 돌려준다). 보간 구간마다",
     r"의 단조 3차 Hermite 보간으로 $\Omega$를 정의한다. 보간 구간마다", 1),
    ("장v2/부록D_장8.md",
     r" 이 글을 쓰며 확인한 것: 상수 연장 때문에 $\Omega'$은 $5.9997$에서 $-0.0020$에서 $0$으로 뛰고, (나)의 셀 Lipschitz 경계(부분적분 꼴 $\int\tau\,d[\varsigma'|\Omega'|]$)는 이 도약의 원자 $5.9997\cdot0.0020=0.0123$을 넣지 않았다. 원자가 닿는 셀은 $[5.999,6]$ 하나이고 그 무게는 $\frac2\pi\cdot\frac1{5.999}\cdot(1-5.9997/6+1/J_i)^{-1/2}\le15.5$라 빠진 몫은 $15.5\cdot0.0123\cdot0.001<2\times10^{-4}$인데, 그 셀의 여유는 우변 $\ge6^{3/2}\cdot0.78\cdot0.00229=0.0262$의 $1.125\%$ 이상, 곧 $2.9\times10^{-4}$ 이상이다.",
     r" 이 글의 $\Omega$(격자 $0\le i\le12927$)에 대한 (가)·(나)의 검사는 이 글을 쓰며 같은 코드를 다시 돌린 것이고(" + SESS + r"), 표의 처음 $12927$개 값은 기록의 표와 비트 단위로 같다.", 1),
]

# 결과 줄: 수치가 바뀌었을 때만 교체(인자로 받은 값으로 재구성)
RESULT_OLD_HEAD = "**결과.** (가) $1\\le q\\le2999$ 전부 통과. 셀 최솟값의 우변 대비 상대 여유의 최솟값은 $q=2999$, $\\xi\\approx0.919$에서 $3.35\\%$이고,"
RESULT_NEW_HEAD = f"**결과.** (가) $1\\le q\\le2999$ 전부 통과. 셀 최솟값의 우변 대비 상대 여유의 최솟값은 $q={A.cb_q}$, $\\xi\\approx{A.cb_x}$에서 ${A.cb_min}\\%$이고,"
RESULT_OLD_TAIL = "(나) 열일곱 조건 모두 통과. 상대 여유의 최솟값은 $i=0$에서 $1.125\\%$($\\xi\\approx0.912$), $i=1$에서 $1.555\\%$, $i\\ge2$에서 $1.83$–$2.20\\%$이고 첫 셀 여유는 모두 $0.0394$ 이상이다. 포착된 창 질량 $\\int_0^6\\Omega(\\varsigma)\\sqrt{2\\varsigma/\\pi}\\,d\\varsigma\\approx0.729$."
RESULT_NEW_TAIL = f"(나) 열일곱 조건 모두 통과. 상대 여유의 최솟값은 $i=0$에서 ${A.int_min}\\%$($\\xi\\approx{A.int_x}$), $i=1$에서 ${A.int1}\\%$, $i\\ge2$에서 ${A.int2lo}$–${A.int2hi}\\%$이고 첫 셀 여유는 모두 ${A.first}$ 이상이다. 포착된 창 질량 $\\int_0^6\\Omega(\\varsigma)\\sqrt{{2\\varsigma/\\pi}}\\,d\\varsigma\\approx{A.capture}$."


def main():
    texts = {}
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel) or io.open(p, encoding="utf-8").read()
        n = s.count(old)
        if n == 0:
            if new and new in s:
                print(f"{rel}: 이미 반영 — {old[:40]}")
                texts[rel] = s
                continue
            print(f"{rel}: 원문 없음 — {old[:70]}")
            sys.exit(1)
        if n != expect:
            print(f"{rel}: 횟수 {n}≠{expect} — {old[:60]}")
            sys.exit(1)
        texts[rel] = s.replace(old, new)
        print(f"{rel}: {n}곳 — {old[:48]}")
    rel = "장v2/부록D_장8.md"
    s = texts[rel]
    for old, new in ((RESULT_OLD_HEAD, RESULT_NEW_HEAD), (RESULT_OLD_TAIL, RESULT_NEW_TAIL)):
        if old in s:
            s = s.replace(old, new)
            print(f"{rel}: 결과 수치 갱신" if old != new else f"{rel}: 결과 수치 동일")
        elif new not in s:
            print(f"{rel}: 결과 줄 앵커 없음 — {old[:50]}")
            sys.exit(1)
    texts[rel] = s
    if A.dry:
        print("(dry) 쓰지 않음")
        return
    for rel, s in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", ", ".join(texts))


if __name__ == "__main__":
    main()
