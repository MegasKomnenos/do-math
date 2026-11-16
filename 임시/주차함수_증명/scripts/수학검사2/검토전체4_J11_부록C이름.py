import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# heads with full names
files=['장v2/장%s.md'%c for c in ['1','2','3','4','5A','5B','6','7A','7B','8','9','10']]
H={}
for f in files:
    for line in open(f,encoding='utf-8'):
        m=re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\} \((.*?)\) \[',line)
        if m: H[m.group(2)]=(m.group(1),m.group(3))
        else:
            m=re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\} \((.*?)\)\s*\[',line)
            if m: H[m.group(2)]=(m.group(1),m.group(3))
C=open('장v2/부록C.md',encoding='utf-8').read().split('\n')
n=0
for l in C:
    m=re.match(r'^\| (기록 \[.*?) \| (정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\} \| (.*?) \|$',l)
    if not m: continue
    n+=1
    recname,typ,lab,name=m.groups()
    if lab not in H: print('없는 라벨',lab); continue
    htyp,hname=H[lab]
    # head name: "이름; 기록 [rX]의 Y" possibly
    parts=hname.split('; ',1)
    hn=parts[0].strip(); hrec=parts[1].strip() if len(parts)>1 else ''
    issues=[]
    if htyp!=typ: issues.append(f'유형 {typ}≠머리 {htyp}')
    if name!='—' and name.strip()!=hn: issues.append(f'이름 "{name}"≠머리 "{hn}"')
    if hrec and re.sub(r'\s','',hrec)!=re.sub(r'\s','',recname): issues.append(f'기록이름 "{recname}"≠머리 "{hrec}"')
    if not hrec: issues.append(f'머리에 기록 이름 없음(머리 이름 "{hn}")')
    if issues: print(lab,'|',' ; '.join(issues))
print('rows',n)
