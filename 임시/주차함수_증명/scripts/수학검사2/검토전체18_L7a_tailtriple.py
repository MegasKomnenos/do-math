import numpy as np, math
def logBor(w): return -w+(w-1)*math.log(w)-math.lgamma(w+1)
def kebar(K1,M):
    a=M-1; b=K1+1; c=K1+2-M
    return 3*a/(2*b)+a*(3*M-4)/(12*b*b)+a*a/(2*b*c)+a**4/(12*b*b*c)
def check712(K1,M,tf):
    ek=math.exp(kebar(K1,M)); mn=None
    for q in range(2,M+1):
        s=np.arange(0,q-1); r=q-1-s
        val=tf*q**1.5-ek*np.sum(np.exp([logBor(x+1) for x in s])*(r+tf*r**1.5))
        if mn is None or val<mn[0]: mn=(float(val),q)
    return mn
triples=[(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]
for t in triples: print("7.12",t,check712(*t))
def nuP(K1,M,tf):
    k=K1; q=np.arange(1,M+1,dtype=float)
    nh=np.where(q>=2,tf*q**1.5/k,0.0); ex=q+(k+q)*nh/(1-nh)
    Q,QP=np.meshgrid(q,q,indexing='ij'); EQ,EQP=np.meshgrid(ex,ex,indexing='ij')
    last=0
    for nu in range(1,M+2):
        J=nu-Q-QP; mask=(Q<=QP)&(J>=0)
        if not mask.any(): last=nu; continue
        lb=1-J/k*(EQ+EQP)-(EQ*(QP-1)+EQP*(Q-1))/(2*k)
        if lb[mask].min()>0: last=nu
        else: return last, lb[mask].min()
    return last,None
table=[(12000,120,0.54),(13000,120,0.54),(14000,120,0.54),(15000,120,0.54),(20000,120,0.54),(30000,250,0.593),(50000,250,0.593),(10**5,300,0.522),(2*10**5,450,0.548),(5*10**5,450,0.548),(10**6,700,0.519)]
for t in table: print("nuP",t,nuP(*t))
