# -*- coding: utf-8 -*-
"""8차 YD의 부록 D 이름 정리(「층 B·A-int·A″」→「범위 1–5」, 「(A3)·(A5)」→「두 범위」, $u_{top}$→$\\mathrm{ku}_{top}$)를
README 세션 재계산 설명문과 패치 스크립트 PARAS에 반영한다. 2026-11-15."""
import io, os
ROOT = r"C:\math\임시\주차함수_증명"


def sub(rel, pairs, must=True):
    path = os.path.join(ROOT, rel)
    s = io.open(path, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        if must:
            assert n == 1, (rel, a[:70], n)
        elif n == 0:
            print("  (없음)", rel, a[:50]); continue
        s = s.replace(a, b)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", rel)


X = [
    ("다섯 층 인증 항목을 binary64 사전 오차 해석", "다섯 범위 인증 항목을 binary64 사전 오차 해석"),
    ("점근 층의 식은 `asym_iv.py`", "점근 범위의 식은 `asym_iv.py`"),
    ("층별 실행은 `layerB.py`(층 B $[501,5000]$", "범위별 실행은 `layerB.py`(범위 1 $[501,5000]$"),
    ("`layerAint.py`(A-int $[5000,10^5]$", "`layerAint.py`(범위 2 $[5000,10^5]$"),
    ("`layerA1.py`(A″-1), `layerA2.py`(A″-2), `layerA3.py`(A″-3)이고",
     "`layerA1.py`(범위 3), `layerA2.py`(범위 4), `layerA3.py`(범위 5)이고(파일 이름의 B·Aint·A1–A3은 기록의 실행 이름)"),
    ("층별 성공 구간의 합집합이", "범위별 성공 구간의 합집합이"),
    ("(다섯 층 전부 통과, 최대 $R_U$", "(다섯 범위 전부 통과, 최대 $R_U$"),
]
M_readme = [
    ("모멘트 판정 항목 (ㄱ)(재귀 (A3)·(A5)의 인증)을 구간 산술로",
     "모멘트 판정 항목 (ㄱ)(두 범위의 재귀 인증)을 구간 산술로"),
    ("이 (A1)–(A5) 7619열 60,703,015개 위치에서 전부 통과했고",
     "이 기록의 다섯 실행 A1–A5(글이 쓰는 두 범위는 A3·A5이고, A1·A2는 어느 장도 쓰지 않는 추가 계산이다) 7619열 60,703,015개 위치에서 전부 통과했고"),
]
M_script = [
    ("모멘트 판정 항목 (ㄱ)(재귀 (A1)–(A5)의 인증)을 구간 산술로",
     "모멘트 판정 항목 (ㄱ)(두 범위의 재귀 인증; 파일·요약의 A1–A5는 기록의 실행 이름이고 글이 쓰는 두 범위는 A3·A5다)을 구간 산술로"),
]
U = [
    (r"`verify_exact_cover.py`는 저장된 인증서만 읽어 $u$ 타일링과 $u_{\mathrm{top}}^3\cdot10001\ge1$",
     r"`verify_exact_cover.py`는 저장된 인증서만 읽어 $\mathrm{ku}$ 타일링과 $\mathrm{ku}_{\mathrm{top}}^3\cdot10001\ge1$"),
]
U_script = [(a.replace("\\", "\\\\"), b.replace("\\", "\\\\")) for a, b in U]

sub(r"원고_자료\README.md", X + M_readme + U)
sub(r"scripts\_patch_README_세션파일.py", X + M_script + U_script)
