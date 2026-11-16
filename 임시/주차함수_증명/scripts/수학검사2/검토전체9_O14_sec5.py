# O14: 장부 5절(장별 배정·여유 글자)을 1.2(정의 절·쓰이는 장)·1.1·6절과 대조한다.
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:/math/임시/주차함수_증명/"
txt = open(BASE + "장부_v2.md", encoding='utf-8').read()
def section(a_mark, b_mark):
    a = txt.index(a_mark); b = txt.index(b_mark, a)
    return txt[a:b]
s12 = section('### 1.2', '### 1.3'); s5 = section('## 5.', '## 6.'); s11 = section('### 1.1', '### 1.2')
FACE = re.compile(r'\\(mathcal|mathfrak|mathsf|mathrm|mathbb|Pr)\s*\{?\s*([A-Za-z]+)')
LEAD = re.compile(r'(\\[a-zA-Z]+|[A-Za-z])')
def base_face(g):
    g = g.strip().strip('$')
    g = re.sub(r'^\(', '', g)
    m = FACE.match(g)
    if m:
        face, letters = m.groups()
        if face in ('mathrm', 'Pr'):
            return None
        return (letters[0] if (face != 'mathsf' or len(letters) == 1) else letters, face)
    m = LEAD.match(g)
    if m:
        return (m.group(1), 'it')
    return None
def split_glyphs(s):
    out = []; depth = 0; cur = ''
    for c in s:
        if c in '{(': depth += 1
        if c in '})': depth -= 1
        if c == ',' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += c
    out.append(cur)
    return [x.strip() for x in out if x.strip()]
rows = []
for line in s12.split('\n'):
    if line.startswith('| $'):
        cols = [c.strip() for c in line.strip().strip('|').split(' | ')]
        glyph, defsec, used = cols[0], cols[3], cols[4]
        rows.append((split_glyphs(glyph.strip('$')), glyph.strip('$'), defsec, used))
ch5 = {}
for line in s5.split('\n'):
    m = re.match(r'^\| (\d+) \| (.*?) \| (.*?) \| (.*?) \|$', line.strip())
    if m:
        ch = m.group(1)
        defs = [x.strip().strip('$') for x in m.group(2).split(';')]
        spare_set = set()
        for cat, lst in re.findall(r'(라틴 소문자|라틴 대문자|그리스|필기체|프락투어|산세리프\(명명 상수에만\)): (.*?)(?:\. |$| \|)', m.group(4)):
            for g in re.findall(r'\$([^$]+)\$', lst):
                bf = base_face(g)
                if bf: spare_set.add(bf)
        ch5[ch] = dict(defs=defs, spare=spare_set)
print("5절 장 수:", len(ch5))
# (a) 정의 절 chapter must list glyph among 5절 defs
for gl, glyph_full, defsec, used in rows:
    for ds in set(re.findall(r'(\d+)\.\d+', defsec)):
        d = ch5.get(ds)
        if not d:
            print("5절에 장 없음", ds); continue
        found = any(glyph_full == x or gl[0] == x or gl[0] in x for x in d['defs'])
        if not found:
            print(f"5절 {ds}장 정의 목록에 없음: {glyph_full} (정의 절 {defsec})")
# 5절 defs not in 1.2
all12 = set()
for gl, glyph_full, defsec, used in rows:
    all12.add(glyph_full)
    for g in gl: all12.add(g)
for c, d in ch5.items():
    for x in d['defs']:
        if x and x != '없음' and not any(x == y or x in y for y in all12):
            print(f"5절 {c}장 정의 목록의 글자가 1.2에 없음: {x}")
# (b) spare letters vs used letters
used_by = {str(c): set() for c in range(1, 12)}
for gl, glyph_full, defsec, used in rows:
    chs = set(re.findall(r'\d+', used)) if '전 장' not in used else set(used_by)
    for g in gl:
        bf = base_face(g)
        if bf:
            for c in chs: used_by[c].add(bf)
ch1 = set()
for gl, glyph_full, defsec, used in rows:
    if re.match(r'1\.\d', defsec):
        for g in gl:
            bf = base_face(g)
            if bf: ch1.add(bf)
vars11 = set()
for line in s11.split('\n'):
    if line.startswith('| $'):
        g = line.split('|')[1].strip()
        for x in re.findall(r'\$([^$]+)\$', g):
            bf = base_face(x.split(':=')[0].split('=')[0])
            if bf: vars11.add(bf)
reserved = {('a', 'it'), ('b', 'it'), ('c', 'it'), ('e', 'it'), ('h', 'it'), ('\\delta', 'it'), ('l', 'it'), ('o', 'it'), ('O', 'it'), ('\\varpi', 'it'), ('P', 'it'), ('Q', 'it'), ('W', 'it'), ('X', 'it'), ('d', 'it'), ('x', 'it')}
for c, d in ch5.items():
    bad = d['spare'] & (used_by[c] | ch1 | vars11 | reserved)
    if bad:
        print(f"{c}장 여유 글자가 그 장의 전역·1장 전역·변수·예약과 겹침: {sorted(bad)}")
print("1.1 변수:", sorted(vars11))
print("1장 전역:", sorted(ch1))
