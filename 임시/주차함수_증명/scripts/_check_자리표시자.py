# -*- coding: utf-8 -*-
"""결정 90의 자리표시자 `[Dn:이름]`이 장 조각·부록 D·조립본에 남아 있는지 센다. 0이면 통과(exit 0), 남아 있으면 자리를 적고 exit 1.
사용: python -I scripts/_check_자리표시자.py [--list]"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r"\[D\d+:[^\]\n]{1,40}\]")


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [os.path.join(ROOT, "원고.md"),
                                                                      os.path.join(ROOT, "원고_자료", "README.md"), os.path.join(ROOT, "원고_자료", "재실행표.md")]
    total = 0
    for p in files:
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding="utf-8").read()
        hits = [(s.count("\n", 0, m.start()) + 1, m.group()) for m in PAT.finditer(s)]
        if hits:
            total += len(hits)
            print(os.path.relpath(p, ROOT), len(hits), sorted({h[1] for h in hits}))
            if "--list" in sys.argv:
                for ln, tok in hits:
                    print("  ", ln, tok)
    print("자리표시자", total)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
