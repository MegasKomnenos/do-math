# -*- coding: utf-8 -*-
# 심사 X7 — E3 검산: 9장 세 하계(9:old-7-25 균일 / 9:old-7-30 한 절단 / 9:old-7-32 LP)와
# F2 §9의 phi-변수 통합 LP  min{ phi/k + sum c_t z_t : -Ups<=phi<=0, 0<=z_t<=(phi+P^theta_t)/k, sum z_t >= v - (k+1)/k phi }
# 를 k=6668, 여러 nu 에서 비교한다. 모든 양은 9.4절의 닫힌 꼴 그대로(배정밀도; 증명이 아니라 크기 비교).
import math, sys

def g(x): return (x-1)*math.log(1+1/x)
def u_fn(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def v_fn(k):
    vp = max(k+1, 4000); iota = 2*k+1-vp
    return 2-2*min(1, 3*vp*iota**-1.5)-2*u_fn(k)-50.62/math.sqrt(k-1)
def Ups_hat(k): return (k-1)*u_fn(k)/(2*k+1)

def theta_list(k, tmax):
    # theta_t(k), t=k+1..tmax ; theta_{k+1} = (k/(k+1))^{k-1}; ratio theta_{t+1}/theta_t = (1+1/j)^j (1+1/t)^{-(t-1)}, j=t-k
    th = {k+1: (k/(k+1))**(k-1)}
    for t in range(k+1, tmax):
        j = t-k
        th[t+1] = th[t]*(1+1/j)**j*(1+1/t)**(-(t-1))
    return th

def setup(k, nu):
    n = 2*k+nu
    th = theta_list(k, 2*k+1)
    # P^theta_t = sum_{t'=k+1}^{t-1} theta_{t'},  t=k+2..2k+1
    P = {}; acc = 0.0
    for t in range(k+2, 2*k+2):
        acc += th[t-1]; P[t] = acc
    hN = lambda N: 1.5-47/(24*k)+(1-1.5/k)*0.307*k/(N+1)
    rho = {}
    for t in range(k+2, 2*k+2):
        env = n-t
        if env <= k-1:
            rho[t] = math.exp(g(t-1)-g(n-t+1))-1
        else:
            rho[t] = max(0.0, math.exp((hN(env)-k*(1-g(t-1)))/k)-1)
    rhoH = (1/k)*((1-1.5/k)*0.307*k/(k+nu-1)-47/(24*k))
    rhoL = 1.5*nu/(k*(k+nu))*(1-1.2/k)
    rhomin = max(0.0, min(rhoH, rhoL)) if nu <= k else max(0.0, rhoH)
    return n, P, rho, rhoH, rhoL, rhomin

def LP_greedy(costs, boxes, mass):
    # min sum c z, 0<=z<=u, sum z >= mass : fill cheapest first
    order = sorted(range(len(costs)), key=lambda i: costs[i])
    rem = mass; val = 0.0
    for i in order:
        if rem <= 0: break
        take = min(boxes[i], rem); val += costs[i]*take; rem -= take
    if rem > 1e-15: return float('nan')   # infeasible
    return val

out = []
k = 6668
v = v_fn(k); U = Ups_hat(k)
out.append(f"k={k}: v(k)={v:.5f}, Ups_hat={U:.5f}")
for nu in (103, 120, 150, 200, 300, 500, 742):
    n, P, rho, rhoH, rhoL, rhomin = setup(k, nu)
    ts = list(range(k+2, 2*k+2))
    costs = [rho[t] for t in ts]
    # 9.29 (균일):  Y = k rhomin v - U (1-(k+1) rhomin)
    Y29 = k*rhomin*v - U*(1-(k+1)*rhomin)
    # 9.36 (LP): Y^LP = k LP - U  with boxes P^theta_t/k, mass v
    lp36 = LP_greedy(costs, [P[t]/k for t in ts], v)
    Y36 = k*lp36 - U
    # 통합 LP: min over phi in [-U,0] of k*(phi/k + LP(phi))
    best = None; bestphi = None
    steps = 200
    for i in range(steps+1):
        phi = -U + U*i/steps
        val = LP_greedy(costs, [(phi+P[t])/k for t in ts], v-(k+1)/k*phi)
        tot = k*(phi/k + val)
        if best is None or tot < best: best, bestphi = tot, phi
    # 9.29 의 추가항 (U (k+1) rhomin) 과 LP-통합 차이
    out.append(f"nu={nu:4d}: rhomin*k={k*rhomin:.4f}  Y29={Y29:+.5f}  Y36(LP)={Y36:+.5f}  Y_unified={best:+.5f} (phi*={bestphi:+.4f})  "
               f"LP-29 gap={Y36-Y29:+.5f}  unified-LP={best-Y36:+.5f}  U(k+1)rhomin={U*(k+1)*rhomin:.5f}  F^LP=min(0,Y36)+(1-1/k)^nu/20={min(0,Y36)+(1-1/k)**nu/20:+.5f}")
with open(sys.argv[1] if len(sys.argv) > 1 else 'scripts/구조압축/심사_X7_E3_LP_out.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out)+'\n')
print('\n'.join(out))
