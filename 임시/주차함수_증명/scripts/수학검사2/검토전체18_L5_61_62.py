from mpmath import mp, mpf, e, sqrt, pi, exp, log, ceil, factorial
mp.dps=30
# 6.1
print("12000^(2/3)=", mpf(12000)**(mpf(2)/3), "ceil", ceil(mpf(12000)**(mpf(2)/3)))
print("1-1.6/sqrt525=", 1-mpf('1.6')/sqrt(525))
b=mpf('0.8')*sqrt(2)/3*(1+mpf(1)/1048); c=mpf('3.923')*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3); d=mpf('1.5')/(3*sqrt(525))
print("bracket terms", b,c,d, "sum", b+c+d, "x2", 2*(b+c+d))
print("1.2(1-2/525)^-2.5=",mpf('1.2')*(1-mpf(2)/525)**(-mpf(5)/2))
print("1.2(1+2/525)^.5=",mpf('1.2')*(1+mpf(2)/525)**(mpf(1)/2))
print("1.5(1-1/525)^-2.5=",mpf('1.5')*(1-mpf(1)/525)**(-mpf(5)/2))
print("2/sqrt(2pi)=",2/sqrt(2*pi))
# 6.2
def B2(k):
    k=mpf(k); return (1-1/e)+(exp(mpf(3)/2+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)=",B2(43),"B2(2000)=",B2(2000), "1-B2(2000)=",1-B2(2000))
def Bor(n): n=mpf(n); return exp(-n)*n**(n-1)/factorial(n)
def S(k):
    x=(mpf(k)/(k+1))**(k-1); q=e*x
    return sum(Bor(n)*q**n for n in range(2,k+2))
print("S(2)=",S(2),"8/9=",mpf(8)/9)
print("max S k=2..42:", max((S(k),k) for k in range(2,43)))
print("S(43)=",S(43),"S(2000)=",S(2000))
print("k rho^L(3k) k=2000:", mpf(3)/4*(1-mpf('1.2')/2000), "k rho^H(3k)<=", mpf('0.307')*2000/3999)
# (1-3/(2k))*0.307 k/(2k-1) - 47/(24k) at k=2000
k=mpf(2000); print("krhoH(3k) exact k=2000:", (1-3/(2*k))*mpf('0.307')*k/(2*k-1)-mpf(47)/(24*k))
