# -*- coding: utf-8 -*-
"""원고_자료/README.md의 「세션이 만든 수정판」 표를 세션 재계산 파일의 현재 SHA-256으로 맞춘다(있으면 갱신, 없으면 추가). 멱등.
인자로 상대 경로(세션_재계산/ 아래의 경로)를 받는다. `--remove <상대경로>`는 지워진 파일의 행을 표에서 뺀다(파일이 남아 있으면 멈춘다).
설명 문단은 PARAS에 없으면 덧붙인다."""
import hashlib
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "원고_자료")
README = os.path.join(BUNDLE, "README.md")

PARAS = [
    ("witness_offset_iv/code/witness_offset_iv.py",
     "`세션_재계산/witness_offset_iv/`는 부록 D의 모든 $n\\le20000$의 단봉성 항목 (ㅂ), 곧 명제 witness-position-bound(5.1절)가 확인하는 증인 위치 차 $n+1-\\ell^\\ast_n-0.59963(n+1)^{2/3}-1.24847(n+1)^{1/3}$을 기록 [r19de912]의 행 자료(자료 묶음의 사본 `r19de912/evidence__peer__cert__v2run20000-rows.tsv`의 봉우리 열 `mode_ell_mid`)에서 방향 반올림 구간(mpmath `iv`, 소수 30자리)으로 다시 계산한 것이다(2026-11-15 세션). 기록의 계산 `mode_offset.py`는 binary64 최근접 반올림의 배정밀도 평가였다. `code/witness_offset_iv.py`는 두 상수를 십진 문자열의 구간으로, 두 지수 $2/3$·$1/3$을 정수 나눗셈의 구간으로 두고 두 범위 $50\\le n\\le900$·$901\\le n\\le20000$마다 구간 아래 끝의 최솟값과 위 끝의 최댓값을 이진 유리수 그대로의 분수와 소수 열다섯 자리(아래 끝 내림·위 끝 올림)로 `witness_offset_iv.json`에 적고, 진술의 구간 $[0.85,1.99]$ 안에 드는지를 정확한 유리수 비교로 판정한다(두 범위 $[0.889979773145161,1.986242781217464]$·$[0.850826875264814,1.875832792791377]$, 모두 안에 듦, 최소 여유 $8.27\\times10^{-4}$, 구간 폭 $7.5\\times10^{-28}$ 이하, 약 10초). `code/summarize.py`가 부록 D 항목과 재실행표에 적는 꼴(바깥쪽 세 자리 $[0.889,1.987]$·$[0.850,1.876]$)로 요약하고, 실행 명령·시각·환경은 `logs/commands.txt`, 설명은 `README_run.md`에 있다."),
    ("left_columns_k2_120/code/left_columns.py",
     "`세션_재계산/left_columns_k2_120/`는 부록 D의 모든 $n\\le20000$의 단봉성 항목 (ㄱ) 가운데 열 $2\\le k\\le120$($\\max(2k+1,12)\\le n\\le10000$)을 기록 [rc9aee43]의 열 인증 코드(`code/positive_columns.py`, 바이트 그대로의 사본)의 열 계산으로 다시 인증한 것이다(2026-11-15 세션). `code/left_columns.py`가 용량 $1\\le c\\le121$의 열을 열별 이진 유리 반지름(`code/radii.json`)으로 한 번씩 계산하고 이웃 세 열을 정확한 유리수 배율의 구간으로 한 반지름에 맞추어 비교하며, 출력은 `results_k2_70.jsonl`·`results_k71_120.jsonl`과 `summary.json`(비교 1,175,466개, 실패 0, 최소 상대 여유 $1.2608\\times10^{-4}$, $k=6$, $n=13$)이다. `code/exact_check.py`→`exact_check.json`은 $n\\le300$의 정확 정수(정리 2.6의 재귀)와 전수 대조, `indep/`는 기록의 독립 프로그램 `indep_lastcar.py`(사본)와 그 재귀로 최소 여유를 재는 `indep_margin.py`를 표본 열 $k\\in\\{2,3,7,30,60,120\\}$에 돌린 것이다. 첫 실행(범위 $2k+1$부터; $n=5,7,9,11$의 네 예외가 드러남)의 결과는 `logs/firstpass/`에 있다."),
    ("r030ffae_window/work/wKrig.npy",
     "`세션_재계산/r030ffae_window/`는 부록 D의 창의 수준 질량 하계 항목의 셀 검사를 시험 함수 격자를 한 점 늘려($0\\le i\\le12927$) 다시 돌린 것이다(2026-11-13 세션). `work/`는 기록 [r030ffae] `evidence/peer/rerun/work/`의 코드 사본에 늘린 표 `xKrig.npy`·`wKrig.npy`(기록의 표는 `xKrig_orig.npy`·`wKrig_orig.npy`; 처음 12,927개 값은 비트 단위로 같다)와 결과 JSON을 더한 것이고, `NEW_*.out`이 실행 출력이다."),
    ("bprime_boxes/ivbox_lib.py",
     "`세션_재계산/bprime_boxes/ivbox_lib.py`는 `band_boxes/band_iv.py`가 쓰는 공용 구간 성분이다. 스칼라는 mpmath `iv`(소수 34자리), 리만 합 벡터는 binary64의 정확 반올림 사칙연산·제곱근만 써서 1 ulp 바깥 밀기와 합의 $1-10^{-11}$ 인자로 아래로 민다. $\\Omega$의 하계는 `window_mass_env/ia.py`의 정확 정의(격자 $i\\mathsf K^{-2/3}$·절점값·Fritsch–Carlson 기울기의 구간)에서 조각별 3차 계수의 바깥 괄호를 만들어 쓰며 조각별 비증가를 구간으로 확인한다. 저장된 봉투 표 $\\hat{\\mathcal T}$는 저장값을 정확한 점 $\\xi^{\\mathcal T}_i=0.0005\\,i$에 둔 선형 보간으로 읽는다."),
    ("band_boxes/band_iv.py",
     "`세션_재계산/band_boxes/`는 부록 D의 띠 정리의 상자 검사 항목을 같은 구간 산술로 다시 계산한 것이다. 상자 안의 모든 경우 가름과 되먹임 폭의 점별 범위를 함께 고려해 식 (8.30) 자체를 아래에서 막는다. `band_iv.py`가 계산, `band_summary.py`가 요약, `run_all.sh`가 실행 순서이고, `compare_record.py`가 기록의 상자 값과 대조한다. $\\Omega$는 `bprime_boxes/ivbox_lib.py`의 정확 정의를 쓴다. 이 글의 방식(`fbox`)은 보조정리 hazard-H1의 $\\mathfrak h(k,\\nu)=\\frac k{k+\\nu}-\\frac k{2k-1}$를 그대로 쓰고, 기록의 상자 방식(`box`)만 기록의 $\\mathfrak h$에 곱해진 인자 $1-0.798(\\nu+1)^{-1/2}-0.81k^{-1/2}$를 그대로 두어 기록 값과 대조한다."),
    ("critical_window_rerun/rig_cert.py",
     "`세션_재계산/critical_window_rerun/`은 부록 D의 임계 창 인증 항목의 44개 상자를 이 글의 코드로 다시 돌린 것이다. `rig_*.py`·`ivio.py`가 계산 코드, `orig/`가 기록의 원본, `boxes.py`·`common.py`·`rerun_boxes.py`·`launch_rerun.py`·`recert_first.py`·`postrun.py`가 상자 모임·실행기·기동기·첫 셀 재인증·뒤처리 기동기다. 이 글의 코드가 기록의 코드와 다른 넷(실수축 나머지의 지수 상수, $\\hat x$ 셀의 격자, 둘러싸기 식 세 곳, $(e^w-1)/w$의 1·2계 도함수 급수의 계수)은 부록 D 항목의 「독립 재계산」에 적혀 있다. $\\hat x$ 셀은 십진 격자 $[1.4+0.2i,1.6+0.2i]$를 품는 바깥 구간으로 두고 Taylor 중심·반지름이 셀을 품게 하며 끝점·중심·반지름·여유를 정확한 이진값으로 저장한다. `verify_exact_cover.py`는 저장된 인증서만 읽어 $\\mathrm{ku}$ 타일링과 $\\mathrm{ku}_{\\mathrm{top}}^3\\cdot10001\\ge1$, 셀의 격자 포함, Taylor 영역의 셀 포함, 여유의 양수성을 허용 오차 없는 유리수로 검사한다(출력 `verify_exact_cover_out.txt`). 인증서는 `cert/`, 상자 자료는 `cache/`, 실행 기록은 `logs/`, 요약은 `summarize.py`→`summary_out.txt`, `_test_exact_grid.py`는 두 셀 시험, `check_fixes.py`→`check_fixes_out.txt`는 코드 자체 검사(둘러싸기의 포함, 급수 상수, 감마 상계, 상자 모임)다."),
    ("window_mass_env/ia.py",
     "`세션_재계산/window_mass_env/`는 부록 D의 창의 수준 질량 하계 항목의 셀 검사((가) $q\\le2999$, (나) 구간 열일곱 개)를 구간 산술로 다시 계산한 것이다(2026-11-13 세션). `ia.py`가 바깥 반올림 구간(binary64의 정확 반올림 사칙연산·제곱근만 사용)과 $\\Omega$의 Hermite 조각·봉투 표·정확 표(mpmath `iv` 25–40자리)를 만들고(세 제타 상수 $\\zeta(\\frac12)$, $\\zeta(-\\frac12)$, $\\zeta(\\frac32)$는 `zeta_constants/zeta_iv_out.txt`의 인증 구간을 바깥쪽으로 넓혀 넣는다), `cert_interval_iv.py`·`cert_Cb_iv.py`가 두 검사를 돌리며, `check_table_iv.py`가 저장된 봉투 표의 하계 조건을 다시 확인하고, `test_ia.py`가 기록의 값이 구간 안에 듦을 확인한다. 출력은 `*_out*.txt`와 `*_result*.json`, 요약은 `summarize_out.txt`."),
    ("c50_iv/c50iv.c",
     "`세션_재계산/c50_iv/`는 부록 D의 $20001\\le n\\le50000$의 오른쪽 절반 인증과 $n\\le20000$의 재인증 항목을 본문의 마지막 차 재귀에서 새로 쓴 C 프로그램 `c50iv.c`로 다시 인증한 것이다(2026-11-13 세션). 아래 끝은 아래 반올림 패스, 위 끝은 위 반올림 패스로 따로 계산하는 binary64 방향 반올림 구간이고, 표 $\\mathrm{Bor}$·$\\mathrm{hB}$는 `make_tables_iv.py`가 mpmath `iv` 40자리로 포위해 바깥 반올림한 이진 표다. 빌드는 `build.bat`(MSVC `/O2 /fp:strict /arch:AVX /openmp`; 어셈블리에 FMA 명령이 없음을 확인). `runs/`에 C20·C50의 요약과 행 파일, $n\\le300$의 정확 정수 대조(`exact_small.py`), 미달 수 재귀 참조 대조(`probe_undercount.py`)의 출력이 있다. 명령은 `run_commands.txt`. 미결 위치 0, 최대 상대 폭 $2.25\\times10^{-12}$."),
    ("column_k500_iv/lastcar_iv.py",
     "`세션_재계산/column_k500_iv/`는 부록 D의 열 인증($121\\le k\\le500$) 항목을 이 글의 새 구현으로 380열 전부 다시 인증한 것이다(2026-11-13 세션). `lastcar_iv.py`는 세 재귀 G·H·E를 쓰지 않고 마지막 차 재귀 $n\\mathfrak e_n=\\mathfrak x\\sum_j\\min(j+1,y)\\mathfrak e_j\\mathfrak e_{n-1-j}$ 하나를 정확한 큰 정수 합성곱의 온라인 분할 정복(Kronecker 포장; 큰 크기는 `decimal`의 수론 변환, 부정확 반올림은 트랩)으로 160비트 고정소수점 정수 구간에서 계산하며, 반올림은 계수를 확정할 때 한 번(아래 끝은 내림, 위 끝은 올림)뿐이라 끝점이 직접 합과 비트 단위로 같다. 연속한 열 열 개가 하나의 정확한 이진 유리수 $\\mathfrak x=e^{-1}(1+c/\\bar k)$를 공유한다. `colk500.py`(`--worker i --nworkers 2`)가 열별 판정·최소 상대 여유·시간을 `res/k<k>.json`에 쓰고(380개; 해시 목록 `res/SHA256SUMS.txt`), `summarize.py`→`summary_out.txt`(380열 실패 0, 직접 차분 20,368,570개·띠 10,302,655개, 최소 상대 여유 $1.3778\\times10^{-5}$($k=500$, $n=2k+1$)), `compare_indep.py`→`compare_indep_out.txt`(기록 검토의 다섯 열과 판정·최대 폭 일치, $k=121$은 모든 끝점 동일; 열별 최소 여유가 기록과 상대 $1.1\\times10^{-35}$ 안), `test_small.py`→`test_small_out.txt`($n\\le7$ 전수·$n\\le120$ 정확 개수 포함, 분할 정복과 직접 합의 일치). 두 작업자 각 약 9500초(공유 기계, 벽시계 2.7시간; `run_w0.log`·`run_w1.log`). `make_draft.py`는 결과에서 부록 D 항목 본문을 만든다."),
    ("moment_cert_iv/mcert_iv.py",
     "`세션_재계산/moment_cert_iv/`는 부록 D의 모멘트 판정 항목 (ㄱ)(두 범위의 재귀 인증; 파일·요약의 A1–A5는 기록의 실행 이름이고 글이 쓰는 두 범위는 A3·A5다)을 구간 산술로 다시 계산한 것이다(2026-11-13 세션). `mcert_iv.py`는 재귀 (7.2)·(7.3)에 $\\hat{\\mathfrak a}_n$을 곱해 나눗셈 없는 네 양의 재귀로 바꾸고, 필요한 끝점만 binary64 구간으로 계산한다(아래 끝 $\\hat{\\mathfrak a}$, $\\hat{\\mathfrak a}\\mathfrak Z^\\flat$, $\\hat{\\mathfrak a}\\mathfrak Z$; 위 끝 $\\hat{\\mathfrak a}$, $\\hat{\\mathfrak a}\\mathfrak Z^{\\mathrm H}$). 합은 행렬곱으로 계산한 뒤 덧셈 순서·융합 여부와 무관한 한계 $(1\\pm u)^{m+1}$($m=6n+3$)로 넓히고 언더플로는 절대 오차로 덮으며, 스칼라 연산은 한 ulp 밖으로 민다. 초등함수와 기록의 binary64 판정식(부록 D 모멘트 판정 항목의 「식」 줄)은 쓰지 않고 $\\mathbb E>0$을 직접 판정한다. 7619열 60,703,015개 위치 전부 통과(실패 0; 프로세스 2개로 약 2시간 10분, CPU 합 15,164초; `sweep_p0.jsonl`·`sweep_p1.jsonl`과 로그). `summarize.py`→`summary.txt`(범위별 집계), `compare.py`→`compare_out.txt`(기록의 여덟 열 대조: 인쇄값이 모두 구간 안), `test_exact.py`→`test_exact_out.txt`(작은 열의 정확 유리수 포함), `nM.py`→`nM.json`·`nM_out.txt`(열별 문턱 $n_{\\mathrm M}(k)$의 정확 유리수 재계산; 1160열 모두 기록과 같음). `make_draft.py`는 결과에서 부록 D 항목 본문을 만든다."),
    ("column_cert_iv/colcert_iv.py",
     "`세션_재계산/column_cert_iv/`는 부록 D의 열 $501\\le k\\le2000$의 열별 갱신 인증서 항목을 라이브러리 함수 가정 없이 방향 반올림 구간으로 다시 계산한 것이다(2026-11-13 세션). `colcert_iv.py`가 열 $501\\le k\\le2000$마다 정리 G′의 조건 (a′)(b′)(c′)를 확인한다: 소인 질량과 창 계수의 양의 재귀는 아래 끝·위 끝 두 줄의 binary64 구간(연산마다 바깥 밀기, 내적은 짝지은 합 나무와 끝의 $(1\\mp2^{-53})^{-(d+1)}$ 인자), 원 위의 격자값은 `ivlib.py`의 자기 구현 구간 FFT(실부·허부 상자, 회전 인자는 mpmath `iv` 표), 주편각은 $\\arctan$ 포위, 스칼라 조립은 mpmath `iv` 소수 40자리다. $k$에 무관한 표(Borel 수, $n\\le2000$의 소인 질량, 회전 인자)는 `tables.py`가 `_cache/bor_pr0.npy`·`_cache/twiddle_2p21.npy`로 만든다(약 1.5분; 33 MB라 묶음에 넣지 않고 다시 만든다). 실행은 `python -I colcert_iv.py --ks 841-2000 --part 0 --nparts 2 --batch 16 --out res_p0.jsonl`과 `--part 1`(각 2.9시간), 열 501–840은 `--ks 501-840 … --out res_ext_p0.jsonl`과 `--part 1`(각 16분)이다. 열별 성분과 판정은 `res_*.jsonl`(binary64 값을 왕복 가능한 전체 자리로), 실행 기록은 `run_*.log`, 요약은 `summary.py`(`summary_all_out.txt`: 1500열 모두 성공, 최소 $\\mathfrak b_0=0.03478$, 최소 여유 $0.02722$, $V$ 위 끝은 저장값 곱의 $1.000007$배 이하), 기록 검토의 40자리 값과의 대조는 `crosscheck_review.py` → `crosscheck_review_out.txt`, numpy FFT와의 대조는 `test_841.txt`·`test_1171.txt`·`test_2000.txt`다. `make_draft.py`는 결과에서 부록 D 항목 본문을 만든다."),
    ("four_families_DDLnat/families_iv.py",
     "`세션_재계산/four_families_DDLnat/families_iv.py`는 부록 D의 네 가족의 첫 열 검사 항목의 모든 값(여유, 하계, 가장자리, 보조정리 조건, 단조성 표본)을 mpmath 구간 산술(소수 30자리)로 다시 계산한다(2026-11-17 세션). 실행은 폴더 안에서 `python -I families_iv.py > families_iv_out.txt`(약 93초)이고 출력은 `families_iv_out.txt`다. `변경.md`는 이 판이 바꾼 함수 `DDL`의 전후를, `결과_요약.md`는 결과값과 실행 기록을 적는다."),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def parse_args(argv):
    """위치 인자는 등록·갱신할 상대 경로, `--remove <상대경로>`는 표에서 지울 행(파일이 지워진 뒤에만)."""
    rels, removes = [], []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--remove":
            if i + 1 >= len(argv):
                print("--remove 뒤에 상대 경로가 없다")
                sys.exit(2)
            removes.append(argv[i + 1])
            i += 2
            continue
        if not a.startswith("--"):
            rels.append(a)
        i += 1
    return rels, removes


def main():
    rels, removes = parse_args(sys.argv[1:])
    s = io.open(README, encoding="utf-8").read()
    head, rest = s.split("## 파일 목록", 1)
    lines = head.split("\n")
    # 표의 범위: "| 경로 | SHA-256 |" 머리 다음부터 빈 줄 전까지
    hi = [i for i, l in enumerate(lines) if l.startswith("| 경로 | SHA-256 |")][0]
    j = hi + 2
    rows = {}
    order = []
    while j < len(lines) and lines[j].startswith("|"):
        cells = [c.strip() for c in lines[j].strip("|").split("|")]
        rows[cells[0].strip("`")] = cells[1].strip("`")
        order.append(cells[0].strip("`"))
        j += 1
    end = j
    order = list(dict.fromkeys(order))  # 동시 편집으로 생긴 중복 행은 첫 자리만 남긴다
    changed = 0
    for rel in rels:
        key = "세션_재계산/" + rel
        p = os.path.join(BUNDLE, key)
        if not os.path.exists(p):
            print("없음:", key)
            sys.exit(1)
        h = sha(p)
        if rows.get(key) != h:
            rows[key] = h
            if key not in order:
                order.append(key)
            changed += 1
    removed = 0
    for rel in removes:
        key = "세션_재계산/" + rel
        if os.path.exists(os.path.join(BUNDLE, key)):
            print("파일이 아직 있어 지우지 않는다:", key)
            sys.exit(1)
        if key in rows:
            del rows[key]
            order = [k for k in order if k != key]
            removed += 1
    table = [f"| `{k}` | `{rows[k]}` |" for k in order]
    lines[hi + 2:end] = table
    head = "\n".join(lines)
    for key, para in PARAS:
        if key not in head.split("| 경로 | SHA-256 |")[1].split("\n\n", 1)[1] and para not in head:
            pass
        tok = "`" + para.split("`")[1] + "`"          # 문단의 첫 경로 토큰으로 유무를 판정(문단 본문이 README에서 다듬어져도 중복 추가하지 않음)
        if tok not in head and para not in head and ("세션_재계산/" + key) in rows:
            head = head.rstrip("\n") + "\n\n" + para + "\n\n"
    s2 = head.rstrip("\n") + "\n\n## 파일 목록" + rest
    io.open(README, "w", encoding="utf-8", newline="\n").write(s2)
    print(f"README 갱신: 행 {changed}개 갱신/추가, {removed}개 삭제, 표 {len(order)}행")


if __name__ == "__main__":
    main()
