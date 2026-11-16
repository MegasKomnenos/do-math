from fractions import Fraction as F
import math
k=10000
def ex(q,k):
    pi=F(q*(q-1),2*(k+1)); return q+(k+q)*pi/(1-pi)
cnt=0; cnt_ord=0; mn=None
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0,51-q-qp):
            cnt+=1; cnt_ord+= 1 if q==qp else 2
            v=1-F(j,k)*(ex(q,k)+ex(qp,k))-(ex(q,k)*(qp-1)+ex(qp,k)*(q-1))/(2*k)
            if mn is None or v<mn[0]: mn=(v,(q,qp,j))
print("unordered",cnt,"ordered",cnt_ord,"min",float(mn[0]),mn[1])
# (c) nu_P for table K1 with (M,tf)
def lb(q,qp,j,k,tf):
    def nh(q): return 0.0 if q==1 else tf*q**1.5/k
    def exh(q): return q+(k+q)*nh(q)/(1-nh(q))
    return 1-(j/k)*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*k)
tab=[(12000,120,.54),(13000,120,.54),(14000,120,.54),(15000,120,.54),(20000,120,.54),(30000,250,.593),(50000,250,.593),(100000,300,.522),(200000,450,.548),(500000,450,.548),(1000000,700,.519)]
for K1,M,tf in tab:
    nu=2; last=None
    while True:
        worst=None
        for q in range(1,nu):
            for qp in range(q,nu-q+1):
                j=nu-q-qp
                if j<0: continue
                v=lb(q,qp,j,K1,tf)
                if worst is None or v<worst[0]: worst=(v,(q,qp,j))
        if worst[0]<=0: break
        last=(nu,worst); nu+=1
    print(K1, "nu_P", last[0], "worst", last[1][1], "%.4f"%last[1][0], "next shell min %.4f"%worst[0])
# (d) counts
ga=sum(2*k+40-max(20001,2*k+1)+1 for k in range(9981,11100) if 2*k+40>=max(20001,2*k+1))
na=sum(2*k+102-max(2*k+41,20001)+1 for k in range(9950,12000) if 2*k+102>=max(2*k+41,20001))
da=sum(102-59+1 for k in range(12000,13000))+sum(102-80+1 for k in range(13000,14000))+sum(102-96+1 for k in range(14000,15000))
print("(가)",ga,"(나)",na,"(다)",da,"(나)+(다)",na+da)
