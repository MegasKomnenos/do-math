# -*- coding: utf-8 -*-
"""두 끝 정리에서 모든 장의 진술 블록(머리~∎)을 따라 닿는 진술 집합을 구해, 11.3절이 「공유 입력 안에서 쓰인다」고 한 문헌 결과의 자리가 실제로 닿는지 본다."""
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
HEAD = re.compile(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?:[^}]+)\}\} [\(\[]")
PROOF = re.compile(r"\*\*(정리|명제|보조정리|따름정리) \{\{(\d+[AB]?:[^}]+)\}\}의 증명\.\*\*")
B={}
for f in sorted(glob.glob(root+"장*.md")):
    cur=None; buf=[]
    for l in open(f,encoding="utf-8"):
        if l.startswith("### "):
            if cur: B[cur]=B.get(cur,"")+"\n".join(buf); cur=None; buf=[]
            continue
        m=HEAD.match(l) or PROOF.match(l)
        if m:
            if cur: B[cur]=B.get(cur,"")+"\n".join(buf)
            cur=m.group(2); buf=[l]
        elif cur:
            buf.append(l)
            if "∎" in l: B[cur]=B.get(cur,"")+"\n".join(buf); cur=None; buf=[]
    if cur: B[cur]=B.get(cur,"")+"\n".join(buf)
def closure(start):
    seen=set(); st=[start]
    while st:
        x=st.pop()
        if x in seen or x not in B: continue
        seen.add(x)
        for lab in re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", B[x]):
            if lab in B and lab not in seen: st.append(lab)
    return seen
c1=closure("9:old-7-46"); c2=closure("10:old-8-37"); c=c1|c2
print("블록 수", len(B), "| 첫째 폐포", len(c1), "둘째", len(c2), "합", len(c))
for lab in ["7:old-6-6","7:factorial-moment","7:old-6-8","7:old-6-7","2:old-2-11","2:old-2-10","5:renewal-fkg","5:cut-rep","7:fourier-lemmas","6:geometric-mean","7:lemma-P-prime","4:correction-contour","8:explicit-bounds","4:borel-tail-arc","5:kernel-sandwich","5:old-5-12","6:lemma-O","7:X-cert","7:old-6-12","5:suff-cond","2:chain-expansion","3:old-3-6","6:tilt-sum","6:old-7-24","9:old-7-14","9:old-7-2","9:centroid-stop","10:old-8-15","9:old-7-1"]:
    print(f"{lab:22s} 첫째={lab in c1} 둘째={lab in c2}")
# who cites 7:old-6-6 / 7:old-6-8 / factorial-moment within blocks
for tgt in ["7:old-6-6","7:old-6-8","7:factorial-moment","7:old-6-7"]:
    print(tgt, "<-", sorted(k for k,v in B.items() if "{{"+tgt+"}}" in v and k!=tgt))
print("폐포 밖 7장 진술:", sorted(k for k in B if k.startswith("7:") and k not in c))
