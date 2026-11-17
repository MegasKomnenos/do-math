# -*- coding: utf-8 -*-
# 검토전체23 R13: 장 파일의 진술 머리를 뽑아 번호를 매기고 JSON으로 저장한다.
import re, json, os, sys
base = r"C:\math\임시\주차함수_증명"
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CH = re.compile(r"^## (\d+)\.")
SEC = re.compile(r"^(#{2,5}) (\S+)")
heads = []
chap = None; cnt = {}
for f in files:
    p = os.path.join(base, "장v2", f + ".md")
    sec = None; sec3 = None
    for ln, line in enumerate(open(p, encoding="utf-8").read().split("\n"), 1):
        m = CH.match(line)
        if m:
            chap = int(m.group(1)); cnt.setdefault(chap, 0)
        m = SEC.match(line)
        if m:
            sec = m.group(2)
            if m.group(1) == "###": sec3 = m.group(2)
        m = HEAD_RE.match(line)
        if m:
            cnt[chap] += 1
            rest = line[m.end():]
            name = None
            mm = re.match(r" \(((?:[^()]|\([^()]*\))*)\)", rest)
            if mm: name = mm.group(1)
            st = None
            # status bracket: first " [" ... "].**" 
            j = rest.find("].**")
            i = rest.rfind(" [", 0, j) if j >= 0 else -1
            if i >= 0 and j > i: st = rest[i+2:j]
            heads.append(dict(file=f, line=ln, kind=m.group(1), label="{{%s:%s}}" % (m.group(2), m.group(3)),
                              num="%d.%d" % (chap, cnt[chap]), sec=sec, sec3=sec3, name=name, status=st))
json.dump(heads, open(os.path.join(base, "scripts", "수학검사2", "검토전체23_R13_heads.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(heads), cnt)
