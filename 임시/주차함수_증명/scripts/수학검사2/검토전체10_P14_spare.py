# -*- coding: utf-8 -*-
# 5절 여유 글자의 자기 정합: 그 장의 전역(1.2 쓰이는 장)·1장 전역·1.1 변수·6절 예약과 (바탕 글자, 글자체) 겹침
import re, io
base = r"C:\math\임시\주차함수_증명"
jb = io.open(base + r"\장부_v2.md", encoding='utf-8').read().split('\n')

def norm(s):
    return re.sub(r'\s+', '', s).replace('{', '').replace('}', '')

def baseglyph(sym):
    s = norm(sym.strip().strip('$'))
    s = re.sub(r'^\\(hat|tilde|bar|overline|underline)', '', s)
    m = re.match(r'^(\\mathcal|\\mathfrak|\\mathsf|\\mathrm|\\mathbb|\\mathscr)?(\\[A-Za-z]+|[A-Za-z])', s)
    if not m: return None
    font = m.group(1) or ''
    g = m.group(2)
    if font == '\\mathrm': return ('rm', g)
    return (font, g)

def split_top(sym):
    parts = []; d = 0; cur = ''
    for ch in sym:
        if ch in '({[': d += 1
        if ch in ')}]': d -= 1
        if ch == ',' and d == 0:
            parts.append(cur); cur = ''
        else:
            cur += ch
    parts.append(cur)
    return parts

glob_by_ch = {ch: set() for ch in range(1, 12)}
ch1 = set()
for i in range(48, 340):
    l = jb[i]
    if not l.startswith('| $'): continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    sym, defsec, chs = cells[0], cells[3], cells[4]
    chset = set(range(1, 12)) if '전 장' in chs else set(int(x) for x in re.findall(r'\d+', chs))
    for p in split_top(sym):
        g = baseglyph(p)
        if g is None or g[0] == 'rm': continue
        for c in chset: glob_by_ch[c].add(g)
        if defsec.startswith('1.'): ch1.add(g)

var = set()
for i in range(27, 42):
    l = jb[i]
    if not l.startswith('| $'): continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    for p in split_top(cells[0]):
        g = baseglyph(p)
        if g: var.add(g)

reserved = {('', 'a'), ('', 'b'), ('', 'c'), ('', 'e'), ('', 'h'), ('', 'o'), ('', 'O'), ('', 'l'),
            ('', '\\delta'), ('', '\\Delta'), ('', '\\Sigma'), ('', '\\varpi')}
fontmap = {'라틴 소문자': '', '라틴 대문자': '', '그리스': '', '필기체': '\\mathcal', '프락투어': '\\mathfrak', '산세리프': '\\mathsf'}
for i in range(1197, 1208):
    l = jb[i]
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    ch = int(cells[0]); spare = cells[3]
    for seg in re.split(r'\.\s+(?=[가-힣])', spare):
        m = re.match(r'([가-힣 ]+?)(?:\([^)]*\))?:\s*(.*)', seg.strip())
        if not m: continue
        fname = m.group(1).strip(); font = fontmap.get(fname)
        if font is None: continue
        for tok in re.findall(r'\$([^$]+)\$', m.group(2)):
            g = baseglyph(tok)
            if font and g and g[0] == '': g = (font, g[1])
            bad = []
            if g in glob_by_ch[ch]: bad.append('그 장 전역')
            if g in ch1: bad.append('1장 전역')
            if g in var: bad.append('1.1 변수')
            if g in reserved: bad.append('6절 예약')
            if bad: print(f"5절 {ch}장 여유 {tok} ({fname}) 겹침: {bad}")
    # also: globals used in chapter whose glyph is NOT excluded from spare -> i.e., missing from spare list? (reverse check)
print("--- 역검사: 그 장 전역·1장 전역·1.1 변수·예약에 들지 않는데 여유 목록에도 없는 글자(라틴·그리스만) ---")
latin_l = [chr(c) for c in range(97, 123)]
latin_u = [chr(c) for c in range(65, 91)]
greek = ['\\alpha','\\beta','\\gamma','\\delta','\\epsilon','\\varepsilon','\\zeta','\\eta','\\theta','\\vartheta','\\iota','\\kappa','\\varkappa','\\lambda','\\mu','\\nu','\\xi','\\pi','\\rho','\\varrho','\\sigma','\\varsigma','\\tau','\\upsilon','\\phi','\\varphi','\\chi','\\psi','\\omega','\\Gamma','\\Delta','\\Theta','\\Lambda','\\Xi','\\Pi','\\Sigma','\\Upsilon','\\Phi','\\Psi','\\Omega']
nameletters = {('', 'P'), ('', 'Q'), ('', 'W'), ('', 'X')}
for i in range(1197, 1208):
    l = jb[i]
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    ch = int(cells[0]); spare = cells[3]
    listed = set()
    for seg in re.split(r'\.\s+(?=[가-힣])', spare):
        m = re.match(r'([가-힣 ]+?)(?:\([^)]*\))?:\s*(.*)', seg.strip())
        if not m: continue
        font = fontmap.get(m.group(1).strip())
        if font is None: continue
        for tok in re.findall(r'\$([^$]+)\$', m.group(2)):
            g = baseglyph(tok)
            if font and g and g[0] == '': g = (font, g[1])
            listed.add(g)
    excl = glob_by_ch[ch] | ch1 | var | reserved | nameletters
    free = []
    for g in [('', x) for x in latin_l + latin_u + greek]:
        if g not in excl and g not in listed:
            free.append(g[1])
    if free: print(f"{ch}장: 여유 목록에 없으나 배제 사유도 없는 글자: {free}")
    over = []
    for g in listed:
        if g[0] == '' and g in excl:
            over.append(g[1])
    if over: print(f"{ch}장: 여유 목록에 있으나 배제되어야 하는 글자: {over}")
