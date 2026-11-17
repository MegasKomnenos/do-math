# S1 검산 도구: 수식($...$, $$...$$) 안의 「맨 이탤릭 한 글자」를 장별로 센다.
# 글자체 명령의 인수(\mathfrak m, \mathrm{...}, \text{...} 등)와 \명령 이름은 지운 뒤, 앞뒤가 라틴 글자가 아닌 한 글자만 센다.
# 사용: python -I 검토전체22_R13S1_let.py [-c 장|파일 [-n 표시수]] 글자1 [글자2 ...]
#   -s: 첨자 자리(바로 앞이 _ 또는 _{ ... 안)의 출현을 따로 세지 않고 뺀다(옵션).
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
FILES = [('1','장1'),('2','장2'),('2','부록D_장2'),('3','장3'),('3','부록D_장3'),('4','장4'),('4','부록D_장4'),
         ('5','장5A'),('5','장5B'),('5','부록D_장5A'),('6','장6'),('7','장7A'),('7','장7B'),('7','부록D_장7A'),('7','부록D_장7B'),
         ('8','장8'),('8','부록D_장8'),('9','장9'),('9','부록D_장9'),('10','장10')]
BS = chr(92)
a = sys.argv[1:]; only = None; show = 0
while a and a[0] in ('-c', '-n'):
    if a[0] == '-c': only = a[1]
    else: show = int(a[1])
    a = a[2:]
letters = a
fontre = re.compile(BS + BS + '(mathfrak|mathsf|mathcal|mathrm|mathbb|mathbf|mathscr|text|operatorname|mathit|texttt|boldsymbol)' + BS + 's*(' + BS + '{[^{}]*' + BS + '}|[A-Za-z0-9])')
cmdre = re.compile(BS + BS + '[A-Za-z]+')
codere = re.compile('`[^`]*`')
secre = re.compile(r'^(#{2,4})\s+(\S+)', re.M)
def blank(m): return ' ' * len(m.group(0))
tot = {l: {} for l in letters}
for ch, fn in FILES:
    if only and ch != only and fn != only: continue
    s = io.open(os.path.join(BASE, fn + '.md'), encoding='utf-8').read()
    s2 = codere.sub(blank, s)
    # 수식 구간 표시
    mask = [False] * len(s2)
    i = 0; inmath = False; disp = False
    while i < len(s2):
        if s2.startswith('$$', i):
            if not inmath: inmath = True; disp = True
            elif disp: inmath = False
            i += 2; continue
        if s2[i] == '$':
            if not inmath: inmath = True; disp = False
            elif not disp: inmath = False
            i += 1; continue
        if inmath: mask[i] = True
        i += 1
    s3 = fontre.sub(blank, s2)
    s3 = cmdre.sub(blank, s3)
    secs = [(m.start(), m.group(2)[:10]) for m in secre.finditer(s)]
    def secof(pos):
        r = ''
        for st, nm in secs:
            if st <= pos: r = nm
            else: break
        return r
    for l in letters:
        hits = []
        for m in re.finditer('(?<![A-Za-z])' + re.escape(l) + '(?![A-Za-z])', s3):
            if mask[m.start()]:
                hits.append(m.start())
        if hits:
            tot[l][ch] = tot[l].get(ch, 0) + len(hits)
            if only:
                ss = []
                for h in hits:
                    x = secof(h)
                    if x not in ss: ss.append(x)
                print('[%s] %s %s: %d건; 절 %s' % (l, ch, fn, len(hits), ' '.join(ss[:20])))
                for h in hits[:show]:
                    ln = s.count('\n', 0, h) + 1
                    print('    %d(%s): …%s…' % (ln, secof(h), s[max(0, h-70):h+70].replace('\n', ' ')))
for l in letters:
    print('%s: %s' % (l, ', '.join('%s(%d)' % (c, tot[l][c]) for c in ['1','2','3','4','5','6','7','8','9','10'] if c in tot[l])))
