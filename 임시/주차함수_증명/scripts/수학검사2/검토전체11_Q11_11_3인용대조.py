# -*- coding: utf-8 -*-
"""11.3절 세 표의 「직접 인용하는 자리」가 실제로 그 입력을 인용하는지 자리를 찾는다.
진술 블록 = 머리 줄부터 다음 머리 줄 또는 다음 절 머리 직전까지(증명과 바로 뒤 준비 문단 포함).
판단은 출력을 읽고 사람이 한다."""
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명\장v2'

# 블록 수집
blocks = {}   # label -> text
sections = {} # (chapter file, sec) -> text
for f in sorted(glob.glob(ROOT + r'\장*.md')):
    lines = open(f, encoding='utf-8').read().split('\n')
    cur = None; sec = None
    for ln in lines:
        ms = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)', ln)
        if ms:
            sec = ms.group(1); cur = None
        mh = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}', ln)
        if mh:
            cur = mh.group(2); blocks.setdefault(cur, '')
        if cur: blocks[cur] += ln + '\n'
        key = (f.split('\\')[-1], sec)
        sections[key] = sections.get(key, '') + ln + '\n'

ch11 = open(ROOT + r'\장11.md', encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(ch11) if l.startswith('### 11.3'))
end = next(i for i, l in enumerate(ch11) if l.startswith('### 11.4'))
tbl = [l for l in ch11[start:end] if l.startswith('| ') and not l.startswith('| 입력') and not l.startswith('|---')]
print('11.3 rows:', len(tbl))
LAB = re.compile(r'\{\{(\d+[AB]?:[^}]+)\}\}')
for row in tbl:
    cells = [c.strip() for c in row.strip().strip('|').split(' | ')]
    inputs = LAB.findall(cells[0])
    print('\n' + '=' * 90)
    print('INPUT ROW:', cells[0][:160])
    for ci, col in enumerate(cells[2:]):
        print(f' -- 인용 열 {ci+1}: {col[:200]}{"..." if len(col)>200 else ""}')
        citers = LAB.findall(col)
        # 괄호 안의 라벨(입력 자신)은 제외하려 하지 않고 모두 검사하되, 입력 라벨은 건너뜀
        for c in citers:
            if c in inputs: continue
            b = blocks.get(c)
            if b is None:
                print(f'    !! citer block not found: {c}'); continue
            found = [i for i in inputs if ('{{' + i + '}}') in b]
            missing = [i for i in inputs if ('{{' + i + '}}') not in b]
            print(f'    citer {c}: cites {found}' + (f'   ?? NOT citing {missing}' if missing else ''))
