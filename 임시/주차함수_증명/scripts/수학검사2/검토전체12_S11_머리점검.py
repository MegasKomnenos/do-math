# S11: 진술 머리(첫 등장)를 다시 모으고, 11.3절 계산 열의 진술·관심 진술의 머리 전문과 9·10장의 고아 진술(아무도 인용하지 않는 진술)을 찍는다.
import re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HDR = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의|관찰)\s+\{\{(\d+[AB]?:[^}]+)\}\}(?!의 증명)(.*?)\*\*')
idx = {}
for ch in ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']:
    sec = None
    for ln, line in enumerate(open(f'장v2/{ch}.md', encoding='utf-8'), 1):
        m = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)', line)
        if m: sec = m.group(2)
        m = HDR.match(line)
        if m and m.group(2) not in idx:
            idx[m.group(2)] = (m.group(1), sec, ch, ln, m.group(3).strip())
json.dump(idx, open('scripts/수학검사2/_S11_idx.json', 'w', encoding='utf-8'), ensure_ascii=False)
want = ['4:old-4-5','4:gauss-contraction','4:gauss-coeff','4:two-corrections','4:gauss-coeff-numeric','5:old-5-18','5:old-5-12','5:old-5-13','5:old-5-32','5:old-5-4','5:old-5-5','5:old-5-7','5:old-5-2','5:band-inequality','5:witness-position-bound','6:theorem-U','6:theorem-D','6:v-negative','6:old-8-13','7:column-lemma','7:seed-transfer','7:pair-check-10000','7:pair-reach-table','7:analytic-transfer','7:integer-strips','7:hermite-nu','7:theorem-C-moment','7:self-consistent-S','7:cor-S-prime','7:polar-W','7:qstar-implies-wlflat','7:qstar-columns','7:old-6-12','7:polar-PD','8:closed-form-envelope','8:table-tolerance','8:old-6-28','8:old-6-33','8:old-6-29','9:H-star-plus','9:head-sum-2','9:head-sum-1','9:old-7-16','9:old-7-35','9:pair-one-variable','9:old-7-26','9:old-7-28','9:old-7-31','9:old-7-33','10:old-8-23','10:check-na','10:check-ga','3:old-3-6','9:old-7-2','8:old-6-30','8:old-6-23','9:old-7-17','9:old-7-44','9:old-7-45','9:old-7-46','10:old-8-37','10:reduction-na','10:reduction-ga','10:old-8-33','10:bulk-majorants','10:old-8-35','10:families','10:row-3k']
for lab in want:
    e = idx.get(lab)
    print('--', lab, '|', e[0] if e else '?', e[1] if e else '', e[2] if e else '', e[3] if e else '')
    print('   ', (e[4] if e else '')[:420])
cites = {k: set(v) for k, v in json.load(open('scripts/수학검사2/_S11_citesA.json', encoding='utf-8')).items()}
cited = set().union(*cites.values())
print('\n=== 9·10장 진술 가운데 라벨로 인용되지 않는 것:', sorted(l for l in idx if l.startswith(('9:', '10:')) and l not in cited))
print('=== 3:old-3-6을 인용:', sorted(k for k, v in cites.items() if '3:old-3-6' in v))
print('=== 10:reduction-na 인용:', sorted(cites.get('10:reduction-na', [])))
print('=== 10:reduction-ga 인용:', sorted(cites.get('10:reduction-ga', [])))
print('=== 10:old-8-33 인용:', sorted(cites.get('10:old-8-33', [])))
print('=== 10:bulk-majorants 인용:', sorted(cites.get('10:bulk-majorants', [])))
print('=== 10:old-8-35 인용:', sorted(cites.get('10:old-8-35', [])))
print('=== 10:old-8-14 인용:', sorted(cites.get('10:old-8-14', [])))
print('=== 6:diag-first-layer 인용:', sorted(cites.get('6:diag-first-layer', [])))
print('=== 6:classes-increase 인용:', sorted(cites.get('6:classes-increase', [])))
print('=== 6:pointwise 인용:', sorted(cites.get('6:pointwise', [])))
print('=== 6:chain-count 인용:', sorted(cites.get('6:chain-count', [])))
print('=== 6:class-polynomial 인용:', sorted(cites.get('6:class-polynomial', [])))
print('=== 9:old-7-39 인용:', sorted(cites.get('9:old-7-39', [])))
