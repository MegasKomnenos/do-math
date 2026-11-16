# 장 파일의 진술 머리를 추출해 장부 4절과 대조한다.
import re,glob,os,io,sys
base=r"C:\math\임시\주차함수_증명"
heads={}
order=[]
for f in sorted(glob.glob(os.path.join(base,"장v2","장*.md"))):
    txt=io.open(f,encoding='utf-8').read()
    for m in re.finditer(r'^\*\*(정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}(.*?)\*\*',txt,re.M):
        kind,lab,rest=m.group(1),m.group(2),m.group(3)
        heads.setdefault(lab,[]).append((os.path.basename(f),kind,rest.strip()))
        order.append(lab)
# 장부 4절
jb=io.open(os.path.join(base,"장부_v2.md"),encoding='utf-8').read().split('\n')
rows={}
for i in range(743,1191):
    l=jb[i]
    if not l.startswith('|'): continue
    cells=[c.strip() for c in l.strip().strip('|').split('|')]
    if len(cells)<6: continue
    old,kind,name,rec,sec,lab=cells[:6]
    m=re.search(r'\{\{([^}]+)\}\}',lab)
    if m:
        rows[m.group(1)]=(i+1,old,kind,name,rec,sec)
print("== 장 머리에 있으나 4절에 없는 라벨")
for lab in heads:
    if lab not in rows: print(lab,heads[lab])
print("== 4절에 있으나 장 머리에 없는 라벨")
for lab in rows:
    if lab not in heads: print(lab,rows[lab])
print("== 종류 불일치")
for lab,v in rows.items():
    if lab in heads:
        kinds=set(h[1] for h in heads[lab])
        if v[2] not in kinds: print(lab,v,kinds)
print("== 이름 대조 (4절 이름 vs 머리 괄호)")
for lab,v in rows.items():
    if lab in heads:
        rest=heads[lab][0][2]
        name=v[3]
        # extract name in parentheses
        mm=re.match(r'\s*\((.*?)\)\s*\[',rest)
        hn=mm.group(1) if mm else ''
        if name and name not in hn:
            print(lab,"| 4절:",name,"| 머리:",hn[:150])
        if not name and hn and not hn.startswith('기록'):
            print(lab,"| 4절 이름 비어있음 | 머리:",hn[:150])
