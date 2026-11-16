# 부록 A·C가 인용한 라벨이 정의되어 있는지, 부록 C 둘째 표의 「이 글의 이름」이 진술 머리의 이름과 맞는지 본다.
import re, json, glob, io
root = r"C:\math\임시\주차함수_증명\장v2"
defs = json.load(open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_라벨지도.json", encoding="utf-8"))
# 머리의 이름: **정리 {{..}} (이름; ...)** 에서 이름 추출
names = {}
head_re = re.compile(r"^\*\*(정리|보조정리|명제|따름정리|정의|관찰)\s+\{\{(\d+[AB]?):([^}]+)\}\}\s*(?:\(([^;)]*)[;)])?")
for f in glob.glob(root+r"\장*.md"):
    for l in open(f,encoding="utf-8"):
        m = head_re.match(l)
        if m:
            key=f"{m.group(2)}:{m.group(3)}"
            if key not in names and m.group(4): names[key]=(m.group(1), m.group(4).strip())
out=io.StringIO()
for ap in ["부록A.md","부록C.md"]:
    txt=open(root+"\\"+ap,encoding="utf-8").read()
    out.write(f"== {ap}: 정의 없는 라벨\n")
    for kind,ch,lab in set(re.findall(r"(정리|보조정리|명제|따름정리|정의)?\s*\{\{(\d+[AB]?):([^}]+)\}\}", txt)):
        key=f"{ch}:{lab}"
        if key not in defs: out.write(f"  {kind} {key}\n")
        elif kind and defs[key][0][0]!=kind: out.write(f"  종류 다름: {ap} {kind} {key} / 정의 {defs[key][0][0]}\n")
C=open(root+r"\부록C.md",encoding="utf-8").read().splitlines()
out.write("== 부록 C 둘째 표: 이름 대조\n")
sec=None
for l in C:
    if l.startswith("### "): sec=l
    if sec and "기록이 결과에 붙인 이름" in sec and l.startswith("| ") and not l.startswith("| 기록의 이름"):
        c=[x.strip() for x in l.strip().strip("|").split("|")]
        if len(c)<3: continue
        labs=re.findall(r"(정리|보조정리|명제|따름정리|정의)\s+\{\{(\d+[AB]?):([^}]+)\}\}", c[1])
        for kind,ch,lab in labs:
            key=f"{ch}:{lab}"
            nm=names.get(key)
            if nm is None: out.write(f"  이름 없음(머리에 괄호 이름 없음): {key} | C: {c[2]}\n"); continue
            if nm[1].replace(" ","")!=c[2].replace(" ",""):
                out.write(f"  이름 다름: {key} | 머리: {nm[1]} | C: {c[2]}\n")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_부록AC라벨_out.txt","w",encoding="utf-8").write(out.getvalue())
print(out.getvalue())
