# -*- coding: utf-8 -*-
"""E14: 장부 5절의 「이 장이 처음 정의하는 전역 기호」·「낱말」 열을 1.2·3절에서 다시 만들어 견주고, 뺌 라벨 집합(4절·의존지도 1.1·대응표)을 견준다."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
lines = open(f"{ROOT}/장부_v2.md", encoding='utf-8').read().split("\n")
def block(a, b):
    s = next(i for i,l in enumerate(lines) if l.startswith(a))
    e = next(i for i,l in enumerate(lines) if l.startswith(b))
    return lines[s:e]
norm = lambda s: re.sub(r'\s+', '', s)
# 1.2 → 장별 정의 기호
sym_by_ch = {c:set() for c in range(1,12)}
for l in block("### 1.2", "### 1.3"):
    if not l.startswith("| $"): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    latex, defsec = cells[0], cells[3]
    chs = set(int(m.group(1)) for m in re.finditer(r'(?<![\d.])(\d+)\.\d+', defsec))
    for c in chs: sym_by_ch[c].add(norm(latex))
# 3절 → 장별 낱말
word_by_ch = {c:set() for c in range(1,12)}
for l in block("## 3.", "## 4."):
    if not l.startswith("| ") or l.startswith("| 낱말") or l.startswith("|---"): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells)<4: continue
    words, first = cells[0], cells[2]
    chs = [int(m.group(1)) for m in re.finditer(r'(?<![\d.])(\d+)(?:\.\d+)?', first)]
    if not chs or first.startswith('—') or first.startswith('부록'): continue
    word_by_ch[min(chs)].add(norm(words))
# 5절 표
for l in block("## 5.", "## 6."):
    m = re.match(r'\| (\d+) \|', l)
    if not m: continue
    c = int(m.group(1))
    cells=[x.strip() for x in l.strip().strip("|").split("|")]
    syms = set(norm(x) for x in cells[1].split(';') if x.strip() and x.strip()!='없음')
    words = set(norm(x) for x in cells[2].split(';') if x.strip())
    # 기호: 1.2 정의 절의 장과 비교(장식·첨자 차이는 부분 일치로 느슨하게)
    only5 = [s for s in syms if s not in sym_by_ch[c] and not any(s in t or t in s for t in sym_by_ch[c])]
    only12 = [t for t in sym_by_ch[c] if t not in syms and not any(t in s or s in t for s in syms)]
    print(f"== 장 {c} 기호: 5절에만 {only5} | 1.2에만 {only12}")
    w5 = [w for w in words if w not in word_by_ch[c]]
    w3 = [w for w in word_by_ch[c] if w not in words]
    print(f"   낱말: 5절에만 {w5} | 3절에만 {w3}")
# 뺌 집합
rm4=set()
for l in block("## 4.", "## 5."):
    if not l.startswith("| "): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells)==6 and cells[4]=='뺌':
        m=re.match(r'\((\d+:[^)]+)\)', cells[5]); rm4.add(m.group(1) if m else cells[2])
dep=open(f"{ROOT}/의존지도_v2.md",encoding='utf-8').read().split("\n")
s=next(i for i,l in enumerate(dep) if l.startswith("### 1.1")); e=next(i for i,l in enumerate(dep) if l.startswith("## 2."))
rmD=set()
for l in dep[s:e]:
    m=re.match(r'\| `\{\{(\d+:[^}]+)\}\}`', l)
    if m: rmD.add(m.group(1))
    elif l.startswith("| (라벨 없음)"): rmD.add(l.split("|")[1].strip())
tbl=open(f"{ROOT}/대조v2/라벨_번호_대응표_1114.md",encoding='utf-8').read()
rmT=set(re.findall(r'`\((\d+:[^)]+)\)`', tbl))
print("\n4절 뺌 행:", len(rm4), "| 의존지도 1.1 행:", len(rmD), "| 대응표 뺌 행:", len(rmT))
print("4절에만(의존지도 대비):", sorted(rm4-rmD)); print("의존지도에만:", sorted(rmD-rm4))
print("4절에만(대응표 대비):", sorted(rm4-rmT)); print("대응표에만:", sorted(rmT-rm4))
