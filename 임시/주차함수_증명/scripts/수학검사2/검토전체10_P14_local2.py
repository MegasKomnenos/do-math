# -*- coding: utf-8 -*-
# 1.3 국소 글자(각 항목의 머리 글자만) vs 그 장의 전역(1.2 쓰이는 장)·1장 전역·1.1 변수·예약 — 2판(잡음 줄임)
import re, io
base = r"C:\math\임시\주차함수_증명"
jb = io.open(base + r"\장부_v2.md", encoding='utf-8').read().split('\n')
def norm(s): return re.sub(r'\s+', '', s).replace('{', '').replace('}', '')
def baseglyph(sym):
    s = norm(sym.strip().strip('$'))
    s = re.sub(r'^\\(hat|tilde|bar|overline|underline|widetilde)', '', s)
    m = re.match(r'^(\\mathcal|\\mathfrak|\\mathsf|\\mathrm|\\mathbb|\\mathscr)?(\\[A-Za-z]+|[A-Za-z])', s)
    if not m: return None
    font = m.group(1) or ''
    g = m.group(2)
    if font in ('\\mathrm', '\\mathbb'): return None
    return (font, g)
def split_top(sym):
    parts = []; d = 0; cur = ''
    for ch in sym:
        if ch in '({[': d += 1
        if ch in ')}]': d -= 1
        if ch == ',' and d == 0:
            parts.append(cur); cur = ''
        else: cur += ch
    parts.append(cur)
    return parts
glob_by_ch = {ch: {} for ch in range(1, 12)}
ch1 = {}
for i in range(48, 340):
    l = jb[i]
    if not l.startswith('| $'): continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    sym, defsec, chs = cells[0], cells[3], cells[4]
    chset = set(range(1, 12)) if '전 장' in chs else set(int(x) for x in re.findall(r'\d+', chs))
    for p in split_top(sym):
        g = baseglyph(p)
        if g is None: continue
        for c in chset: glob_by_ch[c].setdefault(g, p.strip())
        if defsec.startswith('1.'): ch1.setdefault(g, p.strip())
var = {}
for i in range(27, 42):
    l = jb[i]
    if not l.startswith('| $'): continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    for p in split_top(cells[0]):
        g = baseglyph(p)
        if g: var[g] = p.strip()
reserved = {('', 'a'), ('', 'b'), ('', 'c'), ('', 'e'), ('', 'h'), ('', 'o'), ('', 'O'), ('', 'l'), ('', '\\delta'), ('', '\\Delta'), ('', '\\Sigma'), ('', '\\varpi')}

def items(cell):
    # split by ';' at top level (outside parentheses)
    out = []; d = 0; cur = ''
    for ch in cell:
        if ch == '(': d += 1
        if ch == ')': d -= 1
        if ch == ';' and d == 0:
            out.append(cur); cur = ''
        else: cur += ch
    out.append(cur)
    return out

for i in range(346, 414):
    l = jb[i]
    if not l.startswith('| '): continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    if len(cells) < 3: continue
    letters, place = cells[0], cells[2]
    chs = set(int(x) for x in re.findall(r'(?<![\d.])(\d+)\.\d+', place))
    chs |= set(int(x) for x in re.findall(r'\{\{(\d+):', place))
    if not chs: continue
    for it in items(letters):
        head = it.split('(')[0]
        for m in re.finditer(r'\$([^$]+)\$', head):
            tok = m.group(1)
            for p in split_top(tok):
                p = re.sub(r'(:=|=).*$', '', p)
                g = baseglyph(p)
                if g is None: continue
                for ch in chs:
                    hits = []
                    if g in glob_by_ch[ch]: hits.append('장 전역 ' + glob_by_ch[ch][g])
                    elif g in ch1 and ch != 1: hits.append('1장 전역 ' + ch1[g])
                    if g in var: hits.append('1.1 변수 ' + var[g])
                    if g in reserved: hits.append('예약')
                    if hits:
                        print(f"L{i+1} {ch}장 | {p.strip()[:30]} | {hits} | …{it.strip()[:90]}…")
