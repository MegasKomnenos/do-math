# -*- coding: utf-8 -*-
"""24차 세션 몫 계산·README 수정(2026-11-18 01:xx) — ZD2 인계 「세션」 3·4·5, Z6 인계 「세션」(README 473행·여유 json 13행), Z1 (ㄹ) 귀결.
(A) column_cert_iv: summary.py 47·66행 문자열·colcert_iv.py 6·426행 주석의 프라임 표지 (a′)(b′)(c′)→(a)(b)(c)(「Theorem G'」·「Lemma P'(c)」는 기록 이름이라 그대로).
(B) moment_cert_iv: sweep_p0/p1.jsonl·.log를 A5만 남기게 거름; summarize.py RANGES=("A5",); compare.py 두 열 거름 한 줄.
(C) README 473·477·479행과 _patch_README_세션파일.py PARAS: (a′)→(a) 문장, 「최소 상대 여유」→「최소 인증 여유」, 「연속한 열 열 개가」→「연속한 열 10개가」.
(D) _재실행표_여유.json: 다섯 키 「상대 여유」→「인증 여유」; 13행 (a′)→(a)·옛 글자 Lip·ψ_V(n^V_k)→𝔩_𝔷·ψ_G(n^ψ_k).
재실행(summary.py 셋·summarize.py·summarize_nb.py)·compare_out 거름·README SHA·재실행표는 이 스크립트 뒤 셸에서."""
import io, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(ROOT, "원고_자료", "세션_재계산")
BS = chr(92)
def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, s): io.open(p, "w", encoding="utf-8", newline="\n").write(s)
def sub(s, a, b, n=1):
    c = s.count(a); assert c == n, (a[:70], c, n); return s.replace(a, b)

# (A) column_cert_iv
p = os.path.join(S, "column_cert_iv", "summary.py"); s = rd(p)
s = sub(s, "P('--- condition (a" + BS + "'): circle |xi| = e^{theta/k}, Lemma P" + BS + "'(c)')",
           "P('--- condition (a): circle |xi| = e^{theta/k}, Lemma P" + BS + "'(c)')")
s = sub(s, "P('--- conditions (b" + BS + "') (c" + BS + "') and Gamma')", "P('--- conditions (b) (c) and Gamma')")
wr(p, s)
p = os.path.join(S, "column_cert_iv", "colcert_iv.py"); s = rd(p)
s = sub(s, "and checks the conditions (a') (b') (c') of Theorem G' with rigorous enclosures:",
           "and checks the conditions (a) (b) (c) of Theorem G' with rigorous enclosures:")
s = sub(s, "# Theorem G' (c'), with the specific reals", "# Theorem G' (c), with the specific reals")
wr(p, s)

# (B) moment_cert_iv — jsonl·log 거름
M = os.path.join(S, "moment_cert_iv")
for fn, want in (("sweep_p0.jsonl", 569), ("sweep_p1.jsonl", 591)):
    lines = rd(os.path.join(M, fn)).split("\n")
    keep = [l for l in lines if l.strip() and json.loads(l)["range"] == "A5"]
    assert len(keep) == want, (fn, len(keep))
    wr(os.path.join(M, fn), "\n".join(keep) + "\n")
for fn in ("sweep_p0.log", "sweep_p1.log"):
    lines = rd(os.path.join(M, fn)).split("\n")
    keep = [l for l in lines if l.strip() and (l.split()[1:2] == ["A5"] or l.startswith("SWEEP DONE"))]
    print(fn, "kept", len(keep), "of", len([l for l in lines if l.strip()]))
    wr(os.path.join(M, fn), "\n".join(keep) + "\n")
# summarize.py
p = os.path.join(M, "summarize.py"); s = rd(p)
s = sub(s, "# every column of (A1),(A2),(A3),(A5) present exactly once with the prescribed row range.",
           "# every column of (A5) present exactly once with the prescribed row range\n# (2026-11-18: the item covers A5 only; the A1-A3 lines of the record's run names were filtered out of sweep_p*.jsonl).")
s = sub(s, "jobs = M.ranges()", 'RANGES = ("A5",)\njobs = [j for j in M.ranges() if j[0] in RANGES]')
s = sub(s, 'for rg in ("A1", "A2", "A3", "A5"):', "for rg in RANGES:")
wr(p, s)
# compare.py — 두 열 거름(다시 돌릴 때)
p = os.path.join(M, "compare.py"); s = rd(p)
anchor = "npres = {}\n"
assert s.count(anchor) == 1
s = s.replace(anchor, 'rows = [r for r in rows if r["k"] in (2000, 1000)]  # 2026-11-18: only the two record columns inside the item\'s range (A5)\n' + anchor)
wr(p, s)

# (C) README·PARAS
for P in (os.path.join(ROOT, "원고_자료", "README.md"), os.path.join(ROOT, "scripts", "_patch_README_세션파일.py")):
    s = rd(P)
    s = sub(s, "마다 정리 G′의 조건 (a′)(b′)(c′)를 확인한다", "마다 열별 갱신 인증서(기록의 정리 G′)의 조건 (a)(b)(c)를 확인한다")
    s = sub(s, "최소 상대 여유", "최소 인증 여유", 3)
    s = sub(s, "연속한 열 열 개가", "연속한 열 10개가")
    wr(P, s)

# (D) 여유 json
p = os.path.join(ROOT, "scripts", "_재실행표_여유.json"); s = rd(p)
s = sub(s, '"exact-n20000": "최소 상대 여유', '"exact-n20000": "최소 인증 여유')
s = sub(s, '"column-certification-k500": "직접 비교의 최소 상대 여유', '"column-certification-k500": "직접 비교의 최소 인증 여유')
s = sub(s, "(나) 실행 일곱의 최소 상대 여유", "(나) 실행 일곱의 최소 인증 여유")
s = sub(s, '"moment-certification": "상대 여유 하계의 최솟값', '"moment-certification": "인증 여유 하계의 최솟값')
s = sub(s, '"window-mass-env": "(나) 최소 상대 여유', '"window-mass-env": "(나) 최소 인증 여유')
s = sub(s, '"column-certificates-501-2000": "(a′) 여유', '"column-certificates-501-2000": "(a) 여유')
s = sub(s, BS + BS + "mathrm{Lip}", BS + BS + "mathfrak l_{" + BS + BS + "mathfrak z}")
s = sub(s, BS + BS + "psi_V(n^{" + BS + BS + "mathrm V}_k)", BS + BS + "psi_G(n^{" + BS + BS + "psi}_k)")
assert "상대 여유" not in s, [l for l in s.split("\n") if "상대 여유" in l]
wr(p, s)
json.loads(rd(p))
print("edits ok")
