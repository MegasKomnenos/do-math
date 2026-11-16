import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
H={}
for line in open('대조v2/수학검사2/_J11_heads.tsv',encoding='utf-8'):
    f,i,sec,typ,lab,mark=line.rstrip('\n').split('\t')
    H[lab]=(typ,sec,mark)
def deps(lab):
    mark=H[lab][2]
    return re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',mark)
def grade(lab):
    mark=H[lab][2]
    g=[]
    if '계산' in mark:
        for m in re.finditer(r'계산 (?:증거|보조)\(([^)]*)\)',mark): g.append(m.group(1))
    return g
def closure(root):
    seen=set(); st=[root]
    while st:
        x=st.pop()
        if x in seen: continue
        seen.add(x)
        for d in deps(x):
            if d not in H: print('  !! unknown dep',d,'from',x); continue
            st.append(d)
    return seen
C1=closure('9:old-7-46'); C2=closure('10:old-8-37')
comp1={x for x in C1 if grade(x)}; comp2={x for x in C2 if grade(x)}
lit={x for x in C1|C2 if '문헌 인용' in H[x][2]}
print('closure sizes',len(C1),len(C2),' 문헌 인용 in closures:',lit)
# parse 11.3 tables
txt=open('장v2/장11.md',encoding='utf-8').read().split('\n')
tab=[]; which=None
for i,l in enumerate(txt,1):
    if l.startswith('**공유 입력.**'): which='S'
    elif l.startswith('**첫째 증명의 고유'): which='1'
    elif l.startswith('**둘째 증명의 고유'): which='2'
    elif l.startswith('### 11.4'): which=None
    if which and l.startswith('| ') and not l.startswith('| 입력') and not l.startswith('|---'):
        cells=[c.strip() for c in l.strip().strip('|').split(' | ')]
        tab.append((which,i,cells))
listed={}
for w,i,cells in tab:
    inputs=re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',cells[0])
    comp=re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',cells[1])
    for c in comp:
        listed.setdefault(c,[]).append((w,i))
    # row-level: inputs must be in right closure
    for x in inputs:
        inC1=x in C1; inC2=x in C2
        exp={'S':(True,True),'1':(True,False),'2':(False,True)}[w]
        if (inC1,inC2)!=exp:
            print(f'L{i} [{w}] 입력 {x}: 첫째폐포={inC1} 둘째폐포={inC2} (표의 배치와 다름)')
comp_all=comp1|comp2
print('\n== 11.3 계산 진술 열에 적혔으나 두 증명의 의존 폐포에 없음:')
for c in listed:
    if c not in comp_all: print('  ',c, listed[c], 'grade',grade(c) if c in H else '?')
print('== 폐포의 계산 진술인데 11.3 표에 없음:')
for c in sorted(comp_all):
    if c not in listed: print('  ',c, H[c][1], grade(c), 'in1' if c in comp1 else '', 'in2' if c in comp2 else '')
print('== 계산 진술의 배치 확인(공유/고유):')
for c in sorted(listed):
    if c not in H: continue
    ws={w for w,i in listed[c]}
    inC1=c in comp1; inC2=c in comp2
    exp = 'S' if (inC1 and inC2) else ('1' if inC1 else ('2' if inC2 else '-'))
    if ws!={exp}: print(f'   {c}: 표={ws} 실제={exp} (첫째={inC1}, 둘째={inC2}) grade={grade(c)}')
# grade text check
print('== 등급 글귀 대조:')
for w,i,cells in tab:
    col=cells[1]
    for part in re.split(r';',col):
        labs=re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',part)
        m=re.search(r':\s*([^(]*)$',part.strip())
        if not labs or not m: continue
        gtxt=re.sub(r'\(.*?\)','',m.group(1)).strip()
        for L in labs:
            if L not in H: continue
            g='; '.join(grade(L))
            if gtxt and set(re.split(r'[,·]\s*',gtxt))!=set(re.split(r',\s*',g)):
                print(f'   L{i} {L}: 표 "{gtxt}" / 머리 "{g}"')
