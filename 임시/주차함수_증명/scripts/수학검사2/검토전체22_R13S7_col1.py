# 7절 첫 열의 $…$ 토막마다: 1.2 첫 열에 같은 토막이 있는가, 장 파일(본문·부록 D)에 고정 문자열로 몇 번 나오는가(자리 찾기용)
import io, re, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
rows = [(i+1, L[i]) for i in range(1236, 1430)]
g12 = [(i+1, L[i]) for i in range(47, 288) if L[i].startswith('| $')]
c12 = {}
for n, l in g12:
    first = l.split(' | ')[0]
    for t in re.findall(r'\$([^$]+)\$', first):
        c12.setdefault(t, []).append(n)
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
txt = {f: open('장v2/%s.md' % f, encoding='utf-8').read() for f in files}
dtxt = ''.join(open(f, encoding='utf-8').read() for f in glob.glob('장v2/부록D_*.md'))
def variants(t):
    v = {t}
    v.add(t.replace('^\prime', "'"))
    v.add(t.replace("'", '^\prime'))
    v.add(t.replace('\ast', '*')); v.add(t.replace('*', '\ast'))
    return v
for n, l in rows:
    first = l.split(' | ')[0]
    toks = re.findall(r'\$([^$]+)\$', first)
    for t in toks:
        ex = c12.get(t, [])
        hits = []
        for f in files:
            c = max(txt[f].count(v) for v in variants(t))
            if c: hits.append('%s:%d' % (f.replace('장',''), c))
        d = max(dtxt.count(v) for v in variants(t))
        print('%d\t%s\t1.2=%s\t본문[%s]\tD=%d' % (n, t, ex if ex else '-', ' '.join(hits), d))
