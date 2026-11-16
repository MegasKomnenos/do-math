# -*- coding: utf-8 -*-
"""8차 Y8-1(hazard-H1 앞 인자 삭제) 뒤 D.band-boxes (ㄱ)(ㄴ) 재계산 값을 세션 소유 파일에 반영하고,
Y4의 「소구간」→「셀」을 README 설명문(패치 스크립트)에 반영한다. 2026-11-15."""
import io, os
ROOT = r"C:\math\임시\주차함수_증명"


def sub(rel, pairs):
    path = os.path.join(ROOT, rel)
    s = io.open(path, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        assert n == 1, (rel, a[:70], n)
        s = s.replace(a, b)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", rel)


sub(r"scripts\_재실행표_여유.json", [
    (r"(ㄱ) $1.0091268$ 대 문턱 $1.009$(상자 하계 최솟값; 문턱 대비 $0.0126\\%$, 보증이 쓰는 $1$ 대비 $0.913\\%$)",
     r"(ㄱ) $1.0097628$ 대 문턱 $1.009$(상자 하계 최솟값; 문턱 대비 $0.0756\\%$, 보증이 쓰는 $1$ 대비 $0.976\\%$)"),
])
sub(r"scripts\_gen_재실행표.py", [
    ('expect="최솟값 (ㄱ) $1.0091268$, (ㄴ) $1.0066914$, (ㄷ) $1.0136495$, (ㄹ) $1.0091044$; 꼬리 (ㄱ) $1.12224$"',
     'expect="최솟값 (ㄱ) $1.0097628$, (ㄴ) $1.0068936$, (ㄷ) $1.0136495$, (ㄹ) $1.0091044$; 꼬리 (ㄱ) $1.12224$"'),
    ('time="프로세스 2개로 각 $340$초에서 $430$초, 꼬리 각 $3$초(`band_result.txt`의 wall 줄)"',
     'time="항목마다 프로세스 2개로 각 $330$초에서 $430$초, 꼬리 각 $3$초(`band_result.txt`의 wall 줄)"'),
])
sub(r"원고_자료\빠른_확인.py", [
    ('expect=["faithful rho >= 1.00912689405 (case i); record-scheme rho >= 1.00942285566"]',
     'expect=["faithful rho >= 1.00976283256 (case i); record-scheme rho >= 1.00942285566"]'),
    ('expect=["faithful rho >= 1.00669141756 (case i); record-scheme rho >= 1.00669264606"]',
     'expect=["faithful rho >= 1.00689363122 (case i); record-scheme rho >= 1.00669264606"]'),
])
sub(r"scripts\_patch_README_세션파일.py", [
    (r"$\\Omega$는 `bprime_boxes/ivbox_lib.py`를 통해 같은 정확 정의를 쓴다(2026-11-14 H1; 앞선 판의 출력은 `v1_binary64omega/`). 두 폴더의 재실행 순서는 `세션_재계산/rerun_omega_h1.sh`다.",
     r"$\\Omega$는 `bprime_boxes/ivbox_lib.py`를 통해 같은 정확 정의를 쓴다(2026-11-14 H1; 앞선 판의 출력은 `v1_binary64omega/`). 두 폴더의 재실행 순서는 `세션_재계산/rerun_omega_h1.sh`다. 이 글의 방식(`fbox`)은 보조정리 hazard-H1의 $\\mathfrak h(k,\\nu)=\\frac k{k+\\nu}-\\frac k{2k-1}$를 그대로 쓰고, 기록의 상자 방식(`box`)만 기록의 $\\mathfrak h$에 곱해진 인자 $1-0.798(\\nu+1)^{-1/2}-0.81k^{-1/2}$를 그대로 두어 기록 값과 대조한다(2026-11-15; (ㄱ)(ㄴ)의 `fbox` 재실행은 `rerun_fbox_H_1115.sh`, 인자를 곱하던 앞선 판의 출력은 `v2_hazard_factor/`)."),
    ("우변에 더하는 항의 계수 $0$, 소구간 $4000$개)로 다시 돌린 것이다", "우변에 더하는 항의 계수 $0$, 셀 $4000$개)로 다시 돌린 것이다"),
    ("(최소 비 $1.355874$, 첫 소구간 $[1/2,12001/24000]$)", "(최소 비 $1.355874$, 첫 셀 $[1/2,12001/24000]$)"),
    ("새로 쓴 구간 판정(소구간 끝점은 정확한 유리수", "새로 쓴 구간 판정(셀 끝점은 정확한 유리수"),
    ("가 소구간별 비의 표 `band_cells_CE0.tsv`를 낸다", "가 셀별 비의 표 `band_cells_CE0.tsv`를 낸다"),
])
