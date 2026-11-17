# -*- coding: utf-8 -*-
# 보고 3절에 적은 수와 자리를 다시 센다.
import re, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
def secof(f, ln):
    sec = "(머리)"
    for i, line in enumerate(rd(f).split("\n"), 1):
        m = re.match(r"^### (\S+)", line)
        if m: sec = m.group(1)
        if i == ln: return sec
print("장6 433·438행의 절:", secof("장6", 433), secof("장6", 438))
t = rd("부록D_장7B").split("\n")
cur = None
for i, l in enumerate(t, 1):
    m = re.match(r"^### D\.\{\{D:([A-Za-z0-9\-]+)\}\}", l)
    if m: cur = m.group(1)
    if i == 5: print("부록D_장7B 5행의 항목:", cur)
print("zeta(:", {f: rd(f).count("\\zeta(") for f in files + appx if rd(f).count("\\zeta(")}, "| zeta 전체:", {f: len(re.findall(r"\\zeta(?![A-Za-z])", rd(f))) for f in files + appx if re.findall(r"\\zeta(?![A-Za-z])", rd(f))})
for f in ["장1", "장3"]:
    s = rd(f); n = 0
    for m in re.finditer(r"\$\$(.+?)\$\$|\$([^$\n]+?)\$", s, re.S):
        body = m.group(1) or m.group(2)
        body = re.sub(r"\\[A-Za-z]+", " ", body)
        n += len(re.findall(r"(?<![A-Za-z])o(?![A-Za-z])", body))
    print(f, "맨 o:", n)
out = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "검토전체23_R13_depmap.py")], capture_output=True, text=True, encoding="utf-8").stdout
rows = [l for l in out.split("\n") if l.startswith("본문 인용 다름") and "표에만: []" not in l]
print("본문 인용 칸에 머리 다음 문단 밖의 라벨이 든 행:", len(rows))
for w in ["exponential formula", "hitting time", "size-biased", "ladder epoch", "Fekete"]:
    print(w, {f: rd(f).count(w) for f in files if rd(f).count(w)})
print("5장 본문의 대문자 N:", [(f, len(re.findall(r"(?<![A-Za-z\\{])N(?![A-Za-z}])", rd(f)))) for f in ["장5A", "장5B"]])
