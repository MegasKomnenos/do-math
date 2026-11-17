# R13 검토 22차: 장 파일의 진술 머리를 순서대로 뽑는다(읽기 전용).
import re, sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = r"C:/math/임시/주차함수_증명/장v2/"
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
KIND = "정의|정리|보조정리|명제|따름정리|관찰|주의|예|가설|추측|사실|계산|주장|문제|질문|규약|표기|기호"
head_re = re.compile(r'^\*\*([^\s*{]+) \{\{(\d+):([^}]+)\}\}(.*)$')
def parse(rest):
    # rest: text after label, up to closing '.**'
    name = None; status = None
    s = rest
    if s.startswith('의 증명') or s.startswith('의 ') :
        return None
    # find end of head: first occurrence of '.**'
    i = s.find('.**')
    head = s if i < 0 else s[:i]
    h = head.strip()
    # name: leading parenthesis (balanced)
    if h.startswith('('):
        d = 0
        for j,ch in enumerate(h):
            if ch == '(':
                d += 1
            elif ch == ')':
                d -= 1
                if d == 0:
                    name = h[1:j]; h = h[j+1:].strip(); break
    if h.startswith('['):
        d = 0
        for j,ch in enumerate(h):
            if ch == '[':
                d += 1
            elif ch == ']':
                d -= 1
                if d == 0:
                    status = h[1:j]; h = h[j+1:].strip(); break
    return name, status, h, (i >= 0)
out = []
cnt = {}
for f in files:
    L = open(base+f+".md", encoding='utf-8').read().split('\n')
    sec = None; sec_title = None
    for ln, line in enumerate(L, 1):
        m = re.match(r'^###\s+(\S+)\s*(.*)$', line)
        if m and not line.startswith('####'):
            sec = m.group(1); sec_title = m.group(2)
        m = head_re.match(line)
        if m:
            kind, ch, lab, rest = m.groups()
            p = parse(rest)
            if p is None:
                out.append(dict(file=f, line=ln, kind=kind, label=f"{ch}:{lab}", proof=True)); continue
            name, status, tail, closed = p
            chn = re.match(r'장(\d+)', f).group(1)
            cnt[chn] = cnt.get(chn, 0) + 1
            out.append(dict(file=f, line=ln, kind=kind, label=f"{ch}:{lab}", name=name, status=status, tail=tail, closed=closed, sec=sec, sec_title=sec_title, num=f"{chn}.{cnt[chn]}", proof=False))
json.dump(out, open(r"C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체22_R13_heads.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
heads = [o for o in out if not o['proof']]
print(len(heads), 'heads;', len(out)-len(heads), 'proof lines')
from collections import Counter
print(Counter(o['kind'] for o in heads))
print([ (o['file'],o['line'],o['label']) for o in heads if o['tail'] or not o['closed']])
c = Counter(o['label'] for o in heads)
print('dups', [k for k,v in c.items() if v>1])
print(cnt)
