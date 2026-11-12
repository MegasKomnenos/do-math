# -*- coding: utf-8 -*-
"""Gr 치환이 삼킨 닫는 중괄호의 남은 네 자리를 정확한 문자열로 복구한다(2장 411·445·449행, 7B 147행)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = {
    "장2.md": [
        ("$e^{\\pm z\\mathrm{Gr}$", "$e^{\\pm z\\mathrm{Gr}}$"),
        ("\\bigl(e^{T+z\\mathrm{Gr}\\bigr)'", "\\bigl(e^{T+z\\mathrm{Gr}}\\bigr)'"),
        ("e^{T+z\\mathrm{Gr}$", "e^{T+z\\mathrm{Gr}}$"),
        ("e^{-z\\mathrm{Gr}x^{k-1}", "e^{-z\\mathrm{Gr}}x^{k-1}"),
    ],
    "장7B.md": [
        ("(e^{-z\\mathrm{Gr}\\mathcal S^{\\mathrm G})'", "(e^{-z\\mathrm{Gr}}\\mathcal S^{\\mathrm G})'"),
    ],
}
for rel, pairs in FIX.items():
    p = os.path.join(ROOT, "장v2", rel)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        print(rel, repr(a[:40]), "count", n)
        if n == 1:
            s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("done")
