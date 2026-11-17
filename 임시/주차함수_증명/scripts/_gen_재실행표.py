# -*- coding: utf-8 -*-
"""원고_자료/재실행표.md(부록 D 항목 → 다시 돌리는 법 대응표)를 만든다. 멱등: 다시 돌리면 표 전체를 새로 쓴다.

한 행 = 부록 D 항목 하나(머리 `### D.{{D:이름}}`). 열:
  라벨 | 확인하는 진술(첫 구절) | 스크립트 | 실행 명령 | 기대 출력 | 출력 파일·SHA-256 | 실행 시간 | 산술 등급 | 최소 여유 | 재실행
읽는 곳:
  - 확인하는 진술·산술 등급·결과·꺾쇠 요약 〔구현; 범위; 산술; 자료〕는 장v2/부록D_장*.md에서 자동으로 읽는다.
    산술 등급은 그 줄의 첫 문장, 재실행은 꺾쇠의 자료 항목(기록 / 이 글 / 기록·이 글)이다.
  - 스크립트·실행 명령·출력 파일은 아래 CONFIG(이 글의 재계산 폴더가 있는 항목)에서, 없으면 README 「파일 목록」 표에서
    그 라벨이 붙은 기록 코드·출력 파일을 읽는다. 기록 코드의 실행 명령은 RECORD_CMDS(코드·출력·로그에서 확인한 실제 인자)에
    있으면 그것, 없고 코드가 인자를 읽지 않으면 `python -I <스크립트>`, 인자를 읽고 머리 주석에 사용법이 있으면 그 줄,
    없으면 「(인자 확인 필요)」. 같은 폴더의 모듈을 읽는 기록 코드 사본은 `python -I` 대신 `python -E -s`(README 「실행 환경」).
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
    "exact-n20000": dict(
        scripts=[S + "left_columns_k2_120/code/left_columns.py", S + "left_columns_k2_120/code/positive_columns.py",
                 S + "left_columns_k2_120/code/summarize.py", S + "left_columns_k2_120/code/exact_check.py",
                 S + "left_columns_k2_120/indep/indep_margin.py",
                 S + "witness_offset_iv/code/witness_offset_iv.py", S + "witness_offset_iv/code/summarize.py"],
        cmd=["python -I left_columns.py radii --cmax 121 --N 3000 --out radii.json",
             "python -I left_columns.py run --kmin 2 --kmax 70 --radii radii.json --nmax 10000 --nmin 12 --out ../results_k2_70.jsonl",
             "python -I left_columns.py run --kmin 71 --kmax 120 --radii radii.json --nmax 10000 --nmin 12 --out ../results_k71_120.jsonl",
             "python -I summarize.py ../results_k2_70.jsonl ../results_k71_120.jsonl --out ../summary.json",
             "python -I exact_check.py --nmax 300 --cmax 121 --out ../exact_check.json",
             "cd ../indep && python -I make_certs.py --ks 2 3 7 30 60 120 --nmax 10000 --out sample_certs.json",
             "cd ../indep && python -I indep_lastcar.py 2 3 7 30 60 120 --bits 160 --from-cert sample_certs.json --output indep_lastcar_out.json",
             "cd ../indep && python -I indep_margin.py --ks 2 3 7 30 60 120 --nmax 10000 --bits 160 --out indep_margin.json",
             "cd ../indep && python -I indep_margin.py --ks 2 3 --nmax 10000 --bits 160 --nmin 12 --out indep_margin_k2_3_n12.json",
             "[witness_offset_iv/code] python -I witness_offset_iv.py --rows ../../../r19de912/evidence__peer__cert__v2run20000-rows.tsv --out ../witness_offset_iv.json --dps 30",
             "[witness_offset_iv/code] python -I summarize.py ../witness_offset_iv.json"],
        expect="(ㄱ) 열 $2\\le k\\le120$: total comparisons 1,175,466, total failures 0; min relative margin $1.2608\\times10^{-4}$ at k=6 n=13; exact_check success: True(enclosure 36,421·rescaled 71,638·sign 21,166, failures 0); indep_margin의 표본 여섯 열에서 같은 판정·같은 최소 여유. (ㅂ) all within [0.85,1.99]: True; 두 범위 [0.889979773145161, 1.986242781217464]·[0.850826875264814, 1.875832792791377](바깥쪽 세 자리 $[0.889,1.987]$·$[0.850,1.876]$), min margin $8.2688\\times10^{-4}$, max interval width $7.45\\times10^{-28}$",
        outputs=[S + "left_columns_k2_120/summary.json", S + "left_columns_k2_120/results_k2_70.jsonl", S + "left_columns_k2_120/results_k71_120.jsonl",
                 S + "left_columns_k2_120/exact_check.json", S + "left_columns_k2_120/indep/indep_lastcar_out.json",
                 S + "left_columns_k2_120/indep/indep_margin.json",
                 S + "witness_offset_iv/witness_offset_iv.json"],
        time="열 계산·비교는 프로세스 2개가 330초·286초(벽시계 약 5.5분; `logs/run_k2_70.log`·`run_k71_120.log`), 반지름 추정 16초, 정확값 대조 52초, 독립 프로그램은 표본 열마다 61–157초(`indep/*.log`); (ㅂ)의 구간 재계산은 약 10초(`witness_offset_iv/logs/run.log`); 다른 조각 (ㄴ)(ㄷ)(ㄹ)(ㅁ)과 (ㄱ)의 $k\\ge121$은 기록 자료",
        note="(ㄱ)의 열 $2\\le k\\le120$과 (ㅂ)만 이 글의 재계산"),
    "column-certification-k500": dict(
        scripts=[S + "column_k500_iv/lastcar_iv.py", S + "column_k500_iv/colk500.py", S + "column_k500_iv/summarize.py"],
        cmd=["python -I colk500.py --worker 0 --nworkers 2", "python -I colk500.py --worker 1 --nworkers 2",
             "python -I summarize.py > summary_out.txt", "python -I compare_indep.py > compare_indep_out.txt"],
        expect="380열 실패 0(직접 차분 20,368,570개·비 비교 10,302,655개); 최소 상대 여유 $1.3778\\times10^{-5}$($k=500$, $n=2k+1$)",
        outputs=[S + "column_k500_iv/summary_out.txt", S + "column_k500_iv/compare_indep_out.txt", S + "column_k500_iv/res/SHA256SUMS.txt"],
        time="작업자 2개 각 약 9500초(공유 기계; 벽시계 2.7시간; `run_w0.log`·`run_w1.log`)"),
    "central-gap-integer": dict(
        scripts=[S + "icert_py_full/rev_icert_unpaired_fast.py", S + "icert_py_full/worker.py", S + "icert_py_full/launch.py", S + "icert_py_full/stop.py", S + "icert_py_full/summarize.py", S + "icert_py_full/make_draft.py"],
        cmd=["python -I launch.py 4", "python -I summarize.py", "python -I make_draft.py"],
        expect="$1001\\le k\\le10000$의 9000열 전부에서 네 출력값이 `icert.c`의 `out_8_10000.txt`와 비트 동일(불일치 0, `ok` 거짓 0); `summary.json`의 `complete` 참",
        outputs=[S + "icert_py_full/summary.json", S + "icert_py_full/launches.txt", S + "icert_py_full/out_1001_1100.txt", S + "icert_py_full/out_9632_10000.txt"],
        time="작업자 1→4→2→3개(11-13 17:46–11-15 13:51), 정지 뒤 4개(11-15 21:00–11-16 08:01); 열별 시간 합 573,394초(159시간; 코어를 나눠 쓴 구간 포함), 열당 최대 421초($k=9537$)"),
    "moment-certification": dict(
        scripts=[S + "moment_cert_iv/mcert_iv.py", S + "moment_cert_iv/sweep_ct_mp.py", S + "moment_cert_iv/summarize_nb.py",
                 S + "moment_cert_iv/summarize.py", S + "moment_cert_iv/compare.py", S + "moment_cert_iv/nM.py"],
        cmd=["python -I mcert_iv.py sweep_nb A5 sweep_ct_A5.jsonl --count",
             "python -I sweep_ct_mp.py A3 0", "python -I sweep_ct_mp.py A3 1", "python -I sweep_ct_mp.py A3 2", "python -I sweep_ct_mp.py A3 3",
             "python -I summarize_nb.py > summary_noblas.txt",
             "python -I mcert_iv.py sweep 0 2 sweep_p0.jsonl", "python -I mcert_iv.py sweep 1 2 sweep_p1.jsonl",
             "python -I summarize.py > summary.txt", "python -I compare.py", "python -I nM.py"],
        expect="(A3)(A5) 1500열 60,479,535개 위치 전부 통과(fails 0; BLAS 없는 연산 수 한계 판, 샤드 넷은 동시에 띄움); 상대 여유 하계의 최솟값 $0.137916$((A3) $k=840$); BLAS 행렬곱 대조 판(`sweep 0 2`·`sweep 1 2`)과 1500열 판정 일치; $n_{\\mathrm M}(k)$ 1160열 기록과 일치",
        outputs=[S + "moment_cert_iv/summary_noblas.txt", S + "moment_cert_iv/sweep_ct_A5.jsonl", S + "moment_cert_iv/sweep_ct_A3_s0.jsonl", S + "moment_cert_iv/sweep_ct_A3_s1.jsonl",
                 S + "moment_cert_iv/sweep_ct_A3_s2.jsonl", S + "moment_cert_iv/sweep_ct_A3_s3.jsonl", S + "moment_cert_iv/summary.txt", S + "moment_cert_iv/sweep_p0.jsonl",
                 S + "moment_cert_iv/sweep_p1.jsonl", S + "moment_cert_iv/compare_out.txt", S + "moment_cert_iv/nM_out.txt"],
        time="BLAS 없는 판: (A5) 프로세스 1개(다른 계산과 코어를 나눔; 11-13 22:29–11-15 14:14), (A3) 샤드 4개(11-15 14:14·15:37–21:00); 열별 소요 시간 합 219,744초. 대조 BLAS 판: 프로세스 2개(BLAS 스레드 1)로 2시간 10분(15:25–17:36; 부록 D 범위 밖 열 포함), CPU 합 15,164초 가운데 (A3)(A5) 9,786초"),
    "column-certificates-501-2000": dict(
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
    "logconcavity-failure-n80": dict(
        scripts=[S + "logconcavity_n80/lc_n80.py"],
        cmd=["python -I lc_n80.py"],
        expect="first failure: (n, l) = (80, 40); three integers equal to appendix D: True",
        outputs=[S + "logconcavity_n80/lc_n80_out.txt"]),
    "c50": dict(
        scripts=[S + "c50_iv/c50iv.c", S + "c50_iv/make_tables_iv.py", S + "c50_iv/postprocess_iv.py"],
        cmd=["python -I make_tables_iv.py 50100", "cmd /c build.bat", "c50iv.exe 20000 5 2 19999 64 2 runs/c20 .",
             "c50iv.exe 50000 20001 10000 49999 64 2 runs/c50 .", "(후처리·대조는 `run_commands.txt`)"],
        expect="미결 위치 0, 최대 상대 폭 $2.25\\times10^{-12}$",
        outputs=[S + "c50_iv/runs/c50_summary.json", S + "c50_iv/runs/c20_summary.json"],
        time="표 41.7초, C20 194.6초, C50 3982.6초(약 66분; `run_commands.txt`)"),
    "critical-window-rig": dict(
        scripts=[S + "critical_window_rerun/rerun_boxes.py", S + "critical_window_rerun/rig_cert.py", S + "critical_window_rerun/recert_first.py",
                 S + "critical_window_rerun/verify_exact_cover.py", S + "critical_window_rerun/summarize.py"],
        cmd=["python -I check_fixes.py > check_fixes_out.txt (코드 자체 검사)", "python -I launch_rerun.py 2 (작업자 둘; 하나면 python -I rerun_boxes.py 0 1)", "python -I recert_first.py A29 (G06, G07, G08, G13도; python -I postrun.py가 본 실행 뒤 다섯을 잇는다)",
             "python -I verify_exact_cover.py > verify_exact_cover_out.txt", "python -I summarize.py > summary_out.txt"],
        expect="모든 셀 여유 양수; 최소 여유 $0.001827$(A00, $\\hat x\\in[9.8,10]$); verify_exact_cover: ALL CHECKS PASSED",
        outputs=[S + "critical_window_rerun/verify_exact_cover_out.txt", S + "critical_window_rerun/summary_out.txt"],
        time="상자별 소요 시간의 합 $17.5$시간(첫 셀 재인증 다섯 포함), 상자당 $12$–$38$분, 벽시계 $8$시간 $51$분(작업자 둘)"),
    "zeta-constants": dict(
        scripts=[S + "zeta_constants/zeta_iv.py"],
        cmd=["python -I zeta_iv.py 4000 4000"],
        expect="$\\mathsf z_{3/2}\\in[2.6123753485,2.6123753488]$, $\\mathsf z_{-1/2}\\in[-0.2078862249784,-0.2078862249773]$, "
               "$\\mathsf z_{1/2}\\in[-1.4603545088096,-1.4603545088095]$; 셋 다 진술의 구간 안(`subset of … True`)",
        outputs=[S + "zeta_constants/zeta_iv_out.txt"],
        time="약 4초(2026-11-13, 다른 계산과 코어 공유)"),
    "stored-table-check": dict(
        scripts=[S + "window_mass_env/check_table_iv.py"],
        cmd=["python -I check_table_iv.py"],
        expect="위반 $0$; 가장 작은 여유 $4.7447\\cdot10^{-13}$($i=0$); 엄격 감소, 최소 감소 $6.643869\\cdot10^{-6}$($i=11999$)",
        outputs=[S + "window_mass_env/check_table_iv_out.txt"],
        time="약 6초(`check_table_iv_out.txt`의 time 줄)"),
    "window-mass-env": dict(
        scripts=[S + "window_mass_env/cert_Cb_iv.py", S + "window_mass_env/cert_interval_iv.py", S + "window_mass_env/check_table_iv.py",
                 S + "r030ffae_window/work/cert_Cb_range.py"],
        cmd=["python -I check_table_iv.py", "python -I cert_interval_iv.py", "python -I cert_Cb_iv.py 1 2280",
             "python -I cert_Cb_iv.py 2280 3000", "python -I summarize.py"],
        expect="(가) $1\\le q\\le2999$ 전부 통과; (나) 열일곱 구간의 최소 상대 여유 $0.011251$($\\xi=0.912$)",
        outputs=[S + "window_mass_env/summarize_out.txt", S + "window_mass_env/cert_interval_iv_out.txt"],
        time="(나) 1981초, (가) 5171초·4206초(두 프로세스 동시), 표 검사 6초(각 출력의 total·time 줄)"),
    "band-boxes": dict(
        scripts=[S + "band_boxes/band_iv.py", S + "band_boxes/ivbox_lib.py", S + "band_boxes/band_summary.py", S + "band_boxes/run_all.sh"],
        cmd=["sh run_all.sh", "python -I band_summary.py"],
        expect="최솟값 $1.0097628$; 꼬리 $1.12224$",
        outputs=[S + "band_boxes/band_result.txt"],
        time="프로세스 2개로 각 $135$초, 꼬리 $1$초(`band_result.txt`의 wall 줄; 2026-11-17 재실행)"),
    "four-families": dict(
        scripts=[S + "four_families_DDLnat/families_iv.py"],
        cmd=["python -I families_iv.py"],
        outputs=[S + "four_families_DDLnat/families_iv_out.txt"]),
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


# 기록 코드 사본 가운데 인자를 읽는 것의 실제 실행 명령(묶음 폴더를 현재 폴더로; 값은 코드의 인자 처리와 묶음의 출력·로그에서
# 확인한 것 — 2026-11-16 ZV3). 키는 원고_자료 기준 경로. 값이 `python`으로 시작하지 않으면 앞에 `python -I` 또는
# (같은 폴더의 모듈을 읽는 사본이면) `python -E -s`를 붙인다(README 「실행 환경」).
RECORD_CMDS = {
    "rce3dc75/icert.c": "컴파일 뒤 `icert rtable.txt 8 10000 <스레드 수> out_8_10000.txt`(README 「컴파일 옵션」; 표는 먼저 `make_rtable.py`)",
    "rce3dc75/make_rtable.py": "make_rtable.py 20002 rtable.txt",
    "rce3dc75/icert_py.py": "icert_py.py rtable.txt 4 5 … 40 551 1000 2500 5000 7500 9000 10000 --cmp out_8_10000.txt",
    "rce3dc75/validate_small.py": "validate_small.py out_8_10000.txt",
    "rce3dc75/v_small_rows.py": "v_small_rows.py 60",
    "r13b0b8f/cert_critical_strip.py": "cert_critical_strip.py --ustep 2 --tstep 2 --out critical-strip-certificate.json",
    "r13b0b8f/indep_cert.py": "indep_cert.py --tdenom 500 --out indep_cert_A.json",
    "r13b0b8f/indep_cert2.py": "indep_cert2.py --rmin 833 --umax_num 70 --out cert2_12_15.json",
    "r13b0b8f/indep_cert3.py": "indep_cert3.py --rmin 966 --udenom 4000 --umax_num 129 --tlo 3/2 --thi 9/5 --ncap 20001 --out cert3_15_18.json",
    "r475ada3/audit_band.py": "audit_band.py",
    "r475ada3/audit_param.py": "audit_param.py 11100 20 21 … 40",
}
THIRD_PARTY = {"numpy", "mpmath", "scipy", "sympy", "gmpy2", "flint", "matplotlib", "pandas"}


def py_prefix(txt):
    """스크립트가 표준 라이브러리·서드파티 밖의 모듈(같은 폴더의 사본)을 읽으면 `python -E -s`, 아니면 `python -I`."""
    for m in re.finditer(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", txt, re.M):
        name = m.group(1)
        if name not in sys.stdlib_module_names and name not in THIRD_PARTY:
            return "python -E -s"
    return "python -I"


def code_command(rel):
    """기록 코드의 실행 명령: RECORD_CMDS에 있으면 그것, 인자를 안 읽으면 python -I(또는 -E -s), 읽으면 머리 주석의 사용법,
    없으면 (인자 확인 필요)."""
    p = os.path.join(BUNDLE, rel)
    base = os.path.basename(rel)
    txt = io.open(p, encoding="utf-8", errors="replace").read() if os.path.isfile(p) else ""
    pre = py_prefix(txt) if txt else "python -I"
    if rel in RECORD_CMDS:
        v = RECORD_CMDS[rel]
        if rel.endswith(".c"):
            return v
        return f"`{v}`" if v.startswith("python") else f"`{pre} {v}`"
    if rel.endswith(".c"):
        return "컴파일 뒤 실행(README 「컴파일 옵션」)"
    if not txt:
        return "(인자 확인 필요)"
    if not re.search(r"sys\.argv|argparse", txt):
        return f"`{pre} {base}`"
    head = txt[:4000]
    m = re.search(r"python3?\s+(?:-I\s+)?(?:\S*/)?" + re.escape(base) + r"[^\n`]*", head)
    if m:
        cmd = re.sub(r"^python3?\s+(-I\s+)?", pre + " ", m.group(0)).strip().rstrip("\"'").strip()
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
    "「실행 명령」의 대괄호는 명령을 돌릴 폴더이고(기록 코드 사본은 그 기록 폴더), 파이썬 명령은 `python -I`로 돌리되 "
    "같은 폴더의 모듈을 읽는 기록 코드 사본은 `python -E -s`로 돌린다(README 「실행 환경」). "
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
