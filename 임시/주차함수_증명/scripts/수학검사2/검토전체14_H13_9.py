# H13 검산: D.AR-integrals 의 네 값과 두 요구값
import mpmath as mp
mp.mp.dps = 30
k = mp.mpf(6668)
def pos(x): return x if x > 0 else mp.mpf(0)
f1 = lambda t: (1+t+2/k)**(-mp.mpf(7)/2)*pos(1-3*k**(-mp.mpf(1)/2)*(t-1/k)**(-mp.mpf(3)/2))
f2 = lambda t: (1+t+1/k)**(-mp.mpf(7)/2)*pos(1-3*(k-1)*k**(-mp.mpf(3)/2)*(t-1/k)**(-mp.mpf(3)/2))
t01 = 1/k + (3*k**(-mp.mpf(1)/2))**(mp.mpf(2)/3)
t02 = 1/k + (3*(k-1)*k**(-mp.mpf(3)/2))**(mp.mpf(2)/3)
J1 = mp.mpf(5)/2*mp.quad(f1, [t01, 1])
J2 = mp.mpf(5)/2*mp.quad(f2, [t02, (k-1)/k])
J3 = (k/(2*k+1))**(mp.mpf(5)/2)*(1-3/mp.sqrt(k))
J4 = (k/(2*k+1))**(mp.mpf(5)/2)*(1-3/mp.sqrt(k-1))
print("J1=%s J2=%s J3=%s J4=%s L*=%s" % tuple(mp.nstr(x, 8) for x in (J1, J2, J3, J4, J1+J2+J3+J4)))
d = mp.mpf('6.62')/mp.sqrt(k)
print("띠 요구값", mp.nstr((1+d/2)/(1-d/2), 8))
bulk = 1 + mp.mpf('1.676')*d/(2-d) + mp.mpf('0.676')*(mp.mpf('0.8825')/mp.sqrt(k) + mp.mpf('0.72')/k + mp.mpf('41.2')*(2/(mp.mpf('0.48')*k-102))**(mp.mpf(3)/2))
print("벌크 요구값", mp.nstr(bulk, 8))
# (2)의 상계 함수 최댓값
best = (0, 0)
for q in range(1, 6668):
    N = k+q
    v = min(1, 3*k*mp.mpf(q)**(-mp.mpf(3)/2))/(k*(mp.mpf('0.734')*pos((q+1)**(-mp.mpf(1)/2)-(mp.ceil(N/2)+1)**(-mp.mpf(1)/2))+mp.mpf('0.98')/(N+1)))
    if v*mp.sqrt(k) > best[0]: best = (v*mp.sqrt(k), q)
print("상계 함수 최댓값 * sqrt k =", mp.nstr(best[0], 7), "at q =", best[1])
