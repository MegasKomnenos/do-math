# -*- coding: utf-8 -*-
# R11 검산: D.exact-n20000 (ㅂ) 증인 위치 차, 그리고 행 자료의 개수 합
from mpmath import mp, mpf
import csv
mp.dps = 40
rows = list(csv.DictReader(open(r"C:/math/임시/주차함수_증명/원고_자료/r19de912/v2run20000-rows.tsv", encoding="utf-8"), delimiter="\t"))
print("rows", len(rows), "n range", rows[0]["n"], rows[-1]["n"])
pos = sum(int(r["positions"]) for r in rows); I = sum(int(r["I"]) for r in rows); Q = sum(int(r["Q"]) for r in rows)
print("positions", pos, "I", I, "Q", Q)
def rng(a, b):
    lo = hi = None
    for r in rows:
        n = int(r["n"])
        if a <= n <= b:
            l = int(r["mode_ell_mid"])
            v = n + 1 - l - mpf("0.59963") * mpf(n + 1) ** (mpf(2) / 3) - mpf("1.24847") * mpf(n + 1) ** (mpf(1) / 3)
            if lo is None or v < lo[0]: lo = (v, n)
            if hi is None or v > hi[0]: hi = (v, n)
    return lo, hi
for a, b in ((50, 900), (901, 20000)):
    lo, hi = rng(a, b)
    print(a, b, mp.nstr(lo[0], 12), lo[1], mp.nstr(hi[0], 12), hi[1])
# mode consistency: mode_ell_mid == firstQ_ell ? and lastI_ell+1 == firstQ_ell
bad = sum(1 for r in rows if int(r["mode_ell_mid"]) != int(r["firstQ_ell"]))
bad2 = sum(1 for r in rows if int(r["lastI_ell"]) >= int(r["firstQ_ell"]))
print("mode != firstQ:", bad, " lastI >= firstQ:", bad2)
