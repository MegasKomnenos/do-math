# 심사 A6 — P1 검산: 극 영역 전용 경로(7:polar-W) 없이 왼쪽 잔여 위치 {k>=501, n>=2k+1}를 덮는 접합 확인.
# 규칙(현행 진술의 범위를 그대로 씀; 가정은 LRP_2뿐):
#   R0  n<=20000: 5:old-5-1 + 4:old-4-5
#   R1  501<=k<=840,  n>=T_k (G′ 7.33(나); T_k = 인증서의 max(n0bis,n^psi))
#   R2  841<=k<=2000, 20001<=n<=T_k-1 : D:moment-certification([10001,n_M-1] ⊇ 이 창; n_M>=T_k 확인은 P3 스크립트)
#   R3  841<=k<=2000, n>=T_k : G′ 7.33(나)
#   R4  2001<=k<=3130, n>=20001 : 7:qstar-columns + 7:old-6-15 (귀납: 2k<m<n 모두 R0 또는 (⋆)(m)>=0)
#   R5  k>=3131, 20001<=n<=2k+102 : 7:old-6-13 (띠 102)
#   R6  k>=3131, max(2k+103,20001)<=n<=3k-1 : LRP_2 (가정)
#   R7  k>=3131, n=3k>=20001 : 7:old-6-21 ((⋆)(3k)>0) + old-6-15
#   R8  k>=3131, n>=3k+1 : 7:old-6-20 + old-6-15
# 어디에도 n^circ_k, n^flat_k, n^sharp_k, polar-W, cor-S-prime, theorem-C-moment가 들어가지 않음을 규칙 목록 자체가 보인다.
import json, io
from pathlib import Path
ROOT = Path(r"C:\math\임시\주차함수_증명")
CC = ROOT / "원고_자료" / "세션_재계산" / "column_cert_iv"
T = {}
for f in ["res_ext_p0.jsonl", "res_ext_p1.jsonl", "res_p0.jsonl", "res_p1.jsonl"]:
    for line in io.open(CC / f, encoding="utf-8"):
        if line.strip():
            d = json.loads(line); T[d["k"]] = d["NE_new"]
def rules(n, k):
    r = []
    if n <= 20000: r.append("R0")
    if 501 <= k <= 840 and n >= T[k]: r.append("R1")
    if 841 <= k <= 2000 and 20001 <= n <= T[k] - 1: r.append("R2")
    if 841 <= k <= 2000 and n >= T[k]: r.append("R3")
    if 2001 <= k <= 3130 and n >= 20001: r.append("R4")
    if k >= 3131 and 20001 <= n <= 2 * k + 102: r.append("R5")
    if k >= 3131 and max(2 * k + 103, 20001) <= n <= 3 * k - 1: r.append("R6(LRP2)")
    if k >= 3131 and n == 3 * k and n >= 20001: r.append("R7")
    if k >= 3131 and n >= 3 * k + 1: r.append("R8")
    return r
gaps = []
checked = 0
# exhaustive over k in [501, 12000], n in [2k+1, 3k+2] plus n up to 80000 for k<=2000 (T_k <= 71871)
for k in range(501, 12001):
    nmax = max(3 * k + 2, 80000 if k <= 2000 else 0)
    for n in range(2 * k + 1, nmax + 1):
        checked += 1
        if not rules(n, k):
            gaps.append((n, k))
            if len(gaps) > 20: break
    if len(gaps) > 20: break
out = [f"positions checked: {checked:,}", f"gaps (first 20): {gaps[:20]}", f"gap count (capped at 21): {len(gaps)}"]
# beyond nmax: for k<=2000, n>=T_k covered by R1/R3 (T_k<=71871<80000); for 2001<=k<=3130, R4 covers all n>=20001; for k>=3131, R8 covers all n>=3k+1. Symbolic.
out.append("symbolic tail: k<=2000: n>80000>=T_k -> R1/R3; 2001-3130: R4 unbounded; k>=3131: R8 unbounded.")
# boundary checks named by F4
for (n, k) in [(20001, 6667), (20000, 6667), (20001, 6666), (19998, 6666), (20001, 9950), (20001, 2001), (20001, 3131), (20025, 841), (20024, 841), (19990, 840)]:
    out.append(f"  ({n},{k}): {rules(n,k)}")
# band R5 relevance: 2k+102>=20001 iff k>=9950
out.append(f"band rule R5 non-empty only for k>=9950: {all(not rules(20001,k).count('R5') for k in range(3131,9950)) and 'R5' in rules(20001,9950)}")
txt = "\n".join(out)
print(txt)
io.open(ROOT / "scripts" / "구조압축" / "심사_A6_P1_coverage_out.txt", "w", encoding="utf-8").write(txt + "\n")
