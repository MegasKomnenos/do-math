# -*- coding: utf-8 -*-
"""K14: 장 파일 머리(_K14_heads.json)와 대응표·장부 4절·의존지도 1절을 대조한다."""
import re, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B=r'C:\math\임시\주차함수_증명'
H=json.load(open(os.path.join(B,'scripts','수학검사2','_K14_heads.json'),encoding='utf-8'))
heads=[r for r in H['rows'] if r['typ']!='??']
secnum=lambda s: (re.match(r'(\d+(?:\.\d+)?)',s).group(1) if re.match(r'\d',s) else '?')
byl={}
for r in heads:
    r['secn']=secnum(r['sec']); r['full']=f"{r['chap']}:{r['label']}"
    byl[r['full']]=r
print('heads parsed',len(heads))
# ---------- 대응표
rows=[]
for line in open(os.path.join(B,'대조v2','라벨_번호_대응표_1114.md'),encoding='utf-8'):
    if line.startswith('| `{{'):
        c=[x.strip() for x in line.strip().strip('|').split('|')]
        lab=c[0].strip('`').strip('{}'); rows.append(dict(lab=lab,typ=c[1],name=c[2],num=c[3],old=c[4],sec=c[5]))
print('--- 대응표 rows',len(rows))
seen=set()
for d in rows:
    seen.add(d['lab']); h=byl.get(d['lab'])
    if not h: print('대응표: 장 파일에 없는 라벨',d); continue
    if h['typ']!=d['typ']: print('종류 불일치',d['lab'],'대응표',d['typ'],'장',h['typ'])
    if h['num']!=d['num']: print('번호 불일치',d['lab'],'대응표',d['num'],'장',h['num'])
    if h['secn']!=d['sec']: print('절 불일치',d['lab'],'대응표',d['sec'],'장',h['secn'],h['sec'][:30])
    hn=h['name'] if h['name'] else '—'
    if hn!=d['name']: print('이름 불일치',d['lab'],'\n   대응표:',d['name'],'\n   장   :',hn)
for f in byl:
    if f not in seen: print('대응표에 없는 장 머리',f,byl[f]['num'])
# ---------- 장부 4절
print('--- 장부 4절')
sec4=[];on=False
for line in open(os.path.join(B,'장부_v2.md'),encoding='utf-8'):
    if line.startswith('## 4.'): on=True
    elif line.startswith('## 5.'): on=False
    if on and line.startswith('| ') and not line.startswith('| 첫 판 번호') and not line.startswith('|---'):
        c=[x.strip() for x in line.strip().strip('|').split('|')]
        if len(c)>=6: sec4.append(dict(old=c[0],typ=c[1],name=c[2],rec=c[3],sec=c[4],lab=c[5]))
print('rows',len(sec4))
seen4=set()
for d in sec4:
    m=re.match(r'\{\{(.+)\}\}',d['lab'])
    if not m:
        if d['sec']!='뺌': print('뺌 아닌데 라벨 꼴 아님',d)
        continue
    lab=m.group(1); seen4.add(lab); h=byl.get(lab)
    if not h: print('4절: 장 파일에 없는 라벨',d); continue
    if h['typ']!=d['typ']: print('4절 종류 불일치',lab,d['typ'],h['typ'])
    if h['secn']!=d['sec']: print('4절 절 불일치',lab,d['sec'],h['secn'])
    # 머리 괄호 = 이름[; 기록 ...]
    exp=d['name']+(('; '+d['rec']) if d['rec'] else '')
    hn=h['name']
    if exp!=hn: print('4절 이름/기록 불일치',lab,'\n   4절:',exp,'\n   장 :',hn)
for f in byl:
    if f not in seen4: print('4절에 없는 장 머리',f)
# ---------- 의존지도 1절
print('--- 의존지도 1절')
dep=[];on=False
for line in open(os.path.join(B,'의존지도_v2.md'),encoding='utf-8'):
    if line.startswith('## 1.'): on=True
    elif line.startswith('### 1.1'): on=False
    if on and line.startswith('| `{{'):
        c=[x.strip() for x in line.strip().strip('|').split('|')]
        dep.append(dict(lab=c[0].strip('`').strip('{}'),sec=c[1],old=c[2],gist=c[3],status=c[4],inputs=c[5],rec=c[6],lit=c[7],D=c[8],note=c[9] if len(c)>9 else ''))
print('rows',len(dep))
# read chapter texts to compute citations per statement body
order=['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
texts={ch:open(os.path.join(B,'장v2',ch+'.md'),encoding='utf-8').read().split('\n') for ch in order}
# head line indexes (including 증명 heads) to delimit bodies
allheads=sorted([(r['file'],r['line']) for r in H['rows']])
def body(h):
    ch=h['file']; L=texts[ch]; start=h['line']  # 1-based
    nxt=[l for (f,l) in allheads if f==ch and l>start]
    end=(nxt[0]-1) if nxt else len(L)
    # also deferred proof segments: find "**<typ> {{lab}}의 증명.**" lines
    seg=L[start-1:end]
    for r in H['rows']:
        if r['typ']=='??' and ('{{'+h['full']+'}}의 증명' in r['raw']):
            s=r['line']; n2=[l for (f,l) in allheads if f==r['file'] and l>s]; e2=(n2[0]-1) if n2 else len(texts[r['file']])
            seg=seg+texts[r['file']][s-1:e2]
    return seg
lab_re=re.compile(r'\{\{(\d+:[^}]+)\}\}')
seenD=set()
for d in dep:
    lab=d['lab']; seenD.add(lab); h=byl.get(lab)
    if not h: print('의존지도: 장 파일에 없는 라벨',lab); continue
    if h['secn']!=d['sec']: print('의존 절 불일치',lab,d['sec'],h['secn'])
    # 지위: bracket before ';'
    st=h['status']; st_pre=st.split(';')[0].strip() if st else ''
    exp_status=d['status']
    if h['typ']=='정의':
        if exp_status!='정의' and exp_status!=st_pre: print('의존 지위(정의) 불일치',lab,'|',exp_status,'|',st_pre)
    else:
        if exp_status!=st_pre: print('의존 지위 불일치',lab,'\n   지도:',exp_status,'\n   장 :',st_pre)
    recs=set(re.findall(r'r[0-9a-f]{7}',st.split(';',1)[1])) if ';' in st else set()
    drecs=set(re.findall(r'r[0-9a-f]{7}',d['rec']))
    if recs!=drecs and h['typ']!='정의': print('의존 기록 식별자 불일치',lab,'지도',sorted(drecs),'장 머리',sorted(recs))
    if h['typ']=='정의' and drecs: print('정의 행의 기록 식별자(머리 없음; 옛 판 상속)',lab,sorted(drecs))
    # inputs: head citations and body citations
    headcites=[x for x in lab_re.findall(h['raw']) if x!=lab]
    seg=body(h)
    bodytxt='\n'.join(seg[1:])  # exclude head line itself
    bodycites=sorted(set(x for x in lab_re.findall(bodytxt) if x!=lab)-set(headcites))
    # also citations in head line not in status? include whole head line
    headc=sorted(set(headcites))
    inp=d['inputs']
    parts=inp.split('본문 인용:')
    dh=sorted(set(lab_re.findall(parts[0]))) if parts[0].strip() not in ('—','') else []
    db=sorted(set(lab_re.findall(parts[1]))) if len(parts)>1 else []
    if set(dh)!=set(headc): print('머리 인용 불일치',lab,'\n   지도:',dh,'\n   장 :',headc)
    if set(db)!=set(bodycites): print('본문 인용 불일치',lab,'\n   지도만:',sorted(set(db)-set(bodycites)),'\n   장만 :',sorted(set(bodycites)-set(db)))
    # gist = head paren
    g=d['gist']; hn=h['name']
    if hn and g!=hn: print('요지 불일치',lab,'\n   지도:',g,'\n   장 :',hn)
for f in byl:
    if f not in seenD: print('의존지도에 없는 장 머리',f)
