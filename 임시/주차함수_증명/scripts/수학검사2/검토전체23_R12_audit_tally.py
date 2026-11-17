# R12 검산: D.band102-integer (가)의 감사 수, 음의 하계, omega 범위, (나)의 비교 수
# 사용: python -I 검토전체23_R12_audit_tally.py DIR
# DIR = 기록 r6b37c7e 폴더의 evidence/peer/audit_rerun
import os
import re
import sys

d = sys.argv[1]
table = {12000: 58, 13000: 79, 14000: 99, 15000: 102, 20000: 115, 30000: 132, 50000: 164,
         100000: 228, 200000: 298, 500000: 435, 1000000: 590}
pat = re.compile(r"nu=\+(\d+): lam=([\d.]+).*margin=(-?[\d.]+)")
tot = 0
neg = []
lams = set()
for K, vmax in table.items():
    rows = {}
    fs = ["rerun_audit_K%d.txt" % K]
    if K == 14000:
        fs.append("rerun_audit_K14000_nu97_100.txt")
    for f in fs:
        for line in open(os.path.join(d, f)):
            m = pat.match(line)
            if m:
                rows[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    tot += len(rows)
    neg += [(K, v, rows[v][1]) for v in rows if rows[v][1] <= 0]
    lams.update(rows[v][0] for v in rows if v <= vmax)
    print(K, min(rows), max(rows), rows[41][1], rows[vmax][1], rows[vmax + 1])
print(tot, neg, sorted(lams))
# (나) 실행 1, 2, 3, 4의 비교 수
print(sum(2 * k + 19 - 20000 for k in range(9991, 10000)),
      sum(2 * k + 40 - max(20001, 2 * k + 1) + 1 for k in range(9981, 11100)),
      sum(58 - max(41, 20001 - 2 * k) + 1 for k in range(9972, 12000)),
      sum(102 - max(59, 20001 - 2 * k) + 1 for k in range(9950, 12000)))
