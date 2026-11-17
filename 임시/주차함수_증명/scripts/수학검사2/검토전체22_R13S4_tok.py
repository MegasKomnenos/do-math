# 장부 1.3절 한 행의 첫째 열(또는 지정 열)에서 $...$ 토큰을 뽑아 장 파일에서 고정 문자열로 세는 보조 도구(자리 찾기용; 판정은 원문을 읽어 한다).
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
row = int(sys.argv[1]); col = int(sys.argv[2]) if len(sys.argv) > 2 else 1
files = sys.argv[3:] or ['장v2/장6.md', '장v2/장7A.md', '장v2/장7B.md']
line = open('장부_v2.md', encoding='utf-8').read().split('\n')[row-1]
# 열 가르기: ' | ' 로 가르되 수식 안의 | 는 드물다고 보고 단순 분리 후 열 수 확인
cells = line.strip().strip('|').split(' | ')
print('열 수', len(cells), '(4여야 함)')
cell = cells[col-1]
toks = re.findall(r'\$([^$]+)\$', cell)
texts = {}
for f in files:
    L = open(f, encoding='utf-8').read().split('\n')
    sec = ''
    secs = []
    for l in L:
        m = re.match(r'^###\s+(\S+)', l)
        if m: sec = m.group(1)
        secs.append(sec)
    texts[f] = (L, secs)
seen = set()
for t in toks:
    core = re.split(r':?=', t)[0].strip()
    for c in dict.fromkeys([t, core]):
        if c in seen: continue
        seen.add(c)
        out = []
        for f, (L, secs) in texts.items():
            hits = [(i+1, secs[i]) for i, l in enumerate(L) if c in l]
            if hits:
                bysec = {}
                for ln, s in hits: bysec.setdefault(s, []).append(ln)
                out.append(f.split('/')[-1] + ': ' + '; '.join(f"{s}[{len(v)}줄: {','.join(map(str, v[:6]))}{'…' if len(v) > 6 else ''}]" for s, v in bysec.items()))
        print(f"  {c!r:60s} -> {' | '.join(out) if out else '없음'}")
