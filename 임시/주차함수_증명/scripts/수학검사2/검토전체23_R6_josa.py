# 수식 바로 뒤 조사가 수식 끝 글자의 받침과 맞는지 의심 자리를 뽑는다(자리 찾기 전용; 판정은 원문을 읽고 한다).
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = sys.argv[1]
BS = chr(92)
bat = set('LMNRlmnr')            # 엘 엠 엔 알
nob = set('ABCDEFGHIJKOPQSTUVWXYZabcdefghijkopqstuvwxyz')
dig_b = set('013678'); dig_n = set('2459')
greek_nob = {'alpha','beta','gamma','delta','zeta','eta','theta','vartheta','iota','kappa','lambda','mu','nu','xi','pi','rho','varrho','sigma','varsigma','tau','phi','varphi','chi','psi','omega','Gamma','Lambda','Omega','Psi','Phi','Pi','Sigma','Theta','sharp'}
greek_bat = {'epsilon','varepsilon','upsilon','flat'}
P_no = ['는','가','를','라 ','라고','와']
P_yes = ['은','을','이라','과','으로']
pat = re.compile('[$]([^$]+)[$]([가-힣]{1,3}[ .,]?)')
strip = re.compile('[{}() ' + BS + ']' + ']|' + BS + BS + '[,;!]')
cmd = re.compile(BS + BS + '([A-Za-z]+)$')
for ln, line in enumerate(open(path, encoding='utf-8'), 1):
    for m in pat.finditer(line):
        math, post = m.group(1), m.group(2)
        s = math
        for f in ['mathfrak','mathcal','mathsf','mathrm','mathbb','tilde','bar','hat','widetilde']:
            s = s.replace(BS + f, '')
        for junk in ['{', '}', ' ', ')', ']', "'", '′', BS + ',', BS + ';', BS + '!', BS + 'bigr', BS + 'Bigr', BS + 'rvert']:
            s = s.replace(junk, '')
        mc = cmd.search(s)
        if mc:
            name = mc.group(1)
            if name in greek_nob: last = 'nob'
            elif name in greek_bat: last = 'bat'
            else: continue
        else:
            c = s[-1] if s else ''
            if c in bat or c in dig_b: last = 'bat'
            elif c in nob or c in dig_n: last = 'nob'
            else: continue
        bad = None
        if last == 'bat':
            for p in P_no:
                if post.startswith(p.strip()) and not any(post.startswith(q.strip()) for q in P_yes): bad = p
            if bad and bad.strip().startswith('로') and (s[-1:] in 'LRlr178'): bad = None
        else:
            for p in P_yes:
                if post.startswith(p.strip()): bad = p
        if bad:
            print(str(ln) + ': $' + math[-40:] + '$ + ' + repr(post))
