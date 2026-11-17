# 부록 C 「기록이 결과에 붙인 이름과 이 글의 번호」 표를 진술 머리와 맞춘다.
import re,glob
heads={}
for f in glob.glob("장v2/장*.md"):
    for i,l in enumerate(open(f,encoding="utf-8").read().split("\n")):
        m=re.match(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}(?: \((.*?)\))? \[",l)
        if m: heads[m.group(2)]=(m.group(1),m.group(3) or "",f,i+1,l[:300])
C=open("장v2/부록C.md",encoding="utf-8").read().split("\n")
inside=False
for l in C:
    if l.startswith("### 기록이 결과에"): inside=True; continue
    if l.startswith("### ") and inside: break
    if not inside or not l.startswith("| 기록"): continue
    cells=[x.strip() for x in l.strip().strip("|").split(" | ")]
    recname,stmt,name=cells
    m=re.match(r"(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}",stmt)
    if not m: print("PARSE",l[:100]); continue
    kind,lab=m.groups()
    if lab not in heads: print("NOHEAD",lab); continue
    hk,paren,f,ln,hl=heads[lab]
    issues=[]
    if hk!=kind: issues.append(f"종류 {kind}≠{hk}")
    # title = part before ';'
    title=paren.split(";")[0].strip()
    if title!=name: issues.append(f"이름 '{name}'≠'{title}'")
    rn=paren.split(";",1)[1].strip() if ";" in paren else ""
    if rn!=recname: issues.append(f"기록이름 '{recname}' ≠ '{rn}'")
    if issues: print(lab,f,ln,"|"," ; ".join(issues))
print("done")
