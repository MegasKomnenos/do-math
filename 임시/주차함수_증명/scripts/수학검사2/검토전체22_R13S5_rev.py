# 장 파일의 글자(프락투어·필기체·산세리프·로마체 이름)를 뽑아 장부에 같은 고정 문자열이 있는지 본다(후보 목록일 뿐; 판정은 원문으로).
# 정규식의 역슬래시는 '@'로 적고 실행 때 바꾼다.
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS = chr(92)
def R(p): return re.compile(p.replace('@', BS + BS))
led = open('장부_v2.md', encoding='utf-8').read()
dec = '(?:[_^](?:[{][^{}]*(?:[{][^{}]*[}][^{}]*)*[}]|@[a-zA-Z]+|[A-Za-z0-9*]))*'
pat = R('(@(?:mathfrak|mathcal|mathsf) [A-Za-z]|@mathrm[{][A-Za-z]+[}])(' + dec + ')')
for f in sys.argv[1:]:
    txt = open('장v2/' + f, encoding='utf-8').read()
    seen = {}
    for t in pat.finditer(txt):
        tok = t.group(1) + t.group(2)
        seen[tok] = seen.get(tok, 0) + 1
    miss = []
    for tok, c in sorted(seen.items()):
        if tok in led: continue
        base = pat.match(tok).group(1)
        m2 = R('^(.+?)([_^](?:[{][^{}]*(?:[{][^{}]*[}][^{}]*)*[}]|@[a-zA-Z]+|.))').match(tok)
        key = m2.group(0) if m2 else base
        if key in led: continue
        miss.append((tok, c, base in led))
    print(f, '— 장부에 (바탕+첫 장식) 문자열이 없는 후보:', len(miss))
    for tok, c, b in miss: print('   ', tok, c, '(바탕 글자는 장부에 있음)' if b else '(바탕 글자도 장부에 없음)')
