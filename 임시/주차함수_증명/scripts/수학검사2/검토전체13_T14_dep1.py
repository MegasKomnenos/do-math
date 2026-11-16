# T14: 의존지도 1절 대 장 파일 머리(절·지위·머리 인용 라벨·식별자) 대조
import re, os
root=r"C:\math\임시\주차함수_증명"
chfiles=["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re=re.compile(r'^\*\*(정의|정리|보조정리|명제|따름정리)\s+(\{\{[^}]+\}\})\s*(?:\((.*?)\)\s*)?(?:\[(.*?)\])?\s*\.?\*\*')
lab_re=re.compile(r'\{\{(\d+):[^}]+\}\}')
info={}; order=[]
cursec={}
for f in chfiles:
    lines=open(os.path.join(root,"장v2",f),encoding='utf-8').read().split('\n')
    sec=''; cur=None
    for ln,l in enumerate(lines,1):
        m=re.match(r'#+\s*([0-9]+(?:\.[0-9]+)*)',l)
        if m: sec=m.group(1)
        h=head_re.match(l)
        if h and h.group(2) not in info:
            lab=h.group(2); status=h.group(4) or ''
            st=status.split(';')[0].strip(); ids=status.split(';')[1].strip() if ';' in status else ''
            headlabs=set(lab_re.findall(l) and re.findall(r'\{\{\d+:[^}]+\}\}',l))-{lab}
            info[lab]={'sec':sec,'status':st,'ids':ids,'headlabs':headlabs,'body':set(),'file':f,'ln':ln}
            order.append(lab); cur=lab
        elif h and h.group(2) in info:
            cur=h.group(2)  # 뒤로 미룬 증명
        elif cur and not l.startswith('#'):
            for x in re.findall(r'\{\{\d+:[^}]+\}\}',l):
                if x!=cur: info[cur]['body'].add(x)
print("heads",len(info))
# parse 의존지도 1절
rows=[]
for i,l in enumerate(open(os.path.join(root,"의존지도_v2.md"),encoding='utf-8'),1):
    if l.startswith('## 2'): break
    if l.startswith('| `{{'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        rows.append((i,c))
print("rows",len(rows))
seen=set()
for i,c in rows:
    lab=c[0].strip('`'); seen.add(lab)
    if lab not in info: print(f"L{i} {lab} 장 파일에 없음"); continue
    I=info[lab]; probs=[]
    sec=c[1]
    if not (I['sec']==sec or I['sec'].startswith(sec+'.')): probs.append(f"절 지도={sec} 장={I['sec']}")
    st=c[4]
    stn=re.sub(r'\s+','',st); In=re.sub(r'\s+','',I['status'])
    if stn!=In and not (st=='정의' and I['status']==''): probs.append(f"지위 지도=「{st}」 장=「{I['status']}」")
    # 입력 라벨
    inp=c[5]
    headpart=inp.split('본문 인용:')[0]
    bodypart=inp.split('본문 인용:')[1] if '본문 인용:' in inp else ''
    hl=set(re.findall(r'\{\{\d+:[^}]+\}\}',headpart)); bl=set(re.findall(r'\{\{\d+:[^}]+\}\}',bodypart))
    if hl!=I['headlabs']: probs.append(f"머리 인용 지도={sorted(hl)} 장={sorted(I['headlabs'])}")
    bodyexp=I['body']-I['headlabs']
    if bl!=bodyexp:
        probs.append(f"본문 인용 차이: 지도에만={sorted(bl-bodyexp)} 장에만={sorted(bodyexp-bl)}")
    ids=c[6]
    jid=set(re.findall(r'r[0-9a-f]{7}',ids)); hid=set(re.findall(r'r[0-9a-f]{7}',I['ids']))
    if hid and not hid<=jid: probs.append(f"식별자 장에만={sorted(hid-jid)}")
    if probs: print(f"L{i} {lab} ({I['file']}:{I['ln']}): "+" | ".join(probs))
print("--- 장에 있으나 지도 1절에 없음:",[l for l in order if l not in seen])
