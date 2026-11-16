import re,glob,os,io,sys
base=r"C:\math\임시\주차함수_증명"
heads={}
for f in sorted(glob.glob(os.path.join(base,"장v2","장*.md"))):
    txt=io.open(f,encoding='utf-8').read()
    for m in re.finditer(r'^\*\*(정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}(.*?)\*\*',txt,re.M):
        heads.setdefault(m.group(2),[]).append((os.path.basename(f),m.group(1),m.group(3).strip()))
jb=io.open(os.path.join(base,"장부_v2.md"),encoding='utf-8').read().split('\n')
rows={}
for i in range(743,1191):
    l=jb[i]
    if not l.startswith('|'): continue
    cells=[c.strip() for c in l.strip().strip('|').split('|')]
    if len(cells)<6: continue
    old,kind,name,rec,sec,lab=cells[:6]
    m=re.search(r'\{\{([^}]+)\}\}',lab)
    if m: rows[m.group(1)]=(i+1,old,kind,name,rec,sec)
def paren(rest):
    # first balanced parenthesis group
    if not rest.startswith('('): return None
    depth=0
    for j,ch in enumerate(rest):
        if ch=='(': depth+=1
        elif ch==')':
            depth-=1
            if depth==0: return rest[1:j]
    return None
for lab,v in rows.items():
    h=heads[lab][0]
    p=paren(h[2])
    if p is None:
        print("NOPAREN",lab,"| 4절:",v[3],"|",h[2][:120]); continue
    parts=[s.strip() for s in p.split(';')]
    hname=parts[0]; hrec='; '.join(parts[1:])
    if v[3]!=hname:
        print("NAME",lab,"| 4절:",repr(v[3]),"| 머리:",repr(hname))
    if v[4]!=hrec:
        print("REC ",lab,"| 4절:",repr(v[4]),"| 머리:",repr(hrec))
# 둘째 판 절: check head is in the section
