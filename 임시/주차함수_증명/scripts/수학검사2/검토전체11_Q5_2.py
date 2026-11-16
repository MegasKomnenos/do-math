# Q5 검산 2: 6.4 뒷부분–6.6의 수치
from mpmath import mp, mpf, exp, log, sqrt, pi, e, factorial, quad, findroot, floor, ceil
mp.dps=30
def Bor(n): n=mpf(n); return exp(-n)*n**(n-1)/factorial(n)
def Ren(n): return n*Bor(n)
def Psi(q): return sum(Ren(j) for j in range(1,q+1))
c=1/sqrt(2*pi)
def u(k): k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(1.5))*k**(-mpf(0.5))
print("u(3131)=",u(3131)," u(3131)/2=",u(3131)/2)
# 6.5 theorem-U constants
tp=mpf('0.55'); kap=mpf('2.4978')
root=(kap*tp+2+sqrt((kap*tp+2)**2-4*tp*kap))/(2*tp)
print("m(0.55,2.4978): root=",root," value=",(root**2-kap*root)*exp(-tp*root))
x=mpf(3132)/3130; print("Gamma_tp=",x/((1+x)**(1-tp)-1))
print("50.62/sqrt(3130)=",mpf('50.62')/sqrt(3130))
J_I,Y_I,J_X,Y_X=mpf('8.133'),mpf('10.301'),mpf('17.951'),mpf('23.462')
Gs,ms=mpf('2.7323'),mpf('0.8051')
print("3c(J+cY)=",3*c*(J_I+c*Y_I)," 1.5 G m c(J+cY)=",mpf(1.5)*Gs*ms*c*(J_X+c*Y_X))
print("ex_max=",mpf(3131)/6261, " 2-exmax-20/(9t)=",2-mpf(3131)/6261-mpf(20)/(9*3130), " kappa_d min=",mpf('1.498')+2*mpf(3130)/6261)
# V-core
def vfun(k):
    k=mpf(k); vp=max(k+1,mpf(4000)); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**(-mpf(1.5)))-2*u(k)-mpf('50.62')/sqrt(k-1), 2*min(1,3*vp*io**(-mpf(1.5))), 2*u(k), mpf('50.62')/sqrt(k-1)
for k in (3131,6667,10000): print("v(",k,")=",vfun(k))
print("12000*3997^-1.5 vs 12000*3999^-1.5:",12000*mpf(3997)**-1.5,12000*mpf(3999)**-1.5)
# 6.6
print("Psi(14)=",Psi(14)," /2e=",Psi(14)/(2*e))
k=mpf(3131)
f1=sqrt(2*pi)*mpf(3146)**1.5*Bor(3146); print("first factor 3146:",f1, " product:",f1*(k/(k+15))**1.5*(k+1)/(k+14))
ups=lambda k: mpf(0.5)+mpf(5)/(2*k)+1/(4*k*k)
gW=2*exp(mpf('0.0031'))/e; print("gamma_W=",gW, " ups*gW(3131)=",ups(k)*gW)
print("Fr/ (sB k^-1.5) at 3131 minus loss:", f1*(k/(k+15))**1.5*(k+1)/(k+14)*Psi(14)/(2*e) - ups(k)*gW)
# max of (1-D)(1+(e-2)D)/(2-D)
g=lambda D:(1-D)*(1+(e-2)*D)/(2-D)
print("max (1-D)(1+0.7183D)/(2-D):", max(g(mpf(i)/10000) for i in range(0,10001)))
print("(e+0.75)/3131=",(e+mpf(0.75))/3131, " 0.5006*k*(3.469/k)^2=",mpf('0.5006')*3131*(mpf('3.469')/3131)**2)
print("2k/(k-2),k/(k-1):",2*k/(k-2),k/(k-1)," (1+2/3129)(1+2/3130)=",(1+mpf(2)/3129)*(1+mpf(2)/3130))
# d(k)
def dfun(k): k=mpf(k); return gW*ups(k)+u(k)/(e*2**mpf(1.5)), gW*ups(k), u(k)/(e*2**mpf(1.5))
print("d(3131)=",dfun(3131)," d(10001)=",dfun(10001))
# Low
def Low(k,rho):
    k=mpf(k); rho=mpf(rho); eps=k**(-mpf(1)/3)
    br=2*sqrt(rho)-mpf('2.218')*eps
    return c*k**(mpf(1)/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/(c*br))
print("Low(10001,1.4)=",Low(10001,'1.4')," Low(3131,0.75)=",Low(3131,'0.75'))
k=mpf(10001); print("Obar far:",dfun(k)[0]*exp(1+1/(12*k))*(1+mpf('1.4')*k**(-mpf(1)/3)+1/k)**1.5)
k=mpf(3131); print("Obar small:",dfun(k)[0]*exp(1+1/(12*k))*(1+mpf('0.75')*k**(-mpf(1)/3)+1/k)**1.5)
# 6.49
k=mpf(3131); uu=k**(mpf(1)/3); print("u=",uu)
wp=lambda m: mpf('1.99')+mpf('0.59963')*(m+1)**(mpf(2)/3)+mpf('1.24847')*(m+1)**(mpf(1)/3)
print("quad at u:",mpf('0.15037')*uu**2-mpf('1.54829')*uu-mpf('1.3314'), " direct diff:",mpf('0.75')*k**(mpf(2)/3)-(wp(k+mpf('0.75')*k**(mpf(2)/3))-1))
print("root:",(mpf('1.54829')+sqrt(mpf('1.54829')**2+4*mpf('0.15037')*mpf('1.3314')))/(2*mpf('0.15037')))
print("wp'(1)=",mpf(2)/3*mpf('0.59963')*2**(-mpf(1)/3)+mpf(1)/3*mpf('1.24847')*2**(-mpf(2)/3))
print("10*10001^(2/3)=",10*mpf(10001)**(mpf(2)/3), " 1.4*10001^(2/3)=",mpf('1.4')*mpf(10001)**(mpf(2)/3))
# (6.50) at k=3131
k=3131
for d in range(1,14):
    m=k+d
    Lh=(k-1)*(e*Ren(d+1)-mpf(60)*(d+1)/m)
    Rh=2*(1+sum(e*Ren(r+1)+mpf(60)*(r+1)/m for r in range(1,d)))
    print(d, mp.nstr(Lh,7), mp.nstr(Rh,5))
# lemma-M R(1/2)
B=mpf('2.218')*mpf(3131)**(-mpf(1)/3); print("B=",B," R(1/2)=",3/mpf(4)-2*B*mpf(0.5)**1.5-2*c*sqrt(mpf(0.5))+c*B, 0.18581-0.30817*B)
# theorem-D numbers
m=mpf(701); d=floor(m**(mpf(2)/3)/2); print("d(701)=",d, d/m, " k=",(m/2**1.5)/(m-m**(mpf(2)/3)/2))
print("es bound:",mpf('0.798')*mpf('0.3747'), " N:",exp(-1/(12*mpf(661))), " bracket:",mpf('0.99987')*(1-0.5-mpf('0.2991'))-mpf('0.7979')*0.5*mpf('0.3747'))
print("rhs lower:",mpf('0.7979')*0.5/sqrt(2)/(12*mpf('0.9437')), " at 701:",mpf('0.025')*mpf(701)**(-mpf(2)/3))
print("upper rhs coeffs:",mpf('0.09')*1.5*mpf('0.7979')+(1+mpf('0.09')/701)*mpf('1.74')*mpf('0.7979'), (1+mpf('0.09')/701)*mpf('3.28')*1.5/2)
print("1.4963*0.7071/0.9437=",mpf('1.4963')/sqrt(2)/mpf('0.9437')," 2.4604*0.5/0.9437=",mpf('2.4604')*0.5/mpf('0.9437'), " at 701:",mpf('1.1212')*701**(-mpf(2)/3)+mpf('1.3036')*701**(-mpf(1)/3))
print("(4/3)^1.5=",(mpf(4)/3)**1.5, " chord slope (1+M)^1.5 on [0,1/3]:",((mpf(4)/3)**1.5-1)*3)
# old-8-12 / old-8-11 extra
print("0.0648*e*2^1.5=",mpf('0.0648')*e*2**mpf(1.5), " 0.3951/(e 2^1.5)=",mpf('0.3951')/(e*2**mpf(1.5)))
print("e Ren(14)-60*14/3144:",e*Ren(14)-mpf(60)*14/3144)
