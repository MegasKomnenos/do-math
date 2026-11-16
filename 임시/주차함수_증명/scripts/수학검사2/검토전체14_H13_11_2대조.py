# H13: 부록 D(7A·7B·8·9·10)의 「독립 재계산」 줄과 11.2 표 행의 자리 찾기용 대조
import re, difflib
items = {}
for f in ("장v2/부록D_장7A.md","장v2/부록D_장7B.md","장v2/부록D_장8.md","장v2/부록D_장9.md","장v2/부록D_장10.md"):
    txt = open(f, encoding="utf-8").read()
    for m in re.finditer(r"^### D\.\{\{D:([^}]+)\}\}(.*?)(?=^### D\.|\Z)", txt, re.S|re.M):
        name, body = m.group(1), m.group(2)
        ir = re.search(r"\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*?)\n", body, re.S)
        ag = re.search(r"\*\*산술 등급\.\*\*\s*(.*?)\n", body)
        items[name] = (ir.group(1) if ir else None, ir.group(2).strip() if ir else None, ag.group(1).strip() if ag else None)
rows = {}
for line in open("장v2/장11.md", encoding="utf-8"):
    m = re.match(r"\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (〔[^〕]*〕) \| (.*?) \|\s*$", line)
    if m: rows[m.group(1)] = (m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))
for name, (br, text, grade) in items.items():
    if name not in rows: print("11.2에 없음:", name); continue
    stmt, g2, where, br2, text2 = rows[name]
    print("==", name, "| 11.2 진술:", stmt[:90], "| 등급:", g2, "| 곳:", where)
    if br != br2: print("  꺾쇠 다름:\n   D :", br, "\n   11:", br2)
    t2 = text2.replace("「재계산」 열의 꺾쇠 괄호", "이 문단 머리의 꺾쇠 괄호")
    if text != t2:
        sm = difflib.SequenceMatcher(None, text, t2)
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op != "equal": print("  본문 다름 [%s]: D=%r | 11=%r" % (op, text[max(0,a1-15):a2+15], t2[max(0,b1-15):b2+15]))
    print("  D 산술 등급 줄:", (grade or "")[:120])
