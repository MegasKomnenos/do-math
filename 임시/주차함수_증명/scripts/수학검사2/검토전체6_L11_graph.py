# -*- coding: utf-8 -*-
"""L11 검토 보조 2: 진술 인용 그래프를 만들어 11.3절의 공유/고유 입력 표를 대조한다.
블록 = 머리 줄부터 다음 머리 줄 직전까지(진술+증명+그 사이 산문). 과대 추정이므로 차이는 손으로 읽어 판정한다."""
import re, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
CH = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}(?= ?[(\[.])')
LAB = re.compile(r'\{\{([^}D][^}]*)\}\}')

blocks = {}   # label -> dict(type, head, body(list of lines), sec, file)
prose = []    # (file, sec, line_no, text) for lines not in any block? we attribute all lines to the preceding head within the same section
order = []
for fp in sorted(glob.glob(os.path.join(CH, "장*.md"))):
    cur = None; curlab = None
    for i, line in enumerate(open(fp, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^###+ (\d+(?:\.\d+)*)', line)
        if m:
            cur = m.group(1); curlab = None
        pm = re.match(r'^\*\*(?:정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}의 증명', line)
        if pm and pm.group(1) in blocks:
            curlab = pm.group(1)
            blocks[curlab]['body'].append((i, line))
            continue
        h = HEAD.match(line)
        if h:
            curlab = h.group(2)
            blocks[curlab] = dict(type=h.group(1), head=line, body=[], sec=cur, file=os.path.basename(fp), line=i)
            order.append(curlab)
            continue
        if curlab:
            blocks[curlab]['body'].append((i, line))
        else:
            prose.append((os.path.basename(fp), cur, i, line))

def cites(lab):
    b = blocks[lab]
    s = set(LAB.findall(b['head']))
    for _, l in b['body']: s |= set(LAB.findall(l))
    s.discard(lab)
    return s

def head_deps(lab):
    return set(LAB.findall(blocks[lab]['head'])) - {lab}

graph = {lab: cites(lab) for lab in blocks}

def closure(start):
    seen = set(); stack = [start]
    while stack:
        x = stack.pop()
        for y in graph.get(x, ()):
            if y not in seen and y in blocks:
                seen.add(y); stack.append(y)
    return seen

def chap(lab): return lab.split(':')[0]

if __name__ == '__main__':
    A = closure('9:old-7-46'); A.add('9:old-7-46')
    B = closure('10:old-8-37'); B.add('10:old-8-37')
    ante = lambda S: {x for x in S if chap(x) not in ('9', '10')}
    shared = ante(A) & ante(B)
    onlyA = ante(A) - ante(B)
    onlyB = ante(B) - ante(A)
    print("앞 장 입력(닫힘): 첫째", len(ante(A)), "둘째", len(ante(B)), "공유", len(shared), "첫째만", len(onlyA), "둘째만", len(onlyB))
    print("\n첫째만:", sorted(onlyA))
    print("\n둘째만:", sorted(onlyB))
    # 11.3 table labels
    ch11 = open(os.path.join(CH, "장11.md"), encoding='utf-8').read().split('\n')
    def table_after(marker):
        rows = []; on = False
        for l in ch11:
            if l.startswith(marker): on = True; continue
            if on:
                if l.startswith('| 입력 |') or l.startswith('|---'): continue
                if l.startswith('|'): rows.append(l)
                elif rows: break
        return rows
    T_sh = table_after('**공유 입력.**'); T_a = table_after('**첫째 증명의 고유 입력.**'); T_b = table_after('**둘째 증명의 고유 입력.**')
    def inputs_of(rows):
        s = set()
        for r in rows:
            cells = [c.strip() for c in r.strip().strip('|').split(' | ')]
            s |= set(LAB.findall(cells[0]))
        return s
    I_sh, I_a, I_b = inputs_of(T_sh), inputs_of(T_a), inputs_of(T_b)
    print("\n표: 공유", len(I_sh), "첫째", len(I_a), "둘째", len(I_b))
    print("\n[표 공유인데 닫힘상 공유 아님]:", sorted(x for x in I_sh if x not in shared), )
    for x in sorted(I_sh):
        if x not in shared: print("   ", x, "A" if x in A else "-", "B" if x in B else "-")
    print("\n[닫힘상 공유인데 표 공유에 없음]:", sorted(shared - I_sh))
    print("\n[표 첫째 고유인데 닫힘상]:", [(x, 'A' if x in A else '-', 'B' if x in B else '-') for x in sorted(I_a) if not (x in A and x not in B)])
    print("\n[표 둘째 고유인데 닫힘상]:", [(x, 'A' if x in A else '-', 'B' if x in B else '-') for x in sorted(I_b) if not (x in B and x not in A)])
    print("\n[닫힘상 첫째만(앞 장)인데 표 첫째 고유에 없음]:", sorted(onlyA - I_a))
    print("\n[닫힘상 둘째만(앞 장)인데 표 둘째 고유에 없음]:", sorted(onlyB - I_b))
    # 9/10장 중간 진술 중 표 첫째/둘째 고유에 든 것과 닫힘
    print("\n[표 첫째 고유의 9장 진술이 A 닫힘에 없음]:", sorted(x for x in I_a if chap(x) == '9' and x not in A))
    print("[표 둘째 고유의 10장 진술이 B 닫힘에 없음]:", sorted(x for x in I_b if chap(x) == '10' and x not in B))
    # who cites each input directly among 9/10 statements in closures, plus 7:old-6-22 block
    print("\n=== 입력별 직접 인용 진술(9·10장 닫힘 안, 그리고 7:old-6-22) ===")
    allin = I_sh | I_a | I_b
    for x in sorted(allin, key=lambda s: (int(chap(s)) if chap(s).isdigit() else 0, s)):
        citersA = sorted(c for c in A if chap(c) == '9' and x in graph[c])
        citersB = sorted(c for c in B if chap(c) == '10' and x in graph[c])
        c722 = x in graph.get('7:old-6-22', set())
        print(f"{x}: 9장 {citersA} | 10장 {citersB} | 7:old-6-22 {'Y' if c722 else '-'}")

    print("\n=== 10장 블록이 9장 라벨 또는 첫째 고유 입력을 인용하는 자리 ===")
    for c in sorted(B):
        if chap(c) != '10': continue
        hits = sorted(x for x in graph[c] if chap(x) == '9' or x in I_a)
        if hits:
            b = blocks[c]
            for i, l in [(b['line'], b['head'])] + b['body']:
                for x in hits:
                    if '{{' + x + '}}' in l: print(f"  {c} L{i} cites {x}: …{l[max(0, l.find('{{'+x)-120):l.find('{{'+x)+80]}…")
    print("\n=== 7:old-6-22 블록이 인용하는 라벨 ===", sorted(graph['7:old-6-22']))
    print("=== 7:old-6-21 블록이 인용하는 라벨 ===", sorted(graph['7:old-6-21']))
    print("=== 9:old-7-46 블록 ===", sorted(graph['9:old-7-46']))
    print("=== 9:old-7-45 블록 ===", sorted(graph['9:old-7-45']))
    print("=== 10:old-8-37 블록 ===", sorted(graph['10:old-8-37']))
    print("=== 10:old-8-10 블록 ===", sorted(graph['10:old-8-10']))
    print("=== 6:old-8-13 블록 ===", sorted(graph['6:old-8-13']))
    print("=== 6:cor-L 블록 ===", sorted(graph['6:cor-L']))
    print("=== 5:old-5-18 블록 ===", sorted(graph['5:old-5-18']))
