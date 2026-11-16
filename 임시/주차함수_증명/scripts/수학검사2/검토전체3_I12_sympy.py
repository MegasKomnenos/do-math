# I12: 기호 검산 — (1) 보조정리 gauss-contraction 잔차 R(iota)의 x^0..x^4 계수, (2) 보조정리 kernel-bounds의 두 유리함수 항등식
import sympy as sp
x,g=sp.symbols('x gamma',positive=True)
ups=lambda gm:(1+gm)/2
C1=lambda gm:(1-ups(gm))/gm**2
C2=lambda gm:-(1-ups(gm))*(2+ups(gm))/gm**5
C3=lambda gm:sp.Rational(5,2)*(1-ups(gm))*(6+gm-gm**2)/gm**8
uhat=lambda gm:ups(gm)+x*C1(gm)+x**2*C2(gm)+x**3*C3(gm)
R=(uhat(g)-1)*uhat(sp.sqrt(g**2+4*x))+(1-g**2)/4
ser=sp.series(R,x,0,5).removeO()
for j in range(5):
    c=sp.simplify(ser.coeff(x,j)); print("x^%d:"%j, c if j<4 else "(gamma=1/3) "+str(c.subs(g,sp.Rational(1,3))))
P=sp.symbols('Psi'); th=2*P/(1-P)
L=2*sum(P**(2*i+1)/(2*i+1) for i in range(4)); U=L+2*P**9/(9*(1-P**2))
up=1+th/2-th**2/44; um=1+th/2-th**2/24
dup=sp.diff(up,P)/sp.diff(th,P); dum=sp.diff(um,P)/sp.diff(th,P)
PT=175-665*P+581*P**2-427*P**3+375*P**4-309*P**5+150*P**6+15*P**7
QT=945+42*P-252*P**2+66*P**3-108*P**4+42*P**5-60*P**6-10*P**7
print("P_Theta identity:", sp.simplify(th**2*dup-(th-L)*up-2*P**3*PT/(1155*(1-P)**3))==0)
print("Q_Theta identity:", sp.simplify(th**2*dum-(th-U)*um+P**4*QT/(945*(1-P)**3*(1+P)))==0)
