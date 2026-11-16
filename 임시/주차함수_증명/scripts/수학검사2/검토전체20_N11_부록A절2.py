# -*- coding: utf-8 -*-
"""부록 A의 기호가 「처음 정의된 절」로 적힌 절 안에 실제로 나타나는지 본다(고정 문자열, 철자 변형 포함)."""
import re, io, os
ROOT = r"C:\math\임시\주차함수_증명"
OUT = os.path.join(ROOT, r"대조v2\수학검사2\_N11_부록A절2_out.txt")
CH = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10"]
SEC = re.compile(r"^### (\d+\.\d+)")
sections = {}
order = []
for ch in CH:
    sec = ch + "-머리"
    for ln in io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n"):
        m = SEC.match(ln)
        if m:
            sec = m.group(1)
        if sec not in sections:
            sections[sec] = []; order.append(sec)
        sections[sec].append(ln)
for s in sections: sections[s] = "\n".join(sections[s])

def split_top(s):
    out, depth, cur = [], 0, ""
    for chh in s:
        if chh in "{(": depth += 1
        if chh in "})": depth -= 1
        if chh == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += chh
    out.append(cur)
    return [x.strip() for x in out if x.strip()]

def variants(tok):
    v = {tok}
    t = tok.split(":=")[0].strip()
    v.add(t)
    v.add(re.sub(r"\^\{([A-Za-z])\}", r"^\1", t))
    v.add(re.sub(r"_\{([A-Za-z>])\}", r"_\1", t))
    v.add(t.replace("^\\prime", "'").replace("\\prime", "'"))
    v.add(re.sub(r"\([^()]*\)$", "", t).strip())   # 인수 제거
    v.add(re.sub(r"\^\{([A-Za-z])\}", r"^\1", re.sub(r"\([^()]*\)$", "", t)).strip())
    v.add(t.replace("\\mathrm ", "\\mathrm{").replace("$", ""))
    return {x for x in v if len(x) >= 2}

o = io.open(OUT, "w", encoding="utf-8")
n_flag = 0
for ln in io.open(os.path.join(ROOT, r"장v2\부록A.md"), encoding="utf-8"):
    if not ln.startswith("| $"): continue
    c = [x.strip() for x in ln.strip().strip("|").split(" | ")]
    syms = []
    for m in re.findall(r"\$([^$]+)\$", c[0]):
        syms += split_top(m)
    claimed = re.findall(r"\d+\.\d+", c[2])
    report = []
    for s in syms:
        vs = variants(s)
        in_claimed = [sec for sec in claimed if sec in sections and any(v in sections[sec] for v in vs)]
        first = None
        for sec in order:
            if any(v in sections[sec] for v in vs):
                first = sec; break
        if not in_claimed:
            report.append((s, "주장 절에 없음", "첫 출현=" + str(first)))
    if report:
        n_flag += 1
        print(c[0][:70], "| 주장:", c[2], "|", report, file=o)
print("\n플래그 행 수:", n_flag, file=o)
o.close()
