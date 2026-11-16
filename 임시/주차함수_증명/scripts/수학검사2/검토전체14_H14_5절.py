# H14: 장부 5절(장별 배정·여유 글자)을 1.2(정의 절·쓰이는 장·바탕 글자·글자체)와 견준다.
import re, os
root = r"C:\math\임시\주차함수_증명"
lines = open(os.path.join(root, "장부_v2.md"), encoding="utf-8").read().split("\n")
def section(start_pat, end_pat):
    s = next(i for i, l in enumerate(lines) if l.startswith(start_pat))
    e = next(i for i, l in enumerate(lines) if i > s and l.startswith(end_pat))
    return lines[s:e]
# 1.2 행
rows12 = [l for l in section("### 1.2", "### 1.3") if l.startswith("| $") or l.startswith("| (")]
glob = []
for l in rows12:
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if len(c) < 7: continue
    glyph, base, meaning, defsec, used = c[0], c[1], c[2], c[3], c[4]
    chs = set()
    if "전 장" in used: chs = set(range(1, 12))
    else:
        for m in re.finditer(r"\b(\d+)\b", used): chs.add(int(m.group(1)))
    defchs = set(int(m.group(1)) for m in re.finditer(r"(\d+)\.\d+", defsec))
    glob.append(dict(glyph=glyph, base=base, defsec=defsec, defchs=defchs, used=chs))
# 바탕 글자·글자체 → 여유 토큰
def tokens(base):
    out = set()
    for part in base.split(";"):
        m = re.match(r"\s*(\\?[A-Za-z]+(?:_d)?)·(.+)", part.strip())
        if not m: continue
        letter, style = m.group(1), m.group(2)
        if "로마체" in style or "칠판체" in style or "꼬리표" in style: continue
        if "일반" in style:
            out.add("$" + letter + "$")
        elif "필기체" in style: out.add("$\\mathcal " + letter + "$")
        elif "프락투어" in style: out.add("$\\mathfrak " + letter + "$")
        elif "산세리프" in style: out.add("$\\mathsf " + letter + "$")
    return out
var_tokens = {"$n$","$m$","$t$","$N$","$k$","$\\ell$","$y$","$Y$","$i$","$j$","$u$","$v$","$r$","$\\nu$","$d$","$q$"}
reserved = {"$a$","$b$","$c$","$e$","$h$","$\\delta$","$\\Delta$","$\\Sigma$","$l$","$o$","$O$","$\\varpi$","$P$","$Q$","$W$","$X$"}
ch1 = set()
for g in glob:
    if 1 in g["defchs"]: ch1 |= tokens(g["base"])
# 5절 행
rows5 = [l for l in section("## 5. ", "## 6. ") if re.match(r"\| \d+ \|", l)]
for l in rows5:
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    ch = int(c[0]); defined, words, spare = c[1], c[2], c[3]
    # (a) 처음 정의하는 전역 기호 대 1.2 정의 절
    exp = [g["glyph"] for g in glob if ch in g["defchs"]]
    listed = [x.strip() for x in defined.split(";")]
    def norm(s): return re.sub(r"\s", "", s)
    exp_n = {norm(x) for x in exp}; listed_n = {norm(x) for x in listed}
    only12 = sorted(exp_n - listed_n); only5 = sorted(listed_n - exp_n)
    if only12 or only5:
        print(f"[장 {ch}] 1.2에만(정의 절이 {ch}장): {only12}")
        print(f"[장 {ch}] 5절에만: {only5}")
    # (b) 여유 글자 충돌
    spare_tokens = set(re.findall(r"\$[^$]+\$", spare))
    forb = set(var_tokens) | reserved | ch1
    for g in glob:
        if ch in g["used"] or ch in g["defchs"]: forb |= tokens(g["base"])
    clash = sorted(spare_tokens & forb)
    if clash: print(f"[장 {ch}] 여유 글자인데 그 장의 전역·1장 전역·변수·예약과 겹침: {clash}")
    # (c) 여유에 없는데 쓸 수 있는 글자(참고): 생략
print("끝")
