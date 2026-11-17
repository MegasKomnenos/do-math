# 검토전체22 R7b: 7.6-7.8절 상수 재계산
from mpmath import mp, mpf, sqrt, pi, e, log, exp, factorial, binomial
mp.dps = 40
print('sqrt(2/pi)/sqrt(301)=', sqrt(2/pi)/sqrt(301), ' 1-..=', 1-sqrt(2/pi)/sqrt(301))
print('2(2pi)^-1/2 (301.5)^-1/2 =', 2/sqrt(2*pi)/sqrt(mpf(301.5)))
print('(2pi)^-1/2=', 1/sqrt(2*pi))
print('0.9538/0.398943=', mpf('0.9538')/mpf('0.398943'))
n=904
sg = n*log(mpf(n)/(n+1))+1
print('sg_904=', sg, ' bound=', mpf(1)/(2*(n+1))+mpf(1)/(6*n*(n+1)), ' e^-0.0006=', exp(-mpf('0.0006')))
print('2.38*0.9994*4/9/2=', mpf('2.38')*mpf('0.9994')*4/9/2)
print('0.528*sqrt(301)-151/301-1=', mpf('0.528')*sqrt(301)-mpf(151)/301-1)
# true Borel sum
def Bor(m): return exp(-mpf(m))*mpf(m)**(m-1)/factorial(m)
print('sum_{d<=301}Bor(d)=', sum(Bor(d) for d in range(1,302)))
# v(6667), v(2001)
def ub(k): return mpf('1.15')/mpf('0.35')*(2+mpf(1)/k)*(mpf('0.65')-mpf(1)/k)**(-mpf(3)/2)*mpf(k)**(-mpf(1)/2)
def DDL(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k))+mpf('37.6')/(5*sqrt(pi)*k)
def v(k): return 2-mpf('4.6')/sqrt(k+1)-2*ub(k)-DDL(k)/2
for k in (2001,6667): print('v(%d)='%k, v(k), ' 2v-e=', 2*v(k)-e)
print('3.098-2.7183=', mpf('3.098')-mpf('2.7183'), ' e=', e)
# explicit-bounds numeric check
def P(m,j): return j*binomial(m-1,j-1)*mpf(j)**(j-2 if j>=2 else 0)*(mpf(m-j+1)**(m-j-1))/mpf(m+1)**(m-1) if j>=2 else binomial(m-1,0)*mpf(m)**(m-2)/mpf(m+1)**(m-1)
def Pm(m,j):
    pj1 = mpf(j)**(j-2) if j>=2 else mpf(1)
    pmj = mpf(m-j+1)**(m-j-1) if m-j>=1 else mpf(1)
    return j*binomial(m-1,j-1)*pj1*pmj/mpf(m+1)**(m-1)
def Ren(j): return mpf(j)**j*exp(-mpf(j))/factorial(j)
bad=0; worst1=0; worst2=0
for m in (1,2,3,5,10,37,100,400):
    sgm = m*log(mpf(m)/(m+1))+1
    assert 0 <= sgm <= mpf(1)/(2*(m+1))+mpf(1)/(6*m*(m+1))
    for j in range(1,m+1):
        U=m-j
        r1 = Pm(m,m-U)/(Bor(U+1)*exp(sgm)*(m+1)/mpf(m-U))
        r2 = Pm(m,j)/(Ren(j)*exp(sgm)*(m+1)/mpf(m+1-j)**2)
        worst1=max(worst1,r1); worst2=max(worst2,r2)
        if r1>1 or r2>1: bad+=1
        if Pm(m,m-U) < Bor(U+1): bad+=1; print('2.32 lower fail',m,U)
print('explicit-bounds violations:', bad, ' max ratios', worst1, worst2)
# apex bracket check at k=301, n=904 using exact P, rw: sum_{U<=300}(rw-1)
k=301
for n in (3*k+1, 4*k, 10*k, 100*k):
    nu=n-2*k
    S = sum(mpf(k)/(n-U)*Pm(n,n-U)/Pm(n,k)-1 for U in range(0,301))
    lb = mpf('2.38')*mpf(k)**1.5*(n+1-k)**2/(exp(n*log(mpf(n)/(n+1))+1)*n*(n+1))-301
    print('k=301 n=%d: true sum(rw-1)=%s  text lower=%s  bracket true/(2k)-1=%s' % (n, mp.nstr(S,8), mp.nstr(lb,8), mp.nstr(S/(2*k)-1,6)))
