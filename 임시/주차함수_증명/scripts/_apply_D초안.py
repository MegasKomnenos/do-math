# -*- coding: utf-8 -*-
"""이식 에이전트가 쓴 D 항목 초안(`D항목_초안.md`의 ```markdown 울타리 안 `### D.{{D:…}}` 블록)으로 부록 D 조각의 같은 라벨 블록을 바꾸고,
지정한 본문 조각의 머리 줄에서 괄호 등급 낱말을 바꾼다. 멱등.
사용: python scripts/_apply_D초안.py <초안.md> <부록D 조각> [--heads <본문 조각> <라벨> ...] [--old-grade <머리의 옛 등급 낱말>] [--dry]"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_GRADE = "배정밀도 평가, 인증 아님"
NEW_GRADE = "방향 반올림 구간"


def main():
    global OLD_GRADE
    argv = list(sys.argv[1:])
    if "--old-grade" in argv:
        k = argv.index("--old-grade"); OLD_GRADE = argv[k + 1]; del argv[k:k + 2]
    args = [a for a in argv if a != "--dry"]
    dry = "--dry" in sys.argv
    draft, target = args[0], args[1]
    heads = []
    if "--heads" in args:
        k = args.index("--heads")
        heads = args[k + 1:]
    d = io.open(os.path.join(ROOT, draft), encoding="utf-8").read()
    m = re.search(r"```markdown\n(### D\.\{\{D:([^}]+)\}\}.*?)\n```", d, re.S)
    if m:
        blk, label = m.group(1).rstrip("\n"), m.group(2)
    else:
        # 울타리 없는 초안: 첫 `### D.{{D:…}}` 줄부터 다음 `## ` 머리 앞까지(끝의 `---` 줄은 뺀다)
        m2 = re.search(r"\n(### D\.\{\{D:([^}]+)\}\}.*?)(?=\n## )", d, re.S)
        if not m2:
            print("초안에서 D 블록을 찾지 못함"); sys.exit(1)
        blk, label = m2.group(1), m2.group(2)
        blk = re.sub(r"(\n-{3,}\s*)+$", "", blk).rstrip("\n")
    p = os.path.join(ROOT, target)
    s = io.open(p, encoding="utf-8").read()
    head = "### D.{{D:" + label + "}}"
    i = s.find(head)
    if i < 0:
        print("대상에 라벨 없음:", label); sys.exit(1)
    j = s.find("\n### D.", i + 1)
    old = s[i:j] if j > 0 else s[i:]
    if old.rstrip("\n") == blk:
        print(f"{target}: D.{label} 이미")
    else:
        tail = "\n\n" if j > 0 else "\n"
        s2 = s[:i] + blk + tail + (s[j:].lstrip("\n") if j > 0 else "")
        print(f"{target}: D.{label} 블록 교체 ({len(old)}→{len(blk)}자)")
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="\n").write(s2)
    if heads:
        hp = os.path.join(ROOT, heads[0])
        t = io.open(hp, encoding="utf-8").read()
        lines = t.split("\n")
        n = 0
        for lab in heads[1:]:
            for idx, l in enumerate(lines):
                if l.startswith("**") and ("{{" + lab + "}}") in l.split("**")[1] if l.count("**") >= 2 else False:
                    if OLD_GRADE in l:
                        lines[idx] = l.replace(OLD_GRADE, NEW_GRADE); n += 1
                        print(f"{heads[0]}: {lab} 머리 등급 교체")
                    elif NEW_GRADE in l:
                        print(f"{heads[0]}: {lab} 이미")
                    else:
                        print(f"{heads[0]}: {lab} 머리에 등급 낱말 없음")
                    break
            else:
                print(f"{heads[0]}: {lab} 머리 줄 없음")
        if n and not dry:
            io.open(hp, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("(dry)" if dry else "기록함")


if __name__ == "__main__":
    main()
