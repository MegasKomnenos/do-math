# 5B 상수 검산 (검토전체21 R4)
from mpmath import mp, mpf, sqrt, pi, exp, log, floor, ceil, e
mp.dps = 30
def Bor(m): return mpf(m)**(m-1)*exp(-m)/mp.factorial(m)
def Ren(j): return mpf(j)**j*exp(-j)/mp.factorial(j) if j>0 else mpf(1)
def pi_n(n,t): return Bor(t)*Bor(n+1-t)/Bor(n+1)
print("== old-5-30 (나) top_pi")
n=mpf(50001)
v1=(2*pi)**-0.5*sqrt(2)*mpf(3)**1.5*(1+1/n)**1.5*n**-0.5*exp(1/(12*(n+1)))
print("y<=2n/3 top_pi bound:", v1, "<=0.0132", v1<=0.0132)
v2=(mpf(1.5)/10)**1.5; print("(1.5/10)^1.5=",v2,"<=0.0581",v2<=0.0581)
v3=(2*pi)**-0.5*mpf('0.0581')*(1+1/n)**1.5*exp(1/(12*(n+1))); print("top_pi right:",v3,"<=0.0232",v3<=0.0232)
v4=exp(-2)*((n+1)/(n-1))**1.5*exp(1/(12*(n+1))); print("pi_n(n-1) bound:",v4,"<0.1354",v4<0.1354)
print("e^-1-0.1354-0.0232=",exp(-1)-mpf('0.1354')-mpf('0.0232'))
print("== joining-width")
v=mpf(20001)**(mpf(1)/3); print("v=",v,">=27",v>=27)
print("m1^(1/3) bound: 1/3+2/(3v^2)=",mpf(1)/3+2/(3*v*v))
print("(v+.34)^2-4.5(v+.34) coeffs: ", 2*mpf('0.34')-4.5, mpf('0.34')**2-4.5*mpf('0.34'))
print("== W# t0<=n: 10((n+1)/2)^(2/3) vs 6n^(2/3)+2 at n=50001:", 10*((n+1)/2)**(mpf(2)/3), 6*n**(mpf(2)/3)+2)
print("== landing-mass")
a=mpf('1.15')
print("1.15^(2/3)+2.3(1.15^(-1/3)-6^(-1/2))=", a**(mpf(2)/3)+mpf('2.3')*(a**(-mpf(1)/3)-mpf(6)**-0.5), "<=2.3541")
print("2.3(sqrt6-1.15^(1/3))=", mpf('2.3')*(sqrt(6)-a**(mpf(1)/3)), "<=3.2242")
print("1-1.15/6^1.5=",1-a/mpf(6)**1.5,">=0.9217")
print("3.2242-36*1.15/6^1.5=",mpf('3.2242')-36*a/mpf(6)**1.5,"<=0.4074")
u=mpf(25000)**(mpf(1)/3); print("u=",u,">29.24",u>29.24)
print("2.3541/u=",mpf('2.3541')/u,"0.4074/u^2=",mpf('0.4074')/u**2,"2/u^3=",2/u**3)
print("sum:",mpf('0.9217')-mpf('2.3541')/u-mpf('0.4074')/u**2-2/u**3)
Y=25000; Q=int(floor(6*mpf(Y)**(mpf(2)/3))); print("Q=",Q,"Q+1<=Y",Q+1<=Y, "d1=",a**(mpf(2)/3)*u**2)
# direct check of the first inequality's RHS at Y=25000 (closed form before u-bounding)
phi=lambda d: a*(Y+d)/mpf(d)**1.5
rhs=1-mpf(2)/Y-(1-mpf(Q+1)/Y)*phi(Q+1)-sum(min(1,phi(q+1)) for q in range(1,Q))/Y
print("direct RHS at Y=25000:",rhs)
print("== hover-tail / band constants (n=50001)")
hv=lambda c: mpf(c)**-0.5*(2/sqrt(pi)*(1+mpf(1)/c)+1/sqrt(pi))
print("hv(5000)=",hv(5000),"<=0.02394", hv(5000)<=0.02394, " *3=",3*hv(5000))
print("sqrt(2/pi)/sqrt(5000)=",sqrt(2/pi)/sqrt(5000))
n=mpf(50001); w2=(2*n/3)**(mpf(2)/3); print("(2n/3)^(2/3)=",w2," n/3=",n/3," 10*w2=",10*w2)
print("0.4n/3-6w2+1 =",mpf('0.4')*n/3-6*w2+1, " (claimed >=453)")
print("0.4n/3 >= 6 w2+1:",mpf('0.4')*n/3, 6*w2+1)
pit=(2*pi)**-0.5*((n+1)/((n/2)*(n/3-1-w2)))**1.5*exp(1/(12*(n+1))); print("pi_n(t0-1) bound=",pit,"<=5.775e-7",pit<=5.775e-7, " *0.15n=",pit*mpf('0.15')*n)
c4=1/(12*(mpf('0.4')*n/3-6*w2+1))+1/(12*mpf(25000))+1/(12*mpf(50002)); print("c4=",c4,"<=0.00019",c4<=0.00019, "e^-c4=",exp(-c4))
wbar=w2+2; y=n/2
print("(1+3y^-2/3)^1.5=",(1+3*y**(-mpf(2)/3))**1.5)
print("(n/3+1)/(n/3-wbar)=",(n/3+1)/(n/3-wbar),"<=1.0665")
print("(1+2wbar/n)^1.5=",(1+2*wbar/n)**1.5,"<=1.0630")
eps0=mpf(1.5)*wbar/(n/2+wbar-1)*(n/3+2*wbar)/(n/3+1-wbar); print("eps0=",eps0,"<=0.0717",eps0<=0.0717)
K=(2*pi)**-0.5*mpf('1.0053')*mpf('1.0665')*mpf('1.0630')*exp(mpf('0.0717')+1/mpf(300006)); print("K=",K,"<=0.4885",K<=0.4885)
print("K*2wbar/n=",mpf('0.4885')*2*wbar/n,"<=0.0203")
A=(1-mpf('0.0719'))*mpf('0.8')*mpf('0.9998')*(2*mpf('0.9843')-mpf('0.0132')); print("A=",A,">=1.4515",A>=1.4515)
print("A-2K+1=",mpf('1.4515')-2*mpf('0.4885')+1," K-0.0203-1-1/n=",mpf('0.4885')-mpf('0.0203')-1-1/n)
print("Psi at 1/2:",mpf('1.4745')/2-mpf('0.5319'))
print("== right part")
y=mpf(33334); r=mpf(10357)
print("10y^(2/3)-1=",10*y**(mpf(2)/3)-1)
print("0.2r-7.3=",mpf('0.2')*r-mpf('7.3'))
print("e^-(1/156+1/(12y)+1/(12*50002))=",exp(-(mpf(1)/156+1/(12*y)+1/(12*mpf(50002)))),">=0.9936")
print("hv coeff at 2064:",2/sqrt(pi)*(1+mpf(1)/2064)+1/sqrt(pi),"<=1.6932")
t=y**(mpf(1)/3); eh=mpf('1.6932')*(t/10+1)/sqrt(2*t*t-mpf('7.5')); print("eps_hov=",eh,"<=0.1573",eh<=0.1573)
print("sqrt(2/pi)/sqrt(2064)=",sqrt(2/pi)/sqrt(2064),"<=0.01757")
print("(2pi)^-.5 (1.50003/0.8998)^1.5=",(2*pi)**-0.5*(mpf('1.50003')/mpf('0.8998'))**1.5, " *e^(1/(12*50002))=",(2*pi)**-0.5*(mpf('1.50003')/mpf('0.8998'))**1.5*exp(1/(12*mpf(50002))))
print("0.3*0.8588=",mpf('0.3')*mpf('0.8588')," 0.25764/sqrt(10358)=",mpf('0.25764')/sqrt(10358))
print("1-0.01757-0.00254=",1-mpf('0.01757')-mpf('0.00254'))
wid=mpf('0.1')*(r+1)+2
print("(r+1)/(r-wid)=",(r+1)/(r-wid),"<=1.1116")
print("(1+3y^-2/3)^1.5=",(1+3*y**(-mpf(2)/3))**1.5,"<=1.0044")
print("1.5wid/(r+1-wid)=",mpf(1.5)*wid/(r+1-wid),"<=0.1671")
print("(1+(y^2/3+2)/y)^1.5=",(1+(y**(mpf(2)/3)+2)/y)**1.5,"<=1.0472")
W=(2*pi)**-0.5*mpf(2)/3*mpf('1.0044')*mpf('1.5')*mpf('1.1116')*mpf('1.0472')*exp(mpf('0.1671')+1/mpf(400008)); print("W bound=",W,"<=0.5513",W<=0.5513)
P=(1-mpf('0.1573'))*mpf('0.8')*mpf('0.9936')*(2*mpf('0.9798')-mpf('0.0232'))-mpf('0.5513'); print("0.8427*0.8*0.9936*1.9364-0.5513=",P,">=0.7457",P>=0.7457)
print("0.7457*2/3=",mpf('0.7457')*2/3, " final:",mpf('0.7457')*2/3-(1-mpf(2)/3)-mpf('2.5e-5'))
print("== 5A tail cells: m(50001)")
def mfrak(n):
    m=170
    for mm in range(171,100000):
        if mpf(mm)**1.5+9*mm<=n: m=mm
        else: break
    return m
print("m(20001)=",mfrak(20001)," m(50001)=",mfrak(50001))
# t0(y) for y=25001 and wid
def t0(y):
    m=y+1
    while not (m-y>=mfrak(m)+1): m+=1
    return m+1
y0=25001; T=t0(y0); print("t0(25001)=",T," wid=",T-1-y0," y^(2/3)+2=",mpf(y0)**(mpf(2)/3)+2)
