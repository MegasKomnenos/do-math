# -*- coding: utf-8 -*-
# 7절 머리말의 계약 「1.2의 '기록의 글자' 열은 기록의 집합이 7절 표와 같아야 한다」를 후보 수준으로 본다.
# (가) 1.2 행이 든 기록 가운데, 7절에서 같은 (글자체, 바탕 글자) 토큰을 가진 어느 행에도 없는 기록.
# (나) 7절 행의 (토큰, 기록) 가운데, 같은 (글자체, 바탕 글자)의 1.2 행 어느 것도 그 기록을 들지 않은 것.
# 여러 글자·여러 기록 묶음 행은 글자와 기록의 짝을 넓게 잡으므로(행 안의 모든 글자 × 모든 기록) 후보는 원문으로 확인한다.
import sys, io, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
BS=chr(92)
GREEK='alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa varkappa lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega ell'.split()
def keys(tok):
    # 토큰의 (글자체, 바탕) 열쇠들. 첨자·인수 안의 글자는 세지 않도록 맨 앞 머리만 본다(쉼표로 이은 변형은 호출 쪽에서 쪼갠다).
    t = tok.strip()
    t = re.sub(r'^(-|e\,|e\s*\,|'+re.escape(BS)+r'(widehat|hat|tilde|bar)\s*)', '', t)
    m = re.match(re.escape(BS)+r'(mathrm|operatorname)\s*\{([A-Za-z0-9]+)\}', t)
    if m: return ('로마체', m.group(2))
    m = re.match(re.escape(BS)+r'math(cal|frak|sf|bb)\s*(?:\{([A-Za-z]+)\}|\s*([A-Za-z]))', t)
    if m: return ({'cal':'필기체','frak':'프락투어','sf':'산세리프','bb':'칠판체'}[m.group(1)], m.group(2) or m.group(3))
    m = re.match(re.escape(BS)+r'(Pr)\b', t)
    if m: return ('칠판체','Pr')
    m = re.match(re.escape(BS)+r'([A-Za-z]+)', t)
    if m and m.group(1) in GREEK: return ('이탤릭', BS+m.group(1))
    m = re.match(r'([A-Za-z])', t)
    if m: return ('이탤릭', m.group(1))
    return None
def variants(cell):
    out=[]
    for tok in re.findall(r'\$([^$]+)\$', cell):
        depth=0; cur=''
        for ch in tok:
            if ch in '({[': depth+=1
            if ch in ')}]': depth-=1
            if ch==',' and depth==0: out.append(cur); cur=''
            else: cur+=ch
        out.append(cur)
    return [v.strip() for v in out if v.strip()]
def recs(cell): return set(re.findall(r'\[(r[0-9a-f]{7})\]', cell))
R12={}   # 열쇠 -> [(행, 글자, 기록집합)]
for ln,c in t12.table(49,288):
    for v in variants(c[0]):
        k=keys(v)
        if k: R12.setdefault(k,[]).append((ln,c[0],recs(c[6])))
R7={}    # 열쇠 -> [(행, 기록집합)]
rows7=t12.table(1243,1441)
for ln,c in rows7:
    for v in variants(c[0]):
        k=keys(v)
        if k: R7.setdefault(k,[]).append((ln,recs(c[1])))
mode=sys.argv[1] if len(sys.argv)>1 else 'a'
if mode=='a':
    done=set()
    for k,lst in R12.items():
        for ln,letter,rs in lst:
            if ln in done: continue
            done.add(ln)
            have=set()
            for kk in set(keys(v) for v in variants(letter) if keys(v)):
                for l7,r7 in R7.get(kk,[]): have|=r7
            miss=sorted(rs-have)
            if miss: print('(가) 1.2 %d행 %s: 1.2가 든 기록 %s 이 7절의 같은 바탕 글자 행에 없음 (7절 그 글자의 기록 %d개)'%(ln,letter,miss,len(have)))
else:
    for ln,c in rows7:
        rr=recs(c[1])
        for v in variants(c[0]):
            k=keys(v)
            if not k: continue
            cand=R12.get(k,[])
            if not cand: continue
            allr=set()
            for _,_,rs in cand: allr|=rs
            miss=sorted(rr-allr)
            if miss: print('(나) 7절 %d행 토큰 $%s$ %s: 기록 %s 이 1.2의 같은 바탕 글자 행(%s) 어디에도 없음'%(ln,v[:40],k,miss,','.join(str(x[0]) for x in cand)))
if mode=='a2':
    # (가) 후보마다 1.2의 「기록의 글자」 칸 원문과, 그 기록이 7절의 같은 바탕 글자 행 어느 칸에든 나오는지를 찍는다
    full={ln:c for ln,c in rows7}
    done=set()
    for k,lst in R12.items():
        for ln,letter,rs in lst:
            if ln in done: continue
            done.add(ln)
            have=set(); rowsk=set()
            for kk in set(keys(v) for v in variants(letter) if keys(v)):
                for l7,r7 in R7.get(kk,[]): have|=r7; rowsk.add(l7)
            for r in sorted(rs-have):
                anywhere=[l7 for l7 in sorted(rowsk) if ('['+r+']') in ' | '.join(full[l7])]
                allrows=[l7 for l7,c in rows7 if ('['+r+']') in c[1]]
                c12=[c for l,c in t12.table(ln,ln)][0]
                print('1.2 %d행 %s — 기록 [%s]\n   1.2 기록 칸: %s\n   7절 같은 바탕 글자 행의 다른 칸에 등장: %s; 7절에서 이 기록을 둘째 칸에 든 행: %s'%(ln,letter,r,c12[6][:420],anywhere,allrows))
