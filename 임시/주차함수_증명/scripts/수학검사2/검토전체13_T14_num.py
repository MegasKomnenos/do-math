# T14: 대응표 「현재 번호」·종류·절 대 장 파일 머리 순서 대조
import re, os
root = r"C:\math\임시\주차함수_증명"
chmap={"장1.md":1,"장2.md":2,"장3.md":3,"장4.md":4,"장5A.md":5,"장5B.md":5,"장6.md":6,"장7A.md":7,"장7B.md":7,"장8.md":8,"장9.md":9,"장10.md":10,"장11.md":11}
heads=[]; seen=set()
for line in open(os.path.join(root,"scripts","수학검사2","검토전체13_T14_heads.tsv"),encoding='utf-8'):
    f,ln,kind,label,name,status=line.rstrip('\n').split('\t')
    if f not in chmap or not label or label in seen: continue
    seen.add(label); heads.append((chmap[f],f,int(ln),kind,label,name))
num={}; cnt={}
for ch,f,ln,kind,label,name in heads:
    cnt[ch]=cnt.get(ch,0)+1; num[label]=(f"{ch}.{cnt[ch]}",kind,f,ln,name)
secs={}
for line in open(os.path.join(root,"scripts","수학검사2","검토전체13_T14_secs.tsv"),encoding='utf-8'):
    f,ln,title=line.rstrip('\n').split('\t'); secs.setdefault(f,[]).append((int(ln),title))
def sec_of(f,ln):
    best=None
    for l,t in secs.get(f,[]):
        if l<=ln: best=t
    m=re.match(r'#+\s*([0-9]+(?:\.[0-9]+)*)',best or ''); return m.group(1) if m else ''
rows=[]
for i,l in enumerate(open(os.path.join(root,"대조v2","라벨_번호_대응표_1114.md"),encoding='utf-8'),1):
    if l.startswith('| `{{') or l.startswith('| ('):
        cells=[c.strip() for c in l.strip().strip('|').split('|')]
        rows.append((i,cells))
print("rows",len(rows),"heads",len(num))
seen2=set()
for i,c in rows:
    lab=c[0].strip('`'); kind=c[1]; name=c[2]; cur=c[3]; sec=c[5] if len(c)>5 else ''
    if lab.startswith('('):
        if '{{'+lab.strip('()')+'}}' in num: print(f"L{i} 뺌 표기인데 장 파일에 있음 {lab}")
        continue
    seen2.add(lab)
    if lab not in num: print(f"L{i} {lab}: 장 파일에 없음 (표 번호 {cur})"); continue
    n,k,f,ln,hname=num[lab]
    probs=[]
    if n!=cur: probs.append(f"번호 표={cur} 실제={n}")
    if k!=kind: probs.append(f"종류 표={kind} 실제={k}")
    hs=sec_of(f,ln)
    if sec and not (hs==sec or hs.startswith(sec+'.')): probs.append(f"절 표={sec} 실제={hs}")
    hn=hname.strip('()')
    if name!='—' and name.replace(' ','')!=hn.replace(' ',''): probs.append(f"이름 표=「{name}」 실제=「{hn}」")
    if name=='—' and hn: probs.append(f"이름 표=— 실제=「{hn}」")
    if probs: print(f"L{i} {lab} ({f}:{ln}): "+" | ".join(probs))
print("--- 장 파일에 있으나 표에 없음:",[l for l in num if l not in seen2])
