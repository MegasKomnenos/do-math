# R13: 장부 4절(이름 사전)을 장 파일 머리와 견준다 — 종류·이름·기록 이름·절·라벨 생사.
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = json.load(open(os.path.join(ROOT, '대조v2', '수학검사2', '_R13_heads.json'), encoding='utf-8'))
by_label = {h['label']: h for h in heads}
rows = []
in4 = False
for ln, line in enumerate(open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8'), 1):
    if line.startswith('## 4.'):
        in4 = True
        continue
    if line.startswith('## 5.'):
        break
    if in4 and line.startswith('| ') and not line.startswith('| 첫 판') and not line.startswith('|---'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) != 6:
            print('열 수 이상', ln, len(cells), line[:80])
            continue
        rows.append(dict(line=ln, old=cells[0], type=cells[1], name=cells[2], rec=cells[3], sec=cells[4], label=cells[5]))
print('4절 행 수', len(rows))
live_rows = [r for r in rows if r['label'].startswith('{{')]
dead_rows = [r for r in rows if not r['label'].startswith('{{')]
print('살아 있는 라벨 행', len(live_rows), '뺌 행', len(dead_rows))
seen = set()
print('\n== 4절 live 행 vs 머리')
for r in live_rows:
    lab = r['label'].strip('{}')
    if lab in seen:
        print('  중복 행', r['line'], lab)
    seen.add(lab)
    h = by_label.get(lab)
    if not h:
        print('  머리에 없는 라벨', r['line'], lab)
        continue
    diffs = []
    if r['type'] != h['type']:
        diffs.append(f"종류 {r['type']}→{h['type']}")
    if r['sec'] != h['sec']:
        diffs.append(f"절 {r['sec']}→{h['sec']}")
    hn = h['name'] or ''
    parts = [p.strip() for p in hn.split(';')]
    hname = parts[0]
    hrec = '; '.join(parts[1:]) if len(parts) > 1 else ''
    if r['name'] != hname:
        diffs.append(f"이름 「{r['name']}」→머리 「{hname}」")
    if r['rec'] != hrec:
        diffs.append(f"기록 이름 「{r['rec']}」→머리 「{hrec}」")
    if diffs:
        print(' ', r['line'], lab, '; '.join(diffs))
print('\n== 머리에 있으나 4절 live 행에 없는 라벨')
for h in heads:
    if h['label'] not in seen:
        print(' ', h['num'], h['label'])
print('\n== 뺌 행인데 살아 있는 라벨')
for r in dead_rows:
    lab = r['label'].strip('()')
    if lab in by_label:
        print(' ', r['line'], lab, by_label[lab]['num'])
# 첫 판 번호와 의존지도 1절 「첫 판 번호」 열 비교
dep = json.load(open(os.path.join(ROOT, '대조v2', '수학검사2', '_R13_depmap_rows.json'), encoding='utf-8'))
dep_by = {d['label']: d for d in dep}
print('\n== 첫 판 번호: 4절 vs 의존지도 1절')
for r in live_rows:
    lab = r['label'].strip('{}')
    d = dep_by.get(lab)
    if not d:
        continue
    o = r['old']
    exp = '새 진술' if o == '—' else f"{r['type']} {o}"
    if d['old'] != exp:
        print(' ', r['line'], lab, '4절:', o, '| 의존지도:', d['old'])
# 대응표와 종류·이름 비교
tbl = {}
for ln, line in enumerate(open(os.path.join(ROOT, '대조v2', '라벨_번호_대응표_1114.md'), encoding='utf-8'), 1):
    if line.startswith('| `{{'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        tbl[cells[0].strip('`{}')] = dict(line=ln, type=cells[1], name=cells[2])
print('\n== 대응표 이름 vs 4절(이름; 기록 이름)')
for r in live_rows:
    lab = r['label'].strip('{}')
    t = tbl.get(lab)
    if not t:
        continue
    full = r['name'] + ('; ' + r['rec'] if r['rec'] else '')
    tn = t['name'] if t['name'] != '—' else ''
    if full != tn:
        print(' ', lab, '\n    4절:', full, '\n    대응표:', tn)
