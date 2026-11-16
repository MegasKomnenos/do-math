# -*- coding: utf-8 -*-
"""9장·10장 끝 정리에서 인용 연쇄를 거슬러 닿는 9장·10장 진술(폐포)을 구하고, 그 진술들이 인용하는 앞 장 라벨을 11.3절 표의 라벨과 견준다."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
HEAD = re.compile(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?:[^}]+)\}\} [\(\[]")
def blocks(fname):
    t = open(root+fname, encoding="utf-8").read().split("\n")
    out = {}; cur=None; buf=[]
    for l in t:
        if l.startswith("### "):
            if cur: out[cur]="\n".join(buf); cur=None; buf=[]
            continue
        m = HEAD.match(l)
        if m:
            if cur: out[cur]="\n".join(buf)
            cur=m.group(2); buf=[l]
        elif cur:
            buf.append(l)
            if "∎" in l: out[cur]="\n".join(buf); cur=None; buf=[]
    if cur: out[cur]="\n".join(buf)
    return out
B = {}
B.update(blocks("장9.md")); B.update(blocks("장10.md"))
b7 = blocks("장7B.md"); B["7:old-6-22"] = b7["7:old-6-22"]
def closure(start):
    seen=set(); stack=[start]
    while stack:
        x=stack.pop()
        if x in seen or x not in B: continue
        seen.add(x)
        for lab in re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", B[x]):
            if lab in B and lab not in seen: stack.append(lab)
    return seen
c1 = closure("9:old-7-46"); c2 = closure("10:old-8-37")
print("첫째 폐포(9장·10장·6-22):", sorted(c1))
print("둘째 폐포:", sorted(c2))
all9 = [k for k in B if k.startswith("9:")]; all10=[k for k in B if k.startswith("10:")]
print("폐포 밖 9장 진술:", sorted(set(all9)-c1-c2))
print("폐포 밖 10장 진술:", sorted(set(all10)-c1-c2))
def ext(cl):
    s=set()
    for x in cl:
        for lab in re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", B[x]):
            if not (lab.startswith("9:") or lab.startswith("10:") or lab.startswith("D:")) and lab!="7:old-6-22": s.add(lab)
    return s
e1, e2 = ext(c1), ext(c2)
ch11 = open(root+"장11.md", encoding="utf-8").read()
sec = ch11.split("### 11.3")[1].split("### 11.4")[0]
tab_labels = set(re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", sec))
print("\n첫째 폐포가 직접 인용하는 앞 장 라벨 가운데 11.3절에 없는 것:", sorted(e1 - tab_labels))
print("둘째 폐포가 직접 인용하는 앞 장 라벨 가운데 11.3절에 없는 것:", sorted(e2 - tab_labels))
print("\n첫째·둘째 폐포 둘 다 직접 인용하는 앞 장 라벨:", sorted(e1 & e2))
print("첫째만:", sorted(e1 - e2)); print("둘째만:", sorted(e2 - e1))
# 9장/10장 계산 진술(머리에 계산 증거/계산 보조)
for k in sorted(c1|c2):
    h = B[k].split("\n")[0]
    if "계산" in h.split("**")[1]: print("계산 진술:", k, "|", h.split("**")[1][:160])
