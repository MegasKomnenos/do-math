# -*- coding: utf-8 -*-
"""결정 96의 자료 쪽 갱신: 원고_자료/README.md 설명 문단 셋(bprime·band 수정, critical_window_rerun 추가)과 `_patch_README_세션파일.py`의 PARAS,
`_gen_재실행표.py` CONFIG(critical-window-rig 교체, bprime·band의 시간·기대 출력 자리표시자), `_재실행표_여유.json` 셋, `_check_자리표시자.py`가
README·재실행표도 세게 함, zenodo_v4/절차.md 0항에 자리표시자 채움 명시. 멱등."""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sub1(path, old, new, must=True):
    p = os.path.join(ROOT, path)
    s = io.open(p, encoding="utf-8").read()
    if new in s:                 # 이미 반영됨(멱등; 삽입형 치환의 중복 방지)
        return 0
    c = s.count(old)
    if c == 1:
        s = s.replace(old, new); io.open(p, "w", encoding="utf-8", newline="\n").write(s); return 1
    if must:
        print("앵커 수", c, path, old[:60])
    return 0

n = 0
# ---- README 문단 ----
BP_OLD = ("`ivbox_lib.py`가 공용 구간 성분, `bprime_iv.py`가 계산, `bprime_summary.py`가 요약이며 `compare_record.py`가 기록의 상자 값과 대조한다.")
BP_NEW = ("`ivbox_lib.py`가 공용 구간 성분, `bprime_iv.py`가 계산, `bprime_summary.py`가 요약이며 `compare_record.py`가 기록의 상자 값과 대조한다. "
          "$\\Omega$의 하계는 `window_mass_env/ia.py`의 정확 정의(격자 $i\\mathsf K^{-2/3}$·절점값·Fritsch–Carlson 기울기의 구간)에서 조각별 3차 계수의 바깥 괄호를 만들어 쓰며 조각별 비증가를 구간으로 확인한다(2026-11-14 H1; `test_lib.py`→`test_lib_out.txt`가 기록의 binary64 함수와 대조). "
          "기록의 binary64 PCHIP을 정확한 수로 읽던 앞선 판의 출력은 `v1_binary64omega/`에 두었다.")
BD_OLD = ("`band_iv.py`가 계산, `band_summary.py`가 요약, `run_all.sh`가 실행 순서이고, `compare_record.py`가 기록의 상자 값과 대조한다.")
BD_NEW = ("`band_iv.py`가 계산, `band_summary.py`가 요약, `run_all.sh`가 실행 순서이고, `compare_record.py`가 기록의 상자 값과 대조한다. "
          "$\\Omega$는 `bprime_boxes/ivbox_lib.py`를 통해 같은 정확 정의를 쓴다(2026-11-14 H1; 앞선 판의 출력은 `v1_binary64omega/`). 두 폴더의 재실행 순서는 `세션_재계산/rerun_omega_h1.sh`다.")
CW_ANCHOR = "F1의 셀별 입력 `F1_rows.json`은 기록에 실리지 않은 생산자 상자 캐시에서 `make_F1_rows.py`로 뽑은 것이고, 출력은 `verify_margins_out.txt`다."
CW_NEW = ("`세션_재계산/critical_window_rerun/`은 부록 D의 임계 창 인증 항목의 44개 상자를 이 글의 코드(기록의 생산자 코드에 정정 F1–F5·G1·G2를 넣은 것)로 다시 돌린 것이다(2026-11-13 세션; 2026-11-14 H1). "
          "`rig_*.py`·`ivio.py`가 계산 코드, `orig/`가 기록의 원본, `boxes.py`·`common.py`·`rerun_boxes.py`·`launch_rerun.py`·`recert_first.py`가 상자 모임·실행기·기동기·첫 셀 재인증이다. "
          "H1은 $\\hat x$ 셀을 십진 격자 $[1.4+0.2i,1.6+0.2i]$를 품는 바깥 구간으로 두고 Taylor 중심·반지름이 셀을 품게 하며 끝점·중심·반지름·여유를 정확한 이진값으로 저장한다. "
          "`verify_exact_cover.py`는 저장된 인증서만 읽어 $u$ 타일링과 $u_{\\mathrm{top}}^3\\cdot10001\\ge1$, 셀의 격자 포함, Taylor 영역의 셀 포함, 여유의 양수성을 허용 오차 없는 유리수로 검사한다(출력 `verify_exact_cover_out.txt`). "
          "인증서는 `cert/`, 상자 자료는 `cache/`, 실행 기록은 `logs/`, 요약은 `summarize.py`→`summary_out.txt`, `_test_exact_grid.py`는 H1의 두 셀 시험이다. "
          "binary64 격자로 돌린 앞선 실행의 인증서·로그·검증기는 `v1_floatgrid/`에 두었다(그 격자는 격자점 18곳에서 폭 $10^{-15}$ 이하의 틈을 남긴다).")
n += sub1("원고_자료/README.md", BP_OLD, BP_NEW)
n += sub1("원고_자료/README.md", BD_OLD, BD_NEW)
n += sub1("원고_자료/README.md", CW_ANCHOR, CW_ANCHOR + "\n\n" + CW_NEW)

# ---- PARAS ----
P = "scripts/_patch_README_세션파일.py"
n += sub1(P, '"`세션_재계산/bprime_boxes/`는 부록 D의 첫 조립의 상자 검사 항목(140,729개 유한 상자와 꼬리 상자)을 구간 산술로 다시 계산한 것이다(2026-11-13 세션). 스칼라는 mpmath `iv`(소수 34자리), 리만 합 벡터는 binary64의 정확 반올림 사칙연산·제곱근만 써서 1 ulp 바깥 밀기와 합의 $1-10^{-11}$ 인자로 아래로 민다. ' + BP_OLD + '"',
          '"`세션_재계산/bprime_boxes/`는 부록 D의 첫 조립의 상자 검사 항목(140,729개 유한 상자와 꼬리 상자)을 구간 산술로 다시 계산한 것이다(2026-11-13 세션). 스칼라는 mpmath `iv`(소수 34자리), 리만 합 벡터는 binary64의 정확 반올림 사칙연산·제곱근만 써서 1 ulp 바깥 밀기와 합의 $1-10^{-11}$ 인자로 아래로 민다. ' + BP_NEW.replace("\\", "\\\\") + '"')
n += sub1(P, BD_OLD + '"', (BD_NEW.replace("\\", "\\\\")) + '"')
n += sub1(P, '    ("window_mass_env/ia.py",',
          '    ("critical_window_rerun/rig_cert.py",\n     "' + CW_NEW.replace("\\", "\\\\") + '"),\n    ("window_mass_env/ia.py",')

# ---- 재실행표 CONFIG ----
G = "scripts/_gen_재실행표.py"
OLD_CW = ('    "critical-window-rig": dict(\n'
          '        scripts=[S + "critical_window/verify_margins.py", S + "critical_window/make_F1_rows.py"],\n'
          '        cmd=["python -I verify_margins.py <기록 ra4c01fc의 evidence 경로>",\n'
          '             "(검증기가 읽는 인증서 JSON과 검토 파일은 이 묶음에 없다)"],\n'
          '        outputs=[S + "critical_window/verify_margins_out.txt"]),\n')
NEW_CW = ('    "critical-window-rig": dict(\n'
          '        scripts=[S + "critical_window_rerun/rerun_boxes.py", S + "critical_window_rerun/rig_cert.py", S + "critical_window_rerun/recert_first.py",\n'
          '                 S + "critical_window_rerun/verify_exact_cover.py", S + "critical_window_rerun/summarize.py"],\n'
          '        cmd=["python -I launch_rerun.py 3 (작업자 셋; 하나면 python -I rerun_boxes.py 0 1)", "python -I recert_first.py A29 (G06, G07, G08, G13도)",\n'
          '             "python -I verify_exact_cover.py > verify_exact_cover_out.txt", "python -I summarize.py > summary_out.txt",\n'
          '             "(기록 인증서의 정정 후 여백 검증기는 critical_window/verify_margins.py)"],\n'
          '        expect="모든 셀 여유 양수; 최소 여유 [D15:최소여유]([D15:최소자리]); verify_exact_cover: ALL CHECKS PASSED",\n'
          '        outputs=[S + "critical_window_rerun/verify_exact_cover_out.txt", S + "critical_window_rerun/summary_out.txt"],\n'
          '        time="[D15:시간]"),\n')
n += sub1(G, OLD_CW, NEW_CW)
n += sub1(G, 'time="상자 약 803초(두 프로세스), 꼬리 3초(`log_box_…_p0.txt`의 done 줄)"),',
          'time="[D36:시간](`log_box_…_p0.txt`의 done 줄)"),')
n += sub1(G, 'expect="최솟값 (ㄱ) $1.00912689$, (ㄴ) $1.00669142$, (ㄷ) $1.01364957$, (ㄹ) $1.00910449$; 꼬리 (ㄱ) $1.122243024$",',
          'expect="최솟값 (ㄱ) [D37:ㄱ], (ㄴ) [D37:ㄴ], (ㄷ) [D37:ㄷ], (ㄹ) [D37:ㄹ]; 꼬리 (ㄱ) [D37:ㄱ꼬리]",')
n += sub1(G, 'time="상자 넷 각 174–294초(두 프로세스), 꼬리 각 2초(`band_result.txt`의 wall 줄)"),',
          'time="[D37:시간](`band_result.txt`의 wall 줄)"),')

# ---- 여유 JSON ----
J = "scripts/_재실행표_여유.json"
n += sub1(J, '"critical-window-rig": "(계산 뒤 채움)",', '"critical-window-rig": "최소 여유 [D15:최소여유]([D15:최소자리]; 기준은 양수)",')
n += sub1(J, '"bprime-boxes": "$1.052428971$ 대 문턱 $1.05$(상자 하계 최솟값; 문턱 대비 $0.231\\\\%$)",',
          '"bprime-boxes": "[D36:최솟값] 대 문턱 $1.05$(상자 하계 최솟값; 문턱 대비 [D36:여유])",')
n += sub1(J, '"band-boxes": "(ㄱ) $1.0091269$ 대 문턱 $1.009$(상자 하계 최솟값; 문턱 대비 $0.0126\\\\%$, 보증이 쓰는 $1$ 대비 $0.913\\\\%$)",',
          '"band-boxes": "(ㄱ) [D37:ㄱ] 대 문턱 $1.009$(상자 하계 최솟값; 문턱 대비 [D37:여유ㄱ], 보증이 쓰는 $1$ 대비 [D37:보증여유])",')

# ---- 자리표시자 검사기: README·재실행표도 ----
C = "scripts/_check_자리표시자.py"
n += sub1(C, '    files = sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [os.path.join(ROOT, "원고.md")]',
          '    files = sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [os.path.join(ROOT, "원고.md"),\n'
          '                                                                      os.path.join(ROOT, "원고_자료", "README.md"), os.path.join(ROOT, "원고_자료", "재실행표.md")]')

# ---- 절차 ----
Z = "zenodo_v4/절차.md"
n += sub1(Z, "D.36·D.37 항목(`장v2/부록D_장8.md`) 갱신, D.35의 Ω 정의 문장 보강.",
          "D.36·D.37 항목(`장v2/부록D_장8.md`)의 자리표시자 채움. 채울 자리와 출처는 `대조v2/수학검사2/자리표시자_채움표_1114.md`(D.15·D.36·D.37 쉰 곳쯤, 본문·README·재실행표·여유 JSON), 확인은 `python -I scripts/_check_자리표시자.py`(0이어야 함).")
print("치환", n)
