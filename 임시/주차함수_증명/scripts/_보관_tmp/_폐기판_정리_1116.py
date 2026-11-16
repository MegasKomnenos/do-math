# -*- coding: utf-8 -*-
"""10차 RD 인계 6: 글이 더는 가리키지 않는 폐기 판 코드·출력을 자료 묶음에서 빼 보관하고, README 설명문·패치 스크립트 PARAS·
재실행 스크립트 주석·재실행표 생성기 cmd의 이력 서술을 걷는다. R6 인계: README 657행 varkappa(theta) → L^T(theta). 2026-11-16."""
import io, os, shutil
ROOT = r"C:\math\임시\주차함수_증명"
S = os.path.join(ROOT, "원고_자료", "세션_재계산")
KEEP = os.path.join(ROOT, "대조v2", "보관_재계산_옛판_1116")
MOVE = ["bprime_boxes/ivbox_lib_v1_binary64omega.py", "bprime_boxes/ivbox_lib_v2_storedgrid.py",
        "bprime_boxes/v1_binary64omega", "bprime_boxes/v3_storedgrid",
        "band_boxes/v1_binary64omega", "band_boxes/v2_hazard_factor", "band_boxes/v3_storedgrid",
        "band_boxes/rerun_fbox_H_1115.sh", "band_boxes/rerun_fbox_H_1115_log.txt",
        "rerun_omega_h1.sh", "rerun_omega_h1_log.txt"]
for rel in MOVE:
    src = os.path.join(S, rel.replace("/", os.sep))
    if not os.path.exists(src):
        print("없음", rel); continue
    dst = os.path.join(KEEP, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    print("옮김", rel)


def sub(rel, pairs, must=True):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            if must:
                raise SystemExit(f"{rel}: {n}건 — {a[:70]}")
            print("  건너뜀", rel, a[:50]); continue
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", rel)


P_B1 = [
    ("구간 산술로 다시 계산한 것이다(2026-11-13 세션). 스칼라는 mpmath", "구간 산술로 다시 계산한 것이다. 스칼라는 mpmath"),
    ("조각별 비증가를 구간으로 확인한다(2026-11-14 H1; `test_lib.py`→`test_lib_out.txt`가 기록의 binary64 함수와 대조).",
     "조각별 비증가를 구간으로 확인한다(`test_lib.py`→`test_lib_out.txt`가 기록의 binary64 함수와 대조). 저장된 봉투 표 $\\hat{\\mathcal T}$는 저장값을 정확한 점 $\\xi^{\\mathcal T}_i=0.0005\\,i$에 둔 선형 보간으로 읽는다."),
]
P_B2 = [
    ("같은 구간 산술로 다시 계산한 것이다(2026-11-13 세션). 상자 안의", "같은 구간 산술로 다시 계산한 것이다. 상자 안의"),
    ("같은 정확 정의를 쓴다(2026-11-14 H1; 앞선 판의 출력은 `v1_binary64omega/`). 두 폴더의 재실행 순서는 `세션_재계산/rerun_omega_h1.sh`다. 이 글의 방식(`fbox`)은 보조정리 hazard-H1의 $\\mathfrak h(k,\\nu)=\\frac k{k+\\nu}-\\frac k{2k-1}$를 그대로 쓰고, 기록의 상자 방식(`box`)만 기록의 $\\mathfrak h$에 곱해진 인자 $1-0.798(\\nu+1)^{-1/2}-0.81k^{-1/2}$를 그대로 두어 기록 값과 대조한다(2026-11-15; (ㄱ)(ㄴ)의 `fbox` 재실행은 `rerun_fbox_H_1115.sh`, 인자를 곱하던 앞선 판의 출력은 `v2_hazard_factor/`).",
     "같은 정확 정의를 쓴다. 두 폴더의 재실행 순서는 `세션_재계산/rerun_exactgrid_1116.sh`다. 이 글의 방식(`fbox`)은 보조정리 hazard-H1의 $\\mathfrak h(k,\\nu)=\\frac k{k+\\nu}-\\frac k{2k-1}$를 그대로 쓰고, 기록의 상자 방식(`box`)만 기록의 $\\mathfrak h$에 곱해진 인자 $1-0.798(\\nu+1)^{-1/2}-0.81k^{-1/2}$를 그대로 두어 기록 값과 대조한다."),
]
P_K = [("$\\varkappa(\\theta)$, 묶음 가중", "$\\mathcal L^{\\mathrm T}(\\theta)$, 묶음 가중")]

sub(r"원고_자료\README.md", P_B1 + P_B2 + P_K)
# 패치 스크립트 PARAS(백슬래시 두 겹)
def dbl(pairs):
    return [(a.replace("\\", "\\\\"), b.replace("\\", "\\\\")) for a, b in pairs]
sub(r"scripts\_patch_README_세션파일.py", dbl(P_B1 + P_B2 + P_K), must=False)
sub(r"원고_자료\세션_재계산\rerun_exactgrid_1116.sh", [
    ("# table hat T to the exact nodes xi_j = j/2000.  Previous outputs: bprime_boxes/v3_storedgrid/, band_boxes/v3_storedgrid/.",
     "# table hat T to the exact nodes xi_j = j/2000."),
])
sub(r"scripts\_gen_재실행표.py", [
    ('"python -I summarize.py > summary_out.txt (기록 ra4c01fc의 cert2/cert3 경로와 verify_A00.json이 필요)"',
     '"python -I summarize.py > summary_out.txt"'),
], must=False)
