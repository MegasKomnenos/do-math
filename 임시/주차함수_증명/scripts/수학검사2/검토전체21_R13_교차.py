# R13: (1) 7절 「이 글의 글자」 토큰이 1.1·1.2 첫 셀(전역 글자)이나 장 파일 본문에 있는가,
#      (2) 5절 「이 장이 처음 정의하는 전역 기호」가 1.2의 정의 절과 맞는가,
#      (3) 1.2 「정의 절」이 장 파일에서 그 글자가 처음 나오는 절과 맞는가(고정 문자열; 안내용).
import re, sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
lines = open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8').read().split('\n')
def norm(s):
    return s.replace(' ', '').replace('\\,', '').replace('\\;', '').replace('\\!', '').replace('\\prime', "'")
def rows_between(a, b, pred=lambda l: l.startswith('| $')):
    out, on = [], False
    for i, l in enumerate(lines, 1):
        if l.startswith(a): on = True; continue
        if on and l.startswith(b): break
        if on and pred(l):
            out.append((i, [c.strip() for c in l.strip().strip('|').split('|')]))
    return out
r11 = rows_between('### 1.1', '### 1.2')
r12 = rows_between('### 1.2', '### 1.3')
r13 = rows_between('### 1.3', '## 2.', pred=lambda l: l.startswith('| ') and not l.startswith('|---') and not l.startswith('| 글자'))
def toks(cell):
    out = []
    for f in re.findall(r'\$(.+?)\$', cell):
        for piece in re.split(r',\s*(?![^{]*\})', f):
            p = piece.strip().split(':=')[0].strip()
            if p: out.append(p)
    return out
glob12 = set()
for _, c in r11 + r12:
    for t in toks(c[0]): glob12.add(norm(t))
loc13 = norm('\n'.join(c[0] for _, c in r13))
files = {1:['장1.md'],2:['장2.md'],3:['장3.md'],4:['장4.md'],5:['장5A.md','장5B.md'],6:['장6.md'],7:['장7A.md','장7B.md'],8:['장8.md'],9:['장9.md'],10:['장10.md']}
chap = {ch: norm(''.join(open(os.path.join(ROOT, '장v2', f), encoding='utf-8').read() for f in fl)) for ch, fl in files.items()}
allchap = ''.join(chap.values())
appD = norm(''.join(open(f, encoding='utf-8').read() for f in glob.glob(os.path.join(ROOT, '장v2', '부록D_*.md'))))
def strip_sub(p):
    return re.sub(r'(\^|_)(\{[^{}]*\}|\\?[A-Za-z0-9]+)', '', p)
def strip_arg(p):
    return re.sub(r'\([^()]*\)$', '', p)
r7 = rows_between('## 7.', '## 8.', pred=lambda l: l.startswith('| $') or l.startswith('| 교차항') or l.startswith('| $'))
print('== (1) 7절 토큰 가운데 1.1·1.2 첫 셀에 없는 것(장 파일 본문·부록 D 출현 여부 함께)')
for ln, c in r7:
    if len(c) < 4: continue
    miss = []
    for t in toks(c[0]):
        n = norm(t)
        cands = {n, norm(strip_arg(t)), norm(strip_sub(strip_arg(t)))}
        if any(x in glob12 for x in cands):
            continue
        # 전역 글자 셀에 부분 문자열로 들어 있는가(예: $\Omega(\xi), \Omega_q$ 행의 '\Omega_q')
        if any(any(x and x in g for g in glob12) for x in cands if len(x) >= 3):
            continue
        inchap = any(x in allchap for x in cands if len(x) >= 3)
        inD = any(x in appD for x in cands if len(x) >= 3)
        inloc = any(x in loc13 for x in cands if len(x) >= 3)
        miss.append(f"{t} [본문 {'O' if inchap else 'X'} / 부록D {'O' if inD else 'X'} / 1.3 {'O' if inloc else 'X'}]")
    if miss:
        print(f'  행 {ln}:', '; '.join(miss))
print('\n== (2) 5절 「처음 정의하는 전역 기호」 vs 1.2 정의 절')
r5 = rows_between('## 5.', '## 6.', pred=lambda l: re.match(r'^\| \d+ \|', l) is not None)
five = {}
for ln, c in r5:
    five[int(c[0])] = {norm(t) for t in toks(c[1])}
def_by_ch = {ch: set() for ch in range(1, 11)}
for ln, c in r12:
    secs = re.findall(r'(\d+)\.\d+', c[3])
    if not secs: continue
    ch = int(secs[0])
    for t in toks(c[0]): def_by_ch.setdefault(ch, set()).add(norm(t))
for ch in range(1, 11):
    a, b = five.get(ch, set()), def_by_ch.get(ch, set())
    only5 = {x for x in a if x not in b}
    only12 = {x for x in b if x not in a}
    if only5 or only12:
        print(f'  장 {ch}: 5절에만 {sorted(only5)} | 1.2에만 {sorted(only12)}')
print('\n== (3) 1.2 정의 절 vs 장 파일 첫 출현 절(고정 문자열; 전체 꼴로 찾고 없으면 인수 뗀 꼴)')
sec_re = re.compile(r'^##+ (\d+\.\d+)')
chap_lines = {}
for ch, fl in files.items():
    L = []
    for f in fl:
        sec = None
        for line in open(os.path.join(ROOT, '장v2', f), encoding='utf-8'):
            m = sec_re.match(line)
            if m: sec = m.group(1)
            L.append((sec, norm(line)))
    chap_lines[ch] = L
for ln, c in r12:
    defsec = c[3]
    m = re.match(r'(\d+)\.(\d+)', defsec)
    if not m: continue
    t0 = toks(c[0])[0]
    forms = [norm(t0), norm(strip_arg(t0))]
    forms = [f for f in forms if len(f) >= 3]
    if not forms: continue
    first = None
    for ch in range(1, 11):
        for sec, line in chap_lines[ch]:
            if any(f in line for f in forms):
                first = (ch, sec); break
        if first: break
    if first is None:
        print(f'  {ln} {t0}: 장 파일에서 못 찾음(정의 절 {defsec})')
    elif first[1] != f'{m.group(1)}.{m.group(2)}':
        print(f'  {ln} {t0}: 정의 절 {defsec} | 첫 출현 {first[1]}')
