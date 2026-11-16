# -*- coding: utf-8 -*-
"""부록 C 「기록이 결과에 붙인 이름과 이 글의 번호」 표를 진술 머리와 맞춘다."""
import re, os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
from 검토전체3_I11_index import labels, CH
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
C = open(os.path.join(CH,"부록C.md"),encoding="utf-8").read()
sec = C.split("### 기록이 결과에 붙인 이름과 이 글의 번호")[1].split("### 기록의 글자와 이 글의 글자")[0]
rows=[l for l in sec.splitlines() if l.startswith("| 기록")]
print("행 수:",len(rows))
used=set()
for l in rows:
    c=[x.strip() for x in l.strip().strip("|").split("|")]
    recname, stmt, ourname = c
    m=re.search(r"(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?):([^}]+)\}\}", stmt)
    if not m: print("!! 진술 칸 해석 불가:", l[:120]); continue
    kind, ch, lab = m.groups()
    key=[k for k in labels if k[1]==lab and k[0].rstrip("AB")==ch]
    if not key: print("!! 라벨 없음:", stmt); continue
    info=labels[key[0]]; used.add(key[0])
    head=info["head"]
    # 머리의 괄호
    pm=re.match(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{[^}]+\}\}\s*(?:\(([^)]*(?:\([^)]*\))?[^)]*)\))?\s*\[", head)
    paren = pm.group(2) if pm else None
    hkind = pm.group(1) if pm else info["kind"]
    probs=[]
    if hkind!=kind: probs.append(f"종류: 표 {kind} / 머리 {hkind}")
    if paren is None: probs.append("머리에 괄호 이름 없음")
    else:
        parts=[p.strip() for p in paren.split(";")]
        hname=parts[0]; hrec="; ".join(parts[1:])
        if ourname!="—" and hname!=ourname: probs.append(f"이 글의 이름: 표 «{ourname}» / 머리 «{hname}»")
        # 기록 이름 비교(정규화)
        norm=lambda s: re.sub(r"\s+","",s.replace("\\",""))
        if norm(hrec)!=norm(recname): probs.append(f"기록 이름: 표 «{recname}» / 머리 «{hrec}»")
    if probs:
        print(f"- {kind} {ch}:{lab} ({info['file']} L{info['line']})"); [print("    ",p) for p in probs]
# 머리에 기록 이름이 있는데 표에 없는 진술
print("\n== 머리에 「기록 […]의」가 있으나 표에 없는 진술 ==")
for k,v in labels.items():
    if k in used or k[0]=="D": continue
    if "기록 [" in v["head"].split("[증명됨")[0].split(") [")[0] if ") [" in v["head"] else "기록 [" in v["head"][:200]:
        print(k, v["file"], v["head"][:160])
