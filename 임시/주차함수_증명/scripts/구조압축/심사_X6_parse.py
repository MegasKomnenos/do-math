# -*- coding: utf-8 -*-
"""심사 X6 — 진술 머리·증명 범위·인용 그래프 파싱.

출력: scripts/구조압축/심사_X6_graph.json
  statements: [{label, kind, name, status, file, line, body_end, proof_start, proof_end, proof_lines, deferred, cites_body, cites_prose_after}]
  reach_main: 1:main-theorem에서 거꾸로 닿는 라벨 집합(진술 본문·증명·미룬 증명의 인용만 선으로 봄)
  reach_main_loose: 진술 뒤 산문의 인용까지 선으로 넣은 느슨한 도달
"""
import re, json, os
from collections import defaultdict, OrderedDict

ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, "장v2")
FILES = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md",
         "부록A.md","부록B.md","부록C.md"] + sorted(f for f in os.listdir(CH) if f.startswith("부록D_"))

KIND = r'(정의|정리|명제|보조정리|따름정리)'
HEAD_RAW = re.compile(r'^\*\*' + KIND + r' \{\{([^}]+)\}\}(?P<rest>.*?)\.\*\*')
DEFER = re.compile(r'^\*\*' + KIND + r' \{\{([^}]+)\}\}의 증명\.\*\*')
LAB = re.compile(r'\{\{([^}]+)\}\}')
PROOF = re.compile(r'^\*\*증명(?: 개관)?\.\*\*')

def parse_head(l):
    """머리 줄이면 (kind, label, name, status) 아니면 None. 이름 괄호는 균형으로 잰다."""
    m = re.match(r'^\*\*' + KIND + r' \{\{([^}]+)\}\}', l)
    if not m: return None
    kind, label = m.group(1), m.group(2)
    rest = l[m.end():]
    if rest.startswith('의 증명'): return None
    name = ''; status = ''
    if rest.startswith(' ('):
        depth = 0; k = 1
        while k < len(rest):
            if rest[k] == '(': depth += 1
            elif rest[k] == ')':
                depth -= 1
                if depth == 0: break
            k += 1
        name = rest[2:k]; rest = rest[k+1:]
    if rest.startswith(' ['):
        k = rest.find(']')
        status = rest[2:k]; rest = rest[k+1:]
    if not rest.startswith('.**'):
        return None
    return kind, label, name, status

def read(f):
    with open(os.path.join(CH, f), 'rb') as fh:
        return fh.read().decode('utf-8').split('\n')

stmts = []
for f in FILES:
    lines = read(f)
    heads = [(i, h) for i, h in ((i, parse_head(l)) for i, l in enumerate(lines)) if h]
    for idx, (i, h) in enumerate(heads):
        nxt = heads[idx+1][0] if idx+1 < len(heads) else len(lines)
        kind, label, name, status = h
        proof_start = proof_end = None
        for j in range(i, nxt):
            if PROOF.match(lines[j]) or DEFER.match(lines[j]):
                proof_start = j; break
        if proof_start is not None:
            for j in range(proof_start, nxt):
                if '∎' in lines[j]:
                    proof_end = j; break
            if proof_end is None: proof_end = nxt - 1
            body_end = proof_end
        else:
            j = i + 1; in_math = False
            while j < nxt:
                s = lines[j].strip()
                if s == '$$': in_math = not in_math
                if s == '' and not in_math: break
                j += 1
            body_end = j - 1
        body = '\n'.join(lines[i:body_end+1])
        cites = [c for c in LAB.findall(body) if c != label]
        prose = '\n'.join(lines[body_end+1:nxt])
        stmts.append(OrderedDict(label=label, kind=kind, name=name, status=status, file=f, line=i+1,
                                 body_end=body_end+1, proof_start=(proof_start+1 if proof_start is not None else None),
                                 proof_end=(proof_end+1 if proof_end is not None else None),
                                 proof_lines=((proof_end-proof_start+1) if proof_start is not None else 0),
                                 deferred=[], cites_body=sorted(set(cites)), cites_prose_after=sorted(set(LAB.findall(prose)))))

labels = {s['label'] for s in stmts}
by = {s['label']: s for s in stmts}
# 미룬 증명: '**정리 {{L}}의 증명.**' 줄부터 ∎까지를 L의 증명으로 붙인다
for f in FILES:
    lines = read(f)
    for i, l in enumerate(lines):
        dm = DEFER.match(l)
        if not dm: continue
        lab = dm.group(2)
        j = i
        while j < len(lines) - 1 and '∎' not in lines[j] and not (j > i and parse_head(lines[j])): j += 1
        body = '\n'.join(lines[i:j+1])
        if lab in by:
            st = by[lab]
            st['deferred'].append([f, i+1, j+1])
            st['proof_lines'] += (j - i + 1)
            st['cites_body'] = sorted(set(st['cites_body']) | {c for c in LAB.findall(body) if c != lab})
        else:
            print('미룬 증명의 라벨 없음', f, i+1, lab)
# 4:old-4-5의 증명 개관: "이 절의 나머지 전부가 이 정리의 증명" — 4.1절 끝(미룬 증명 줄)까지의 인용을 붙인다
l4 = read('장4.md')
for i, l in enumerate(l4):
    if PROOF.match(l) and '개관' in l:
        j = i
        while j < len(l4) and not DEFER.match(l4[j]): j += 1
        st = by['4:old-4-5']
        st['deferred'].append(['장4.md', i+1, j])
        st['cites_body'] = sorted(set(st['cites_body']) | {c for c in LAB.findall('\n'.join(l4[i:j])) if c != '4:old-4-5'})

# 식 번호(tag X) → 진술 라벨
TAG = re.compile(r'[\\]tag[{]([^}]+)[}]')
tag_owner = {}
NL = chr(10)
def _body_text(st):
    lines = read(st['file'])
    t = NL.join(lines[st['line']-1:st['body_end']])
    for f, a, b in st['deferred']:
        t += NL + NL.join(read(f)[a-1:b])
    return t
bodies = {st['label']: _body_text(st) for st in stmts}
for st in stmts:
    for tg in TAG.findall(bodies[st['label']]):
        tag_owner.setdefault(tg, st['label'])
EQREF = re.compile(r'\((\d+\.\d+[a-z′]?)\)')
for st in stmts:
    refs = set()
    for eq in EQREF.findall(bodies[st['label']]):
        own = tag_owner.get(eq)
        if own and own != st['label']:
            refs.add(own)
    st['cites_eq'] = sorted(refs)
    st['cites_body'] = sorted(set(st['cites_body']) | refs)
dep = {s['label']: [c for c in s['cites_body'] if c in labels] for s in stmts}
def reach(start, dep):
    seen = set(); st = [start]
    while st:
        x = st.pop()
        if x in seen: continue
        seen.add(x); st.extend(dep.get(x, []))
    return seen
R = reach('1:main-theorem', dep)
dep2 = {s['label']: sorted(set([c for c in s['cites_body']+s['cites_prose_after'] if c in labels])) for s in stmts}
R2 = reach('1:main-theorem', dep2)
cited_anywhere = defaultdict(list)
for f in FILES:
    for i, l in enumerate(read(f)):
        h = parse_head(l)
        for c in LAB.findall(l):
            if c in labels and not (h and h[1] == c):
                cited_anywhere[c].append(f"{f}:{i+1}")
# 소비처(진술 본문·증명에서 인용하는 진술)
consumers = defaultdict(list)
for s in stmts:
    for c in dep[s['label']]:
        consumers[c].append(s['label'])

out = dict(statements=stmts, reach_main=sorted(R), reach_main_loose=sorted(R2),
           not_reached=[s['label'] for s in stmts if s['label'] not in R],
           not_reached_loose=[s['label'] for s in stmts if s['label'] not in R2],
           cited_anywhere={k: v for k, v in cited_anywhere.items()},
           consumers={k: v for k, v in consumers.items()},
           never_cited=[s['label'] for s in stmts if s['label'] not in cited_anywhere])
with open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_graph.json'), 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('진술 수', len(stmts), '도달(엄격)', len(R), '도달(느슨)', len(R2))
    print('비도달(엄격):', len(out['not_reached']))
    for l in out['not_reached']:
        s = by[l]; print(' ', s['file'], s['line'], s['kind'], l, s['name'][:30], '| 인용처:', len(cited_anywhere.get(l, [])), '| 소비 진술:', consumers.get(l, []))
    print('비도달(느슨):', len(out['not_reached_loose']))
    for l in out['not_reached_loose']:
        s = by[l]; print(' ', s['file'], s['line'], s['kind'], l, s['name'][:30])
    print('어디서도 인용되지 않음:', out['never_cited'])
