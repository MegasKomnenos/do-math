# R13: 의존지도 v2 1절(진술별 입력 표)을 장 파일 현행과 견준다 — 절, 지위, 머리 줄 인용 라벨, 요지(머리 괄호).
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = json.load(open(os.path.join(ROOT, '대조v2', '수학검사2', '_R13_heads.json'), encoding='utf-8'))
by_label = {h['label']: h for h in heads}
# 머리 줄 전체 텍스트가 필요 — 다시 읽어 머리 줄과 대괄호 지위를 뽑는다
files = {1:['장1.md'],2:['장2.md'],3:['장3.md'],4:['장4.md'],5:['장5A.md','장5B.md'],6:['장6.md'],7:['장7A.md','장7B.md'],8:['장8.md'],9:['장9.md']}
head_re = re.compile(r'^\*\*(정의|정리|보조정리|명제|따름정리) \{\{(\d+):([^}]+)\}\}(.*)$')
lab_re = re.compile(r'\{\{(\d+:[^}]+)\}\}')
headline = {}
for ch, fl in files.items():
    for f in fl:
        for line in open(os.path.join(ROOT, '장v2', f), encoding='utf-8'):
            m = head_re.match(line)
            if m:
                lab = f'{m.group(2)}:{m.group(3)}'
                if lab in headline:
                    continue
                headline[lab] = line.rstrip('\n')
def status_of(line):
    # 머리의 대괄호: 첫 '**...**' 안에서 '[' ... ']' 마지막 것
    m = re.match(r'\*\*.*?\]\.?\*\*', line)
    seg = m.group(0) if m else line
    # 대괄호 안
    mm = re.search(r'\[((?:[^\[\]]|\[[^\[\]]*\])*)\]\.?\*\*$', seg)
    if not mm:
        return None, seg
    inside = mm.group(1)
    # ';' 앞 전문
    st = inside.split(';')[0].strip()
    return st, seg
rows = []
with open(os.path.join(ROOT, '의존지도_v2.md'), encoding='utf-8') as fh:
    in1 = False
    for ln, line in enumerate(fh, 1):
        if line.startswith('## 1.'):
            in1 = True
            continue
        if line.startswith('## 2.') or line.startswith('### 1.1'):
            break
        if in1 and line.startswith('| `{{'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 10:
                print('열 부족', ln, len(cells))
                continue
            rows.append(dict(line=ln, label=cells[0].strip('`{}'), sec=cells[1], old=cells[2], gist=cells[3], status=cells[4], inputs=cells[5], rec=cells[6], lit=cells[7], D=cells[8], note=cells[9]))
print('의존지도 1절 행 수', len(rows), '; 장 파일 머리 수', len(heads))
tbl = {r['label']: r for r in rows}
print('\n== 머리에 있으나 표에 없는 라벨')
for h in heads:
    if h['label'] not in tbl:
        print(' ', h['num'], h['label'])
print('\n== 표에 있으나 머리에 없는 라벨')
for l in tbl:
    if l not in by_label:
        print(' ', tbl[l]['line'], l)
print('\n== 절 불일치')
for l, r in tbl.items():
    h = by_label.get(l)
    if h and h['sec'] != r['sec']:
        print(' ', r['line'], l, r['sec'], '→', h['sec'])
print('\n== 지위 불일치 (표 vs 머리 대괄호 ; 앞)')
for l, r in tbl.items():
    line = headline.get(l)
    if not line:
        continue
    st, seg = status_of(line)
    if st is None:
        print(' [대괄호 못 찾음]', l, seg[:120])
        continue
    tst = r['status']
    if by_label[l]['type'] == '정의' and tst == '정의':
        continue
    # 라벨을 정규화: 표는 {{..}} 그대로, 머리는 {{..}}
    if st != tst:
        print(' ', r['line'], l, '\n    표:', tst, '\n    머리:', st)
print('\n== 머리 줄 인용 라벨 불일치 (표의 "본문 인용:" 앞 라벨 집합 vs 머리 줄의 자기 이외 라벨)')
for l, r in tbl.items():
    line = headline.get(l)
    if not line:
        continue
    head_labels = [x for x in lab_re.findall(line) if x != l]
    inp = r['inputs']
    pre = inp.split('본문 인용:')[0]
    tbl_labels = [x for x in lab_re.findall(pre) if x != l]
    if sorted(set(head_labels)) != sorted(set(tbl_labels)):
        print(' ', r['line'], l, '\n    표:', sorted(set(tbl_labels)), '\n    머리:', sorted(set(head_labels)))
print('\n== 요지 불일치 (표의 요지 vs 머리 괄호 이름; 괄호 없는 머리는 건너뜀)')
for l, r in tbl.items():
    h = by_label[l]
    if h['name'] is None:
        continue
    if r['gist'] != h['name']:
        print(' ', r['line'], l, '\n    표:', r['gist'], '\n    머리:', h['name'])
json.dump(rows, open(os.path.join(ROOT, '대조v2', '수학검사2', '_R13_depmap_rows.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
