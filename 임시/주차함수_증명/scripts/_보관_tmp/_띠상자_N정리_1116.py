# -*- coding: utf-8 -*-
"""12차 B8 결정(정리 old-6-33 셋째 문장·D.band-boxes (ㄷ)(ㄹ) 삭제)의 자료 쪽 뒷정리. BD 둘째 단계가 D를 고친 뒤 돌린다. 2026-11-16.
 - band_boxes의 N·FN 산출물(box/log/tail)과 r030ffae의 (ㄷ)(ㄹ) 기록 파일 셋을 보관으로 옮긴다.
 - run_all.sh·band_summary.py에서 N 구성을 빼고 band_result.txt를 다시 만든다.
 - README 문단·PARAS·재실행표 생성기의 (ㄱ)–(ㄹ) 서술을 (ㄱ)(ㄴ)으로 좁힌다.
 - README 2열 SHA 표: 옮긴 파일 행 제거, 바뀐 세 파일 행 갱신."""
import glob, io, os, shutil, subprocess, sys
ROOT = r"C:\math\임시\주차함수_증명"
BB = os.path.join(ROOT, "원고_자료", "세션_재계산", "band_boxes")
KEEP = os.path.join(ROOT, "대조v2", "보관_재계산_옛판_1116", "band_boxes_N")
KEEP2 = os.path.join(ROOT, "대조v2", "보관_자료_1114", "r030ffae")
os.makedirs(KEEP, exist_ok=True); os.makedirs(KEEP2, exist_ok=True)

moved = []
for pat in ("box_N_*", "box_FN_*", "log_N_*", "log_FN_*", "tail_N_*"):
    for p in sorted(glob.glob(os.path.join(BB, pat))):
        shutil.move(p, os.path.join(KEEP, os.path.basename(p)))
        moved.append("band_boxes/" + os.path.basename(p))
print("band_boxes 옮김", len(moved))
for name in ("cert_assembly_low.py", "LOW_cert_assembly_T0.44_k6668.out", "LOW_cert_assembly_T0.53_k100000.out"):
    p = os.path.join(ROOT, "원고_자료", "r030ffae", name)
    if os.path.exists(p):
        shutil.move(p, os.path.join(KEEP2, name)); print("r030ffae 옮김", name)
    else:
        print("없음", name)


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
    ('for cfg in "box H 57 100 100000" "box N 11 25 6668" "box N 53 100 100000" "fbox H 12 25 6668" "fbox H 57 100 100000" "fbox N 11 25 6668" "fbox N 53 100 100000"; do',
     'for cfg in "box H 57 100 100000" "fbox H 12 25 6668" "fbox H 57 100 100000"; do'),
    ('for cfg in "H 12 25 6668" "H 57 100 100000" "N 11 25 6668" "N 53 100 100000"; do',
     'for cfg in "H 12 25 6668" "H 57 100 100000"; do'),
])
sub(os.path.join(BB, "band_summary.py"), [
    ("# band_summary.py -- merges the box parts and tails of band_iv.py for the four statements (a)-(d) of D.band-boxes.",
     "# band_summary.py -- merges the box parts and tails of band_iv.py for the two statements (a)-(b) of D.band-boxes."),
    ('CFG = [("(a)", True, 12, 25, 6668, "1.009"), ("(b)", True, 57, 100, 100000, "1"),\n       ("(c)", False, 11, 25, 6668, "1"), ("(d)", False, 53, 100, 100000, "1")]',
     'CFG = [("(a)", True, 12, 25, 6668, "1.009"), ("(b)", True, 57, 100, 100000, "1")]'),
])
out = subprocess.run([sys.executable, "-I", "band_summary.py"], cwd=BB, capture_output=True, text=True, encoding="utf-8")
if out.returncode != 0:
    print(out.stderr[-800:]); raise SystemExit("band_summary 실패")
io.open(os.path.join(BB, "band_result.txt"), "w", encoding="utf-8", newline="\n").write(out.stdout)
print("band_result.txt 재생성", len(out.stdout.splitlines()), "줄")

OLD = "`세션_재계산/band_boxes/`는 부록 D의 띠 정리의 상자 검사 항목 넷((ㄱ)–(ㄹ))을 같은 구간 산술로 다시 계산한 것이다."
NEW = "`세션_재계산/band_boxes/`는 부록 D의 띠 정리의 상자 검사 항목 둘((ㄱ)(ㄴ))을 같은 구간 산술로 다시 계산한 것이다."
sub(os.path.join(ROOT, "원고_자료", "README.md"), [(OLD, NEW)])
sub(os.path.join(ROOT, "scripts", "_patch_README_세션파일.py"), [(OLD, NEW)])
sub(os.path.join(ROOT, "scripts", "_gen_재실행표.py"), [
    ('expect="최솟값 (ㄱ) $1.0097628$, (ㄴ) $1.0068936$, (ㄷ) $1.0136495$, (ㄹ) $1.0091044$; 꼬리 (ㄱ) $1.12224$",',
     'expect="최솟값 (ㄱ) $1.0097628$, (ㄴ) $1.0068936$; 꼬리 (ㄱ) $1.12224$",'),
])

args = []
for rel in moved:
    args += ["--remove", rel]
r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")] + args, capture_output=True, text=True, encoding="utf-8")
print("SHA 행 제거", r.returncode, r.stdout.strip().splitlines()[-2:] if r.stdout else r.stderr[-300:])
r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_patch_README_세션파일.py"), "band_boxes/run_all.sh", "band_boxes/band_summary.py", "band_boxes/band_result.txt"], capture_output=True, text=True, encoding="utf-8")
print("SHA 행 갱신", r.returncode, r.stdout.strip().splitlines()[-2:] if r.stdout else r.stderr[-300:])
