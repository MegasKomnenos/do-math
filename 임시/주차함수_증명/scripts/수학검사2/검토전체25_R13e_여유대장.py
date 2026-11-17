# -*- coding: utf-8 -*-
# 5절이 어떤 장의 여유로 적은 글자 가운데 1.2에 같은 (바탕 글자, 글자체)의 전역 행이 있는 것을 골라,
# 그 장의 파일(본문과 딸린 부록 D)에서 그 글자가 나오는 자리의 꼴을 모은다(판단은 원문을 열어 한다).
import sys, io, re, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
t12 = load('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
BS = chr(92)
C = load('common','scripts/수학검사2/검토전체25_R13e_공통.py')
FILES = C.FILES
def chap_of_sec(s):
    m = re.match(r'\s*(\d+)\.', s); return int(m.group(1)) if m else None
def chapters(s):
    return set(int(x) for x in re.findall(r'\d+', s.split('(')[0]))
rows12=[]
for ln,c in t12.table(49,288):
    base, font = c[1].split('·',1)
    font = '이탤릭' if font.startswith('일반') else font.split('(')[0].strip()
    rows12.append(dict(ln=ln, letter=c[0], base=base.strip(), font=font, defch=chap_of_sec(c[3]), used=chapters(c[4])))
def parse_spare(cell):
    out=set()
    for tok in re.findall(r'\$([^$]+)\$', cell):
        tok=tok.strip()
        m = re.match(r'^'+re.escape(BS)+r'math(cal|frak|sf)\s+(\w)$', tok)
        if m: out.add(({'cal':'필기체','frak':'프락투어','sf':'산세리프'}[m.group(1)], m.group(2)))
        else: out.add(('이탤릭', tok))
    return out
spare = {int(c[0]): parse_spare(c[3]) for ln,c in t12.table(1191,1200)}
def segs(ch):
    return [(f,i,sg.replace(chr(10),' ')) for f in FILES[ch] for i,sg in C.segments(f)]
strip_fonts = C.strip_fonts
def find(ch, font, base):
    hits=[]
    for f,i,sg in segs(ch):
        if font=='이탤릭':
            t = strip_fonts(sg)
            if base.startswith(BS):
                pat = re.escape(base)+r'(?![A-Za-z])'
            else:
                pat = r'(?<![A-Za-z'+re.escape(BS)+r'])'+re.escape(base)+r'(?![A-Za-z])'
            for m in re.finditer(pat, t):
                hits.append((f,i,t[max(0,m.start()-6):m.end()+14]))
        else:
            cmd = {'필기체':'mathcal','프락투어':'mathfrak','산세리프':'mathsf'}[font]
            pat = re.escape(BS+cmd)+r'\s*(?:\{\s*'+re.escape(base)+r'\s*\}|\s'+re.escape(base)+r'(?![A-Za-z]))'
            for m in re.finditer(pat, sg):
                hits.append((f,i,sg[max(0,m.start()-6):m.end()+14]))
    return hits
only = sys.argv[1:]  # 선택: '장번호:글자체:바탕' 로 자세히
if only:
    ch,font,base = only[0].split(':'); ch=int(ch)
    for f,i,ctx in find(ch,font,base): print(f,i,ctx.replace('\n',' '))
    sys.exit()
for r in rows12:
    key=(r['font'], r['base'])
    for ch in range(1,11):
        if ch in r['used'] or ch==r['defch']: continue
        if key not in spare[ch]: continue
        h = find(ch, r['font'], r['base'])
        if not h: continue
        cnt = collections.Counter(re.sub(r'\s+',' ',x[2][6:18]) for x in h)
        print('1.2 %d행 %s (쓰이는 장 %s) — 장 %d 여유 %s: %d건; %s; 첫 자리 %s:%d' % (r['ln'], r['letter'], sorted(r['used']), ch, key, len(h), cnt.most_common(4), h[0][0], h[0][1]))
