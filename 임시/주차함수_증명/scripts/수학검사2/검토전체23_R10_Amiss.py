# -*- coding: utf-8 -*-
# 본문에서 ":=" 로 정의된 이름 붙은 기호(로마체 이름·프락투어·산세리프·필기체) 가운데 부록 A에 핵이 없는 것을, 쓰인 절의 수와 함께 낸다(후보; 국소 기호일 수 있다).
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9']
A = open(os.path.join(base, '장v2', '부록A.md'), encoding='utf-8').read()
BS = chr(92)
pat = re.compile('(' + BS + BS + '(?:mathrm|mathfrak|mathsf|mathcal)(?:[{][A-Za-z]+[}]| [A-Za-z]))((?:[_^](?:[{][^{}]*(?:[{][^{}]*[}][^{}]*)*[}]|[A-Za-z0-9' + BS + BS + ']+))*)(?:[(][^()]*[)])?' + BS + 's*:=')
lines = []
for fn in files:
    sec = ''
    for i, line in enumerate(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+)', line)
        if m: sec = m.group(1)
        lines.append((sec, fn, i, line))
defs = {}
for sec, fn, i, line in lines:
    for m in pat.finditer(line):
        core = m.group(1) + m.group(2)
        defs.setdefault(core, (sec, fn, i))
def n(s): return s.replace(' ', '').replace('{', '').replace('}', '')
nA = n(A)
out = []
for core, (sec, fn, i) in defs.items():
    base_core = core
    if n(core) in nA: continue
    # 첨자 없는 머리만으로도 A에 있는지
    head = re.match('(' + BS + BS + '(?:mathrm|mathfrak|mathsf|mathcal)(?:[{][A-Za-z]+[}]| [A-Za-z]))', core).group(1)
    secs = sorted(set(s for s, f, j, l in lines if core in l))
    chaps = sorted(set(s.split('.')[0] for s in secs))
    out.append((len(secs), core, sec, fn, i, secs, n(head) in nA))
for x in sorted(out, reverse=True):
    if x[0] >= 2: print('절 %d개 | %s | 정의 %s %s L%d | 쓰인 절 %s | 머리가 A에 %s' % (x[0], x[1], x[2], x[3], x[4], x[5], x[6]))
