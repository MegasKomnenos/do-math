# -*- coding: utf-8 -*-
"""빠른_확인.py -- 부록 D 계산의 축소판을 차례로 돌려 기대 출력과 맞춰 본다.

각 항목은 원 계산의 한 부분(앞쪽 몇 q, 최솟값이 나온 상자 하나, 열 몇 개 등)이나 원래 짧은 계산 전체를 돌리고,
출력에 기대 문자열(핵심 수치)이 모두 나타나는지 본다. 기대 문자열은 이 축소판을 한 번 돌려 얻은 값이며,
원 계산의 출력 파일에 같은 수치가 있는 경우 그 대조는 ENTRIES의 note에 적었다.
명령은 항목마다 새 임시 폴더를 현재 폴더로 하여 `python -I -B <스크립트> <인자…>`로 돌린다(묶음 안에 파일을 쓰지 않는다).
인자의 {B}는 이 파일이 있는 폴더(원고_자료)의 절대 경로로 바뀐다.

사용: python -I 빠른_확인.py                 모든 항목
      python -I 빠른_확인.py --list          항목 목록
      python -I 빠른_확인.py 이름 [이름 …]    고른 항목만(이름의 앞부분이 맞으면 된다)
      python -I 빠른_확인.py --show          불일치 항목의 출력 끝부분도 보인다
      python -I 빠른_확인.py --fast          60초를 넘는 항목(slow)을 뺀다
      python -I 빠른_확인.py --all           기본으로 빼 둔 긴 항목(long; 열 판독 약 3–4분)까지 돌린다
기본 실행(긴 항목 제외)의 목표는 이 기계에서 10분 안이다.
C 프로그램 항목은 빌드된 `세션_재계산/c50_iv/c50iv.exe`(Windows x64)를 부른다. 다른 운영체제에서는 README 「컴파일 옵션」대로
빌드한 실행 파일 이름으로 그 두 항목의 경로를 바꾸거나 이름을 골라 빼고 돌린다.
끝나면 일치/불일치 수와 걸린 시간을 적고, 불일치가 하나라도 있으면 종료 코드 1을 돌려준다.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

B = os.path.dirname(os.path.abspath(__file__))
S = "세션_재계산/"

ENTRIES = [
    # ---- 처음 돌려 볼 것(짧은 정확 정수·구간 계산 전체) ----
    dict(name="n80-로그오목성", label="logconcavity-failure-n80",
         cmd=[S + "logconcavity_n80/lc_n80.py"],
         expect=["failures with n <= 79: []", "first failure: (n, l) = (80, 40)",
                 "b_80,39 b_80,41 - b_80,40^2 > 0: True",
                 "three integers equal to appendix D (D.logconcavity-failure-n80): True"],
         note="계산 전체(n<=80). 세 정수는 부록 D 결과 줄의 값과 비교"),
    dict(name="섬유-전수", label="fiber-enumeration",
         cmd=[S + "fiber_exhaustive/fiber_exhaustive.py", "7"],
         expect=["n=6: parking functions 16807", "non-unimodal fibers 0", "n=7: parking functions 262144",
                 "distinct capacity multisets 96; non-unimodal fibers 30", "first n with a non-unimodal fiber: n=7"],
         note="계산 전체(n<=7). fiber_exhaustive.txt와 같다"),
    dict(name="제타-상수", label="zeta-constants",
         cmd=[S + "zeta_constants/zeta_iv.py", "4000", "4000"],
         expect=["z_{3/2}  in [2.6123753485619618733741325227235424, 2.6123753487472708831470185371446987]  subset of [2.61237, 2.61238]: True",
                 "z_{-1/2} in [-0.20788622497838395326979410317034486, -0.20788622497735456601058539192484968]  subset of [-0.20789, -0.20788]: True",
                 "z_{1/2}  in [-1.4603545088095868128895142528195161, -1.4603545088095855261554402483008795]  subset of [-1.46036, -1.46035]: True"],
         note="계산 전체. zeta_iv_out.txt와 같다"),
    dict(name="열세-항", label="prop-W-thirteen",
         cmd=[S + "prop_W_thirteen/iv13.py"],
         expect=["[49.6718494084121861016712837494180210158330572", "all 13 pass: True"],
         note="계산 전체. iv13_out.txt와 같다"),
    dict(name="띠-검사", label="band-check",
         cmd=[S + "band_check/band_iv.py", "0.71216", "0", "4000"],
         expect=["s0=0.71216 CE=0.0 NSUB=4000: certified min ratio = 1.355874",
                 "(0, 0.5, 0.5000416666666667, 1.9570106198050503, 0.9885536169418088, 0.007137543258748978, 0.4999889445552375, 0.01687367305105114, 0.0)"],
         note="계산 전체(기록 코드의 바이트 사본). band_iv_out_CE0.txt와 같다"),
    dict(name="띠-검사-판독", label="band-check",
         cmd=[S + "band_check/band_read.py", "{B}/" + S + "band_check/band_cells_CE0.tsv", "{B}/" + S + "band_check/band_iv_out_CE0.txt"],
         expect=["cells: 4000, tile [1/2, 2/3] contiguously: yes", "cells with ratio lower bound < 1.3558: 0",
                 "minimum ratio lower bound: 1.3558739652 at cell i=0, [1/2, 12001/24000]",
                 "margin over threshold: 0.0000739652",
                 "independent minimum rounded to 6 places agrees: True"],
         note="저장된 칸 표의 판독. band_read_out_CE0.txt와 같다"),
    dict(name="정리D-기저", label="theorem-D-base",
         cmd=[S + "theorem_D_base/thmD_base_iv.py"],
         expect=["pairs=240, mismatches=0", "min q: (m,d)=(689, 39)  q in [0.85613376342948715147", "all q in [0.856, 1.392]: True"],
         note="계산 전체. thmD_base_iv_out.txt와 같다"),
    dict(name="머리합-여유", label="H-star-plus-interval",
         cmd=[S + "H_star_plus/hplus_interval.py", "0.2"],
         expect=["max G/Theta <= [0.83202473690441142149823920822295521", "max G/Theta <= [0.63468645905221103862161087795185857",
                 "G/Theta <= [0.83207357914152365234597193234799555"],
         note="계산 전체. hplus_interval_out.txt와 같다"),
    dict(name="열-판독", label="m1-column-reading", long=True,
         cmd=[S + "m1_column_reading/m1_read.py", "{B}/r19de912/v2run20000-rows.tsv"],
         expect=["rows read: 19996 (n = 5..20000); rows failing the structure test: 0 []",
                 "= 0.709457 at k = 3136 (m1' = 3288)", "rows with mode_ell_mid != firstQ_ell: 0 []"],
         note="판독 전체. m1_read_out.txt와 같다"),
    dict(name="귀납-행", label="induction-rows",
         cmd=[S + "induction_rows/induction_rows.py", "{B}/r19de912/v2run20000-rows.tsv"],
         expect=["rows with Y0(m) < m - floor(0.75 m^(2/3)): 0 []",
                 "minimum margin Y0(m) - (m - floor(0.75 m^(2/3))) = 42 at m = 10001"],
         note="판독 전체. induction_rows_out.txt와 같다"),
    # ---- 무거운 계산의 축소판 ----
    dict(name="창질량-가-q50", label="window-mass-env",
         cmd=[S + "window_mass_env/cert_Cb_iv.py", "--quick", "1", "50"],
         expect=["worst relative margin 0.624610 at q=49, xi=0.1393 -> PASSES", "min rel margin 8.560727 at q=9"],
         note="(가)의 1<=q<50(전체 1<=q<=2999). cert_Cb_iv_out_1_2280.txt의 해당 최솟값과 같다"),
    dict(name="창질량-나-i0", label="window-mass-env", slow=True,
         cmd=[S + "window_mass_env/cert_interval_iv.py", "--quick", "0", "0"],
         expect=["i= 0 J_i=      3000: min rel margin 0.011251 at xi=0.912", "all cells and first cells positive: True"],
         note="(나) 열일곱 구간 가운데 전체 최솟값이 나오는 i=0(약 100초). cert_interval_iv_out.txt의 i=0 줄과 같다"),
    dict(name="창질량-기록코드-b31", label="window-mass-env",
         cmd=[S + "r030ffae_window/work/cert_Cb_range.py", "--quick", "1", "31"],
         expect=["worst relative margin = 1.32981 at b=30, x=0.0853 -> PASSES"],
         note="기록 코드의 (C_b) 첫 조각(늘린 격자). NEW_cert_Cb_1_31.out과 같다"),
    dict(name="B'-상자-최악", label="bprime-boxes",
         cmd=[S + "bprime_boxes/bprime_iv.py", "point", "6935", "7213", "1301", "1340"],
         expect=["rho in [1.052428971,"],
         note="유한 상자 140,729개 가운데 최솟값 상자 하나. bprime_result.txt와 같다"),
    dict(name="B'-꼬리", label="bprime-boxes",
         cmd=[S + "bprime_boxes/bprime_iv.py", "tail"],
         expect=["tail worst rho >= 1.305596158 at zeta in (0.0, 0.05)"],
         note="꼬리 상자 전부. tail_out.txt와 같다"),
    dict(name="띠상자-ㄱ-최악", label="band-boxes",
         cmd=[S + "band_boxes/band_iv.py", "fpoint", "H", "12", "25", "6668", "6668", "6935", "3280", "3328"],
         expect=["faithful rho >= 1.00912689405 (case i); record-scheme rho >= 1.00942285566"],
         note="(ㄱ)의 최솟값 상자. band_result.txt와 같다"),
    dict(name="띠상자-ㄴ-최악", label="band-boxes",
         cmd=[S + "band_boxes/band_iv.py", "fpoint", "H", "57", "100", "100000", "100000", "104000", "57969", "59280"],
         expect=["faithful rho >= 1.00669141756 (case i); record-scheme rho >= 1.00669264606"],
         note="(ㄴ)의 최솟값 상자. band_result.txt와 같다"),
    dict(name="띠상자-ㄷ-최악", label="band-boxes",
         cmd=[S + "band_boxes/band_iv.py", "fpoint", "N", "11", "25", "6668", "6668", "6935", "3000", "3051"],
         expect=["faithful rho >= 1.0136495704 (case i); record-scheme rho >= 1.01364914708"],
         note="(ㄷ)의 최솟값 상자. band_result.txt와 같다"),
    dict(name="띠상자-ㄹ-최악", label="band-boxes",
         cmd=[S + "band_boxes/band_iv.py", "fpoint", "N", "53", "100", "100000", "100000", "104000", "54640", "55120"],
         expect=["faithful rho >= 1.0091044897 (case i); record-scheme rho >= 1.00910146258"],
         note="(ㄹ)의 최솟값 상자. band_result.txt와 같다"),
    dict(name="띠상자-ㄱ-꼬리", label="band-boxes",
         cmd=[S + "band_boxes/band_iv.py", "tail", "H", "12", "25", "6668"],
         expect=["tail worst rho >= 1.122243024 at nu/k in (0.475, 0.48)"],
         note="(ㄱ)의 꼬리 전부. tail_H_T12-25_k6668.txt와 같다"),
    dict(name="Q_fin-두열", label="Q-fin-1130",
         cmd=[S + "Q_fin_1130/qfin_iv.py", "2001", "3130", "1129", "0", "q.jsonl"],
         expect=["2001 True 1.157825 4.470053e-01", "3130 True 0.785457 2.437312e-04"],
         note="1130열 가운데 첫 열과 최솟값 열 k=3130. qfin_iv_out_p0/p1.txt와 같다"),
    dict(name="Q_fin-정확정수", label="Q-fin-1130",
         cmd=[S + "Q_fin_1130/test_small.py"],
         expect=["Bor violations 0", "ALL OK"],
         note="작은 열에서 구간 열이 정확 정수를 담는지. test_small_out.txt와 같다"),
    dict(name="누적로그오목-780창", label="cumulative-logconcavity",
         cmd=[S + "cumulative_logconcavity_n779/lca_exact.py", "quick", "572", "581", "780"],
         expect=["violations at n = 780: [575, 576, 577, 578]", "n=780 l=575: relative D/A^2 = -1.7174e-09",
                 "n=780 l=577: relative D/A^2 = -5.8810e-09", "n=779 minimum relative D/A^2 in this window = 1.02688e-08 at l = 576"],
         note="열 572–581, n<=780만(전체는 n<=800의 모든 열). lca_exact_N800.txt의 값과 같다"),
    dict(name="Newton-r60", label="newton-m170",
         cmd=[S + "newton_r61_169/newton_cert.py", "2", "60", "1", "newton_quick.txt"],
         expect=["r=2 polynomials=1 failures=[] nonzero_beyond_r+d+3=[] max_degree_minus_(r+d+1)=0",
                 "r=60 polynomials=59 failures=[] nonzero_beyond_r+d+3=[] max_degree_minus_(r+d+1)=0"],
         note="2<=r<=60(전체 2<=r<=170). 각 줄이 newton_cert_out.txt와 같다"),
    dict(name="띠LP-가나", label="band-LP",
         cmd=[S + "band_LP/part_ga_na.py", "--quick"],
         expect=["k mu/(1-mu) in [741.781730899, 741.781730899]", "number of k with lower end of F_k(103) < 0: 0 []",
                 "minimum lower end at k = 38887: F_k(103) in [3.85784634041e-7, 3.85784634041e-7]", "gap [3.54834e-7, 3.54834e-7]"],
         note="(가)(나)의 계산 전체. 시간 줄을 빼고 out_ga_na.txt와 같다"),
    dict(name="띠LP-다-최소근처", label="band-LP",
         cmd=[S + "band_LP/part_da.py", "9467", "9475", "q_da", "9466", "9472", "--quick"],
         expect=["range 9467..9475: k with a failing width-1 block: 0 []",
                 "minimum block lower bound among passing k: 4.594086e-09 at k=9472 block (165, 166)", "k=9466: nu1 cover M=401"],
         note="(다)의 9467<=k<=9475(전체 9467–38886). out_da_9467_22000.txt의 최솟값·점별 줄과 같다"),
    dict(name="띠LP-라-최소근처", label="band-LP",
         cmd=[S + "band_LP/part_ra.py", "7270", "7280", "q_ra", "7275", "--quick"],
         expect=["range 7270..7280: k with a failing width-1 block: 0 []",
                 "minimum block lower bound among passing k: 3.130617e-07 at k=7275 block (190, 275)",
                 "pointwise (a=b=nu) min lower bound of F^LP 1.896907e-02 at nu=109"],
         note="(라)의 7270<=k<=7280(전체 6668–9466). out_ra_6668_8000.txt와 같다"),
    dict(name="극영역-첫블록", label="polar-blocks-488", slow=True,
         cmd=[S + "r89eb039_polar_iv/recert.py", "{B}/" + S + "r89eb039_polar_iv/inputs/recert_P1.jsonl", "q_P1.jsonl", "0", "1"],
         expect=["[2001,2011] ok=True eta=0.0220857 (orig 0.0220874) Vsqrtk=1.21142 (orig 1.21142) psi=0.0007661 (orig 0.0007661)"],
         note="구간 판(r89eb039_polar_iv)으로 488블록 가운데 첫 블록(약 50초). out/run_w0.log의 [2001,2011] 줄과 같다"),
    dict(name="모멘트-열840", label="moment-certification",
         cmd=[S + "moment_cert_iv/mcert_iv.py", "one", "840", "1681", "91728", "full"],
         expect=['"k": 840, "N": 91728, "nlo": 1681, "fails": 0, "minE": 15.035292', '"argminE": 1681, "minrel": 0.137915',
                 '"argminrel": 1690'],
         note="(A3)의 열 k=840, 1681<=n<=91728(full 모드, 약 30초; 전체는 (A3)(A5) 1500열). 상대 여유 하계의 최솟값이 나오는 열이다. compare_out.txt의 k=840 줄, summary.txt A3 줄의 상대 여유 최솟값(0.137916, (840,1690))과 같다"),
    dict(name="열인증-841", label="column-certificates-841-2000", slow=True,
         steps=[[S + "column_cert_iv/tables.py"],
                [S + "column_cert_iv/colcert_iv.py", "--ks", "841-841", "--part", "0", "--nparts", "1", "--batch", "1",
                 "--out", "res_841.jsonl"]],
         expect=["lo<=hi True",
                 "k=841 ok=True b0=0.119193 margin=0.114942 Gamma_hi=1.0000956 PU_hi=0.025458659 stored_ok=True nV=20025 NE_rec=20025"],
         note="1160열 가운데 첫 열 k=841. run_p0.log의 k=841 줄과 같다. 표 _cache가 없으면 tables.py가 묶음 안 column_cert_iv/_cache/에 만든다(약 1.5분, 33 MB). colcert_iv.py는 기록 [rb7effe0]의 열 자료 block3_501_2000_all.json을 묶음 안 사본 `rb7effe0/evidence/code/turn3/block3_501_2000_all.json`을 읽는다(없으면 기록 폴더)"),
    dict(name="C구간-n60-정확정수", label="c50",
         steps=[[S + "c50_iv/c50iv.exe", "60", "5", "2", "59", "16", "2", "t60", "{B}/" + S + "c50_iv", "-dumpall"],
                [S + "c50_iv/exact_small.py", "60", "t60"]],
         expect=['"records_checked": 927', '"outside": 0', '"rows_compared": 56', '"row_mismatches": 0'],
         note="C 프로그램(빌드된 c50iv.exe)을 n<=60에서 돌리고 모든 구간이 정확 정수를 담는지. runs/t60_exact_check.txt와 같다"),
    dict(name="C20-탐침B", label="c50",
         steps=[[S + "c50_iv/c50iv.exe", "20000", "5", "19522", "19585", "64", "1", "c20_probeB", "{B}/" + S + "c50_iv",
                 "-probe", "19522", "19523", "19524"],
                [S + "c50_iv/probe_undercount.py", "c20_probeB_dump.bin"]],
         expect=['"records_checked": 1431', '"outside": 0', '"pair_disagree": 0', '"lc_disagree": 0'],
         note="C20의 최소 여유 자리를 지나는 열 블록 하나를 미달 수 재귀의 참조 구간과 대조. runs/c20_probeB_undercount.txt와 같다"),
    dict(name="정리U-상수", label="theorem-U-constant", slow=True,
         cmd=[S + "theorem_U_constant/theorem_U_iv.py", "8000", "8000"],
         expect=["J_I(1) <= 8.1309087594   claim <= 8.133   ok: True",
                 "C_I + C_X <= 50.59610054   (<= 50.62: True, margin 0.023899)"],
         note="기본 격자의 계산 전체(더 거친 격자는 진술의 값에 못 미친다). theorem_U_iv_out.txt와 같다"),
]


def argv_of(cmd):
    args = [a.replace("{B}", B) for a in cmd[1:]]
    script = os.path.join(B, cmd[0])
    if script.endswith(".exe"):
        return [script] + args
    return [sys.executable, "-I", "-B", script] + args


def run(e, show):
    """steps가 있으면 같은 임시 폴더에서 차례로 돌리고, 기대 문자열은 모든 단계의 출력을 이어 붙인 것에서 찾는다."""
    tmp = tempfile.mkdtemp(prefix="pf_quick_")
    steps = e.get("steps") or [e["cmd"]]
    t0 = time.time()
    out, rc = "", 0
    for cmd in steps:
        try:
            p = subprocess.run(argv_of(cmd), cwd=tmp, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=e.get("timeout", 900))
            out += p.stdout + p.stderr
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = "timeout"
        except OSError as ex:
            out += f"실행 실패: {ex}\n"
            rc = "oserror"
        if rc != 0:
            break
    dt = time.time() - t0
    shutil.rmtree(tmp, ignore_errors=True)
    missing = [x for x in e["expect"] if x not in out]
    ok = not missing and rc == 0
    tag = "일치" if ok else "불일치"
    print(f"[{tag}] {e['name']:<18} {dt:7.1f} s  D.{e['label']}" + ("" if ok else f"  (종료 코드 {rc}; 없는 기대 문자열 {len(missing)}개)"), flush=True)
    if not ok:
        for m in missing:
            print(f"        없음: {m}")
        if show:
            print("        --- 출력 끝 ---")
            for ln in out.strip().splitlines()[-15:]:
                print("        " + ln)
    return ok, dt


def main():
    args = sys.argv[1:]
    show = "--show" in args
    if "--list" in args:
        for e in ENTRIES:
            flag = " [long]" if e.get("long") else " [slow]" if e.get("slow") else ""
            print(f"{e['name']:<18} D.{e['label']:<28} {e['note']}{flag}")
        return 0
    names = [a for a in args if not a.startswith("--")]
    sel = [e for e in ENTRIES if not names or any(e["name"].startswith(n) for n in names)]
    if "--fast" in args:
        sel = [e for e in sel if not e.get("slow")]
    if "--all" not in args and not names:
        sel = [e for e in sel if not e.get("long")]
    if not sel:
        print("고른 항목이 없다. --list로 이름을 보라.")
        return 2
    import platform
    try:
        import numpy, mpmath
        vers = f"numpy {numpy.__version__}, mpmath {mpmath.__version__}"
    except ImportError as ex:
        vers = f"패키지 없음: {ex}"
    print(f"Python {platform.python_version()} ({platform.system()} {platform.machine()}), {vers}; 항목 {len(sel)}개", flush=True)
    t0 = time.time()
    res = [run(e, show) for e in sel]
    n_ok = sum(1 for ok, _ in res if ok)
    print(f"일치 {n_ok} / {len(res)}, 불일치 {len(res) - n_ok}; 전체 {time.time() - t0:.0f} s")
    return 0 if n_ok == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
