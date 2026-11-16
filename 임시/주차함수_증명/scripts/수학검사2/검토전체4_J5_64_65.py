import math
c=(2*math.pi)**-0.5
# 6.4
u=lambda k:3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("u(3131)=",u(3131),"u/2=",u(3131)/2)
print("9*1.5^1.5=",9*1.5**1.5,"*4/3=",9*1.5**1.5*4/3)
print("(10+7sqrt7)/54=",(10+7*math.sqrt(7))/54,"X*=",(5-math.sqrt(7))/6)
# 6.5 constants
x=3132/3130; G=x/((1+x)**0.45-1); print("Gamma_tp(x)=",G)
kap=2.4978; tp=0.55
chi=((kap*tp+2)+math.sqrt((kap*tp+2)**2-4*tp*kap))/(2*tp)
print("big root=",chi,"c*=",(chi*chi-kap*chi)*math.exp(-tp*chi))
print("kappa_d lower=",1.498+2*3130/6261, "ex_max=",3131/6261, "2-exmax-20/(9t)=",2-3131/6261-20/(9*3130))
JI,YI,JX,YX=8.133,10.301,17.951,23.462
A=3*c*(JI+c*YI); B=1.5*2.7323*0.8051*c*(JX+c*YX)
print("A=",A,"B=",B,"sum=",A+B, "50.62/sqrt3130=",50.62/math.sqrt(3130))
# v(k)
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/math.sqrt(k-1)
for k in [3131,3998,3999,6667,10000]:
    vp=max(k+1,4000); io=2*k+1-vp
    print(k, v(k), 2*min(1,3*vp*io**-1.5), 2*u(k), 50.62/math.sqrt(k-1))
print("12.15 check:",4.5*2+4.5*2/3+0.375*2/5, 4.5*2/3+4.5*2/5+0.375*2/7, 3*2+1.875*2/3, 3*2/3+1.875*2/5)
