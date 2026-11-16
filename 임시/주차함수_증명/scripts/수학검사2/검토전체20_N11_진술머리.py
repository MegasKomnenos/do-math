# -*- coding: utf-8 -*-
"""장 파일의 진술 머리를 모아 11.2·11.3·부록 C의 라벨·등급·인용을 대조한다."""
import re, glob, io, os, sys
ROOT = r"C:\math\임시\주차함수_증명"
OUT = os.path.join(ROOT, r"대조v2\수학검사2")
CH_ORDER = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10", "장11"]
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?|D):([^}]+)\}\}(.*?)\*\*", re.S)
LAB = re.compile(r"\{\{(\d+[AB]?):([^}]+)\}\}")
SEC = re.compile(r"^### (\d+\.\d+)")

stm = {}   # (ch,label) -> dict
chapter_text = {}
for ch in CH_ORDER:
    f = os.path.join(ROOT, "장v2", ch + ".md")
    lines = io.open(f, encoding="utf-8").read().split("\n")
    chapter_text[ch] = lines
    sec = None
    cur = None
    for i, ln in enumerate(lines):
        m = SEC.match(ln)
        if m:
            sec = m.group(1)
        h = HEAD.match(ln)
        if h:
            typ, chn, lab, rest = h.groups()
            cur = (chn, lab)
            if rest.strip().startswith("의 증명") and cur in stm:
                stm[cur]["body"].append(ln)
                continue
            br = re.search(r"\[([^\]]*)\]\.?\s*$", rest.strip())
            name = re.match(r"\s*\(([^)]*(?:\([^)]*\)[^)]*)*)\)", rest)
            stm[cur] = {"type": typ, "ch": ch, "sec": sec, "line": i + 1, "bracket": br.group(1) if br else None,
                        "name": name.group(1) if name else "", "head": rest.strip()[:400], "body": []}
        if cur:
            stm[cur]["body"].append(ln)
for k in stm:
    stm[k]["text"] = "\n".join(stm[k]["body"])

def grades_of(bracket):
    if bracket is None: return "(표지 없음)"
    return bracket

# ---------- 11.2: 확인하는 진술의 머리와 절
o = io.open(os.path.join(OUT, "_N11_112머리_out.txt"), "w", encoding="utf-8")
t11 = io.open(os.path.join(ROOT, r"장v2\장11.md"), encoding="utf-8").read().split("\n")
rows112 = [[c.strip() for c in ln.strip().strip("|").split(" | ")] for ln in t11 if ln.startswith("| 부록 D.{{D:")]
for r in rows112:
    print("\n==", r[0], "| 표 등급:", r[2], "| 표 절:", r[3], file=o)
    for chn, lab in LAB.findall(r[1]):
        s = stm.get((chn, lab))
        if not s:
            print("   !! 라벨 없음", chn, lab, file=o); continue
        print("   ", s["type"], lab, "| 절", s["sec"], "| [", s["bracket"], "]", file=o)
o.close()

# ---------- 11.3: 계산 진술과 산술 등급; 직접 인용
o = io.open(os.path.join(OUT, "_N11_113인용_out.txt"), "w", encoding="utf-8")
in113 = False
rows113 = []
for ln in t11:
    if ln.startswith("### 11.3"): in113 = True
    if ln.startswith("### 11.4"): in113 = False
    if in113 and ln.startswith("| ") and "{{" in ln:
        rows113.append([c.strip() for c in ln.strip().strip("|").split(" | ")])
print("11.3 행 수:", len(rows113), file=o)
for r in rows113:
    inputs = LAB.findall(r[0])
    print("\n====", r[0][:150], file=o)
    # 입력 진술의 머리
    for chn, lab in inputs:
        s = stm.get((chn, lab))
        if not s: print("   !! 입력 라벨 없음", chn, lab, file=o); continue
        print("   입력:", s["type"], chn, lab, "| 절", s["sec"], "| [", s["bracket"], "]", file=o)
    # 계산 진술 열
    print("   -- 계산 진술 열:", r[1][:300], file=o)
    for chn, lab in LAB.findall(r[1]):
        s = stm.get((chn, lab))
        if not s: print("   !! 계산 라벨 없음", chn, lab, file=o); continue
        print("      계산:", s["type"], chn, lab, "| [", s["bracket"], "]", file=o)
    # 직접 인용 열들
    for col in r[2:]:
        print("   -- 인용 열:", col[:200], file=o)
        for chn, lab in LAB.findall(col):
            s = stm.get((chn, lab))
            if not s: print("      !! 라벨 없음", chn, lab, file=o); continue
            if (chn, lab) in inputs: continue
            found = [l2 for c2, l2 in inputs if ("{{%s:%s}}" % (c2, l2)) in s["text"]]
            missing = [l2 for c2, l2 in inputs if ("{{%s:%s}}" % (c2, l2)) not in s["text"]]
            print("      인용자", s["type"], chn, lab, "(절", s["sec"], ") 블록에 있는 입력:", found, " 없는 입력:", missing, file=o)
o.close()

# ---------- 부록 C 둘째 표: 라벨 존재와 기록 이름이 머리에 있는지
o = io.open(os.path.join(OUT, "_N11_부록C이름_out.txt"), "w", encoding="utf-8")
for ln in io.open(os.path.join(ROOT, r"장v2\부록C.md"), encoding="utf-8"):
    if ln.startswith("| 기록 ["):
        c = [x.strip() for x in ln.strip().strip("|").split(" | ")]
        labs = LAB.findall(c[1])
        if not labs: print("!! 라벨 없음:", ln[:100], file=o); continue
        chn, lab = labs[0]
        s = stm.get((chn, lab))
        if not s: print("!! 진술 없음:", chn, lab, "|", c[0], file=o); continue
        typ_in_C = c[1].split(" ")[0]
        flag = ""
        if typ_in_C != s["type"]: flag += " [유형 다름: 글=%s]" % s["type"]
        # 이 글의 이름과 머리 괄호의 이름
        name_head = s["name"].split(";")[0].strip()
        if c[2].strip() != name_head: flag += " [이름: 머리=%s]" % name_head
        # 기록의 이름: 머리 괄호에 '기록 [r…]의 …' 부분
        rec_part = s["name"].split(";", 1)[1].strip() if ";" in s["name"] else ""
        cname = c[0]
        if rec_part.replace(" ", "") != cname.replace(" ", ""):
            flag += " [기록이름: 머리=%s]" % rec_part
        if flag: print(chn, lab, "|", cname, "|", c[1], "|", c[2], flag, file=o)
o.close()

# ---------- 진술 목록 덤프(절·표지)
o = io.open(os.path.join(OUT, "_N11_진술목록_out.txt"), "w", encoding="utf-8")
for k, s in stm.items():
    print(s["ch"], s["sec"], s["type"], k[1], "| (", s["name"][:120], ") [", s["bracket"], "]", file=o)
o.close()
