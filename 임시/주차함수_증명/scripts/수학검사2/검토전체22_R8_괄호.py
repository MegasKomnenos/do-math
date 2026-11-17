# 검토 22차 R8: 정리 8:old-6-33 둘째 단계의 행별 괄호가 (8.23)의 L들로 막히는지,
# 본문의 행 경우 나눔(수준 k, k-1)이 모든 행을 덮는지 직접 센다.
from math import floor, ceil, exp, inf
import sys
def qmaxf(k):
    q = int(round(6*k**(2/3)))
    while q**3 > 216*k*k: q -= 1
    while (q+1)**3 <= 216*k*k: q += 1
    return q
def hfun(k, nu): return k/(k+nu)-k/(2*k-1)
def check(k, nu, report):
    n = 2*k+nu; qmax = qmaxf(k)
    qfb = (3*(k-1)//4 - qmax - 3)  # floor((3(k-1)/4 - qmax - 3)/8) 를 정확히
    # 3(k-1)/4 는 정수가 아닐 수 있다: floor((3(k-1) - 4qmax - 12)/32)
    qfb = (3*(k-1) - 4*qmax - 12)//32
    mfb = -((-5*k)//4) + qmax
    if nu >= qmax+1: case = 'i'; qw = qmax; qstar = 6*k**(2/3)
    elif nu-1 >= k/4: case = 'ii'; qw = nu-1; qstar = nu-1
    else: return None
    # 수준 k
    if nu >= qfb+2: La = k/(n-k)-k/(2*k+2)*exp(-hfun(k, nu)); La_un = k/(n-k)-k/(2*k+2)
    else: La = k/(n-k)-max(0.5, k/(n-qfb)); La_un = La
    Lc = k/(k+qfb+1)-0.5 if (nu >= qfb+2 and qfb >= qw) else inf
    k1 = k-1
    if nu >= qfb+2: La1 = k1/(k+nu+1)-k1/(2*k)*exp(-hfun(k1, nu+2)); La1_un = k1/(k+nu+1)-k1/(2*k)
    else: La1 = k1/(k+nu+1)-max(0.5, k1/(n-qfb)); La1_un = La1
    Lc1 = k1/(k+qfb+1)-0.5 if (nu >= qfb+2 and qfb >= qw) else inf
    out = []
    for i in range(8):
        Li = k/(k+qstar+1)-k/(2*k+2-(i+1)*qfb)
        Li1 = k1/(k+qstar)-k1/(2*k+2-(i+1)*qfb)
        for m in range(2*k+1-i*qfb, n):
            assert m >= mfb
            # 수준 k
            a = max(m-k+1, k+qw+1); b = min(2*k+1, m-qfb)
            br = k/a-k/(b+1)
            typeA = (b == 2*k+1 and a == m-k+1)
            # typeA 행은 위험률로 다듬은 괄호가 La 이상(본문 논증). 그 밖의 행은 다듬지 않은 괄호가 min(L) 이상이어야 한다.
            tgt = min(La, Lc, Li)
            ok = (tgt <= 0) or (typeA and min(La_un, Lc, Li) <= br + 1e-15 and True) or (not typeA and br >= tgt-1e-15)
            if typeA:
                # 다듬은 괄호 >= La 는 본문 논증(m에 감소)으로 성립; 여기서는 다듬지 않은 값끼리 비교
                ok = (min(La_un, Lc, Li) <= br+1e-15) or tgt <= 0
            if not ok: out.append(('k', i, m, a, b, br, La, Lc, Li))
            # 본문의 경우 나눔 (수준 k): 첫째 m>=max(2k+1+qfb,2k+qw); 둘째 2k+qw<=m<2k+1+qfb; 셋째 m<2k+qw
            # 수준 k-1
            a1 = max(m-k+2, k+qw); b1 = min(2*k-1, m-qfb)
            br1 = k1/a1-k1/(b1+1)
            typeA1 = (b1 == 2*k-1 and a1 == m-k+2)
            tgt1 = min(La1, Lc1, Li1)
            if typeA1: ok1 = (min(La1_un, Lc1, Li1) <= br1+1e-15) or tgt1 <= 0
            else: ok1 = (br1 >= tgt1-1e-15) or tgt1 <= 0
            if not ok1: out.append(('k-1', i, m, a1, b1, br1, La1, Lc1, Li1))
            # 본문의 수준 k-1 경우 나눔에서 '둘째 경우'(2k+qw-2 <= m <= 2k+qfb-1)인데 Lc1=inf 인 행
            if report and i == 0 and (2*k+qw-2 <= m <= 2*k+qfb-1) and Lc1 == inf and nu >= qfb+2:
                out.append(('본문 둘째 경우·L\'c=inf', k, nu, m, 'qfb', qfb, 'qw', qw, 'br1', br1, 'La1', La1, 'Li1', Li1))
    return case, qfb, qw, out
if __name__ == '__main__':
    tot = 0; flagged = 0; examples = []
    # q_fb = q_w - 1 이 되는 k 찾기 (경우 (i): q_w = q_max)
    special = [k for k in range(300000, 450000) if (3*(k-1)-4*qmaxf(k)-12)//32 == qmaxf(k)-1][:3]
    print("q_fb = q_max - 1 인 k (처음 셋):", special)
    ks = [6668, 6669, 6700, 9000, 13000, 13823, 20000, 10**5] + special
    for k in ks:
        qmax = qmaxf(k); qfb = (3*(k-1)-4*qmax-12)//32
        nus = set()
        step = max(1, int(0.48*k)//25)
        nus.update(range(103, int(0.48*k)+1, step))
        for d in range(-3, 5):
            for base in (qmax, qfb, k//4, int(0.48*k)):
                v = base+d
                if 103 <= v <= 0.48*k: nus.add(v)
        for nu in sorted(nus):
            r = check(k, nu, True)
            if r is None: continue
            tot += 1
            for o in r[3]:
                flagged += 1
                if len(examples) < 12: examples.append(o)
        print("k", k, "qmax", qmax, "qfb", qfb, "누적 검사", tot, "누적 표시", flagged, flush=True)
    for e in examples: print(e)
