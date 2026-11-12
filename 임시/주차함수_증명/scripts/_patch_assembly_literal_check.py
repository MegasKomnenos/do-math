# -*- coding: utf-8 -*-
"""조립 스크립트에 장 파일의 옛 번호 리터럴 검사(경고)를 더한다: 「정리 6.23」처럼 라벨 밖에 적힌 진술 번호는
조립 뒤 다른 진술을 가리킬 수 있다(독해 1의 지적 9)."""
import io


def rw(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


p = "임시/주차함수_증명/scripts/조립.py"
s = rw(p)
old = '''    for name in PARTS:
        if name in texts:
            pieces.append("\\n" + texts[name])'''
assert s.count(old) == 1, s.count(old)
new = '''    for name in PARTS:
        if name in texts:
            pieces.append("\\n" + texts[name])
    # 장 파일의 옛 번호 리터럴 검사: 라벨·기록 이름 괄호·문헌 표기 밖의 「정리 x.y」는 조립 뒤 다른 진술을 가리킬 수 있다
    literal_warnings = []
    for name, text in texts.items():
        for ln_no, ln in enumerate(text.split("\\n"), 1):
            for m in LITERAL_RE.finditer(ln):
                before = ln[max(0, m.start() - 40): m.start()]
                if "{{old:" in ln[max(0, m.start() - 6): m.start()] or "기록 [" in before or "의 " == ln[max(0, m.start() - 2): m.start()] and "기록" in before:
                    continue
                literal_warnings.append(f"{name}:{ln_no}: 옛 번호 리터럴 '{m.group(0)}' (라벨이어야 하면 고칠 것) … {ln[max(0, m.start() - 30): m.end() + 20]}")
    if literal_warnings:
        print(f"[경고: 라벨 밖 진술 번호 {len(literal_warnings)}건 — 문헌·기록 번호 언급이면 정상]")
        for w in literal_warnings:
            print(" ", w)'''
s = s.replace(old, new)
old2 = 'CHAPTER_RE = re.compile(r"^## (\\d+)\\.")'
assert s.count(old2) == 1
s = s.replace(old2, old2 + '\nLITERAL_RE = re.compile(r"(?<!\\{\\{old:)(정리|명제|보조정리|따름정리|정의) \\d+\\.\\d+(?!\\}\\})")')
wr(p, s)
print("조립: 옛 번호 리터럴 검사 추가")
