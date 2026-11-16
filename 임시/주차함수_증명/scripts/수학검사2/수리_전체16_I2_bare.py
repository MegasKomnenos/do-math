import re, sys
path = sys.argv[1]; letters = sys.argv[2:]
lines = open(path, encoding='utf-8').read().split('\n')
segs = []; inblock = False; buf = ''; start = 0
for ln, l in enumerate(lines, 1):
    if l.strip() == '$$':
        if inblock:
            segs.append((start, buf)); buf = ''; inblock = False
        else:
            inblock = True; start = ln
        continue
    if inblock:
        buf += l + '\n'; continue
    for m in re.finditer(r'\$([^$]+)\$', l):
        segs.append((ln, m.group(1)))

def clean(s):
    s = re.sub(r'\\(mathfrak|mathcal|mathsf|mathbb|mathscr|bar|hat|tilde|dot|vec|overline|widehat)\s*(\{[^{}]*\}|[A-Za-z])', '', s)
    s = re.sub(r'\\(mathrm|operatorname|text|tag|label)\{[^{}]*\}', '', s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return s

for L in letters:
    pat = re.compile(r'(?<![A-Za-z])' + re.escape(L) + r'(?![A-Za-z])')
    hits = [(ln, s) for ln, s in segs if pat.search(clean(s))]
    print(f'--- {path} bare {L}: {len(hits)} segs; lines:', sorted(set(ln for ln, _ in hits)))
