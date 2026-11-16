# -*- coding: utf-8 -*-
"""11.2절 표의 각 행을 부록 D 항목과 본문 진술 머리와 나란히 놓는다(판정은 사람이 읽어서 한다)."""
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
ch11 = open(root+"장11.md", encoding="utf-8").read().split("\n")
rows = [l for l in ch11 if l.startswith("| 부록 D.{{D:")]
# 부록 D items
items = {}
for f in glob.glob(root+"부록D_장*.md"):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"(?m)^### D\.\{\{D:([^}]+)\}\}", txt)
    for i in range(1, len(parts), 2):
        key = parts[i]; body = parts[i+1]
        title = body.split("\n",1)[0].strip()
        def line(name):
            m = re.search(r"\*\*"+name+r"\.\*\*\s*(.*)", body)
            return m.group(1).strip() if m else "(없음)"
        items[key] = dict(file=f.split("/")[-1], title=title, 진술=line("확인하는 진술"), 등급=line("산술 등급"), 재계산=line("독립 재계산"), 범위=line("범위"))
# statement heads
heads = {}
for f in glob.glob(root+"장*.md"):
    for l in open(f, encoding="utf-8"):
        m = re.match(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?:[^}]+)\}\}(.*?)\*\*", l)
        if m:
            heads[m.group(2)] = (m.group(1), m.group(3).strip(), f.split("/")[-1])
# sections: map label -> section number
sec_of = {}
for f in glob.glob(root+"장*.md"):
    cur = None
    for l in open(f, encoding="utf-8"):
        m = re.match(r"###+ (\d+\.\d+(\.\d+)?)", l)
        if m: cur = m.group(1)
        m2 = re.match(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?:[^}]+)\}\}", l)
        if m2: sec_of[m2.group(2)] = cur
for r in rows:
    cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
    key = re.search(r"\{\{D:([^}]+)\}\}", cells[0]).group(1)
    it = items.get(key)
    print("="*100)
    print("행:", cells[0], "|", cells[1], "|", cells[2], "|", cells[3])
    print("행 재계산:", cells[4])
    if not it: print("!!! 부록 D 항목 없음"); continue
    print("D 파일:", it["file"], "| 제목:", it["title"])
    print("D 등급:", it["등급"])
    print("D 범위:", it["범위"][:300])
    br = re.match(r"(〔[^〕]*〕)\s*(.*)", it["재계산"])
    print("D 꺾쇠:", br.group(1) if br else "(없음)")
    rest = br.group(2) if br else it["재계산"]
    if rest.strip() == cells[5].strip(): print("독립 재계산 서술: 같음")
    else:
        print("독립 재계산 서술: 다름")
        # show first difference
        a, b = rest.strip(), cells[5].strip()
        i = 0
        while i < min(len(a),len(b)) and a[i]==b[i]: i+=1
        print("  D : ...", a[max(0,i-60):i+120])
        print("  표: ...", b[max(0,i-60):i+120])
    for lab in re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", cells[1]):
        h = heads.get(lab)
        print("  진술", lab, "절", sec_of.get(lab), "->", h[0] if h else "!!없음", "|", (h[1][:400] if h else ""))
