import math
# head-sum-1 numeric checks
u1=3132**(-1/3); l0=3131
print("u1",u1, "3132^(2/3)",3132**(2/3),"(k-1)/6",3131/6)
print("q/l max",3132**(2/3)/3131)
c1max=(1+3132**(2/3)/3131)**1.5*math.exp(1/(12*3131)); print("c1max",c1max)
print("4/3/sqrt(2pi)",4/3/math.sqrt(2*math.pi), "0.5320*1.105",0.5320*1.105)
print("consts",2/math.sqrt(2*math.pi)/7,2/math.sqrt(2*math.pi)/5,2/math.sqrt(2*math.pi)*3.2/3)
print("0.8848/sqrt2",0.8848/math.sqrt(2))
# step4
xi=0.03; ql=xi*u1*(1+1/l0); print("q/l at .03",ql, "c1",(1+ql)**1.5*math.exp(1/(12*l0)))
uq=(1+1/l0)**2*(xi*u1+u1**3)**2/2; print("uq",uq)
br=0.11399*0.03+0.15958*u1**2+0.85108*math.sqrt(0.03)*u1; print("bracket",br, 1.0004*1.0035*1.0001*br)
c1=1.0035; num=c1*1.0004*(0.5320*xi*u1+0.7979*u1**3+c1*(0.625*xi**1.5+math.sqrt(xi)*u1**2)); print("E<=",num/0.1721)
print("L den",1+(0.03*u1+u1**3)*1.0004, "L coef",0.1721*math.exp(-0.0317)/1.0024)
# step5 thresholds
for p in [3.5,2.5,3,1.5,2,1]:
    print("p",p,(1.11*p*u1/(p-0.5))**2)
# c2
def c2val(xi): return 0.7979*math.sqrt(xi)*u1**3/(0.7978*math.sqrt(xi)-0.8848*u1)
print("c2 at .03",c2val(0.03), "at 1",c2val(1))
# step6
print("1+1/l0",1+1/l0, "u1(1+1/l0)",u1*(1+1/l0))
c1=(1.06838)**1.5*math.exp(1/(12*3131)); print("c1 end",c1)
uq=1.00032**2*(0.06835+0.06835**3)**2/2; print("uq end",uq, math.exp(0.00237))
br=0.11399+0.15958*0.06835**2+0.85108*0.06835; print("br end",br)
print("Phi end",1.00032*1.10434*1.00238*0.17292)
print("Eden",0.7978-0.8848*0.06835,"Enum",0.5320*0.06835+1.10434*(0.625+0.06835**2))
print("Ebar",1.10434*1.00032*(0.73174/0.73732+0.000568))
print("Lden",1+(0.06835+0.06835**3)*1.00032, "Lbar",0.73732*math.exp(-1.0970)/1.0687, "R",0.19148/0.2303)
# H-star-plus regions, float grid
def funcs(xi,u):
    il=1/(1-u**3)  # 1+1/l
    c1=(1+xi*u*il)**1.5*math.exp(il*u**3/12)
    uq=il**2*(xi*u+u**3)**2/2
    Phi=il*c1*math.exp(uq)*(0.11399*xi**3.5+0.15958*xi**2.5*u**2+0.85108*xi**3*u)
    den=0.7978*math.sqrt(xi)-0.8848*u
    E=c1*il*(0.5320*xi**1.5*u+0.7979*math.sqrt(xi)*u**3+c1*(0.625*xi**2+xi*u**2))/den
    L=den*math.exp(-E)/(1+(xi*u+u**3)*il)
    G=Phi+u*(0.5320*c1*xi**1.5+0.2)
    return Phi,L,G
u2=19404**(-1/3)
mA=max(funcs(2*u1**2+(0.75-2*u1**2)*i/20000,u1)[2]/funcs(2*u1**2+(0.75-2*u1**2)*i/20000,u1)[1] for i in range(20001))
mB=max(funcs(0.75+0.25*i/4000,u2)[2]/funcs(0.75+0.25*i/4000,u2)[1] for i in range(4001))
print("A max",mA,"B max",mB)
mC=max(funcs(2*u*u,u)[2]/funcs(2*u*u,u)[1] for u in [u1*i/2000 for i in range(1,2001)])
print("C max",mC, "limit",0.2/(0.7978*math.sqrt(2)-0.8848))
# Phi<=L check head-sum-1 on grid incl xi in [2u^2,1], u<=u1
worst=max(funcs(xi,u)[0]/funcs(xi,u)[1] for u in [u1*i/200 for i in range(1,201)] for xi in [2*u*u+(1-2*u*u)*j/2000 for j in range(2001)])
print("Phi/L max",worst)
# Rbar(1)
print("R(1,u1) Phi/L", funcs(1,u1)[0]/funcs(1,u1)[1])
# head-sum-2 numbers
print(597**1.5+9*597, 598**1.5+9*598, 19404**(2/3), 20001**(2/3)-6*20001**(1/3))
print("phi(7/16)",1-1.5*7/16+0.5*(7/16)**2-(9/16)**1.5)
print("0.75*3132^(2/3)",0.75*3132**(2/3))
# t=k+1
print(0.6*math.exp(-1))
