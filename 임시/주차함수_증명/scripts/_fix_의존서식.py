# -*- coding: utf-8 -*-
"""지위 표지의 의존 목록 서식을 세션 결정 60의 한 꼴로 맞춘다(기계적 부분만).

- 「정리 {{A}}·정리 {{B}}·명제 {{C}}에 의존」 → 「정리 {{A}}·{{B}}·명제 {{C}}에 의존」 (같은 유형 낱말의 되풀이 제거)
- 「정리 {{A}}과 보조정리 {{B}}에 의존」 → 「정리 {{A}}·보조정리 {{B}}에 의존」 (「과」→「·」)
대상: 장v2/장*.md의 진술 머리 줄. 내용(어떤 X를 드는가)은 바꾸지 않는다. `--dry`로 미리 본다.
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAP = os.path.join(ROOT, "장v2")
DRY = "--dry" in sys.argv
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{\d+:[A-Za-z0-9\-]+\}\}.*\[(.*?)\]\.\*\*")
TYPES = r"(?:정의|정리|명제|보조정리|따름정리)"
LABEL = r"\{\{\d+:[A-Za-z0-9\-]+\}\}"
DEP = re.compile(r"((?:%s \{\{[^}]+\}\}[^,;\[\]]*?)에 의존)" % TYPES)


def normalize(dep):
    body = dep[: -len("에 의존")]
    body = re.sub(r"(%s)과 (%s)" % (LABEL, TYPES), r"\1·\2", body)
    # 같은 유형 낱말의 되풀이: 「정리 L·정리 L」 → 「정리 L·L」
    changed = True
    while changed:
        new = re.sub(r"(%s) (%s(?:·%s)*)·\1 (%s)" % (TYPES, LABEL, LABEL, LABEL), r"\1 \2·\3", body)
        changed = new != body
        body = new
    return body + "에 의존"


def main():
    total = 0
    for p in sorted(glob.glob(os.path.join(CHAP, "장*.md"))):
        s = io.open(p, encoding="utf-8").read()
        lines = s.split("\n")
        n = 0
        for i, ln in enumerate(lines):
            if not HEAD.match(ln):
                continue
            new = DEP.sub(lambda m: normalize(m.group(1)), ln)
            if new != ln:
                n += 1
                print(f"{os.path.basename(p)}:{i+1}")
                print("  -", ln[:200])
                print("  +", new[:200])
                lines[i] = new
        if n and not DRY:
            io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        total += n
    print(f"{'(dry) ' if DRY else ''}고친 머리 {total}")


if __name__ == "__main__":
    main()
