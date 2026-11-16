# H14: 장부 7절(기록 글자 대응)의 기록 집합을 부록 B·본문·부록 D·1.2와 견준다.
import re, os, glob
root = r"C:\math\임시\주차함수_증명"
lines = open(os.path.join(root, "장부_v2.md"), encoding="utf-8").read().split("\n")
def section(start_pat, end_pat):
    s = next(i for i, l in enumerate(lines) if l.startswith(start_pat))
    e = next((i for i, l in enumerate(lines) if i > s and l.startswith(end_pat)), len(lines))
    return lines[s:e]
rid = re.compile(r"\[(r[0-9a-f]{7})\]")
sec7 = section("## 7. ", "## 8. ")
rows7 = [l for l in sec7 if l.startswith("| $") or l.startswith("| (") or l.startswith("| \\")]
ids7 = set(); glyphs7 = []
for l in rows7:
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if len(c) < 4: continue
    glyphs7.append(c[0]); ids7 |= set(rid.findall(c[1]))
    if not c[3].strip(): print("이동 열 비어 있음:", c[0][:60])
print("7절 행", len(rows7), "7절 기록 집합", len(ids7))
# 부록 B
B = open(os.path.join(root, "장v2", "부록B.md"), encoding="utf-8").read()
idsB = set(re.findall(r"\b(r[0-9a-f]{7})\b", B))
print("부록 B 기록", len(idsB))
# 본문·부록 D 인용
body = ""
for f in sorted(glob.glob(os.path.join(root, "장v2", "*.md"))):
    b = os.path.basename(f)
    if b.startswith("장") or b.startswith("부록D"):
        body += open(f, encoding="utf-8").read()
idsBody = set(re.findall(r"\b(r[0-9a-f]{7})\b", body))
print("본문·부록 D 인용 기록", len(idsBody))
print("부록 B에 있으나 본문·D에 없음:", sorted(idsB - idsBody))
print("본문·D에 있으나 부록 B에 없음:", sorted(idsBody - idsB))
print("7절에 없는 부록 B 기록:", sorted(idsB - ids7))
print("부록 B에 없는 7절 기록:", sorted(ids7 - idsB))
# 1.2의 기록 글자 열
sec12 = [l for l in section("### 1.2", "### 1.3") if l.startswith("| $") or l.startswith("| (")]
ids12 = set()
for l in sec12:
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if len(c) >= 7: ids12 |= set(rid.findall(c[6]))
print("1.2 기록 글자 열의 기록 집합", len(ids12))
print("7절에만:", sorted(ids7 - ids12))
print("1.2에만:", sorted(ids12 - ids7))
# 7절 글자가 1.2에 있는가(바탕 문자열의 느슨한 비교)
glyph12 = " ".join(l.split("|")[1] for l in sec12)
def norm(s): return re.sub(r"\s", "", s)
g12n = norm(glyph12)
miss = []
for g in glyphs7:
    parts = [p.strip() for p in re.split(r",\s*(?=\$)", g)]
    for p in parts:
        core = re.sub(r"\(.*?\)$", "", norm(p)).strip("$")
        core = core.split("(")[0]
        if core and core not in g12n: miss.append(p)
print("1.2에서 바로 찾지 못한 7절 글자(느슨한 비교):", miss[:40], "…총", len(miss))
