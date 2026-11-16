# H14: 장부 3절 낱말 사전의 「첫 정의 절」을 장 파일의 첫 출현 절과 견준다(자리 찾기용).
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
sec_re = re.compile(r"^(#+)\s+(\d+(?:\.\d+)*)\b")
# 장 본문을 (절, 행, 텍스트)로 펼친다
seq = []
for f in files:
    cur = None
    for ln, line in enumerate(open(os.path.join(root, "장v2", f), encoding="utf-8"), 1):
        m = sec_re.match(line)
        if m:
            s = m.group(2); parts = s.split(".")
            cur = ".".join(parts[:2]) if len(parts) >= 2 else parts[0]
            continue
        seq.append((cur, f, ln, line))
def sec_key(s):
    try:
        a, b = s.split("."); return (int(a), int(b))
    except Exception:
        return (99, 99)
# 3절 표 파싱
lines = open(os.path.join(root, "장부_v2.md"), encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("## 3. 낱말 사전"))
end = next(i for i, l in enumerate(lines) if l.startswith("## 4. "))
rows = [l for l in lines[start:end] if l.startswith("| ") and not l.startswith("| 낱말") and not l.startswith("|---")]
print("3절 행", len(rows))
for r in rows:
    cells = [c.strip() for c in r.strip().strip("|").split("|")]
    if len(cells) < 3: continue
    words_cell, claim = cells[0], cells[2]
    claims = re.findall(r"\d+\.\d+|\d+(?=\()|부록 D|일반어", claim)
    # 낱말 분해(쉼표·가운뎃점); 수식 낱말은 건너뜀
    words = [w.strip() for w in re.split(r",\s*|·", words_cell) if w.strip()]
    words = [re.sub(r"\(.*?\)", "", w).strip() for w in words]
    words = [w for w in words if w and "$" not in w and len(w) >= 2]
    if not words or not claims: continue
    first_claim = min((sec_key(c) for c in claims if re.match(r"\d+\.\d+", c)), default=None)
    for w in words:
        hit = None
        for cur, f, ln, line in seq:
            if w in line:
                hit = (cur, f, ln); break
        if hit is None:
            print(f"[없음] {w!r} (주장 {claim})")
            continue
        if first_claim and hit[0] and sec_key(hit[0]) < first_claim and hit[0] not in ("1.4", "1.5"):
            print(f"[앞섬] {w!r}: 주장 {claim}, 첫 출현 {hit[0]} {hit[1]}:{hit[2]}")
