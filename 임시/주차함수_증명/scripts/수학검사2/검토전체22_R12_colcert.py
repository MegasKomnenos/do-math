# R12 review check: D.column-certificates-501-2000 and D.moment-certification numbers from session outputs
import json, math, sys, os
base = sys.argv[1]
rows = {}
for fn in ('res_p0.jsonl','res_p1.jsonl','res_ext_p0.jsonl','res_ext_p1.jsonl'):
    for line in open(os.path.join(base,'column_cert_iv',fn),encoding='utf-8'):
        line=line.strip()
        if not line: continue
        d=json.loads(line); rows[d['k']]=d
ks=sorted(rows)
print('columns',len(ks),ks[0],ks[-1],'all ok',all(rows[k]['ok'] for k in ks))
print('keys',sorted(rows[841].keys()))
mn=min(ks,key=lambda k:rows[k]['b0']); print('min b0',rows[mn]['b0'],mn)
print('min margin',min(rows[k]['margin'] for k in ks))
print('max e',max(rows[k]['e'] for k in ks),'max r_box',max(rows[k]['r_box'] for k in ks),'max E_trunc',max(rows[k]['E_trunc'] for k in ks))
print('max 2*pi_l_over_Nf',max(2*rows[k]['pi_l_over_Nf'] for k in ks), 'max Lip_h', max(rows[k]['Lip_h'] for k in ks))
print('wind',min(rows[k]['wind_sum_lo'] for k in ks),max(rows[k]['wind_sum_hi'] for k in ks),'tmax',max(rows[k]['t_max'] for k in ks))
print('s_hi-s_lo',min(rows[k]['s_hi']-rows[k]['s_lo'] for k in ks),max(rows[k]['s_hi']-rows[k]['s_lo'] for k in ks))
print('tailg max',max(rows[k]['tailg'] for k in ks),'Usharp max',max(rows[k]['Usharp_hi'] for k in ks),'eps_n0 max',max(rows[k]['eps_n0_hi'] for k in ks))
seps={}
for k in ks:
    d=rows[k]; seps[d['j0']/k]=seps.get(d['j0']/k,0)+1
print('sep/k counts',seps)
print('min n0-sep',min(rows[k]['n0']-rows[k]['j0'] for k in ks))
mg=max(ks,key=lambda k:rows[k]['Gamma_hi']); print('max Gamma',rows[mg]['Gamma_hi'],mg)
print('nV==NE_rec all',all(rows[k]['nV']==rows[k]['NE_rec'] for k in ks),'min psi_NE_lo',min(rows[k]['psi_NE_lo'] for k in ks))
print('n0<=nV all',all(rows[k]['n0']<=rows[k]['nV'] for k in ks),'NE_new==max',all(rows[k]['NE_new']==max(rows[k]['n0'],rows[k]['nV']) for k in ks))
NE={k:rows[k]['NE_new'] for k in ks}
print('NE<=ceil(0.836k^1.5)',all(NE[k]<=math.ceil(0.836*k**1.5) for k in ks),'max ratio',max(NE[k]/k**1.5 for k in ks))
print('monotone',all(NE[k]<NE[k+1] for k in ks[:-1]),'nondecr',all(NE[k]<=NE[k+1] for k in ks[:-1]))
print('NE 840,841,2000,501',NE[840],NE[841],NE[2000],NE[501],'max<=840',max(NE[k] for k in ks if k<=840),'min>=841',min(NE[k] for k in ks if k>=841))
th={}
for k in ks: th[rows[k]['theta']]=th.get(rows[k]['theta'],0)+1
print('theta',th)
for k in (501,841,1000,2000):
    d=rows[k]; print(k,d['theta'],repr(d['s_lo']),repr(d['s_hi']),d['b0'],d['PU_hi'],d['Gamma_hi'],d['n0'],d['nV'],d['j0'])
print('N,J,Nf for 501,2000',[(rows[k]['N'],rows[k]['J'],rows[k]['Nf'],14*k,40*k,64*14*k) for k in (501,2000)])
for key in ('rec_m0','rec_e'):
    pass
print({k:v for k,v in rows[501].items() if k.startswith('rec') or 'stored' in k or 'half' in k.lower()})
# moment: positions used by text
nM=json.load(open(os.path.join(base,'moment_cert_iv','nM.json')))
tot=sum(NE[k]-20001 for k in range(841,2001)); print('used positions',tot)
dif=[nM[str(k)]-NE[k] for k in range(841,2001)]; print('nM-NG range',min(dif),max(dif))
print('second range positions',sum(nM[str(k)]-1-10001+1 for k in range(841,2001)))
print('first range positions',sum((13*k*k)//100-(2*k+1)+1 for k in range(501,841)))
