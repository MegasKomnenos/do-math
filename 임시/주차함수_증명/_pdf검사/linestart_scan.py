"""시각 줄 단위 검사: 줄 머리가 구두점이거나, 앞 줄이 수식으로 끝나고 이 줄이 한글 조사로 시작하는 곳을 찾는다."""
import sys, collections, pymupdf as fitz
doc = fitz.open(sys.argv[1])
PUNCT = set(",.;:)]」』?!")
JOSA = ("은","는","이","가","을","를","의","에","와","과","로","도","다","이고","이다","에서","으로","라","까지","부터","처럼","보다","마다","이면","면","인")
hits = collections.defaultdict(list)
for pno in range(doc.page_count):
    d = doc[pno].get_text("rawdict")
    rows = []  # (y, x, char, font)
    for b in d["blocks"]:
        if b["type"] != 0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                for c in s["chars"]:
                    if c["c"].strip():
                        rows.append((round(c["origin"][1]), c["origin"][0], c["c"], s["font"]))
    # group by baseline (within 3pt)
    rows.sort()
    lines = []
    for r in rows:
        if lines and abs(lines[-1][0] - r[0]) <= 3: lines[-1][1].append(r)
        else: lines.append([r[0], [r]])
    prev_math_end = False
    for y, chars in lines:
        chars.sort(key=lambda t: t[1])
        first = chars[0]; last = chars[-1]
        if y > 790: continue  # 쪽 번호
        txt = "".join(c[2] for c in chars)
        if first[2] in PUNCT and first[1] < 80:
            hits["punct"].append((pno+1, txt[:60]))
        ismath_last = ("Type3" in last[3] or "KaTeX" in last[3])
        if prev_math_end and first[1] < 80 and txt[:2] in JOSA or (prev_math_end and first[1] < 80 and txt[:1] in JOSA and (len(txt)<2 or not ('가' <= txt[1] <= '힣'))):
            hits["josa"].append((pno+1, txt[:60]))
        prev_math_end = ismath_last
for k, v in hits.items():
    print(k, len(v))
    for e in v[:80]: print("  ", e)
