# 부록 A의 행마다 기호의 머리 토큰이 「처음 정의된 절」 안에서 처음 나오는 자리의 글귀를 찍는다(정의 문장을 눈으로 맞추기 위한 자리 찾기).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명/장v2/'
names = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9']
docs = []
for n in names:
    sec = '0'
    for i, l in enumerate(open(base+n+'.md', encoding='utf-8').read().split('\n')):
        m = re.match(r'^#{2,4} (\d+(?:\.\d+)*)', l)
        if m: sec = m.group(1)
        docs.append((n, i+1, sec, l))
def variants(h):
    v = [h]
    v.append(re.sub(r'\^\{([A-Za-z])\}', r'^\1', h))
    v.append(h.replace('_{>}', '_>'))
    v.append(h.replace('^\prime', "'").replace('^{\prime-}', "'^-").replace('^{\prime', "^{'"))
    v.append(h.replace('^{\pm}', '^+'))
    v.append(re.sub(r'_[a-z]$', '_', h)) if re.search(r'_[a-z]$', h) else None
    out = []
    for x in v:
        if x and x not in out: out.append(x)
    return out
def heads(c0):
    s = c0.strip().strip('$')
    depth = 0; cur = ''; items = []
    for ch in s:
        if ch in '({[': depth += 1
        if ch in ')}]': depth -= 1
        if ch == ',' and depth == 0: items.append(cur.strip()); cur = ''
        else: cur += ch
    items.append(cur.strip())
    res = []
    for it in items:
        h = re.sub(r'\([^()]*\)$', '', it).strip()
        h = re.sub(r':?=.*$', '', h).strip()
        res.append(h)
    return res
lo, hi = int(sys.argv[1]), int(sys.argv[2]); W = int(sys.argv[3]) if len(sys.argv) > 3 else 130
for i, l in enumerate(open(base+'부록A.md', encoding='utf-8').read().split('\n')):
    if not l.startswith('| $') or not (lo <= i+1 <= hi): continue
    c0 = l[2:].split(' | ')[0]
    sec = l.rstrip().rstrip('|').rstrip().rsplit(' | ', 2)[-2]
    claimed = re.findall(r'\d+\.\d+', sec)
    for h in heads(c0):
        found = None
        for v in variants(h):
            for n, ln, s, t in docs:
                if '.'.join(s.split('.')[:2]) in claimed and v in t:
                    # 정의 꼴(:=)이 있는 자리를 먼저
                    found = (n, ln, s, t, v); break
            if found: break
        if not found:
            print(f'## A:{i+1} {h} [{sec}] — 그 절에서 못 찾음'); continue
        n, ln, s, t, v = found
        # := 이 붙은 자리를 우선 찾아 본다
        best = None
        for n2, ln2, s2, t2 in docs:
            if '.'.join(s2.split('.')[:2]) in claimed:
                for vv in variants(h):
                    k = t2.find(vv)
                    while k >= 0:
                        seg = t2[k:k+len(vv)+40]
                        if ':=' in seg:
                            best = (n2, ln2, s2, t2, k); break
                        k = t2.find(vv, k+1)
                    if best: break
            if best: break
        if best:
            n, ln, s, t, k = best; tag = ':='
        else:
            k = t.find(v); tag = '첫'
        print(f'## A:{i+1} {h} [{sec}] {n}:{ln} §{s} ({tag})')
        print('   …' + t[max(0,k-W):k+len(v)+W] + '…')
