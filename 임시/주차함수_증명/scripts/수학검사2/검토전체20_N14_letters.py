# -*- coding: utf-8 -*-
"""N14: 1.1 변수 글자의 장별 출현, 6절 예약 글자의 선언, 5절 여유 글자와 1.2 전역의 충돌을 수식 토큰 단위로 센다."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
CH = {"1":["장1"],"2":["장2"],"3":["장3"],"4":["장4"],"5":["장5A","장5B"],"6":["장6"],"7":["장7A","장7B"],"8":["장8"],"9":["장9"],"10":["장10"],"11":["장11"]}
raw = {k: ''.join(open(os.path.join(ROOT,"장v2",f+".md"),encoding='utf-8').read() for f in fs) for k,fs in CH.items()}
MATH = re.compile(r'\$\$(.*?)\$\$|\$(.*?)\$', re.S)
FONT = re.compile(r'\\(mathcal|mathfrak|mathsf|mathrm|mathbb|mathscr|mathbf|operatorname|text|textrm|mathit)\s*(\{[^{}]*\}|[A-Za-z])')
def math_segments(t):
    out = []
    for m in MATH.finditer(t):
        out.append(m.group(1) if m.group(1) is not None else m.group(2))
    # also display math blocks on own lines ($$ ... $$ handled); ignore code
    return out
def bare_letters(seg):
    """return list of bare italic letters (standalone identifiers) in a math segment"""
    s = FONT.sub(' ', seg)              # remove font-wrapped identifiers
    s = re.sub(r'\\[A-Za-z]+', ' ', s)  # remove commands (\alpha, \frac, ...)
    s = re.sub(r'\\.', ' ', s)
    return re.findall(r'(?<![A-Za-z])([A-Za-z])(?![A-Za-z])', s)
def greek_tokens(seg):
    return re.findall(r'\\(alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|varkappa|lambda|mu|nu|xi|pi|varpi|rho|varrho|sigma|varsigma|tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega|ell)(?![A-Za-z])', seg)
def font_tokens(seg):
    out = []
    for m in FONT.finditer(seg):
        f, a = m.group(1), m.group(2).strip('{}')
        out.append((f, a))
    return out
from collections import Counter
bare = {}; greek = {}; fonts = {}
for k, t in raw.items():
    cb, cg, cf = Counter(), Counter(), Counter()
    for seg in math_segments(t):
        cb.update(bare_letters(seg)); cg.update(greek_tokens(seg)); cf.update(font_tokens(seg))
    bare[k], greek[k], fonts[k] = cb, cg, cf
print("=== 1.1 변수 글자: 장별 맨 글자 출현 수(수식 안, 글꼴 없는 이탤릭) ===")
for L in ["n","m","t","N","k","y","Y","i","j","u","v","r","d","q","l","o","O","X","P","Q","W","x","f","g","w","z"]:
    print(L, {k: bare[k][L] for k in CH if bare[k][L]})
print("\n=== 그리스 글자 장별 ===")
for g in ["nu","zeta","lambda","xi","vartheta","theta","varpi","tau","sigma","psi","Psi","Pi","Omega","Phi","chi","kappa","varkappa","varrho","rho","mu","eta","iota","upsilon","omega","gamma","beta","epsilon","varepsilon","phi","varphi","Gamma","Lambda","Xi","Theta","Upsilon","Delta","Sigma"]:
    d = {k: greek[k][g] for k in CH if greek[k][g]}
    print(g, d)
print("\n=== 6절·1.3 선언 점검 ===")
print("\\mathscr:", {k: sum(c for (f,a),c in fonts[k].items() if f=='mathscr') for k in CH if any(f=='mathscr' for (f,a) in fonts[k])})
print("\\mathbf 인수:", {k: {a:c for (f,a),c in fonts[k].items() if f=='mathbf'} for k in CH if any(f=='mathbf' for (f,a) in fonts[k])})
print("\\varpi:", {k: greek[k]['varpi'] for k in CH if greek[k]['varpi']})
print("맨 l:", {k: bare[k]['l'] for k in CH if bare[k]['l']}, "| 맨 o:", {k: bare[k]['o'] for k in CH if bare[k]['o']}, "| 맨 O:", {k: bare[k]['O'] for k in CH if bare[k]['O']})
print("맨 X:", {k: bare[k]['X'] for k in CH if bare[k]['X']}, "| 맨 P:", {k: bare[k]['P'] for k in CH if bare[k]['P']}, "| 맨 Q:", {k: bare[k]['Q'] for k in CH if bare[k]['Q']}, "| 맨 W:", {k: bare[k]['W'] for k in CH if bare[k]['W']})
print("5장 대문자 N:", bare["5"]["N"], "| 4장 이탤릭 m:", bare["4"]["m"], "| 11장 맨 t:", bare["11"]["t"], "| 7·8장 맨 u:", bare["7"]["u"], bare["8"]["u"])
print("theta':", {k: len(re.findall(r"\\theta\^?\\?prime|\\theta'", raw[k])) for k in CH if re.search(r"\\theta\^?\\?prime|\\theta'", raw[k])})
print("o(·)/O(·):", {k: [m.start() for m in re.finditer(r'(?<![A-Za-z\\])[oO]\(', ' '.join(math_segments(raw[k])))][:5] for k in CH if re.search(r'(?<![A-Za-z\\])[oO]\(', ' '.join(math_segments(raw[k])))})
print("\n=== 산세리프 글자 장별(명제 이름·명명 상수) ===")
for k in CH:
    print(k, sorted({a for (f,a) in fonts[k] if f=='mathsf'}))
print("\n=== 필기체·프락투어 글자 장별 ===")
for k in CH:
    print(k, "cal:", ''.join(sorted({a for (f,a) in fonts[k] if f=='mathcal' and len(a)==1})), "| frak:", ''.join(sorted({a for (f,a) in fonts[k] if f=='mathfrak' and len(a)==1})))
print("\n=== 라틴 대문자(맨) 장별 ===")
for k in CH:
    print(k, ''.join(sorted({L for L in bare[k] if L.isupper() and bare[k][L]>0})))
print("\n=== 그리스(소·대) 장별 ===")
for k in CH:
    print(k, ' '.join(sorted({g for g in greek[k] if greek[k][g]>0})))

# ---- 5절 여유 글자 vs 1.2 전역 (바탕 글자, 글자체) per chapter
lines = open(os.path.join(ROOT, "장부_v2.md"), encoding='utf-8').read().split('\n')
s = lines.index("### 1.2 전역 기호(라틴 소문자 / 라틴 대문자 / 그리스 / 필기체·프락투어·산세리프 / 로마체 이름·꼬리표 순)")
e = lines.index("### 1.3 국소 기호")
glob = []  # (base, font, used_set, symcell)
for ln in lines[s:e]:
    if not ln.startswith('| $'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    bf, used = c[1], c[4]
    used_set = set(CH) if used == '전 장' else set(x.strip() for x in used.split(','))
    m = re.match(r'(\\?[A-Za-z]+)·(.+)', bf)
    if not m: continue
    base, font = m.group(1), m.group(2)
    glob.append((base, font, used_set, c[0]))
s5 = lines.index("## 5. 장별 배정과 여유 글자"); e5 = lines.index("## 6. 예약 글자")
FONTMAP = {"라틴 소문자":"일반", "라틴 대문자":"일반", "그리스":"일반", "필기체":"필기체", "프락투어":"프락투어", "산세리프(명명 상수에만)":"산세리프"}
print("\n=== 5절 여유 글자 vs 1.2 전역(같은 장에 쓰이는 같은 바탕 글자·글자체) ===")
for ln in lines[s5:e5]:
    if not re.match(r'^\| \d+ \|', ln): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    chap, spare = c[0], c[3]
    for part in spare.split('. '):
        mm = re.match(r'(라틴 소문자|라틴 대문자|그리스|필기체|프락투어|산세리프\(명명 상수에만\)): (.*)', part.strip())
        if not mm: continue
        fam, lst = mm.group(1), mm.group(2)
        letters = re.findall(r'\$(?:\\mathcal |\\mathfrak |\\mathsf )?(\\?[A-Za-z]+)\$', lst)
        for L in letters:
            for base, font, used, cell in glob:
                if base == L and chap in used and font.startswith(FONTMAP[fam]):
                    print(f"장 {chap}: 여유 {fam} ${L}$ 인데 1.2 {cell[:40]} ({font}) 가 {chap}장에 쓰임")
# 5절 '처음 정의하는 전역 기호' vs 1.2 정의 절
print("\n=== 5절 「처음 정의하는 전역 기호」 vs 1.2 정의 절 ===")
defsec = {}
for ln in lines[s:e]:
    if not ln.startswith('| $'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    defsec[c[0]] = c[3]
for ln in lines[s5:e5]:
    if not re.match(r'^\| \d+ \|', ln): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    chap = c[0]
    syms = [x.strip() for x in c[1].split(';')] if c[1] != '없음' else []
    for sym in syms:
        sym0 = re.sub(r'\(.*?\)$', '', sym).strip()
        hit = [k for k in defsec if k == sym or k.startswith(sym0)]
        if not hit:
            print(f"장 {chap}: 5절 기호 {sym[:50]} 가 1.2에 없음(철자 다름?)")
            continue
        ds = defsec[hit[0]]
        chaps = set(re.findall(r'(\d+)\.\d+', ds))
        if chap not in chaps:
            print(f"장 {chap}: 5절 기호 {sym[:40]} 의 1.2 정의 절 {ds}")
    # reverse: 1.2 symbols defined in this chapter but not listed in 5절
for k_, ds in defsec.items():
    chaps = set(re.findall(r'(\d+)\.\d+', ds))
    for chap in chaps:
        pass
listed5 = {}
for ln in lines[s5:e5]:
    if not re.match(r'^\| \d+ \|', ln): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    listed5[c[0]] = c[1]
for k_, ds in defsec.items():
    chaps = set(re.findall(r'(\d+)\.\d+', ds))
    for chap in chaps:
        core = re.sub(r'\(.*?\)$', '', k_.split(',')[0]).strip()
        if core not in listed5.get(chap, '') and k_ not in listed5.get(chap, ''):
            print(f"1.2 {k_[:50]} (정의 절 {ds}) 가 5절 장 {chap}의 목록에 없음")
