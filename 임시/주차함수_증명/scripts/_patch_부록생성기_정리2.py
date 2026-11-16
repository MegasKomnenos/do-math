# -*- coding: utf-8 -*-
"""부록 생성기 손질 둘째: preclean에 「— Qnn」 꼴을 더하고, 기록 글자 대응표의 첫·셋째 열에도 preclean을 적용한다. 멱등."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "scripts", "부록_v2.py")

OLD1 = '    text = re.sub(r"\\(Q\\d+\\)", "", text)\n'
NEW1 = OLD1 + '    text = re.sub(r"\\s*—\\s*Q\\d+(?=[;)])", "", text)\n'
OLD2 = '        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {clean(r[3]) or \'—\'} |")\n'
NEW2 = '        out.append(f"| {preclean(r[0])} | {r[1]} | {preclean(r[2])} | {clean(r[3]) or \'—\'} |")\n'


def main():
    s = io.open(P, encoding="utf-8").read()
    changed = False
    if NEW1 not in s:
        assert s.count(OLD1) == 1, s.count(OLD1)
        s = s.replace(OLD1, NEW1, 1)
        changed = True
        print("preclean: — Qnn 추가")
    if OLD2 in s:
        s = s.replace(OLD2, NEW2, 1)
        changed = True
        print("build_C: 7절 첫·셋째 열 preclean")
    if changed and "--dry" not in sys.argv:
        io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    elif not changed:
        print("이미 반영")


if __name__ == "__main__":
    main()
