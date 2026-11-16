# O14: 장부 1.2의 「쓰이는 장」을 장 파일(장1–11; 부록 제외)의 실제 출현과 느슨한 정규식으로 대조한다.
# 결과는 자리를 찾는 안내일 뿐이고 판정은 사람이 원문을 읽고 한다.
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:/math/임시/주차함수_증명/"
CHF = {"1":["장1"],"2":["장2"],"3":["장3"],"4":["장4"],"5":["장5A","장5B"],"6":["장6"],"7":["장7A","장7B"],"8":["장8"],"9":["장9"],"10":["장10"],"11":["장11"]}
def norm(s):
    s = re.sub(r'\s+', '', s)
    s = s.replace('{', '').replace('}', '')
    s = s.replace('\\prime', "'").replace('\\ast', '*')
    s = s.replace('\\mathsf', '\\sf').replace('\\mathrm', '\\rm').replace('\\mathfrak', '\\fk').replace('\\mathcal', '\\cal').replace('\\mathbb', '\\bb')
    return s
texts = {}
for k, fs in CHF.items():
    texts[k] = norm("\n".join(open(BASE + "장v2/" + f + ".md", encoding='utf-8').read() for f in fs))
def split_top(s, sep=','):
    out = []; depth = 0; cur = ''
    for c in s:
        if c in '{(': depth += 1
        if c in '})': depth -= 1
        if c == sep and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += c
    out.append(cur)
    return [x.strip() for x in out if x.strip()]
FIXED = re.compile(r'\\rm|\\sf|\\max|\\min|\\circ|\\flat|\\sharp|\\dagger|\\natural|\\infty|\\star|\\diamond|\*|\'|\d')
def glyph_regex(g):
    g = norm(g)
    g = re.sub(r'\(.*\)$', '', g)   # 인수 제거
    m = re.match(r'^((?:\\[a-zA-Z]+)?[A-Za-z]?(?:\\[a-zA-Z]+)?)(.*)$', g)
    base, rest = m.group(1), m.group(2)
    if base == '':
        return None, False
    pat = re.escape(base)
    strong = base.startswith('\\') and not re.fullmatch(r'\\(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|ell|varrho|varsigma|vartheta|varkappa|varphi|varepsilon|Gamma|Lambda|Xi|Pi|Upsilon|Phi|Psi|Omega|Theta)', base) is not None
    for sm in re.finditer(r'([_^])([^_^]*)', rest):
        kind, val = sm.groups()
        if FIXED.search(val) or (kind == '^' and not re.fullmatch(r'[a-zA-Z]', val)):
            pat += re.escape(kind) + re.escape(val)
            strong = True
        else:
            pat += re.escape(kind) + r'[^$ ]{1,12}?'
    if not rest:
        # 바탕 글자만: 뒤에 첨자·윗첨자·인수가 오지 않는 꼴을 찾는다
        pat += r'(?![A-Za-z_^])'
    return pat, strong
rows = []
sec = None
for line in open(BASE + "장부_v2.md", encoding='utf-8'):
    if line.startswith('### 1.2'): sec = '1.2'
    elif line.startswith('### 1.3'): sec = None
    if sec and line.startswith('| $'):
        cols = [c.strip() for c in line.strip().strip('|').split(' | ')]
        rows.append((cols[0], cols[3], cols[4]))
print("rows", len(rows))
for glyph, defsec, used in rows:
    listed = set(re.findall(r'\d+', used)) if '전 장' not in used else set(CHF)
    glyphs = split_top(glyph.strip('$'), ',')
    found = {}; weak = False
    for g in glyphs:
        g = g.strip().strip('$')
        if not g: continue
        pat, strong = glyph_regex(g)
        if pat is None: continue
        if not strong: weak = True
        for k, t in texts.items():
            n = len(re.findall(pat, t))
            if n: found[k] = found.get(k, 0) + n
    fset = set(found)
    miss = listed - fset
    extra = fset - listed
    if miss or extra:
        tag = "(약한 패턴)" if weak else ""
        print(f"{glyph} {tag} | 정의 {defsec} | 장부: {sorted(listed, key=int)} | 발견: {sorted(found.items(), key=lambda x: int(x[0]))}" + (f" | 장부에만: {sorted(miss, key=int)}" if miss else "") + (f" | 본문에만: {sorted(extra, key=int)}" if extra else ""))
