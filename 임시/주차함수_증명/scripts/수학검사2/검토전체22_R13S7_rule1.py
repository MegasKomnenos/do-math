# 8절 규칙 1의 「1.2의 기호 28개」: 정의 절이 1장 밖인 1.2 기호 가운데 장1.md에 나타나는 것을 센다(후보; 핵 문자열의 고정 검색)
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
ch1 = open('장v2/장1.md', encoding='utf-8').read()
norm = lambda s: s.replace('{', '').replace('}', '').replace(' ', '')
ch1n = norm(ch1)
def toks(cell):
    out = []
    for seg in re.findall(r'\$([^$]+)\$', cell):
        depth = 0; cur = ''
        for ch in seg:
            if ch in '({[': depth += 1
            if ch in ')}]': depth -= 1
            if ch == ',' and depth == 0:
                out.append(cur); cur = ''
            else: cur += ch
        out.append(cur)
    return [o.strip() for o in out if o.strip()]
rows = 0; syms = []
for i in range(48, 288):
    l = L[i]
    if not l.startswith('| $'): continue
    c = l.strip().strip('|').split(' | ')
    sec = c[3].strip()
    m = re.match(r'(\d+)\.', sec)
    if not m or m.group(1) == '1': continue
    hit = []
    for t in toks(c[0]):
        core = norm(t.split('(')[0])
        core2 = re.sub(r'_[a-zA-Z]$|_[a-z],[a-z]$', '', core)
        n = ch1n.count(core)
        if n: hit.append((t, n))
    if hit:
        rows += 1; syms += hit
        print(i+1, sec[:25], '| 쓰이는 장:', c[4].strip()[:28], '|', hit)
print('행', rows, '기호', len(syms))
