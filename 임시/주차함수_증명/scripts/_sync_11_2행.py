# -*- coding: utf-8 -*-
"""11.2 표(장v2/장11.md)의 지정한 행만 부록 D 조각과 맞춘다: 여섯째 칸(독립 재계산)을 그 항목의 **독립 재계산.** 줄에서
꺾쇠 요약을 뺀 전문으로 바꾼다(손으로 채운 다른 행은 건드리지 않는다). 수식 안의 `|`는 `\\vert `로 바꾼다(`_gen_11_2표.py`와 같음).
사용: python -I scripts/_sync_11_2행.py <라벨> [<라벨> ...]   (예: critical-window-rig bprime-boxes band-boxes)"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAP = os.path.join(ROOT, "장v2")
HEAD = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
PREFIX = re.compile(r"^\*\*독립 재계산\.\*\*\s*〔[^〕]*〕\s*")


def cell(s):
    # 11.2절 머리말의 약속: 부록 D 줄이 표 안의 자리를 가리키는 말은 표의 자리로 바꾼다.
    s = s.replace("이 문단 머리의 꺾쇠 괄호", "「재계산」 열의 꺾쇠 괄호")
    return re.sub(r"\$[^$]*\$", lambda m: m.group().replace("|", r"\vert "), s)


def recheck_of(name):
    for p in sorted(glob.glob(os.path.join(CHAP, "부록D_*.md"))):
        lines = io.open(p, encoding="utf-8").read().split("\n")
        on = False
        for l in lines:
            m = HEAD.match(l)
            if m:
                on = (m.group(1) == name)
                continue
            if on and l.startswith("**독립 재계산.**"):
                return PREFIX.sub("", l).strip()
    raise SystemExit("독립 재계산 줄 없음: " + name)


def main():
    names = sys.argv[1:]
    p = os.path.join(ROOT, "장v2", "장11.md")
    lines = io.open(p, encoding="utf-8").read().split("\n")
    n = 0
    for name in names:
        rc = cell(recheck_of(name))
        key = "| 부록 D.{{D:%s}} |" % name
        idx = [i for i, l in enumerate(lines) if l.startswith(key)]
        if len(idx) != 1:
            raise SystemExit("행 %d개: %s" % (len(idx), name))
        row = lines[idx[0]]
        j = row.find("〕 | ")
        if j < 0:
            raise SystemExit("꺾쇠 칸 없음: " + name)
        new = row[:j + len("〕 | ")] + rc + " |"
        if new != row:
            lines[idx[0]] = new
            n += 1
            print("갱신", name, len(row), "->", len(new))
        else:
            print("같음", name)
    io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("갱신 행", n)


if __name__ == "__main__":
    main()
