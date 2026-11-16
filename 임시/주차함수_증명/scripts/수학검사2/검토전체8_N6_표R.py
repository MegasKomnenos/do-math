# -*- coding: utf-8 -*-
"""자기일관 상계 표: R_J를 어떤 값으로 잡아야 표의 Xi가 재현되는지 역산한다."""
import mpmath as mp
mp.mp.dps = 50
def ao(m): return mp.mpf(m + 1) ** (m - 1) / mp.factorial(m)
layers = [(mp.mpf(267)/100, 25, 501, 82, 0.749711, 0.736245, 0.13), (mp.mpf(27)/10, 70, 1855, 220, 0.854757, 0.849132, 0.08), (mp.mpf(271)/100, 100, 6098, 490, 0.865504, 0.862859, 0.055)]
for L, J, k0, js, Xit, Xikt, y in layers:
    xk0 = (mp.mpf(k0)/(k0+1))**(k0-1)
    xbar = [ao(v)*L**(-(v+1)) for v in range(J)]
    qlow = [max(mp.mpf(0), 1-sum(ao(j)*L**(-(j+1)) for j in range(v))) for v in range(J)]
    Elow = sum(ao(J+i)/ao(J)*mp.e**(-i) for i in range(1, k0-js+1)); Einf=(L/mp.e)*(1-(L/mp.e)**k0)/(1-L/mp.e)
    Rexact = max(1/(1+Elow), 1/(1+Einf))
    def Xi(R): return sum(max(mp.mpf(0), xbar[v]-R*qlow[v]) for v in range(J))
    def Xik(R): return sum(max(mp.mpf(0), ao(v)*xk0*L**(-v)-R*qlow[v]) for v in range(J))
    Rsol = mp.findroot(lambda R: Xi(R)-Xit, Rexact)
    print(f"L={L}: R 정확={mp.nstr(Rexact,9)}, 표 Xi 재현 R={mp.nstr(Rsol,9)}, Xi^(k0)(Rsol)={mp.nstr(Xik(Rsol),7)} (표 {Xikt})")
    for R in [Rexact, Rsol, mp.mpf('0.024992') if L==mp.mpf(267)/100 else (mp.mpf('0.008802') if L==mp.mpf(27)/10 else mp.mpf('0.005691'))]:
        A0 = xk0 + Xik(R)/(L*(1-Xi(R))); B0 = R*(1+Xik(R)/(1-Xi(R)))
        xi = mp.mpf(1)/k0
        g = (y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
        print(f"   R={mp.nstr(R,9)}: Xi={mp.nstr(Xi(R),7)} Xi^(k0)={mp.nstr(Xik(R),7)} A0={mp.nstr(A0,7)} B0={mp.nstr(B0,7)} g={mp.nstr(g,5)}")
