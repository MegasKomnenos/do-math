# O14: 의존지도 1절의 「입력」(머리 선언 + 본문 인용) 라벨 집합을 현행 장 파일에서 다시 뽑아 비교한다.
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:/math/임시/주차함수_증명/"
CH = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
HEAD = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+:[^}]+)\}\}(.*?)\.\*\*')
blocks = {}  # label -> text (head line + body until next head), deferred proofs appended
order = []
for ch in CH:
    lines = open(BASE+"장v2/"+ch+".md", encoding='utf-8').read().split('\n')
    cur = None
    for line in lines:
        m = HEAD.match(line)
        if m:
            lab = m.group(2)
            if m.group(3).strip().startswith('의 증명'):
                cur = ('proof', lab)
                blocks.setdefault(lab, []).append(line)
                continue
            cur = ('head', lab); order.append(lab)
            blocks.setdefault(lab, []).append(line)
            continue
        if cur: blocks[cur[1]].append(line)
cites = {}
for lab, ls in blocks.items():
    s = "\n".join(ls)
    found = set(LAB.findall(s)) - {lab}
    cites[lab] = found
# 의존지도
dj = {}
in1=False
for line in open(BASE+"의존지도_v2.md", encoding='utf-8'):
    if line.startswith('## 1.'): in1=True; continue
    if line.startswith('### 1.1'): in1=False
    if not in1: continue
    m = re.match(r'^\| `\{\{([^`]+)\}\}` \| ([^|]*) \| ([^|]*) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line.strip())
    if m:
        dj[m.group(1)] = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', m.group(6)))
n=0
for lab in order:
    a = cites.get(lab, set()); b = dj.get(lab)
    if b is None: print("지도에 없음", lab); continue
    if a != b:
        n+=1
        print(f"{{{{{lab}}}}}: 지도에만 {sorted(b-a)} | 본문에만 {sorted(a-b)}")
print("다른 행 수:", n, "/", len(order))
