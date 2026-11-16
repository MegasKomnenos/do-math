# -*- coding: utf-8 -*-
"""I14: (1) 5절 「처음 정의하는 전역 기호」 vs 1.2 정의 절, (2) 5절 여유 글자와 그 장 전역 기호의 충돌, (3) 1.2 정의 절에 기호가 실제로 나타나는가·정의 절 앞 사용."""
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
L = open(os.path.join(ROOT,'장부_v2.md'),encoding='utf-8').read().split('\n')
files = {'1':['장1'],'2':['장2'],'3':['장3'],'4':['장4'],'5':['장5A','장5B'],'6':['장6'],'7':['장7A','장7B'],'8':['장8'],'9':['장9'],'10':['장10'],'11':['장11']}
sec_re = re.compile(r'^###\s+(\d+\.\d+)')
sectext = {}   # sec -> text
order = []
for c,fs in files.items():
    for f in fs:
        sec = c+'.0'
        for l in open(os.path.join(ROOT,'장v2',f+'.md'),encoding='utf-8'):
            m = sec_re.match(l)
            if m: sec = m.group(1)
            if sec not in sectext: sectext[sec]=''; order.append(sec)
            sectext[sec] += l
def seckey(s): a,b=s.split('.'); return (int(a),int(b))
norm = lambda s: re.sub(r'\s+','',s)
# 1.2 rows
rows12 = []
for i in range(49,342):
    l = L[i-1]
    if not (l.startswith('| $') or l.startswith('| (')): continue
    cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
    rows12.append((i, cells))
print("=== (1) 5절 「이 장이 처음 정의하는 전역 기호」 vs 1.2 정의 절")
def_by_ch = {}
for i,c in rows12:
    secs = re.findall(r'\d+\.\d+', c[3])
    chs = sorted({s.split('.')[0] for s in secs}, key=int)
    for ch in chs: def_by_ch.setdefault(ch,set()).add(norm(c[0]))
for i in range(1181,1192):
    l = L[i-1]
    m = re.match(r'^\| (\d+) \| ([^|]*) \|', l)
    if not m: continue
    ch = m.group(1)
    listed = {norm(x) for x in m.group(2).split('; ') if x.strip() and x.strip()!='없음'}
    exp = def_by_ch.get(ch,set())
    # 3장 행은 국소 글자도 적어 두었으므로 1.2 glyph만 비교
    only5 = [x for x in listed if x not in exp and x.startswith('$')]
    only12 = [x for x in exp if x not in listed]
    if only5 or only12:
        print(f"  장{ch}: 5절에만: {only5}\n        1.2에만(정의 절이 이 장): {only12}")

print("\n=== (2) 5절 여유 글자가 그 장에서 쓰이는 전역 기호·1장 전역·1.1 변수·예약 글자와 (바탕 글자, 글자체) 충돌")
def family(g):
    g = g.strip().strip('$')
    m = re.match(r'^\\(mathcal|mathfrak|mathsf|mathrm|mathbb|bar|hat|tilde)\s*(\{[^}]*\}|[A-Za-z])', g)
    if m:
        font = m.group(1); base = m.group(2).strip('{}')
        if font in ('bar','hat','tilde'):
            inner = g[m.end(0)-len(m.group(2)):]
            return ('italic', base)
        return (font, base)
    m = re.match(r'^(\\[A-Za-z]+|[A-Za-z])', g)
    if m: return ('italic', m.group(1))
    return None
used_by_ch = {str(c):set() for c in range(1,12)}
for i,c in rows12:
    glyphs = [g for gl in re.findall(r'\$([^$]+)\$', c[0]) for g in re.split(r',\s*(?=[\\A-Za-z(])', gl)]
    fams = {family(g) for g in glyphs if family(g)}
    chs = set(files.keys()) if '전 장' in c[4] else {x.strip() for x in c[4].split(',') if x.strip().isdigit()}
    for s in re.findall(r'\d+\.\d+', c[3]): chs.add(s.split('.')[0])
    for ch in chs:
        if ch in used_by_ch: used_by_ch[ch] |= fams
ch1 = set(used_by_ch['1'])
for i,c in rows12:
    if any(s.startswith('1.') for s in re.findall(r'\d+\.\d+', c[3])):
        for g in re.findall(r'\$([^$]+)\$', c[0]):
            for gg in re.split(r',\s*(?=[\\A-Za-z(])', g):
                if family(gg): ch1.add(family(gg))
vars11 = {('italic',x) for x in ['n','m','t','N','k','\\ell','y','Y','i','j','u','v','r','\\nu','d','q']}
reserved = {('italic',x) for x in ['a','b','c','e','h','\\delta','o','O','\\varpi','l','d','x','t','m','N','P','Q','W','X']} | {('italic','\\Delta'),('italic','\\Sigma')}
for i in range(1181,1192):
    l = L[i-1]
    m = re.match(r'^\| (\d+) \| [^|]* \| [^|]* \| ([^|]*) \|', l)
    if not m: continue
    ch = m.group(1)
    free = [family(g) for g in re.findall(r'\$([^$]+)\$', m.group(2))]
    bad = [f for f in free if f in used_by_ch[ch] or f in ch1 or f in vars11]
    if bad: print(f"  장{ch} 여유 글자 가운데 충돌: {bad}")

print("\n=== (3) 1.2 기호가 선언된 정의 절에 나타나는가 / 정의 절보다 앞선 장(1장 제외)에 나타나는가")
B = chr(92)
def stem_regex(g):
    g=g.strip().strip('$').strip()
    if g.startswith('('+B+'mathrm G)_d'): return B+'('+B+B+'mathrm G'+B+')_d', False
    if g.startswith('('+B+'star)'): return B+'('+B+B+'star'+B+')', False
    m=re.match(r'^(\\(?:mathcal|mathfrak|mathsf|mathrm|mathbb|bar|hat|tilde)\s*(?:\{[^}]*\}|[A-Za-z]))',g)
    if m: stem=m.group(1); rest=g[len(stem):]
    else:
        m=re.match(r'^(\\[A-Za-z]+|[A-Za-z])',g)
        if not m: return None, True
        stem=m.group(1); rest=g[len(stem):]
    sub=re.match(r'^(\^|_)(\\[A-Za-z]+|\{[^{}]*\}|[A-Za-z0-9])',rest)
    pat=re.escape(stem); manual=False
    if sub: pat+=re.escape(sub.group(1))+r'\{?'+re.escape(sub.group(2).strip('{}'))+r'\}?'
    else:
        if re.fullmatch(r'[A-Za-z]',stem): manual=True
        if stem.startswith(B) and not stem.endswith('}'): pat+=r'(?![A-Za-z])'
        elif re.fullmatch(r'[A-Za-z]',stem): pat+=r'(?![A-Za-z_^])'
    return pat, manual
for i,c in rows12:
    secs = re.findall(r'\d+\.\d+', c[3])
    if not secs: continue
    glyphs = [g for gl in re.findall(r'\$([^$]+)\$', c[0]) for g in re.split(r',\s*(?=[\\A-Za-z(])', gl)]
    pats = []
    for g in glyphs:
        p,man = stem_regex(g)
        if p and not man: pats.append(p)
    if not pats: continue
    first_def = min(secs, key=seckey)
    in_def = any(re.search(p, sectext.get(s,'')) for p in pats for s in secs)
    early = [s for s in order if seckey(s) < seckey(first_def) and not s.startswith('1.') and any(re.search(p, sectext[s]) for p in pats)]
    if not in_def or early:
        print(f"  행{i} {c[0][:50]} 정의 절 {c[3][:20]} | 정의 절에 나타남: {in_def} | 앞선 절: {early[:5]}")
