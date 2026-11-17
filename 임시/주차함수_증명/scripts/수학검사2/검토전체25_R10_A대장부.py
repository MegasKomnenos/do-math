# 부록 A의 행을 장부 1.1·1.2의 같은 기호 행과 맞대어 뜻·정의 절·기록의 글자가 다른 행을 보여 준다(다른 행은 원문을 열어 읽는다).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/'
def cells(ln):
    # 수식 안의 | 를 보호: $...$ 안의 | 는 치환
    out = []; buf = ''; inm = False
    for ch in ln:
        if ch == '$': inm = not inm
        if ch == '|' and not inm:
            out.append(buf); buf = ''
        else: buf += ch
    out.append(buf)
    return [c.strip() for c in out[1:-1]]
J = open(base + '장부_v2.md', encoding='utf-8').read().split('\n')
s11 = J.index('### 1.1 변수·지표 글자'); s12 = [i for i, l in enumerate(J) if l.startswith('### 1.2')][0]; s13 = [i for i, l in enumerate(J) if l.startswith('### 1.3')][0]
led = {}
for i in range(s11, s12):
    if J[i].startswith('| $'):
        c = cells(J[i]); led[c[0]] = dict(mean=c[1], sec=None, rec=None, line=i+1, n=len(c))
for i in range(s12, s13):
    if J[i].startswith('| '):
        c = cells(J[i])
        if len(c) >= 7 and c[0] not in ('글자(LaTeX)',) and not c[0].startswith('---'):
            led[c[0]] = dict(mean=c[2], sec=c[3], rec=c[6], line=i+1, n=len(c))
A = open(base + '장v2/부록A.md', encoding='utf-8').read().split('\n')
na = 0; miss = []
seenA = set()
for i, ln in enumerate(A):
    if not ln.startswith('| $') and not ln.startswith('| ('):
        continue
    c = cells(ln); na += 1
    if len(c) != 4: print('A row', i+1, 'cells', len(c)); continue
    sym, mean, sec, rec = c
    seenA.add(sym)
    if sym not in led: miss.append((i+1, sym)); continue
    L = led[sym]
    d = []
    if L['mean'] != mean: d.append(('뜻', mean, L['mean']))
    if L['sec'] is not None and L['sec'] != sec: d.append(('절', sec, L['sec']))
    if L['rec'] is not None and L['rec'] != rec: d.append(('기록', rec, L['rec']))
    for k, a, b in d:
        import difflib
        na_ = a.replace('`','').replace('; x', ';x').replace('; n', ';n').replace('; k', ';k').replace('; \eta', ';\eta')
        nb_ = b.replace('`','').replace('; x', ';x').replace('; n', ';n').replace('; k', ';k').replace('; \eta', ';\eta')
        if na_ == nb_: continue
        sm = difflib.SequenceMatcher(None, na_, nb_, autojunk=False)
        ops = [(t, na_[i1:i2], nb_[j1:j2]) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']
        print(f'--- A:{i+1} 장부:{L["line"]} {sym} [{k}]')
        for t, x, y in ops:
            print(f'   {t}: A「{x[:300]}」 장부「{y[:300]}」')
print('A rows', na, 'ledger rows', len(led))
print('A symbols not in ledger:', miss)
print('ledger 1.2 symbols not in A:', [(k, v['line']) for k, v in led.items() if k not in seenA])
