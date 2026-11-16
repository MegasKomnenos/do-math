# -*- coding: utf-8 -*-
"""M14: 장부 5절 「여유 글자」가 같은 장부 1.2의 「쓰이는 장」·「바탕 글자·글자체」와 맞는지 센다
(그 장에서 쓰이는 전역 글자의 (바탕 글자, 글자체)가 여유 목록에 남아 있으면 적는다)."""
import re, pathlib
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
lines = (ROOT / "장부_v2.md").read_text(encoding="utf-8").splitlines()
# 1.2 행
rows = []; in12 = False
for ln in lines:
    if ln.startswith("### 1.2"): in12 = True; continue
    if ln.startswith("### 1.3"): break
    if in12 and ln.startswith("| $"):
        rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
style_map = {"일반(이탤릭)": "it", "필기체": "cal", "프락투어": "frak", "산세리프": "sf"}
used = {c: set() for c in range(1, 12)}   # chapter -> set of (base, style)
defch1 = set()
for cells in rows:
    glyph, bs, _, defsec, chaps = cells[:5]
    m = re.match(r"^(.+?)·(일반\(이탤릭\)|필기체|프락투어|산세리프|로마체 이름|칠판체.*|꼬리표)", bs)
    if not m: continue
    base, style = m.group(1).strip(), m.group(2)
    if style not in style_map: continue
    st = style_map[style]
    base = base.replace("\\ell", "\\ell")
    if chaps.strip() == "전 장": cs = set(range(1, 12))
    else: cs = {int(x) for x in re.findall(r"\d+", chaps)}
    for c in cs: used[c].add((base, st))
    if defsec.strip().startswith("1."): defch1.add((base, st))
# 1.1 변수 글자
vars11 = {("n","it"),("m","it"),("t","it"),("N","it"),("k","it"),("\\ell","it"),("y","it"),("Y","it"),("i","it"),("j","it"),("u","it"),("v","it"),("r","it"),("\\nu","it"),("d","it"),("q","it")}
reserved = {("a","it"),("b","it"),("c","it"),("e","it"),("h","it"),("\\delta","it"),("o","it"),("O","it"),("l","it"),("\\Delta","it"),("\\Sigma","it"),("\\varpi","it"),("P","it"),("Q","it"),("W","it"),("X","it")}
# 5절 표
in5 = False
for ln in lines:
    if ln.startswith("## 5."): in5 = True; continue
    if ln.startswith("## 6."): break
    if not in5 or not re.match(r"^\| \d+ \|", ln): continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    ch = int(cells[0]); free = cells[3]
    letters = set()
    for seg in re.split(r"\.\s+", free):
        if ":" not in seg: continue
        head, body = seg.split(":", 1)
        if "그리스" in head or "라틴" in head: st = "it"
        elif "필기체" in head: st = "cal"
        elif "프락투어" in head: st = "frak"
        elif "산세리프" in head: st = "sf"
        else: continue
        for g in re.findall(r"\$([^$]+)\$", body):
            g = g.strip()
            g = re.sub(r"^\\(mathcal|mathfrak|mathsf)\s*", "", g)
            letters.add((g, st))
    bad = letters & (used[ch] | defch1 | vars11 | reserved)
    if bad:
        print(f"장 {ch}: 여유 목록에 있으나 그 장의 전역(1.2 쓰이는 장)·1장 전역·1.1 변수·예약과 겹침: {sorted(bad)}")
    # 반대로: 그 장의 전역 글자 가운데 여유 목록 규칙상 빠져야 할 것은 위에서 셌다. 여유에서 빠졌지만 어느 전역도 쓰지 않는 글자(빠진 까닭이 없는 것)도 적는다.
    all_latin = {chr(c) for c in range(ord("a"), ord("z")+1)} | {chr(c) for c in range(ord("A"), ord("Z")+1)}
    greek = ["\\alpha","\\beta","\\gamma","\\delta","\\epsilon","\\varepsilon","\\zeta","\\eta","\\theta","\\vartheta","\\iota","\\kappa","\\varkappa","\\lambda","\\mu","\\nu","\\xi","\\pi","\\rho","\\varrho","\\sigma","\\varsigma","\\tau","\\upsilon","\\phi","\\varphi","\\chi","\\psi","\\omega","\\Gamma","\\Delta","\\Theta","\\Lambda","\\Xi","\\Pi","\\Sigma","\\Upsilon","\\Phi","\\Psi","\\Omega"]
    cand = {(x,"it") for x in all_latin} | {(x,"it") for x in greek} | {(x,"cal") for x in all_latin if x.isupper()} | {(x,"frak") for x in all_latin} | {(x,"sf") for x in all_latin}
    should_free = cand - used[ch] - defch1 - vars11 - reserved - {("\\ell","it")}
    missing = should_free - letters
    # 산세리프·필기체 소문자 등은 목록 관례가 다를 수 있어 라틴 이탤릭·그리스·필기체 대문자·프락투어만 보고한다
    missing = {x for x in missing if x[1] in ("it","cal","frak","sf")}
    if missing:
        print(f"장 {ch}: 어느 전역·변수·예약도 아닌데 여유 목록에 없는 글자: {sorted(missing)}")
