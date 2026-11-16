# -*- coding: utf-8 -*-
"""심사 A7 — P3 검산: G′ 열별 인증서(원고_자료/세션_재계산/column_cert_iv/res_*.jsonl)에서
T_k = max(n0bis, n^psi_k)를 다시 세고, 501–840의 max, T_841, T_2000, n_M(k)-T_k의 범위,
모멘트 인증 위치 수(현행 10001..n_M-1 / G′ 직결 20001..T_k-1)를 센다.
또 n=20001에서 psi_G(20001)의 최소 여유(501–840)를 mpmath로 다시 잰다.
실행: python -I scripts/구조압축/심사_A7_Gprime_Tk.py  (저장소 루트에서)
"""
import json, os, sys
from mpmath import mp, mpf

mp.dps = 40
ROOT = r"C:\math\임시\주차함수_증명"
CC = os.path.join(ROOT, "원고_자료", "세션_재계산", "column_cert_iv")
MC = os.path.join(ROOT, "원고_자료", "세션_재계산", "moment_cert_iv")

rows = {}
for fn in ["res_ext_p0.jsonl", "res_ext_p1.jsonl", "res_p0.jsonl", "res_p1.jsonl"]:
    with open(os.path.join(CC, fn), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[r["k"]] = r

ks = sorted(rows)
out = []
out.append(f"columns read: {len(ks)}, range {ks[0]}..{ks[-1]}, missing: {[k for k in range(501, 2001) if k not in rows]}")
out.append(f"all ok flags: {all(rows[k]['ok'] for k in ks)}; nV_exact all: {all(rows[k]['nV_exact'] for k in ks)}")

T = {k: max(rows[k]["n0"], rows[k]["nV"]) for k in ks}
out.append(f"T_k := max(n0bis, n^psi_k).  NE_new equals T_k in all columns: {all(rows[k]['NE_new'] == T[k] for k in ks)}")
out.append(f"T_k == NE_rec (record) in all columns: {all(rows[k]['NE_rec'] == T[k] for k in ks)}")
sub = [T[k] for k in ks if 501 <= k <= 840]
out.append(f"501-840: max T_k = {max(sub)} (k={max((k for k in ks if k<=840), key=lambda k: T[k])}); all <= 20000: {max(sub) <= 20000}")
out.append(f"T_841 = {T[841]}, T_2000 = {T[2000]}; n0bis(841)={rows[841]['n0']}, nV(841)={rows[841]['nV']}")
out.append(f"T_k nondecreasing in k: {all(T[ks[i]] <= T[ks[i+1]] for i in range(len(ks)-1))}")
out.append(f"T_k <= ceil(0.836 k^1.5) all: {all(T[k] <= -(-int(mpf('0.836')*mpf(k)**mpf('1.5')*10**6)//10**6) for k in ks)}")
out.append(f"first k with T_k > 20000: {min(k for k in ks if T[k] > 20000)}")

nM = {int(k): v for k, v in json.load(open(os.path.join(MC, "nM.json"), encoding="utf-8")).items()}
diffs = [nM[k] - T[k] for k in range(841, 2001)]
out.append(f"841-2000: n_M(k) - T_k in [{min(diffs)}, {max(diffs)}]; n_M(841)={nM[841]}, n_M(2000)={nM[2000]}; n_M > T_k in all: {min(diffs) > 0}")
# position counts
cur_second = sum(nM[k] - 1 - 10001 + 1 for k in range(841, 2001))
new_second_20001 = sum(max(0, T[k] - 1 - 20001 + 1) for k in range(841, 2001))
new_second_10001 = sum(max(0, T[k] - 1 - 10001 + 1) for k in range(841, 2001))
cur_first = sum((13 * k * k) // 100 - (2 * k + 1) + 1 for k in range(501, 841))
out.append(f"moment-cert positions, first range 501-840 (2k+1..floor(13k^2/100)): {cur_first}")
out.append(f"moment-cert positions, second range 841-2000 current (10001..n_M-1): {cur_second}")
out.append(f"  G' direct, rows 20001..T_k-1: {new_second_20001};  rows 10001..T_k-1: {new_second_10001}")
out.append(f"  saved vs current total {cur_first+cur_second}: with 20001 start {cur_first+cur_second-new_second_20001}; with 10001 start {cur_first+cur_second-new_second_10001}")

# psi_G(20001) with stored G = V_hi (upper end), columns 501..840
def psi(k, n, G):
    k = mpf(k); n = mpf(n); G = mpf(G)
    m = (n - k) / (k + 1)
    return (1 + 1 / k) ** m + (1 - 1 / k) ** (m + G * n / k) - 2

vals = [(psi(k, 20001, rows[k]["V_hi"]), k) for k in ks if k <= 840]
mn = min(vals)
out.append(f"min over 501-840 of psi_G(20001) with G = upper end of Gamma*P^U: {mp.nstr(mn[0], 8)} at k={mn[1]}; all positive: {all(v > 0 for v, _ in vals)}")
# min psi at NE (lower end) as stored
pm = min((rows[k]["psi_NE_lo"], k) for k in ks)
out.append(f"min stored lower end of psi_G(n^psi_k) over 1500 columns: {pm[0]:.4e} at k={pm[1]}")
# T_k for k=841: does psi_G(20001)<0 ? (to confirm 841 is not coverable at 20001)
out.append(f"k=841: psi_G(20001) = {mp.nstr(psi(841, 20001, rows[841]['V_hi']), 6)}, psi_G(20025) = {mp.nstr(psi(841, 20025, rows[841]['V_hi']), 6)}, psi_G(20024) = {mp.nstr(psi(841, 20024, rows[841]['V_hi']), 6)}")

txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "scripts", "구조압축", "심사_A7_Gprime_Tk_out.txt"), "w", encoding="utf-8") as f:
    f.write(txt + "\n")
