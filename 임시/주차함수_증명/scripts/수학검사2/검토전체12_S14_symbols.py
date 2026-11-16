# -*- coding: utf-8 -*-
"""S14: 장부 1.1·1.2의 「쓰이는 장」 열을 장 파일에서 기계적으로 대조한다(후보 찾기용; 판정은 손으로 한다).
항목마다 (글자체 명령+바탕 글자)와 첫 첨자·윗첨자의 「모양」을 키로 삼아 장별 등장 여부를 센다.
  - 윗첨자가 있으면 바탕+윗첨자를 그대로 찾는다(예: b^T, s^\\mathrm{low}, \\Pi^\\mathrm{up}).
  - 아래첨자가 한 글자(변수)이면 바탕+'_'+한 글자 꼴을, 두 첨자이면 바탕+'_'+두 첨자 꼴을,
    그 밖의 고정 첨자(fb, max, 0 등)이면 그대로 찾는다.
  - 첨자가 없으면 바탕 글자가 첨자 없이 나오는 자리를 찾는다.
공백·\\,·중괄호는 양쪽에서 지운다."""
import re, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
CH = {1:["장1.md"],2:["장2.md"],3:["장3.md"],4:["장4.md"],5:["장5A.md","장5B.md"],6:["장6.md"],7:["장7A.md","장7B.md"],8:["장8.md"],9:["장9.md"],10:["장10.md"],11:["장11.md"]}
BS = chr(92)
def norm(s):
    s = re.sub(r'\s+', '', s)
    s = s.replace(BS + ',', '').replace(BS + '!', '').replace(BS + ';', '')
    return s.replace('{', '').replace('}', '')
math = {}
for c, fs in CH.items():
    t = ''.join((ROOT/"장v2"/f).read_text(encoding='utf-8') for f in fs)
    segs = re.findall(r'\$\$?(.+?)\$\$?', t, flags=re.S)
    math[c] = '\n'.join(norm(s) for s in segs)
lines = (ROOT/"장부_v2.md").read_text(encoding='utf-8').splitlines()
def rows(a, b):
    for i in range(a-1, b):
        l = lines[i]
        if l.startswith('| $'):
            yield i+1, [c.strip() for c in l.strip().strip('|').split('|')]
def split_top(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '{(': depth += 1
        if ch in '})': depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else: cur += ch
    out.append(cur)
    return [x for x in out if x]
FONT = re.compile(r'^(\\(?:mathcal|mathfrak|mathsf|mathrm|mathbb|tilde|hat|bar|overline|Pr)\s*\{?[A-Za-z]*\}?|\\[A-Za-z]+|[A-Za-z])')
def group(s):
    if s.startswith('{'):
        d = 0
        for i, ch in enumerate(s):
            if ch == '{': d += 1
            elif ch == '}':
                d -= 1
                if d == 0: return s[1:i], s[i+1:]
        return s[1:], ''
    m = re.match(r'(\\[A-Za-z]+|[A-Za-z0-9*#])', s)
    return (m.group(1), s[m.end():]) if m else ('', s)
NOTLET = r'(?![A-Za-z])'
def key(item):
    item = re.sub(r'\s+', '', item).replace(BS + ',', '')
    item = re.split(r':=|=|>|\\in', item)[0].lstrip('(')
    m = FONT.match(item)
    if not m: return None
    b = m.group(1).replace('{', '').replace('}', '')
    rest = item[m.end():]
    sub = sup = None
    for _ in range(2):
        if rest.startswith('_'):
            sub, rest = group(rest[1:])
        elif rest.startswith('^'):
            sup, rest = group(rest[1:])
    pre = '' if b.startswith(BS) else r'(?<![A-Za-z\\])'
    if sup is not None:
        pat = pre + re.escape(b + '^' + norm(sup))
        if sub is not None:
            pat += r'(?:_[^(),]+?)?'
        return pat + NOTLET
    if sub is not None:
        ns = norm(sub)
        if re.fullmatch(r'[a-zA-Z]|\\[a-zA-Z]+', ns):
            return pre + re.escape(b) + r'_(?:[a-zA-Z]|\\[a-zA-Z]+)(?![A-Za-z,])'
        if ',' in ns:
            return pre + re.escape(b) + r'_[^,()]+,[^,()]+'
        return pre + re.escape(b) + '_' + re.escape(ns) + NOTLET
    if b.startswith(BS):
        return re.escape(b) + r'(?![A-Za-z_^])'
    return pre + re.escape(b) + r'(?![A-Za-z_^])'
def chapters(col):
    if '전 장' in col: return set(range(1, 12))
    return set(int(x) for x in re.findall(r'\b(\d{1,2})\b', col.split('(')[0]))
mode = sys.argv[1] if len(sys.argv) > 1 else '1.2'
rng = (28, 41) if mode == '1.1' else (49, 338)
for ln, c in rows(*rng):
    items = []
    for m in re.findall(r'\$([^$]+)\$', c[0]):
        items += split_top(m)
    keys = [k for k in (key(x) for x in items) if k]
    claimed = chapters(c[4] if mode == '1.2' else c[2])
    found = {ch for ch in math if any(re.search(k, math[ch]) for k in keys)}
    miss, extra = claimed - found, found - claimed
    if miss or extra:
        print(f"L{ln} {c[0][:50]} | 장부 {sorted(claimed)} | 없음 {sorted(miss)} | 장부밖 {sorted(extra)}")
