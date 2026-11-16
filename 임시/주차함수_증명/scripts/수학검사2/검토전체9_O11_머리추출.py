# -*- coding: utf-8 -*-
"""장 파일에서 진술 머리를 추출해 라벨→(유형, 이름, 기록 이름, 표지, 파일, 절)을 만든다 (O11)."""
import re, glob, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
files = [f for f in glob.glob(BASE + r"\장*.md") if '부록' not in f]
heads = {}
sections = {}
for f in sorted(files):
    cur = ''
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^#{2,4}\s+(\d+(?:\.\d+)*)\s', line)
        if m:
            cur = m.group(1)
        for hm in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+:[^}]+)\}\}\s*(.*?)\*\*', line):
            typ, lab, rest = hm.group(1), hm.group(2), hm.group(3)
            if rest.startswith('의 ') or rest.startswith('의증명'): continue
            if lab in heads: print('!! 중복 머리', lab, f, ln)
            heads[lab] = {'type': typ, 'rest': rest, 'file': f.split('\\')[-1], 'line': ln, 'sec': cur}
json.dump(heads, open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_O11_heads.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(heads), "heads")
# 라벨 정의 중복 확인
for lab, h in heads.items():
    print(f"{lab}\t{h['type']}\t{h['file']}:{h['line']}\t{h['sec']}\t{h['rest'][:160]}")
