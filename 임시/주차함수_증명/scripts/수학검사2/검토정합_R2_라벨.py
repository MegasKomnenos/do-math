# -*- coding: utf-8 -*-
"""R2 (ㄱ)(ㄴ): 장부 1.3·3절 행이 인용하는 라벨 {{…}}이 장 파일의 진술 머리에 있는지, 머리가 있는 절이 행의 「자리」 절과 맞는지 본다(읽기 전용)."""
import io, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
ORDER = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
heads = {}  # label -> (ch, line, sec)
for ch in ORDER:
    sec = None
    for i, ln in enumerate(io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n"), 1):
        m = re.match(r"^### (\d+\.\d+)", ln)
        if m: sec = m.group(1)
        if ln.startswith("**"):
            for lab in re.findall(r"\{\{([^}]+)\}\}", ln.split("**")[1] if ln.count("**") >= 2 else ln):
                heads.setdefault(lab, (ch, i, sec))
L = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read().split("\n")
out = io.StringIO()
def check(a, b, name, seccol):
    out.write(f"==== {name}\n")
    for n in range(a-1, b):
        ln = L[n]
        if not ln.startswith("|") or ln.startswith("|---"): continue
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        labs = re.findall(r"\{\{([^}]+)\}\}", ln)
        if not labs: continue
        decl = set(re.findall(r"\d+\.\d+", cells[seccol])) if len(cells) > seccol else set()
        for lab in dict.fromkeys(labs):
            if lab not in heads:
                out.write(f"[{n+1}] 라벨 없음: {{{{{lab}}}}}  (행 글자: {cells[0][:60]})\n"); continue
            ch, i, sec = heads[lab]
            if decl and sec not in decl and not any(d.startswith(sec + ".") for d in decl):
                out.write(f"[{n+1}] 절 어긋남: {{{{{lab}}}}} 머리는 {ch}:{i} ({sec}절), 행의 자리 {sorted(decl)}  (행 글자: {cells[0][:60]})\n")
check(341, 416, "1.3 국소 기호", 2)
check(503, 706, "3절 낱말 사전", 2)
sys.stdout.buffer.write(out.getvalue().encode("utf-8"))
