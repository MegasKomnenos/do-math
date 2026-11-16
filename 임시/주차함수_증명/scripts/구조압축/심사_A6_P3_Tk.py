# 심사 A6 — P3 검산: 열별 갱신 인증서(G′)의 문턱 T_k = max(n0bis, n^psi_k)와 모멘트 문턱 n_M(k)의 대조.
# 자료: 원고_자료/세션_재계산/column_cert_iv/res_*.jsonl (1500열), moment_cert_iv/nM.json (841–2000).
# 확인: (1) 501–840의 max T_k, 20001과의 비교; (2) 841–2000의 n_M(k) − T_k 범위; (3) 단조성;
#       (4) psi_G(NE)의 아래 끝 최솟값; (5) 501–840에서 n=20001의 psi_G 여유(F3의 4.5676e-7 주장).
import json, math, sys, io
from pathlib import Path
ROOT = Path(r"C:\math\임시\주차함수_증명")
CC = ROOT / "원고_자료" / "세션_재계산" / "column_cert_iv"
MC = ROOT / "원고_자료" / "세션_재계산" / "moment_cert_iv"
rows = {}
for f in ["res_ext_p0.jsonl", "res_ext_p1.jsonl", "res_p0.jsonl", "res_p1.jsonl"]:
    for line in io.open(CC / f, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        rows[d["k"]] = d
ks = sorted(rows)
out = []
out.append(f"columns read: {len(ks)}  range {ks[0]}..{ks[-1]}  missing: {[k for k in range(501,2001) if k not in rows]}")
out.append(f"all ok flags: {all(rows[k]['ok'] for k in ks)}")
# T_k := NE_new = max(n0, nV)
T = {k: rows[k]["NE_new"] for k in ks}
chk = all(T[k] == max(rows[k]["n0"], rows[k]["nV"]) for k in ks)
out.append(f"NE_new == max(n0bis, n^psi) in all columns: {chk}")
lo = [k for k in ks if k <= 840]
hi = [k for k in ks if k >= 841]
out.append(f"(1) 501-840: max T_k = {max(T[k] for k in lo)} at k={max(lo, key=lambda k: T[k])};  all T_k <= 20000: {all(T[k] <= 20000 for k in lo)}")
out.append(f"    T_840={T[840]}, T_841={T[841]}, T_2000={T[2000]}")
out.append(f"    T_k nondecreasing over 501-2000: {all(T[ks[i]] <= T[ks[i+1]] for i in range(len(ks)-1))}")
nM = {int(k): v for k, v in json.load(io.open(MC / "nM.json", encoding="utf-8")).items()}
diffs = {k: nM[k] - T[k] for k in hi if k in nM}
out.append(f"(2) 841-2000: n_M present for {len(diffs)} columns; n_M - T_k in [{min(diffs.values())}, {max(diffs.values())}]; all T_k <= n_M: {all(v >= 0 for v in diffs.values())}")
out.append(f"    n_M(841)={nM[841]}, n_M(2000)={nM[2000]}")
out.append(f"    841-2000: all T_k >= 20001 (so a finite moment window [20001, T_k-1] is nonempty): {all(T[k] >= 20001 for k in hi)}")
# (4) psi margins
pm = min(ks, key=lambda k: rows[k]["psi_NE_lo"])
out.append(f"(4) min psi_G(NE) lower end over 1500 columns = {rows[pm]['psi_NE_lo']:.6e} at k={pm}")
pm2 = min(lo, key=lambda k: rows[k]["psi_NE_lo"])
out.append(f"    min over 501-840 = {rows[pm2]['psi_NE_lo']:.6e} at k={pm2}")
# (5) psi_G(20001) over 501-840 with G = V_hi (upper end of Gamma*P^U)
def psi(k, G, n):
    m = (n - k) / (k + 1)
    return (1 + 1 / k) ** m + (1 - 1 / k) ** (m + G * n / k) - 2
vals = {k: psi(k, rows[k]["V_hi"], 20001) for k in lo}
km = min(vals, key=vals.get)
out.append(f"(5) 501-840, n=20001: min psi_G(20001) = {vals[km]:.10e} at k={km} (double precision; F3 claims 4.5676e-7); all positive: {all(v > 0 for v in vals.values())}")
# T_k / k^{3/2}
r = [T[k] / k ** 1.5 for k in ks]
out.append(f"    T_k/k^1.5 in [{min(r):.5f}, {max(r):.5f}]")
# positions count in moment window after re-cut: sum over 841-2000 of (T_k - 20001)
cnt_new = sum(max(0, T[k] - 20001) for k in hi)
cnt_old = sum(max(0, nM[k] - 10001) for k in hi)
out.append(f"(6) 841-2000 moment-cert positions: current [10001, n_M-1] = {cnt_old:,}; re-cut [20001, T_k-1] = {cnt_new:,} (F3 claims 40,638,833 -> 28,086,453)")
txt = "\n".join(out)
print(txt)
io.open(ROOT / "scripts" / "구조압축" / "심사_A6_P3_Tk_out.txt", "w", encoding="utf-8").write(txt + "\n")
