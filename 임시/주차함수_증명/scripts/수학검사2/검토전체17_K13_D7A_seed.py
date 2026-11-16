# K13: read r9e782f5 certificates; check cut/r, counts, nonneg, negative small-n differences
import json,glob,os,sys
d=r'C:\math\임시\주차함수_증명\원고_자료\r9e782f5\producer'
files=sorted(glob.glob(os.path.join(d,'certificate-k*.json')),key=lambda f:int(os.path.basename(f)[13:-5]))
print(len(files))
c0=json.load(open(files[0]))
print(sorted(c0.keys()))
tot_lb=0; tot_Q=0; tot_init=0; bad=[]
for f in files:
    c=json.load(open(f)); k=c.get('k'); cut=c.get('cut'); r=c.get('r')
    if k in (2,8,34,120): print(k,cut,r, c.get('finite_seed_ok'), c.get('all_lower_bound_coefficients_nonnegative'))
    if not c.get('finite_seed_ok') or not c.get('all_lower_bound_coefficients_nonnegative'): bad.append(k)
    if r is not None and cut is not None and r<cut: bad.append(('r<cut',k))
    lb=c.get('lower_bound_coefficients') or c.get('lower_bound_vector') or c.get('lower_cone')
    for key in c:
        v=c[key]
        if isinstance(v,dict) and all(isinstance(x,list) for x in v.values()):
            pass
    si=c.get('smoothed_initial'); fdi=c.get('full_differences_initial')
    if si is not None:
        tot_init+=len(si)
        tot_Q+=sum(1 for n in range(cut, r+k+1) if n<len(si))
    if fdi is not None:
        neg=[n for n,v in enumerate(fdi) if (int(v) if not isinstance(v,str) else int(v))<0]
        if k==120: print('k=120 neg n:', neg[:3], '...', neg[-3:], 'len', len(fdi))
        # check positivity on max(16,2k-1)<=n<cut
        for n in range(max(16,2*k-1),cut):
            if int(fdi[n])<=0: bad.append(('nonpos',k,n))
print('bad',bad[:10]); print('tot smoothed initial',tot_init,'tot Q in check range',tot_Q)
