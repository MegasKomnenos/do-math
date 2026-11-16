import re,glob,io,sys
root=r'C:\math\임시\주차함수_증명'
files=['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11','부록A','부록B','부록C']+['부록D_장%s'%x for x in ['2','3','4','5A','5B','6','7A','7B','8','9','10']]
lines={}
for f in files:
    lines[f]=io.open(root+r'\장v2\%s.md'%f,encoding='utf-8').read().split('\n')
heads={}  # label -> (file,line)
for f in files:
    for i,l in enumerate(lines[f],1):
        for m in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+:[^}]+)\}\}',l):
            heads.setdefault(m.group(2),(f,i))
        m=re.match(r'### D\.\{\{D:([^}]+)\}\}',l)
        if m: heads.setdefault('D:'+m.group(1),(f,i))
mode=sys.argv[1]
out=io.open(root+r'\scripts\수학검사2\_K11_인용대조_out.txt','w',encoding='utf-8')
if mode=='labels':
    for f in ['장11','부록A','부록B','부록C']:
        for i,l in enumerate(lines[f],1):
            for m in re.finditer(r'\{\{([^}]+)\}\}',l):
                lab=m.group(1)
                if lab.startswith('D:'):
                    if lab not in heads: out.write('%s L%d missing %s\n'%(f,i,lab))
                elif lab not in heads: out.write('%s L%d missing %s\n'%(f,i,lab))
    out.write('done\n')
elif mode=='grep':
    pat=sys.argv[2]
    for f in files:
        cur=None;sec=''
        for i,l in enumerate(lines[f],1):
            m=re.match(r'### (\S+)',l)
            if m: sec=m.group(1); cur=None
            m=re.search(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+:[^}]+)\}\}',l)
            if m: cur=m.group(1)+' '+m.group(2)
            m=re.match(r'### D\.\{\{D:([^}]+)\}\}',l)
            if m: cur='D:'+m.group(1)
            if re.search(pat,l):
                out.write('%s L%d [%s | %s] %s\n'%(f,i,sec,cur,re.sub(r'\s+',' ',l)[:int(sys.argv[3]) if len(sys.argv)>3 else 200]))
out.close()
