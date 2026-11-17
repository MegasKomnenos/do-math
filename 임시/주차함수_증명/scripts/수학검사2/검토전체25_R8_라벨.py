# 검토전체25 R8: 장8.md가 부르는 라벨이 정의 머리로 있는지, 줄마다 $ 짝과 중괄호 짝이 맞는지 센다 (자리 찾기용)
import re, glob, io
src = io.open("장v2/장8.md", encoding="utf-8").read()
refs = sorted(set(re.findall(r"\{\{([0-9D]+:[^}]+)\}\}", src)))
heads = {}
for f in glob.glob("장v2/*.md"):
    t = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r"^\*\*(정리|보조정리|명제|따름정리|정의) \{\{([^}]+)\}\}", t, re.M):
        heads.setdefault(m.group(2), []).append((f, m.group(1)))
    for m in re.finditer(r"^### D\.\{\{([^}]+)\}\}", t, re.M):
        heads.setdefault(m.group(1), []).append((f, "부록 D 항목"))
kinds = {}
for m in re.finditer(r"(정리|보조정리|명제|따름정리|정의|부록 D\.)\s*((?:\{\{[^}]+\}\}[·]?)+)", src):
    for lab in re.findall(r"\{\{([^}]+)\}\}", m.group(2)):
        kinds.setdefault(lab, set()).add(m.group(1))
for r in refs:
    h = heads.get(r)
    print(r, "->", h if h else "!! 머리 없음", "| 본문이 부른 유형:", sorted(kinds.get(r, [])))
for i, line in enumerate(src.split("\n"), 1):
    body = line.replace("\$", "")
    nd = len(re.findall(r"(?<!\$)\$(?!\$)", body))
    if nd % 2: print("홀수 $ 줄", i)
    if body.count("{") != body.count("}"): print("중괄호 불균형 줄", i, body.count("{"), body.count("}"))
    if body.count("(") != body.count(")"): print("소괄호 불균형 줄", i, body.count("("), body.count(")"))
