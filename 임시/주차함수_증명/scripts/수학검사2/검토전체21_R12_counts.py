# R12: 부록 D 7A·7B 항목의 수치 검산
import json, glob, os, math
from fractions import Fraction
base = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산"
# (1) 정수 부등식
L = 10**21 * 400**10; R = 17**21 * 123**10
print("10^21*400^10 =", L, "%.6e" % L); print("17^21*123^10 =", R, "%.6e" % R, "L>R:", L > R)
# (2) 열 인증 비교 수
def B(k): return -(-k*k//4)
d1 = sum(2*B(k)-2*k for k in range(121,161)); d2 = sum(2*B(k)-2*k for k in range(161,501))
b1 = sum(B(k)+1 for k in range(121,161)); b2 = sum(B(k)+1 for k in range(161,501))
print("direct 121-160:", d1, "161-500:", d2, "band:", b1, b2)
# (3) 반지름의 c 값
for k in (121, 161, 495, 500):
    p = os.path.join(base, "column_k500_iv", "res", f"k{k}.json")
    if os.path.exists(p):
        j = json.load(open(p, encoding="utf-8"))
        keys = [kk for kk in j if 'rad' in kk.lower()]
        print(k, {kk: j[kk] for kk in keys})
        for kk in keys:
            v = j[kk]
            if isinstance(v, str) and '/' in v:
                fr = Fraction(v)
                c = (float(fr)*math.e - 1)*k
                print("  c from radius at k:", c)
# (4) n_M - n^G over all columns; count of positions 20001..n^G-1
nM = json.load(open(os.path.join(base, "moment_cert_iv", "nM.json"), encoding="utf-8"))
print("nM type", type(nM), list(nM.items())[:3] if isinstance(nM, dict) else nM[:3])
NE = {}
for f in glob.glob(os.path.join(base, "column_cert_iv", "res_p*.jsonl")):
    for line in open(f, encoding="utf-8"):
        line=line.strip()
        if not line: continue
        j = json.loads(line); NE[j["k"]] = j.get("NE_new", max(j["n0"], j.get("nV", j.get("n_V", 0))))
print("NE columns", len(NE), min(NE), max(NE))
diffs = []
for k in range(841, 2001):
    nm = nM[str(k)] if isinstance(nM, dict) else None
    if nm is None: break
    nm = nm if isinstance(nm, int) else (nm.get("nM") if isinstance(nm, dict) else nm)
    diffs.append(nm - NE[k])
print("n_M - n^G: min", min(diffs), "max", max(diffs), "n", len(diffs))
print("positions 20001..n^G-1 total:", sum(NE[k]-20001 for k in range(841,2001)))
print("positions 10001..n_M-1 total:", sum((nM[str(k)] if not isinstance(nM[str(k)],dict) else nM[str(k)]['nM'])-10001 for k in range(841,2001)))
print("positions 2k+1..floor(13k^2/100):", sum((13*k*k)//100 - 2*k for k in range(501,841)))
# (5) integer-strips 비교 수
r1 = sum(2*k+19-20001+1 for k in range(9991,10000))
r2 = sum(2*k+40-max(20001,2*k+1)+1 for k in range(9981,11100))
r3 = sum(max(0,58-max(41,20001-2*k)+1) for k in range(9972,12000))
r4 = sum(max(0,102-max(59,max(41,20001-2*k))+1) for k in range(9950,12000))
print("runs:", r1, r2, r3, r4, 1000*44, 1000*23, 1000*7, "sum3-7:", r3+r4+44000+23000+7000)
