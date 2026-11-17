# R13: 장 파일의 진술 머리를 순서대로 세어 라벨-번호-종류-이름-절을 뽑고 대응표와 견준다.
# 같은 라벨의 머리가 되풀이되면(뒤로 미룬 증명 앞의 재진술) 첫 자리만 번호를 받는다.
import re, sys, io, json, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
files = {1:['장1.md'],2:['장2.md'],3:['장3.md'],4:['장4.md'],5:['장5A.md','장5B.md'],6:['장6.md'],7:['장7A.md','장7B.md'],8:['장8.md'],9:['장9.md'],10:['장10.md']}
head_re = re.compile(r'^\*\*(정의|정리|보조정리|명제|따름정리) \{\{(\d+):([^}]+)\}\}(.*)$')
sec_re = re.compile(r'^##+ (\d+)\.(\d+)')
heads = []
seen = {}
dups = []
for ch, fl in files.items():
    n = 0
    sec = None
    for f in fl:
        with open(os.path.join(ROOT, '장v2', f), encoding='utf-8') as fh:
            for ln, line in enumerate(fh, 1):
                m = sec_re.match(line)
                if m:
                    sec = f'{m.group(1)}.{m.group(2)}'
                m = head_re.match(line)
                if m:
                    lab = f'{m.group(2)}:{m.group(3)}'
                    if lab in seen:
                        dups.append((lab, f, ln, seen[lab]))
                        continue
                    n += 1
                    seen[lab] = f'{ch}.{n} {f}:{ln}'
                    rest = m.group(4)
                    name = None
                    mm = re.match(r'\s*\((.*)\)\s*\[', rest)
                    if not mm:
                        mm = re.match(r'\s*\((.*?)\)\s*\.?\*\*', rest)
                    if mm:
                        name = mm.group(1)
                    heads.append(dict(ch=ch, num=f'{ch}.{n}', label=lab, type=m.group(1), name=name, sec=sec, file=f, line=ln, rest=rest.strip()))
json.dump(heads, open(os.path.join(ROOT, '대조v2', '수학검사2', '_R13_heads.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('heads total (unique)', len(heads))
print('== 되풀이된 머리(라벨, 파일, 행, 첫 자리)')
for d in dups:
    print(' ', d)
rows = []
with open(os.path.join(ROOT, '대조v2', '라벨_번호_대응표_1114.md'), encoding='utf-8') as fh:
    for ln, line in enumerate(fh, 1):
        if not line.startswith('| `'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 6:
            continue
        lab = cells[0].strip('`')
        rows.append(dict(line=ln, label=lab, type=cells[1], name=cells[2], cur=cells[3], old=cells[4], sec=cells[5]))
live = [r for r in rows if r['label'].startswith('{{')]
dead = [r for r in rows if not r['label'].startswith('{{')]
print('table live rows', len(live), 'dead rows', len(dead))
by_label = {h['label']: h for h in heads}
tbl_labels = {r['label'].strip('{}'): r for r in live}
print('\n== 장 파일에 있으나 대응표 live 행에 없는 라벨')
for h in heads:
    if h['label'] not in tbl_labels:
        print(' ', h['num'], h['type'], h['label'], h['name'], h['sec'], h['file'], h['line'])
print('\n== 대응표 live 행에 있으나 장 파일에 없는 라벨')
for l, r in tbl_labels.items():
    if l not in by_label:
        print(' ', r['line'], l, r['cur'])
print('\n== 번호/종류/절 불일치 (대응표 행번호, 라벨, 표 vs 현행)')
for l, r in tbl_labels.items():
    h = by_label.get(l)
    if not h:
        continue
    diffs = []
    if r['cur'] != h['num']:
        diffs.append(f"번호 {r['cur']}→{h['num']}")
    if r['type'] != h['type']:
        diffs.append(f"종류 {r['type']}→{h['type']}")
    if r['sec'] != h['sec']:
        diffs.append(f"절 {r['sec']}→{h['sec']}")
    if diffs:
        print(' ', r['line'], l, '; '.join(diffs))
print('\n== 이름 비교 (표의 이름 첫 조각 vs 머리 괄호)')
for l, r in tbl_labels.items():
    h = by_label.get(l)
    if not h:
        continue
    tn = r['name'].split(';')[0].strip()
    hn = (h['name'] or '').split(';')[0].strip()
    if tn == '—' and not h['name']:
        continue
    if tn != hn:
        print(' ', r['line'], l, '| 표:', r['name'], '| 머리:', h['name'], '| rest:', h['rest'][:80])
print('\n== 뺌 행 라벨이 장 파일에 아직 있는가')
for r in dead:
    l = r['label'].strip('()')
    if l in by_label:
        print(' ', r['line'], l, '→ 현행', by_label[l]['num'])
text = ''
for f in glob.glob(os.path.join(ROOT, '장v2', '*.md')):
    text += open(f, encoding='utf-8').read()
print('\n== 뺌 행 라벨이 장 파일 본문에 {{…}}로 인용되는가')
for r in dead:
    l = r['label'].strip('()')
    if '{{' + l + '}}' in text:
        print(' ', r['line'], l)
# 장별 머리 수
from collections import Counter
print('\n== 장별 머리 수', Counter(h['ch'] for h in heads))
