# -*- coding: utf-8 -*-
"""11.2절 표의 각 행을 부록 D 항목과 대조한다 (O11, 9차 검토)."""
import re, glob, io, sys, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"

# 부록 D 읽기
items = {}
for f in sorted(glob.glob(BASE + r"\부록D_장*.md")):
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^### D\.\{\{D:([^}]+)\}\}', txt)
    for i in range(1, len(parts), 2):
        key = parts[i]; body = parts[i+1]
        head = body.split('\n',1)[0]
        d = {'file': f.split('\\')[-1], 'head': head}
        for line in body.split('\n'):
            m = re.match(r'\*\*([^*]+)\.\*\*\s*(.*)', line)
            if m:
                d[m.group(1)] = m.group(2)
        items[key] = d

# 11.2 표 읽기
ch11 = open(BASE + r"\장11.md", encoding='utf-8').read()
rows = [l for l in ch11.split('\n') if l.startswith('| 부록 D.{{D:')]
print("D 항목 수", len(items), "표 행 수", len(rows))
seen = set()
for r in rows:
    cells = [c.strip() for c in r.strip().strip('|').split(' | ')]
    if len(cells) != 6:
        # 셀 안에 ' | '가 없다고 가정; 실패 시 보고
        print("!! 셀 분리 실패", r[:80]); continue
    key = re.search(r'\{\{D:([^}]+)\}\}', cells[0]).group(1)
    seen.add(key)
    d = items.get(key)
    if d is None:
        print("!! 표에만 있음", key); continue
    print("\n====", key, "(", d['file'], ")")
    # 1 확인하는 진술: 머리의 괄호 안
    hm = re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$', d['head'])
    head_stmts = hm.group(1) if hm else '?'
    print(" 머리 괄호 :", head_stmts)
    print(" 표 진술   :", cells[1])
    # 라벨 집합 비교
    lab_h = set(re.findall(r'\{\{([^}]+)\}\}', head_stmts))
    lab_t = set(re.findall(r'\{\{([^}]+)\}\}', cells[1]))
    if lab_h != lab_t:
        print(" !! 라벨 집합 다름: 머리-표", lab_h - lab_t, "표-머리", lab_t - lab_h)
    # 2 산술 등급
    grade = d.get('산술 등급', '?')
    print(" D 산술 등급:", grade[:150])
    print(" 표 산술 등급:", cells[2])
    # 3 독립 재계산
    ind = d.get('독립 재계산', '?')
    m = re.match(r'〔([^〕]*)〕\s*(.*)', ind)
    if m:
        br, rest = m.group(1), m.group(2)
        tb = cells[4].strip('〔〕')
        if br != tb:
            print(" !! 꺾쇠 다름\n   D:", br, "\n   표:", tb)
        rest2 = rest.replace('이 문단 머리의 꺾쇠 괄호', '「재계산」 열의 꺾쇠 괄호')
        if rest2 != cells[5]:
            print(" !! 서술 다름")
            sm = difflib.SequenceMatcher(None, rest2, cells[5])
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != 'equal':
                    print(f"   {tag}: D[{rest2[max(0,i1-20):i2+20]}] / 표[{cells[5][max(0,j1-20):j2+20]}]")
    else:
        print(" !! D 독립 재계산 줄에 꺾쇠가 없음:", ind[:100])
    print(" 쓰인 곳:", cells[3])
print("\nD에만 있음:", set(items) - seen)
