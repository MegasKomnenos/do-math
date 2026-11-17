# -*- coding: utf-8 -*-
"""U14 인계(세션 1항): 결정_K4_E2_readout.py 를 band_boxes/readout_front.py 로 복사하되 절대 경로 상수를 이 폴더 상대 경로로 바꾼다. 2026-11-17."""
import io, re, os, subprocess, sys
ROOT = r"C:\math\임시\주차함수_증명"
SRC = os.path.join(ROOT, "scripts", "구조압축", "결정_K4_E2_readout.py")
DST_DIR = os.path.join(ROOT, "원고_자료", "세션_재계산", "band_boxes")
DST = os.path.join(DST_DIR, "readout_front.py")
src = io.open(SRC, encoding="utf-8").read()
pat = re.compile(r'^D = r"[^"\n]*band_boxes"\s*$', re.M)
m = pat.search(src)
assert m, "경로 상수 못 찾음"
new = 'D = os.path.dirname(os.path.abspath(__file__))  # 이 폴더(band_boxes)의 저장 상자값을 읽는다. 사본 출처: scripts/구조압축/결정_K4_E2_readout.py (U14 인계 세션 1항)'
dst = src[:m.start()] + new + src[m.end():]
io.open(DST, "w", encoding="utf-8", newline="\n").write(dst)
print("copied ->", DST)
out = subprocess.run([sys.executable, "-I", "readout_front.py"], cwd=DST_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
io.open(os.path.join(DST_DIR, "readout_front_out.txt"), "w", encoding="utf-8", newline="\n").write(out.stdout + (("\n[stderr]\n" + out.stderr) if out.stderr.strip() else ""))
print("exit", out.returncode)
print(out.stdout[:1500])
if out.stderr.strip():
    print("[stderr]", out.stderr[:800])
