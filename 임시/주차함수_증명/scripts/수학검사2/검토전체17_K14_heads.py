# -*- coding: utf-8 -*-
"""K14: 장 파일의 진술 머리 추출과 대응표·의존지도 1절 대조. 출력은 파일로."""
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+):([^}]+)\}\}((?!의 증명).*?)\*\*')
heads = []
for c in CH:
    p = os.path.join(ROOT, '장v2', c + '.md')
    sec = ''
    with open(p, encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            m = re.match(r'^###\s+(\S+)', line)
            if m:
                sec = m.group(1)
            m2 = re.match(r'^####\s+(\S+)', line)
            if m2:
                pass
            m = HEAD.match(line)
            if m:
                kind, chno, lab, rest = m.groups()
                rest = rest.strip().rstrip('.')
                name = ''; status = ''
                if rest.endswith(']'):
                    i = rest.rfind(' [')
                    if i < 0: i = rest.rfind('[')
                    status = rest[i+1:].strip()[1:-1]
                    rest = rest[:i].strip()
                if rest.startswith('(') and rest.endswith(')'):
                    name = rest[1:-1]
                elif rest:
                    name = 'RAW:' + rest
                heads.append(dict(file=c, line=ln, kind=kind, ch=int(chno), label='{{%s:%s}}' % (chno, lab), name=name, status=status, sec=sec))
# 번호 매기기: 장별 순서
cnt = {}
for h in heads:
    cnt[h['ch']] = cnt.get(h['ch'], 0) + 1
    h['num'] = '%d.%d' % (h['ch'], cnt[h['ch']])
out = os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_heads.tsv')
with open(out, 'w', encoding='utf-8') as f:
    for h in heads:
        f.write('\t'.join(str(h[k]) for k in ['file','line','num','kind','label','name','status','sec']) + '\n')
print('heads', len(heads))

# 대응표
tab = {}
with open(os.path.join(ROOT, '대조v2', '라벨_번호_대응표_1114.md'), encoding='utf-8') as f:
    for line in f:
        m = re.match(r'^\| `(\{\{[^`]+\}\})` \| ([^|]*) \| (.*?) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|\s*$', line)
        if m:
            lab, kind, name, cur, old, sec = [x.strip() for x in m.groups()]
            tab[lab] = dict(kind=kind, name=name, cur=cur, old=old, sec=sec)
print('table rows', len(tab))
hl = {h['label']: h for h in heads}
probs = []
for lab, h in hl.items():
    if lab not in tab:
        probs.append(('표에 없음', lab, h['num'], h['kind'], h['name']))
        continue
    t = tab[lab]
    if t['cur'] != h['num'] and t['cur'] != '뺌':
        probs.append(('번호', lab, '표 ' + t['cur'], '현행 ' + h['num']))
    if t['kind'] != h['kind']:
        probs.append(('종류', lab, t['kind'], h['kind']))
    nm = h['name'] if h['name'] else '—'
    if t['name'] != nm:
        probs.append(('이름', lab, t['name'], nm))
    if t['sec'] != h['sec']:
        probs.append(('절', lab, t['sec'], h['sec']))
for lab, t in tab.items():
    if lab not in hl:
        probs.append(('장에 없음', lab, t['cur'], t['kind'], t['name']))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_table_out.txt'), 'w', encoding='utf-8') as f:
    for p in probs:
        f.write('\t'.join(p) + '\n')
print('table probs', len(probs))

# 의존지도 1절
dep = {}
with open(os.path.join(ROOT, '의존지도_v2.md'), encoding='utf-8') as f:
    in1 = False
    for line in f:
        if line.startswith('## 1.'):
            in1 = True
        elif line.startswith('## 2'):
            in1 = False
        if in1:
            m = re.match(r'^\| `(\{\{[^`]+\}\})` \| ([^|]*) \| ([^|]*) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
            if m:
                lab, sec, old, gist, status, inputs, rec, lit, dcalc, note = [x.strip() for x in m.groups()]
                dep[lab] = dict(sec=sec, old=old, gist=gist, status=status, inputs=inputs, rec=rec, lit=lit, dcalc=dcalc, note=note)
print('dep rows', len(dep))
dprobs = []
for lab, h in hl.items():
    if lab not in dep:
        dprobs.append(('의존지도에 없음', lab, h['num'], h['kind'], h['name']))
        continue
    d = dep[lab]
    if d['sec'] != h['sec']:
        dprobs.append(('절', lab, d['sec'], h['sec']))
    # 지위: 머리 대괄호의 ; 앞
    st = h['status'].split(';')[0].strip() if h['status'] else '정의'
    if h['kind'] == '정의' and not h['status']:
        st = '정의'
    if d['status'] != st:
        dprobs.append(('지위', lab, d['status'], st))
    if h['name'] and d['gist'] != h['name']:
        dprobs.append(('요지', lab, d['gist'], h['name']))
for lab in dep:
    if lab not in hl:
        dprobs.append(('장에 없음', lab, dep[lab]['sec'], dep[lab]['gist']))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_dep_out.txt'), 'w', encoding='utf-8') as f:
    for p in dprobs:
        f.write('\t'.join(p) + '\n')
print('dep probs', len(dprobs))
