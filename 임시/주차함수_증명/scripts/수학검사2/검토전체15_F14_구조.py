# -*- coding: utf-8 -*-
"""F14: 장 파일 진술 머리 ↔ 장부 4절 ↔ 대응표 ↔ 의존지도 1절 대조.
자리 찾기와 셈만 한다. 판정은 보고에서 손으로 한다."""
import re, sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH_FILES = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
APP_FILES = ['부록A','부록B','부록C'] + [f'부록D_장{c}' for c in ['2','3','4','5A','5B','6','7A','7B','8','9','10']]
KINDS = '정의|정리|보조정리|명제|따름정리'

def rd(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

heads = {}   # label -> dict
order = []
refs = {}    # label -> set of files referencing
sec_re = re.compile(r'^(#{2,4}) (\d+(?:\.\d+)*)[ .]')
head_re = re.compile(r'^\*\*(' + KINDS + r') \{\{(\d+):([A-Za-z0-9-]+)\}\}(?!의 증명)(.*?)\.\*\*')
counters = {}
for fn in CH_FILES:
    txt = rd(os.path.join(ROOT, '장v2', fn + '.md'))
    cur_sec = None
    for ln, line in enumerate(txt.split('\n'), 1):
        m = sec_re.match(line)
        if m:
            cur_sec = m.group(2)
        m = head_re.match(line)
        if m:
            kind, ch, name, rest = m.group(1), m.group(2), m.group(3), m.group(4)
            label = f'{ch}:{name}'
            # name in parens, status in brackets
            title = None; status = None
            rest = rest.strip()
            if rest.startswith('('):
                depth = 0
                for i, c in enumerate(rest):
                    if c == '(':
                        depth += 1
                    elif c == ')':
                        depth -= 1
                        if depth == 0:
                            title = rest[1:i]; rest = rest[i+1:].strip(); break
            if rest.startswith('['):
                status = rest[1:rest.rfind(']')]
            counters[ch] = counters.get(ch, 0) + 1
            num = f'{ch}.{counters[ch]}'
            if label in heads:
                print('!! 중복 머리', label, fn, ln)
            heads[label] = dict(kind=kind, sec2='.'.join(cur_sec.split('.')[:2]) if cur_sec else None, title=title, status=status, sec=cur_sec, file=fn, line=ln, num=num, chapter=ch)
            order.append(label)
# collect references
all_files = CH_FILES + APP_FILES
ref_re = re.compile(r'\{\{(\d+):([A-Za-z0-9-]+)\}\}')
dref_re = re.compile(r'\{\{D:([A-Za-z0-9-]+)\}\}')
ditems = {}
drefs = {}
for fn in all_files:
    txt = rd(os.path.join(ROOT, '장v2', fn + '.md'))
    for m in ref_re.finditer(txt):
        refs.setdefault(f'{m.group(1)}:{m.group(2)}', set()).add(fn)
    for ln, line in enumerate(txt.split('\n'), 1):
        mm = re.match(r'^### D\.\{\{D:([A-Za-z0-9-]+)\}\}', line)
        if mm:
            if mm.group(1) in ditems:
                print('!! 중복 D 항목', mm.group(1), fn, ln)
            ditems[mm.group(1)] = (fn, ln, line)
    for m in dref_re.finditer(txt):
        drefs.setdefault(m.group(1), set()).add(fn)

print('머리 수', len(heads), '장별', counters)
print('\n== 참조되었으나 머리 없는 라벨 ==')
for lab, fs in sorted(refs.items()):
    if lab not in heads:
        print(lab, sorted(fs))
print('\n== 머리 있으나 어디서도 (자기 파일 밖에서) 참조되지 않는 라벨 ==')
for lab in order:
    fs = refs.get(lab, set()) - {heads[lab]['file']}
    if not fs:
        print(lab, heads[lab]['kind'], heads[lab]['title'], heads[lab]['file'], heads[lab]['line'])
print('\n== D 참조되었으나 항목 없는 것 ==')
for d, fs in sorted(drefs.items()):
    if d not in ditems:
        print(d, sorted(fs))
print('D 항목 수', len(ditems))

# ---- 대응표
tbl = rd(os.path.join(ROOT, '대조v2', '라벨_번호_대응표_1114.md'))
corr = {}
removed_corr = {}
for line in tbl.split('\n'):
    m = re.match(r'^\| `\{\{(\d+):([A-Za-z0-9-]+)\}\}` \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if m:
        corr[f'{m.group(1)}:{m.group(2)}'] = dict(kind=m.group(3), title=m.group(4), num=m.group(5), old=m.group(6), sec=m.group(7))
        continue
    m = re.match(r'^\| `\((\d+):([A-Za-z0-9-]+)\)` \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if m:
        removed_corr[f'{m.group(1)}:{m.group(2)}'] = dict(kind=m.group(3), title=m.group(4), num=m.group(5))
print('\n== 대응표 ==', len(corr), '행; 뺌', len(removed_corr))
for lab in order:
    h = heads[lab]
    if lab not in corr:
        print('대응표에 없음:', lab, h['num']); continue
    c = corr[lab]
    htitle = (h['title'] or '—')
    if c['num'] != h['num']:
        print('번호 다름', lab, '대응표', c['num'], '현행', h['num'])
    if c['sec'] != h['sec2']:
        print('절 다름', lab, '대응표', c['sec'], '현행', h['sec'])
    if c['kind'] != h['kind']:
        print('종류 다름', lab, c['kind'], h['kind'])
    if c['title'] != htitle:
        print('이름 다름', lab, '\n   대응표:', c['title'], '\n   현행  :', htitle)
for lab in corr:
    if lab not in heads:
        print('대응표에 있으나 머리 없음:', lab, corr[lab])
for lab in removed_corr:
    if lab in heads:
        print('대응표 뺌 행이나 머리 있음:', lab)
    if lab in refs:
        print('대응표 뺌 라벨이 참조됨:', lab, sorted(refs[lab]))

# ---- 장부 4절
jb = rd(os.path.join(ROOT, '장부_v2.md'))
s4 = jb[jb.index('## 4. 이름 사전'):jb.index('## 5. 장별 배정')]
sec4 = {}
removed4 = {}
for line in s4.split('\n'):
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if not m or m.group(1) in ('첫 판 번호', '---'):
        continue
    old, kind, title, rec, sec, lab = m.groups()
    mm = re.match(r'\{\{(\d+):([A-Za-z0-9-]+)\}\}', lab)
    if mm:
        sec4[f'{mm.group(1)}:{mm.group(2)}'] = dict(old=old, kind=kind, title=title, rec=rec, sec=sec)
    else:
        mm = re.match(r'\((\d+):([A-Za-z0-9-]+)\)', lab)
        removed4[f'{mm.group(1)}:{mm.group(2)}' if mm else lab] = dict(old=old, kind=kind, title=title, sec=sec)
print('\n== 장부 4절 ==', len(sec4), '행; 뺌', len(removed4))
for lab in order:
    h = heads[lab]
    if lab not in sec4:
        print('4절에 없음:', lab); continue
    r = sec4[lab]
    full = (h['title'] or '')
    if '; 기록' in full:
        t1, rec1 = full.split('; 기록', 1); rec1 = '기록' + rec1
    else:
        t1, rec1 = full, ''
    if r['kind'] != h['kind']:
        print('4절 종류 다름', lab, r['kind'], h['kind'])
    if r['sec'] != h['sec2']:
        print('4절 절 다름', lab, '4절', r['sec'], '현행', h['sec'])
    if r['title'].strip() != t1.strip():
        print('4절 이름 다름', lab, '\n   4절:', r['title'], '\n   현행:', t1)
    if r['rec'].strip() != rec1.strip():
        print('4절 기록 이름 다름', lab, '\n   4절:', r['rec'], '\n   현행:', rec1)
for lab in sec4:
    if lab not in heads:
        print('4절에 있으나 머리 없음:', lab, sec4[lab])
for lab in removed4:
    if lab in heads:
        print('4절 뺌 행이나 머리 있음:', lab)
    if lab in refs:
        print('4절 뺌 라벨이 참조됨:', lab, sorted(refs[lab]))
# 4절 vs 대응표 뺌 목록
print('4절 뺌에만:', sorted(set(removed4) - set(removed_corr)))
print('대응표 뺌에만:', sorted(set(removed_corr) - set(removed4)))

# ---- 의존지도 1절
dm = rd(os.path.join(ROOT, '의존지도_v2.md'))
s1 = dm[dm.index('## 1. 진술별 입력 표'):dm.index('### 1.1 뺌·대체된 라벨')]
dep = {}
for line in s1.split('\n'):
    m = re.match(r'^\| `\{\{(\d+):([A-Za-z0-9-]+)\}\}` \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if m:
        dep[f'{m.group(1)}:{m.group(2)}'] = dict(sec=m.group(3), old=m.group(4), gist=m.group(5), status=m.group(6), inputs=m.group(7), rec=m.group(8), lit=m.group(9), D=m.group(10), note=m.group(11))
print('\n== 의존지도 1절 ==', len(dep))
def norm_status(s, kind=None):
    if s is None or kind == '정의':
        return '정의'
    return s.split(';')[0].strip()
def norm_lab(s):
    return re.sub(r'`', '', s)
for lab in order:
    h = heads[lab]
    if lab not in dep:
        print('의존지도에 없음:', lab); continue
    d = dep[lab]
    if d['sec'] != h['sec2']:
        print('의존지도 절 다름', lab, d['sec'], h['sec'])
    hs = norm_status(h['status'], h['kind'])
    ds = norm_lab(d['status'])
    if hs != ds:
        print('의존지도 지위 다름', lab, '\n   지도:', ds, '\n   머리:', hs)
    # 요지 vs title
    full = h['title'] or ''
    if full and d['gist'] != full and not d['gist'].startswith(full):
        print('의존지도 요지 다름', lab, '\n   지도:', d['gist'], '\n   머리:', full)
    # 머리 줄 인용 라벨 vs 지도 입력(본문 인용 앞부분)
    head_labs = set(f'{a}:{b}' for a, b in ref_re.findall(h['status'] or ''))
    first_part = d['inputs'].split('본문 인용:')[0]
    dep_labs = set(f'{a}:{b}' for a, b in ref_re.findall(first_part))
    if head_labs != dep_labs:
        print('의존지도 머리 인용 다름', lab, '\n   머리:', sorted(head_labs), '\n   지도:', sorted(dep_labs))
    # 기록 식별자
    hrec = set(re.findall(r'r[0-9a-f]{7}', h['status'] or ''))
    drec = set(re.findall(r'r[0-9a-f]{7}', d['rec']))
    if hrec != drec:
        print('의존지도 기록 식별자 다름', lab, '머리', sorted(hrec), '지도', sorted(drec))
for lab in dep:
    if lab not in heads:
        print('의존지도에 있으나 머리 없음:', lab)
