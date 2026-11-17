# 부록 A의 행마다 기호의 머리 토큰을 고정 문자열로 장 파일에서 찾아 처음 나오는 절을 「처음 정의된 절」 칸과 견준다.
# 자리 찾기용이다. 어긋난 행은 원문을 열어 손으로 확인한다.
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
def first(tok, k=3):
    out = []
    for n, i, sec, l in docs:
        if tok in l:
            out.append((n, i, sec))
            if len(out) >= k: break
    return out
rows = []
for i, l in enumerate(open(base+'부록A.md', encoding='utf-8').read().split('\n')):
    if not l.startswith('| $'): continue
    c0 = l[2:].split(' | ')[0]
    rest = l.rstrip().rstrip('|').rstrip()
    parts = rest.rsplit(' | ', 2)
    sec = parts[-2]
    rows.append((i+1, c0, sec))
def heads(c0):
    s = c0.strip().strip('$')
    # 쉼표로 나눈 첫 항목만(괄호 안 쉼표는 보존)
    depth = 0; cur = ''; items = []
    for ch in s:
        if ch in '({[': depth += 1
        if ch in ')}]': depth -= 1
        if ch == ',' and depth == 0:
            items.append(cur.strip()); cur = ''
        else: cur += ch
    items.append(cur.strip())
    res = []
    for it in items:
        h = re.sub(r'\([^()]*\)$', '', it).strip()   # 끝의 인수 괄호를 뗀다
        h = re.sub(r':?=.*$', '', h).strip()
        res.append(h)
    return res
show_all = len(sys.argv) > 1
for ln, c0, sec in rows:
    claimed = re.findall(r'\d+\.\d+', sec)
    for h in heads(c0):
        if len(h) <= 1 or re.fullmatch(r'\?[A-Za-z]+', h) and len(h) <= 6:
            tag = 'SKIP(짧음)'
            if show_all: print(f'A:{ln} {h!r} claimed={sec} {tag}')
            continue
        f = first(h)
        got = f[0][2] if f else None
        # 절 번호의 앞 두 마디만 비교(5.2.2 → 5.2)
        g2 = '.'.join(got.split('.')[:2]) if got else None
        ok = g2 in claimed
        if show_all or not ok:
            print(f'A:{ln} {h!r} claimed={sec!r} first={f}')
