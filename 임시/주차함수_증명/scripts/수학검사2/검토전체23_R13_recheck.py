# -*- coding: utf-8 -*-
# 보고에 적은 「0건」·「처음 나오는 절」 주장을 고정 문자열로 다시 센다.
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
allf = files + appx
def cnt(tok, fs=allf):
    return {f: rd(f).count(tok) for f in fs if rd(f).count(tok)}
def bysec(tok, f):
    out = {}; sec = "(머리)"
    for ln, line in enumerate(rd(f).split("\n"), 1):
        m = re.match(r"^### (\S+)", line)
        if m: sec = m.group(1)
        if tok in line: out.setdefault(sec, []).append(ln)
    return out
print("1 \\mathsf z:", cnt("\\mathsf z"), "| \\mathsf{z}:", cnt("\\mathsf{z}"))
print("1 zeta-constants 라벨:", cnt("{{2:zeta-constants}}"))
print("2 장10의 120/121:", rd("장10").count("120"), rd("장10").count("121"))
print("3 결손 고정 생존비:", cnt("결손 고정 생존비"), "| 생존비:", cnt("생존비"), "| 생존 비:", cnt("생존 비"))
print("3 몫의 집계:", cnt("몫의 집계"), "| 몫 집계:", cnt("몫 집계"))
print("5 무게 장2:", {k: len(v) for k, v in bysec("무게", "장2").items()})
print("6 꼭대기 뿌리 장7B:", {k: v[:3] for k, v in bysec("꼭대기 뿌리", "장7B").items()}, "장7A:", bysec("꼭대기 뿌리", "장7A"))
print("7 상한 장1:", bysec("상한", "장1"), "하한 장1:", bysec("하한", "장1"))
print("8 Borel 꼬리 장2:", bysec("Borel 꼬리", "장2"), "| 사슬 생존 곱 장2:", bysec("사슬 생존 곱", "장2"))
print("8 Borel 꼬리 첫 장들:", {f: bysec("Borel 꼬리", f) for f in ["장4", "장6"]})
J = open(os.path.join(base, "장부_v2.md"), encoding="utf-8").read().split("\n")
print("4 0.1절:", [i + 1 for i, l in enumerate(J) if re.search(r"(?<![\d.])0\.1절", l)])
print("9 (10: 행:", sum(1 for l in J if re.search(r"\| \(10:[A-Za-z0-9\-]+\) \|$", l)), "(9: 행:", sum(1 for l in J if re.search(r"\| \(9:[A-Za-z0-9\-]+\) \|$", l)))
print("k≤120:", [i + 1 for i, l in enumerate(J) if "k\\le120" in l][:5])
M = open(os.path.join(base, "대조v2", "라벨_번호_대응표_1114.md"), encoding="utf-8").read().split("\n")
for n in (64, 228, 393, 475): print("대응표", n, M[n - 1][:260])
D = open(os.path.join(base, "의존지도_v2.md"), encoding="utf-8").read().split("\n")
for n in (297, 303, 304, 307, 412, 425, 460): print("지도", n, D[n - 1][:230])
for n in (1038, 1139): print("장부", n, J[n - 1][:300])
