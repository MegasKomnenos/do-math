# -*- coding: utf-8 -*-
"""외부 피드백(2026-11-13)의 기계적 결함을 고친다.
(가) 명령어에 글자가 붙은 오타: \\ley→\\le y, \\leU→\\le U, \\inftyy→\\infty y, \\fracy→\\frac y, \\mathfrak sy→\\mathfrak s y, \\mathfrak am→\\mathfrak a m (장v2 전체).
(나) 3장 로그오목 꼬리 합: T_h T_{3I}→T_I T_{3I}, T^{(n)}_h→T^{(n)}_I.
(다) 7A 정리 7.20 증명의 옛 T: e^{\\epsilon_kT}→e^{\\epsilon_k\\mathcal J^{\\mathrm S}}, \\int_0^Tx→\\int_0^{\\mathcal J^{\\mathrm S}}x.
(라) 7B 식 번호 (7.n)→(7.n+1) (장7B.md·부록D_장7B.md; 7A의 (7.1)과 중복 해소).
(마) 장부 v2의 짧은 식별자 r9e782→r9e782f5, r8d685→r8d6850a.
(바) 7A 부록 D의 표 값 가족 \\mathfrak K^{L,U}_j(세션 치환으로 \\mathrm{km}_j가 된 것 포함)→\\mathrm{pw} 가족(9.3 전역 \\mathfrak K_N·1.2 km_N 회피).
(사) 작성자 판단 문장 표지 「(작성자 판단) 」→「† 」와 1.5의 설명 문장 변경(세션 결정 57).
"""
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "장v2")


def rw(path, fn, label):
    s = io.open(path, encoding="utf-8").read()
    t, n = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
    print(f"{label}: {os.path.basename(path)} {n}")


# (가)
GLUE = [(r"\\ley(?![A-Za-z])", r"\\le y"), (r"\\leU(?![A-Za-z])", r"\\le U"), (r"\\inftyy(?![A-Za-z])", r"\\infty y"),
        (r"\\fracy(?![A-Za-z])", r"\\frac y"), (r"\\mathfrak sy(?![A-Za-z])", r"\\mathfrak s y"), (r"\\mathfrak am(?![A-Za-z])", r"\\mathfrak a m")]
for p in sorted(glob.glob(os.path.join(CH, "*.md"))):
    def f(s):
        n = 0
        for a, b in GLUE:
            s, k = re.subn(a, b, s)
            n += k
        return s, n
    rw(p, f, "(가)")

# (나)
def f3(s):
    s, n1 = re.subn(r"T_h\s*T_\{3I\}", r"T_I T_{3I}", s)
    s, n2 = re.subn(r"T\^\{\(n\)\}_h(?![A-Za-z])", r"T^{(n)}_I", s)
    return s, n1 + n2
rw(os.path.join(CH, "장3.md"), f3, "(나)")

# (다)
def f7a(s):
    s, n1 = re.subn(r"e\^\{\\epsilon_kT\}", r"e^{\\epsilon_k\\mathcal J^{\\mathrm S}}", s)
    s, n2 = re.subn(r"\\int_0\^Tx\^", r"\\int_0^{\\mathcal J^{\\mathrm S}}x^", s)
    return s, n1 + n2
rw(os.path.join(CH, "장7A.md"), f7a, "(다)")

# (라)
def renum(s):
    n = 0
    def tag(m):
        nonlocal n
        n += 1
        return "\\tag{7.%d}" % (int(m.group(1)) + 1)
    def ref(m):
        nonlocal n
        n += 1
        return "(7.%d)" % (int(m.group(1)) + 1)
    s = re.sub(r"\\tag\{7\.(\d+)\}", tag, s)
    s = re.sub(r"\(7\.(\d+)\)", ref, s)
    return s, n
for nm in ["장7B.md", "부록D_장7B.md"]:
    rw(os.path.join(CH, nm), renum, "(라)")

# (마)
def ids(s):
    s, n1 = re.subn(r"r9e782(?![0-9a-f])", "r9e782f5", s)
    s, n2 = re.subn(r"r8d685(?![0-9a-f])", "r8d6850a", s)
    return s, n1 + n2
rw(os.path.join(ROOT, "장부_v2.md"), ids, "(마)")

# (바)
def pw(s):
    n = 0
    for a, b in [(r"\\mathrm\{km\}_j", r"\\mathrm{pw}^{\\mathrm U}_j"), (r"\\mathrm\{km\}_2", r"\\mathrm{pw}^{\\mathrm U}_2"), (r"\\mathrm\{km\}_\{(\d+)\}", r"\\mathrm{pw}^{\\mathrm U}_{\1}"),
                 (r"\\mathfrak K\^\{\\mathrm L\}", r"\\mathrm{pw}^{\\mathrm L}"), (r"\\mathfrak K'\^\{\\mathrm U\}", r"\\mathrm{pw}'^{\\mathrm U}"),
                 (r"\\hat\{\\mathfrak K\}", r"\\hat{\\mathrm{pw}}"), (r"\\check\{\\mathfrak K\}", r"\\check{\\mathrm{pw}}")]:
        s, k = re.subn(a, b, s)
        n += k
    return s, n
rw(os.path.join(CH, "부록D_장7A.md"), pw, "(바)")

# (사)
for p in sorted(glob.glob(os.path.join(CH, "장*.md"))):
    def dag(s):
        return re.subn(r"\(작성자 판단\)\s*", "† ", s)
    rw(p, dag, "(사)")
def f1(s):
    a = "본문에서는 그 단계가 시작하는 문장 앞에 † 을 붙인다"
    if a in s:
        s = s.replace(a, "본문에서는 그 단계가 시작하는 문장 앞에 칼표 †를 붙인다")
        return s, 1
    return s, 0
rw(os.path.join(CH, "장1.md"), f1, "(사-1.5)")
print("done")
