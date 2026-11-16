import json,gzip,os,sys
from fractions import Fraction
base=sys.argv[1]
def I(v):
    if isinstance(v,str):
        return Fraction(v) if '/' in v else int(v)
    return v
tot_coef=0; tot_seed=0; tot_init=0; reps={}; neg120=None; ntails=0
for k in range(2,121):
    d=json.load(open(os.path.join(base,f"producer/certificate-k{k}.json")))
    cut=d['cut']; r=d['r']
    assert r>=cut
    assert d['all_lower_bound_coefficients_nonnegative'] and d['finite_seed_ok']
    if k in (2,8,34,120): reps[k]=(cut,r,d['buffer'])
    fd=[I(v) for v in d['full_differences_initial']]
    assert len(fd)==cut,(k,len(fd),cut)
    negs=[n for n,v in enumerate(fd) if v<0]
    if k==120: neg120=(min(negs),max(negs)) if negs else None
    for n in range(max(16,2*k-1),cut): assert fd[n]>0,(k,n)
    si=[I(v) for v in d['smoothed_initial']]
    tot_init+=len(si)
    assert len(si)==r+k+2,(k,len(si),r+k+2)
    seeds=si[cut:r+k+1]; tot_seed+=len(seeds)
    assert all(v>=0 for v in seeds) and seeds[0]>0,(k,)
    assert all(v==0 for v in si[:cut]),(k,)
    gz=os.path.join(base,"producer",d['polynomials_gzip'])
    P=json.load(gzip.open(gz))
    if k==2: print(type(P), list(P.keys())[:10] if isinstance(P,dict) else len(P))
    polys=P['lower_bound_polynomials'] if isinstance(P,dict) and 'lower_bound_polynomials' in P else P
    if isinstance(polys,dict):
        for key,v in polys.items():
            coefs=v if isinstance(v,list) else v.get('coefficients',v)
            tot_coef+=len(coefs)
            assert all(I(c)>=0 for c in coefs),(k,key)
    elif isinstance(polys,list):
        for v in polys:
            coefs=v if isinstance(v,list) else v.get('coefficients',v)
            tot_coef+=len(coefs)
print("reps",reps,"neg k=120 range",neg120)
print("coef",tot_coef,"seeds",tot_seed,"init",tot_init)
