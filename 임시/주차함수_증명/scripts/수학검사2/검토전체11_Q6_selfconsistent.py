# 정리 self-consistent-S (다) 표와 따름정리 cor-S-prime 세 값의 독립 재계산 (Decimal 60자리; 표 값의 자릿수 대조용)
from decimal import Decimal as D, getcontext
getcontext().prec = 60
E = D(1).exp()
def ao_list(M):
    a=[D(1)]
    for m in range(M):   # a°_{m+1}=a°_m*(1+1/(m+1))^m
        a.append(a[m]*((D(1)+D(1)/D(m+1))**m))
    return a
def xk(k): return (D(k)/D(k+1))**(k-1)
def table(L,J,k0):
    ao=ao_list(k0+J+5)
    def fr(m): return ao[m+1]/ao[m]
    js=0
    while fr(js) < L: js+=1
    js-=1
    kR=max(2*js+2, int((L**(js+2)/ao[js+1]).to_integral_value(rounding="ROUND_CEILING")))
    Eu=sum(ao[J+i]/ao[J]*E**(-i) for i in range(1,k0-js+1))
    r=L/E; Einf=r*(1-r**k0)/(1-r)
    R=max(1/(1+Eu),1/(1+Einf))
    xbar=[ao[v]*L**(-(v+1)) for v in range(J)]
    qbar=[max(D(0),1-sum(ao[j]*L**(-(j+1)) for j in range(v))) for v in range(J)]
    Xi=sum(max(D(0),xbar[v]-R*qbar[v]) for v in range(J))
    x0=xk(k0)
    Xik=sum(max(D(0),ao[v]*x0*L**(-v)-R*qbar[v]) for v in range(J))
    A0=x0+Xik/(L*(1-Xi)); B0=R*(1+Xik/(1-Xi))
    return js,kR,R,Xi,Xik,A0,B0
rows=[(D("2.67"),25,501,D("0.13")),(D("2.7"),70,1855,D("0.08")),(D("2.71"),100,6098,D("0.055"))]
tab={501:(D("1.4708"),D("0.098505")),1855:(D("2.5335"),D("0.060259")),6098:(D("2.7354"),D("0.0422"))}
for L,J,k0,y in rows:
    js,kR,R,Xi,Xik,A0,B0=table(L,J,k0)
    print(f"L={L} J={J} k0={k0}: j*={js} kR={kR} R={R:.10f} Xi={Xi:.8f} Xi(k0)={Xik:.8f} A0={A0:.6f} B0={B0:.8f}")
    xi=D(1)/D(k0)
    g=lambda A,B:(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A*xi+B*y)
    print(f"   g_S exact-ish: {g(A0,B0):.6E}; with table values: {g(*tab[k0]):.6E}; vertex/k^2={(3*xi+xi*xi)/2+(1+xi)**2*B0/2:.6f} <= y={y}")
