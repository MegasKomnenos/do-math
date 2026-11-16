# -*- coding: utf-8 -*-
"""A12: 부록 D 42항목의 머리·확인하는 진술·산술 등급·범위·자료 줄을 뽑고,
각 D 라벨이 장v2 어디서 인용되는지(파일·행) 센다."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
files = sorted(glob.glob(os.path.join(ROOT, '장v2', '부록D_장*.md')))
items = []
for f in files:
    txt = open(f, encoding='utf-8').read()
    lines = txt.split('\n')
    cur = None
    for i, ln in enumerate(lines, 1):
        m = re.match(r'^### D\.\{\{(D:[^}]+)\}\}\s*(.*)$', ln)
        if m:
            cur = {'file': os.path.basename(f), 'line': i, 'label': m.group(1), 'title': m.group(2).strip(), 'fields': {}}
            cur['head_refs'] = re.findall(r'\{\{([^}]+)\}\}', m.group(2))
            items.append(cur)
            continue
        if cur is None: continue
        m = re.match(r'^\*\*([^*]+)\.\*\*\s*(.*)$', ln)
        if m:
            cur['fields'][m.group(1)] = m.group(2)
# consumers: grep D labels across 장v2 (excluding 부록D files themselves) and 장부
chap = sorted(glob.glob(os.path.join(ROOT, '장v2', '*.md')))
chap_txt = {os.path.basename(c): open(c, encoding='utf-8').read().split('\n') for c in chap}
out = []
for it in items:
    lab = it['label']
    tok = '{{' + lab + '}}'
    cons = []
    for name, lns in chap_txt.items():
        if name.startswith('부록D_'): continue
        for j, ln in enumerate(lns, 1):
            if tok in ln:
                cons.append((name, j, ln.count(tok)))
    it['consumers'] = cons
    out.append(it)
print(f'항목 수: {len(items)}')
for it in items:
    print('=' * 100)
    print(f"[{it['file']}:{it['line']}] {it['label']}")
    print('  제목:', it['title'][:200])
    print('  머리 라벨:', it['head_refs'])
    print('  산술 등급:', it['fields'].get('산술 등급', '')[:200])
    print('  범위:', it['fields'].get('범위', '')[:300])
    print('  확인하는 진술:', it['fields'].get('확인하는 진술', '')[:500])
    print('  자료:', it['fields'].get('자료', '')[:600])
    print('  인용(부록D 밖):', [(c[0], c[1]) for c in it['consumers']])
json.dump([{k: v for k, v in it.items()} for it in items], open(os.path.join(ROOT, 'scripts', '구조압축', '심사_A12_장부.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
