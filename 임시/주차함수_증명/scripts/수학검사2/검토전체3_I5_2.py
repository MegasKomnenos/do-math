# I5 검산 2: 6.5 상수 (c*, Gamma*, u(k), v(k)) 와 정리 theorem-U 의 적분 J, Y 의 단순 수치 적분(위합이 아닌 참값 근사; 진술의 상계가 참값 이상인지 보는 건전성 검사)
from math import sqrt, exp, log, pi, e
c = 1/sqrt(2*pi)
# c* = sup_{chi>=k}(chi^2 - k chi) e^{-tp chi}, tp=0.55, k=2.4978
tp=0.55; ka=2.4978
a=tp; b=-(ka*tp+2); cc=ka
root=(-b+sqrt(b*b-4*a*cc))/(2*a)
print("larger root",root,"c*",(root**2-ka*root)*exp(-tp*root))
x=3132/3130; G=x/((1+x)**(1-tp)-1); print("Gamma*",G)
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
for k in (3131,6667,10000):
    vp=max(k+1,4000); io=2*k+1-vp
    t1=2*min(1,3*vp*io**-1.5); t2=2*u(k); t3=50.62/sqrt(k-1)
    print(k,"u=",u(k),"2min=",t1,"2u=",t2,"curv=",t3,"v=",2-t1-t2-t3)
print("14.653 check:",3*c*(8.133+c*10.301)," 35.952 check:",1.5*G*0.8051*c*(17.951+c*23.462))
# ---- J, Y numeric (plain midpoint integration, fine grid) ----
def FI(L): return exp(1.5*L)*L*(1+0.75*L)
def FX(L): return exp(1.5*L)*L
def Ical(F,T,n=400):
    # T^{-1/2} int_0^T s^{-3/2} F(-log(1-s)) ds ; substitution s=T*w^2 to tame s^{-1/2} singularity: ds=2Tw dw, s^{-3/2}=T^{-3/2}w^{-3}
    # integrand -> T^{-1/2} * T^{-3/2} w^{-3} F(-log(1-T w^2)) * 2 T w = 2 T^{-1} w^{-2} F(...)
    h=1.0/n; s=0.0
    for i in range(n):
        w=(i+0.5)*h
        s+=2/T*F(-log(1-T*w*w))/(w*w)
    return s*h
V0=1/3130
def J_and_Y(F,Gam,E,Ep,n=3000):
    hi=1+2*V0; h=hi/n; J=0; Y=0
    for i in range(n):
        U=(i+0.5)*h; V=min(U,V0)
        In=sqrt(U+V)*Ical(F,(U+V)/(1+U))/(1+U-V)
        om=1-c+4*c*sqrt(Gam*(Gam+U))/U
        P=Gam*(Gam+U)*E/(U*U*sqrt(1+U-V)); Gf=sqrt(1+U)*Ep
        N=min(P/sqrt(3130),sqrt(P*Gf))
        J+=In*om; Y+=In*N
    return J*h, Y*h
JI,YI=J_and_Y(FI,1.0,12.15,4.908); print("J_I(1)~",JI,"(<=8.133?)  Y_I(1)~",YI,"(<=10.301?)")
JX,YX=J_and_Y(FX,G,7.25,2.75); print("J_X(G*)~",JX,"(<=17.951?)  Y_X(G*)~",YX,"(<=23.462?)")
