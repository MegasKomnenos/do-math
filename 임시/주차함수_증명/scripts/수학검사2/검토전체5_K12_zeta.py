# K12: D.zeta-constants -- check the two-sided formulas at N=2000,4000 (40-digit floats, not interval arithmetic)
import mpmath as mp
mp.mp.dps = 40
for N in (2000, 4000):
    S = mp.fsum(mp.mpf(j)**mp.mpf(-1.5) for j in range(1, N))
    lo = S + 2*mp.mpf(N)**mp.mpf(-0.5) + mp.mpf(N)**mp.mpf(-1.5)/2
    hi = S + 2*(mp.mpf(N)-mp.mpf(0.5))**mp.mpf(-0.5)
    z32 = mp.zeta(mp.mpf(1.5))
    print(f"N={N}: z32 in [{mp.nstr(lo,14)}, {mp.nstr(hi,14)}]  true {mp.nstr(z32,14)}  contains: {lo <= z32 <= hi}")
    S2 = S + mp.mpf(N)**mp.mpf(-1.5)
    print(f"   coarse (no trapezoid): [{mp.nstr(S2+2*mp.mpf(N+1)**mp.mpf(-0.5),9)}, {mp.nstr(S2+2*(N+mp.mpf(0.5))**mp.mpf(-0.5),9)}]")
    Sm = mp.fsum(mp.sqrt(j) for j in range(1, N+1)); Sp = mp.fsum(mp.mpf(j)**mp.mpf(-0.5) for j in range(1, N+1))
    zm = Sm - (mp.mpf(2)/3*mp.mpf(N)**mp.mpf(1.5) + mp.sqrt(N)/2 + mp.mpf(N)**mp.mpf(-0.5)/24); em = mp.mpf(N)**mp.mpf(-2.5)/1920
    zp = Sp - (2*mp.sqrt(N) + mp.mpf(N)**mp.mpf(-0.5)/2 - mp.mpf(N)**mp.mpf(-1.5)/24); ep = mp.mpf(N)**mp.mpf(-3.5)/384
    zmt = mp.zeta(mp.mpf(-0.5)); zpt = mp.zeta(mp.mpf(0.5))
    print(f"   z(-1/2) in [{mp.nstr(zm-em,16)},{mp.nstr(zm+em,16)}] true {mp.nstr(zmt,16)} ok {zm-em <= zmt <= zm+em}")
    print(f"   z(1/2)  in [{mp.nstr(zp-ep,16)},{mp.nstr(zp+ep,16)}] true {mp.nstr(zpt,16)} ok {zp-ep <= zpt <= zp+ep}")
print("ZM12_ABS 0.2078862250607 minus |true| =", mp.nstr(mp.mpf('0.2078862250607') + mp.zeta(mp.mpf(-0.5)), 6))
