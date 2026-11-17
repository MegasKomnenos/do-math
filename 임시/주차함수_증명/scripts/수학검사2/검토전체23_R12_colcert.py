# R12 검산: D.column-certificates-501-2000 「결과」 줄의 수와
# D.moment-certification의 위치 수를 이 글의 열별 결과 파일에서 다시 센다.
# 사용: python -I 검토전체23_R12_colcert.py <원고_자료/세션_재계산 폴더>
import collections
import glob
import json
import math
import os
import sys

base = sys.argv[1]
res = {}
for f in glob.glob(os.path.join(base, "column_cert_iv", "res_*.jsonl")):
    for line in open(f):
        line = line.strip()
        if line:
            r = json.loads(line)
            res[r["k"]] = r
ks = sorted(res)
print("columns", len(ks), ks[0], ks[-1], "all ok", all(res[k]["ok"] for k in ks))
print("min b0", min((res[k]["b0"], k) for k in ks), "min margin", min(res[k]["margin"] for k in ks))
print("max e", max(res[k]["e"] for k in ks), "max box", max(res[k]["r_box"] for k in ks),
      "max 2pi l/Nf", max(2 * res[k]["pi_l_over_Nf"] for k in ks))
print("winding", min(res[k]["wind_sum_lo"] for k in ks), max(res[k]["wind_sum_hi"] for k in ks),
      "max |t|", max(res[k]["t_max"] for k in ks))
print("lp width", set(round(res[k]["s_hi"] - res[k]["s_lo"], 13) for k in ks))
print("premises", 2 * max(res[k]["W_u_hi"] / res[k]["N"] for k in ks),
      2 * max(res[k]["QU_hi"] / res[k]["J"] for k in ks))
print("window tail", max(res[k]["tailg"] for k in ks), "U#", max(res[k]["Usharp_hi"] for k in ks),
      "eps", max(res[k]["eps_n0_hi"] for k in ks), "n0-sep", min(res[k]["n0"] - res[k]["j0"] for k in ks),
      "Gamma", max((res[k]["Gamma_hi"], k) for k in ks), "psi", min(res[k]["psi_NE_lo"] for k in ks))
NE = [res[k]["NE_new"] for k in ks]
print("nG strictly increasing", all(NE[i] < NE[i + 1] for i in range(len(NE) - 1)),
      "n0bis<npsi in", sum(res[k]["n0"] < res[k]["nV"] for k in ks),
      "nG<=ceil(0.836k^1.5)", all(res[k]["NE_new"] <= math.ceil(0.836 * k ** 1.5) for k in ks),
      res[840]["NE_new"], res[841]["NE_new"], res[2000]["NE_new"])
print("theta", collections.Counter(res[k]["theta"] for k in ks))
for k in (501, 841, 1000, 2000):
    r = res[k]
    print(k, r["theta"], r["s_lo"], r["s_hi"], r["b0"], r["PU_hi"], r["Gamma_hi"], r["n0"], r["nV"])
print("vs record", max(res[k]["e"] / res[k]["rec_e"] for k in ks),
      all(res[k]["b0"] >= res[k]["rec_m0"] for k in ks),
      max(abs(res[k]["PU_hi"] / res[k]["rec_P_U"] - 1) for k in ks),
      max(abs(res[k]["Gamma_hi"] / res[k]["rec_Gamma"] - 1) for k in ks))
nM = {int(k): v for k, v in json.load(open(os.path.join(base, "moment_cert_iv", "nM.json"))).items()}
d = [nM[k] - res[k]["NE_new"] for k in range(841, 2001)]
print("moment positions used", sum(res[k]["NE_new"] - 20001 for k in range(841, 2001)),
      "computed", sum(nM[k] - 10001 for k in range(841, 2001)), "nM-nG", min(d), max(d),
      "end rows", nM[841] - 1, nM[2000] - 1)
