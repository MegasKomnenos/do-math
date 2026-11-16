# O14: 장부 1.2의 각 전역 기호가 장 파일에서 처음 나타나는 절을 찾아 「정의 절」과 견준다(감사 규칙 1: 정의 전 사용 0).
# 1장(개관·1.5 표)과 11장(표)은 설계상 미리 부르므로 뺀다. 결과는 안내이고 판정은 원문으로 한다.
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:/math/임시/주차함수_증명/"
CH = ["장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
def norm(s):
    s = re.sub(r'\s+', '', s)
    s = s.replace('{', '').replace('}', '')
    s = s.replace('\\prime', "'").replace('\\ast', '*')
    s = s.replace('\\mathsf', '\\sf').replace('\\mathrm', '\\rm').replace('\\mathfrak', '\\fk').replace('\\mathcal', '\\cal').replace('\\mathbb', '\\bb')
    return s
lines = []  # (chapter, section, normtext, file, lineno)
for ch in CH:
    sec = None
    for i, line in enumerate(open(BASE + "장v2/" + ch + ".md", encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^### (\d+\.\d+)', line)
        if m: sec = m.group(1); continue
        if sec is None: sec = ch.replace('장', '') + '.0'
        lines.append((sec, norm(line), ch, i))
FIXED = re.compile(r'\\rm|\\sf|\\max|\\min|\\circ|\\flat|\\sharp|\\dagger|\\natural|\\infty|\\star|\\diamond|\*|\'|\d')
def glyph_regex(g):
    g = norm(g)
    g = re.sub(r'\(.*\)$', '', g)
    m = re.match(r'^((?:\\[a-zA-Z]+)?[A-Za-z]?(?:\\[a-zA-Z]+)?)(.*)$', g)
    base, rest = m.group(1), m.group(2)
    if base == '': return None, False
    pat = re.escape(base)
    strong = base.startswith('\\') and not re.fullmatch(r'\\(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|ell|varrho|varsigma|vartheta|varkappa|varphi|varepsilon|Gamma|Lambda|Xi|Pi|Upsilon|Phi|Psi|Omega|Theta)', base) is not None
    for sm in re.finditer(r'([_^])([^_^]*)', rest):
        kind, val = sm.groups()
        if FIXED.search(val) or (kind == '^' and not re.fullmatch(r'[a-zA-Z]', val)):
            pat += re.escape(kind) + re.escape(val); strong = True
        else:
            pat += re.escape(kind) + r'[^$ ]{1,12}?'
    if not rest:
        pat += r'(?![A-Za-z_^])'
    return pat, strong
def split_glyphs(s):
    out = []; depth = 0; cur = ''
    for c in s:
        if c in '{(': depth += 1
        if c in '})': depth -= 1
        if c == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += c
    out.append(cur)
    return [x.strip() for x in out if x.strip()]
def seckey(s):
    a, b = s.split('.')[:2]
    a = a.rstrip('AB')
    return (int(a), int(b))
sec12 = False
for line in open(BASE + "장부_v2.md", encoding='utf-8'):
    if line.startswith('### 1.2'): sec12 = True; continue
    if line.startswith('### 1.3'): break
    if not (sec12 and line.startswith('| $')): continue
    cols = [c.strip() for c in line.strip().strip('|').split(' | ')]
    glyph, defsec = cols[0], cols[3]
    defs = re.findall(r'\d+\.\d+', defsec)
    if not defs: continue
    dmin = min(defs, key=seckey)
    for g in split_glyphs(glyph.strip('$')):
        pat, strong = glyph_regex(g)
        if not pat or not strong: continue
        rx = re.compile(pat)
        first = None
        for sec, t, ch, i in lines:
            if rx.search(t):
                first = (sec, ch, i); break
        if first is None:
            print(f"본문(2–10장)에 없음: {g} | 정의 절 {defsec}")
        elif seckey(first[0]) < seckey(dmin):
            print(f"정의 전 사용?: {g} | 정의 절 {defsec} | 첫 출현 {first[0]} ({first[1]}:{first[2]})")
