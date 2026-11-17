# 부록 A 「기록의 글자」 열의 (기호, 기록) 쌍이 부록 C 글자 표에 있는지 찾는다. 없는 쌍은 원문을 열어 읽는다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
def cells(ln):
    out = []; buf = ''; inm = False
    for ch in ln:
        if ch == '$': inm = not inm
        if ch == '|' and not inm: out.append(buf); buf = ''
        else: buf += ch
    out.append(buf)
    return [c.strip() for c in out[1:-1]]
def core(s):
    # 기호의 뼈대: 수식에서 공백·중괄호·인수 괄호·첨자 변수를 느슨하게
    s = re.sub(r'\s+', '', s)
    BS = chr(92)
    s = s.replace('{', '').replace('}', '').replace(BS + 'prime', "'").replace('^' + BS + 'ast', '^*')
    return s
C = open(base + '부록C.md', encoding='utf-8').read().split('\n')
cs = C.index('### 기록의 글자와 이 글의 글자'); ce = C.index('### 영어를 함께 적은 낱말')
crow = []
for i in range(cs, ce):
    if C[i].startswith('| ') and not C[i].startswith('| 이 글의 글자') and not C[i].startswith('|---'):
        c = cells(C[i]); crow.append((i+1, c))
A = open(base + '부록A.md', encoding='utf-8').read().split('\n')
def heads(sym):
    # 기호 셀의 수식 조각들의 '머리'(첫 매크로나 글자)
    hs = set()
    for m in re.finditer(r'\$([^$]+)\$', sym):
        for part in re.split(r',\s*', m.group(1)):
            p = core(part)
            BS = chr(92)
            k = 0
            if p.startswith(BS):
                k = 1
                while k < len(p) and p[k].isalpha(): k += 1
                # \mathrm X 꼴이면 다음 토큰까지
                if p[:k] in (BS+'mathrm', BS+'mathfrak', BS+'mathcal', BS+'mathsf', BS+'mathbb', BS+'widehat', BS+'tilde', BS+'bar', BS+'hat'):
                    if k < len(p) and p[k] == BS:
                        k += 1
                        while k < len(p) and p[k].isalpha(): k += 1
                    else:
                        while k < len(p) and p[k].isalpha(): k += 1
            else:
                k = 1
            mm = p[:k]
            hs.add(p); 
            if mm and len(mm) > 1: hs.add(mm)
    return hs
miss = 0; total = 0
for i, ln in enumerate(A):
    if not ln.startswith('| $') and not ln.startswith('| ('): continue
    c = cells(ln)
    if len(c) != 4 or c[3] == '—': continue
    sym = c[0]; hs = heads(sym)
    rids = sorted(set(re.findall(r'\[(r[0-9a-f]{7})\]', c[3])))
    for rid in rids:
        total += 1
        found = False
        for ln2, cc in crow:
            if '[' + rid + ']' in cc[1]:
                ccore = core(cc[0])
                if any(h and h in ccore for h in hs): found = True; break
        if not found:
            miss += 1
            print(f'A:{i+1} {sym} / [{rid}] — C에 같은 기호·기록 행 없음')
print('pairs', total, 'miss', miss)
