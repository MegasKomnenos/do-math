# -*- coding: utf-8 -*-
"""부록 생성기 손질 셋째: preclean의 「; Qnn」 규칙을 「; Qnn·Qmm」 꼴까지 넓힌다. 멱등."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "scripts", "부록_v2.py")
OLD = '    text = re.sub(r";\\s*Q\\d+(?=[;)])", "", text)\n'
NEW = '    text = re.sub(r";\\s*Q\\d+(?:·Q\\d+)*(?=[;)])", "", text)\n'


def main():
    s = io.open(P, encoding="utf-8").read()
    if NEW in s:
        print("이미 반영")
        return
    assert s.count(OLD) == 1, s.count(OLD)
    if "--dry" not in sys.argv:
        io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(OLD, NEW, 1))
    print("preclean: Qnn·Qmm 꼴 추가")


if __name__ == "__main__":
    main()
