from mpmath import mp, mpf, zeta, pi, exp, cos, sin, log, e, mpc, arg, re, im, fabs
mp.dps = 30
def lm(m): return (2+mpf(1)/m)*zeta(2*m)/pi**(2*m)
M=60
L=[lm(m) for m in range(1,M+1)]
def loget(phi): return sum(L[m-1]*phi**(2*m) for m in range(1,M+1))
def lg(phi): return sum(2*m*L[m-1]*phi**(2*m-2) for m in range(1,M+1))
# hand bounds
print("sum 2m l_m 4^(1-m) =", sum(2*m*L[m-1]*mpf(4)**(1-m) for m in range(1,M+1)))
print("sum_{m>=2} l_m 4^(1-m) =", sum(L[m-1]*mpf(4)**(1-m) for m in range(2,M+1)))
print("0.5*cos(pi/4) =", cos(pi/4)/2)
# numerics on arc
N=2000
mxlg=0; mnre=10
ets=[]
for i in range(N+1):
    a=-pi/8*i/N
    phi=mpf(1)/2*exp(mpc(0,1)*a)
    v=fabs(lg(phi)); mxlg=max(mxlg,v)
    le=loget(phi)
    mnre=min(mnre, re(le)/mpf(1)/4*16)  # re/|phi|^2, |phi|^2=1/4
    ets.append(exp(le))
print("max|lg| on arc", mxlg, " min Re log et/|phi|^2", mnre)
# min |et - xi| over ag' in (0,1]
mn=10
K=4000
for j in range(1,K+1):
    ag=mpf(j)/K
    pt=exp(mpc(0,1)*ag); xi=pt*exp(1-pt)
    for et in ets[::20]:
        d=fabs(et-xi)
        if d<mn: mn=d; where=(ag,et)
print("min|et-xi| arc x ag'", mn, where)
print("needed for 1.8 at k=10001:", mpf('1.8')/mpf(10001)**(mpf(2)/3))
# arc bound at k=10001
k=mpf(10001); R0=mpf(1)/2*k**(mpf(1)/2)
print("log arc bound k=10001:", log(pi/8*R0*mpf('1.03')*R0*R0*exp(-mpf('0.34')*R0*R0)/mpf('1.8')))

# --- hand bound for the denominator on the arc (R11 problem 11; constant 0.1666 from D.critical-window-rig)
mn=10
for j in range(1,200001):
    a=mpf(j)/200000
    v=max(mpf('0.1666')*a**3, exp(mpf('0.085'))-exp(1-cos(a)))
    if v<mn: mn=v; at=a
print("min max(0.1666 ag'^3, e^0.085 - e^(1-cos ag')) =", mn, "at ag' =", at, "; times 10001^(2/3) =", mn*mpf(10001)**(mpf(2)/3))
print("171^(3/2)+9*171 =", mpf(171)**mpf('1.5')+9*171)
