"""15차 수리 GL — 장 파일의 수식 구간에서 맨 글자(첨자·장식 없는 이탤릭 한 글자)의 출현을 센다.
용법: python -I 수리전체15_GL_글자셈.py <글자> <파일>...
"""
import re
import sys

FONT_CMDS = {"mathrm", "mathsf", "mathcal", "mathfrak", "operatorname", "text", "mathbf", "textrm", "mathscr", "mathbb"}


def math_segs(text):
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"\$\$(.+?)\$\$|\$(.+?)\$", line):
            out.append((i, m.group(1) or m.group(2)))
    return out


def enclosing_cmd(seg, pos):
    depth = 0
    for j in range(pos - 1, -1, -1):
        c = seg[j]
        if c == "}":
            depth += 1
        elif c == "{":
            if depth == 0:
                mm = re.search(r"\\([A-Za-z]+)$", seg[:j])
                return mm.group(1) if mm else None
            depth -= 1
    return None


def bare(letter, seg):
    pat = re.compile(r"(?<![A-Za-z\\])" + re.escape(letter) + r"(?![A-Za-z_^])")
    spaced_font = re.compile(r"\\(" + "|".join(sorted(FONT_CMDS)) + r")\s+$")
    hits = []
    for m in pat.finditer(seg):
        if enclosing_cmd(seg, m.start()) in FONT_CMDS:
            continue
        if spaced_font.search(seg[: m.start()]):
            continue
        hits.append(m.start())
    return hits


def main():
    letter = sys.argv[1]
    for f in sys.argv[2:]:
        txt = open(f, encoding="utf-8").read()
        n = 0
        for i, s in math_segs(txt):
            h = bare(letter, s)
            if h:
                n += len(h)
                print(f"{f}:{i}: {s[:140]}")
        print(f"TOTAL {f} {letter!r} {n}")


if __name__ == "__main__":
    main()
