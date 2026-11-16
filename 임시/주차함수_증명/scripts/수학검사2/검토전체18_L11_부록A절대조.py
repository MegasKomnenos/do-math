# 부록 A의 각 행: 기호 문자열이 「처음 정의된 절」의 장 파일(그리고 그 절)에 나타나는지 거칠게 본다.
import re, io
root = r"C:\math\임시\주차함수_증명\장v2"
chap_files = {"1":["장1.md"],"2":["장2.md"],"3":["장3.md"],"4":["장4.md"],"5":["장5A.md","장5B.md"],"6":["장6.md"],"7":["장7A.md","장7B.md"],"8":["장8.md"],"9":["장9.md"],"10":["장10.md"]}
BS = chr(92)
def norm(s): return re.sub(r"\s+", "", s).replace(BS+"prime", "'")
sections = {}; texts = {}
for ch, fs in chap_files.items():
    for f in fs:
        txt = open(root + BS + f, encoding="utf-8").read()
        texts[ch] = texts.get(ch, "") + txt
        cur = None
        for l in txt.splitlines():
            m = re.match(r"^###+\s+(\d+\.\d+)", l)
            if m: cur = m.group(1)
            if cur: sections[cur] = sections.get(cur, "") + l + "\n"
A = open(root + BS + "부록A.md", encoding="utf-8").read().splitlines()
out = io.StringIO()
splitter = re.compile(":=|=|" + BS + BS + "in|" + BS + BS + "ge|>|<")
for l in A:
    if not l.startswith("| $"): continue
    c = [x.strip() for x in l.strip().strip("|").split(" | ")]
    if len(c) < 3: continue
    syms = [s.strip() for s in re.findall(r"\$([^$]+)\$", c[0])]
    secs = re.findall(r"\d+\.\d+", c[2])
    if not secs: continue
    sec = secs[0]; ch = sec.split(".")[0]
    parts = []
    for s in syms:
        depth = 0; cur = ""
        for ch_ in s:
            if ch_ in "{(": depth += 1
            if ch_ in "})": depth -= 1
            if ch_ == "," and depth == 0: parts.append(cur); cur = ""
            else: cur += ch_
        parts.append(cur)
    parts = [norm(p) for p in parts if p.strip()]
    cores = [splitter.split(p)[0] for p in parts]
    chtxt = norm(texts.get(ch, "")); sectxt = norm(sections.get(sec, ""))
    miss_ch = [p for p in cores if p and p not in chtxt]
    miss_sec = [p for p in cores if p and p not in sectxt and p not in miss_ch]
    if miss_ch or miss_sec:
        out.write(f"{c[0][:60]:60s} 절 {c[2][:28]:28s} 장에없음:{miss_ch} 절에없음:{miss_sec}\n")
open(root.replace("장v2", "scripts" + BS + "수학검사2") + BS + "검토전체18_L11_부록A절대조_out.txt", "w", encoding="utf-8").write(out.getvalue())
print(out.getvalue())
