from fractions import Fraction as Fr
import mpmath as mp, json, glob, os
mp.mp.dps=40
# (ㄱ) pair-check-10000
k=10000
def pish(q): return Fr(q*(q-1),2*(k+1))
def exb(q): p=pish(q); return q+(k+q)*p/(1-p)
def rhs(q,qp,j): return 1-Fr(j,k)*(exb(q)+exb(qp))-(exb(q)*(qp-1)+exb(qp)*(q-1))/(2*k)
for NU in ():
    cnt=0; cnt_ord=0; mn=None
    for q in range(1,NU):
        for qp in range(q,NU):
            for j in range(0,NU-q-qp+1):
                cnt+=1; cnt_ord += 1 if q==qp else 2
                v=rhs(q,qp,j)
                if mn is None or v<mn[0]: mn=(v,(q,qp,j))
    print("shell<=",NU,"unordered",cnt,"ordered",cnt_ord,"min %.5f"%float(mn[0]),mn[1])
# (ㄴ) tail triples margins (high precision, not rational)
def Bor(m): return mp.e**(-m)*mp.mpf(m)**(m-1)/mp.factorial(m)
def kebar(K1,M):
    K1=mp.mpf(K1); M=mp.mpf(M)
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
for (K1,M,C) in [] and [(10**4,120,'0.54'),(2*10**4,250,'0.593'),(10**5,300,'0.522'),(10**5,450,'0.548'),(10**6,700,'0.519')]:
    C=mp.mpf(C); ke=kebar(K1,M); ek=mp.e**ke
    B=[Bor(s+1) for s in range(M)]
    mnrel=None
    for q in range(2,M+1):
        F=C*mp.mpf(q)**1.5-ek*sum(B[s]*((q-1-s)+C*mp.mpf(q-1-s)**1.5) for s in range(q-1))
        rel=F/(C*mp.mpf(q)**1.5)
        if mnrel is None or rel<mnrel[0]: mnrel=(rel,q)
    print("triple",K1,M,C,"min rel margin %.3e at q=%d"%(float(mnrel[0]),mnrel[1]),"ke=%.4f"%float(ke))
# (ㄷ) nu_P
def lbk(K1,M,C):
    C=mp.mpf(C)
    def nh(q): return mp.mpf(0) if q==1 else C*mp.mpf(q)**1.5/K1
    def exh(q): x=nh(q); return q+(K1+q)*x/(1-x)
    ex=[None]+[exh(q) for q in range(1,M+1)]
    def lb(q,qp,j): return 1-mp.mpf(j)/K1*(ex[q]+ex[qp])-(ex[q]*(qp-1)+ex[qp]*(q-1))/(2*K1)
    nu=1; last=None
    while True:
        worst=None
        for q in range(1,nu):
            qp=nu-q  # j=0 .. ; lb decreasing in j, so worst at j = nu-q-qp => consider all (q,qp) with j=nu-q-qp>=0
        for q in range(1,nu):
            for qp in range(q,nu-q+1):
                j=nu-q-qp
                if q>M or qp>M: continue
                v=lb(q,qp,j)
                if worst is None or v<worst[0]: worst=(v,(q,qp,j))
        if worst is None:
            nu+=1; continue
        if worst[0]<=0:
            return last, worst
        last=(nu,worst); nu+=1
table=[(12000,120,'0.54'),(13000,120,'0.54'),(14000,120,'0.54'),(15000,120,'0.54'),(20000,120,'0.54'),(30000,250,'0.593'),(50000,250,'0.593'),(100000,300,'0.522'),(200000,450,'0.548'),(500000,450,'0.548'),(1000000,700,'0.519')]
for K1,M,C in table:
    last,fail=lbk(K1,M,C)
    print("K1",K1,"nu_P",last[0],"worst",last[1][1],"lb=%.4f"%float(last[1][0]),"next shell min lb=%.4f"%float(fail[0]), fail[1])
# (A3) 위치 수
A3=sum((13*k*k)//100 - (2*k+1) + 1 for k in range(501,841))
print("A3 positions",A3)
p="C:/math/임시/주차함수_증명/원고_자료/세션_재계산/moment_cert_iv/nM.json"
if os.path.exists(p):
    nM=json.load(open(p))
    print(type(nM), (list(nM.items())[:3] if isinstance(nM,dict) else nM[:3]))

if os.path.exists(p):
    vals = nM if isinstance(nM,dict) else None
    if isinstance(nM,dict):
        # 키 추정
        try:
            d={int(k):v for k,v in nM.items()}
        except Exception:
            d=None
        if d:
            def nm(v): return v if isinstance(v,int) else (v.get('nM') if isinstance(v,dict) else None)
            tot=sum(nm(d[k])-10001 for k in range(841,2001))
            print("A5 positions (sum nM-10001):",tot, "nM(841)",nm(d[841]),"nM(2000)",nm(d[2000]))
            print("nM/k^1.5 range", min(nm(d[k])/k**1.5 for k in d), max(nm(d[k])/k**1.5 for k in d))
