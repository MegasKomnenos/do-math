# -*- coding: utf-8 -*-
"""K14: 장부 1.2 전역 기호의 「정의 절」·「쓰이는 장」을 장 파일에서 글자 검색으로 대조한다(정규화 문자열 검색; 거짓 양성·음성은 손으로 본다)."""
import re,sys,io,os,json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B=r'C:\math\임시\주차함수_증명'
order=['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
chapof={'장1':'1','장2':'2','장3':'3','장4':'4','장5A':'5','장5B':'5','장6':'6','장7A':'7','장7B':'7','장8':'8','장9':'9','장10':'10','장11':'11'}
def norm(s): return re.sub(r'[\s{}]','',s)
texts={}
for ch in order:
    L=open(os.path.join(B,'장v2',ch+'.md'),encoding='utf-8').read().split('\n')
    # record section per line
    sec='';out=[]
    for ln in L:
        m=re.match(r'^(#{2,4})\s+(\d+(?:\.\d+)*)',ln)
        if m: sec=m.group(2)
        out.append((sec,norm(ln)))
    texts[ch]=out
rows=[];on=False
for line in open(os.path.join(B,'장부_v2.md'),encoding='utf-8'):
    if line.startswith('### 1.2'): on=True
    elif line.startswith('### 1.3'): on=False
    if on and line.startswith('| $'):
        c=[x.strip() for x in line.strip().strip('|').split('|')]
        rows.append(dict(glyph=c[0],mean=c[2],defsec=c[3],chs=c[4]))
print(len(rows),'rows')
# manual search keys: split glyph cell by ', ' at top level and use each $...$ piece; key = normalized inner
def pieces(g):
    return [norm(x) for x in re.findall(r'\$([^$]+)\$',g)]
# For some glyphs the key should be the base (e.g. 'c_m(Y)' -> 'c_m('): strip trailing argument list
def keys(p):
    ks={p}
    # drop args in parentheses at end
    q=re.sub(r'\([^()]*\)$','',p)
    if q!=p: ks.add(q)
    # drop inner (...) args e.g. s^T_t(y) -> s^T_t
    ks.add(re.sub(r'\([^()]*\)','',p))
    return [k for k in ks if len(k)>=2]
for r in rows:
    ps=pieces(r['glyph'])
    found={}  # chapter -> first (file,sec)
    for p in ps:
        for k in keys(p):
            for ch in order:
                for sec,ln in texts[ch]:
                    if k in ln:
                        c=chapof[ch]
                        if c not in found: found[c]=(ch,sec,k)
                        break
    chs_claim=[x.strip() for x in r['chs'].replace('전 장','1,2,3,4,5,6,7,8,9,10,11').split(',') if x.strip()]
    fchs=sorted(found,key=lambda x:int(x))
    first=min(((int(c),found[c][1]) for c in found),default=None)
    defsec=r['defsec']
    flag=''
    if set(fchs)!=set(chs_claim): flag+=' [쓰이는장≠] 검색:'+','.join(fchs)
    if first:
        # earliest occurrence section vs defsec (first section listed)
        d0=re.findall(r'\d+\.\d+',defsec); d0=d0[0] if d0 else defsec
        fs=min((found[c][1] for c in found if found[c][1]), key=lambda s:[int(x) for x in s.split('.')],default='')
        def key(s): return [int(x) for x in s.split('.')] if s else [0]
        if fs and d0 and key(fs)[:2]<key(d0)[:2]: flag+=f' [첫출현 {fs}<정의절 {d0}; {found[min(found,key=int)]}]'
    else: flag+=' [검색 결과 없음]'
    if flag: print(r['glyph'][:60],'|',defsec,'|',r['chs'],'|',flag)
