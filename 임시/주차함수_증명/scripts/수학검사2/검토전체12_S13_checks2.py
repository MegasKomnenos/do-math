from fractions import Fraction as F
import math, json, glob, os, re, sys
# (a) h recursion test for D.column-certification-k500, x=1
def test_h(y, N=14):
    # e_n = A_{n,y-1}/n! via last-car recursion
    e=[F(1)]
    for n in range(1,N+1):
        s=sum(min(j+1,y)*e[j]*e[n-1-j] for j in range(n))
        e.append(s/n)
    # g_n: exp(sum_{m<=y} m^{m-1} x^m/m!)
    P=[F(0)]+[F(m**(m-1),math.factorial(m)) if m<=y else F(0) for m in range(1,N+1)]
    g=[F(1)]
    for n in range(1,N+1):
        g.append(sum(j*P[j]*g[n-j] for j in range(1,n+1))/n)
    # h = 1 - g/e  (series division)
    # q = g/e : e*q = g
    q=[]
    for n in range(N+1):
        q.append((g[n]-sum(e[j]*q[n-j] for j in range(1,n+1)))/e[0])
    h=[-q[0]+1]+[-q[n] for n in range(1,N+1)]
    ao=lambda m: F(1) if m==0 else F((m+1)**(m-1),math.factorial(m))
    ok=True
    for n in range(1,N+1):
        rhs=y*sum(ao(j-1)*h[n-j] for j in range(1,min(y,n)+1)) + (y*g[n-1] if n>=y+1 else 0)
        if n*h[n]!=rhs: ok=False; print("  y",y,"n",n,"lhs",n*h[n],"rhs",rhs)
    # third recursion: e_n = g_n + sum h_j e_{n-j}
    ok3=all(e[n]==g[n]+sum(h[j]*e[n-j] for j in range(1,n+1)) for n in range(N+1))
    # g_n = a°_n for n<=y
    okg=all(g[n]==ao(n) for n in range(0,y+1))
    print("y",y,"h-recursion ok:",ok," third ok:",ok3," g=a° for n<=y:",okg, " h nonneg:",all(x>=0 for x in h), " first h:", [float(x) for x in h[:6]])
for y in (3,4,5): test_h(y)
# (b) pair-check exact min
k=10000
def exb(q):
    pi=F(q*(q-1),2*(k+1)); return q+(k+q)*pi/(1-pi)
best=None
for q in range(1,50):
    for qp in range(q,50-q+1):
        for j in range(0,50-q-qp+1):
            v=1-F(j,k)*(exb(q)+exb(qp))-(exb(q)*(qp-1)+exb(qp)*(q-1))/(2*k)
            if best is None or v<best[0]: best=(v,q,qp,j)
print("pair-check min", float(best[0]), best[1:])
# (c) ke-bar and F_tf margins (float)
def Bor(m): return math.exp(-m+(m-1)*math.log(m)-math.lgamma(m+1))
for (K1,M,tf) in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    ke=3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
    mn=None
    for q in range(2,M+1):
        Fq=tf*q**1.5-math.exp(ke)*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(0,q-1))
        r=Fq/(tf*q**1.5)
        if mn is None or r<mn[0]: mn=(r,q)
    print("tail triple",K1,M,tf,"ke=%.4f"%ke,"min rel margin %.3e at q=%d"%mn, "tf*M^1.5=%.0f"%(tf*M**1.5))
# (d) best_c count
c3=[]
for f in glob.glob(r"원고_자료\세션_재계산\xcert_iv\resB_p[01].jsonl"):
    for line in open(f,encoding="utf-8"):
        r=json.loads(line)
        if r["best_c"]==3: c3.append(r["k"])
print("best_c==3 count",len(c3),"range",min(c3),max(c3))
# (e) record path existence
root=r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
recs=os.listdir(root)
missing=[]; total=0
for f in ["부록D_장7A","부록D_장7B","부록D_장8","부록D_장9","부록D_장10"]:
    txt=open(r"장v2\%s.md"%f,encoding="utf-8").read()
    for m in re.finditer(r"`(records/[^`]+)`",txt):
        p=m.group(1); total+=1
        parts=p.split("/")
        rid=parts[1].rstrip("…")
        cand=[r for r in recs if r.startswith(rid)]
        if len(cand)!=1: missing.append((f,p,"rid?",cand)); continue
        full=os.path.join(root,cand[0],*parts[2:])
        if "*" in full:
            if not glob.glob(full): missing.append((f,p))
        elif not os.path.exists(full.rstrip("/")): missing.append((f,p))
print("record paths checked",total,"missing",len(missing))
for x in missing: print("  ",x)
print("lower-cone files:", len(glob.glob(os.path.join(root,[r for r in recs if r.startswith("r9e782f5")][0],"producer","lower-cone-k*-cut*.json.gz"))))
print("certificate files:", len(glob.glob(os.path.join(root,[r for r in recs if r.startswith("r9e782f5")][0],"producer","certificate-k*.json"))))
