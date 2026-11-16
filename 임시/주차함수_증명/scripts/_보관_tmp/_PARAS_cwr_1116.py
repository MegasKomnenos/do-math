# -*- coding: utf-8 -*-
"""`_patch_README_세션파일.py` PARAS의 critical_window_rerun 문단을 README 563행의 새 문단과 같게 맞춘다(파이썬 문자열 안이라 백슬래시를 두 겹으로). 2026-11-16."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
PATCH = os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")
README = os.path.join(ROOT, "원고_자료", "README.md")
r = io.open(README, encoding="utf-8").read()
m = re.search(r"^`세션_재계산/critical_window_rerun/`은 .*$", r, re.M)
assert m, "README 문단 없음"
new_par = m.group(0)
assert "정정 F1" not in new_par and "v1_floatgrid" not in new_par
t = io.open(PATCH, encoding="utf-8").read()
start = "`세션_재계산/critical_window_rerun/`은 부록 D의 임계 창 인증 항목의 44개 상자를 이 글의 코드(기록의 생산자 코드에 정정 F1–F6·G1·G2를 넣은 것)로 다시 돌린 것이다"
i = t.find(start)
assert i >= 0, "PARAS 옛 문단 시작 없음"
end_tok = "이하의 틈을 남긴다)."
j = t.find(end_tok, i)
assert j > i, "PARAS 옛 문단 끝 없음"
j += len(end_tok)
old = t[i:j]
assert t.count(old) == 1
t = t[:i] + new_par.replace("\\", "\\\\") + t[j:]
io.open(PATCH, "w", encoding="utf-8", newline="\n").write(t)
print("PARAS ok: 옛 %d자 → 새 %d자" % (len(old), len(new_par)))
# 검증: PARAS를 평가해 README 문단과 같은지
import importlib.util, sys
spec = importlib.util.spec_from_file_location("pr", PATCH)
mod = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
try:
    spec.loader.exec_module(mod)
    paras = getattr(mod, "PARAS", None)
    if paras is not None:
        txt = paras if isinstance(paras, str) else "\n".join(paras if isinstance(paras, (list, tuple)) else paras.values())
        print("PARAS에 새 문단 포함:", new_par in txt)
except SystemExit:
    pass
