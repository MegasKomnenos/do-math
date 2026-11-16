# -*- coding: utf-8 -*-
"""19차 M12 5절·XD 인계 3: 11-13 세션의 정정 항 검증기 `세션_재계산/critical_window/`(현행 D.critical-window-rig가 자료로 삼지 않는 옛 방식)를
보관으로 옮기고, README의 SHA 행 넷·설명 문단, `_patch_README_세션파일.py`의 PARAS 항목, `_gen_재실행표.py`의 cmd 한 줄을 걷어 낸다. 2026-11-16 20:5x."""
import io, os, re, shutil, subprocess, sys
ROOT = r"C:\math\임시\주차함수_증명"
SRC = os.path.join(ROOT, "원고_자료", "세션_재계산", "critical_window")
DST = os.path.join(ROOT, "대조v2", "보관_재계산_옛판_1116", "critical_window")
PAT = os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")
GEN = os.path.join(ROOT, "scripts", "_gen_재실행표.py")
RD = os.path.join(ROOT, "원고_자료", "README.md")
FILES = ["verify_margins.py", "verify_margins_out.txt", "make_F1_rows.py", "F1_rows.json"]

def rw(path, fn):
    b = io.open(path, "rb").read()
    assert b.count(b"\r") == 0, path
    s = fn(b.decode("utf-8"))
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)

# 1. 폴더 보관 이동
assert os.path.isdir(SRC) and not os.path.exists(DST)
assert sorted(os.listdir(SRC)) == sorted(FILES), os.listdir(SRC)
shutil.move(SRC, DST)
print("보관 이동 ok", DST)

# 2. PARAS 항목 제거
def fix_pat(s):
    m = re.search(r'    \("critical_window/verify_margins\.py",\n     "`세션_재계산/critical_window/verify_margins\.py`는 [^\n]*"\),\n', s)
    assert m, "PARAS 항목 못 찾음"
    return s[:m.start()] + s[m.end():]
rw(PAT, fix_pat); print("PARAS 제거 ok")

# 3. README SHA 행 넷 제거(공식 스크립트)
r = subprocess.run([sys.executable, "-I", PAT] + sum([["--remove", "critical_window/" + f] for f in FILES], []), capture_output=True, text=True, encoding="utf-8")
print(r.stdout.strip()); assert r.returncode == 0, r.stderr

# 4. README 설명 문단 제거
def fix_rd(s):
    pre = "`세션_재계산/critical_window/verify_margins.py`는 "
    i = s.find(pre); assert i >= 0 and s.count(pre) == 1
    j = s.find("\n", i)
    # 문단 뒤의 빈 줄 하나도 함께
    k = j + 1
    if s[k:k + 1] == "\n":
        k += 1
    return s[:i] + s[k:]
rw(RD, fix_rd); print("README 문단 제거 ok")

# 5. 재실행표 생성기 cmd 한 줄
def fix_gen(s):
    a = '''             "python -I verify_exact_cover.py > verify_exact_cover_out.txt", "python -I summarize.py > summary_out.txt",
             "(기록 인증서의 정정 후 여백 검증기는 critical_window/verify_margins.py)"],'''
    b = '''             "python -I verify_exact_cover.py > verify_exact_cover_out.txt", "python -I summarize.py > summary_out.txt"],'''
    assert s.count(a) == 1
    return s.replace(a, b)
rw(GEN, fix_gen); print("재실행표 생성기 ok")

# 6. 재생성·대조
r = subprocess.run([sys.executable, "-I", GEN], capture_output=True, text=True, encoding="utf-8"); print(r.stdout.strip().splitlines()[-1]); assert r.returncode == 0, r.stderr
r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_보관_tmp", "_readme_sha_mismatch_1116.py")], capture_output=True, text=True, encoding="utf-8"); print(r.stdout.strip()); assert r.returncode == 0, r.stderr

# 7. 남은 흔적
for p in (RD, os.path.join(ROOT, "원고_자료", "재실행표.md")):
    s = io.open(p, encoding="utf-8").read()
    print(os.path.basename(p), "critical_window/ 남은 수", len(re.findall(r"critical_window/(?!$)", s.replace("critical_window_rerun/", ""))), "CR", io.open(p, "rb").read().count(b"\r"))
