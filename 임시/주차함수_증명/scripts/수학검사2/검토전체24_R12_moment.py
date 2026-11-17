# R12: D.moment-certification 범위 수와 n_M - n^G 구간 (읽기 전용)
import json,glob
B=r"C:/math/임시/주차함수_증명/원고_자료/세션_재계산"
nM={int(k):v for k,v in json.load(open(B+'/moment_cert_iv/nM.json')).items()}
nG={}
keys=None
for f in ['res_p0.jsonl','res_p1.jsonl','res_ext_p0.jsonl','res_ext_p1.jsonl']:
    for line in open(B+'/column_cert_iv/'+f,encoding='utf-8'):
        line=line.strip()
        if not line: continue
        d=json.loads(line)
        if keys is None: keys=list(d.keys()); print(keys)
        nG[d['k']]=d
print(len(nM), min(nM),max(nM), len(nG), min(nG), max(nG))
ex=nG[841]; print({k:ex[k] for k in list(ex)[:40]})
print('---- counts')
NG={k:nG[k]['NE_new'] for k in nG}
assert all(NG[k]==max(nG[k]['n0'],nG[k]['nV']) for k in nG)
print('n0<=nV all:', all(nG[k]['n0']<=nG[k]['nV'] for k in nG), 'n0<nV all:', all(nG[k]['n0']<nG[k]['nV'] for k in nG))
print('NE_new==NE_rec all:', all(nG[k]['NE_new']==nG[k]['NE_rec'] for k in nG))
ks=sorted(nG)
print('monotone', all(NG[ks[i]]<NG[ks[i+1]] for i in range(len(ks)-1)), 'nondecr', all(NG[ks[i]]<=NG[ks[i+1]] for i in range(len(ks)-1)))
print('max over 501..840', max(NG[k] for k in range(501,841)), NG[840], 'min over 841..2000', min(NG[k] for k in range(841,2001)), NG[841], NG[2000], NG[501])
used=sum(NG[k]-1-20001+1 for k in range(841,2001))
comp=sum(nM[k]-1-10001+1 for k in range(841,2001))
print('used positions',used,'computed',comp)
dif=[nM[k]-NG[k] for k in range(841,2001)]
print('nM-nG range',min(dif),max(dif))
import math
print('bound 0.836k^1.5:', all(NG[k]<=math.ceil(0.836*k**1.5) for k in ks), max(NG[k]/k**1.5 for k in ks))
from collections import Counter
print(Counter(nG[k]['theta'] for k in ks))
print('min b0',min((nG[k]['b0'],k) for k in ks), 'min margin', min((nG[k]['margin'],k) for k in ks))
print('max e',max(nG[k]['e'] for k in ks),'max r_box',max(nG[k]['r_box'] for k in ks),'max E_trunc',max(nG[k]['E_trunc'] for k in ks))
print('max 2pi l/Nf', max(2*nG[k]['pi_l_over_Nf'] for k in ks))
print('wind', min(nG[k]['wind_sum_lo'] for k in ks), max(nG[k]['wind_sum_hi'] for k in ks),'tmax',max(nG[k]['t_max'] for k in ks))
print('lpU-lpL', set(round((nG[k]['s_hi']-nG[k]['s_lo'])*1e10,3) for k in ks))
print('Usharp max',max(nG[k]['Usharp_hi'] for k in ks),'eps_n0 max',max(nG[k]['eps_n0_hi'] for k in ks),'Gamma max',max((nG[k]['Gamma_hi'],k) for k in ks),'tailg max',max(nG[k]['tailg'] for k in ks))
print('psi_NE_lo min',min(nG[k]['psi_NE_lo'] for k in ks))
for k in (501,841,1000,2000):
    d=nG[k]; print(k,d['theta'],repr(d['s_lo']),repr(d['s_hi']),d['b0'],d['PU_hi'],d['Gamma_hi'],d['n0'],d['nV'],d['rec_m0'],d['rec_P_U'],d['rec_Gamma'])
print('b0>=rec', all(nG[k]['b0']>=nG[k]['rec_m0'] for k in ks), 'e/rec_e max', max(nG[k]['e']/nG[k]['rec_e'] for k in ks))
print('PU rel',max(abs(nG[k]['PU_hi']-nG[k]['rec_P_U'])/nG[k]['rec_P_U'] for k in ks),'Gamma rel',max(abs(nG[k]['Gamma_hi']-nG[k]['rec_Gamma'])/nG[k]['rec_Gamma'] for k in ks))
print('SU/N',max(nG[k]['SU'] for k in ks),'SL', max(nG[k]['SL'] for k in ks))
