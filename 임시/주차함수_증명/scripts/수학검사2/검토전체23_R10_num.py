# -*- coding: utf-8 -*-
# 부록 A·C의 뜻 열에 적힌 수치의 재계산
from math import *
def ub(k): return 1.15/0.35*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def ddl(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k))+37.6/(5*sqrt(pi)*k)
def v(k): return 2-4.6/sqrt(k+1)-2*ub(k)-0.5*ddl(k)
print('v(6667)=', v(6667), ' v(2001)=', v(2001), 'v increasing check', all(v(k+1) > v(k) for k in range(2001, 30000)))
print('ub(2001)=', ub(2001), 'u(2001)=', u(2001), 'u(10001)=', u(10001))
print('u(2001)/(e 2^1.5)=', u(2001)/(e*2**1.5), 'u(10001)/(e 2^1.5)=', u(10001)/(e*2**1.5))
print('ddl decreasing from 7:', all(ddl(k+1) < ddl(k) for k in range(7, 100000)), 'ddl(6)<ddl(7)?', ddl(6) < ddl(7), ddl(5), ddl(6), ddl(7), ddl(8))
print('f1=', 4/(3*sqrt(2*pi)))
print('theta0=', (2*exp(-0.48)-1)*exp(-0.48))
print('c_Psi range', 1.46035+2.61237/12, 1.46036+2.61238/12)
print('n_inf=', 2/sqrt(pi), 'sB=', e/sqrt(2*pi))
from math import gamma
print('a0=', 3**(-2/3)*gamma(1/3), 'a1=', 3**(-1/3)*gamma(2/3))
print('Gamma(1/3)Gamma(5/6)=', gamma(1/3)*gamma(5/6), ' 2^(1/3) sqrt(pi) Gamma(2/3)=', 2**(1/3)*sqrt(pi)*gamma(2/3))
print('140^2+280=', 140*140+280, ' 3*6666=', 3*6666)
print('(10+7 sqrt7)/54=', (10+7*sqrt(7))/54)
print('1.84*2/sqrt(pi)=', 1.84*2/sqrt(pi))
