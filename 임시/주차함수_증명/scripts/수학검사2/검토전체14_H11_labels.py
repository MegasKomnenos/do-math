# -*- coding: utf-8 -*-
"""H11: 장 파일 머리에서 (라벨 -> 유형, 이름, 기록이름) 지도를 만들고,
장11/부록A/부록C 가 '유형 {{장:라벨}}' 로 부르는 자리의 유형이 머리와 맞는지 검사한다.
또 장11의 D 라벨이 부록 D 파일에 있는지 본다."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
head_re = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?|D):([^}]+)\}\}\s*(\(([^)]*)\))?\s*(\[([^\]]*)\])?')
label_map = {}
for f in sorted(glob.glob(os.path.join(root, '장*.md'))):
    ch = os.path.basename(f)[1:-3]
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = head_re.match(line)
        if m:
            typ, c, lab, _, name, _, tag = m.groups()
            key = f'{c}:{lab}'
            if key in label_map:
                print('DUP HEAD', key, os.path.basename(f), ln, label_map[key][3])
            label_map[key] = (typ, name, tag, f'{os.path.basename(f)}:{ln}', line.strip()[:200])
print('heads:', len(label_map))
# D labels
d_labels = {}
for f in sorted(glob.glob(os.path.join(root, '부록D_장*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'\{\{D:([^}]+)\}\}', line):
            d_labels.setdefault(m.group(1), []).append(f'{os.path.basename(f)}:{ln}')
# D item heads: lines starting with '### ' or '**D.' ? detect
d_heads = {}
for f in sorted(glob.glob(os.path.join(root, '부록D_장*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^(#+\s*|\*\*)?(부록\s*)?D\.\{\{D:([^}]+)\}\}', line.strip())
        if m:
            d_heads[m.group(3)] = f'{os.path.basename(f)}:{ln}'
print('D heads:', len(d_heads), sorted(d_heads)[:5])
ref_re = re.compile(r'(정리|명제|보조정리|따름정리|정의)\s+`?\{\{(\d+[AB]?|D):([^}]+)\}\}`?')
chain_re = re.compile(r'`?\{\{(\d+[AB]?):([^}]+)\}\}`?')
for fname in ['장11.md', '부록A.md', '부록C.md']:
    f = os.path.join(root, fname)
    print('=====', fname)
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        # typed references
        for m in ref_re.finditer(line):
            typ, c, lab = m.groups()
            key = f'{c}:{lab}'
            if c == 'D':
                continue
            if key not in label_map:
                print(f'  MISSING LABEL  {fname}:{ln}  {typ} {{{{{key}}}}}')
            elif label_map[key][0] != typ:
                print(f'  TYPE MISMATCH  {fname}:{ln}  text={typ} head={label_map[key][0]}  {{{{{key}}}}}  ({label_map[key][3]})')
        # untyped references existence
        for m in chain_re.finditer(line):
            key = f'{m.group(1)}:{m.group(2)}'
            if key not in label_map:
                print(f'  MISSING LABEL(untyped)  {fname}:{ln}  {{{{{key}}}}}')
        for m in re.finditer(r'\{\{D:([^}]+)\}\}', line):
            if m.group(1) not in d_heads:
                print(f'  MISSING D LABEL  {fname}:{ln}  {m.group(1)}')
# chain-list refs like 정리 {{a}}·{{b}} : second item type check (type inherited)
for fname in ['장11.md']:
    f = os.path.join(root, fname)
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'(정리|명제|보조정리|따름정리|정의)\s+((?:\{\{\d+[AB]?:[^}]+\}\}(?:·|,\s*)?)+)', line):
            typ = m.group(1)
            labs = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', m.group(2))
            # only '·'-joined inherit the type
            parts = re.split(r'·', m.group(2))
            if len(parts) > 1:
                for p in parts[1:]:
                    for lab in re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', p):
                        if lab in label_map and label_map[lab][0] != typ:
                            print(f'  CHAIN TYPE MISMATCH {fname}:{ln} text={typ} head={label_map[lab][0]} {{{{{lab}}}}}')
# dump label map for later use
import json
json.dump({k: list(v) for k, v in label_map.items()}, open(os.path.join(os.path.dirname(__file__), '_H11_labelmap.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('D heads not in 장11 table:', sorted(set(d_heads) - set(re.findall(r'\| 부록 D\.\{\{D:([^}]+)\}\} \|', open(os.path.join(root,'장11.md'),encoding='utf-8').read()))))
