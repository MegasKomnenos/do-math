# -*- coding: utf-8 -*-
"""S14: 장부 7절(기록 글자 대응)의 「이 글의 글자」가 1.1·1.2에 있는지, 그리고 1.2의 「정의 절」이
그 기호가 처음 쓰이는 절보다 뒤가 아닌지를 기계적으로 센다(후보 찾기; 판정은 손으로)."""
import re, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
lines = (ROOT/"장부_v2.md").read_text(encoding='utf-8').splitlines()
BS = chr(92)
def norm(s):
    s = re.sub(r'\s+', '', s); s = s.replace(BS + ',', '')
    return s.replace('{', '').replace('}', '')
FONT = re.compile(r'(\\(?:mathcal|mathfrak|mathsf|mathrm|mathbb|tilde|hat|bar|Pr)[A-Za-z]*|\\[A-Za-z]+|[A-Za-z])')
def split_top(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '{(': depth += 1
        if ch in '})': depth -= 1
        if ch == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    out.append(cur)
    return [x for x in out if x]
glyphs = set()
for i in list(range(27, 41)) + list(range(48, 338)):
    l = lines[i]
    if l.startswith('| $'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        for m in re.findall(r'\$([^$]+)\$', c[0]):
            for it in split_top(m):
                it = norm(it.split(':=')[0])
                glyphs.add(it)
                b = FONT.match(it)
                if b: glyphs.add(b.group(1))
print("=== 7절 「이 글의 글자」 가운데 1절에 없는 것")
n = 0
for i in range(1251, 1473):
    l = lines[i]
    if not l.startswith('| $'): continue
    c = [x.strip() for x in l.strip().strip('|').split('|')]
    n += 1
    for m in re.findall(r'\$([^$]+)\$', c[0]):
        for it in split_top(m):
            it0 = norm(it).split('=')[0]
            b = FONT.match(it0)
            ok = it0 in glyphs or (b and b.group(1) in glyphs)
            if not ok: print(f"  L{i+1}: {it}  (행 글자: {c[0][:60]})")
print("7절 행 수", n)

# ---- 정의 절 대조
print("=== 1.2 기호가 「정의 절」보다 앞 절에서 먼저 나오는 경우(첫 쓰이는 장 기준)")
CH = {1:["장1.md"],2:["장2.md"],3:["장3.md"],4:["장4.md"],5:["장5A.md","장5B.md"],6:["장6.md"],7:["장7A.md","장7B.md"],8:["장8.md"],9:["장9.md"],10:["장10.md"],11:["장11.md"]}
SEC = re.compile(r'^#{2,4} (\d+(?:\.\d+)*)')
segs = {}
for c, fs in CH.items():
    segs[c] = []
    for f in fs:
        txt = (ROOT/'장v2'/f).read_text(encoding='utf-8')
        marks = []; p = 0; sec = ''
        for line in txt.splitlines(True):
            m = SEC.match(line)
            if m: sec = m.group(1)
            marks.append((p, sec)); p += len(line)
        def secat(k):
            lo = ''
            for q, s in marks:
                if q <= k: lo = s
                else: break
            return lo
        for m in re.finditer(r'\$\$?(.+?)\$\$?', txt, flags=re.S):
            segs[c].append((secat(m.start()), norm(m.group(1))))
src = (ROOT/'scripts/수학검사2/검토전체12_S14_symbols.py').read_text(encoding='utf-8')
src = src.split("mode = sys.argv")[0].replace("sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')", "")
ns = {}
exec(src, ns)
key = ns['key']; rows = ns['rows']
def tup(x): return tuple(int(v) for v in x.split('.'))
for ln, c in rows(49, 338):
    items = []
    for m in re.findall(r'\$([^$]+)\$', c[0]): items += split_top(m)
    keys = [k for k in (key(x) for x in items) if k]
    dsecs = re.findall(r'\d+\.\d+', c[3])
    if not dsecs: continue
    chs = list(range(1, 12)) if '전 장' in c[4] else sorted(set(int(x) for x in re.findall(r'\b(\d{1,2})\b', c[4].split('(')[0])))
    first = None
    for ch in chs:
        for s, t in segs[ch]:
            if s and any(re.search(k, t) for k in keys):
                first = (ch, s); break
        if first: break
    if not first: continue
    s2 = '.'.join(first[1].split('.')[:2])
    if all(tup(s2) < tup(d) for d in dsecs):
        print(f"  L{ln} {c[0][:45]} | 정의 절 {c[3]} | 첫 등장 {first[1]}(장{first[0]})")
