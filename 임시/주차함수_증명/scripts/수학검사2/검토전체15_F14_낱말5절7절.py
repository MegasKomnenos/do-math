# -*- coding: utf-8 -*-
"""F14: (1) 장부 3절 낱말의 첫 출현 절 대 「첫 정의 절」, (2) 5절 장별 전역 기호 대 1.2 정의 절,
(3) 7절 기록 집합 대 부록 B·1.2 기록 열, (4) 의존지도 2.1 라벨 수, (5) 문맥 보기."""
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH = [('장1','1'),('장2','2'),('장3','3'),('장4','4'),('장5A','5'),('장5B','5'),('장6','6'),('장7A','7'),('장7B','7'),('장8','8'),('장9','9'),('장10','10'),('장11','11')]
def rd(p):
    return open(p, encoding='utf-8').read()
jb = rd(os.path.join(ROOT, '장부_v2.md'))
sec_re = re.compile(r'^(#{2,4}) (\d+(?:\.\d+)*)[ .]')

# 장별·절별 본문(수식 제거한 산문)과 원문
prose_by_sec = []   # list of (seckey, text, file)
raw_by_sec = []
for fn, ch in CH:
    txt = rd(os.path.join(ROOT, '장v2', fn + '.md'))
    cur = ch
    buf = []; rbuf = []
    for line in txt.split('\n'):
        m = sec_re.match(line)
        if m:
            if buf:
                prose_by_sec.append((cur, '\n'.join(buf), fn)); raw_by_sec.append((cur, '\n'.join(rbuf), fn))
            cur = m.group(2); buf = []; rbuf = []
        rbuf.append(line)
        buf.append(re.sub(r'\$\$.+?\$\$|\$.+?\$', ' ', line))
    prose_by_sec.append((cur, '\n'.join(buf), fn)); raw_by_sec.append((cur, '\n'.join(rbuf), fn))
def seckey(s):
    return [int(x) for x in s.split('.')]

print('########## (1) 3절 낱말: 첫 정의 절보다 앞에서 나타나는 낱말')
s3 = jb[jb.index('## 3. 낱말 사전'):jb.index('## 4. 이름 사전')]
for line in s3.split('\n'):
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if not m or m.group(1) in ('낱말', '---'):
        continue
    words_raw, meaning, defsec, old = m.groups()
    if defsec.startswith('—') or '부록' in defsec:
        continue
    decl = [d.strip().split('(')[0].split('–')[0].strip() for d in re.split(r'[,;]', defsec) if re.match(r'\s*\d', d)]
    if not decl:
        continue
    dmin = min(decl, key=seckey)
    words = [w.strip() for w in re.split(r'[,;]', re.sub(r'\$.*?\$', '', words_raw)) if w.strip() and len(w.strip()) >= 2]
    for w in words:
        first = None
        for sec, text, fn in prose_by_sec:
            if w in text:
                if first is None or seckey(sec) < seckey(first[0]):
                    first = (sec, fn)
        if first is None:
            print(f'  [본문에 없음] 「{w}」 (첫 정의 절 {defsec})')
        elif seckey(first[0]) < seckey(dmin) and not first[0].startswith('1.4') and not first[0].startswith('1.5') and first[0] != '1':
            # 1.4·1.5의 미리 부름은 설계된 예외
            print(f'  「{w}」 첫 정의 절 {defsec} / 실제 첫 출현 {first[0]} ({first[1]})')

print('\n########## (2) 5절 장별 전역 기호 대 1.2 정의 절')
s12 = jb[jb.index('### 1.2 전역 기호'):jb.index('### 1.3 국소 기호')]
def12 = {}
for line in s12.split('\n'):
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if not m or m.group(1).startswith('글자') or m.group(1).startswith('---'):
        continue
    glyph, font, meaning, defsec, chs, old, rec = m.groups()
    chaps = set()
    for d in re.findall(r'(\d+)\.\d+', defsec):
        chaps.add(d)
    def12[glyph.strip()] = (chaps, defsec)
s5 = jb[jb.index('## 5. 장별 배정'):jb.index('## 6. 예약 글자')]
sec5 = {}
for line in s5.split('\n'):
    m = re.match(r'^\| (\d+) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if m:
        syms = [s.strip() for s in m.group(2).split(';')] if m.group(2).strip() != '없음' else []
        sec5[m.group(1)] = syms
for ch in sorted(sec5, key=int):
    listed = set(sec5[ch])
    expected = set(g for g, (chaps, _) in def12.items() if ch in chaps)
    only5 = listed - expected
    only12 = expected - listed
    if only5 or only12:
        print(f'  장{ch}: 5절에만 {sorted(only5)} / 1.2 정의 절 기준에만 {sorted(only12)}')
# 1.2에서 정의 절이 두 장에 걸친 것
for g, (chaps, d) in def12.items():
    if len(chaps) > 1:
        print('  1.2 정의 절이 두 장:', g, d)

print('\n########## (3) 7절 기록 집합 대 부록 B·1.2 기록 열')
s7 = jb[jb.index('## 7. 기록 글자 대응'):jb.index('## 8. 감사 규칙')]
rec7 = set(re.findall(r'\[(r[0-9a-f]{7})\]', s7))
rec7b = set(re.findall(r'\b(r[0-9a-f]{7})\b', s7))
appB = rd(os.path.join(ROOT, '장v2', '부록B.md'))
recB = set(re.findall(r'\b(r[0-9a-f]{7})\b', appB))
rec12 = set(re.findall(r'\[(r[0-9a-f]{7})\]', s12))
body = ''
for fn in ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11'] + [f'부록D_장{c}' for c in ['2','3','4','5A','5B','6','7A','7B','8','9','10']]:
    body += rd(os.path.join(ROOT, '장v2', fn + '.md'))
recBody = set(re.findall(r'\b(r[0-9a-f]{7})\b', body))
print('  7절 [r] 수', len(rec7), '/ 7절 r 토큰 수', len(rec7b), '/ 부록 B 수', len(recB), '/ 1.2 열 수', len(rec12), '/ 본문·부록 D 수', len(recBody))
print('  부록 B에만:', sorted(recB - rec7b))
print('  7절에만(부록 B에 없음):', sorted(rec7b - recB))
print('  1.2 열에만(7절에 없음):', sorted(rec12 - rec7b))
print('  7절에만(1.2 열에 없음):', sorted(rec7b - rec12))
print('  본문·부록D에만(부록 B에 없음):', sorted(recBody - recB))
print('  부록 B에만(본문·부록 D에 없음):', sorted(recB - recBody))
# 7절 행 수와 기록별 행 유무
rows7 = [l for l in s7.split('\n') if l.startswith('| $') or l.startswith('| ')]
print('  7절 표 행 수(대략)', len([l for l in s7.split('\n') if l.startswith('|') and not l.startswith('|---') and '이 글의 글자' not in l]))

print('\n########## (4) 의존지도 2.1 라벨 수')
dm = rd(os.path.join(ROOT, '의존지도_v2.md'))
s1 = dm[dm.index('## 1. 진술별 입력 표'):dm.index('### 1.1 뺌·대체된 라벨')]
labs = set()
for line in s1.split('\n'):
    m = re.match(r'^\| `\{\{(\d+):([A-Za-z0-9-]+)\}\}` \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|', line)
    if m:
        labs |= set(re.findall(r'\{\{(\d+:[A-Za-z0-9-]+)\}\}', m.group(6)))
print('  입력 열의 라벨(중복 제외)', len(labs))

print('\n########## (5) 문맥 보기')
def ctx(fn, s, w=140, maxn=4):
    txt = rd(os.path.join(ROOT, '장v2', fn + '.md'))
    n = 0
    for ln, line in enumerate(txt.split('\n'), 1):
        i = line.find(s)
        while i >= 0 and n < maxn:
            print(f'  {fn}:{ln}: …{line[max(0,i-w):i+len(s)+w]}…')
            n += 1
            i = line.find(s, i + 1)
    if n == 0:
        print(f'  {fn}: 「{s}」 없음')
for fn, s in [('장5A', r'U\times X'), ('장6', 'X:=(n+1)'), ('장5A', r'\beta'), ('장5B', r'\beta'), ('장6', r'\beta'), ('장5A', 'L_1'), ('장8', r'\Omega'), ('장2', 'b^{(2)}'), ('장11', '$t'), ('장2', '첫 층 나무')]:
    print('==', fn, s)
    ctx(fn, s)
print('== 장부 L_1 / L_s 등록?')
for s in ['L_1', 'L_s', 'X:=', '$X$(']:
    for m in re.finditer(re.escape(s), jb):
        i = m.start()
        print('  장부:', jb[max(0, i-80):i+60].replace('\n', ' '))
