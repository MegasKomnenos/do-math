import re, sys
src = open("임시/dream-20261106/확정-G09.md", encoding="utf-8").read()
sec = src[src.index("## 5. L 패킷 확정본"):src.index("## 6. 지적 처분표")]
blocks = re.split(r"\n\*\*편집 (\d+)\*\*\n", sec)[1:]
edits = []
for i in range(0, len(blocks), 2):
    n, body = int(blocks[i]), blocks[i+1]
    tgt = re.search(r"- 대상: (L-\d{4})", body).group(1)
    anchor = re.search(r'- 기준점: "(.+)"\n', body).group(1)
    paras, cur = [], []
    for line in body.split("\n"):
        if line.startswith("> "): cur.append(line[2:])
        elif line.strip() == ">" and cur: paras.append(" ".join(cur)); cur = []
    if cur: paras.append(" ".join(cur))
    inline = "목록 항목 안" in body
    edits.append((n, tgt, anchor, paras, inline))
assert len(edits) == 11, len(edits)
applied = 0
for n, tgt, anchor, paras, inline in edits:
    path = f"기억/layer3/{tgt}.md"
    raw = open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    assert raw.count(anchor) == 1, (n, raw.count(anchor))
    pos = raw.index(anchor)
    if inline:
        end = raw.find(nl, pos); assert len(paras) == 1
        new = raw[:end] + " " + paras[0] + raw[end:]
    else:
        end = raw.find(nl + nl, pos)
        if end < 0: end = len(raw.rstrip())
        new = raw[:end] + "".join(nl + nl + p for p in paras) + raw[end:]
    assert len(new) > len(raw)
    open(path, "w", encoding="utf-8", newline="").write(new)
    applied += 1
    print(n, tgt, "nl=CRLF" if nl == "\r\n" else "nl=LF", "paras", len(paras), "| before insert:", raw[max(0,end-40):end].replace(nl, "/"))
print("applied", applied)
