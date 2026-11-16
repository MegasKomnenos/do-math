# -*- coding: utf-8 -*-
"""장 파일의 진술 머리를 색인하고(라벨→유형·이름·절·표지), 진술 블록마다 인용하는 라벨을 모은다.
또 장11·부록A·B·C가 쓰는 라벨이 모두 정의되어 있는지 본다."""
import re, glob, os, json, sys
ROOT = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding="utf-8").read()

HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\}\s*(?:\(([^)]*(?:\([^)]*\))?[^)]*)\))?\s*(?:\[([^\]]*)\])?\.?\*\*(.*)$")
index = {}      # key "장:label" -> info
blocks = []     # (key, chapter, section, text)
for f in sorted(glob.glob(os.path.join(ROOT, "장*.md"))):
    ch = os.path.basename(f)[1:-3]
    if ch == "11": pass
    lines = rd(f).splitlines()
    sec = ""
    cur = None; buf = []
    def flush():
        global cur, buf
        if cur is not None:
            blocks.append((cur, ch, cursec, "\n".join(buf)))
        cur = None; buf = []
    cursec = ""
    for i, ln in enumerate(lines, 1):
        ms = re.match(r"^(#{2,4}) ([\d.]+[A-Z]?)\s", ln)
        if ms:
            flush(); sec = ms.group(2); continue
        m = HEAD.match(ln)
        if m:
            flush()
            typ, chp, lab, name, tag, rest = m.groups()
            key = f"{chp}:{lab}"
            if key in index: print("중복 라벨:", key, f, i)
            index[key] = dict(type=typ, name=name, tag=tag, file=os.path.basename(f), line=i, sec=sec, head=ln[:400])
            cur = key; cursec = sec; buf = [ln]
        else:
            if cur is not None:
                # 블록 끝: 빈 줄 뒤 다음 머리 또는 절 머리까지 포함 (증명 포함). 단순히 이어붙인다.
                buf.append(ln)
    flush()

json.dump(dict(index=index, blocks=[(k, c, s, t) for k, c, s, t in blocks]),
          open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_M11_index.json", "w", encoding="utf-8"), ensure_ascii=False)
print("진술 수:", len(index))

# 사용 라벨 검사
for name in ["장11.md", "부록A.md", "부록B.md", "부록C.md"]:
    txt = rd(os.path.join(ROOT, name))
    used = set(re.findall(r"\{\{(\w+:[^}]+)\}\}", txt))
    missing = sorted(u for u in used if not u.startswith("D:") and u not in index)
    print(name, "사용 라벨", len(used), "미정의:", missing)
# D 라벨
Dlabs = set()
for f in glob.glob(os.path.join(ROOT, "부록D_장*.md")):
    Dlabs |= set(re.findall(r"(?m)^### D\.\{\{D:([^}]+)\}\}", rd(f)))
for name in ["장11.md", "부록A.md", "부록C.md"]:
    txt = rd(os.path.join(ROOT, name))
    used = set(re.findall(r"\{\{D:([^}]+)\}\}", txt))
    print(name, "D 라벨 미정의:", sorted(used - Dlabs))

# 유형 일치 검사: 장11/부록C에서 "정리 {{x}}" 처럼 유형 낱말이 붙은 자리의 유형이 색인과 같은지
for name in ["장11.md", "부록A.md", "부록C.md"]:
    txt = rd(os.path.join(ROOT, name))
    for m in re.finditer(r"(정리|명제|보조정리|따름정리|정의) \{\{(\w+:[^}]+)\}\}", txt):
        typ, key = m.groups()
        if key in index and index[key]["type"] != typ:
            print(f"[유형 불일치] {name}: '{typ} {key}' 색인={index[key]['type']} ({index[key]['file']}:{index[key]['line']})")
    # 가운뎃점 묶음: '정리 {{a}}·{{b}}' 에서 뒤 라벨 유형
    for m in re.finditer(r"(정리|명제|보조정리|따름정리|정의) \{\{(\w+:[^}]+)\}\}((?:·\{\{\w+:[^}]+\}\})+)", txt):
        typ = m.group(1)
        for key in re.findall(r"\{\{(\w+:[^}]+)\}\}", m.group(3)):
            if key in index and index[key]["type"] != typ:
                print(f"[유형 불일치·묶음] {name}: '{typ} …·{key}' 색인={index[key]['type']}")
