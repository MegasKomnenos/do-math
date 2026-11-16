# -*- coding: utf-8 -*-
"""R5: 부록 D 자료 줄이 가리키는 세션_재계산 파일(맨이름 해석 포함)이 README 「세션이 만든 수정판」 표에 있는가. 읽기만 한다."""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토정합_R5_추출 import parse_D  # noqa: E402
from 검토정합_R5_자료 import parse_readme, DATA, INPROG  # noqa: E402


def main():
    items, order = parse_D()
    sess, files = parse_readme()
    total = 0
    for lab in order:
        mat = items[lab]["fields"].get("자료", (0, ""))[1]
        toks = re.findall(r"`([^`]+)`", mat)
        curdir = None
        out = []
        for t in toks:
            t = t.strip()
            if t.startswith("원고_자료/"):
                rel = t[len("원고_자료/"):]
                curdir = rel if rel.endswith("/") else os.path.dirname(rel)
                if not rel.endswith("/") and os.path.isfile(os.path.join(DATA, rel)) and rel not in sess:
                    out.append(rel)
                continue
            if t.startswith("records/"):
                curdir = None
                continue
            if curdir and re.search(r"\.[A-Za-z0-9]{1,5}$", t) and " " not in t and "…" not in t and "*" not in t:
                cands = [os.path.join(curdir, t)] + glob.glob(os.path.join(DATA, curdir, "**", t), recursive=True)
                cands = [os.path.relpath(c if os.path.isabs(c) else os.path.join(DATA, c), DATA).replace("\\", "/") for c in cands]
                cands = [c for c in cands if os.path.isfile(os.path.join(DATA, c))]
                if cands and not any(c in sess for c in cands):
                    out.append(cands[0])
        if out:
            inprog = any(x.rstrip("/") in o for o in out for x in INPROG)
            total += len(out)
            print(lab, "(계산 중 폴더 포함)" if inprog else "", len(out), out)
    print("합계", total)


if __name__ == "__main__":
    main()
