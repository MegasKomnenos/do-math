# -*- coding: utf-8 -*-
"""L14: 장부 1.2 「쓰이는 장」 열을 바탕 글자(글자체 포함) 기준으로 장 파일과 맞춘다.
단일 글자(첨자 없는 F, G, L 등)는 뺀다. 결과는 자리 찾기용이며 판정은 손으로 한다.
사용: python -I 검토전체6_L14_symbols2.py
"""
import re
from pathlib import Path

ROOT = Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
FILES = {"1": ["장1"], "2": ["장2"], "3": ["장3"], "4": ["장4"], "5": ["장5A", "장5B"], "6": ["장6"],
         "7": ["장7A", "장7B"], "8": ["장8"], "9": ["장9"], "10": ["장10"], "11": ["장11"]}
TEXT = {c: "\n".join((CH / f"{f}.md").read_text(encoding="utf-8") for f in fs) for c, fs in FILES.items()}
NT = {c: re.sub(r"[ \t]+", "", t) for c, t in TEXT.items()}

def variants(cell):
    cell = cell.strip().strip("$")
    out, depth, cur = [], 0, ""
    for ch in cell:
        if ch in "{(": depth += 1
        if ch in "})": depth -= 1
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return [re.sub(r"\s+", "", v) for v in out if v.strip()]

FONT = r"(\\(?:mathcal|mathfrak|mathsf|mathrm|mathbb|tilde|hat|bar)\s*)"

def pattern(v):
    """변형 하나에서 검색 정규식을 만든다. None이면 검사하지 않음(단일 글자)."""
    m = re.match(r"^(" + FONT + r"?\{?([A-Za-z]+|\\[A-Za-z]+)\}?)(.*)$", v)
    if not m:
        return None
    head, font, letters, rest = m.group(1), m.group(2), m.group(3), m.group(4)
    core = re.escape(letters)
    if font:
        fnt = re.escape(re.sub(r"\s+", "", font))
        base = fnt + r"\{?" + core + r"\}?"
        if not rest:
            return base + r"(?![A-Za-z])"
        return base
    # 글자체 없는 라틴/그리스 바탕 글자
    if letters.startswith("\\"):
        if not rest:
            return None  # 첨자 없는 그리스 단일 글자는 국소로도 쓰여 판정 불가
        return core + r"(?=[_^(])"
    if len(letters) == 1:
        if not rest:
            return None
        # 첨자·인수가 있는 라틴 단일 글자: \mathfrak 등 뒤가 아니고, 다른 글자 뒤가 아님
        return r"(?<![A-Za-z\\])(?<!\\mathcal\{)(?<!\\mathfrak\{)(?<!\\mathsf\{)(?<!\\mathrm\{)(?<!\\mathbb\{)" + core + r"(?=[_^(])"
    return r"(?<![A-Za-z\\])" + core + r"(?=[_^(])"

def main():
    lb = (ROOT / "장부_v2.md").read_text(encoding="utf-8").splitlines()
    s = next(i for i, l in enumerate(lb) if l.startswith("### 1.2"))
    e = next(i for i, l in enumerate(lb) if l.startswith("### 1.3"))
    for i in range(s, e):
        ln = lb[i]
        if not (ln.startswith("| $") or ln.startswith("| (")):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 7:
            continue
        sym, chaps = c[0], c[4]
        listed = ["1","2","3","4","5","6","7","8","9","10","11"] if "전 장" in chaps else re.findall(r"\d+", chaps)
        pats = [p for p in (pattern(v) for v in variants(sym)) if p]
        if not pats:
            continue
        found = []
        for ch, t in NT.items():
            if any(re.search(p, t) for p in pats):
                found.append(ch)
        miss = [x for x in listed if x not in found]
        extra = [x for x in found if x not in listed]
        if miss or extra:
            print(f"[장부 {i+1}] {sym[:55]} | 표: {chaps} | 못 찾음: {miss} | 표 밖에서 찾음: {extra}")

if __name__ == "__main__":
    main()
