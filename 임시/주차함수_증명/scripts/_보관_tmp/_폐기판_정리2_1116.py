# -*- coding: utf-8 -*-
"""_폐기판_정리_1116.py의 문자열 불일치를 정규식으로 다시 적용(README·PARAS·재실행 스크립트·생성기), 그리고 README SHA 표의 없는 행 제거. 2026-11-16."""
import io, os, re, subprocess, sys
ROOT = r"C:\math\임시\주차함수_증명"


def patch(rel, fn):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    t, n = fn(s)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("ok", rel, n)


def readme_fn(s, esc=False):
    n = 0
    def rep(pat, new, flags=0):
        nonlocal s, n
        s, k = re.subn(pat, (new if callable(new) else (lambda m, t=new: t)), s, flags=flags)
        n += k
    bs = "\\\\" if esc else "\\"
    rep(r"구간 산술로 다시 계산한 것이다\(2026-11-13 세션\)\. 스칼라는 mpmath", "구간 산술로 다시 계산한 것이다. 스칼라는 mpmath")
    rep(r"조각별 비증가를 구간으로 확인한다\(2026-11-14 H1; (`test_lib\.py`→`test_lib_out\.txt`가 기록의 binary64 함수와 대조)\)\.",
        lambda m: "조각별 비증가를 구간으로 확인한다(" + m.group(1) + "). 저장된 봉투 표 $" + bs + "hat{" + bs + "mathcal T}$는 저장값을 정확한 점 $" + bs + "xi^{" + bs + "mathcal T}_i=0.0005" + bs + ",i$에 둔 선형 보간으로 읽는다.")
    rep(r"같은 구간 산술로 다시 계산한 것이다\(2026-11-13 세션\)\. 상자 안의", "같은 구간 산술로 다시 계산한 것이다. 상자 안의")
    rep(r"같은 정확 정의를 쓴다\(2026-11-14 H1; 앞선 판의 출력은 `v1_binary64omega/`\)\. 두 폴더의 재실행 순서는 `세션_재계산/rerun_omega_h1\.sh`다\.",
        "같은 정확 정의를 쓴다. 두 폴더의 재실행 순서는 `세션_재계산/rerun_exactgrid_1116.sh`다.")
    rep(r"기록 값과 대조한다\(2026-11-15; \(ㄱ\)\(ㄴ\)의 `fbox` 재실행은 `rerun_fbox_H_1115\.sh`, 인자를 곱하던 앞선 판의 출력은 `v2_hazard_factor/`\)\.",
        "기록 값과 대조한다.")
    rep(r"\$" + re.escape(bs) + r"varkappa\(" + re.escape(bs) + r"theta\)\$, 묶음 가중", "$" + bs + "mathcal L^{" + bs + "mathrm T}(" + bs + "theta)$, 묶음 가중")
    return s, n


patch(r"원고_자료\README.md", lambda s: readme_fn(s, esc=False))
patch(r"scripts\_patch_README_세션파일.py", lambda s: readme_fn(s, esc=True))
patch(r"원고_자료\세션_재계산\rerun_exactgrid_1116.sh",
      lambda s: re.subn(r"  Previous outputs: bprime_boxes/v3_storedgrid/, band_boxes/v3_storedgrid/\.", "", s))
patch(r"scripts\_gen_재실행표.py",
      lambda s: re.subn(r' \(기록 ra4c01fc의 cert2/cert3 경로와 verify_A00\.json이 필요\)', "", s))

# README SHA 표에서 디스크에 없는 세션_재계산 행 제거
README = os.path.join(ROOT, "원고_자료", "README.md"); BASE = os.path.join(ROOT, "원고_자료", "세션_재계산")
s = io.open(README, encoding="utf-8").read()
missing = [m.group(1) for m in re.finditer(r"^\| `세션_재계산/([^`]+)` \| `[0-9a-f]{64}` \|", s, re.M)
           if not os.path.exists(os.path.join(BASE, m.group(1).replace("/", os.sep)))]
print("없는 행", len(missing)); [print("  -", r) for r in missing]
if missing:
    args = []
    for r in missing:
        args += ["--remove", r]
    subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")] + args, check=True)
