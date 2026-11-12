# -*- coding: utf-8 -*-
"""첫 판 진술 머리(heads.txt)와 구조표 v2에서 둘째 판 라벨 등록부 파견/라벨_v2.md를 만든다."""
import io, re

DRAFT = r"C:\math\임시\주차함수_증명\원고.md"
STRUCT = r"C:\math\임시\주차함수_증명\구조표_v2.md"
OUT = r"C:\math\임시\주차함수_증명\파견\라벨_v2.md"

# 첫 판 번호 → 둘째 판 (장, 절) 규칙
MOVED = {
    "7.13": (6, "6.1"), "7.19": (6, "6.2"), "7.20": (6, "6.2"), "7.21": (6, "6.2"), "7.24": (6, "6.2"),
    "8.11": (6, "6.4"), "8.12": (6, "6.4"), "8.13": (6, "6.3"),
    "6.18": (6, "6.5"), "6.19": (6, "6.5"),
}
DELETED = {"7.47", "7.48", "7.49", "8.38", "8.7", "8.27", "8.29"}
SEC_MAP_6 = {  # 첫 판 6.x 절 → 둘째 판 절
    "6.1": (7, "7.1"), "6.2": (7, "7.2"), "6.3": (7, "7.3"), "6.4": (7, "7.4"),
    "6.5": (7, "7.5"), "6.6": (7, "7.6"), "6.7": (6, "6.5"), "6.8": (7, "7.7"),
    "6.9": (8, "8.x"), "6.10": (7, "7.8"),
}
SEC_MAP_7 = {"7.1": "9.2", "7.2": "9.3", "7.3": "9.4", "7.4": "9.5", "7.5": "9.6", "7.6": "삭제"}
SEC_MAP_8 = {"8.1": "10.1", "8.2": "10.2", "8.3": "10.3", "8.4": "10.4", "8.5": "10.5", "8.6": "10.6", "8.7": "10.7", "8.8": "삭제"}
# 6.9절 안의 세부 자리
SEC_69 = {"6.23": "8.1", "6.24": "8.1", "6.25": "8.1", "6.26": "8.1", "6.27": "8.1",
          "6.28": "8.2", "6.29": "8.4", "6.30": "8.3", "6.31": "8.3", "6.32": "8.3", "6.33": "8.4"}

rows = []
cur_sec = None
# 진술 머리는 첫 판 조립본(원고.md)에서 직접 읽는다. heads.txt는 `$H^*_+$`처럼 머리 안에 `*`가 든 진술(정리 7.23)을 놓쳤다.
for lineno, ln in enumerate(io.open(DRAFT, encoding="utf-8").read().split("\n"), 1):
    body = ln.strip()
    m = re.match(r"^#{2,4} (\d+(?:\.\d+)*)", body)
    if m:
        cur_sec = m.group(1)
        continue
    m = re.match(r"^\*\*(정의|정리|명제|보조정리|따름정리) (\d+)\.(\d+) (.*)$", body)
    if not m:
        continue
    kind, ch, no, rest = m.groups()
    num = f"{ch}.{no}"
    rest = rest.split(".**")[0].strip()
    name = ""
    if rest.startswith("("):
        # 균형 잡힌 괄호 안의 이름(안에 「식 (2.1)」 같은 괄호가 들 수 있다)
        depth = 0
        for i, c in enumerate(rest):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    name = rest[1:i]
                    break
        name = name.split("; 기록")[0].strip()
    sec1 = cur_sec if cur_sec else ch
    sec1_top = ".".join(sec1.split(".")[:2])
    if num in DELETED:
        new = "뺌"; label = "—"
    elif num in MOVED:
        nch, nsec = MOVED[num]
        new = nsec; label = f"{{{{{nch}:old-{ch}-{no}}}}}"
    else:
        ichap = int(ch)
        if ichap <= 5:
            nch, nsec = ichap, sec1_top
        elif ichap == 6:
            if num in SEC_69:
                nch, nsec = 8, SEC_69[num]
            else:
                nch, nsec = SEC_MAP_6[sec1_top]
        elif ichap == 7:
            nch, nsec = 9, SEC_MAP_7[sec1_top]
        elif ichap == 8:
            nch, nsec = 10, SEC_MAP_8[sec1_top]
        else:
            nch, nsec = ichap, sec1_top
        new = nsec; label = f"{{{{{nch}:old-{ch}-{no}}}}}"
    note = ""
    if num == "2.31":
        note = "세 부등식 (SM)·(DM0)·(SC)만의 정리로 다시 진술(결합의 존재와 문헌 인용은 뺌)"
    if num == "2.39":
        note = "괄호의 「이름은 3.4절에서 정한다」는 뺌"
    rows.append((num, lineno, f"{kind} {name}".strip(), new, label, note))

# 구조표 v2의 새 라벨
struct = io.open(STRUCT, encoding="utf-8").read()
new_labels = []
seen = set()
for m in re.finditer(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}", struct):
    ch, name = m.groups()
    if name.startswith("old-"):
        continue
    key = (ch, name)
    if key in seen:
        continue
    seen.add(key)
    # 절 추정: 라벨이 나온 행의 첫 칸
    line_start = struct.rfind("\n", 0, m.start()) + 1
    line = struct[line_start: struct.find("\n", m.start())]
    sec = line.split("|")[1].strip() if line.startswith("|") else ""
    sec = sec.split(" ")[0]
    new_labels.append((ch, name, sec))

out = []
out.append("# 라벨 등록부 v2\n")
out.append("작성일 2026-11-12. 둘째 판의 모든 번호 붙은 진술은 라벨로 쓰고 조립 스크립트가 장 안의 등장 순서로 번호를 매긴다. 라벨의 꼴은 `{{N:이름}}`(N은 둘째 판 장 번호). 첫 판에서 옮기는 진술은 `old-장-번호`(첫 판 번호), 새 진술은 영문 이름. 이 등록부는 `scripts/_gen_라벨_v2.py`가 `구조표_v2.md`와 첫 판 진술 머리에서 만들었고, 집필자가 장 안에서만 쓰는 진술의 라벨을 반환에 적으면 세션이 여기에 더한다.\n")
out.append("## 1. 첫 판 진술의 대응\n")
out.append("| 첫 판 번호 | 첫 판 행 | 종류와 이름 | 둘째 판 절 | 라벨 | 비고 |")
out.append("|---|---|---|---|---|---|")
for num, lineno, kn, new, label, note in rows:
    out.append(f"| {num} | {lineno} | {kn} | {new} | `{label}` | {note} |")
out.append("")
out.append(f"첫 판 진술 {len(rows)}개 가운데 뺌 {sum(1 for r in rows if r[3]=='뺌')}개.\n")
out.append("## 2. 둘째 판의 새 진술(구조표 v2에서)\n")
out.append("| 장 | 라벨 | 절 |")
out.append("|---|---|---|")
for ch, name, sec in sorted(new_labels, key=lambda t: (int(t[0]), t[2], t[1])):
    out.append(f"| {ch} | `{{{{{ch}:{name}}}}}` | {sec} |")
out.append("")
out.append(f"새 라벨 {len(new_labels)}개.\n")
out.append("## 3. 부록 D 라벨\n")
out.append("부록 D 항목의 라벨은 `{{D:영문이름}}`이고 집필자가 부록 D 조각에서 만든다. 조립 때 등장 순서로 D.1, D.2, …를 매긴다.\n")
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("rows", len(rows), "new", len(new_labels))
