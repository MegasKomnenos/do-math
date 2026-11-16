# 의존지도 1절의 「입력: 이 글의 다른 진술」(머리 줄 인용 + 본문 인용)을 현행 장 파일에서 다시 만들어 대조
import re,glob,os,io
base=r"C:\math\임시\주차함수_증명"
order={'장1.md':1,'장2.md':2,'장3.md':3,'장4.md':4,'장5A.md':5,'장5B.md':5,'장6.md':6,'장7A.md':7,'장7B.md':7,'장8.md':8,'장9.md':9,'장10.md':10,'장11.md':11}
files=sorted(glob.glob(os.path.join(base,"장v2","장*.md")),key=lambda f:(order[os.path.basename(f)],os.path.basename(f)))
HEAD=re.compile(r'^\*\*(정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}')
PROOF=re.compile(r'^\*\*(?:정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}(?:\([^)]*\))?의 증명')
headline={}; body={}
for f in files:
    lines=io.open(f,encoding='utf-8').read().split('\n')
    cur=None
    for line in lines:
        pm=PROOF.match(line)
        hm=HEAD.match(line)
        if pm:
            cur=pm.group(1); body.setdefault(cur,[]).append(line); continue
        if hm:
            cur=hm.group(2); headline[cur]=line; body.setdefault(cur,[]); continue
        if cur: body[cur].append(line)
dep=io.open(os.path.join(base,"의존지도_v2.md"),encoding='utf-8').read().split('\n')
for i,l in enumerate(dep,1):
    if i>480: break
    cells=[x.strip() for x in l.strip().strip('|').split('|')]
    if len(cells)<10: continue
    m=re.match(r'`\{\{([^}]+)\}\}`',cells[0])
    if not m: continue
    lab=m.group(1)
    if lab not in headline: continue
    col=cells[5]
    parts=col.split('본문 인용:')
    dh=set(re.findall(r'`\{\{([^}]+)\}\}`',parts[0]))
    db=set(re.findall(r'`\{\{([^}]+)\}\}`',parts[1])) if len(parts)>1 else set()
    hh=set(c for c in re.findall(r'\{\{([^}]+)\}\}',headline[lab]) if c!=lab and not c.startswith('D:'))
    bb=set(c for c in re.findall(r'\{\{([^}]+)\}\}','\n'.join(body[lab])) if c!=lab and not c.startswith('D:'))-hh
    if hh!=dh: print("머리줄",lab,"| 현행-지도:",sorted(hh-dh),"| 지도-현행:",sorted(dh-hh))
    if bb!=db: print("본문",lab,"| 현행-지도:",sorted(bb-db),"| 지도-현행:",sorted(db-bb))
