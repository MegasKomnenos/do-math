# -*- coding: utf-8 -*-
"""13차 T13 5절 3·4·5의 자료 묶음 뒷정리. C 물결 앞 단계 회수 뒤, 파이프라인 전에 돌린다. 2026-11-16.
 - 부록 D 항목의 초안·세션 인계·빈 stdout·보관 폴더·_claims·_D_item_* 등 연구 흔적을 `대조v2/보관_재계산_옛판_1116/작업흔적/`로 옮긴다(상대 경로 보존).
 - README 2열 SHA 표에 등록된 흔적 셋(`r89eb039_polar_iv/out/_diff.txt`, `M_natural/j_integrals.py`·`j_integrals_out.txt` — 부록 D가 인용하지 않는 binary64 판)은 옮긴 뒤 `--remove`로 행을 뺀다.
 - `rc9aee43/`의 같은 내용 두 이름 다섯 쌍은 건드리지 않는다(README 파일 목록이 둘을 다른 항목에 붙여 적었으므로 사용자 판단으로 올림).
 - `critical_window_rerun/D항목_초안.md`는 `_gen_재실행표.py`·`_apply_D초안.py`가 가리키므로 두고 사용자 판단으로 올림(실행 인자 `--include-cwr`를 주면 함께 옮긴다).
 - make_draft*.py·handoff_A3.py·launch_handoff.py·run_slot*.sh·_test_exact_grid.py는 계산을 띄우고 항목 글을 만든 코드라 둔다(사용자 판단으로 올림)."""
import io, os, shutil, subprocess, sys, glob
ROOT = r"C:\math\임시\주차함수_증명"
BASE = os.path.join(ROOT, "원고_자료", "세션_재계산")
KEEP = os.path.join(ROOT, "대조v2", "보관_재계산_옛판_1116", "작업흔적")
include_cwr = "--include-cwr" in sys.argv

unreg = [
    "moment_cert_iv/D항목_원본.md", "moment_cert_iv/D항목_초안.md", "moment_cert_iv/D항목_초안_v2.md",
    "moment_cert_iv/handoff_A3.log",
    "moment_cert_iv/stdout_handoff.txt", "moment_cert_iv/stdout_shard0.txt", "moment_cert_iv/stdout_shard1.txt",
    "moment_cert_iv/stdout_shard2.txt", "moment_cert_iv/stdout_shard3.txt",
    "moment_cert_iv/보관_A1A2", "xcert_iv/_claims",
    "r89eb039_polar_iv/out/_D_item_current.md", "r89eb039_polar_iv/out/_D_item_new.md",
    "r89eb039_polar_iv/out/_cur_lf.md", "r89eb039_polar_iv/out/_new_lf.md", "r89eb039_polar_iv/out/_sec23.md",
]
reg = ["r89eb039_polar_iv/out/_diff.txt", "M_natural/j_integrals.py", "M_natural/j_integrals_out.txt"]
if include_cwr:
    unreg.append("critical_window_rerun/D항목_초안.md")

moved = []
for rel in unreg + reg:
    src = os.path.join(BASE, rel)
    if not os.path.exists(src):
        print("없음", rel); continue
    dst = os.path.join(KEEP, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    moved.append(rel)
print("옮김", len(moved))
for rel in moved:
    print("  ", rel)

args = []
for rel in reg:
    if rel in moved:
        args += ["--remove", rel]
if args:
    r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")] + args, capture_output=True, text=True, encoding="utf-8")
    print("SHA 행 제거", r.returncode, (r.stdout or r.stderr)[-600:])

# 묶음 안에 흔적이 남았는지 다시 센다
left = []
for pat in ("*/D항목_*.md", "*/handoff_*.log", "*/stdout_*.txt", "*/_claims", "*/out/_*.md", "*/보관_*"):
    left += glob.glob(os.path.join(BASE, pat))
print("남은 흔적 후보", [os.path.relpath(p, BASE) for p in left])
