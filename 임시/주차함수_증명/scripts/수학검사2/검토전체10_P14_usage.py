# 장부 1.1·1.2 「쓰이는 장」을 장 파일에서 다시 센다(후보 검출; 판단은 손으로).
import re,glob,os,io,sys
base=r"C:\math\임시\주차함수_증명"
order={'장1.md':1,'장2.md':2,'장3.md':3,'장4.md':4,'장5A.md':5,'장5B.md':5,'장6.md':6,'장7A.md':7,'장7B.md':7,'장8.md':8,'장9.md':9,'장10.md':10,'장11.md':11}
def norm(s):
    s=re.sub(r'\s+','',s)
    s=s.replace('{','').replace('}','')
    s=s.replace('\prime',"'")
    s=s.replace('^\ast','^*').replace('_\ast','_*')
    s=s.replace('\le(','_\le(')  # no-op safety
    return s
chap={}
for f in glob.glob(os.path.join(base,"장v2","장*.md")):
    ch=order[os.path.basename(f)]
    chap.setdefault(ch,'')
    chap[ch]+=norm(io.open(f,encoding='utf-8').read())
jb=io.open(os.path.join(base,"장부_v2.md"),encoding='utf-8').read().split('\n')
def parse_rows(lo,hi,symcol,chcol):
    rows=[]
    for i in range(lo,hi):
        l=jb[i]
        if not l.startswith('| $') : continue
        cells=[c.strip() for c in l.strip().strip('|').split('|')]
        rows.append((i+1,cells[symcol],cells[chcol]))
    return rows
def keys_of(sym):
    # split at top-level commas
    parts=[]; d=0; cur=''
    for ch in sym:
        if ch in '({[': d+=1
        if ch in ')}]': d-=1
        if ch==',' and d==0: parts.append(cur); cur=''
        else: cur+=ch
    parts.append(cur)
    out=[]
    for p in parts:
        p=p.strip().strip('$').strip()
        p=re.sub(r'\(.*$','',p)          # drop arguments
        p=norm(p)
        p=p.replace(':=','').strip()
        if p: out.append(p)
    return out
def chapters_with(key):
    found=[]
    for ch in sorted(chap):
        if key in chap[ch]: found.append(ch)
    return found
def prefix(key):
    m=re.match(r'^(\[A-Za-z]+(?:\?[A-Za-z])?|[A-Za-z])',key)
    # base letter incl font command, e.g. \mathfrakR or \kappa or A
    m=re.match(r'^((?:\math[a-z]+|\mathsf|\mathrm)?\?[A-Za-z]+|[A-Za-z])',key)
    return m.group(1) if m else key
for lo,hi,sc,cc,title in [(27,42,0,2,'1.1'),(48,340,0,4,'1.2')]:
    print("=====",title)
    for ln,sym,chs in parse_rows(lo,hi,sc,cc):
        want=chs
        ks=keys_of(sym)
        res=[]
        for k in ks:
            res.append((k,chapters_with(k)))
        wantset=set()
        if '전 장' in want: wantset=set(range(1,12))
        else:
            wantset=set(int(x) for x in re.findall(r'\d+',want))
        allfound=set()
        for k,f in res: allfound|=set(f)
        flag=''
        if allfound-wantset: flag+=' 추가후보:'+str(sorted(allfound-wantset))
        if wantset-allfound: flag+=' 미검출:'+str(sorted(wantset-allfound))
        if flag:
            print(ln,sym[:60],'| 장부:',want,'|',[(k,f) for k,f in res],flag)
