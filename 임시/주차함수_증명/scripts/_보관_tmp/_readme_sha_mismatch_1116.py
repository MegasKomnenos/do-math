# -*- coding: utf-8 -*-
"""README 세션 재계산 SHA 표와 디스크를 대조해 어긋난 행과 표에 없는 새 파일(지정 폴더의 바로 아래 파일)을 찾고,
`--register`면 그것들을 `_patch_README_세션파일.py`로 등록한다. 2026-11-16.
처음 판은 진행 중이던 세 폴더(critical_window_rerun, moment_cert_iv, icert_py_full)의 어긋남을 건너뛰었다(SKIP).
세 계산이 끝난 뒤(11-16 20:5x) SKIP을 없애고 세 폴더를 지정 폴더에 더했다. 표는 처음부터 항목이 이름을 드는 코드·요약·인증서만
담고 열별 결과 덤프·캐시·바이너리·실행 로그 폴더는 담지 않았으므로(`--all`로 전체 재귀 목록만 볼 수 있다), 등록은 지정 폴더의 바로 아래 파일에 한한다."""
import hashlib, io, os, re, subprocess, sys
ROOT = r"C:\math\임시\주차함수_증명"
README = os.path.join(ROOT, "원고_자료", "README.md")
BASE = os.path.join(ROOT, "원고_자료", "세션_재계산")
NEW_DIRS = ["bprime_boxes", "band_boxes", "band_LP", "four_families", "critical_window_rerun", "moment_cert_iv", "icert_py_full"]
NEW_FILES = ["rerun_exactgrid_1116.sh", "rerun_exactgrid_1116_log.txt"]
EXCLUDE_REL = ("band_boxes/rerun_fbox_H_1115_log.txt",)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


rows = {}
for m in re.finditer(r"^\| `세션_재계산/([^`]+)` \| `([0-9a-f]{64})` \|", io.open(README, encoding="utf-8").read(), re.M):
    rows[m.group(1)] = m.group(2)
mism, missing = [], []
for rel, h in rows.items():
    p = os.path.join(BASE, rel.replace("/", os.sep))
    if not os.path.exists(p):
        missing.append(rel)
    elif sha(p) != h:
        mism.append(rel)
new = []
for d in NEW_DIRS:
    for f in sorted(os.listdir(os.path.join(BASE, d))):
        p = os.path.join(BASE, d, f)
        rel = d + "/" + f
        if os.path.isfile(p) and not f.endswith((".pyc", ".part")) and not f.startswith("_") and rel not in rows and rel not in EXCLUDE_REL:
            new.append(rel)
for f in NEW_FILES:
    if f not in rows and os.path.exists(os.path.join(BASE, f)):
        new.append(f)
print("어긋남", len(mism)); [print("  ~", r) for r in mism]
print("표에 없음(지정 폴더)", len(new)); [print("  +", r) for r in new]
print("파일 없음", len(missing)); [print("  -", r) for r in missing]
if "--all" in sys.argv:
    allnew = []
    for dp, dn, fn in os.walk(BASE):
        dn[:] = sorted(x for x in dn if x != "__pycache__")
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), BASE).replace(os.sep, "/")
            if not f.endswith((".pyc", ".part")) and rel not in rows:
                allnew.append(rel)
    from collections import Counter
    print("전체 재귀 — 표에 없음", len(allnew), dict(Counter(re.sub(r"/[^/]*$", "", r) if "/" in r else "(루트)" for r in allnew)))
if "--register" in sys.argv:
    todo = mism + new
    print("등록", len(todo))
    if todo:
        subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")] + todo, check=True)
