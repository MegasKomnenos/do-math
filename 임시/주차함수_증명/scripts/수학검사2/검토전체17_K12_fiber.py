# K12: D.fiber-enumeration 재검산 — 순열 열거(곱 공식)와 직접 주차(n<=7) 둘 다
import itertools, sys
from collections import Counter

def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        m=0
        for j in range(1,i):
            if sig[j-1]>sig[i-1]: m=j
        h.append(i-m)
    return h

def row_from_caps(h):
    n=len(h)
    A=[0]
    for l in range(n):
        p=1
        for x in h: p*=min(x,l+1)
        A.append(p)
    return tuple(A[l+1]-A[l] for l in range(n))

def unimodal(b):
    i=0
    while i+1<len(b) and b[i]<=b[i+1]: i+=1
    while i+1<len(b) and b[i]>=b[i+1]: i+=1
    return i==len(b)-1

def park(pref):
    n=len(pref); occ=[0]*(n+2); out=[0]*(n+1)
    for car,a in enumerate(pref,1):
        s=a
        while s<=n and occ[s]: s+=1
        if s>n: return None
        occ[s]=1; out[s]=car
    return tuple(out[1:])

for n in range(1,8):
    ms=set(); nonuni=[]; 
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); ms.add(tuple(sorted(h)))
        b=row_from_caps(h)
        if not unimodal(b): nonuni.append((sig,h,b))
    print(f"n={n}: distinct cap multisets {len(ms)}, nonunimodal fibers {len(nonuni)}")
    if nonuni:
        nonuni.sort()
        print("  lex-first:", nonuni[0])
    # direct parking
    if n<=7:
        fib={}
        cnt=0
        for pref in itertools.product(range(1,n+1),repeat=n):
            out=park(pref)
            if out is None: continue
            cnt+=1
            M=max(i+1-a for i,a in zip(range(n),[0]*n)) if False else None
            # max displacement: position - preference
            disp=[0]*n
            for pos,car in enumerate(out,1):
                disp[pos-1]=pos-pref[car-1]
            fib.setdefault(out,Counter())[max(disp)]+=1
        print(f"  direct: parking functions {cnt} (expected {(n+1)**(n-1)}), permutations seen {len(fib)}")
        bad=0
        for sig,c in fib.items():
            b=tuple(c.get(l,0) for l in range(n))
            if b!=row_from_caps(caps(sig)): bad+=1
        print(f"  rows differing from product formula: {bad}")
