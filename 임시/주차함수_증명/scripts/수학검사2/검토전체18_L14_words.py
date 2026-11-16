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
            if ms: sec = ms.group(1)
            doc.append((ch, f, i, sec, line))
lines = open(os.path.join(root, '장부_v2.md'), encoding='utf-8').read().split('\n')
def seckey(s):
    return tuple(int(x) for x in s.split('.'))
for ln in range(508, 742):
    line = lines[ln-1]
    if not line.startswith('| '): continue
    cols = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cols) < 4: continue
    words, meaning, defsec, old = cols[:4]
    if defsec.startswith('—') or '부록' in defsec: continue
    secs = re.findall(r'\d{1,2}(?:\.\d+)?', defsec)
    if not secs: continue
    first_claim = min(secs, key=seckey)
    wl = [w.strip() for w in re.split(r'[,;]', words) if w.strip() and not w.strip().startswith('$')]
    for w in wl:
        w2 = re.sub(r'\(.*?\)', '', w).strip()
        if not w2 or len(w2) < 2: continue
        occ = [(ch, f, i, sec) for ch, f, i, sec, t in doc if w2 in t and ch not in ('1',)]
        if not occ:
            print(f'L{ln} 「{w2}」 claimed {defsec}: NOT FOUND outside ch1')
            continue
        earliest = occ[0]
        ch, f, i, sec = earliest
        # earlier than claimed section (compare by seckey of 2-level)
        s2 = '.'.join(sec.split('.')[:2])
        if seckey(s2) < seckey(first_claim):
            # allow chapter opener of the same chapter
            if s2.split('.')[0] == first_claim.split('.')[0] and len(sec.split('.'))==1:
                continue
            print(f'L{ln} 「{w2}」 claimed {defsec}: earliest {f}:{i} (sec {sec})')
