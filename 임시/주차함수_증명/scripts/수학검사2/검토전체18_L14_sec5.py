import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명'
lines = open(os.path.join(root, '장부_v2.md'), encoding='utf-8').read().split('\n')
# 1.2 rows -> (glyphcol, defsec chapter)
rows = []
for ln in range(49, 340):
    line = lines[ln-1]
    if not line.startswith('| $'): continue
    cols = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cols) < 7: continue
    glyphcol, base, meaning, defsec, chapters, first, rec = cols[:7]
    m = re.search(r'(\d{1,2})(?:\.\d+)?', defsec)
    rows.append((ln, glyphcol, m.group(1) if m else None, defsec))
# 5절 rows: 1203..1213
sec5 = {}
for ln in range(1203, 1214):
    line = lines[ln-1]
    cols = [c.strip() for c in line.strip().strip('|').split(' | ')]
    ch = cols[0]
    sec5[ch] = cols[1]
def norm(s):
    return re.sub(r'\s+', '', s)
for ln, g, ch, defsec in rows:
    if ch is None: continue
    target = sec5.get(ch, '')
    ok = norm(g) in norm(target)
    if not ok:
        # try first glyph only
        g1 = re.findall(r'\$([^$]+)\$', g)
        ok = any(norm('$'+x+'$') in norm(target) for x in g1)
    if not ok:
        # find which chapter lists it
        where = [c for c, t in sec5.items() if norm(g) in norm(t) or any(norm('$'+x+'$') in norm(t) for x in re.findall(r'\$([^$]+)\$', g))]
        print(f'L{ln} {g[:50]} defsec {defsec} -> ch {ch}; 5절 lists in {where}')
