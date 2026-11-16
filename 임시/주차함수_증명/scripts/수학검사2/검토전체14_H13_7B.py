# H13 검산: 부록 D.band102-integer (ㄱ)(ㄴ)(ㄷ)
from fractions import Fraction as Fr
from math import isqrt, factorial, floor
import mpmath as mp
mp.mp.dps = 40
# (ㄱ) 쌍 수와 최솟값 (k=10000)
k = 10000
def ex_bar(q):
    pi = Fr(q*(q-1), 2*(k+1))
    return q + (k+q)*pi/(1-pi)
cnt_u = cnt_o = 0; best = (None, Fr(10))
for q in range(1, 50):
    for qp in range(q, 50):
        for j in range(0, 51-q-qp):
            cnt_u += 1; cnt_o += 1 if q == qp else 2
            v = 1 - Fr(j, k)*(ex_bar(q)+ex_bar(qp)) - (ex_bar(q)*(qp-1)+ex_bar(qp)*(q-1))/(2*k)
            if v < best[1]: best = ((q, qp, j), v)
print("(ㄱ) 순서없는 쌍 수", cnt_u, "순서쌍 수", cnt_o, "최솟값", best[0], float(best[1]))
# (ㄴ) 꼬리 삼중 (7.12) 정확 평가 (mpmath 40자리로; 방향은 참값 평가)
def Bor(m): return mp.e**(-m)*mp.mpf(m)**(m-1)/mp.factorial(m)
def kebar(K1, M):
    K1 = mp.mpf(K1); M = mp.mpf(M)
    return 3*(M-1)/(2*(K1+1)) + (M-1)*(3*M-4)/(12*(K1+1)**2) + (M-1)**2/(2*(K1+1)*(K1+2-M)) + (M-1)**4/(12*(K1+1)**2*(K1+2-M))
for (K1, M, tf) in ((10**4,120,'0.54'),(2*10**4,250,'0.593'),(10**5,300,'0.522'),(10**5,450,'0.548'),(10**6,700,'0.519')):
    tf = mp.mpf(tf); kb = kebar(K1, M); ekb = mp.e**kb
    bors = [Bor(s+1) for s in range(M)]
    minrel = None; argmin = None; allok = True
    for q in range(2, M+1):
        s = mp.fsum(bors[sidx]*((q-1-sidx)+tf*mp.mpf(q-1-sidx)**1.5) for sidx in range(q-1))
        F = tf*mp.mpf(q)**1.5 - ekb*s
        if F < 0: allok = False
        rel = F/(tf*mp.mpf(q)**1.5)
        if minrel is None or rel < minrel: minrel, argmin = rel, q
    print("(ㄴ) K1=%d M=%d tf=%s: 모두>=0 %s, 최소 상대 여유 %s (q=%d), kebar=%s, tf*M^1.5=%s <K1 %s" % (K1, M, tf, allok, mp.nstr(minrel, 4), argmin, mp.nstr(kb, 4), mp.nstr(tf*mp.mpf(M)**1.5, 6), tf*mp.mpf(M)**1.5 < K1))
# (ㄷ) nu_P(K1) 배정밀도 훑기 (방향 반올림 없음; 후보 확인용)
def lb(K1, M, tf, q, qp, j):
    def nh(q): return 0.0 if q == 1 else tf*q**1.5/K1
    def exh(q):
        n = nh(q); return q + (K1+q)*n/(1-n)
    return 1 - j/K1*(exh(q)+exh(qp)) - (exh(q)*(qp-1)+exh(qp)*(q-1))/(2*K1)
table = [(12000,120,0.54),(13000,120,0.54),(14000,120,0.54),(15000,120,0.54),(20000,120,0.54),(30000,250,0.593),(50000,250,0.593),(100000,300,0.522),(200000,450,0.548),(500000,450,0.548),(1000000,700,0.519)]
for (K1, M, tf) in table:
    nu = 2; last_ok = None; worst=None
    while True:
        mn = None; arg=None
        for q in range(1, min(M, nu-1)+1):
            for qp in range(q, min(M, nu-q)+1):
                j = nu-q-qp
                if j < 0: continue
                v = lb(K1, M, tf, q, qp, j)
                if mn is None or v < mn: mn, arg = v, (q, qp, j)
        if mn is None or mn <= 0:
            print("(ㄷ) K1=%d: nu_P=%s 최악 %s lb=%.4f ; 껍질 %d 최소 lb=%.4f" % (K1, last_ok, worst[1], worst[0], nu, mn if mn is not None else float('nan')))
            break
        last_ok = nu; worst = (mn, arg); nu += 1
        if nu > M+1: 
            print("(ㄷ) K1=%d: 껍질 한계 M+1 도달" % K1); break
