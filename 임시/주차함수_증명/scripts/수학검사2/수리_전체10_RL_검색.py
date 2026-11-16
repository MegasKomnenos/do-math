# -*- coding: utf-8 -*-
"""RL 수리용 읽기 전용 검색 도구(2026-11-16): 장 파일의 $…$ 안에서 장식 없는 이탤릭 글자의 출현을 센다.
사용: python -I 수리_전체10_RL_검색.py <장파일> <글자> [<글자>...]
"""
import io, re, sys
ROOT = r"C:\math\임시\주차함수_증명\장v2"
FONT = r"(?:mathfrak|mathrm|mathsf|mathcal|mathbb|mathscr|text|operatorname|mathbf)"


def italic_hits(text, letter):
    hits = []
    for m in re.finditer(r"\$([^$]+)\$", text):
        s = m.group(1)
        s2 = re.sub("\\\\" + FONT + r"\s*\{[^{}]*\}", "", s)
        s2 = re.sub("\\\\" + FONT + r"\s*[A-Za-z]", "", s2)
        s2 = re.sub(r"\\[A-Za-z]+", " ", s2)
        if re.search(r"(?<![A-Za-z])" + re.escape(letter) + r"(?![A-Za-z])", s2):
            hits.append(s[:110])
    return hits


if __name__ == "__main__":
    f = sys.argv[1]
    t = io.open(ROOT + "\\" + f, encoding="utf-8").read()
    for L in sys.argv[2:]:
        h = italic_hits(t, L)
        print(f"{f} italic {L}: {len(h)}")
        for x in h[:8]:
            print("   ", repr(x))
