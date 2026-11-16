from mpmath import mp, mpf, sqrt, exp, log, quad, pi, e, zeta, ceil, floor
mp.dps = 30
out=[]
def P(*a): out.append(" ".join(str(x) for x in a))
# head-sum-1 constants
k=mpf(3132); l=k-1; u1=k**(-mpf(1)/3)
P("u1=",u1, "<0.06835?", u1<0.06835)
P("k^(2/3)/(k-1)=", k**(mpf(2)/3)/(k-1), "<=0.0684?", k**(mpf(2)/3)/(k-1)<=0.0684)
P("6k^(2/3)<=k-1?", 6*k**(mpf(2)/3)<=k-1)
c1max=(1+k**(mpf(2)/3)/l)**mpf(1.5)*exp(1/(12*l)); P("c1max=",c1max,"<=1.105?",c1max<=1.105)
P("4/3*(2pi)^-1/2=", mpf(4)/3/sqrt(2*pi), " 2(2pi)^-1/2=",2/sqrt(2*pi))
P("consts 7,5,3.2/3:", 2/sqrt(2*pi)/7, 2/sqrt(2*pi)/5, 2/sqrt(2*pi)*mpf('3.2')/3)
P("0.8848/sqrt2=",mpf('0.8848')/sqrt(2), " 0.7978-0.6257=",mpf('0.7978')-mpf('0.6257'))
# step4
xi=mpf('0.03'); ql=xi*u1*(1+1/l); P("q/l step4=",ql, " c1=",(1+ql)**mpf(1.5)*exp(1/(12*l)), " uq=",((ql+1/l)**2)/2)
br=mpf('0.11399')*xi+mpf('0.15958')*u1**2+mpf('0.85108')*sqrt(xi)*u1
P("Phi coef step4:", mpf('1.0004')*mpf('1.0035')*mpf('1.0001')*br)
c1=mpf('1.0035')
En=c1*(1+1/l)*(mpf('0.5320')*xi*u1+mpf('0.7979')*u1**3+c1*(mpf('0.625')*xi**mpf(1.5)+sqrt(xi)*u1**2))/mpf('0.1721')
P("E step4 <=",En, " L denom", 1+(xi*u1+u1**3)*(1+1/l), " L>=", mpf('0.1721')*exp(-mpf('0.0317'))/mpf('1.0024'))
P("L/Phi at xi=0.03:", mpf('0.1662')/(mpf('0.01434')*mpf('0.03')**2))
# step5 thresholds
P("b/a=",mpf('0.8848')/mpf('0.7978'))
for p in [mpf(7)/2,mpf(5)/2,3,mpf(3)/2,2,1]:
    P(" p=",p," xi thr=",(mpf('1.11')*p*u1/(p-mpf(0.5)))**2)
c2=mpf('0.7979')*sqrt(xi)*u1**3/(mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u1); P("c2 actual=",c2,"<=5.68e-4?",c2<=mpf('5.68e-4'))
P("0.7978*sqrt(0.03)=",mpf('0.7978')*sqrt(xi), " 0.8848*u1=",mpf('0.8848')*u1)
# step6 with upper bounds as in text
l0=mpf(3131); U1=mpf('0.06835'); r=1+1/l0
P("1+1/l0=",r,"<1.00032?",r<mpf('1.00032'))
ql=U1*r; P("q/l=",ql); c1=(1+ql)**mpf(1.5)*exp(1/(12*l0)); P("c1=",c1,"<1.10434?",c1<mpf('1.10434'))
uq=r**2*(U1+U1**3)**2/2; P("uq=",uq,"<0.00237?",uq<mpf('0.00237'), " e^uq=",exp(mpf('0.00237')))
br=mpf('0.11399')+mpf('0.15958')*U1**2+mpf('0.85108')*U1; P("bracket=",br,"<0.17292?",br<mpf('0.17292'))
Phi=mpf('1.00032')*mpf('1.10434')*mpf('1.00238')*mpf('0.17292'); P("Phi<",Phi,"<0.19148?",Phi<mpf('0.19148'))
den=mpf('0.7978')-mpf('0.8848')*U1; P("Ebar denom=",den)
num=mpf('0.5320')*U1+mpf('1.10434')*(mpf('0.625')+U1**2); P("Ebar num=",num,"<0.73174?",num<mpf('0.73174'))
Eb=mpf('1.10434')*mpf('1.00032')*(mpf('0.73174')/mpf('0.73732')+mpf('0.000568')); P("Ebar<",Eb,"<1.0970?",Eb<mpf('1.0970'))
Ld=1+(U1+U1**3)*r; P("Lbar denom=",Ld,"<1.0687?",Ld<mpf('1.0687'))
Lb=mpf('0.73732')*exp(-mpf('1.0970'))/mpf('1.0687'); P("Lbar>",Lb,">0.2303?",Lb>mpf('0.2303'))
P("Rbar(1)<",mpf('0.19148')/mpf('0.2303'))
# psi-two-sided
P("(2pi)^-1/2*(2*sqrt(d+1)-2-z32/12): coef",2/sqrt(2*pi)," const",(2+mpf('2.61238')/12)/sqrt(2*pi))
# psi-low
P("1.46036+2.61238/12=",mpf('1.46036')+mpf('2.61238')/12, " (2pi)^-1/2-0.3989=",1/sqrt(2*pi)-mpf('0.3989'), " *2=",2*(1/sqrt(2*pi)-mpf('0.3989')), " const diff=",1.67806/sqrt(2*pi)-mpf('0.3989')*mpf('1.678'))
P("Psi(1)=e^-1=",exp(-1)," 0.3989*0.322=",mpf('0.3989')*mpf('0.322'))
# old-7-39
P("(2pi)^-1/2 e^-1/12=",exp(-mpf(1)/12)/sqrt(2*pi), " 2(2pi)^-1/2=",2/sqrt(2*pi))
# theorem A+ constants
P("e^-1/12 - e^1/4/4=",exp(-mpf(1)/12)-exp(mpf(1)/4)/4, " sqrt(2/pi)*0.599=",sqrt(2/pi)*mpf('0.599'), " 1.5/0.477=",mpf(1.5)/mpf('0.477'))
# head-sum-2
for m in [597,598]: P("m=",m, m**mpf(1.5)+9*m)
n=mpf(20001); P("m0 at 20001:", n**(mpf(2)/3)-6*n**(mpf(1)/3))
P("19404^(2/3)=",mpf(19404)**(mpf(2)/3), " 7.4^3=",7.4**3, " 39*3/16=",39*3/16)
k=mpf(3132); P("k^(1/3) at 3132 k^2/3=",k**(mpf(2)/3))
# centroid 0.0196
P("sqrt(8/(pi*6669))=",sqrt(8/(pi*6669)))
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L9_상수검산_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
