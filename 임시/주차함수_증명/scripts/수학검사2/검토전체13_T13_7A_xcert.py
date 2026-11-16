import json, glob
from mpmath import mp, mpf, e, pi, sqrt, exp, findroot, factorial
rows=[]
for f in glob.glob(r"원고_자료/세션_재계산/xcert_iv/resB_p[01].jsonl"):
    for line in open(f,encoding="utf-8"):
        line=line.strip()
        if line: rows.append(json.loads(line))
print("rows",len(rows), "keys", list(rows[0].keys())[:30])
ck=[k for k in rows[0].keys() if 'c' == k or k.startswith('c_') or k.endswith('_c') or k=='c_used' or k=='cbest']
print("c-like keys", ck)
# find key with c values 3/4
for key in rows[0].keys():
    vals=set(str(r.get(key)) for r in rows)
    if vals<= {'3','4'} : 
        c3=sorted(r['k'] for r in rows if str(r[key])=='3'); print(key, "c=3 count", len(c3), "range", c3[0], c3[-1], "k>=607 all c=4:", all(str(r[key])=='4' for r in rows if r['k']>=607))
mp.dps=30
S0=sum(mpf(n-1)**(n-1)*exp(-n)/factorial(n) for n in range(1,257))
Xc=1-S0-2/sqrt(2*pi)/e/sqrt(257)+1/sqrt(2*pi)/e*mpf(257)**(-1.5)
print("S0",S0,"Xc",Xc)
k=mpf(10)**30
def CL(s):
    tb1L=exp(s)*(1/s+1.5/s**2-3*exp(-s))
    return S0+1/sqrt(2*pi)/e*(2/sqrt(257)-2/sqrt(k)+(tb1L-2*s*sqrt(257/k)*exp(257*s/k))/sqrt(k)-mpf(257)**(-1.5)*exp(257*s/k))
s1=findroot(lambda s: CL(s)-1, 39)
print("s1",s1)
