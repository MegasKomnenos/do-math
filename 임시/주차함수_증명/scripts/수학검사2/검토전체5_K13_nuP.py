# D.band102-integer (ㄷ): nu_P(K1) 재계산 — 배정밀도로 빠르게 찾고, 경계 껍질 둘은 mpmath로 다시 확인
import mpmath as mp
mp.mp.dps=30
def make_lb(K1,M,C,ar):
    C=ar(C)
    def nh(q): return ar(0) if q==1 else C*ar(q)**ar(1.5)/K1
    ex=[None]+[q+(K1+q)*nh(q)/(1-nh(q)) for q in range(1,M+1)]
    def lb(q,qp,j): return 1-ar(j)/K1*(ex[q]+ex[qp])-(ex[q]*(qp-1)+ex[qp]*(q-1))/(2*K1)
    return lb
def shell_min(lb,nu,M):
    worst=None
    for q in range(1,nu):
        for qp in range(q,nu-q+1):
            if q>M or qp>M: continue
            v=lb(q,qp,nu-q-qp)
            if worst is None or v<worst[0]: worst=(v,(q,qp,nu-q-qp))
    return worst
table=[(12000,120,'0.54'),(13000,120,'0.54'),(14000,120,'0.54'),(15000,120,'0.54'),(20000,120,'0.54'),(30000,250,'0.593'),(50000,250,'0.593'),(100000,300,'0.522'),(200000,450,'0.548'),(500000,450,'0.548'),(1000000,700,'0.519')]
for K1,M,C in table:
    lbf=make_lb(K1,M,C,float)
    nu=2; last=None
    while True:
        w=shell_min(lbf,nu,M)
        if w is not None and w[0]<=0: break
        last=(nu,w); nu+=1
    lbm=make_lb(K1,M,C,mp.mpf)
    wP=shell_min(lbm,last[0],M); wF=shell_min(lbm,nu,M)
    print("K1",K1,"nu_P",last[0],"worst",wP[1],"lb=%.4f"%float(wP[0]),"| shell",nu,"min lb=%.4f"%float(wF[0]),wF[1])
