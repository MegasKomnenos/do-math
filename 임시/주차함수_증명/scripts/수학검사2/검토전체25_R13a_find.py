# -*- coding: utf-8 -*-
# R13a: fixed-string locator over chapter files. Usage:
#   python -I 검토전체25_R13a_find.py [-l] [-s] [-c CH] TOKEN [TOKEN ...]
# -l: list matching lines (truncated context), -s: per-section counts, -c CH: restrict to chapter
import io, re, glob, os, sys
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def chap_of(fn):
    b = os.path.basename(fn)[:-3]
    m = re.match(r'장(\d+)[AB]?$', b)
    if m: return m.group(1)
    m = re.match(r'부록D_장(\d+)[AB]?$', b)
    if m: return m.group(1)
    return None
def order(fn):
    b = os.path.basename(fn)
    m = re.search(r'장(\d+)([AB]?)', b)
    return (int(m.group(1)), m.group(2), b.startswith('부록'))
files = [f for f in glob.glob(os.path.join(base, '장v2', '*.md')) if chap_of(f)]
files.sort(key=order)
def load():
    out = []
    for f in files:
        sec = ''
        b = os.path.basename(f)[:-3]
        for i, l in enumerate(io.open(f, encoding='utf-8').read().split('\n'), 1):
            m = re.match(r'#{2,4}\s+(D\.\{\{D:[^}]+\}\}|[0-9]+(?:\.[0-9]+)*)', l)
            if m: sec = m.group(1)
            out.append((chap_of(f), b, i, sec, l))
    return out
if __name__ == '__main__':
    args = sys.argv[1:]
    lst = False; persec = False; only = None; ctx = 70
    toks = []
    while args:
        a = args.pop(0)
        if a == '-l': lst = True
        elif a == '-s': persec = True
        elif a == '-c': only = args.pop(0)
        elif a == '-w': ctx = int(args.pop(0))
        else: toks.append(a)
    data = load()
    cnt = {}; seccnt = {}
    for ch, b, i, sec, l in data:
        if only and ch != only: continue
        for t in toks:
            st = 0
            while True:
                p = l.find(t, st)
                if p < 0: break
                key = ch + ('D' if b.startswith('부록') else '')
                cnt[key] = cnt.get(key, 0) + 1
                seccnt[(b, sec)] = seccnt.get((b, sec), 0) + 1
                if lst:
                    sys.stdout.write('%s:%d [%s] ...%s...\n' % (b, i, sec, l[max(0, p-ctx):p+len(t)+ctx]))
                st = p + len(t)
    def k(x):
        m = re.match(r'(\d+)(D?)', x); return (int(m.group(1)), m.group(2))
    print('TOKENS', toks)
    print('per chapter:', ', '.join('%s:%d' % (c, cnt[c]) for c in sorted(cnt, key=k)))
    if persec:
        for (b, sec), v in seccnt.items(): print('   %s %s: %d' % (b, sec, v))
