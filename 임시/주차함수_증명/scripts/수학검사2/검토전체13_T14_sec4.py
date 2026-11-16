# T14: 장부 4절(라벨 대응) 대 장 파일 진술 머리 대조
import re, os
root = r"C:\math\임시\주차함수_증명"
heads = {}
order = []
for line in open(os.path.join(root,"scripts","수학검사2","검토전체13_T14_heads.tsv"),encoding='utf-8'):
    f,ln,kind,label,name,status = line.rstrip('\n').split('\t')
    if not label: continue
    if label in heads:  # second occurrence (증명 머리) -> skip
        continue
    heads[label]=(f,int(ln),kind,name,status)
    order.append(label)
# sections
secs = {}
for line in open(os.path.join(root,"scripts","수학검사2","검토전체13_T14_secs.tsv"),encoding='utf-8'):
    f,ln,title = line.rstrip('\n').split('\t')
    secs.setdefault(f,[]).append((int(ln),title))
def sec_of(f,ln):
    best=None
    for l,t in secs.get(f,[]):
        if l<=ln: best=t
    m = re.match(r'#+\s*([0-9]+(?:\.[0-9]+)*)',best or '')
    return m.group(1) if m else (best or '')
# parse 4절
lines = open(os.path.join(root,"장부_v2.md"),encoding='utf-8').read().split('\n')
rows=[]
in4=False
for i,l in enumerate(lines,1):
    if l.startswith('## 4.'): in4=True; continue
    if l.startswith('## 5.'): break
    if in4 and l.startswith('|') and not l.startswith('|---') and not l.startswith('| 첫 판 번호'):
        cells=[c.strip() for c in l.strip().strip('|').split('|')]
        if len(cells)>=6: rows.append((i,cells))
print("rows",len(rows))
seen=set()
for i,c in rows:
    old,kind,name,rec,sec,label=c[:6]
    m=re.match(r'\{\{(.+)\}\}',label)
    if not m:
        # 뺀 라벨: 장 파일에 있으면 안 됨
        m2=re.match(r'\((.+)\)',label)
        if m2:
            lab='{{'+m2.group(1)+'}}'
            if lab in heads: print(f"L{i} 뺌인데 장 파일에 있음: {lab} {heads[lab][:2]}")
        continue
    lab=label; seen.add(lab)
    if lab not in heads:
        print(f"L{i} 장부에 있으나 장 파일 머리에 없음: {lab}"); continue
    f,ln,hk,hname,hstatus=heads[lab]
    hsec=sec_of(f,ln)
    probs=[]
    if hk!=kind: probs.append(f"종류 장부={kind} 장={hk}")
    # section: compare prefix (장부 sec may be '5.5', head sec '5.5.3')
    if sec and not (hsec==sec or hsec.startswith(sec+'.')): probs.append(f"절 장부={sec} 장={hsec}")
    # name: 장부 name should appear in head paren
    hn = hname.strip('()')
    hn_main = hn.split(';')[0].strip()
    if name and name.replace(' ','') != hn_main.replace(' ',''):
        probs.append(f"이름 장부=「{name}」 장=「{hn_main}」")
    if not name and hn_main: probs.append(f"이름 장부=빈칸 장=「{hn_main}」")
    # record name
    if rec:
        rec_main = re.sub(r'^기록 ','',rec)
        if rec_main.replace(' ','') not in hn.replace(' ',''):
            probs.append(f"기록이름 장부=「{rec}」 장괄호=「{hn}」")
    else:
        if '기록' in hn or '[r' in hn: probs.append(f"기록이름 장부=빈칸 장괄호=「{hn}」")
    if probs: print(f"L{i} {lab} ({f}:{ln}): "+" | ".join(probs))
print("--- 장 파일 머리에 있으나 장부 4절에 없음:")
for lab in order:
    if lab not in seen: print(lab, heads[lab][:2])
