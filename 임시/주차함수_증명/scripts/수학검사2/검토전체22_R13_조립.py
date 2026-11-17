# R13 보고 조립: 내 절(R13본/)과 보조 검토자 부분 보고(부분_S*.md)를 한 파일로 잇는다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = "C:/math/임시/주차함수_증명/"
D = W + "scripts/수학검사2/"
ns = {}
exec(compile(open(D+"R13본/notes.py", encoding='utf-8').read(), 'notes', 'exec'), ns)
NOTES = ns['NOTES']
def rd(p):
    t = open(p, encoding='utf-8', newline='').read()
    t = t.replace(chr(13)+chr(10), chr(10))
    BS = chr(92)
    for ch, name in ((chr(13), 'r'), (chr(8), 'b'), (chr(11), 'v'), (chr(12), 'f'), (chr(7), 'a'), (chr(9), 't')):
        t = t.replace(ch, BS + name)
    t = re.sub('(?<=[^'+chr(10)+'])'+chr(10)+'ho(?=[)$])', (lambda m: BS+'rho'), t)
    return t.rstrip(chr(10))
def split(tag):
    L = rd(D+f"검토전체22_R13_부분_{tag}.md").split('\n')
    idx = [(i, l) for i, l in enumerate(L) if l.startswith('## ')]
    sec = {}
    for n, (i, l) in enumerate(idx):
        j = idx[n+1][0] if n+1 < len(idx) else len(L)
        m = re.match(r'^## (\d)\.', l)
        key = m.group(1) if m else 'x'
        sec[key] = L[i+1:j]
    return sec
def demote(lines, extra=1):
    out = []
    for l in lines:
        if re.match(r'^#{2,5} ', l): l = '#'*extra + l
        out.append(l)
    return '\n'.join(out).strip('\n')
S = {t: split(t) for t in ['S1','S2','S3','S4','S5','S6','S7']}
# S7-5 제거
l7 = S['S7']['2']
a = next(i for i, l in enumerate(l7) if l.startswith('**S7-5.'))
b = next(i for i, l in enumerate(l7) if l.startswith('**S7-6.'))
S['S7']['2'] = l7[:a] + ['(S7-5는 R13의 재확인에서 기록 원문으로 반증되어 뺐다 — 이 절 머리와 3.1절.)', ''] + l7[b:]
names = {'S1':'S1 — 장부 1.1·1.2 앞 절반','S2':'S2 — 장부 1.2 뒤 절반','S3':'S3 — 장부 1.3(1–5장)','S4':'S4 — 장부 1.3(6–7장)','S5':'S5 — 장부 1.3(8–9장·부록 D)','S6':'S6 — 장부 2·3절','S7':'S7 — 장부 7·8절'}
out = [rd(D+"R13본/1_범위.md"), '']
for f in ['2a_대응표','2b_의존지도','2c_구조표','2d_장부_0456']:
    out += [rd(D+f"R13본/{f}.md"), '']
for t in S:
    h, note = NOTES[t]
    out += [h, '', note, '', demote(S[t]['2']), '']
def tail(mainfile, key, base, title):
    o = [rd(D+f"R13본/{mainfile}.md"), '']
    for n, t in enumerate(S, 2):
        body = demote(S[t].get(key, []))
        if not body.strip(): body = '없음.'
        o += [f"### {base}.{n} {names[t]}", '', body, '']
    return o
x3 = tail('3_옳았던것', '3', '3', '')
out += x3
out += tail('4_사용자판단', '4', '4', '')
out += tail('5_범위밖', '5', '5', '')
out += [rd(D+"R13본/6_수.md"), '']
for t in S:
    body = demote(S[t].get('6', []))
    if body.strip(): out += [f"### 확인하지 못한 것 — {names[t]}", '', body, '']
txt = '\n'.join(out) + '\n'
open(W+"대조v2/수학검사2/검토전체22_R13.md", 'w', encoding='utf-8', newline=chr(10)).write(txt)
print(len(txt), 'chars', txt.count('\n'), 'lines')
print([ (t, {k: len(v) for k, v in S[t].items()}) for t in S ])
