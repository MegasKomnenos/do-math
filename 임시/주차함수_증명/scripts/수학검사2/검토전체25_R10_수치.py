# 부록 A·C와 10장에 적힌 수치를 다시 센다.
from mpmath import mp, mpf, sqrt, pi, log, e, exp, zeta, gamma, floor
mp.dps = 30
def ub(k): return mpf('1.15')/mpf('0.35')*(2+mpf(1)/k)*(mpf('0.65')-mpf(1)/k)**(-mpf(3)/2)/sqrt(k)
def ddl(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k)) + mpf('37.6')/(5*sqrt(pi)*k)
def v(k): return 2 - mpf('4.6')/sqrt(k+1) - 2*ub(k) - ddl(k)/2
print('v(6667)=', v(6667), ' v(2001)=', v(2001), 'v(3131)=', v(3131))
print('v increasing 2001..20000:', all(v(k+1) > v(k) for k in range(2001, 20000)))
print('DDL nat decreasing k>=7:', all(ddl(k+1) < ddl(k) for k in range(7, 20000)), 'ddl(6)<ddl(7)?', ddl(6) < ddl(7))
cpsi = -zeta(mpf(1)/2) + zeta(mpf(3)/2)/12
print('c_Psi=', cpsi, 'z1/2', zeta(mpf(1)/2), 'z-1/2', zeta(-mpf(1)/2), 'z3/2', zeta(mpf(3)/2))
print('f1=4/(3 sqrt(2pi))=', 4/(3*sqrt(2*pi)))
print('s_B=e/sqrt(2pi)=', e/sqrt(2*pi), ' n_inf=2/sqrt(pi)=', 2/sqrt(pi))
print('theta0=', (2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')))
print('a0=', gamma(mpf(1)/3)*3**(-mpf(2)/3), 'a1=', gamma(mpf(2)/3)*3**(-mpf(1)/3))
print('(10+7sqrt7)/54=', (10+7*sqrt(7))/54)
print('140^2+280=', 140**2+2*140, '141:', 141**2+2*141)
# 꼬리 칸 수 m(n) 확인용: 170^1.5+9*170, 171
print('171^1.5+9*171=', mpf(171)**1.5+9*171)
# x_k=(k/(k+1))^(k-1) -> 1/e
print('x_2000=', (mpf(2000)/2001)**1999, '1/e', 1/e)
# 3k<=19998 for k<=6666; 3*6667-1
print(3*6666, 3*6667-1, 2*6667+103)
