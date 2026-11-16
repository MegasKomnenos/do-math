# -*- coding: utf-8 -*-
"""원고_자료/재실행표.md(부록 D 항목 → 다시 돌리는 법 대응표)를 만든다. 멱등: 다시 돌리면 표 전체를 새로 쓴다.

한 행 = 부록 D 항목 하나(머리 `### D.{{D:이름}}`). 열:
  라벨 | 확인하는 진술(첫 구절) | 스크립트 | 실행 명령 | 기대 출력 | 출력 파일·SHA-256 | 실행 시간 | 산술 등급 | 최소 여유 | 재실행
읽는 곳:
  - 확인하는 진술·산술 등급·결과·꺾쇠 요약 〔구현; 범위; 산술; 자료〕는 장v2/부록D_장*.md에서 자동으로 읽는다.
    산술 등급은 그 줄의 첫 문장, 재실행은 꺾쇠의 자료 항목(기록 / 이 글 / 기록·이 글)이다.
  - 스크립트·실행 명령·출력 파일은 아래 CONFIG(이 글의 재계산 폴더가 있는 항목)에서, 없으면 README 「파일 목록」 표에서
    그 라벨이 붙은 기록 코드·출력 파일을 읽는다. 기록 코드의 실행 명령은 코드가 인자를 읽지 않으면 `python -I <스크립트>`,
    인자를 읽고 머리 주석에 사용법이 있으면 그 줄, 없으면 「(인자 확인 필요)」.
  - SHA-256은 원고_자료/README.md의 두 표(세션 재계산 표, 파일 목록 표)에서 읽는다(파일을 다시 해시하지 않는다).
  - 실행 시간은 CONFIG의 time(사람이 적은 값과 출처)이 있으면 그것을, 없으면 CONFIG의 timefiles·출력 파일에서
    `total time N s`, `total N s`, `elapsed N`, `finished in N s`, `worker seconds: [...]` 꼴을 자동으로 읽는다. 못 읽으면 「—」.
  - 기대 출력은 CONFIG의 expect가 있으면 그것을, 없으면 결과 줄의 첫 문장(잘라서)을 쓴다.
  - 최소 여유는 scripts/_재실행표_여유.json(라벨 → 문자열; 사람이 결과 줄에서 옮겨 적은 값)에서 읽는다. 없는 라벨은 「(계산 뒤 채움)」.
진행 중인 항목: IN_PROGRESS에 든 라벨은 스크립트·명령·기대 출력·출력·시간·산술 등급·재실행 칸을 「(진행 중)」로 둔다.
  계산이 끝나 부록 D 항목과 README 표가 갱신되면, IN_PROGRESS에서 그 라벨을 빼고(필요하면 CONFIG에 행을 더하고)
  다시 돌린다. `--all`을 주면 IN_PROGRESS를 무시한다.
사용: python -I scripts/_gen_재실행표.py [--all] [--out 원고_자료/재실행표.md]
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAP = os.path.join(ROOT, "장v2")
BUNDLE = os.path.join(ROOT, "원고_자료")
README = os.path.join(BUNDLE, "README.md")
OUT_DEFAULT = os.path.join(BUNDLE, "재실행표.md")
PH = "(진행 중)"
MARGIN_FILE = os.path.join(ROOT, "scripts", "_재실행표_여유.json")
MARGIN_PH = "(계산 뒤 채움)"

# 진행 중인 계산이 걸린 항목(계산이 끝나면 빼고 다시 돌린다).
IN_PROGRESS = {
}

S = "세션_재계산/"
# 이 글의 재계산 폴더가 있는 항목. 경로는 원고_자료 기준. cmd의 cwd는 각 명령 앞의 [폴더]로 적는다.
CONFIG = {
    "polar-blocks-488": dict(
        scripts=[S + "r89eb039_polar_iv/recert.py", S + "r89eb039_polar_iv/ia.py", S + "r89eb039_polar_iv/achain_iv.py",
                 S + "r89eb039_polar_iv/summarize.py"],
        cmd=["sh run_worker.sh 0", "sh run_worker.sh 1", "sh run_worker.sh 2", "python -I achain_iv.py",
             "python -I summarize.py > out/summary.txt"],
        expect="488블록 전부 통과(new FAIL blocks: []), $\\varsigma$-구간 2472개 통과(0 FAIL), $V\\sqrt{k_1}\\in[0.57022,1.44544]$",
        outputs=[S + "r89eb039_polar_iv/out/NEW_blocks_merged.jsonl", S + "r89eb039_polar_iv/out/summary.txt",
                 S + "r89eb039_polar_iv/out/achain_iv.jsonl"],
        time="블록 재인증은 프로세스 3개가 각 2시간 30분(13:43–16:15; `out/run_w*.log`), $\\varsigma$-구간은 783초(`out/achain_iv.log`)"),
    "column-certification-k500": dict(
        scripts=[S + "column_k500_iv/lastcar_iv.py", S + "column_k500_iv/colk500.py", S + "column_k500_iv/summarize.py"],
        cmd=["python -I colk500.py --worker 0 --nworkers 2", "python -I colk500.py --worker 1 --nworkers 2",
             "python -I summarize.py > summary_out.txt", "python -I compare_indep.py > compare_indep_out.txt"],
        expect="380열 실패 0(직접 차분 20,368,570개·띠 10,302,655개); 최소 상대 여유 $1.3778\\times10^{-5}$($k=500$, $n=2k+1$)",
        outputs=[S + "column_k500_iv/summary_out.txt", S + "column_k500_iv/compare_indep_out.txt", S + "column_k500_iv/res/SHA256SUMS.txt"],
        time="작업자 2개 각 약 9500초(공유 기계; 벽시계 2.7시간; `run_w0.log`·`run_w1.log`)"),
    "moment-certification": dict(
        scripts=[S + "moment_cert_iv/mcert_iv.py", S + "moment_cert_iv/summarize.py", S + "moment_cert_iv/compare.py", S + "moment_cert_iv/nM.py"],
        cmd=["python -I mcert_iv.py sweep 0 2 sweep_p0.jsonl", "python -I mcert_iv.py sweep 1 2 sweep_p1.jsonl",
             "python -I summarize.py > summary.txt", "python -I compare.py", "python -I nM.py"],
        expect="(A3)(A5) 1500열 60,479,535개 위치 전부 통과(fails 0); 상대 여유 하계의 최솟값 $0.137916$((A3) $k=840$); $n_{\\mathrm M}(k)$ 1160열 기록과 일치",
        outputs=[S + "moment_cert_iv/summary.txt", S + "moment_cert_iv/sweep_p0.jsonl", S + "moment_cert_iv/sweep_p1.jsonl",
                 S + "moment_cert_iv/compare_out.txt", S + "moment_cert_iv/nM_out.txt"],
        time="프로세스 2개(BLAS 스레드 1)로 2시간 10분(15:25–17:36; 부록 D 범위 밖 열 포함), CPU 합 15,164초 가운데 (A3)(A5) 9,786초(`sweep_p*.log`, `summary.txt`)"),
    "xcert-partAB": dict(
        scripts=[S + "xcert_iv/ivv.py", S + "xcert_iv/midfft.py", S + "xcert_iv/common.py", S + "xcert_iv/asym_iv.py", S + "xcert_iv/tables_iv.py",
                 S + "xcert_iv/layerB.py", S + "xcert_iv/layerAint.py", S + "xcert_iv/layerA1.py", S + "xcert_iv/layerA2.py", S + "xcert_iv/layerA3.py",
                 S + "xcert_iv/summarize.py"],
        cmd=["python -I tables_iv.py",
             "python -I layerB.py --run --part 0 --nparts 2 --out resB_p0.jsonl",
             "python -I layerB.py --run --part 1 --nparts 2 --out resB_p1.jsonl",
             "python -I layerAint.py --run --part 0 --nparts 2 --idx 0 97 --out resAint_p0.jsonl",
             "python -I layerAint.py --run --part 1 --nparts 2 --idx 97 110 --out resAint_p1.jsonl",
             "python -I layerA1.py --run --part 0 --nparts 2 --out resA1_p0.jsonl",
             "python -I layerA1.py --run --part 1 --nparts 2 --out resA1_p1.jsonl",
             "python -I layerA2.py --run --out resA2.jsonl",
             "python -I layerA3.py --run --out resA3.json",
             "python -I summarize.py > summary.txt"],
        expect="다섯 층 전부 통과(failed: [], missing 0), 덮개 covers_501_to_infinity: True; 최대 R_U(구간 위 끝) 층 B 1.274643(k=501), A-int 1.938978([23462,24646]), A″-1 1.869748, A″-2 1.881602, A″-3 R_maj 1.000183; 최소 여유 0.0610(A-int); 2002≤k≤5000의 최대 R_U 1.03086(𝔠=4), ς_L(2002)=5.3146753",
        outputs=[S + "xcert_iv/summary.txt", S + "xcert_iv/summary.json", S + "xcert_iv/resB_p0.jsonl", S + "xcert_iv/resB_p1.jsonl",
                 S + "xcert_iv/resAint_p0.jsonl", S + "xcert_iv/resAint_p1.jsonl", S + "xcert_iv/resAint_p3.jsonl",
                 S + "xcert_iv/resA1_p0.jsonl", S + "xcert_iv/resA1_p1.jsonl", S + "xcert_iv/resA1_p3.jsonl", S + "xcert_iv/resA2.jsonl", S + "xcert_iv/resA3.json"],
        time="프로세스 2개(OPENBLAS_NUM_THREADS=1, 다른 계산과 4코어 공유)로 벽시계 약 9.6시간(11-13 16:53–11-14 02:30); 프로세스 시간 층 B 6.5시간, A-int 2.7시간, A″-1 7.3시간, A″-2 1.6시간(`summary.json`의 cpu_hours)"),
    "column-certificates-841-2000": dict(
        scripts=[S + "column_cert_iv/colcert_iv.py", S + "column_cert_iv/ivlib.py", S + "column_cert_iv/tables.py",
                 S + "column_cert_iv/summary.py"],
        cmd=["python -I tables.py",
             "python -I colcert_iv.py --ks 841-2000 --part 0 --nparts 2 --batch 16 --out res_p0.jsonl",
             "python -I colcert_iv.py --ks 841-2000 --part 1 --nparts 2 --batch 16 --out res_p1.jsonl",
             "python -I colcert_iv.py --ks 501-840 --part 0 --nparts 2 --batch 16 --out res_ext_p0.jsonl",
             "python -I colcert_iv.py --ks 501-840 --part 1 --nparts 2 --batch 16 --out res_ext_p1.jsonl",
             "python -I summary.py 501-2000 res_p0.jsonl res_p1.jsonl res_ext_p0.jsonl res_ext_p1.jsonl > summary_all_out.txt"],
        expect="1500열 모두 성공(failing columns: []), 최소 $\\mathfrak b_0=0.03478$($k=1131$), 여유 $\\ge0.02722$, $V$ 위 끝은 저장값 곱의 $1.000007$배 이하",
        outputs=[S + "column_cert_iv/summary_all_out.txt", S + "column_cert_iv/res_p0.jsonl", S + "column_cert_iv/res_p1.jsonl",
                 S + "column_cert_iv/res_ext_p0.jsonl", S + "column_cert_iv/res_ext_p1.jsonl"],
        time="프로세스 2개가 각 10,475초(열 841–2000)와 946·901초(열 501–840); 표 58초"),
    "fiber-enumeration": dict(
        scripts=[S + "fiber_exhaustive/fiber_exhaustive.py"],
        cmd=["python -I fiber_exhaustive.py 7"],
        expect="$n=7$: non-unimodal fibers 30; $n\\le6$: 0",
        outputs=[S + "fiber_exhaustive/fiber_exhaustive.txt"]),
    "fiber-nonunimodal-bound": dict(
        scripts=[S + "fiber_nonunimodal_bound/fiber_bound_iv.py"],
        cmd=["python -I fiber_bound_iv.py"],
        expect="$n=17$: bound $\\le0.739508687662\\le0.74$; 모든 $n$에서 upper end <= claim: True",
        outputs=[S + "fiber_nonunimodal_bound/fiber_bound_iv_out.txt"],
        timesum=True),
    "logconcavity-failure-n80": dict(
        scripts=[S + "logconcavity_n80/lc_n80.py"],
        cmd=["python -I lc_n80.py"],
        expect="first failure: (n, l) = (80, 40); three integers equal to appendix D: True",
        outputs=[S + "logconcavity_n80/lc_n80_out.txt"]),
    "cumulative-logconcavity": dict(
        scripts=[S + "cumulative_logconcavity_n779/lca_exact.py"],
        cmd=["python -I lca_exact.py worker 1 350 800 part1.json", "python -I lca_exact.py worker 351 798 800 part2.json",
             "python -I lca_exact.py merge 800 part1.json part2.json"],
        expect="위반 390곳, $n\\le779$에 없음, $n=780$에서 $\\ell=575$–$578$",
        outputs=[S + "cumulative_logconcavity_n779/lca_exact_N800.txt"],
        timefiles=[S + "cumulative_logconcavity_n779/lca_exact_N800.txt"]),
    "c50": dict(
        scripts=[S + "c50_iv/c50iv.c", S + "c50_iv/make_tables_iv.py", S + "c50_iv/postprocess_iv.py"],
        cmd=["python -I make_tables_iv.py 50100", "cmd /c build.bat", "c50iv.exe 20000 5 2 19999 64 2 runs/c20 .",
             "c50iv.exe 50000 20001 10000 49999 64 2 runs/c50 .", "(후처리·대조는 `run_commands.txt`)"],
        expect="미결 위치 0, 최대 상대 폭 $2.25\\times10^{-12}$",
        outputs=[S + "c50_iv/runs/c50_summary.json", S + "c50_iv/runs/c20_summary.json"],
        time="표 41.7초, C20 194.6초, C50 3982.6초(약 66분; `run_commands.txt`)"),
    "newton-m170": dict(
        scripts=[S + "newton_r61_169/newton_cert.py"],
        cmd=["python -I newton_cert.py 2 170 2 <출력>", "python -I newton_cert.py 3 169 2 <출력>",
             "(짝·홀 r 두 프로세스; 인자는 `run_even.log`·`run_odd.log`에서 추정)"],
        expect="$2\\le r\\le170$의 다항식 14,365개, failures=[]",
        outputs=[S + "newton_r61_169/newton_cert_out.txt"],
        time="2124초·2079초(두 프로세스 동시; `run_even.log`·`run_odd.log`)"),
    "critical-window-rig": dict(
        scripts=[S + "critical_window_rerun/rerun_boxes.py", S + "critical_window_rerun/rig_cert.py", S + "critical_window_rerun/recert_first.py",
                 S + "critical_window_rerun/verify_exact_cover.py", S + "critical_window_rerun/summarize.py"],
        cmd=["python -I launch_rerun.py 3 (작업자 셋; 하나면 python -I rerun_boxes.py 0 1)", "python -I recert_first.py A29 (G06, G07, G08, G13도)",
             "python -I verify_exact_cover.py > verify_exact_cover_out.txt", "python -I summarize.py > summary_out.txt (기록 ra4c01fc의 cert2/cert3 경로와 verify_A00.json이 필요)",
             "(기록 인증서의 정정 후 여백 검증기는 critical_window/verify_margins.py)"],
        expect="모든 셀 여유 양수; 최소 여유 [D15:최소여유]([D15:최소자리]); verify_exact_cover: ALL CHECKS PASSED",
        outputs=[S + "critical_window_rerun/verify_exact_cover_out.txt", S + "critical_window_rerun/summary_out.txt"],
        time="[D15:시간]"),
    "window-mass-constant": dict(
        scripts=[S + "r8a9b11e/ul_iv_fixed.py"],
        cmd=["python -I ul_iv_fixed.py 25000 1600 1200 0.1 6400 4", "python -I ul_iv_fixed.py 25000 800 600 0.1 3200 4"],
        expect="$\\mathsf w_0\\ge0.71216801$ (1600×1200), $0.70623905$ (800×600)",
        outputs=[S + "r8a9b11e/outputs_fixed/ul_iv_fixed_1600x1200.txt", S + "r8a9b11e/outputs_fixed/ul_iv_fixed_800x600.txt"],
        timefiles=[S + "r8a9b11e/outputs_fixed/ul_iv_fixed_1600x1200.txt"]),
    "zeta-constants": dict(
        scripts=[S + "zeta_constants/zeta_iv.py"],
        cmd=["python -I zeta_iv.py 4000 4000"],
        expect="$\\mathsf z_{3/2}\\in[2.6123753485,2.6123753488]$, $\\mathsf z_{-1/2}\\in[-0.2078862249784,-0.2078862249773]$, "
               "$\\mathsf z_{1/2}\\in[-1.4603545088096,-1.4603545088095]$; 셋 다 진술의 구간 안(`subset of … True`)",
        outputs=[S + "zeta_constants/zeta_iv_out.txt"],
        time="약 4초(2026-11-13, 다른 계산과 코어 공유)"),
    "band-check": dict(
        scripts=[S + "band_check/band_iv.py", S + "band_check/band_cells.py", S + "band_check/band_read.py"],
        cmd=["python -I band_iv.py 0.71216 0 4000", "python -I band_cells.py 0.71216 0 4000 band_cells_CE0.tsv",
             "python -I band_read.py band_cells_CE0.tsv band_iv_out_CE0.txt"],
        expect="certified min ratio = 1.355874(첫 소구간 $[1/2,12001/24000]$); 판독 최솟값 $1.3558739652$, 문턱 $1.3558$ 미만 소구간 0개",
        outputs=[S + "band_check/band_iv_out_CE0.txt", S + "band_check/band_cells_CE0.tsv", S + "band_check/band_read_out_CE0.txt"],
        time="`band_iv.py` 약 40초, `band_cells.py` 약 34초, `band_read.py` 약 2초(2026-11-13, 다른 계산과 코어 공유)"),
    "induction-rows": dict(
        scripts=[S + "induction_rows/induction_rows.py"],
        cmd=["python -I induction_rows.py ../../r19de912/v2run20000-rows.tsv"],
        expect="실패 행 0; 최소 여유 42 ($m=10001$)",
        outputs=[S + "induction_rows/induction_rows_out.txt"]),
    "theorem-U-constant": dict(
        scripts=[S + "theorem_U_constant/theorem_U_iv.py"],
        cmd=["python -I theorem_U_iv.py 8000 8000", "python -I theorem_U_iv.py 16000 16000"],
        expect="$C_{\\mathrm I}+C_{\\mathrm X}\\le50.59610054\\le50.62$",
        outputs=[S + "theorem_U_constant/theorem_U_iv_out.txt", S + "theorem_U_constant/theorem_U_iv_out_32000.txt"]),
    "theorem-D-base": dict(
        scripts=[S + "theorem_D_base/thmD_base_iv.py"],
        cmd=["python -I thmD_base_iv.py"],
        expect="min $q$ at $(m,d)=(689,39)$: $0.85613376\\ldots$; all $q\\in[0.856,1.392]$: True",
        outputs=[S + "theorem_D_base/thmD_base_iv_out.txt"]),
    "prop-W-thirteen": dict(
        scripts=[S + "prop_W_thirteen/iv13.py"],
        cmd=["python -I iv13.py"],
        expect="min lower end of $L-R$: $49.67184940\\ldots$; all 13 pass: True",
        outputs=[S + "prop_W_thirteen/iv13_out.txt"]),
    "Q-fin-1130": dict(
        scripts=[S + "Q_fin_1130/qfin_iv.py", S + "Q_fin_1130/extract_inputs.py"],
        cmd=["python -I extract_inputs.py", "python -I qfin_iv.py 2001 3130 2 0 qfin_iv_result_p0.jsonl",
             "python -I qfin_iv.py 2001 3130 2 1 qfin_iv_result_p1.jsonl", "python -I summarize.py"],
        expect="1130열 모두 통과; 최솟값 열 $k=3130$의 $0.785457$",
        outputs=[S + "Q_fin_1130/summarize_out.txt", S + "Q_fin_1130/qfin_iv_out_p0.txt", S + "Q_fin_1130/qfin_iv_out_p1.txt"],
        time="840초(두 프로세스 동시; `qfin_iv_out_p0/p1.txt`의 elapsed)"),
    "window-mass-env": dict(
        scripts=[S + "window_mass_env/cert_Cb_iv.py", S + "window_mass_env/cert_interval_iv.py", S + "window_mass_env/check_table_iv.py",
                 S + "r030ffae_window/work/cert_Cb_range.py"],
        cmd=["python -I check_table_iv.py", "python -I cert_interval_iv.py", "python -I cert_Cb_iv.py 1 2280",
             "python -I cert_Cb_iv.py 2280 3000", "python -I summarize.py"],
        expect="(가) $1\\le q\\le2999$ 전부 통과; (나) 열일곱 구간의 최소 상대 여유 $0.011251$($\\xi=0.912$)",
        outputs=[S + "window_mass_env/summarize_out.txt", S + "window_mass_env/cert_interval_iv_out.txt"],
        time="(나) 1280초, (가) 5171초·4206초(두 프로세스 동시), 표 검사 14초(각 출력의 total 줄, `D항목_초안.md`)"),
    "bprime-boxes": dict(
        scripts=[S + "bprime_boxes/bprime_iv.py", S + "bprime_boxes/ivbox_lib.py", S + "bprime_boxes/bprime_summary.py"],
        cmd=["python -I bprime_iv.py box 0 2", "python -I bprime_iv.py box 1 2", "python -I bprime_iv.py tail",
             "python -I bprime_iv.py checks", "python -I bprime_summary.py"],
        outputs=[S + "bprime_boxes/bprime_result.txt", S + "bprime_boxes/tail_out.txt"],
        time="프로세스 2개로 $914$초, 꼬리 $3$초(`log_box_…_p0.txt`의 done 줄)"),
    "band-boxes": dict(
        scripts=[S + "band_boxes/band_iv.py", S + "band_boxes/band_summary.py", S + "band_boxes/run_all.sh"],
        cmd=["sh run_all.sh", "python -I band_summary.py"],
        expect="최솟값 (ㄱ) $1.0091268$, (ㄴ) $1.0066914$, (ㄷ) $1.0136495$, (ㄹ) $1.0091044$; 꼬리 (ㄱ) $1.12224$",
        outputs=[S + "band_boxes/band_result.txt"],
        time="프로세스 2개로 각 $340$초에서 $430$초, 꼬리 각 $3$초(`band_result.txt`의 wall 줄)"),
    "m1-column-reading": dict(
        scripts=[S + "m1_column_reading/m1_read.py"],
        cmd=["python -I m1_read.py ../../r19de912/v2run20000-rows.tsv"],
        expect="구조 실패 행 0; 위반 0; $\\max(m_1'(k)-k)/k^{2/3}=0.709457$ ($k=3136$)",
        outputs=[S + "m1_column_reading/m1_read_out.txt"]),
    "H-star-plus-interval": dict(
        scripts=[S + "H_star_plus/hplus_interval.py"],
        cmd=["python -I hplus_interval.py 0.2"],
        expect="영역 A $\\le0.83202474$, B $\\le0.63468646$, C $\\le0.83207358$",
        outputs=[S + "H_star_plus/hplus_interval_out.txt"]),
    "AR-integrals": dict(
        scripts=[S + "AR_integrals/ar_integrals_iv.py"],
        cmd=["python -I ar_integrals_iv.py"],
        outputs=[S + "AR_integrals/ar_integrals_iv_out.txt"]),
    "band-LP": dict(
        scripts=[S + "band_LP/part_ga_na.py", S + "band_LP/part_da.py", S + "band_LP/part_ra.py", S + "band_LP/bandlib.py"],
        cmd=["python -I part_ga_na.py", "python -I part_da.py 9467 22000 out_da_9467_22000 9466 9467 9472",
             "python -I part_da.py 22001 38886 out_da_22001_38886 38886", "python -I part_ra.py 6668 8000 out_ra_6668_8000 6668 7275",
             "python -I part_ra.py 8001 9466 out_ra_8001_9466 9466", "(인자는 출력 파일에서 복원; 명령 기록 없음)"],
        expect="(나) $F_k(103)$의 하계가 음인 $k$ 없음(최소 $3.85784634\\times10^{-7}$, $k=38887$); (다)·(라) 실패 블록 0",
        outputs=[S + "band_LP/out_ga_na.txt", S + "band_LP/out_da_9467_22000.txt", S + "band_LP/out_da_22001_38886.txt",
                 S + "band_LP/out_ra_6668_8000.txt", S + "band_LP/out_ra_8001_9466.txt"],
        time="(가)(나) 25.6초; (다) 222초·384초, (라) 244초·153초(각 `out_*.txt`의 끝 줄)"),
    "pair-one-variable": dict(
        scripts=[S + "pair_one_variable/pair_iv.py"],
        cmd=["python -I pair_iv.py"],
        outputs=[S + "pair_one_variable/pair_iv_out.txt"]),
    "M-natural-integrals": dict(
        scripts=[S + "M_natural/j_integrals_iv.py"],
        cmd=["python -I j_integrals_iv.py"],
        outputs=[S + "M_natural/j_integrals_iv_out.txt"]),
    "four-families": dict(
        scripts=[S + "four_families/families_iv.py"],
        cmd=["python -I families_iv.py"],
        outputs=[S + "four_families/families_iv_out.txt"]),
}

HEAD = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}\s*(.*)$")
CODE_EXT = (".py", ".c", ".sh", ".bat")


def chapter_order(name):
    m = re.match(r"(?:부록D_)?장(\d+)([A-Z]?)\.md", name)
    return (int(m.group(1)), m.group(2)) if m else (99, name)


def first_sentence(text, limit=None):
    """괄호 밖·수식 밖의 첫 「. 」에서 자른다. limit가 있으면 수식을 끊지 않는 자리에서 더 자른다."""
    depth, dollars = 0, 0
    cut = len(text)
    for i, ch in enumerate(text):
        if ch == "$":
            dollars += 1
        elif dollars % 2 == 0:
            if ch in "(〔[":
                depth += 1
            elif ch in ")〕]":
                depth = max(0, depth - 1)
            elif ch == "." and depth == 0 and (i + 1 == len(text) or text[i + 1] == " "):
                cut = i + 1
                break
    s = text[:cut].strip()
    if limit and len(s) > limit:
        d = 0
        best = None
        for i, ch in enumerate(s):
            if ch == "$":
                d += 1
            if i >= limit:
                break
            if d % 2 == 0 and ch in " ,，;":
                best = i
        if best is None:
            best = limit
            while s[:best].count("$") % 2:
                best = s.find("$", best) + 1
        s = s[:best].rstrip(" ,;") + " …"
    return s


def items():
    out = []
    for p in sorted(glob.glob(os.path.join(CHAP, "부록D_장*.md")), key=lambda q: chapter_order(os.path.basename(q))):
        cur = None
        for ln in io.open(p, encoding="utf-8").read().split("\n"):
            m = HEAD.match(ln)
            if m:
                cur = dict(name=m.group(1), file=os.path.basename(p), stmt="", grade="", result="", tag="", data="", algo="")
                out.append(cur)
                continue
            if not cur:
                continue
            for key, field in (("**확인하는 진술.**", "stmt"), ("**산술 등급.**", "grade"), ("**결과.**", "result"),
                               ("**자료.**", "data"), ("**알고리즘.**", "algo")):
                if ln.startswith(key):
                    cur[field] = ln[len(key):].strip()
            if ln.startswith("**독립 재계산.**"):
                t = re.search(r"〔([^〕]*)〕", ln)
                cur["tag"] = t.group(1) if t else ""
    return out


def readme_tables():
    """두 표에서 경로 → SHA, 라벨 → [(경로, SHA)]."""
    sha, by_label = {}, {}
    for ln in io.open(README, encoding="utf-8").read().split("\n"):
        if not ln.startswith("| `"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        path = cells[0].strip("`")
        h = cells[-1].strip("`")
        if not re.fullmatch(r"[0-9a-f]{64}", h):
            continue
        sha[path] = h
        if len(cells) == 4:
            for lab in re.split(r",\s*", cells[2]):
                by_label.setdefault(lab.strip(), []).append((path, h))
    return sha, by_label


def tag_data(tag):
    m = re.search(r"자료\s+([^;〕]*)$", tag) or re.search(r"자료\s+([^;〕]*)", tag)
    return m.group(1).strip() if m else "—"


TIME_PATS = [
    (re.compile(r"total time\s+([\d.]+)\s*s"), 1),
    (re.compile(r"\btotal\s+([\d.]+)\s*s\b"), 1),
    (re.compile(r"\belapsed\s+([\d.]+)"), 1),
    (re.compile(r"finished in\s+([\d.]+)\s*s"), 1),
    (re.compile(r";\s*time\s+([\d.]+)\s*s"), 1),
    (re.compile(r"worker seconds:\s*\[([\d,\s]+)\]"), 2),
]
TIMESUM_PAT = re.compile(r"\(([\d.]+)\s*s\)|seconds=([\d.]+)")


def fmt_sec(x):
    return f"{x:.1f}초" if x < 10 else f"{x:.0f}초" if x < 600 else f"{x:.0f}초(약 {x / 60:.0f}분)"


def read_time(files, timesum=False):
    found = []
    for rel in files:
        p = os.path.join(BUNDLE, rel)
        if not os.path.isfile(p) or os.path.getsize(p) > 5_000_000:
            continue
        try:
            txt = io.open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        val = None
        if timesum:
            xs = [float(a or b) for a, b in TIMESUM_PAT.findall(txt)]
            if xs:
                val = f"{fmt_sec(sum(xs))}(`{os.path.basename(rel)}`의 줄별 시간 합)"
        if val is None:
            for pat, kind in TIME_PATS:
                ms = pat.findall(txt)
                if ms:
                    if kind == 1:
                        val = f"{fmt_sec(float(ms[-1]))}(`{os.path.basename(rel)}`)"
                    else:
                        secs = [float(x) for x in ms[-1].split(",")]
                        val = f"{fmt_sec(max(secs))}(프로세스 {len(secs)}개 동시; `{os.path.basename(rel)}`)"
                    break
        if val:
            found.append(val)
    return "; ".join(found) if found else "—"


def code_command(rel):
    """기록 코드의 실행 명령: 인자를 안 읽으면 python -I, 읽으면 머리 주석의 사용법 또는 (인자 확인 필요)."""
    p = os.path.join(BUNDLE, rel)
    base = os.path.basename(rel)
    if rel.endswith(".c"):
        return "컴파일 뒤 실행(README 「컴파일 옵션」)"
    if not os.path.isfile(p):
        return "(인자 확인 필요)"
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    if not re.search(r"sys\.argv|argparse", txt):
        return f"`python -I {base}`"
    head = txt[:4000]
    m = re.search(r"python3?\s+(?:-I\s+)?(?:\S*/)?" + re.escape(base) + r"[^\n`]*", head)
    if m:
        cmd = re.sub(r"^python3?\s+(-I\s+)?", "python -I ", m.group(0)).strip().rstrip("\"'").strip()
        return f"`{cmd}`"
    return "(인자 확인 필요)"


def esc(s):
    s = re.sub(r"\$[^$]*\$", lambda m: m.group().replace("|", r"\vert "), s)
    return s.replace("\n", " ")


def row(it, sha, by_label, include_all, margins):
    name = it["name"]
    stmt = first_sentence(it["stmt"], 70)
    if name in IN_PROGRESS and not include_all:
        return [f"D.{{{{D:{name}}}}}", stmt] + [PH] * 6 + [margins.get(name, MARGIN_PH), PH]
    grade = first_sentence(it["grade"])
    rerun = tag_data(it["tag"]) if it["tag"] else "—"
    cfg = CONFIG.get(name)
    if cfg:
        scripts = cfg["scripts"]
        folder = os.path.dirname(scripts[0])
        cmds = "; ".join(c if c.startswith("(") else f"`{c}`" for c in cfg["cmd"])
        cmds = f"[`{folder}/`] " + cmds
        outs = [(o, sha.get(o)) for o in cfg.get("outputs", [])]
        expect = cfg.get("expect") or first_sentence(it["result"], 110)
        tfiles = list(dict.fromkeys(cfg.get("timefiles", []) + cfg.get("outputs", [])))
        tm = cfg.get("time") or read_time(tfiles, cfg.get("timesum", False))
        if cfg.get("note"):
            rerun = f"{rerun} ({cfg['note']})"
    else:
        files = by_label.get(name, [])
        seen, code, outsl = set(), [], []
        for path, h in files:
            if h in seen:
                continue
            seen.add(h)
            (code if path.endswith(CODE_EXT) else outsl).append((path, h))
        if code:
            scripts = [c[0] for c in code[:3]]
            cmds = "; ".join(code_command(c) for c in scripts)
        else:
            m = re.search(r"`([^`]*\.(?:py|c))`", it["data"])
            scripts = [m.group(1) + " (묶음에 없음)"] if m else []
            cmds = "(인자 확인 필요)" if m else "—"
        outs = outsl[:2]
        expect = first_sentence(it["result"], 110)
        tm = read_time([o for o, _ in outs])
        if len(code) > 3:
            scripts.append(f"외 {len(code) - 3}개")
    sc = ", ".join(f"`{s}`" if not s.startswith("외 ") and "(묶음에 없음)" not in s else s for s in scripts) or "—"
    oc = "; ".join(f"`{o}` `{h}`" if h else f"`{o}` (README 표에 없음)" for o, h in outs[:2]) or "—"
    if len(outs) > 2:
        oc += f"; 외 {len(outs) - 2}개(README 표)"
    return [f"D.{{{{D:{name}}}}}", stmt, sc, cmds, expect, oc, tm, grade, margins.get(name, MARGIN_PH), rerun]


INTRO = (
    "# 재실행표\n\n"
    "부록 D의 항목마다 그 계산을 이 묶음에서 다시 돌리는 법을 한 줄로 적은 표다. 「스크립트」는 이 글의 재계산 파일"
    "(`세션_재계산/` 아래)이 있으면 그것을, 없으면 연구 기록의 코드 사본을 가리킨다(경로는 `원고_자료/` 기준). "
    "「실행 명령」의 대괄호는 명령을 돌릴 폴더이고, 모든 파이썬 명령은 `python -I`로 돌린다(README 「실행 환경」). "
    "「기대 출력」은 결과 줄 또는 출력 파일의 핵심 수치이고, 「출력 파일·SHA-256」은 README 표의 값이다. "
    "「실행 시간」은 출력·로그에 남은 시간 기록을 읽은 것이며 기록이 없으면 「—」이다(이 기계: 4코어, 다른 계산과 공유). "
    "「최소 여유」는 확인하는 진술의 문턱에 대한 가장 작은 여유를 결과 줄에서 옮긴 것이고, 「(계산 뒤 채움)」은 계산이 진행 중이라 아직 적지 않은 칸이다. "
    "「재실행」은 부록 D 꺾쇠 요약의 자료 항목(기록 / 이 글 / 기록·이 글)이다. 「(진행 중)」 칸은 계산이 끝난 뒤 채운다. "
    "「(인자 확인 필요)」는 코드가 인자를 읽지만 그 값을 자료에서 찾지 못한 경우다. "
    "몇 분 안에 끝나는 축소판은 `빠른_확인.py`가 차례로 돌린다. 이 표는 `scripts/_gen_재실행표.py`가 부록 D와 README에서 만든다.\n\n"
)


def main():
    args = sys.argv[1:]
    include_all = "--all" in args
    out = OUT_DEFAULT
    if "--out" in args:
        out = os.path.join(ROOT, args[args.index("--out") + 1])
    sha, by_label = readme_tables()
    margins = json.load(io.open(MARGIN_FILE, encoding="utf-8")) if os.path.exists(MARGIN_FILE) else {}
    its = items()
    L = ["| 라벨 | 확인하는 진술 | 스크립트 | 실행 명령 | 기대 출력 | 출력 파일·SHA-256 | 실행 시간 | 산술 등급 | 최소 여유 | 재실행 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for it in its:
        L.append("| " + " | ".join(esc(c) for c in row(it, sha, by_label, include_all, margins)) + " |")
    text = INTRO + "\n".join(L) + "\n"
    old = io.open(out, encoding="utf-8").read() if os.path.exists(out) else None
    if old != text:
        io.open(out, "w", encoding="utf-8", newline="\n").write(text)
    miss_sha = sum(1 for l in L[2:] if "README 표에 없음" in l)
    print(f"항목 {len(its)}개, 진행 중 {sum(1 for i in its if i['name'] in IN_PROGRESS and not include_all)}개, "
          f"README 표에 없는 출력 {miss_sha}개; {'갱신' if old != text else '변화 없음'}: {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
