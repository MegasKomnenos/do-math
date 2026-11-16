# 11.4 표의 「쓰인 자리」 대조: 낱말마다 본문에서 나오는 자리를 진술 라벨 또는 절로 돌려 적는다.
import re, glob, io
root = r"C:\math\임시\주차함수_증명\장v2"
head_re = re.compile(r"^\*\*(정리|보조정리|명제|따름정리|정의)\s+\{\{(\d+[AB]?):([^}]+)\}\}")
sec_re = re.compile(r"^###+\s+(\d+\.\d+(\.\d+)?)")
dsec_re = re.compile(r"^### D\.\{\{D:([^}]+)\}\}")
keys = {"Robbins":["Robbins"], "지수 공식":["지수 공식"], "Cayley":["Cayley"], "Lagrange":["Lagrange"], "Jensen":["Jensen"],
        "Wallis":["Wallis"], "Euler–Maclaurin":["Euler–Maclaurin","Euler-Maclaurin"], "Euler 합":["Euler 합"], "Harris":["Harris"],
        "Faà":["Faà"], "FKG":["FKG"], "편각":["편각 원리"], "Cauchy 적분/부등식":["Cauchy의 적분","Cauchy 적분","Cauchy 부등식","Cauchy의 부등식"],
        "부분분수":["부분분수"], "coth":["coth"], "임계값 T(1/e)":["T(1/e)","임계값"], "Lambert":["Lambert"], "갈고리":["갈고리"],
        "Borel–Tanner":["Borel–Tanner"], "Ibragimov":["Ibragimov"], "Janson":["Janson"], "Petersson":["Petersson"], "Konheim":["Konheim"],
        "Foata":["Foata","Pollak"], "Celano":["Celano"], "Aguilar":["Aguilar"], "Knuth":["Knuth"], "Flajolet":["Flajolet"], "Ahlfors":["Ahlfors"],
        "Graham":["Graham"], "Comtet":["Comtet"], "Apostol":["Apostol"], "Titchmarsh":["Titchmarsh"], "Grimmett":["Grimmett"], "Tanner":["Tanner, 1953","Tanner,"], "Corless":["Corless"], "Stanley":["Stanley"]}
out = io.StringIO()
files = sorted(glob.glob(root+r"\장*.md")) + sorted(glob.glob(root+r"\부록D_*.md"))
hits = {k:[] for k in keys}
for f in files:
    cur="(머리말)"; sec=None
    fname=f.split("\\")[-1]
    if fname=="장11.md": continue
    for i,l in enumerate(open(f,encoding="utf-8"),1):
        m=sec_re.match(l)
        if m: sec=m.group(1); cur=f"{sec}절"
        m=dsec_re.match(l)
        if m: cur=f"D.{m.group(1)}"
        m=head_re.match(l)
        if m: cur=f"{m.group(1)} {m.group(2)}:{m.group(3)}"
        for k,pats in keys.items():
            if any(p in l for p in pats):
                hits[k].append(f"{cur}@{fname}:{i}")
for k,v in hits.items():
    out.write(f"\n== {k}\n")
    seen=[]
    for x in v:
        tag=x.split("@")[0]
        if tag not in seen: seen.append(tag); out.write(f"   {x}\n")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_문헌자리_out.txt","w",encoding="utf-8").write(out.getvalue())
print(out.getvalue())
