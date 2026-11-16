# -*- coding: utf-8 -*-
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}")
secof = {}
for f in sorted(glob.glob(R+"장v2/장*.md")):
    sec = None
    for l in open(f, encoding="utf-8"):
        ms = re.match(r"^###\s+(\d+\.\d+)\b", l)
        if ms: sec = ms.group(1)
        m = HEAD.match(l)
        if m: secof[m.group(2)] = sec
ch11 = open(R+"장v2/장11.md", encoding="utf-8").read().split("\n")
print("=== 11.2 쓰인 곳 열 vs 진술의 절")
for ln, line in enumerate(ch11, 1):
    m = re.match(r"\| 부록 D\.\{\{(D:[^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \|", line)
    if m:
        st = re.findall(r"\{\{(\d+:[^}]+)\}\}", m.group(2))
        secs = sorted(set(secof.get(s, "?") for s in st), key=lambda x: [int(t) for t in x.split(".")] if x!="?" else [99])
        claimed = m.group(4)
        flag = "" if "·".join(secs) == claimed else "   <<<"
        print(f"  행{ln} {m.group(1)}: 표 '{claimed}' / 진술 절 {secs}{flag}")
print("\n=== 부록 D 괄호 네 항목의 어휘")
vals = {0:set(),1:set(),2:set(),3:set()}
for f in sorted(glob.glob(R+"장v2/부록D_장*.md")):
    for br in re.findall(r"〔([^〕]*)〕", open(f, encoding="utf-8").read()):
        parts = [p.strip() for p in br.split(";")]
        for i,p in enumerate(parts[:4]):
            vals[i].add(re.sub(r"\(.*?\)", "", p).strip())
for i,n in enumerate(["구현","범위","산술","자료"]):
    print(n, sorted(vals[i]))
