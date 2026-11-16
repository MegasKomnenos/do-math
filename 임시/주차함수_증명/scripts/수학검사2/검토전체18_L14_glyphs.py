import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명'
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
SEC = re.compile(r'^#{2,4} (\d+(?:\.\d+)*)')
doc = []
for f in files:
    ch = re.match(r'장(\d+)', f).group(1)
    sec = ch
    with open(os.path.join(root, '장v2', f + '.md'), encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            ms = SEC.match(line)
            if ms:
                sec = ms.group(1)
            doc.append((ch, f, i, sec, line))

BEFORE = set('$ {(=,;+-<>|[')
AFTER = set('$ }),;=_^\\(<>|]+-/!')
def find_all(tok):
    res = []
    for ch, f, i, sec, t in doc:
        start = 0
        while True:
            j = t.find(tok, start)
            if j < 0:
                break
            b = t[j-1] if j > 0 else ' '
            a = t[j+len(tok)] if j+len(tok) < len(t) else ' '
            if b in BEFORE and a in AFTER:
                res.append((ch, f, i, sec))
                break
            start = j + 1
    return res

def smart_split(g):
    parts, depth, cur = [], 0, ''
    for c in g:
        if c in '{(':
            depth += 1
        elif c in '})':
            depth -= 1
        if c == ',' and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += c
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]

lines = open(os.path.join(root, '장부_v2.md'), encoding='utf-8').read().split('\n')
out = []
for ln in range(49, 340):
    line = lines[ln-1]
    if not line.startswith('| $'):
        continue
    cols = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cols) < 7:
        continue
    glyphcol, base, meaning, defsec, chapters, first, rec = cols[:7]
    glyphs = re.findall(r'\$([^$]+)\$', glyphcol)
    toks = []
    for g in glyphs:
        toks.extend(smart_split(g))
    if chapters.startswith('전 장'):
        claimed = set(str(i) for i in range(1, 12))
    else:
        claimed = set(re.findall(r'\b(\d{1,2})\b', chapters))
    mdef = re.search(r'(\d{1,2}(?:\.\d+)?)', defsec)
    defs = mdef.group(1) if mdef else None
    found = {}
    allocc = []
    for tok in toks:
        occ = find_all(tok)
        for o in occ:
            found.setdefault(o[0], []).append((tok,) + o[1:])
            allocc.append(o)
    fc = set(found)
    msg = []
    if not fc:
        msg.append('TOKENS NOT FOUND')
    else:
        extra = sorted(fc - claimed, key=int)
        missing = sorted(claimed - fc, key=int)
        if extra:
            msg.append('found-but-not-claimed: ' + ','.join(f"{c}({found[c][0][1]}:{found[c][0][2]})" for c in extra))
        if missing:
            msg.append('claimed-but-not-found: ' + ','.join(missing))
    if allocc and defs:
        occ2 = [o for o in allocc if o[0] not in ('1', '11')]
        occ2.sort(key=lambda o: (files.index(o[1]), o[2]))
        if occ2:
            ch2, f2, i2, sec2 = occ2[0]
            if not (sec2 == defs or sec2.startswith(defs + '.')):
                msg.append(f'first-use {f2}:{i2} sec {sec2} vs defsec {defs}')
    if msg:
        out.append(f'L{ln} {glyphcol[:60]} | claimed {sorted(claimed, key=int)} | ' + ' ; '.join(msg))
print('\n'.join(out))
