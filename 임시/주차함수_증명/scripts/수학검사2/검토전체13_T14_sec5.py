# T14: 장부 5절 대 1.2 정합 — (가) 처음 정의 기호 (나) 여유 글자 충돌 (다) 11.2 표의 부록 D 열 대 의존지도
import re, os
root=r"C:\math\임시\주차함수_증명"
lines=open(os.path.join(root,"장부_v2.md"),encoding='utf-8').read().split('\n')
sec=None; rows12=[]; rows11=[]
for i,l in enumerate(lines,1):
    if l.startswith('### 1.1'): sec='1.1'
    elif l.startswith('### 1.2'): sec='1.2'
    elif l.startswith('### 1.3'): sec=None
    if sec and l.startswith('| $'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        if sec=='1.1': rows11.append((i,c[0]))
        else: rows12.append((i,c[0],c[1],c[3],c[4]))
def chs(s):
    if '전 장' in s: return set(range(1,12))
    return set(int(x) for x in re.findall(r'\b(\d{1,2})\b',s) if 1<=int(x)<=11)
def defch(s):
    return set(int(x) for x in re.findall(r'(\d{1,2})\.\d',s))
rows5={}
in5=False
for i,l in enumerate(lines,1):
    if l.startswith('## 5.'): in5=True; continue
    if l.startswith('## 6.'): break
    if in5 and re.match(r'\| \d+ \|',l):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        rows5[int(c[0])]=(i,c[1],c[2],c[3])
def items(col):
    return re.findall(r'\$[^$]+\$',col)
print("== (가) 1.2 정의 절의 장 vs 5절 둘째 열")
for i,latex,font,defsec,used in rows12:
    parts=[p.strip() for p in latex.strip('$').split(',')]
    for ch in defch(defsec):
        if ch not in rows5: continue
        col=rows5[ch][1].replace(' ','')
        if not any(p.replace(' ','') in col for p in parts):
            print(f"L{i} {latex} 정의 절={defsec}: 5절 {ch}장 둘째 열에 없음")
all12=" ".join(x[1].replace(' ','') for x in rows12)
for ch,(i,col,words,free) in rows5.items():
    for it in items(col):
        k=it.replace(' ','').strip('$')
        if k not in all12: print(f"L{i} 5절 {ch}장 둘째 열 {it}: 1.2에 같은 글자열 없음")
def base_font(latex):
    s=latex.strip('$').split(',')[0].strip()
    s=re.sub(r'^\(','',s)
    m=re.match(r'\\(mathcal|mathfrak|mathsf|mathrm|mathbb)\s*\{?([A-Za-z]+)',s)
    if m: return (m.group(2),m.group(1))
    m=re.match(r'\\(bar|hat|tilde)\s*\{?(\\?[A-Za-z]+)',s)
    if m: s=m.group(2)
    m=re.match(r'(\\[A-Za-z]+|[A-Za-z])',s)
    return (m.group(1),'it') if m else None
glob_by_ch={c:set() for c in range(1,12)}
ch1=set()
for i,latex,font,defsec,used in rows12:
    bf=base_font(latex)
    if not bf: continue
    for ch in chs(used): glob_by_ch[ch].add(bf)
    if 1 in defch(defsec): ch1.add(bf)
var11=set(base_font(x[1]) for x in rows11)
reserved={('a','it'),('b','it'),('c','it'),('e','it'),('h','it'),('\\delta','it'),('o','it'),('O','it'),('\\varpi','it'),('l','it'),('P','it'),('Q','it'),('W','it'),('X','it'),('\\Delta','it'),('\\Sigma','it')}
print("== (나) 여유 글자 충돌")
for ch,(i,col,words,free) in rows5.items():
    bad=[]
    for it in re.findall(r'\$([^$]+)\$',free):
        bf=base_font(it)
        if not bf: continue
        src=[]
        if bf in glob_by_ch[ch]: src.append('장 전역')
        if bf in ch1: src.append('1장 전역')
        if bf in var11: src.append('1.1 변수')
        if bf in reserved: src.append('예약')
        if src: bad.append(f"{it}({','.join(src)})")
    if bad: print(f"L{i} {ch}장: "+", ".join(bad))
print("== (다) 11.2 표 부록 D 열 vs 의존지도 1절")
dep={}
for l in open(os.path.join(root,"의존지도_v2.md"),encoding='utf-8'):
    if l.startswith('## 2'): break
    if l.startswith('| `{{'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        dep[c[0].strip('`')]=set(re.findall(r'\{\{D:[^}]+\}\}',c[8]))
t11=open(os.path.join(root,"장v2","장11.md"),encoding='utf-8').read().split('\n')
exp={}
for l in t11:
    if l.startswith('| 부록 D.{{D:'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        d=re.search(r'\{\{D:[^}]+\}\}',c[0]).group(0)
        for lab in re.findall(r'\{\{\d+:[^}]+\}\}',c[1]): exp.setdefault(lab,set()).add(d)
for lab,ds in exp.items():
    if lab not in dep: print("지도에 없음",lab); continue
    if dep[lab]!=ds: print(f"{lab}: 11.2={sorted(ds)} 지도={sorted(dep[lab])}")
for lab,ds in dep.items():
    if ds and lab not in exp: print(f"{lab}: 지도에는 {sorted(ds)} 있으나 11.2 표에 없음")
