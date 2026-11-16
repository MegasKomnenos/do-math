# T5 numeric re-checks for chapter 6 constants
from mpmath import mp, mpf, sqrt, exp, log, e, pi, ceil, floor
mp.dps = 30
def Bor(d): return exp(-d)*mpf(d)**(d-1)/mp.factorial(d)
# 6.1 (6.8)
k=mpf(4000); C=3
qs = ceil((C*k)**(mpf(2)/3)); print("q*(4000)=",qs)
lhs = 1-mpf('1.6')/sqrt(525); print("LHS(525)=",lhs)
br = mpf('0.8')*sqrt(2)/3*(1+mpf(1)/1048) + mpf('3.923')*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3) + mpf('1.5')/(3*sqrt(525))
print("bracket terms:", mpf('0.8')*sqrt(2)/3*(1+mpf(1)/1048), mpf('3.923')*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3), mpf('1.5')/(3*sqrt(525)), "sum",br, "2x",2*br)
print("1.2(1-2/525)^-2.5=",mpf('1.2')*(1-mpf(2)/525)**(-mpf(5)/2), " 1.2(1+2/525)^.5=",mpf('1.2')*(1+mpf(2)/525)**mpf('0.5'), " 1.5(1-1/525)^-2.5=",mpf('1.5')*(1-mpf(1)/525)**(-mpf(5)/2))
# Up max
print("Up(1/2)=",sqrt(mpf(1)/2)*2)
# 6.2 B2
def B2(k):
    k=mpf(k); return (1-1/e)+(exp(mpf(3)/2+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
for kk in (42,43,2000): print("B2(%d)="%kk, B2(kk))
# exact small k sum
from fractions import Fraction
def tilt_sum(k):
    x = Fraction(k, k+1)**(k-1)
    s = Fraction(0)
    for n in range(2,k+2):
        s += Fraction(n**(n-1), __import__('math').factorial(n)) * x**n
    return s
print("tilt_sum(2)=",tilt_sum(2), " max over 2..42:", max((float(tilt_sum(k)),k) for k in range(2,43)))
# 1-B2(2000) >= 0.307 ?
print("1-B2(2000)=",1-B2(2000))
# increment-bounds (다)
print("k rhoH(3k) k=2000:", mpf('0.307')*2000/3999)
# 6.3 lemma omega numbers
print("Xstar=",(5-sqrt(7))/6, " max=",(10+7*sqrt(7))/54)
y=50
print("tl^-1 <=",1/(1-mpf(3)/(4*(y+1))), " e^{1/24+1/612}=",exp(mpf(1)/24+mpf(1)/612), " 1+1/51=",1+mpf(1)/51)
u = exp(mpf(1)/24+mpf(1)/612)*(1/(1-mpf(3)/(4*51)))*(1+mpf(1)/51)*mpf(4)/3
print("u<=",u, " 0.5282*1.449=",mpf('0.5282')*mpf('1.449'), " 0.52815*u=",mpf('0.52815')*u)
print("L/G V>=2:", mpf('1.5')/53*(mpf(4)/3)*mpf('0.5')*(1+mpf(1)/51)*(1/(1-mpf(3)/(4*51))))
print("L/G V=1:", mpf('1.5')/52*mpf('2.02')*mpf('0.51')*(1+mpf(1)/51)*(1/(1-mpf('1.5')/(52*51))))
# d=2 case
print("1.03 check e^{3/(2*51)}=",exp(mpf(3)/(2*51)), " 1.545/e=",mpf('1.545')/e, " e^-2=",exp(-2))
print("c_{y+2} lower:", (2*exp(-2)+exp(-1)-mpf('1.03')*exp(-2)/51))
print("0.12/e=",mpf('0.12')/e)
yy=mpf(50); print("ratio d=3:", mpf('0.0441')*(yy-1)/(yy+3)**2 / (mpf('1.2')*(yy+1)/((yy+2)**2*(yy+3))))
print("d=y+2 ratio bound:", mpf('1.03')*exp(-1)/2)
# 6.4 u(k), witness
def u(k):
    k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)/sqrt(k)
for kk in (3131,6667,10000): print("u(%d)="%kk,u(kk), " 2u=",2*u(kk))
print("witness bound n=20000:", mpf('1.99')+mpf('0.59963')*mpf(20001)**(mpf(2)/3)+mpf('1.24847')*mpf(20001)**(mpf(1)/3))
print("(6262)^(2/3)=",mpf(6262)**(mpf(2)/3), " 0.65*3131-1=",mpf('0.65')*3131-1)
print("9*(3/2)^1.5=",9*mpf('1.5')**mpf('1.5'), " *4/3=",9*mpf('1.5')**mpf('1.5')*4/3)
print("Ups hat <", u(3131)/2)
# 6.5
print("50.62/sqrt(3130)=",mpf('50.62')/sqrt(3130))
for kk in (3131,6667,10000):
    k=mpf(kk); vp=max(k+1,4000); io=2*k+1-vp
    t1=2*min(1,3*vp*io**(-mpf(3)/2)); t2=2*u(k); t3=mpf('50.62')/sqrt(k-1)
    print("v(%d): terms"%kk, t1,t2,t3, " v=",2-t1-t2-t3)
# m*, Gamma*
tp=mpf('0.55'); kap=mpf('2.4978')
a=tp; b=-(kap*tp+2); c=kap
chi=(-b+sqrt(b*b-4*a*c))/(2*a); print("chi root=",chi, " m=",(chi**2-kap*chi)*exp(-tp*chi))
x=mpf(3132)/3130; print("Gamma*=",x/((1+x)**(1-tp)-1))
print("ex_max(3130)=",mpf(3131)/6261, " 2-exmax-20/(9t)=",2-mpf(3131)/6261-mpf(20)/(9*3130), " kappa_d min=",mpf('1.498')+2*mpf(3130)/6261)
print("14.653+35.952=",mpf('14.653')+mpf('35.952'))
cc=1/sqrt(2*pi)
print("3c(8.133+10.301c)=",3*cc*(mpf('8.133')+mpf('10.301')*cc), " 1.5*2.7323*0.8051*c*(17.951+23.462c)=",mpf('1.5')*mpf('2.7323')*mpf('0.8051')*cc*(mpf('17.951')+mpf('23.462')*cc))
# lemma-N constants
print("12.15:",4.5*2+4.5*2/3+0.375*2/5, " 4.908:",4.5*2/3+4.5*2/5+0.375*2/7, " 7.25:",3*2+1.875*2/3," 2.75:",3*2/3+1.875*2/5)
# 24000/2263^1.5
print("24000/2263^1.5=",24000/mpf(2263)**mpf('1.5'))
