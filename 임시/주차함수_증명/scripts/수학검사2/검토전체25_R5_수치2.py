# 검토전체25 R5: 6.6절 수치 재계산
from decimal import Decimal as D, getcontext
getcontext().prec = 40
pi = D('3.14159265358979323846264338327950288419716939937510')
def sqrt(x): return D(x).sqrt()
def ln(x): return D(x).ln()
def exp(x): return D(x).exp()
def pw(x, a): return exp(D(a) * ln(D(x)))
c0 = 1 / sqrt(2 * pi)
def uu(k):
    k = D(k)
    return D(3) / D('0.35') * (D('1.35') + 1 / k) * pw(D('0.65') - 1 / k, D(-3) / 2) / sqrt(k)
def ub(k):
    k = D(k)
    return D('1.15') / D('0.35') * (2 + 1 / k) * pw(D('0.65') - 1 / k, D(-3) / 2) / sqrt(k)
def dd(k):
    return exp(D(-1)) + uu(k) / (exp(D(1)) * pw(2, D('1.5')))
def Low(k, rho):
    k = D(k); rho = D(rho)
    eps = pw(k, D(-1) / 3)
    br = 2 * sqrt(rho) - D('1.6781') * eps
    return c0 * pw(k, D(1) / 3) * br / (1 + rho * eps) * exp(-1 / (12 * (k + 1))) * exp(-rho ** 2 * pw(1 + rho * eps, D('1.5')) * exp(1 / (4 * (k + 1))) / (c0 * br))
print('eps(2001)=', pw(2001, D(-1) / 3), ' u=k^(1/3)=', pw(2001, D(1) / 3))
eps = pw(2001, D(-1) / 3)
Db = 3 * eps / (6 - 2 * eps)
print('Dbar=', Db)
UB = c0 * pw(1 + Db, D('1.5')) * (D(4) / 3 * pw(3 / (6 - 2 * eps), D('1.5')) + sqrt(Db) * pw(eps, D('1.5')))
print('UBbar(2001)=', UB)
k = D(2001)
sbar = D('1.15') * sqrt(2) * (3 * k - 1) * pw(k, D('-1.5'))
print('sbar(2001)=', sbar, ' 4000/6002=', D(4000) / 6002)
print('lower (b) rounded:', D('0.6664') * (1 - D('0.2099') - D('0.1091')) - D('0.2808'), ' exact:', D(4000) / 6002 * (1 - UB - sbar) - ub(2001))
print('d(2001)=', dd(2001), ' d(10001)=', dd(10001), ' u(10001)/(e 2^1.5)=', uu(10001) / (exp(D(1)) * pw(2, D('1.5'))), ' u(2001)/(e2^1.5)=', uu(2001) / (exp(D(1)) * pw(2, D('1.5'))))
print('Low(10001,1.4)=', Low(10001, '1.4'), ' Low(2001,0.75)=', Low(2001, '0.75'))
def Obar(k, a, extra=True):
    k = D(k)
    x = 1 + D(a) * pw(k, D(-1) / 3) + (1 / k if extra else 0)
    return dd(k) * exp(1 + 1 / (12 * k)) * pw(x, D('1.5'))
print('Obar far-window k=10001 with +1/k:', Obar(10001, '1.4'), ' without:', Obar(10001, '1.4', False))
print('Obar small-k (b) k=2001:', Obar(2001, '0.75'))
def wp(m):
    m = D(m)
    return D('1.99') + D('0.59963') * pw(m + 1, D(2) / 3) + D('1.24847') * pw(m + 1, D(1) / 3)
k = D(2001)
k23 = pw(k, D(2) / 3)
print('(6.45) diff at k=2001:', D('0.75') * k23 - (wp(k + D('0.75') * k23) - 1))
u = pw(k, D(1) / 3)
print('quad at u:', D('0.15037') * u * u - D('1.54829') * u - D('1.3365'))
print('big root:', (D('1.54829') + sqrt(D('1.54829') ** 2 + 4 * D('0.15037') * D('1.3365'))) / (2 * D('0.15037')))
print('tail terms:', D('0.39976') / D('12.601') + D('0.41616') / D('12.601') ** 2 + D('1.30212'))
print('wp prime at 1:', D(2) / 3 * D('0.59963') * pw(2, D(-1) / 3) + D(1) / 3 * D('1.24847') * pw(2, D(-2) / 3))
print('10*10001^(2/3)=', 10 * pw(10001, D(2) / 3), ' 10/2^(2/3)=', 10 / pw(2, D(2) / 3))
print('1.4*10001^(2/3)=', D('1.4') * pw(10001, D(2) / 3))
B = D('1.6781') * eps
print('B=', B, ' R(1/2)=', D('0.75') - 2 * B * pw(D('0.5'), D('1.5')) - 2 * c0 * sqrt(D('0.5')) + c0 * B)
# small-k-bulk: is Low(k,rho) used at rho in (1/2,3/4) OK; check monotonic sample
for kk in [2001, 5000, 10000]:
    print(kk, [str(Low(kk, r))[:8] for r in ['0.5', '0.6', '0.75', '1.0', '1.4']])
