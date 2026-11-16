from mpmath import iv, mp
mp.dps=30; iv.dps=30
def z32(N, trap=True):
    s=iv.mpf(0)
    for j in range(1,N): s+= iv.mpf(1)/iv.sqrt(iv.mpf(j))**3
    Nn=iv.mpf(N)
    if trap:
        lo=s+2/iv.sqrt(Nn)+iv.mpf(1)/(2*iv.sqrt(Nn)**3); hi=s+2/iv.sqrt(Nn-iv.mpf(1)/2)
    else:
        s2=s+iv.mpf(1)/iv.sqrt(Nn)**3  # sum_{j<=N}
        lo=s2+2/iv.sqrt(Nn+1); hi=s2+2/iv.sqrt(Nn+iv.mpf(1)/2)
    return lo.a, hi.b
print("trap C=2000:", z32(2000))
print("crude C=2000:", z32(2000,False))
print("mpmath zeta(3/2)=", mp.zeta(1.5), " zeta(1/2)=", mp.zeta(0.5), " zeta(-1/2)=", mp.zeta(-0.5))
