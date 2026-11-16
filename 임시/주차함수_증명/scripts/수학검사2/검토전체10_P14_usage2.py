# -*- coding: utf-8 -*-
# 장부 1.1·1.2 「쓰이는 장」 재검(후보 검출, 2판): 글자 경계를 보고 센다. 판단은 손으로.
import re, glob, os, io
base = r"C:\math\임시\주차함수_증명"
order = {'장1.md':1,'장2.md':2,'장3.md':3,'장4.md':4,'장5A.md':5,'장5B.md':5,'장6.md':6,'장7A.md':7,'장7B.md':7,'장8.md':8,'장9.md':9,'장10.md':10,'장11.md':11}

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = s.replace('{', '').replace('}', '')
    s = s.replace('\\prime', "'")
    s = s.replace('\\ast', '*')
    s = s.replace('\\leq', '\\le').replace('\\geq', '\\ge')
    return s

chap = {}
lines_by_ch = {}
for f in glob.glob(os.path.join(base, "장v2", "장*.md")):
    ch = order[os.path.basename(f)]
    txt = io.open(f, encoding='utf-8').read()
    chap[ch] = chap.get(ch, '') + norm(txt)
    lines_by_ch.setdefault(ch, []).extend((os.path.basename(f), i+1, norm(l)) for i, l in enumerate(txt.split('\n')))

jb = io.open(os.path.join(base, "장부_v2.md"), encoding='utf-8').read().split('\n')

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

def strip_trailing_args(p):
    # remove a trailing (...) group only
    p = p.strip()
    while p.endswith(')'):
        d = 0
        for j in range(len(p)-1, -1, -1):
            if p[j] == ')': d += 1
            elif p[j] == '(':
                d -= 1
                if d == 0:
                    p = p[:j].strip(); break
        else:
            break
    return p

def keys_of(sym):
    out = []
    for p in split_top(sym):
        p = p.strip().strip('$').strip()
        p = re.sub(r':=.*$', '', p)
        p = re.sub(r'=.*$', '', p) if not p.startswith('\\mathrm') else p
        p = strip_trailing_args(p)
        p = norm(p)
        if p and p not in ('\\dots', '\\cdots'):
            out.append(p)
    return out

def find(key):
    pat = re.compile(r'(?<![A-Za-z\\_^])' + re.escape(key) + r'(?![A-Za-z])')
    found = {}
    for ch in sorted(chap):
        hits = []
        for fn, ln, l in lines_by_ch[ch]:
            if pat.search(l):
                hits.append((fn, ln))
        if hits:
            found[ch] = hits
    return found

rows = []
for lo, hi, cc, title in [(27, 42, 2, '1.1'), (48, 340, 4, '1.2')]:
    for i in range(lo, hi):
        l = jb[i]
        if not l.startswith('| $'): continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        rows.append((title, i+1, cells[0], cells[cc]))

for title, ln, sym, chs in rows:
    want = set(range(1, 12)) if '전 장' in chs else set(int(x) for x in re.findall(r'\d+', chs))
    res = []
    allfound = set()
    for k in keys_of(sym):
        f = find(k)
        res.append((k, {c: len(h) for c, h in f.items()}, {c: h[:3] for c, h in f.items()}))
        allfound |= set(f)
    extra = sorted(allfound - want)
    missing = sorted(want - allfound)
    if extra or missing:
        print(f"[{title} L{ln}] {sym[:70]} | 장부: {chs}")
        for k, cnt, ex in res:
            print("   key", k, "count:", cnt)
            for c in extra:
                if c in ex: print("      extra", c, ex[c])
        if missing: print("   미검출:", missing)
