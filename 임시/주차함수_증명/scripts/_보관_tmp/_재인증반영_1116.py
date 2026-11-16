# -*- coding: utf-8 -*-
"""재인증(critical_window_rerun; 44상자 09:54 완료, postrun 10:18 종료) 뒤의 세션 몫. 2026-11-16.
 1) ZV1 `--apply`: 부록D_장5A D.critical-window-rig의 「결과」·재실행 문장·재인증 괄호, `_gen_재실행표.py` expect/time, `_재실행표_여유.json`.
 2) Q12-3·Q12-A: 「범위」 끝의 첫 셀 절 삭제(결과의 중복), 다섯 상자 문장에 까닭(기록이 첫 셀을 따로 다시 인증한 상자) 넣기.
 3) ZV8 2.2 (1): 옛 판 파일·폴더를 `대조v2/보관_재계산_옛판_1116/critical_window_rerun/`로 옮기고 README 2열 표의 행을 뺀다.
 4) ZV8 2.2 (2)(3): README 문단·PARAS·`_gen_재실행표.py` cmd에서 정정 번호·날짜·옛 폴더 서술을 뺀다.
 5) README 2열 표: 폴더의 현행 파일(루트 코드·출력, cert/*.json)을 등록·갱신한다."""
import glob, io, os, re, shutil, subprocess, sys
ROOT = r"C:\math\임시\주차함수_증명"
CWR = os.path.join(ROOT, "원고_자료", "세션_재계산", "critical_window_rerun")
KEEP = os.path.join(ROOT, "대조v2", "보관_재계산_옛판_1116", "critical_window_rerun")
PATCH = os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")
PY = sys.executable


def run(args, **kw):
    r = subprocess.run([PY, "-I"] + args, capture_output=True, text=True, encoding="utf-8", cwd=ROOT, **kw)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def sub1(path, old, new, label):
    s = io.open(path, encoding="utf-8").read()
    n = s.count(old)
    if n != 1:
        raise SystemExit("%s: %d건 — %s" % (label, n, old[:80]))
    io.open(path, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("ok", label)


# 1) ZV1 --apply
rc, out = run([os.path.join(ROOT, "scripts", "수학검사2", "검토_외부피드백_1116_ZV1_D문장.py"), "--apply"])
print("ZV1 --apply rc", rc)
print("\n".join(l for l in out.splitlines() if l.startswith("applied") or "assert" in l.lower() or "Error" in l))
if rc != 0:
    print(out[-1500:]); raise SystemExit("ZV1 apply 실패")

# 2) Q12-3
pD = os.path.join(ROOT, "장v2", "부록D_장5A.md")
sub1(pD, "로 덮고, 첫 셀 $[1.4,1.6]$을 포함한 모든 셀이 $\\mathrm{cw}=0.2$에서 인증된다.", "로 덮는다.", "D 138행 첫 셀 절")
s = io.open(pD, encoding="utf-8").read()
pat = re.compile(r"상자 A29, G06, G07, G08, G13의 첫 셀은 \$\\mathrm\{cw\}=0\.2\$에서 통과한 것\(여유 ([^)]*)\)에 더해, "
                 r"\$\\hat\{\\mathrm\{Wr\}\}_j\$·\$\\hat\{\\mathcal I\}_k\$를 \$\\mathrm\{ku\}\$ 반쪽 상자 둘의 합집합으로 좁힌 방식으로도 다시 인증했다"
                 r"\(셀 폭 \$0\.1\$, A29는 \$\[1\.4,1\.8\]\$; (최소 여유 각각 [^;]*; 다섯 번 합쳐 \$[0-9.]+\$시간)\)\.")
m = pat.search(s)
if not m:
    raise SystemExit("다섯 상자 문장을 찾지 못함")
new = ("기록이 첫 셀을 따로 다시 인증한 다섯 상자(A29, G06, G07, G08, G13)는 이 재실행에서 $\\mathrm{cw}=0.2$로 통과했고(여유 %s), "
       "기록과 같이 $\\hat{\\mathrm{Wr}}_j$·$\\hat{\\mathcal I}_k$를 $\\mathrm{ku}$ 반쪽 상자 둘의 합집합으로 좁히고 셀 폭을 $0.1$로 둔 방식(A29는 $[1.4,1.8]$)으로도 다시 인증했다(%s).") % (m.group(1), m.group(2))
s = s[:m.start()] + new + s[m.end():]
assert "진행 중" not in s.split("### D.{{D:critical-window-rig}}")[1].split("### D.")[0], "「진행 중」이 남아 있음"
io.open(pD, "w", encoding="utf-8", newline="\n").write(s)
print("ok D 144행 다섯 상자 문장")

# 3) 옛 판 파일 보관
os.makedirs(KEEP, exist_ok=True)
old_items = ["v2_E1deriv", "v1_floatgrid", "rig_ray4_v1_bug.py", "verify_fix_on_old_cache.py", "verify_fix_on_old_cache_out.txt",
             "verify_A00.py", "verify_A00_cells.py", "verify_A00.json", "verify_A00_out.txt", "verify_A00_cells_out.txt", "D항목_초안.md"]
readme = io.open(os.path.join(ROOT, "원고_자료", "README.md"), encoding="utf-8").read()
removes = []
for it in old_items:
    src = os.path.join(CWR, it)
    if not os.path.exists(src):
        print("없음", it); continue
    shutil.move(src, os.path.join(KEEP, it))
    rel = "critical_window_rerun/" + it
    if ("`세션_재계산/" + rel + "`") in readme:
        removes += ["--remove", rel]
    print("옮김", it)
if "`세션_재계산/critical_window_rerun/recert_h2_stdout.txt`" in readme:
    removes += ["--remove", "critical_window_rerun/recert_h2_stdout.txt"]
if removes:
    rc, out = run([PATCH] + removes)
    print("SHA 행 제거 rc", rc, out.strip().splitlines()[-2:])

# 4) README 문단·PARAS·재실행표 cmd
OLD_P_START = "`세션_재계산/critical_window_rerun/`은 부록 D의 임계 창 인증 항목의 44개 상자를 이 글의 코드(기록의 생산자 코드에 정정 F1–F6·G1·G2를 넣은 것)로 다시 돌린 것이다"
NEW_P = ("`세션_재계산/critical_window_rerun/`은 부록 D의 임계 창 인증 항목의 44개 상자를 이 글의 코드로 다시 돌린 것이다. "
         "`rig_*.py`·`ivio.py`가 계산 코드, `orig/`가 기록의 원본, `boxes.py`·`common.py`·`rerun_boxes.py`·`launch_rerun.py`·`recert_first.py`·`postrun.py`가 상자 모임·실행기·기동기·첫 셀 재인증·뒤처리 기동기다. "
         "이 글의 코드가 기록의 코드와 다른 넷(실수축 나머지의 지수 상수, $\\hat x$ 셀의 격자, 둘러싸기 식 세 곳, $(e^w-1)/w$의 1·2계 도함수 급수의 계수)은 부록 D 항목의 「독립 재계산」에 적혀 있다. "
         "$\\hat x$ 셀은 십진 격자 $[1.4+0.2i,1.6+0.2i]$를 품는 바깥 구간으로 두고 Taylor 중심·반지름이 셀을 품게 하며 끝점·중심·반지름·여유를 정확한 이진값으로 저장한다. "
         "`verify_exact_cover.py`는 저장된 인증서만 읽어 $\\mathrm{ku}$ 타일링과 $\\mathrm{ku}_{\\mathrm{top}}^3\\cdot10001\\ge1$, 셀의 격자 포함, Taylor 영역의 셀 포함, 여유의 양수성을 허용 오차 없는 유리수로 검사한다(출력 `verify_exact_cover_out.txt`). "
         "인증서는 `cert/`, 상자 자료는 `cache/`, 실행 기록은 `logs/`, 요약은 `summarize.py`→`summary_out.txt`, `_test_exact_grid.py`는 두 셀 시험, `check_fixes.py`→`check_fixes_out.txt`는 코드 자체 검사(둘러싸기의 포함, 급수 상수, 감마 상계, 상자 모임)다.")
for path, label in ((os.path.join(ROOT, "원고_자료", "README.md"), "README 문단"), (PATCH, "PARAS 문단")):
    t = io.open(path, encoding="utf-8").read()
    i = t.find(OLD_P_START)
    if i < 0:
        print("!!", label, "옛 문단 시작을 찾지 못함"); continue
    j = t.find("\n", i)
    old_par = t[i:j]
    if label == "PARAS 문단":
        # 파이썬 문자열 안이면 끝 따옴표 앞까지만
        k = old_par.rfind("`v1_floatgrid/`에 두었다(그 격자는 격자점 18곳에서 폭 $1.1\\times10^{-15}$ 이하의 틈을 남긴다).")
        if k < 0:
            print("!! PARAS 끝 문장을 찾지 못함; 수동 확인"); print(old_par[-200:]); continue
        old_par = old_par[:k + len("`v1_floatgrid/`에 두었다(그 격자는 격자점 18곳에서 폭 $1.1\\times10^{-15}$ 이하의 틈을 남긴다).")]
    assert t.count(old_par) == 1
    t = t.replace(old_par, NEW_P)
    io.open(path, "w", encoding="utf-8", newline="\n").write(t)
    print("ok", label, "(옛 %d자 → 새 %d자)" % (len(old_par), len(NEW_P)))
sub1(os.path.join(ROOT, "scripts", "_gen_재실행표.py"),
     'cmd=["python -I check_fixes.py > check_fixes_out.txt (F1–F6·G1·G2 자체 검사)"', 'cmd=["python -I check_fixes.py > check_fixes_out.txt (코드 자체 검사)"', "재실행표 cmd")

# 5) README 2열 표 등록·갱신
rels = []
for p in sorted(glob.glob(os.path.join(CWR, "*"))):
    if os.path.isfile(p) and os.path.splitext(p)[1] in (".py", ".txt", ".json", ".sh"):
        rels.append("critical_window_rerun/" + os.path.basename(p))
for p in sorted(glob.glob(os.path.join(CWR, "cert", "*.json"))):
    rels.append("critical_window_rerun/cert/" + os.path.basename(p))
print("등록 대상", len(rels))
rc, out = run([PATCH] + rels)
print("SHA 등록 rc", rc, out.strip().splitlines()[-3:])
print("남은 루트 파일:", sorted(os.listdir(CWR)))
