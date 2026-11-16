# 의존지도 1절·대응표를 현행 장 파일 머리와 대조
import re,glob,os,io
base=r"C:\math\임시\주차함수_증명"
order={'장1.md':1,'장2.md':2,'장3.md':3,'장4.md':4,'장5A.md':5,'장5B.md':5,'장6.md':6,'장7A.md':7,'장7B.md':7,'장8.md':8,'장9.md':9,'장10.md':10,'장11.md':11}
files=sorted(glob.glob(os.path.join(base,"장v2","장*.md")),key=lambda f:(order[os.path.basename(f)],os.path.basename(f)))
heads=[]  # (lab,kind,rest,sec,file,lineno)
for f in files:
    cur=None
    for i,line in enumerate(io.open(f,encoding='utf-8'),1):
        m=re.match(r'^#{2,4} (\d+(?:\.\d+)*)',line)
        if m: cur=m.group(1); continue
        m=re.match(r'^\*\*(정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}(.*?)\*\*',line)
        if not m:
            m=re.match(r'^\*\*(정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}(.*)$',line)
        if m and '의 증명' not in m.group(3)[:40]:
            heads.append((m.group(2),m.group(1),m.group(3),cur,os.path.basename(f),i))
# detect duplicates (restatements)
from collections import Counter
c=Counter(h[0] for h in heads)
print("중복 머리:",[(k,v) for k,v in c.items() if v>1])
# numbering: per chapter sequential, first occurrence only
seen=set(); num={}
cnt={}
for h in heads:
    if h[0] in seen: continue
    seen.add(h[0]); ch=order[h[4]]
    cnt[ch]=cnt.get(ch,0)+1
    num[h[0]]=f"{ch}.{cnt[ch]}"
# 대응표
tab=io.open(os.path.join(base,"대조v2","라벨_번호_대응표_1114.md"),encoding='utf-8').read().split('\n')
tl={}
for i,l in enumerate(tab,1):
    cells=[x.strip() for x in l.strip().strip('|').split('|')]
    if len(cells)<6: continue
    m=re.match(r'`\{\{([^}]+)\}\}`',cells[0])
    if m: tl[m.group(1)]=(i,cells[1],cells[2],cells[3],cells[4],cells[5])
print("== 대응표 번호/절/종류/이름 불일치")
hd={h[0]:h for h in heads if h[0] in num}
first={}
for h in heads:
    first.setdefault(h[0],h)
def paren(rest):
    rest=rest.strip()
    if not rest.startswith('('): return '—'
    d=0
    for j,ch in enumerate(rest):
        if ch=='(':d+=1
        elif ch==')':
            d-=1
            if d==0: return rest[1:j]
for lab,v in tl.items():
    if lab not in num: print("대응표에 있으나 머리 없음",lab); continue
    h=first[lab]
    if v[3]!=num[lab]: print("번호",lab,"표:",v[3],"현행:",num[lab])
    if v[5]!=h[3] and not h[3].startswith(v[5]+'.'): print("절",lab,"표:",v[5],"현행:",h[3])
    if v[1]!=h[1]: print("종류",lab,v[1],h[1])
    if v[2]!=paren(h[2]): print("이름",lab,"|",v[2],"|",paren(h[2]))
for lab in num:
    if lab not in tl: print("머리에 있으나 대응표에 없음",lab)
# 뺌 rows still existing?
for i,l in enumerate(tab,1):
    m=re.match(r'\| `\(([^)]+)\)`',l)
    if m and m.group(1) in num: print("뺌 행인데 머리 있음",m.group(1))
# 의존지도 1절
dep=io.open(os.path.join(base,"의존지도_v2.md"),encoding='utf-8').read().split('\n')
dl={}
for i,l in enumerate(dep,1):
    if i>480: break
    cells=[x.strip() for x in l.strip().strip('|').split('|')]
    if len(cells)<10: continue
    m=re.match(r'`\{\{([^}]+)\}\}`',cells[0])
    if m: dl[m.group(1)]=(i,cells)
print("== 의존지도 1절 대조")
for lab in num:
    if lab not in dl: print("의존지도에 없음",lab)
for lab,(i,cells) in dl.items():
    if lab not in num: print("의존지도에 있으나 머리 없음",lab,i); continue
    h=first[lab]
    # status
    rest=h[2]
    mb=re.search(r'\[([^\[\]]*)\]\.?\s*$',rest.strip())
    if mb:
        st=mb.group(1).split(';')[0].strip()
    else: st='정의' if h[1]=='정의' else '?'
    if h[1]=='정의' and not mb: st='정의'
    want=cells[4]
    if st!=want and not (h[1]=='정의' and want=='정의'):
        print("지위",lab,"| 지도:",want,"| 머리:",st)
    if cells[1]!=h[3] and not h[3].startswith(cells[1]+'.'): print("절",lab,cells[1],h[3])
    # head-line label citations
    cites=re.findall(r'\{\{([^}]+)\}\}',rest)
    cites=[c for c in cites if c!=lab]
    col=cells[5]
    headpart=col.split('본문 인용:')[0]
    dcites=re.findall(r'`\{\{([^}]+)\}\}`',headpart)
    if set(cites)!=set(dcites): print("머리 인용",lab,"| 머리:",cites,"| 지도:",dcites)
    # record ids
    ids=set(re.findall(r'\br[0-9a-f]{7}\b',mb.group(1).split(';',1)[1] if mb and ';' in mb.group(1) else ''))
    dids=set(re.findall(r'\br[0-9a-f]{7}\b',cells[6]))
    if ids and not ids<=dids: print("기록",lab,"| 머리:",sorted(ids),"| 지도:",sorted(dids))
