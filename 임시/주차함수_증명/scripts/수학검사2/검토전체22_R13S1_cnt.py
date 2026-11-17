# S1 검산 도구: 고정 문자열(여러 철자)을 장 파일별로 세어 장 단위로 합산하고, 자리(행·절·앞뒤 글)를 보인다.
# 사용: python -I 검토전체22_R13S1_cnt.py [-b] [-n 표시수] [-c 장번호|파일명] [-w 폭] 문자열1 [문자열2 ...]
#  -b: 맨 글자 모드 — 바로 앞이 라틴 글자이거나 \명령(뒤 공백·여는 중괄호 포함)이면 세지 않는다
#      (\mathfrak a_n, \Theta_n, \gamma_j 같은 다른 기호의 부분 문자열을 거른다).
#  -n 0 이면 장별 합계와 파일별 수·절만 보인다.
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
FILES = [('1','장1'),('2','장2'),('2','부록D_장2'),('3','장3'),('3','부록D_장3'),('4','장4'),('4','부록D_장4'),
         ('5','장5A'),('5','장5B'),('5','부록D_장5A'),('6','장6'),('7','장7A'),('7','장7B'),('7','부록D_장7A'),('7','부록D_장7B'),
         ('8','장8'),('8','부록D_장8'),('9','장9'),('9','부록D_장9'),('10','장10')]
args = sys.argv[1:]
BARE = False; maxshow = 0; only = None; ctx = 60
while args and args[0] in ('-n','-c','-w','-b'):
    if args[0] == '-b': BARE = True; args = args[1:]; continue
    if args[0] == '-n': maxshow = int(args[1])
    elif args[0] == '-c': only = args[1]
    else: ctx = int(args[1])
    args = args[2:]
pats = args
BS = chr(92)  # 역슬래시(heredoc이 겹역슬래시를 하나로 줄여서 chr로 적는다)
prevre = re.compile('(' + BS + BS + '[A-Za-z]+' + BS + 's*' + BS + '{?' + BS + 's*|[A-Za-z])$')
secre = re.compile(r'^(#{2,4})\s+(\S+)')
def occ(line, pat):
    out = []; st = 0
    while True:
        j = line.find(pat, st)
        if j < 0: break
        if not (BARE and prevre.search(line[max(0, j-30):j])): out.append(j)
        st = j + len(pat)
    return out
tot = {}; rows = []
for ch, fn in FILES:
    if only and ch != only and fn != only: continue
    p = os.path.join(BASE, fn + '.md')
    sec = ''; hits = []
    for i, line in enumerate(io.open(p, encoding='utf-8'), 1):
        m = secre.match(line)
        if m: sec = m.group(2)[:14]
        for pat in pats:
            for j in occ(line, pat):
                hits.append((i, sec, line[max(0, j-ctx):j+len(pat)+ctx].replace('\n', ' ')))
    if hits:
        tot[ch] = tot.get(ch, 0) + len(hits)
        secs = []
        for h in hits:
            if h[1] not in secs: secs.append(h[1])
        rows.append(('%s:%d(첫 %d행; %s)' % (fn, len(hits), hits[0][0], ','.join(secs[:14])), hits))
print('## ' + ' | '.join(pats) + ('  [맨 글자]' if BARE else ''))
print('   장: ' + ', '.join('%s(%d)' % (c, tot[c]) for c in ['1','2','3','4','5','6','7','8','9','10'] if c in tot))
for head, hits in rows:
    print('     ' + head)
    for h in hits[:maxshow]:
        print('        %d(%s): …%s…' % h)
