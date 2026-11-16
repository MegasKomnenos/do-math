# -*- coding: utf-8 -*-
"""16차 I9·I8·ID 결정(9.4절 0.57k 판 삭제 → 정리 old-6-33 둘째 문장 삭제 → D.band-boxes (ㄴ) 삭제)의 자료 쪽 뒷정리. 2026-11-16.
 - band_boxes의 T57 산출물(box/log/tail 열셋)과 r030ffae의 (ㄴ) 기록 출력 하나를 보관으로 옮긴다.
 - run_all.sh·band_summary.py에서 (ㄴ) 구성을 빼고 band_result.txt를 다시 만든다.
 - README 문단·PARAS·재실행표 생성기·여유 JSON의 「항목 둘((ㄱ)(ㄴ))」 서술을 항목 하나로 좁힌다.
 - README 2열 SHA 표: 옮긴 파일 행 제거, 바뀐 세 파일 행 갱신(4열 표의 r030ffae 행은 자료묶음_v2.py가 다시 만든다)."""
import glob, io, os, shutil, subprocess, sys
ROOT = r"C:\math\임시\주차함수_증명"
BB = os.path.join(ROOT, "원고_자료", "세션_재계산", "band_boxes")
KEEP = os.path.join(ROOT, "대조v2", "보관_재계산_옛판_1116", "band_boxes_T57")
KEEP2 = os.path.join(ROOT, "대조v2", "보관_자료_1114", "r030ffae")
os.makedirs(KEEP, exist_ok=True); os.makedirs(KEEP2, exist_ok=True)

moved = []
for pat in ("box_FH_T57-*", "box_H_T57-*", "log_FH_T57-*", "log_H_T57-*", "tail_H_T57-*"):
    for p in sorted(glob.glob(os.path.join(BB, pat))):
        shutil.move(p, os.path.join(KEEP, os.path.basename(p)))
        moved.append("band_boxes/" + os.path.basename(p))
print("band_boxes 옮김", len(moved))
assert len(moved) == 13, moved
p = os.path.join(ROOT, "원고_자료", "r030ffae", "LOWH_cert_assembly_T0.57_k100000.out")
if os.path.exists(p):
    shutil.move(p, os.path.join(KEEP2, os.path.basename(p))); print("r030ffae 옮김", os.path.basename(p))
else:
    print("없음(이미 옮겨짐?)", p)


def sub(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            raise SystemExit(f"{os.path.basename(path)}: {n}건 — {a[:70]}")
        s = s.replace(a, b)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", os.path.basename(path))


sub(os.path.join(BB, "run_all.sh"), [
    ('for cfg in "box H 57 100 100000" "fbox H 12 25 6668" "fbox H 57 100 100000"; do',
     'for cfg in "fbox H 12 25 6668"; do'),
    ('for cfg in "H 12 25 6668" "H 57 100 100000"; do',
     'for cfg in "H 12 25 6668"; do'),
])
sub(os.path.join(BB, "band_summary.py"), [
    ("# band_summary.py -- merges the box parts and tails of band_iv.py for the two statements (a)-(b) of D.band-boxes.",
     "# band_summary.py -- merges the box parts and the tail of band_iv.py for the statement of D.band-boxes."),
    ('CFG = [("(a)", True, 12, 25, 6668, "1.009"), ("(b)", True, 57, 100, 100000, "1")]',
     'CFG = [("D.band-boxes", True, 12, 25, 6668, "1.009")]'),
])
out = subprocess.run([sys.executable, "-I", "band_summary.py"], cwd=BB, capture_output=True, text=True, encoding="utf-8")
if out.returncode != 0:
    print(out.stderr[-800:]); raise SystemExit("band_summary 실패")
io.open(os.path.join(BB, "band_result.txt"), "w", encoding="utf-8", newline="\n").write(out.stdout)
print("band_result.txt 재생성", len(out.stdout.splitlines()), "줄")
print(out.stdout)

OLD = "`세션_재계산/band_boxes/`는 부록 D의 띠 정리의 상자 검사 항목 둘((ㄱ)(ㄴ))을 같은 구간 산술로 다시 계산한 것이다."
NEW = "`세션_재계산/band_boxes/`는 부록 D의 띠 정리의 상자 검사 항목을 같은 구간 산술로 다시 계산한 것이다."
sub(os.path.join(ROOT, "원고_자료", "README.md"), [(OLD, NEW)])
sub(os.path.join(ROOT, "scripts", "_patch_README_세션파일.py"), [(OLD, NEW)])
sub(os.path.join(ROOT, "scripts", "_gen_재실행표.py"), [
    ('expect="최솟값 (ㄱ) $1.0097628$, (ㄴ) $1.0068936$; 꼬리 (ㄱ) $1.12224$",',
     'expect="최솟값 $1.0097628$; 꼬리 $1.12224$",'),
    ('time="항목마다 프로세스 2개로 각 $330$초에서 $430$초, 꼬리 각 $3$초(`band_result.txt`의 wall 줄)"),',
     'time="프로세스 2개로 각 $340$초, 꼬리 $4$초(`band_result.txt`의 wall 줄)"),'),
])
sub(os.path.join(ROOT, "scripts", "_재실행표_여유.json"), [
    ('"band-boxes": "(ㄱ) $1.0097628$ 대 문턱',
     '"band-boxes": "$1.0097628$ 대 문턱'),
])

args = []
for rel in moved:
    args += ["--remove", rel]
r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")] + args, capture_output=True, text=True, encoding="utf-8")
print("SHA 행 제거", r.returncode, r.stdout.strip().splitlines()[-2:] if r.stdout else r.stderr[-300:])
r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_patch_README_세션파일.py"), "band_boxes/run_all.sh", "band_boxes/band_summary.py", "band_boxes/band_result.txt"], capture_output=True, text=True, encoding="utf-8")
print("SHA 행 갱신", r.returncode, r.stdout.strip().splitlines()[-2:] if r.stdout else r.stderr[-300:])
