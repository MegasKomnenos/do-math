# 1.2의 행 가운데 어느 글자도 7절 첫 열에 나오지 않는 행(후보). 넷째 필드는 1.2의 「기록의 글자」 열.
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
col1 = ' ¶ '.join(L[i].strip().strip('|').split(' | ')[0] for i in range(1236, 1430))
col1n = col1.replace('{', '').replace('}', '').replace(' ', '')
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
for i in range(48, 288):
    l = L[i]
    if not l.startswith('| $'): continue
    c = l.strip().strip('|').split(' | ')
    absent = []
    for t in toks(c[0]):
        core = t.split('(')[0].replace('{', '').replace('}', '').replace(' ', '')
        if core not in col1n: absent.append(t)
    if absent:
        print(i+1, '|', '; '.join(absent), '| 정의', c[3].strip()[:30], '| 기록 열:', c[-1].strip()[:260])
