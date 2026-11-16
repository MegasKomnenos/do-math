# -*- coding: utf-8 -*-
"""용어 통일(결정 95) 후속 — (1) 상계·하계 뜻의 「경계」가 든 진술 머리 23개의 이름 변경(본문 머리, 부록 C 이름 표, 장부_v2 4절의
「이 글의 이름」 칸, 이름을 인용한 산문·요약, 부록 D 절 머리 셋), (2) 부록D_장7A의 합 지표 묶음 「블록」→「묶음」(수식
`\\sum_{\\text{블록}}` 여섯 자리의 글자 변경을 이 파일에 한해 허용받음), README 523행 「블록 가중」→「묶음 가중」,
의존지도 58행 「한 블록 꼴」→「한 나무 꼴」(장부 1134행의 현재 이름). 멱등. 보고: 대조v2/수학검사2/보고_용어.md 6절.
실행: python -I scripts/수학검사2/용어_fix2.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 진술 머리 이름: (라벨, 옛 이름, 새 이름, 방향 판정 근거)
HEADS = [
    ("4:gauss-coeff", "Gauss 계수의 경계", "Gauss 계수의 상하계", "(가) $\\mathcal M_0\\ge$, (나)(다) 양측, (라) $\\le$"),
    ("5:kernel-C-bound", "갱신 핵과 그 도함수 핵의 양측 경계", "갱신 핵과 그 도함수 핵의 상하계", "양측"),
    ("5:kernel-bounds", "갱신 핵의 좁은 계수 경계 (K1)(K2)", "갱신 핵의 좁은 계수 상하계 (K1)(K2)", "(K1) $C$ 하계, (K2) $\\mathfrak E$ 양측"),
    ("5:kernel-sandwich", "방문 핵의 대수적 포락선과 Wallis 경계", "방문 핵의 대수적 포락선과 Wallis 상하계", "(나) 양측"),
    ("5:stirling-bor", "Borel 질량과 Borel 꼬리의 양측 경계", "Borel 질량과 Borel 꼬리의 상하계", "양측"),
    ("5:stop-lower", "쪼개짐 확률의 양측 경계", "쪼개짐 확률의 상하계", "양측"),
    ("5:old-5-40", "Gauss 계수의 균일 경계", "Gauss 계수의 균일 상하계", "명시 구간 $[I^{\\mathrm{lo}},I^{\\mathrm{hi}}]$"),
    ("5:old-5-41", "두 보정의 균일 경계", "두 보정의 균일 상하계", "$\\mathsf b_D$ 하계·$\\mathsf b_J$ 상계"),
    ("6:lemma-phi", "머묾 여유 보조 항의 경계", "머묾 여유 보조 항의 하계", "$\\mathrm{Mg}_y(d,q)\\ge0$"),
    ("6:lemma-ell", "이웃비 로그의 Taylor 경계", "이웃비 로그의 Taylor 상하계", "세 식 모두 양측"),
    ("6:lemma-N", "가중치 상수의 경계", "가중치 상수의 상계", "$\\le$ 하나"),
    ("6:theorem-D", "결손 갱신 항등식과 임계 창 수준 질량의 양측 경계", "결손 갱신 항등식과 임계 창 수준 질량의 상하계", "양측"),
    ("7:fourier-lemmas", "단위원 위의 해석성과 도함수 경계", "단위원 위의 해석성과 도함수 상계", "(마)(바) 절댓값의 $\\le$"),
    ("7:lemma-P-pole", "고정된 열의 단일 극 경계", "고정된 열의 단일 극 상계", "오차 $|\\mathfrak a^\\rho_m-1/\\mathfrak m_\\Pi|$의 상계"),
    ("7:lemma-P-prime", "원 위의 감김수로 얻는 단일 극 경계", "원 위의 감김수로 얻는 단일 극 상계", "(나) 오차의 상계"),
    ("7:hermite-nu", "Hermite 계수의 $\\nu$-일반 경계", "Hermite 계수의 $\\nu$-일반 상하계", "(가) 양측·(다) 하계·(라) 식"),
    ("7:vertical-nu", "수직선 윤곽의 $\\nu$-일반 경계", "수직선 윤곽의 $\\nu$-일반 상하계", "$\\mathsf b_D$ 하계·$\\mathsf b_J$ 상계"),
    ("7:explicit-bounds", "뿌리 법칙과 결합의 명시 경계", "뿌리 법칙과 결합의 명시 상하계", "(가) 양측, (나) 상계, (다) 하계, (라)(마) 상계"),
    ("8:explicit-bounds", "명시 경계", "명시 상하계", "아래·위 경계(126행)"),
    ("8:large-q-bounds", "큰 $q$의 단조 경계", "큰 $q$의 단조 상하계", "왼쪽 이상·오른쪽 이하(527행)"),
    ("8:cell-bound", "셀 경계", "셀 하계", "$\\Phi(\\varsigma)\\ge\\min(\\cdots)-\\Upsilon\\mathfrak l/4$"),
    ("9:prop-6", "결손 수준 질량의 명시적 양측 경계", "결손 수준 질량의 명시적 상하계", "양측"),
    ("9:psi-two-sided", "Borel 갱신함수의 양측 경계", "Borel 갱신함수의 상하계", "위아래에서 막힘(187행)"),
]
CHAP = {"4": "장4", "5": None, "6": "장6", "7": None, "8": "장8", "9": "장9"}
FILE_OF = {"4:gauss-coeff": "장4", "5:kernel-C-bound": "장5A", "5:kernel-bounds": "장5A", "5:kernel-sandwich": "장5A",
           "5:stirling-bor": "장5B", "5:stop-lower": "장5B", "5:old-5-40": "장5B", "5:old-5-41": "장5B",
           "6:lemma-phi": "장6", "6:lemma-ell": "장6", "6:lemma-N": "장6", "6:theorem-D": "장6",
           "7:fourier-lemmas": "장7A", "7:lemma-P-pole": "장7A", "7:lemma-P-prime": "장7A",
           "7:hermite-nu": "장7B", "7:vertical-nu": "장7B", "7:explicit-bounds": "장7B",
           "8:explicit-bounds": "장8", "8:large-q-bounds": "장8", "8:cell-bound": "장8",
           "9:prop-6": "장9", "9:psi-two-sided": "장9"}

EDITS = []
for label, old, new, why in HEADS:
    # 본문 머리: "{{라벨}} (옛 이름" → "{{라벨}} (새 이름"
    EDITS.append((f"장v2/{FILE_OF[label]}.md", "{{" + label + "}} (" + old, "{{" + label + "}} (" + new, "머리", why))
    # 장부 4절: "| 옛 이름 | ... | {{라벨}} |" — 이름 칸은 셋째 칸
    EDITS.append(("장부_v2.md", "| " + old + " | ", "| " + new + " | ", "장부 4절", label))
    # 부록 C 이름 표(기록 이름이 있는 진술만 행이 있음): "| 종류 {{라벨}} | 옛 이름 |"
    EDITS.append(("장v2/부록C.md", "{{" + label + "}} | " + old + " |", "{{" + label + "}} | " + new + " |", "부록 C 이름 표", label))

OPTIONAL = {"장v2/부록C.md"}  # 앵커가 없으면 건너뛰는 파일(부록 C 이름 표에 행이 없는 진술)

EDITS += [
    # ---- 이름을 인용한 산문·요약·절 머리 ----
    ("장v2/장8.md", "셀 안의 변동을 빼는 셀 경계로 덮는다.", "셀 안의 변동을 빼는 셀 하계로 덮는다.", "산문", "503행; cell-bound 이름 도입"),
    ("장v2/장8.md", "큰 초과의 단조 경계와 셀 경계를 합치면", "큰 초과의 단조 상하계와 셀 하계를 합치면", "산문", "509행; 두 이름 인용"),
    ("장v2/장8.md", "(나)의 셀 경계에서 도함수가 도약하면", "(나)의 셀 하계에서 도함수가 도약하면", "산문", "537행"),
    ("장v2/장8.md", "큰 $q$에서 셀 경계가 쓸모없어진다.", "큰 $q$에서 셀 하계가 쓸모없어진다.", "산문", "541행"),
    ("장v2/부록D_장5A.md", "두 Bernstein 부호 인증: 핵 계수 경계의 두 다항식과", "두 Bernstein 부호 인증: 핵 계수 상하계의 두 다항식과", "절 머리", "90행; kernel-bounds"),
    ("장v2/부록D_장5A.md", "핵 계수 경계의 원형은", "핵 계수 상하계의 원형은", "산문", "106행"),
    ("장v2/부록D_장5B.md", "두 보정 경계의 계수 생성 알고리즘", "두 보정 상하계의 계수 생성 알고리즘", "절 머리", "137행; old-5-41"),
    ("장v2/부록D_장6.md", "임계 창 수준 질량 양측 경계의 기저", "임계 창 수준 질량 상하계의 기저", "절 머리", "13행; theorem-D"),
    ("구조표_v2.md", "$C$·$E$의 양측 경계 [r7798355]", "$C$·$E$의 상하계 [r7798355]", "요약", "59행; kernel-C-bound"),
    ("구조표_v2.md", "핵 계수 경계 (K1)(K2) [r690be93]", "핵 계수 상하계 (K1)(K2) [r690be93]", "요약", "59행; kernel-bounds"),
    ("구조표_v2.md", "단일 극 경계 보조정리 P §6.4", "단일 극 상계 보조정리 P §6.4", "요약", "85행; lemma-P-pole"),
    ("구조표_v2.md", "보조정리 r·Sh·H·H′·명시 경계 여섯·정리 V″", "보조정리 r·Sh·H·H′·명시 상하계 여섯·정리 V″", "요약", "88행; explicit-bounds"),
    ("의존지도_v2.md", "명시 유한 경계(보조정리 H;", "명시 유한 상하계(보조정리 H;", "요약", "80행; gauss-coeff"),
    ("의존지도_v2.md", "수직선 윤곽 명시 경계(보조정리 V;", "수직선 윤곽 명시 상하계(보조정리 V;", "요약", "82행"),
    ("의존지도_v2.md", "C·E의 양측 경계: aq_−≼C≼aq_+", "C·E의 상하계: aq_−≼C≼aq_+", "요약", "107행"),
    ("의존지도_v2.md", "갱신 핵 도함수의 계수 경계 (K1)(K2)와", "갱신 핵 도함수의 계수 상하계 (K1)(K2)와", "요약", "108행"),
    ("의존지도_v2.md", "단항식 계수의 Wallis 경계", "단항식 계수의 Wallis 상하계", "요약", "127행"),
    ("의존지도_v2.md", "| Gauss 계수의 균일 경계; 기록 [r5f5cf73]", "| Gauss 계수의 균일 상하계; 기록 [r5f5cf73]", "요약", "156행"),
    ("의존지도_v2.md", "| 두 보정의 균일 경계; 기록 [r5f5cf73]", "| 두 보정의 균일 상하계; 기록 [r5f5cf73]", "요약", "157행"),
    ("의존지도_v2.md", "정리 D(임계 창 결손 확률의 명시 경계)", "정리 D(임계 창 결손 확률의 명시 상하계)", "요약", "172행"),
    ("의존지도_v2.md", "보조정리 P(명시 단일 극 경계)", "보조정리 P(명시 단일 극 상계)", "요약", "210행"),
    ("장부_v2.md", "FKG 보조정리의 양, 핵 계수 경계 (K1)(K2),", "FKG 보조정리의 양, 핵 계수 상하계 (K1)(K2),", "장부 7절", "380행; kernel-bounds"),
    ("장부_v2.md", "(셀 경계 보조정리의 구간 끝", "(셀 하계 보조정리의 구간 끝", "장부 7절", "404행; cell-bound"),
    ("장부_v2.md", "두 보조정리(Gauss 계수·두 보정의 균일 경계) 증명의", "두 보조정리(Gauss 계수·두 보정의 균일 상하계) 증명의", "장부 6절", "386행; old-5-40·41"),
    ("장부_v2.md", "보조정리 r·Sh·H·H′, 명시 경계 여섯, 정리 V″", "보조정리 r·Sh·H·H′, 명시 상하계 여섯, 정리 V″", "장부 7절", "401행; explicit-bounds"),
    # ---- 부록D_장7A 합 지표 묶음 「블록」→「묶음」 ----
    ("장v2/부록D_장7A.md", "블록 괄호: 정수 블록 $[\\mathfrak n_1,\\mathfrak n_2]$ 위에서", "묶음 괄호: 정수 묶음 $[\\mathfrak n_1,\\mathfrak n_2]$ 위에서", "묶음", "98행"),
    ("장v2/부록D_장7A.md", "$\\varsigma>0$에서는 블록 괄호;", "$\\varsigma>0$에서는 묶음 괄호;", "묶음", "98행"),
    ("장v2/부록D_장7A.md", "$i\\le24$는 $\\mathfrak t$-블록 괄호.", "$i\\le24$는 $\\mathfrak t$-묶음 괄호.", "묶음", "98행"),
    ("장v2/부록D_장7A.md", "를 블록 $[\\mathfrak n_1,\\mathfrak n_2]$와 $\\theta$-셀에서", "를 묶음 $[\\mathfrak n_1,\\mathfrak n_2]$와 $\\theta$-셀에서", "묶음", "98행"),
    ("장v2/부록D_장7A.md", "에서 블록 괄호로 상·하계되며", "에서 묶음 괄호로 상·하계되며", "묶음", "100행"),
    ("장v2/부록D_장7A.md", "(4)의 블록 괄호와 해석적", "(4)의 묶음 괄호와 해석적", "묶음", "104행"),
    ("장v2/부록D_장7A.md", "블록 괄호 `asym_iv.py`", "묶음 괄호 `asym_iv.py`", "묶음", "114행"),
    ("장v2/부록D_장7A.md", "$m$을 $40$부터 비 $1.02$의 기하 블록으로 묶어(그 아래는 항별로)", "$m$을 $40$부터 비 $1.02$의 기하 급수 묶음으로 나누어(그 아래는 항별로)", "묶음", "133행; 「묶음으로 묶어」를 피해 「나누어」"),
    ("장v2/부록D_장7A.md", "$i$-합의 블록: $i\\in[", "$i$-합의 묶음: $i\\in[", "묶음", "135행"),
    ("장v2/부록D_장7A.md", "그 위는 $k_1-i$의 비 $1.005$ 기하 블록.", "그 위는 $k_1-i$의 비 $1.005$ 기하 급수 묶음.", "묶음", "135행"),
    ("장v2/부록D_장7A.md", "(ㅅ) $i$-블록과 $\\mathcal J$(", "(ㅅ) $i$-묶음과 $\\mathcal J$(", "묶음", "150행"),
    ("장v2/부록D_장7A.md", "블록 경계는 $e_0=1$,", "묶음 경계는 $e_0=1$,", "묶음", "150행(「경계」는 가장자리 뜻)"),
    ("장v2/부록D_장7A.md", "마지막 $e=k_1$; 블록은 $[\\mathfrak n_1,\\mathfrak n_2]=[e_j,e_{j+1}-1]$.", "마지막 $e=k_1$; 묶음은 $[\\mathfrak n_1,\\mathfrak n_2]=[e_j,e_{j+1}-1]$.", "묶음", "150행"),
    ("장v2/부록D_장7A.md", "(ㄱ) $m$-블록: $e_0=40$,", "(ㄱ) $m$-묶음: $e_0=40$,", "묶음", "179행"),
    ("장v2/부록D_장7A.md", "블록 $[\\mathfrak n_1,\\mathfrak n_2]=[e_j,e_{j+1}-1]$, 마지막 블록은 $[e_{n-1},k_1]$.", "묶음 $[\\mathfrak n_1,\\mathfrak n_2]=[e_j,e_{j+1}-1]$, 마지막 묶음은 $[e_{n-1},k_1]$.", "묶음", "179행"),
    ("원고_자료/README.md", "$\\varkappa(\\theta)$, 블록 가중, $\\eta$의 뺄셈", "$\\varkappa(\\theta)$, 묶음 가중, $\\eta$의 뺄셈", "묶음", "523행"),
    # ---- 장2 이름 ----
    ("의존지도_v2.md", "| 명제 2.42 | 한 블록 꼴; 기록 [r5909c9e]", "| 명제 2.42 | 한 나무 꼴; 기록 [r5909c9e]", "장2 이름", "58행; 장부 1134행 「한 나무 꼴」"),
]

# 수식 안 글자 변경(허용받은 자리에 한함): 부록D_장7A 152·177·183행의 \sum_{\text{블록}} 여섯
MATH_GLOBAL = [("장v2/부록D_장7A.md", "\\sum_{\\text{블록}}", "\\sum_{\\text{묶음}}", 6)]


def rd(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def wr(rel, s):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as f:
        f.write(s)


def main():
    applied = skipped = 0
    for rel, old, new, kind, why in EDITS:
        s = rd(rel)
        n_old, n_new = s.count(old), s.count(new)
        if n_new >= 1:
            skipped += 1
            continue
        if n_old == 0 and rel in OPTIONAL:
            continue
        if n_old != 1:
            print(f"[중단] {rel}: 앵커가 {n_old}번 나타남({kind}; {why}): {old[:70]}")
            sys.exit(1)
        wr(rel, s.replace(old, new))
        applied += 1
        print(f"[적용 {kind}] {rel}: {why}: {old[:45]} -> {new[:45]}")
    for rel, old, new, expect in MATH_GLOBAL:
        s = rd(rel)
        n_old, n_new = s.count(old), s.count(new)
        if n_old == 0 and n_new >= expect:
            skipped += 1
            continue
        if n_old != expect:
            print(f"[중단] {rel}: 「{old}」 {n_old}회(예상 {expect})")
            sys.exit(1)
        wr(rel, s.replace(old, new))
        applied += n_old
        print(f"[적용 수식] {rel}: 「{old}」→「{new}」 {n_old}회")
    print(f"적용 {applied}, 이미 적용 {skipped}")


if __name__ == "__main__":
    main()
