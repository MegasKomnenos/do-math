# 10.2절 표의 「재계산」 열과 부록 D 항목의 「독립 재계산」 줄 첫머리 꺾쇠 괄호를 맞댄다.
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
items = {}
order = []
for f in sorted(glob.glob(base + '부록D_장*.md')):
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^### D\.', txt)
    for p in parts[1:]:
        m = re.match(r'\{\{D:([^}]+)\}\}', p)
        lab = m.group(1)
        order.append(lab)
        head = p.split('\n', 1)[0]
        lines = p.split('\n')
        d = {'head': head, 'file': f.split('/')[-1]}
        for ln in lines:
            mm = re.match(r'\s*[-*]*\s*\*\*([^*]+?)\*\*[.:]?\s*(.*)', ln)
            if mm:
                d[mm.group(1).strip(' .:')] = mm.group(2)
        items[lab] = d
t10 = open(base + '장10.md', encoding='utf-8').read().split('\n')
rows = {}
for ln in t10:
    m = re.match(r'\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', ln)
    if m:
        rows[m.group(1)] = m.groups()[1:]
print('D items', len(order), 'rows', len(rows))
for lab in order:
    d = items[lab]
    print('=====', lab, d['file'])
    print(' keys:', [k for k in d if k not in ('head', 'file')])
    r = rows.get(lab)
    print(' 10.2 진술:', r[0]); print(' D 머리  :', d['head'][-200:])
    print(' 10.2 등급:', r[1]); 
    for k in d:
        if '산술' in k: print(' D', k, ':', d[k][:1500])
    print(' 10.2 놓인곳:', r[2])
    rec = [d[k] for k in d if '재계산' in k]
    if rec:
        mb = re.match(r'(〔.*?〕)', rec[0])
        b = mb.group(1) if mb else None
        print(' bracket equal:', b == r[3])
        if b != r[3]:
            print('  D   :', b); print('  10.2:', r[3])
    else:
        print(' NO 재계산 key')
