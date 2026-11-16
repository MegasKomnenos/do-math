# -*- coding: utf-8 -*-
"""M14: 장부 1.3 「자리」 열의 (절, 라벨) 쌍이 장 파일의 실제 절과 맞는지, 1.2 「정의 절」이 그 글자가 처음 나타나는 장과 맞는지 센다."""
import re, json, pathlib
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
heads = json.load(open(ROOT/"scripts"/"수학검사2"/"_M14_heads.json", encoding="utf-8"))
def sec2(s):
    p = s.split("."); return ".".join(p[:2])
lines = (ROOT / "장부_v2.md").read_text(encoding="utf-8").splitlines()
in13 = False
for i, ln in enumerate(lines, 1):
    if ln.startswith("### 1.3"): in13 = True; continue
    if ln.startswith("## 2."): break
    if not in13 or not ln.startswith("| $") and not ln.startswith("| "): continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells) < 4 or cells[0] in ("글자(LaTeX)", "---"): continue
    place = cells[2]
    # 「2.5 `{{2:old-2-18}}` 증명; 2.8 `{{2:old-2-32}}` 증명」 꼴: 절 번호 뒤에 오는 라벨들
    for m in re.finditer(r"(\d+\.\d+(?:\.\d+)?)\s+((?:`\{\{[^}]+\}\}`(?:–`\{\{[^}]+\}\}`)?[·, ]*(?:증명)?[, ;]*)+)", place):
        sec = sec2(m.group(1))
        for lab in re.findall(r"\{\{([^}]+)\}\}", m.group(2)):
            h = heads.get(lab)
            if not h:
                print(f"L{i}: 라벨 없음 {lab}"); continue
            if sec2(h["sec"]) != sec:
                print(f"L{i}: 1.3 자리 절 {sec} ≠ 실제 {h['sec']} ({lab})")
print("1.3 자리 검사 끝")
