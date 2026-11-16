import re,io,glob,sys
root=r'C:\math\임시\주차함수_증명'
heads={}
for f in glob.glob(root+r'\장v2\장*.md'):
    for i,l in enumerate(io.open(f,encoding='utf-8'),1):
        for m in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+:[^}]+)\}\}\s*(\((.*?)\))?\s*(\[[^\]]*\])?\.\*\*',l):
            heads.setdefault(m.group(2),(f.split(chr(92))[-1],i,m.group(1),m.group(4) or '',m.group(5) or ''))
C=io.open(root+r'\장v2\부록C.md',encoding='utf-8').read().split('\n')
out=io.open(root+r'\scripts\수학검사2\_K11_부록C대조_out.txt','w',encoding='utf-8')
# names table lines 146-437
n=0
for ln in range(146,438):
    l=C[ln-1]
    if not l.startswith('| 기록') and not l.startswith('| ['): continue
    c=[x.strip() for x in l.strip().strip('|').split(' | ')]
    if len(c)<3: continue
    recname,stmt,ourname=c[0],c[1],c[2]
    labs=re.findall(r'\{\{(\d+:[^}]+)\}\}',stmt)
    kinds=re.findall(r'(정리|명제|보조정리|따름정리|정의)',stmt)
    for lab in labs:
        h=heads.get(lab)
        if not h: out.write('C L%d: label %s NOT FOUND\n'%(ln,lab)); n+=1; continue
        paren=h[3]
        issues=[]
        # record ids
        for rid in re.findall(r'r[0-9a-f]{7}',recname):
            if rid not in paren and rid not in h[4]: issues.append('rid %s not in head'%rid)
        # record name tokens: take text after '의 ' in recname segments
        for seg in recname.split(', '):
            m=re.search(r'\]의 (.+)$',seg)
            if m:
                nm=m.group(1).strip()
                if nm not in paren: issues.append('recname [%s] not in head paren [%s]'%(nm,paren[:120]))
        # our name
        ourhead=paren.split(';')[0].strip()
        if ourname and ourname!='—' and ourname!=ourhead: issues.append('ourname [%s] vs head [%s]'%(ourname,ourhead))
        if kinds and h[2] not in kinds: issues.append('kind %s vs head %s'%(kinds,h[2]))
        if issues:
            n+=1; out.write('C L%d %s: %s\n'%(ln,lab,'; '.join(issues)))
out.write('names issues: %d\n'%n)
# which heads with '기록 [r' in paren are NOT in C names table?
Cnames=' '.join(C[145:437])
miss=0
for lab,h in heads.items():
    if '기록 [' in h[3] and ('{{%s}}'%lab) not in Cnames:
        miss+=1; out.write('HEAD not in C: %s %s (%s)\n'%(h[2],lab,h[3][:100]))
out.write('heads with record names missing from C: %d\n'%miss)
out.close()
