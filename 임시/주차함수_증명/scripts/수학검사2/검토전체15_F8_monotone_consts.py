# F8: 8.2절 pieces-k-monotone / escape-y-monotone 증명의 수치 상수 재계산
import math
c=(2*math.pi)**-0.5
k=6600.0; xi=0.2
eps=k**(-1/3); kap=k**(2/3); q=xi*kap; p=q-1; mu=1/q
print("eps(1+xi eps) max:", eps*(1+0.319921), "< 0.0704 ?")
print("R2 second:", (1+1/(4*p))/(1-mu), "<=1.018072")
print("R2 third:", 3.5*k/(k+1), ">=3.49946")
print("R2 sum:", 2.5+1.018072-3.49946-2/3)
cpsi_max=1.46036+2.61238/12
print("c_Psi max:", cpsi_max, "1-c/(2 sqrt p):", 1-cpsi_max/(2*math.sqrt(69.3708)), ">0.89926")
print("D3 total:", 0.319921/3+1/(3*0.985789*0.89926)-2/3, "< -0.184")
print("(na) D1-D3 min:", 0.2-k**(-2/3)-3*c*math.sqrt(0.2)*eps, ">=0.168623")
first=(1.5*math.sqrt(xi)-0.5*xi**-0.5*k**(-2/3))/(2*c)
second=0.75*eps*(1+(1-mu)**-0.5)
third=(k+1)/(2*k)*(1-mu)**-1.5/(xi**2*kap)
print("(ra) first,second,third:", first, second, third, "sum", first-second-third, ">0.7202096")
a=(1+xi*eps)/(12*xi**2*k**(1/3)); b=3/(8*math.sqrt(xi)*k**(1/3))
print("(ma) terms:", a, b, a+b, "<0.156953")
print("Lambda'(1):", 2.75-1.46036)
print("bracket p=1:", -1/6+2/3*1.46035-0.20789)
print("k>=422 check: 9(k+2)-5(k+6k^{2/3}+1) at 422,421,417,416:", [9*(kk+2)-5*(kk+6*kk**(2/3)+1) for kk in (422,421,417,416)])
print("5+sqrt5 /2:", (5+5**0.5)/2)
print("(2pi)^-1/3:", (2*math.pi)**(-1/3))
print("2/6600^(2/3):", 2/kap)
