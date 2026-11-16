# -*- coding: utf-8 -*-
"""L14: 장부 1.2의 「쓰이는 장」·「정의 절」 열을 장 파일 본문과 맞춘다(자리 찾기용; 판정은 손으로).
사용: python -I 검토전체6_L14_symbols.py [--all]
"""
import re, sys, json
from pathlib import Path

ROOT = Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
FILES = {"1": ["장1"], "2": ["장2"], "3": ["장3"], "4": ["장4"], "5": ["장5A", "장5B"], "6": ["장6"],
         "7": ["장7A", "장7B"], "8": ["장8"], "9": ["장9"], "10": ["장10"], "11": ["장11"]}
TEXT = {}
SECS = {}
for c, fs in FILES.items():
    TEXT[c] = ""
    SECS[c] = []
    for f in fs:
        lines = (CH / f"{f}.md").read_text(encoding="utf-8").splitlines()
        cur = None
        for ln in lines:
            m = re.match(r"^(#{2,4})\s+(\S+)", ln)
            if m:
                cur = m.group(2)
            SECS[c].append((cur, ln))
        TEXT[c] += "\n".join(lines) + "\n"

def norm(s):
    return re.sub(r"\s+", "", s)

NTEXT = {c: norm(t) for c, t in TEXT.items()}

def variants(cell):
    cell = cell.strip().strip("$")
    # 쉼표로 나누되 중괄호 안은 보존
    out, depth, cur = [], 0, ""
    for ch in cell:
        if ch == "{": depth += 1
        if ch == "}": depth -= 1
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return [norm(v) for v in out if v.strip()]

def base(v):
    # 첨자·인수를 떼어낸 바탕 토큰
    v = re.sub(r"\([^()]*\)$", "", v)
    m = re.match(r"^(\\(?:mathcal|mathfrak|mathsf|mathrm|mathbb|mathscr|tilde|hat|bar)\s*\{?[A-Za-z]+\}?|\\[A-Za-z]+|[A-Za-z])", v)
    return m.group(1) if m else v

def main():
    lb = (ROOT / "장부_v2.md").read_text(encoding="utf-8").splitlines()
    s = next(i for i, l in enumerate(lb) if l.startswith("### 1.2"))
    e = next(i for i, l in enumerate(lb) if l.startswith("### 1.3"))
    for i in range(s, e):
        ln = lb[i]
        if not ln.startswith("| $") and not ln.startswith("| ("):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 7:
            continue
        sym, meaning, defsec, chaps = c[0], c[2], c[3], c[4]
        listed = ["1","2","3","4","5","6","7","8","9","10","11"] if "전 장" in chaps else re.findall(r"\d+", chaps)
        vs = variants(sym)
        exact = {}
        basef = {}
        for ch, t in NTEXT.items():
            ex = [v for v in vs if v and v in t]
            exact[ch] = ex
            bs = sorted({base(v) for v in vs if base(v) and len(base(v)) > 1 and base(v) in t})
            basef[ch] = bs
        found_any = [ch for ch in NTEXT if exact[ch] or basef[ch]]
        found_exact = [ch for ch in NTEXT if exact[ch]]
        # 정의 절: 첫 등장 절(정의 장에서)
        defchap = re.match(r"\d+", defsec)
        first_sec = None
        if defchap and defchap.group(0) in SECS:
            for sec, l in SECS[defchap.group(0)]:
                nl = norm(l)
                if any(v in nl for v in vs):
                    first_sec = sec
                    break
        miss = [ch for ch in listed if ch not in found_any]
        extra = [ch for ch in found_exact if ch not in listed]
        flag = ""
        if miss: flag += f" 표에 있으나 본문에서 못 찾음: {miss};"
        if extra: flag += f" 본문에 정확히 있으나 표에 없음: {extra};"
        defsecs = re.findall(r"\d+\.\d+", defsec)
        if first_sec and defsecs and not any(first_sec == d or first_sec.startswith(d + ".") for d in defsecs):
            flag += f" 첫 등장 절 {first_sec} ≠ 정의 절 {defsec};"
        if flag or "--all" in sys.argv:
            print(f"[장부 {i+1}] {sym[:60]} | 표 장: {chaps} | 정의 절 {defsec} |{flag}")

if __name__ == "__main__":
    main()
