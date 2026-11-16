# K4: 5.5절의 수치 상수 재검산 (보조정리 5-30, right-part, hover-tail, scaled-integrand(마), 5.5.2 wid)
from math import *
out=[]
n=50001
# 5-30 top_pi bounds
a=(2*pi)**-0.5*sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*exp(1/(12*(n+1)))
out.append(("top_pi y<=2n/3 bound <=0.0133", a))
b=(0.15)**1.5
out.append(("(1.5/10)^1.5 <=0.0581", b))
c=(2*pi)**-0.5*0.0581*(1+1/n)**1.5*exp(1/(12*(n+1)))
out.append(("top_pi y>2n/3 bound <=0.0232", c))
d=exp(-2)*((n+1)/(n-1))**1.5*exp(1/(12*(n+1)))
out.append(("pi_n(n-1) bound <0.1354", d))
out.append(("e^-1-0.1354-0.0232 >0.2", exp(-1)-0.1354-0.0232))
# wid bound at y=25000
y=25000.0; t=y+1+ceil(0.75*(1.1*y)**(2/3))
out.append(("t-1<=1.1y at y=25000", (t-1, 1.1*y)))
# t0<=n: 10((n+1)/2)^(2/3) > 6 n^(2/3)+2
out.append(("10((n+1)/2)^(2/3)-6n^(2/3)-2 >0", 10*((n+1)/2)**(2/3)-6*n**(2/3)-2))
# band-inequality conditions at n=50001, y=2n/3
y=2*n/3
out.append(("0.4(n-y) >= 6y^(2/3)+1", (0.4*(n-y), 6*y**(2/3)+1)))
out.append(("wid<=0.75(1.1y)^(2/3)+1 <= 0.7(n-y)", (0.75*(1.1*y)**(2/3)+1, 0.7*(n-y))))
out.append(("n/3 > 10(2n/3)^(2/3)", (n/3, 10*(2*n/3)**(2/3))))
# right-part constants
y=33334.0; r=10357.0
out.append(("y>2n/3 -> y>=33334 (2*50001/3)", 2*50001/3))
out.append(("10*33334^(2/3)-1", 10*y**(2/3)-1))
chi=0.2*r-7.3
out.append(("chi_w>=0.2r-7.3 at r=10357", chi))
hv_coef=2/sqrt(pi)*(1+1/2064)+1/sqrt(pi)
out.append(("hv coef <=1.6932", hv_coef))
tt=y**(1/3)
eps=1.6932*(tt/10+1)/sqrt(2*tt*tt-7.5)
out.append(("eps_hov <=0.1573", eps))
out.append(("sqrt(2/pi)/sqrt(2064) <=0.01757", sqrt(2/pi)/sqrt(2064)))
out.append(("0.75*1.1^(2/3) <=0.7993", 0.75*1.1**(2/3)))
out.append(("(1.50003/0.9199)^1.5/sqrt(2pi) <=0.8308", (1.50003/0.9199)**1.5/sqrt(2*pi)*exp(1/(12*50002))))
out.append(("0.24924/sqrt(10358) <=0.00245", 0.24924/sqrt(10358)))
out.append(("0.92007(r+1)-1 >= 0.9199(r+1) at r+1=10358", (0.92007*10358-1, 0.9199*10358)))
out.append(("(r+1)/(r-wid) <=1.0872", 10358/(10358*0.92007-2)))
out.append(("(0.7993+2/y^(2/3))^1.5 <=0.7172", (0.7993+2/y**(2/3))**1.5))
out.append(("eps0 <=0.1305", 1.5*(0.07993*10358+1)/(0.92007*10358-1)))
out.append(("(1+wid/y)^1.5 <=1.0376", (1+(0.7993*y**(2/3)+1)/y)**1.5))
W=(2*pi)**-0.5*(2/3)*0.7172*1.5*1.0872*1.0376*exp(0.1305+1/400008)
out.append(("(r+1)/y W <=0.3678", W))
out.append(("e^-c4 >=0.9936", exp(-(1/156+1/(12*33334)+1/(12*50002)))))
out.append(("0.8427*0.71216*0.9936*1.9366-0.3678 >=0.7869", 0.8427*0.71216*0.9936*1.9366-0.3678))
out.append(("Psi_R at 2/3", 0.7869*2/3-(1-2/3)-2.5e-5))
# hover-tail: z^1.5 (2z-3)^-0.5 >= 2 sqrt2 for integer z>=2
out.append(("min over z=2..50 of z^1.5(2z-3)^-.5", min(z**1.5/sqrt(2*z-3) for z in range(2,51))))
# scaled-integrand constants
h0=0.0342; out.append(("h0^3>=1/25000", (h0**3, 1/25000)))
vmax=sqrt(6*h0); c3=1/sqrt(2)-vmax/3
out.append(("c3>=0.556", c3))
f12=c3*12**1.5-12-log(sqrt(2)*(1+6*h0)*12/c3)
out.append(("f(12)>7", f12, sqrt(2)*(1+6*h0)*12/c3))
out.append(("f'(12)>0", 1.5*c3*sqrt(12)-1-1/12))
# borel-gf (다): u0 max <1
out.append(("max u0", max(sqrt(2*s)-2*s/3 for s in [i/1000 for i in range(0,5000)])))
# stop-lower MVT/chord constants
out.append(("1.5*0.95^-2.5 <=1.706", 1.5*0.95**-2.5))
out.append(("(0.8^-1.5-1)/0.2 <=1.988", (0.8**-1.5-1)/0.2))
out.append(("4/sqrt(2pi) <1.596", 4/sqrt(2*pi)))
# 5-11: r0(20001)
out.append(("r0(20001)", floor(0.75*20001**(2/3))))
for o in out: print(o)
