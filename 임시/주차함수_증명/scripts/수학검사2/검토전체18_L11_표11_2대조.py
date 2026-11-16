# 11.2 표의 각 행과 부록 D 항목의 「독립 재계산」·「산술 등급」·머리 괄호 진술을 대조한다.
import re, glob, io, sys
root = r"C:\math\임시\주차함수_증명\장v2"
items = {}
for f in sorted(glob.glob(root + r"\부록D_장*.md")):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"(?m)^### D\.\{\{D:([^}]+)\}\}", txt)
    for i in range(1, len(parts), 2):
        lab = parts[i]; body = parts[i+1]
        head = body.split("\n",1)[0].strip()
        def line(name):
            m = re.search(r"(?m)^\*\*"+name+r"\.\*\*\s*(.*)$", body)
            return m.group(1).strip() if m else None
        items[lab] = dict(file=f.split("\\")[-1], head=head, grade=line("산술 등급"), indep=line("독립 재계산"), stmt=line("확인하는 진술"))
ch11 = open(root + r"\장11.md", encoding="utf-8").read()
rows = [l for l in ch11.splitlines() if l.startswith("| 부록 D.{{D:")]
out = io.StringIO()
seen = []
for r in rows:
    cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
    lab = re.match(r"부록 D\.\{\{D:([^}]+)\}\}", cells[0]).group(1)
    seen.append(lab)
    it = items.get(lab)
    out.write(f"\n===== {lab} ({it['file'] if it else 'MISSING'})\n")
    if not it:
        continue
    out.write(f"표 진술: {cells[1]}\n머리: {it['head']}\n")
    out.write(f"표 등급: {cells[2]}\nD 등급: {it['grade']}\n")
    out.write(f"표 자리: {cells[3]}\n")
    # 재계산 bracket and indep text
    m = re.match(r"〔(.*?)〕\s*(.*)$", it['indep'] or "")
    dbr, dtxt = (m.group(1), m.group(2)) if m else (None, it['indep'])
    tbr = cells[4].strip("〔〕")
    if dbr != tbr:
        out.write(f"!! 괄호 다름\n  표: {tbr}\n  D : {dbr}\n")
    else:
        out.write("괄호 같음\n")
    if dtxt != cells[5]:
        # show diff by words
        import difflib
        sm = difflib.SequenceMatcher(None, dtxt, cells[5])
        out.write("!! 서술 다름:\n")
        for op, a0,a1,b0,b1 in sm.get_opcodes():
            if op != "equal":
                out.write(f"  {op}: D[{dtxt[max(0,a0-30):a1+30]}] -> 표[{cells[5][max(0,b0-30):b1+30]}]\n")
    else:
        out.write("서술 같음\n")
out.write("\n===== 표에 없는 D 항목: " + ", ".join(l for l in items if l not in seen) + "\n")
out.write("===== 표 행 수: %d, D 항목 수: %d\n" % (len(rows), len(items)))
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_표11_2대조_out.txt","w",encoding="utf-8").write(out.getvalue())
print("done")
