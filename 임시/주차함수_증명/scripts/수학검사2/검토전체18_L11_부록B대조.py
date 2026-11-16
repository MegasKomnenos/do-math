# 부록 B의 식별자 목록을 본문·부록이 쓴 식별자, 기록 폴더의 존재, 제목과 대조한다.
import re, glob, os, io, json
root = r"C:\math\임시\주차함수_증명\장v2"
recs = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
B = open(root+r"\부록B.md", encoding="utf-8").read()
brows = {}
for l in B.splitlines():
    if l.startswith("| r"):
        c=[x.strip() for x in l.strip().strip("|").split("|")]
        brows[c[0]] = (c[1], c[2], c[3].strip("`"))
used = {}
for f in sorted(glob.glob(root+r"\*.md")):
    if f.endswith("부록B.md"): continue
    txt=open(f,encoding="utf-8").read()
    for m in re.finditer(r"\br([0-9a-f]{7})\b", txt):
        used.setdefault("r"+m.group(1), set()).add(f.split("\\")[-1])
out=io.StringIO()
out.write("== 본문·부록이 쓰지만 B에 없는 식별자\n")
for k in sorted(used):
    if k not in brows: out.write(f"  {k}: {sorted(used[k])}\n")
out.write("== B에 있지만 본문·부록이 쓰지 않는 식별자\n")
for k in brows:
    if k not in used: out.write(f"  {k}\n")
out.write("== 폴더 존재·제목 대조\n")
dirs = os.listdir(recs)
for k,(t,title,folder) in brows.items():
    ex = folder in dirs
    pre = [d for d in dirs if d.startswith(k)]
    note=""
    if ex:
        # title from record.json or exposition.md first heading
        rj = os.path.join(recs, folder, "record.json")
        rt=None
        if os.path.exists(rj):
            try:
                j=json.load(open(rj,encoding="utf-8"))
                rt = j.get("title") or j.get("제목")
            except Exception as e: rt=f"(json err {e})"
        if rt is None:
            ex_md=os.path.join(recs,folder,"exposition.md")
            if os.path.exists(ex_md):
                for l in open(ex_md,encoding="utf-8"):
                    if l.startswith("#"): rt=l.strip("# \n"); break
        # time
        tm=None
        if os.path.exists(rj):
            try:
                j=json.load(open(rj,encoding="utf-8"))
                for key in ("created","created_at","time","timestamp","date"):
                    if key in j: tm=j[key]; break
            except: pass
        same = (rt or "").replace(" ","")==title.replace(" ","")
        note = f"제목{'같음' if same else '다름'}; 기록제목={rt!r}; 시각={tm!r}"
    out.write(f"  {k} {'있음' if ex else '없음 '+str(pre)} B시각={t} {note}\n")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_부록B대조_out.txt","w",encoding="utf-8").write(out.getvalue())
print(out.getvalue()[:6000])
