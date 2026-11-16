# H14: 대응표(라벨·종류·이름·현재 번호·절)를 장 파일의 머리와 대조한다.
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의|관찰|주의|예|가정|알고리즘)\s+\{\{(\d+):([^}]+)\}\}(?!의)\s*(.*?)\*\*')
sec_re = re.compile(r'^(#+)\s+(\d+\.\d+)\b')
heads = {}
order = []
counters = {}
for f in files:
    cur = None
    with open(os.path.join(root,"장v2",f),encoding='utf-8') as fh:
        for ln,line in enumerate(fh,1):
            m = sec_re.match(line)
            if m: cur = m.group(2); continue
            m = head_re.match(line)
            if m:
                kind, ch, lab, rest = m.groups()
                counters[ch] = counters.get(ch,0)+1
                name = None
                r=rest.strip()
                if r.startswith('('):
                    depth=0
                    for i,c in enumerate(r):
                        if c=='(': depth+=1
                        elif c==')':
                            depth-=1
                            if depth==0: name=r[1:i].strip(); break
                heads[f"{ch}:{lab}"] = dict(file=f,ln=ln,kind=kind,num=f"{ch}.{counters[ch]}",sec=cur,name=name,rest=rest.strip())
                order.append(f"{ch}:{lab}")
# 대응표 파싱
rows=[]
with open(os.path.join(root,"대조v2","라벨_번호_대응표_1114.md"),encoding='utf-8') as fh:
    for ln,line in enumerate(fh,1):
        if line.startswith('| `{{'):
            cells=[c.strip() for c in line.strip().strip('|').split('|')]
            lab=cells[0].strip('`').strip('{}')
            rows.append((ln,lab,cells))
print("장 파일 머리 수:",len(heads),"대응표 행 수:",len(rows))
seen=set()
for ln,lab,cells in rows:
    seen.add(lab)
    h=heads.get(lab)
    if not h:
        print(f"[대응표 {ln}] 장 파일에 없음: {lab} | {cells}")
        continue
    kind,name,num,sec=cells[1],cells[2],cells[3],cells[5] if len(cells)>5 else '?'
    probs=[]
    if kind!=h['kind']: probs.append(f"종류 표={kind} 파일={h['kind']}")
    if num!=h['num']: probs.append(f"번호 표={num} 파일={h['num']}")
    if sec!=h['sec']: probs.append(f"절 표={sec} 파일={h['sec']}")
    hn = h['name'] or '—'
    if name.replace(' ','')!=hn.replace(' ',''):
        probs.append(f"이름 표={name!r} 파일={hn!r}")
    if probs: print(f"[대응표 {ln}] {lab} ({h['file']}:{h['ln']}): "+"; ".join(probs))
for lab in order:
    if lab not in seen: print("대응표에 없음:",lab,heads[lab]['file'],heads[lab]['ln'],heads[lab]['num'])
