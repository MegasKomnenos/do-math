# -*- coding: utf-8 -*-
# R13: 장부 1.2 「정의 절」을 장 파일에서 그 기호가 (정의 꼴 ':=' 또는 처음) 나오는 절과 맞댄다. 후보만 낸다.
import re, sys, io, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('s', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_sym.py')
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
BASE = S.BASE
FILES = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
sec_re = re.compile(r'^(#{2,3}) (\d+(?:\.\d+)*)\.? ')
first2 = {}
first = {}      # key -> (sec, file, line)
secs = collections.defaultdict(lambda: collections.Counter())  # key -> Counter(sec)
for f in FILES:
    t = open(BASE + '장v2/' + f + '.md', encoding='utf-8').read()
    # 줄 시작 오프셋과 절
    offs = []; sec = None; pos = 0
    for ln, line in enumerate(t.split(chr(10)), 1):
        m = sec_re.match(line)
        if m:
            sec = m.group(2) + ('.0' if m.group(1) == '##' else '')
        offs.append((pos, ln, sec)); pos += len(line) + 1
    import bisect
    starts = [o[0] for o in offs]
    t2 = re.sub(r'\{\{[^}]*\}\}', lambda m: ' ' * len(m.group(0)), t)
    for mm in re.finditer(r'\$\$(.+?)\$\$|\$([^$]+)\$', t2, flags=re.S):
        seg = mm.group(1) or mm.group(2)
        _, ln, sec = offs[bisect.bisect_right(starts, mm.start()) - 1]
        for bs, sp, ns, sb in S.scan(seg):
            for k in ((bs, sp, ns), (bs, sp, '*')):
                if k not in first: first[k] = (sec, f, ln)
                if sec and not sec.startswith('1.') and not sec.endswith('.0') and k not in first2: first2[k] = (sec, f, ln)
                secs[k][sec] += 1
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
for i in range(49, 288):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    dsecs = re.findall(r'\d+\.\d+', c[3])
    for sym in S.split_top(c[0]):
        ks = S.scan(sym)
        base, sup, ns, sb = ks[0]
        if len(base) == 1 and not sup and not ns: continue   # 한 글자 바탕은 판정 불가
        key = (base, sup, ns if ns else '*')
        if key not in first:
            print(i, sym, '장 파일에 없음(열쇠 %s)' % (key,)); continue
        fs = first2.get(key, first[key])[0]
        if dsecs and dsecs[0].startswith('1.'): fs = first[key][0]
        if fs not in dsecs:
            used = sorted(secs[key].items(), key=lambda kv: [int(x) for x in kv[0].split('.')])
            print(i, sym, '| 장부 정의 절', c[3], '| 처음 나오는 절(1장·장 머리 밖)', first2.get(key, first[key]), '| 절별 횟수', used[:8])
