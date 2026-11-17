# -*- coding: utf-8 -*-
# 대응표 15:52 번호 열의 내적 정합(장마다 1..N 연속·중복 없음)과 뺌 행의 주석이 부르는 현행 라벨의 실재.
import re, json, os, collections
base = r"C:\math\임시\주차함수_증명"
heads = json.load(open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_heads.json"),encoding="utf-8"))
hd = {h["label"][2:-2]:h for h in heads}
M = open(os.path.join(base,"대조v2","라벨_번호_대응표_1114.md"),encoding="utf-8").read().split("\n")
nums=collections.defaultdict(list)
for i,l in enumerate(M,1):
    if l.startswith("| `"):
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        v=c[4]
        if re.fullmatch(r"\d+\.\d+",v):
            a,b=v.split("."); nums[int(a)].append((int(b),i,c[0]))
        else:
            if l.startswith("| `("): print("뺌 행 15:52 값:",i,c[0],v)
        if l.startswith("| `("):
            for m in re.finditer(r"`(\d+:[A-Za-z0-9\-]+)`",c[2]+c[3]):
                if m.group(1) not in hd: print("주석의 라벨이 현행 머리에 없음",i,c[0],m.group(1))
            for m in re.finditer(r"\{\{(\d+:[A-Za-z0-9\-]+)\}\} (\d+\.\d+)",c[3]):
                h=hd.get(m.group(1))
                if not h or h["num"]!=m.group(2): print("옮김 번호 다름",i,c[0],m.group(0),h and h["num"])
for ch in sorted(nums):
    v=sorted(nums[ch]); ns=[x[0] for x in v]
    miss=[k for k in range(1,max(ns)+1) if k not in ns]
    dup=[k for k,cn in collections.Counter(ns).items() if cn>1]
    print(ch,"max",max(ns),"count",len(ns),"빠짐",miss,"중복",dup)
    for d in dup: print("   ",[x for x in v if x[0]==d])
import collections as C
print(C.Counter(c for c in [ [x.strip() for x in l.strip()[1:-1].split(" | ")][4] for l in M if l.startswith("| `{{")] if not re.fullmatch(r"\d+\.\d+",c)))
