# T14: 장부 1.1·1.2 「쓰이는 장」 열 대 장 파일 실제 출현 대조 (자리 찾기용)
import re, os
root = r"C:\math\임시\주차함수_증명"
chfiles = {1:["장1.md"],2:["장2.md"],3:["장3.md"],4:["장4.md"],5:["장5A.md","장5B.md"],6:["장6.md"],7:["장7A.md","장7B.md"],8:["장8.md"],9:["장9.md"],10:["장10.md"],11:["장11.md"]}
text = {c:"\n".join(open(os.path.join(root,"장v2",f),encoding='utf-8').read() for f in fs) for c,fs in chfiles.items()}
lines = open(os.path.join(root,"장부_v2.md"),encoding='utf-8').read().split('\n')
rows=[]
sec=None
for i,l in enumerate(lines,1):
    if l.startswith('### 1.1'): sec='1.1'
    elif l.startswith('### 1.2'): sec='1.2'
    elif l.startswith('### 1.3'): break
    if sec and l.startswith('| $'):
        cells=[c.strip() for c in l.strip().strip('|').split('|')]
        if sec=='1.1': rows.append((i,cells[0],cells[2]))
        else: rows.append((i,cells[0],cells[4]))
def parse_ch(s):
    if '전 장' in s: return set(range(1,12))
    return set(int(x) for x in re.findall(r'\b(\d{1,2})\b',s) if 1<=int(x)<=11)
FONTS=['mathcal','mathfrak','mathsf','mathrm','mathbb','mathscr','mathbf','operatorname']
def bare(letter):
    lb=''.join('(?<!\\\\'+f+' )(?<!\\\\'+f+'\\{)' for f in FONTS)
    return lb+r'(?<![A-Za-z\\])'+re.escape(letter)+r'(?![A-Za-z])'
def pattern(latex):
    s=latex.strip().strip('$')
    s=s.split(',')[0].strip().strip('$')
    s=re.sub(r':=.*','',s).strip()
    m=re.match(r'^\\(mathrm|mathcal|mathfrak|mathsf|mathbb|operatorname)\s*(\{[^}]*\}|[A-Za-z])',s)
    if m:
        cmd,arg=m.group(1),m.group(2)
        arg=arg.strip('{}')
        pat='\\\\'+cmd+r'\s*\{?'+re.escape(arg)+r'\}?'
        rest=s[m.end():]
        md=re.match(r'^(\^\{[^}]*\}|\^\\?[A-Za-z]+|_\{[^}]*\}|_\\?[A-Za-z0-9]+)',rest)
        if md and ('mathrm' in md.group(0) or '\\' in md.group(0)):
            pat+=re.escape(md.group(0))
        return pat, 'font'
    m=re.match(r'^(\\[A-Za-z]+|[A-Za-z])(.*)$',s)
    if not m: return None,None
    base,rest=m.group(1),m.group(2)
    if rest.startswith('^'):
        md=re.match(r'^\^(\{[^}]*\}|\\?[A-Za-z0-9]+|.)',rest)
        return re.escape(base+md.group(0)), 'deco'
    if rest.startswith('_'):
        return re.escape(base)+r'_', 'sub'
    if rest.startswith('('):
        if base.startswith('\\'): return re.escape(base)+r'\s*\(', 'func'
        return bare(base)+r'\s*\(', 'func'
    if base.startswith('\\'): return bare(base), 'greek'
    return bare(base), 'bare'
out=[]
for i,latex,chs in rows:
    listed=parse_ch(chs)
    pat,kind=pattern(latex)
    if not pat: out.append(f"L{i} {latex}: 패턴 없음"); continue
    found=set(c for c,t in text.items() if re.search(pat,t))
    if found!=listed:
        out.append(f"L{i} {latex} [{kind}] 장부={sorted(listed)} 실제={sorted(found)} | 장부에만={sorted(listed-found)} 실제에만={sorted(found-listed)}")
print(len(rows),"rows;",len(out),"mismatch")
print("\n".join(out))
