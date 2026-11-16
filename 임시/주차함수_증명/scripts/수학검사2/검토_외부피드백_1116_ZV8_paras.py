# -*- coding: utf-8 -*-
"""ZV8 둘째 단계: scripts/_patch_README_세션파일.py PARAS의 band_check 문단을 README.md 591행 문단(현행)과 같게 맞춘다.
README에서 `세션_재계산/band_check/`로 시작하는 문단을 읽어 파이썬 문자열 리터럴로 바꿔 넣는다. 멱등.
python -I scripts/수학검사2/검토_외부피드백_1116_ZV8_paras.py"""
import io, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
readme = io.open(ROOT + r"\원고_자료\README.md", encoding="utf-8").read()
paras = [p for p in readme.split("\n") if p.startswith("`세션_재계산/band_check/`는 ")]
assert len(paras) == 1, len(paras)
para = paras[0]
lit = '"' + para.replace("\\", "\\\\").replace('"', '\\"') + '"'
P = ROOT + r"\scripts\_patch_README_세션파일.py"
s = io.open(P, encoding="utf-8").read()
pat = re.compile(r'(\("band_check/band_iv\.py",\n\s*)"(?:[^"\\]|\\.)*"(\),)')
m = list(pat.finditer(s))
assert len(m) == 1, len(m)
new = pat.sub(lambda mm: mm.group(1) + lit + mm.group(2), s)
io.open(P, "w", encoding="utf-8", newline="").write(new)
# 확인: 리터럴을 평가하면 README 문단과 같다
ns = {}
exec("x = " + lit, ns)
print("PARAS band_check 문단 == README 문단:", ns["x"] == para)
