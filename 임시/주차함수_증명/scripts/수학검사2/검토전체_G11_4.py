# -*- coding: utf-8 -*-
"""G11: 폐포 소속 확인, 빠진 입력의 인용자, D-bound 인용자, 부록 B 제목 대조."""
import re, os, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_src = open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체_G11_1.py", encoding='utf-8').read().split("# 2. 부록 D 항목")[0]
_src = _src.replace("sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')", "")
exec(_src)
cites = {lab: set(x for x in re.findall(r"\{\{([^}]+)\}\}", '\n'.join(s['block'])) if x in stmts and x != lab) for lab, s in stmts.items()}
for lab in cites:
    if lab.startswith('10:'): cites[lab] = {x for x in cites[lab] if not x.startswith('9:')}
    cites[lab] = {x for x in cites[lab] if not x.startswith('1:')}
def closure(start):
    seen = set(); todo = list(start)
    while todo:
        x = todo.pop()
        if x in seen: continue
        seen.add(x); todo.extend(cites.get(x, ()))
    return seen
C1 = closure(['9:old-7-46'])
sec107 = '\n'.join(sections.get(('text', '10.7'), []))
start2 = {x for x in re.findall(r"\{\{([^}]+)\}\}", sec107) if x in stmts and not x.startswith('9:')} | {'10:old-8-37'}
C2 = closure(start2)
print("== 문헌을 쓰는 진술의 폐포 소속 ==")
for x in ['2:old-2-10','2:old-2-11','6:lemma-Hprime','6:lemma-O','7:old-6-6','7:fourier-lemmas','5:cut-rep','5:kernel-sandwich','8:explicit-bounds','5:renewal-fkg','4:borel-tail-arc','3:old-3-1','3:old-3-2','3:old-3-3','3:old-3-4','3:old-3-6','2:old-2-37','2:old-2-38','4:correction-contour','7:lemma-P-prime','6:geometric-mean','9:chain-bounds','10:old-8-30','5:suff-cond','6:lemma-H','7:old-6-7','7:old-6-8','7:flat-threshold','8:jensen-lower','5:old-5-12','2:old-2-3','2:old-2-6']:
    print(f"   {x}: 첫째 {x in C1}, 둘째 {x in C2}")
print("== 6:D-bound 인용자 ==", [(l, stmts[l]['file'], stmts[l]['line']) for l, cs in cites.items() if '6:D-bound' in cs])
print("== 빠진 입력의 9장/10장 인용자 ==")
for t in ['2:old-2-10','2:old-2-11','2:old-2-38','2:old-2-39','2:old-2-6','5:old-5-28','5:zeta-constants','8:old-6-23','8:old-6-30','2:old-2-45','5:witness-position-bound','6:old-7-20']:
    users = [(l, stmts[l]['line']) for l, cs in cites.items() if t in cs and l.startswith(('9:','10:'))]
    print(f"   {t}: {users}")
# 인용 문맥
def ctx(fn, label, target):
    s = stmts[label]
    for ln in s['block']:
        for m in re.finditer(r"\{\{" + re.escape(target) + r"\}\}", ln):
            a = max(0, m.start()-90); print(f"      [{label} {s['file']}] …{ln[a:m.end()+60]}…")
for t in ['2:old-2-10','2:old-2-11','2:old-2-38','2:old-2-39','2:old-2-6','5:old-5-28','8:old-6-23','8:old-6-30','2:old-2-45','6:old-7-20']:
    print("   --", t)
    for l, cs in cites.items():
        if t in cs and l.startswith(('9:','10:')):
            ctx(None, l, t)
# 부록 B 제목 대조
print("== 부록 B 내용 vs record.json title ==")
recdir = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
B = read(os.path.join(CH, "부록B.md"))
for ln in B:
    m = re.match(r"^\| (r[0-9a-f]{7}) \| ([^|]+) \| ([^|]+) \| `([^`]+)` \|", ln)
    if not m: continue
    rid, t, desc, folder = m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4)
    p = os.path.join(recdir, folder, 'record.json')
    if not os.path.exists(p):
        print("   record.json 없음", rid); continue
    try:
        j = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print("   json 오류", rid, e); continue
    title = j.get('title') or j.get('name') or ''
    created = str(j.get('created_at') or j.get('created') or j.get('timestamp') or '')
    norm = lambda s: re.sub(r"[\s`*_]", "", s)
    if norm(title) != norm(desc):
        print(f"   [{rid}] 제목 다름\n      B: {desc}\n      J: {title}")
    if created and t.replace(' ', 'T')[:5] not in created.replace('2026-', ''):
        print(f"   [{rid}] 시각 B={t} J={created}")
