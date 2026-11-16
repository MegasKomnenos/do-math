# 11.3 표의 입력 라벨마다, 9장·10장·7B의 어느 진술(머리~다음 머리)과 어느 절 산문이 그 라벨을 인용하는지 모은다.
import re, io, json
root = r"C:\math\임시\주차함수_증명\장v2"
head_re = re.compile(r"^\*\*(정리|보조정리|명제|따름정리|정의|관찰|추측|문제)\s+\{\{(\d+[AB]?):([^}]+)\}\}")
sec_re = re.compile(r"^###\s+(\d+\.\d+)")
def scan(fname):
    cur = ("(절 산문)", None); sec=None; blocks = {}
    for i,l in enumerate(open(root+"\\"+fname, encoding="utf-8"),1):
        m = sec_re.match(l)
        if m: sec = m.group(1); cur = (f"{sec}절 산문", None)
        m = head_re.match(l)
        if m: cur = (f"{m.group(1)} {{{{{m.group(2)}:{m.group(3)}}}}}", i)
        for ch, lab in re.findall(r"\{\{(\d+[AB]?):([^}]+)\}\}", l):
            blocks.setdefault(f"{ch}:{lab}", set()).add(f"{cur[0]}@{fname}:{i}")
    return blocks
cites = {}
for f in ["장9.md","장10.md","장7B.md","장8.md","장6.md","장5B.md"]:
    for k,v in scan(f).items(): cites.setdefault(k,set()).update(v)
ch11 = open(root+r"\장11.md", encoding="utf-8").read().splitlines()
out = io.StringIO()
in_tab = False
for l in ch11:
    if l.startswith("| 입력 |"): in_tab = True; continue
    if in_tab and not l.startswith("|"): in_tab = False; continue
    if not in_tab or l.startswith("|---"): continue
    cells = [c.strip() for c in l.strip().strip("|").split(" | ")]
    labs = re.findall(r"\{\{(\d+[AB]?):([^}]+)\}\}", cells[0])
    out.write(f"\n##### 행: {cells[0][:120]}\n")
    for ch, lab in labs:
        key=f"{ch}:{lab}"
        c = sorted(x for x in cites.get(key, []) if x.split("@")[1].startswith(("장9","장10","장7B")))
        # 7B: only old-6-22 proof matters, but list all with 7B marker
        out.write(f"  [{key}] 인용 자리:\n")
        for x in c: out.write(f"     {x}\n")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_인용지도_out.txt","w",encoding="utf-8").write(out.getvalue())
print(len(out.getvalue().splitlines()))
