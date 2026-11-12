# -*- coding: utf-8 -*-
"""KaTeX 검사(_katex_check.py)가 찾은 기계적 오류를 고친다(장6.md는 집필자가 편집 중이라 제외; 인자로 파일을 주면 그 파일만).
(1) 글자체 명령 중복: \\mathfrak \\mathfrak S → \\mathfrak S (mathcal·mathrm·mathsf·mathbb·mathbf도).
(2) \\frac의 인자가 글자체 명령으로 시작하면 중괄호로 감싼다: \\frac\\mathfrak t{..} → \\frac{\\mathfrak t}{..}; \\frac1\\mathfrak J → \\frac1{\\mathfrak J}; \\frac{..}\\mathcal X → \\frac{..}{\\mathcal X}.
(3) 첨자·위첨자·적분 한계의 글자체 명령: _\\mathfrak J → _{\\mathfrak J}, ^\\mathfrak t → ^{\\mathfrak t}.
사용: python _fix_katex_glue.py [--dry] [파일 ...]
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dry = "--dry" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
files = args or [p for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) if os.path.basename(p) != "장6.md"]
FONT = r"(mathfrak|mathcal|mathrm|mathsf|mathbb|mathbf)"
ARG = r"(\{[^{}]*\}|[A-Za-z])"
FIRST = r"(\{(?:[^{}]|\{[^{}]*\})*\}|\d|[A-Za-z])"
SUB = r"(?:_(?:\{[^{}]*\}|[^\s{}\\]))?(?:\^(?:\{[^{}]*\}|[^\s{}\\]))?"
RULES = [
    (re.compile(r"\\" + FONT + r"\s+\\" + FONT + r"(?=[\s{])"), r"\\\2"),
    (re.compile(r"\\(d?frac)\s*(\\" + FONT + r"\s?" + ARG + SUB + r")"), r"\\\1{\2}"),
    (re.compile(r"\\(d?frac)\s*(" + FIRST + r"|\\[A-Za-z]+)\s*(\\" + FONT + r"\s?" + ARG + SUB + r")"), r"\\\1{\2}{\4}"),
    (re.compile(r"\\fracr\{"), r"\\frac{r}{"),
    (re.compile(r"\\(tilde|hat|bar|check|widehat|widetilde)\s+(\\" + FONT + r"\s?" + ARG + r")"), r"\\\1{\2}"),
    (re.compile(r"([_^])(\\(?:hat|tilde|bar|check|widehat|widetilde)\{(?:[^{}]|\{[^{}]*\})*\})"), r"\1{\2}"),
    (re.compile(r"\\(int|sum|prod|max|min|sup|inf|lim|bigcup|bigcap)_\\" + FONT + r"\s?([A-Za-z])"), r"\\\1_{\\\2 \3}"),
    (re.compile(r"([A-Za-z0-9)\]}])\^\\" + FONT + r"\s?([A-Za-z])(?![A-Za-z])"), r"\1^{\\\2 \3}"),
    (re.compile(r"([A-Za-z0-9)\]}])_\\" + FONT + r"\s?([A-Za-z])(?![A-Za-z])"), r"\1_{\\\2 \3}"),
    (re.compile(r"\\sqrt\\" + FONT + r"\s?([A-Za-z])(?![A-Za-z])"), r"\\sqrt{\\\1 \2}"),
]
total = 0
for p in files:
    s = io.open(p, encoding="utf-8").read()
    t = s
    counts = []
    for rx, rep in RULES:
        t, n = rx.subn(rep, t)
        counts.append(n)
    if t != s:
        total += sum(counts)
        print(os.path.basename(p), counts)
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("총", total, "(dry)" if dry else "")
