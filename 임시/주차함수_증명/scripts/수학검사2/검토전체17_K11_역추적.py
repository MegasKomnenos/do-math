import re,io,sys,collections
root=r'C:\math\임시\주차함수_증명'
def blocks(fname):
    L=io.open(root+r'\장v2\%s.md'%fname,encoding='utf-8').read().split('\n')
    cur='(머리말)';sec='';res=collections.OrderedDict()
    for i,l in enumerate(L,1):
        m=re.match(r'### (\S+)',l)
        if m: sec=m.group(1); cur='%s절 첫머리'%sec
        m=re.search(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+:[^}]+)\}\}',l)
        if m: cur='%s {{%s}}'%(m.group(1),m.group(2))
        # heuristic: a non-head paragraph after a proof end '∎' is 준비 문단
        res.setdefault(cur,[]).append((i,l))
    return res
B9=blocks('장9'); B10=blocks('장10'); B7=blocks('장7B')
t=io.open(root+r'\장v2\장11.md',encoding='utf-8').read().split('\n')
inputs=[]
for l in t[64:130]:
    if l.startswith('| ') and not l.startswith('| 입력') and not l.startswith('|---'):
        c=[x.strip() for x in l.strip().strip('|').split(' | ')]
        labs=re.findall(r'\{\{(\d+:[^}]+)\}\}',c[0])
        inputs.append((c[0][:60],labs))
out=io.open(root+r'\scripts\수학검사2\_K11_역추적_out.txt','w',encoding='utf-8')
def where(lab,B,name):
    r=[]
    for k,ls in B.items():
        hit=[i for i,l in ls if '{{%s}}'%lab in l]
        if hit: r.append('%s[%s L%s]'%(name,k,','.join(map(str,hit[:4]))))
    return r
for title,labs in inputs:
    out.write('\n### %s\n'%title)
    for lab in labs:
        w=where(lab,B9,'9')+where(lab,B10,'10')
        w7=[x for x in where(lab,B7,'7B') if 'old-6-22' in x]
        out.write('  %s:\n'%lab)
        for x in w+w7: out.write('     %s\n'%x)
out.close()
