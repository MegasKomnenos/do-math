# 검토전체18 L4: 장5B의 명시 상수 검산 (5.5.2, 5-30, right-part, band-inequality 조건)
from math import *
out=[]
# 5.5.2: 10((n+1)/2)^{2/3} > 6 n^{2/3}+2 at n=50001 ; wid bound at y=25000
n=50001; out.append(("t0<=n: 10((n+1)/2)^(2/3)-6n^(2/3)-2", 10*((n+1)/2)**(2/3)-6*n**(2/3)-2))
y=25000; out.append(("wid: ceil(0.75(1.1y)^(2/3)) <= 0.1y", ceil(0.75*(1.1*y)**(2/3)), 0.1*y))
# 5-30
f=lambda n: (2*pi)**-0.5*sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*exp(1/(12*(n+1)))
out.append(("5-30 case y<=2n/3 bound <=0.0133", f(50001)))
out.append(("5-30 case y>2n/3: (0.15)^1.5, *(2pi)^-1/2*(1+1/n)^1.5 e^(1/12(n+1))", 0.15**1.5, (2*pi)**-0.5*0.15**1.5*(1+1/n)**1.5*exp(1/(12*(n+1)))))
out.append(("5-30 pi_n(n-1) <= e^-2 ((n+1)/(n-1))^1.5 e^(1/12(n+1))", exp(-2)*((n+1)/(n-1))**1.5*exp(1/(12*(n+1)))))
out.append(("5-30 bracket e^-1-0.1354-0.0232", exp(-1)-0.1354-0.0232))
# right-part
y=33334; t=y**(1/3); r=ceil(10*y**(2/3)-1)
out.append(("right: y^(2/3)*10-1", 10*y**(2/3)-1, "r>=", r))
out.append(("right: chi_w>=0.2r-7.3", 0.2*r-7.3))
out.append(("right: e^-c4 >= exp(-(1/156+1/(12y)+1/(12*50002)))", exp(-(1/156+1/(12*y)+1/(12*50002)))))
hv=lambda c: c**-0.5*(2/sqrt(pi)*(1+1/c)+1/sqrt(pi))
out.append(("right: hv(2064)*sqrt(2064) <=1.6932", hv(2064)*sqrt(2064)))
out.append(("right: eps_hov at y=33334", 1.6932*(t/10+1)*(2*t*t-7.5)**-0.5))
out.append(("right: sqrt(2/pi)/sqrt(2064)", sqrt(2/pi)/sqrt(2064)))
out.append(("right: 0.75*1.1^(2/3)", 0.75*1.1**(2/3)))
out.append(("right: (2pi)^-1/2 (1.50003/0.9199)^1.5", (2*pi)**-0.5*(1.50003/0.9199)**1.5, "*e^(1/(12*50002))", (2*pi)**-0.5*(1.50003/0.9199)**1.5*exp(1/(12*50002))))
out.append(("right: 0.24924/(r+1)^0.5 at r=10357", 0.24924/(10358)**0.5))
out.append(("right: (0.7993 y^(2/3)+2)^1.5 / y at y=33334", (0.7993*y**(2/3)+2)**1.5/y))
out.append(("right: (r+1)/(r-wid) with wid=0.07993(r+1)+1, r=10357", 10358/(10357-(0.07993*10358+1))))
out.append(("right: eps0 <= 1.5 wid/(r+1-wid)", 1.5*(0.07993*10358+1)/(10358-(0.07993*10358+1))))
out.append(("right: (1+wid/y)^1.5, wid=0.7993y^(2/3)+1", (1+(0.7993*y**(2/3)+1)/y)**1.5))
out.append(("right: (r+1)/y * W bound", (2*pi)**-0.5*(2/3)*0.7172*1.5*1.0872*1.0376*exp(0.1305+1/400008)))
out.append(("right: 0.8427*0.71216*0.9936*1.9366-0.3678", 0.8427*0.71216*0.9936*1.9366-0.3678))
out.append(("right: Psi_R at lambda=2/3", 0.7869*2/3-(1/3)-2.5e-5))
# band-inequality conditions at n=50001
n=50001
out.append(("band: n/3 - 10(2n/3)^(2/3)", n/3-10*(2*n/3)**(2/3)))
out.append(("band: 0.4n/3 - (6(2n/3)^(2/3)+1)", 0.4*n/3-(6*(2*n/3)**(2/3)+1)))
out.append(("band: wid bound at y=2n/3 vs 0.7(n-y)", 0.75*(1.1*2*n/3)**(2/3)+1, 0.7*n/3))
out.append(("band: c4 denominators derivative 0.4(1-2/3)-4(2/3)^(2/3)n^(-1/3)", 0.4/3-4*(2/3)**(2/3)*n**(-1/3)))
# 5-26 sanity: 3/2 * (1/(n-i)-1/i) = 3/2 (2i-n)/(i(n-i))
i=30000; out.append(("5-26 identity", 1.5*(1/(n-i)-1/i), 1.5*(2*i-n)/(i*(n-i))))
# stop-lower constants
out.append(("stop: 1.5*0.95^-2.5", 1.5*0.95**-2.5, "(0.8^-1.5-1)/0.2", (0.8**-1.5-1)/0.2, "4/sqrt(2pi)", 4/sqrt(2*pi)))
# scaled: h0^3 >= 1/25000 ; upsilon_max; c3; f(12)
h0=0.0342; um=sqrt(6*h0); c3=1/sqrt(2)-um/3
out.append(("scaled: h0^3*25000", h0**3*25000, "upsilon_max", um, "c3", c3, "f(12)", c3*12**1.5-12-log(sqrt(2)*(1+6*h0)*12/c3)))
for o in out: print(*o)
