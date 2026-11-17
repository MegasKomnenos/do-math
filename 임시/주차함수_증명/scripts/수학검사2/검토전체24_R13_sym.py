# -*- coding: utf-8 -*-
# R13: 장부 1.2 각 행의 기호를 (바탕, 위첨자, 이름 아래첨자) 열쇠로 바꿔 장 파일(+그 장의 부록 D)에서 세고
#      「쓰이는 장」 열과 맞댄다. 어긋남은 사람이 원문으로 확인할 후보일 뿐이다.
import re, sys, io, collections
BASE = r'C:/math/임시/주차함수_증명/'
CH = {1:['장1'],2:['장2','부록D_장2'],3:['장3','부록D_장3'],4:['장4','부록D_장4'],5:['장5A','장5B','부록D_장5A'],6:['장6'],7:['장7A','장7B','부록D_장7A','부록D_장7B'],8:['장8','부록D_장8'],9:['장9','부록D_장9'],10:['장10']}
FONT = ('mathfrak','mathsf','mathcal','mathrm','mathscr','mathbb','operatorname','widehat','hat','tilde','bar','widetilde','overline')
CMD = re.compile(r'\\[A-Za-z]+|\\.')
def skip_ws(s, i):
    while i < len(s) and s[i] in ' \t': i += 1
    return i
def read_group(s, i):
    depth = 0; j = i
    while j < len(s):
        if s[j] == '{': depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0: return s[i+1:j], j+1
        j += 1
    return s[i+1:], len(s)
def read_atom(s, i):
    i = skip_ws(s, i)
    if i >= len(s): return '', i
    if s[i] == '{':
        g, j = read_group(s, i); return g.strip(), j
    if s[i] == '\\':
        m = CMD.match(s[i:])
        cmd = m.group(0); j = i + len(cmd)
        if cmd[1:] in FONT:
            a, j = read_atom(s, j)
            return cmd + '{' + a + '}', j
        return cmd, j
    return s[i], i+1
def norm(x):
    return re.sub(r'\s+', '', x)
NAMED_SUB = re.compile(r'^(\\mathrm\{.*\}|\\max|\\min|\\ast|\\infty|\\star|\\circ|\\le|\\ge|>|<|\\Psi|0|\*|\\flat|\\sharp)$')
def scan(s):
    i = 0; out = []
    while i < len(s):
        c = s[i]
        if c == '\\':
            m = CMD.match(s[i:])
            cmd = m.group(0)
            if cmd[1:] in FONT:
                a, j = read_atom(s, i + len(cmd))
                base = cmd + '{' + norm(a) + '}'
            else:
                base = cmd; j = i + len(cmd)
        elif c.isalpha() and c.isascii():
            base = c; j = i + 1
        else:
            i += 1; continue
        sup = ''; sub = ''
        k = j
        while True:
            k2 = skip_ws(s, k)
            if k2 < len(s) and s[k2] == '^':
                a, k = read_atom(s, k2 + 1); sup = norm(a); continue
            if k2 < len(s) and s[k2] == '_':
                a, k = read_atom(s, k2 + 1); sub = norm(a); continue
            if k2 < len(s) and s[k2] == "'":
                sup += "'"; k = k2 + 1; continue
            break
        nsub = sub if NAMED_SUB.match(sub) else ''
        out.append((base, sup, nsub, sub))
        i = j
    return out
def math_segments(text):
    text = re.sub(r'\{\{[^}]*\}\}', ' ', text)
    segs = re.findall(r'\$\$(.+?)\$\$|\$([^$]+)\$', text, flags=re.S)
    return [a or b for a, b in segs]
def chapter_counts():
    cnt = {}
    for ch, files in CH.items():
        c = collections.Counter()
        for f in files:
            t = open(BASE + '장v2/' + f + '.md', encoding='utf-8').read()
            for seg in math_segments(t):
                for b, sp, ns, sb in scan(seg):
                    c[(b, sp, ns)] += 1
                    c[(b, sp, '*')] += 1
                    c[(b, '*', '*')] += 1
        cnt[ch] = c
    return cnt
def split_top(cell):
    cell = cell.strip().strip('$')
    out = []; depth = 0; cur = ''
    for ch in cell:
        if ch in '{([': depth += 1
        elif ch in '})]': depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else: cur += ch
    out.append(cur.strip())
    return out
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
    cnt = chapter_counts()
    L = open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
    a, b = int(sys.argv[1]), int(sys.argv[2])
    col = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    for i in range(a, b + 1):
        line = L[i-1]
        if not line.startswith('|'): continue
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        listed = sorted(int(x) for x in re.findall(r'\d+', c[col]))
        for sym in split_top(c[0]):
            ks = scan(sym)
            if not ks: print(i, 'NOKEY', sym); continue
            base, sup, ns, sb = ks[0]
            key = (base, sup, ns if ns else '*')
            found = sorted(ch for ch in cnt if cnt[ch][key] > 0)
            if found != listed:
                extra = [(ch, cnt[ch][key]) for ch in found if ch not in listed]
                missing = [ch for ch in listed if ch not in found]
                print(i, sym, 'key', key, '| listed', listed, '| extra(장에 있으나 열에 없음)', extra, '| missing(열에 있으나 장에 없음)', missing)
