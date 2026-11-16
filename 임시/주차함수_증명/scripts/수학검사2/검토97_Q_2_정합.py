# -*- coding: utf-8 -*-
"""검토 97 Q (2): 스크립트 EDITS 적용 여부, 장10의 기호 사용, 장부 1절 「쓰는 장」 정합, 의존지도·장부 4절의 뺌 선례."""
import io, os, re, sys, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rd = lambda rel: io.open(os.path.join(ROOT, rel), encoding="utf-8").read()

# (가) 스크립트의 EDITS를 소스에서 읽어 새 문자열이 있고 옛 문자열이 없는지
src = rd("scripts/수학검사2/결정97_문턱예산_정리.py")
ns = {}
m = re.search(r"EDITS = \[(.*?)\n\]\n", src, re.S)
EDITS = eval("[" + m.group(1) + "]")
print("EDITS 수", len(EDITS))
for rel, old, new in EDITS:
    s = rd(rel)
    print("  %-14s old=%d new=%d | %s" % (rel, s.count(old), s.count(new), old[:50].replace("\n", " ")))

# (나) 장10에서 기호 사용 수
s10 = rd("장v2/장10.md")
for sym in [r"\mathcal V_k", r"\mathfrak p_m", r"Bd}^{\mathrm V}", r"\mathrm{Quad}", r"\mathrm{Stem}", r"(\star)(n)", r"\mathfrak u_n",
            r"\mathfrak f^X", r"\mathfrak f^Y", r"\epsilon^{\mathrm d}", r"C^{(\ell)}", r"\mathfrak g^{\mathrm L}", r"u^\ast_S", r"\bar w", r"Stays}_{\mathrm{col}}",
            r"\mathsf s_{", r"{{10:old-8-7}}", r"{{10:old-8-27}}", r"{{10:old-8-29}}", r"{{6:old-6-19}}", r"{{6:V-all}}", r"{{10:old-8-3}}", r"{{10:old-8-4}}", r"{{10:old-8-6}}",
            r"\mathrm{DD}(m,k-1)", r"s_N(k+1)", r"\mathcal V_k(N+1)", r"2k+1\le n\le3k", r"k\ge43", r"w_{k-1}"]:
    print("  장10 %-28s %d" % (sym, s10.count(sym)))

# (다) 장부 1절 「쓰는 장」: 10을 적은 행 가운데 기호가 장10에 없는 것 / 장10에 있는데 10이 없는 것(ℒ·Bd·V·p 관련만 표본)
lb = rd("장부_v2.md").split("\n")
sec = None
for i, l in enumerate(lb):
    if l.startswith("## "):
        sec = l.strip()
    if l.startswith("| $") and sec and sec.startswith("## 1"):
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) >= 5:
            sym, kind, mean, defsec, chaps = cells[:5]
            core = sym.strip("$")
            for probe in (r"\mathcal V_k", r"\mathfrak p_m", r"\mathrm{Bd}^{\mathrm V}", r"\mathrm{Stem}", r"\mathrm{Quad}", r"(\star)", r"\mathfrak u_n", r"\varsigma_m", r"\mathrm{DD}", r"\mathfrak T_m", r"\mathfrak f_m", r"\varkappa_m", r"w_m"):
                if core.startswith(probe):
                    in10 = s10.count(core.split(",")[0].split("(")[0].replace(r"\mathrm{Bd}^{\mathrm V}_k", r"Bd}^{\mathrm V}"))
                    print("  1절 %4d %-40s 정의 %s 쓰는 장 [%s] 장10 출현 %d" % (i + 1, sym[:40], defsec, chaps, in10))
