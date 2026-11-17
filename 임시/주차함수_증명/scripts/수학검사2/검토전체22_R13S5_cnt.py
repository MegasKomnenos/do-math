# 고정 문자열을 장 파일의 절별로 센다. 사용: python -I cnt.py <파일들,쉼표> <토큰파일>
import sys, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sys.argv[1].split(',')
toks = [l.rstrip('\n') for l in open(sys.argv[2], encoding='utf-8') if l.strip() and not l.startswith('#')]
def secs(path):
    out = []; cur = '0'
    for i, l in enumerate(open(path, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^###\s+(\S+)', l)
        if m: cur = m.group(1)[:14]
        out.append((cur, i, l))
    return out
data = {f: secs('장v2/' + f) for f in files}
for t in toks:
    parts = []
    for f in files:
        d = {}; first = {}
        for cur, i, l in data[f]:
            c = l.count(t)
            if c:
                d[cur] = d.get(cur, 0) + c; first.setdefault(cur, i)
        if d:
            parts.append(f.replace('.md','') + '[' + ' '.join('%s:%d(L%d)' % (k, v, first[k]) for k, v in d.items()) + ']')
    print('%-40s %s' % (t, ' '.join(parts) if parts else '0'))
