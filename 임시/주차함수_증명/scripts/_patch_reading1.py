# -*- coding: utf-8 -*-
"""첫 독립 독해(8af9330a) 대조 뒤 세션 직권 수리(기계적 항목): 5.5절 배치, 1.4 「문헌의 극한 정리」, s_m(0):=0,
문헌 정리 번호 원문 표기, 7장·8장의 옛 번호 리터럴 → 라벨."""
import io
import re


def rw(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


root = "임시/주차함수_증명"

# A. 조립: 5B(5.5)를 5A의 「### 5.6」 앞에 끼운다
p = root + "/scripts/조립.py"
s = rw(p)
old = '''    for name in PARTS:
        path = os.path.join(ROOT, "장", name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        text = io.open(path, encoding="utf-8").read()
        if not text.endswith("\\n"):
            text += "\\n"
        pieces.append("\\n" + text)'''
assert s.count(old) == 1, s.count(old)
new = '''    texts = {}
    for name in PARTS:
        path = os.path.join(ROOT, "장", name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        text = io.open(path, encoding="utf-8").read()
        if not text.endswith("\\n"):
            text += "\\n"
        texts[name] = text
    # 5장: 장5A.md는 5.1–5.4와 5.6–5.7, 장5B.md는 5.5이므로 5B를 5A의 「### 5.6」 앞에 끼운다(독해 1의 지적 5).
    if "장5A.md" in texts and "장5B.md" in texts:
        a = texts["장5A.md"]
        cut = a.find("\\n### 5.6")
        if cut < 0:
            problems.append("장5A.md에 「### 5.6」 머리가 없어 5.5를 제자리에 끼우지 못함")
        else:
            texts["장5A.md"] = a[:cut + 1] + "\\n" + texts["장5B.md"] + a[cut + 1:]
            del texts["장5B.md"]
    for name in PARTS:
        if name in texts:
            pieces.append("\\n" + texts[name])'''
s = s.replace(old, new)
# problems 변수가 pieces 조립 전에 정의되어야 한다
old2 = '''    pieces = [TITLE]
    missing = []'''
assert s.count(old2) == 1
s = s.replace(old2, '''    pieces = [TITLE]
    missing = []
    problems = []''')
old3 = '''    out = "".join(pieces)
    problems = []'''
assert s.count(old3) == 1
s = s.replace(old3, '''    out = "".join(pieces)''')
wr(p, s)
print("조립: 5.5 배치")

# B1. 1.4 「문헌의 극한 정리」 → 「문헌의 정리」
p = root + "/장/장1.md"
s = rw(p)
n = s.count("문헌의 극한 정리")
s = s.replace("문헌의 극한 정리", "문헌의 정리")
wr(p, s)
print("장1 극한 정리 →", n)

# B2. s_m(0):=0
p = root + "/장/장2.md"
s = rw(p)
old = r"c_m(Y):=\frac{b_{m,Y}}{p_m}=\Pr_m(M=Y)=s_m(Y+1)-s_m(Y)"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, old + r"\qquad(Y\ge0;\ s_m(0):=0)")
wr(p, s)
print("장2 s_m(0)")

# B3. 문헌 정리 번호 원문 표기
p = root + "/장/장3.md"
s = rw(p)
old = "Uppsala Dissertations in Mathematics 63)의 정리 2.1에서"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "Uppsala Dissertations in Mathematics 63)의 Theorem 2.1에서")
wr(p, s)
p = root + "/장/장9.md"
s = rw(p)
old = "Petersson의 학위논문(2009) 정리 2.1에"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "Petersson의 학위논문(2009) Theorem 2.1에")
wr(p, s)
print("장3·장9 Theorem 2.1")

# B4. 7장 옛 번호 리터럴 → 라벨
p = root + "/장/장7.md"
s = rw(p)
n = 0
for old, new in (("입력 정리 B′·정리 6.23", "입력 정리 B′·정리 {{old:정리 6.23}}"),
                 ("정리 6.23의 배정밀도 상자 검사", "정리 {{old:정리 6.23}}의 배정밀도 상자 검사")):
    n += s.count(old)
    s = s.replace(old, new)
assert not re.search(r"(?<!\{\{old:)정리 6\.23", s), "장7에 정리 6.23 리터럴 잔존"
wr(p, s)
print("장7 정리 6.23 → 라벨", n)

# B5. 8장 옛 번호 리터럴 → 라벨
p = root + "/장/장8.md"
s = rw(p)
n = 0
for old, new in (("명제 6.19의 입력인 명제 6.16", "명제 {{old:명제 6.19}}의 입력인 명제 {{old:명제 6.16}}"),
                 ("$t=3k$를 정리 6.20으로, $t\\ge3k+1$을 명제 6.19로", "$t=3k$를 정리 {{old:정리 6.20}}으로, $t\\ge3k+1$을 명제 {{old:명제 6.19}}로")):
    n += s.count(old)
    s = s.replace(old, new)
left = re.findall(r"(?<!\{\{old:)(?:정리|명제) 6\.(?:16|19|20)", s)
print("장8 라벨화", n, "잔존", left)
wr(p, s)
