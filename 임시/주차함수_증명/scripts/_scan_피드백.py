# -*- coding: utf-8 -*-
"""외부 피드백(2026-11-13)의 지적을 현재 파일에서 확인한다: 부록 A·C의 작업 메모, 깨진 LaTeX 명령, 3장 첨자, 7A 옛 T, 식 번호 중복, 짧은 식별자, 작성자 판단 표지."""
import glob
import io
import os
import re
from collections import Counter

ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, "장v2")

def rd(p):
    return io.open(p, encoding="utf-8").read()

# 1. 부록 A·C의 작업 메모
for nm in ["부록A.md", "부록C.md"]:
    s = rd(os.path.join(CH, nm))
    rows = [l for l in s.split("\n") if l.startswith("|")]
    bad = [l for l in rows if re.search(r"세션|집필|2차 대조|회수|지시|초안|결정 \d|파견|재대조|첫 판|확인 요|판정 요|조립본", l)]
    print(f"[1] {nm}: 표 행 {len(rows)}, 작업 메모 의심 행 {len(bad)}")
    for l in bad[:6]:
        print("    ", l[:160])
    if nm == "부록C.md":
        eng = [l for l in rows if l.startswith("| ") and l.count("|") >= 5]
        print("    영어 열 비어 있지 않은 행:", sum(1 for l in rows if re.search(r"\| [A-Za-z][A-Za-z\- ]+ \|", l)))

# 2. 깨진 LaTeX 명령: 전체 조립본의 \명령 토큰 빈도에서 드문 것
src = rd(os.path.join(ROOT, "원고.md"))
toks = Counter(re.findall(r"\\[A-Za-z]+", src))
known_prefix = ["\\mathrm", "\\mathfrak", "\\mathcal", "\\mathsf", "\\mathbb", "\\mathbf", "\\operatorname", "\\text", "\\begin", "\\end"]
rare = {t: c for t, c in toks.items() if c <= 3}
sus = [t for t in rare if re.search(r"(le|ge|infty|frac|sqrt|int|sum|prod|mathfrak s|lim|log|exp|cdot|quad|mid|to|in|ne|ll|gg|pm|mp|sim|ast|star|prime|dots|cdots|ldots|times|bigl|bigr|Bigl|Bigr|left|right|lfloor|rfloor|lceil|rceil|max|min|sup|inf|det|dim)[A-Za-z]$", t)]
print("[2] 드문 명령 토큰(≤3회) 수:", len(rare), "| 접미 글자가 붙은 의심 토큰:", sorted(sus)[:60])
back = re.findall(r"\\\d", src)
print("    역참조 잔재(\\1 등):", Counter(back))
for key in ["\\ley", "\\inftyy", "\\fracy", "\\mathfrak sy", "\\mathfrak am", "_\\1"]:
    n = src.count(key)
    if n:
        print(f"    {key!r}: {n}곳")

# 3. 3장 첨자
s3 = rd(os.path.join(CH, "장3.md"))
print("[3] 장3 T_h T_{3I}:", len(re.findall(r"T_h\s*T_\{3I\}|T\^\{\(n\)\}_h", s3)), "| T_I T_{3I}:", len(re.findall(r"T_I\s*T_\{3I\}", s3)))

# 4. 7A 옛 T
s7a = rd(os.path.join(CH, "장7A.md"))
print("[4] 7A e^{\\epsilon_kT}:", s7a.count("e^{\\epsilon_kT}"), "| \\int_0^T:", len(re.findall(r"\\int_0\^T(?![A-Za-z])", s7a)), "| \\mathcal J^{\\mathrm S}:", s7a.count("\\mathcal J^{\\mathrm S}"))

# 5. 식 번호
for nm in ["장5A.md", "장5B.md", "장7A.md", "장7B.md"]:
    s = rd(os.path.join(CH, nm))
    tags = re.findall(r"\\tag\{(\d+\.\d+)\}|\$\$\s*\((\d+\.\d+)\)\s*$|^\((\d+\.\d+)\)\s*$", s, re.M)
    nums = sorted({a or b or c for a, b, c in tags}, key=lambda x: tuple(int(v) for v in x.split(".")))
    print(f"[5] {nm} 식 번호 {len(nums)}: {nums[:3]} … {nums[-3:]}")

# 6. 짧은 식별자
for nm in ["장부_v2.md", "장v2/부록C.md", "장v2/부록A.md", "원고.md"]:
    s = rd(os.path.join(ROOT, nm))
    short = Counter(re.findall(r"\[(r[0-9a-f]{1,6})\]", s))
    print(f"[6] {nm} 짧은 식별자:", dict(short))

# 7. 작성자 판단 표지
n_inline = src.count("(작성자 판단)")
n_head = len(re.findall(r"작성자 판단[^\]]*\]", src))
print("[7] (작성자 판단) 문장 표지:", n_inline, "| 머리 덧붙임:", n_head)
for m in list(re.finditer(r"\(작성자 판단\)", src))[:3]:
    print("    ", src[m.start()-40:m.end()+80].replace("\n", " "))
