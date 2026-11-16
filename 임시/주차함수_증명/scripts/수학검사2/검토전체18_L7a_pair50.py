from fractions import Fraction as F
k=10000
def pis(q): return F(q*(q-1),2*(k+1))
def exb(q):
    p=pis(q); return q+(k+q)*p/(1-p)
cnt=0; mn=None; arg=None
for j in range(0,49):
    for q in range(1,50):
        for qp in range(q,50):
            if q+qp+j>50: continue
            cnt+=1
            r=1-F(j,k)*(exb(q)+exb(qp))-(exb(q)*(qp-1)+exb(qp)*(q-1))/(2*k)
            if mn is None or r<mn: mn=r; arg=(q,qp,j)
print(cnt, arg, float(mn))
