# -*- coding: utf-8 -*-
"""K14: 장 파일에서 진술별 입력(머리 라벨·본문 인용 라벨)·문헌·부록 D 열을 다시 만들어 의존지도 1절과 대조."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+):([^}]+)\}\}((?!의 증명).*?)\*\*')
PROOF = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+):([^}]+)\}\}의 증명')
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
segs = {}   # label -> list of text (head line, body lines, deferred proof lines)
heads = {}
order = []
for c in CH:
    cur = None
    lines = open(os.path.join(ROOT, '장v2', c + '.md'), encoding='utf-8').read().split('\n')
    for line in lines:
        m = HEAD.match(line)
        mp = PROOF.match(line)
        if m:
            lab = '{{%s:%s}}' % (m.group(2), m.group(3))
            cur = lab
            heads[lab] = line
            segs.setdefault(lab, []).append(('H', line))
            order.append(lab)
        elif mp:
            lab = '{{%s:%s}}' % (mp.group(2), mp.group(3))
            cur = lab
            segs.setdefault(lab, []).append(('P', line))
        elif cur:
            segs[cur].append(('B', line))
def labs(text):
    return ['{{%s}}' % x for x in LAB.findall(text)]
regen = {}
for lab in order:
    hl = heads[lab]
    hlabs = []
    for x in labs(hl):
        if x != lab and x not in hlabs:
            hlabs.append(x)
    blabs = []
    for kind, line in segs[lab]:
        if kind == 'H':
            continue
        for x in labs(line):
            if x != lab and x not in hlabs and x not in blabs:
                blabs.append(x)
    regen[lab] = (hlabs, blabs)
# 의존지도 1절
dep = {}
in1 = False
for line in open(os.path.join(ROOT, '의존지도_v2.md'), encoding='utf-8'):
    if line.startswith('## 1.'):
        in1 = True
    elif line.startswith('### 1.1') or line.startswith('## 2'):
        in1 = False
    if in1:
        m = re.match(r'^\| `(\{\{[^`]+\}\})` \| ([^|]*) \| ([^|]*) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
        if m:
            lab = m.group(1)
            inputs = m.group(6).strip()
            dep[lab] = dict(inputs=inputs, rec=m.group(7).strip(), lit=m.group(8).strip(), dcalc=m.group(9).strip())
out = []
for lab in order:
    if lab not in dep:
        out.append(('의존지도에 없음', lab)); continue
    s = dep[lab]['inputs']
    if s == '—':
        dh, db = [], []
    else:
        parts = s.split('본문 인용:')
        dh = [x.strip('` ;') for x in parts[0].split(',') if x.strip('` ;')]
        db = [x.strip('` ') for x in parts[1].split(',') if x.strip('` ')] if len(parts) > 1 else []
    rh, rb = regen[lab]
    if sorted(dh) != sorted(rh):
        out.append(('머리 입력', lab, '지도=' + ','.join(dh), '현행=' + ','.join(rh)))
    if sorted(db) != sorted(rb):
        out.append(('본문 인용', lab, '지도만=' + ','.join(sorted(set(db) - set(rb))), '현행만=' + ','.join(sorted(set(rb) - set(db)))))
# 기록 주장 열: 머리 대괄호 ; 뒤 식별자
for lab in order:
    if lab not in dep: continue
    hl = heads[lab]
    ms = re.search(r'\[([^\[\]]*(?:\{\{[^}]*\}\}[^\[\]]*)*)\]\.\*\*', hl)
    ids_head = sorted(set(re.findall(r'\br[0-9a-f]{7}\b', hl.split('[증명됨')[-1] if '[증명됨' in hl else hl)))
    ids_dep = sorted(set(re.findall(r'\br[0-9a-f]{7}\b', dep[lab]['rec'])))
    # 머리 전체의 식별자 가운데 지위 대괄호의 것만 뽑기 어려우므로 전체 집합 비교(이름 괄호의 기록 [r…]도 포함) — 차이만 보고
    ids_all = sorted(set(re.findall(r'\br[0-9a-f]{7}\b', hl)))
    if ids_dep and not set(ids_dep) <= set(ids_all):
        out.append(('기록 주장(머리에 없는 식별자)', lab, ','.join(ids_dep), ','.join(ids_all)))
    # 지위 대괄호 안의 식별자가 지도 열에 빠짐
    mstat = re.search(r'\[((?:[^\[\]]|\[[^\]]*\])*)\]\.\*\*\s*$', hl.rstrip())
    if mstat:
        st = mstat.group(1)
        if ';' in st:
            ids_st = sorted(set(re.findall(r'\br[0-9a-f]{7}\b', st.split(';', 1)[1])))
            if set(ids_st) - set(ids_dep):
                out.append(('기록 주장(지도에 빠진 식별자)', lab, ','.join(ids_st), ','.join(ids_dep)))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_deps_out.txt'), 'w', encoding='utf-8') as f:
    for o in out:
        f.write('\t'.join(o) + '\n')
print('rows', len(order), 'diffs', len(out))
