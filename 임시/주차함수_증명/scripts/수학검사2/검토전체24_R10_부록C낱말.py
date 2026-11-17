# 부록 C 낱말 표의 「이 글의 용어」가 장 파일에서 처음 나오는 절을 「처음 정의된 절」 칸과 견준다(자리 찾기; 어긋난 행은 원문을 읽어 판단).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명/장v2/'
names = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
docs = []
for n in names:
    sec = n
    for i, l in enumerate(open(base+n+'.md', encoding='utf-8').read().split('\n')):
        m = re.match(r'^#{2,4} (\d+(?:\.\d+)*)', l)
        if m: sec = m.group(1)
        docs.append((n, i+1, sec, l))
C = open(base+'부록C.md', encoding='utf-8').read().split('\n')
a = next(i for i,l in enumerate(C) if l.startswith('### 낱말'))
b = next(i for i,l in enumerate(C) if l.startswith('### 기록이 결과에'))
for i in range(a, b):
    l = C[i]
    if not l.startswith('| ') or l.startswith('| 이 글의') or l.startswith('|---'): continue
    cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
    terms = re.split(r', |·', re.sub(r'\([^)]*\)', '', cells[0]))
    claimed = re.findall(r'\d+\.\d+', cells[-1])
    for t in terms:
        t = t.strip()
        if not t: continue
        occ = []
        for n, ln, sec, line in docs:
            if t in line:
                s2 = '.'.join(sec.split('.')[:2])
                if not occ or occ[-1][2] != s2: occ.append((n, ln, s2))
                if len(occ) >= 4: break
        firsts = [o[2] for o in occ]
        flag = '' if (firsts and firsts[0] in claimed) else '  <<<'
        print(f'C:{i+1} 「{t}」 claimed={cells[-1]} first={[(o[0],o[1],o[2]) for o in occ[:3]]}{flag}')
