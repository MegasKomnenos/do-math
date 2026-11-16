# K12: D.induction-rows and D.exact-n20000 (ㅂ) from the row file; hashes of the two bundle copies
import hashlib, sys, io
import mpmath as mp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = r"C:/math/임시/주차함수_증명/원고_자료/r19de912/"
for f in ("v2run20000-rows.tsv", "evidence__peer__cert__v2run20000-rows.tsv"):
    h = hashlib.sha256(open(B+f, "rb").read()).hexdigest()
    print(f, "sha256", h[:16], "size", len(open(B+f, "rb").read()))
rows = {}
with open(B+"evidence__peer__cert__v2run20000-rows.tsv", encoding="utf-8") as fh:
    hdr = fh.readline().rstrip("\n").split("\t")
    for line in fh:
        p = line.rstrip("\n").split("\t")
        d = dict(zip(hdr, p)); rows[int(d["n"])] = d
print("rows", len(rows), "n range", min(rows), max(rows))
# induction rows: Y0(m)=firstQ_ell >= m - floor(3/4 m^{2/3}) for 10001<=m<=20000
def fl34(m):
    f = int(round(0.75*m**(2/3)))
    while 64*f**3 > 27*m*m: f -= 1
    while 64*(f+1)**3 <= 27*m*m: f += 1
    return f
viol = 0; minmar = None
for m in range(10001, 20001):
    Y0 = int(rows[m]["firstQ_ell"]); bnd = m - fl34(m); mar = Y0 - bnd
    if mar < 0: viol += 1
    if minmar is None or mar < minmar[0]: minmar = (mar, m, Y0, bnd)
print("induction rows: violations", viol, "min margin (margin,m,Y0,bound)", minmar)
# (ㅂ): n+1-l* - 0.59963 (n+1)^{2/3} - 1.24847 (n+1)^{1/3}, l* = firstQ_ell
mp.mp.dps = 30
def off(n):
    l = int(rows[n]["firstQ_ell"]); N = mp.mpf(n+1)
    return N - l - mp.mpf('0.59963')*N**(mp.mpf(2)/3) - mp.mpf('1.24847')*N**(mp.mpf(1)/3)
for lo, hi in ((50, 900), (901, 20000)):
    vals = [(off(n), n) for n in range(lo, hi+1)]
    mn = min(vals); mx = max(vals)
    print(f"{lo}<={{n}}<={hi}: min {mp.nstr(mn[0],12)} at n={mn[1]}, max {mp.nstr(mx[0],12)} at n={mx[1]}")
print("peak column check n=5..8:", [(n, rows[n]["firstQ_ell"], rows[n]["mode_ell_mid"]) for n in range(5, 9)])
print("rows with mode_ell_mid != firstQ_ell:", sum(1 for n in rows if rows[n]["mode_ell_mid"] != rows[n]["firstQ_ell"]))
