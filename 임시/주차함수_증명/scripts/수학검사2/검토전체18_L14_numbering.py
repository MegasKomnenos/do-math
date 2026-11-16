import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명'
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
heads = []  # (chapter, kind, label, file, line, section)
HEAD = re.compile(r'\*\*(정의|정리|보조정리|명제|따름정리) \{\{([^}]+)\}\}(?!의 증명)')
SEC = re.compile(r'^#{2,4} (\d+(?:\.\d+)*)')
for f in files:
    ch = re.match(r'장(\d+)', f).group(1)
    sec = None
    with open(os.path.join(root, '장v2', f + '.md'), encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            ms = SEC.match(line)
            if ms:
                sec = ms.group(1)
            m = HEAD.match(line)
            if m:
                heads.append((ch, m.group(1), m.group(2), f, i, sec))
num = {}
cnt = {}
for ch, kind, lab, f, i, sec in heads:
    cnt[ch] = cnt.get(ch, 0) + 1
    num[lab] = (f'{ch}.{cnt[ch]}', kind, f, i, sec)
print('heads', len(heads))
rows = []
with open(os.path.join(root, '대조v2', '라벨_번호_대응표_1114.md'), encoding='utf-8') as fh:
    for i, line in enumerate(fh, 1):
        m = re.match(r'\| `\{\{([^}]+)\}\}` \| (\S+) \| (.*?) \| (\S+) \| (.*?) \| (\S+) \|', line)
        if m:
            rows.append((i, m.group(1), m.group(2), m.group(3), m.group(4), m.group(6)))
print('대응표 rows', len(rows))
labs_in_table = set()
for i, lab, kind, name, cur, sec in rows:
    labs_in_table.add(lab)
    if lab not in num:
        print(f'대응표 L{i}: {lab} not in heads; cur={cur}')
        continue
    n, k, f, li, s = num[lab]
    if cur != n:
        print(f'대응표 L{i}: {lab} cur={cur} actual={n} ({f}:{li})')
    if kind != k:
        print(f'대응표 L{i}: {lab} kind={kind} actual={k}')
    # section: compare 2-level prefix
    s2 = '.'.join(s.split('.')[:2]) if s else None
    if sec != s2:
        print(f'대응표 L{i}: {lab} sec={sec} actual={s} ({f}:{li})')
for ch, kind, lab, f, i, s in heads:
    if lab not in labs_in_table:
        print(f'head not in 대응표: {lab} {f}:{i}')
# 4절
rows4 = []
with open(os.path.join(root, '장부_v2.md'), encoding='utf-8') as fh:
    lines = fh.readlines()
for i, line in enumerate(lines, 1):
    if 743 <= i <= 1196:
        m = re.match(r'\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
        if m and m.group(6).startswith(('{{', '(', '—')):
            rows4.append((i,) + m.groups())
print('4절 rows', len(rows4))
labs4 = set()
for i, old, kind, name, rec, sec, lab in rows4:
    m = re.match(r'\{\{([^}]+)\}\}', lab)
    if not m:
        continue
    L = m.group(1)
    labs4.add(L)
    if L not in num:
        print(f'4절 L{i}: {L} not in heads')
        continue
    n, k, f, li, s = num[L]
    if kind != k:
        print(f'4절 L{i}: {L} kind={kind} actual={k}')
    s2 = '.'.join(s.split('.')[:2]) if s else None
    if sec != s2:
        print(f'4절 L{i}: {L} sec={sec} actual={s} ({f}:{li})')
for ch, kind, lab, f, i, s in heads:
    if lab not in labs4:
        print(f'head not in 4절: {lab} {f}:{i}')
# 의존지도 1절: label, section, kind-number, 지위
rowsD = []
with open(os.path.join(root, '의존지도_v2.md'), encoding='utf-8') as fh:
    for i, line in enumerate(fh, 1):
        if i > 409: break
        m = re.match(r'\| `\{\{([^}]+)\}\}` \| (\S+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
        if m:
            rowsD.append((i,) + m.groups())
print('의존지도 rows', len(rowsD))
labsD = set()
for i, lab, sec, old, gist, status, inputs, rec, lit, appD, note in rowsD:
    labsD.add(lab)
    if lab not in num:
        print(f'의존지도 L{i}: {lab} not in heads'); continue
    n, k, f, li, s = num[lab]
    s2 = '.'.join(s.split('.')[:2]) if s else None
    if sec != s2:
        print(f'의존지도 L{i}: {lab} sec={sec} actual={s} ({f}:{li})')
    mo = re.match(r'(정의|정리|보조정리|명제|따름정리) ', old)
    if mo and mo.group(1) != k:
        print(f'의존지도 L{i}: {lab} old-kind={mo.group(1)} actual={k}')
for ch, kind, lab, f, i, s in heads:
    if lab not in labsD:
        print(f'head not in 의존지도: {lab} {f}:{i}')
# dump head list with status for later
with open(os.path.join(root, 'scripts', '수학검사2', '검토전체18_L14_heads2.tsv'), 'w', encoding='utf-8') as out:
    for ch, kind, lab, f, i, s in heads:
        out.write(f'{num[lab][0]}\t{kind}\t{lab}\t{f}\t{i}\t{s}\n')
