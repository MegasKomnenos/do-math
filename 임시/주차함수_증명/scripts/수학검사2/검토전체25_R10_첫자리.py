# 고정 문자열 토큰마다 본문(장1–장9)에서 처음 나오는 자리와 「:=」로 정의되는 자리를 보여 준다. 자리 찾기용(판정은 원문을 읽고 한다).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
names = ['1','2','3','4','5A','5B','6','7A','7B','8','9']
lines = []
for c in names:
    sec = ''
    for i, ln in enumerate(open(base + f'장{c}.md', encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5} (\d+(?:\.\d+)*)', ln)
        if m: sec = m.group(1)
        lines.append((f'장{c}', i, sec, ln))
for spec in sys.argv[1:]:
    exp, tok = spec.split('=', 1) if re.match(r'[\d.]+=', spec) else ('', spec)
    hits = [(f, i, s, ln) for f, i, s, ln in lines if tok in ln]
    if not hits: print(f'[{tok}] exp {exp}: NONE'); continue
    f, i, s, ln = hits[0]
    j = ln.find(tok)
    secs = []
    for h in hits:
        if h[2] not in secs: secs.append(h[2])
    flag = '' if (not exp or s == exp or s.startswith(exp + '.')) else '  <<< DIFF'
    print(f'[{tok}] exp {exp} first {f}:{i} §{s}{flag} | n={len(hits)} secs={secs[:14]}')
    print('    …' + ln[max(0, j-90):j+len(tok)+90] + '…')
