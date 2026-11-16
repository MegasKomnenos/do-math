# S11: 11.3절 각 행의 입력 폐포 안에 든 계산 진술(머리에 「계산」이 있는 진술)을 모아 「계산 진술과 산술 등급」 열과 견주고,
# 확인이 필요한 진술들의 머리와 인용 목록을 찍는다.
import re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
cites = {k: set(v) for k, v in json.load(open('scripts/수학검사2/_S11_citesA.json', encoding='utf-8')).items()}
idx = {}
for line in open('scripts/수학검사2/_S11_labels.tsv', encoding='utf-8'):
    p = line.rstrip('\n').split('\t'); idx[p[0]] = p
def closure(roots):
    seen = set(); stack = list(roots)
    while stack:
        x = stack.pop()
        if x in seen or x.startswith('D:'): continue
        seen.add(x); stack.extend(cites.get(x, ()))
    return seen
def grade(lab):
    h = idx.get(lab, [None]*6)[5] or ''
    m = re.search(r'\[(.*?)\]', h)
    return m.group(1) if m else h[:120]
LAB = re.compile(r'\{\{(\d+[AB]?:[^}]+)\}\}')
tab = open('장v2/장11.md', encoding='utf-8').read()
s = tab.index('**공유 입력.**'); e3 = tab.index('### 11.4')
rows = []
for line in tab[s:e3].split('\n'):
    if line.startswith('| ') and not line.startswith('| 입력') and not line.startswith('|---'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        rows.append(cells)
already = set()
for cells in rows:
    inputs = LAB.findall(cells[0]); listed = set(LAB.findall(cells[1]))
    cl = closure(inputs)
    comp = {x for x in cl if '계산' in grade(x)}
    new = comp - already
    print('\n### 행:', cells[0][:70])
    print('  폐포 안 계산 진술(앞 행에 없던 것):', sorted(new))
    print('  표 열에 적힌 것:', sorted(listed))
    print('  열에 있으나 폐포 계산 진술 아님:', sorted(listed - comp), '| 폐포에 있으나 열에 없음:', sorted(new - listed))
    for x in sorted(new | listed):
        print('    ', x, '::', grade(x)[:160])
    already |= comp | listed
print('\n\n===== 확인용 머리·인용 목록')
for lab in ['5:old-5-18','5:old-5-11','5:old-5-1','6:cor-L','6:old-6-19','6:V-all','6:D-bound','6:old-8-11','6:critical-front','6:far-window','6:prop-R','6:small-k-bulk','6:above-window','6:old-7-24','6:lemma-Hprime','8:old-6-33','8:old-6-29','8:old-6-28','8:hazard-H1','8:closed-form-envelope','8:table-tolerance','7:old-6-9','7:flat-threshold','7:old-6-14','7:old-6-15','7:old-6-21','7:column-lemma','2:old-2-46','2:old-2-38','2:old-2-39','6:old-8-13','9:H-star-plus','9:head-sum-2','9:old-7-17','9:old-7-44','9:old-7-35','9:old-7-23','10:old-8-36','10:old-8-10','7:theorem-W','7:src-plus','7:old-6-20','6:tilt-sum']:
    e = idx.get(lab)
    print('\n--', lab, '|', e[1] if e else '?', e[2] if e else '', e[3] if e else '', '\n   머리:', (e[5] if e else '')[:300], '\n   인용:', sorted(cites.get(lab, [])))
print('\n===== 누가 인용하는가')
for target in ['6:insertion','6:log-derivative','6:trapezoid','6:cor-L','6:D-bound','6:increment-bounds','6:old-8-11','6:old-8-12','6:old-8-13','6:DD-lower-bound','2:old-2-46','2:old-2-44','9:old-7-2','9:old-7-17','9:theorem-A-plus','9:prop-6','9:chain-moments','9:psi-two-sided','9:chain-rep','9:chain-bounds','9:centroid-stop','9:old-7-3','9:old-7-7','9:head-sum-1','9:regeneration-S','10:old-8-23','2:zeta-constants','8:old-6-29','2:old-2-40','7:old-6-14','5:witness-position-bound']:
    print(target, '<-', sorted(k for k, v in cites.items() if target in v))
