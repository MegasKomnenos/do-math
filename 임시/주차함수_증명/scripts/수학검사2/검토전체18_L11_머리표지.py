# 11.2·11.3 표가 적은 계산 진술의 머리 표지(지위·덧붙임·의존)를 모아 표의 산술 등급과 견준다.
import re, glob, io
root = r"C:\math\임시\주차함수_증명\장v2"
heads = {}
for f in glob.glob(root+r"\장*.md"):
    for i,l in enumerate(open(f,encoding="utf-8"),1):
        m = re.match(r"^\*\*(정리|보조정리|명제|따름정리|정의)\s+\{\{(\d+[AB]?):([^}]+)\}\}(.*?)\*\*", l)
        if m:
            key=f"{m.group(2)}:{m.group(3)}"
            if key not in heads: heads[key]=(f.split("\\")[-1], i, m.group(4).strip())
ch11=open(root+r"\장11.md",encoding="utf-8").read().splitlines()
out=io.StringIO()
out.write("##### 11.2 표: 확인하는 진술의 머리\n")
for l in ch11:
    if l.startswith("| 부록 D.{{D:"):
        c=[x.strip() for x in l.strip().strip("|").split(" | ")]
        out.write(f"\n== {c[0][8:50]} | 표 등급: {c[2]}\n")
        for ch,lab in re.findall(r"\{\{(\d+[AB]?):([^}]+)\}\}", c[1]):
            h=heads.get(f"{ch}:{lab}")
            out.write(f"   {ch}:{lab} @{h[0]}:{h[1]}  {h[2][:400]}\n" if h else f"   {ch}:{lab} 없음\n")
out.write("\n##### 11.3 표: 계산 진술 열의 머리\n")
in_tab=False
for l in ch11:
    if l.startswith("| 입력 |"): in_tab=True; continue
    if in_tab and not l.startswith("|"): in_tab=False; continue
    if not in_tab or l.startswith("|---"): continue
    c=[x.strip() for x in l.strip().strip("|").split(" | ")]
    if c[1]=="없음": continue
    out.write(f"\n== {c[0][:60]}\n   열: {c[1][:600]}\n")
    for ch,lab in re.findall(r"\{\{(\d+[AB]?):([^}]+)\}\}", c[1]):
        if ch=="D": continue
        h=heads.get(f"{ch}:{lab}")
        out.write(f"   {ch}:{lab} @{h[0]}:{h[1]}  {h[2][:400]}\n" if h else f"   {ch}:{lab} 없음\n")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_머리표지_out.txt","w",encoding="utf-8").write(out.getvalue())
print(len(out.getvalue().splitlines()))
