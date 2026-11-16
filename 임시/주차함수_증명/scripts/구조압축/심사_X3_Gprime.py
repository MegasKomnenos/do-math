# -*- coding: utf-8 -*-
"""심사 X3 — G′ 열별 인증서(501–2000)의 실제 문턱 T_k = max(n^bis_0, n^psi_k)를 자료에서 센다.
자료: 원고_자료/세션_재계산/column_cert_iv/res_*.jsonl (이 글의 구간 재계산; 필드 n0 = n^bis_0, nV = n^psi_k, NE_new = max),
      원고_자료/세션_재계산/moment_cert_iv/nM.json (정리 7:theorem-C-moment의 n_M(k), 841–2000).
피드백 F2 §1.2 / F3 §4 / F4 §7의 수치(max T_k(501–840)=19990, T_841=20025, T_2000=71871, n_M−T_k∈[482,1161],
501–840 위치 19,840,702, 841–2000 원래 40,638,833 → 28,086,453)를 다시 센다.
"""
import json, os, sys
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
            d = json.loads(line)
            rows[d["k"]] = d
ks = sorted(rows)
out = []
out.append(f"열 수: {len(ks)}, 범위 {ks[0]}–{ks[-1]}, 빠진 열: {[k for k in range(501, 2001) if k not in rows]}")
out.append(f"모든 열 ok: {all(rows[k]['ok'] for k in ks)}; nV_exact 모두: {all(rows[k].get('nV_exact') for k in ks)}")
T = {k: max(rows[k]["n0"], rows[k]["nV"]) for k in ks}
bad = [k for k in ks if T[k] != rows[k]["NE_new"]]
out.append(f"T_k=max(n0,nV)와 NE_new 불일치 열: {bad}")
badrec = [k for k in ks if rows[k]["NE_new"] != rows[k]["NE_rec"]]
out.append(f"NE_new와 기록 NE_rec 불일치 열: {badrec}")
# 501–840
A = [k for k in ks if k <= 840]
out.append(f"501–840: max T_k = {max(T[k] for k in A)} (k={max(A, key=lambda k: T[k])}), T_k<=20000인 열 수 = {sum(T[k] <= 20000 for k in A)}/{len(A)}")
out.append(f"T_840 = {T[840]}, T_841 = {T[841]}, T_2000 = {T[2000]}")
out.append(f"T_k 비감소: {all(T[ks[i]] <= T[ks[i+1]] for i in range(len(ks)-1))}")
# 841–2000 vs n_M
with open(os.path.join(MC, "nM.json"), encoding="utf-8") as f:
    nM = {int(k): v for k, v in json.load(f).items()}
B = [k for k in ks if k >= 841]
diff = {k: nM[k] - T[k] for k in B}
out.append(f"841–2000: n_M(k)−T_k 범위 [{min(diff.values())}, {max(diff.values())}] (최소 k={min(diff, key=diff.get)}, 최대 k={max(diff, key=diff.get)}); 모두 양: {all(v > 0 for v in diff.values())}")
out.append(f"n_M(841)={nM[841]}, n_M(2000)={nM[2000]}")
out.append(f"T_k >= 20001 (841–2000 모든 열): {all(T[k] >= 20001 for k in B)}; min T_k = {min(T[k] for k in B)}")
# 위치 수
posA_cur = sum(max(0, (13*k*k)//100 - (2*k+1) + 1) for k in A)
out.append(f"501–840 현행 모멘트 인증 위치 수 Σ(⌊13k²/100⌋−2k): {posA_cur} (F3/F4 주장 19,840,702)")
posB_cur = sum(nM[k] - 1 - 10001 + 1 for k in B)
out.append(f"841–2000 현행 모멘트 인증 위치 수 Σ(n_M−10001): {posB_cur} (F3 주장 40,638,833)")
posB_new = sum(max(0, T[k] - 1 - 20001 + 1) for k in B)
out.append(f"841–2000 G′ 직접 접합 뒤 [20001, T_k−1] 위치 수: {posB_new} (F3 주장 28,086,453)")
posB_new10001 = sum(max(0, T[k] - 10001) for k in B)
out.append(f"  (참고: 시작 행을 10001로 두면 {posB_new10001})")
out.append(f"차이(현행 합 − 새 합): {posA_cur + posB_cur - posB_new} (F3 주장 32,393,082)")
# psi margins
out.append(f"psi_G(n^psi) 하계 최솟값(1500열): {min(rows[k]['psi_NE_lo'] for k in ks):.4e} (F2 주장 2.07e-10); 501–840만: {min(rows[k]['psi_NE_lo'] for k in A):.4e}")
# G′ at n=20001 for 501–840: not stored; report T_k distribution
out.append("501–840 표본 (k, n0, nV, T_k): " + ", ".join(f"({k},{rows[k]['n0']},{rows[k]['nV']},{T[k]})" for k in [501, 600, 700, 800, 830, 839, 840]))
out.append("841–2000 표본 (k, T_k, n_M, n_M−T_k): " + ", ".join(f"({k},{T[k]},{nM[k]},{diff[k]})" for k in [841, 900, 1000, 1200, 1500, 1800, 2000]))
txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "scripts", "구조압축", "심사_X3_Gprime_out.txt"), "w", encoding="utf-8") as f:
    f.write(txt + "\n")
