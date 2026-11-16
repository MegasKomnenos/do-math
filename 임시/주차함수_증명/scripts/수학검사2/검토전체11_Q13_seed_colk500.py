import json,glob,os,math
R=glob.glob("C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/r9e782f5*")[0]
tot_coef=0; tot_seed=0; tot_init=0; neg120=None
reps={}
for k in range(2,121):
    d=json.load(open(os.path.join(R,"producer",f"certificate-k{k}.json")))
    cut=d['cut']; r=d['r']
    assert d['all_lower_bound_coefficients_nonnegative'] and d['finite_seed_ok']
    tot_coef+=sum(int(x)+1 for x in d['degrees'].values()) if isinstance(d['degrees'],dict) else 0
    sm=d['smoothed_initial']; tot_init+=len(sm)
    assert len(sm)==r+k+2, (k,len(sm),r+k+2)
    seeds=sm[cut:r+k+1]; tot_seed+=len(seeds)
    assert all(float(x)>=0 for x in seeds) and float(sm[cut])>0
    fd=d['full_differences_initial']; assert len(fd)==cut
    lo=max(16,2*k-1)
    assert all(int(x)>0 for x in fd[lo:cut]), k
    negs=[n for n in range(cut) if int(fd[n])<0]
    if k in (2,8,34,120): reps[k]=(cut,r,negs[:1],negs[-1:] )
print("coef",tot_coef,"seeds",tot_seed,"init",tot_init)
print(reps)
d=json.load(open(os.path.join(R,"producer","certificate-k120.json")))
print("degrees k120",d['degrees'])
# integer inequality
L=10**21*400**10; Rr=17**21*123**10
print(L, Rr, L>Rr, "%.6e %.6e"%(L,Rr))
# comparison counts
def B(k): return -(-k*k//4)
dd1=sum(2*B(k)-(2*k+1)+1 for k in range(121,161)); dd2=sum(2*B(k)-(2*k+1)+1 for k in range(161,501))
r1=sum(B(k)+1 for k in range(121,161)); r2=sum(B(k)+1 for k in range(161,501))
print("direct",dd1,dd2,"ratio",r1,r2)
