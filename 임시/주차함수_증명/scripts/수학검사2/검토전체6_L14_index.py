# -*- coding: utf-8 -*-
"""L14 검토용 색인: 장 파일의 진술 머리·절·라벨 인용을 모아 JSON으로 저장한다.
사용: python -I 검토전체6_L14_index.py
출력: scripts/수학검사2/_검토전체6_L14_index.json (보고에 쓰는 중간 자료)
"""
import re, json, sys, os
from pathlib import Path

ROOT = Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
ORDER = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10", "장11"]
APPX = ["부록A", "부록B", "부록C"] + [f"부록D_{c}" for c in ["장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]]

HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|보조명제|관찰|주장)\s+(\{\{(\d+):([^}]+)\}\})(.*?)\*\*", re.S)
SEC = re.compile(r"^(#{2,4})\s+(\S+)\s*(.*)$")
LABEL = re.compile(r"\{\{(\d+|D):([^}]+)\}\}")

def parse_head(line):
    m = HEAD.match(line)
    if not m:
        return None
    kind, lab, chap, name, rest = m.groups()
    if rest.lstrip().startswith("의 증명"):
        return None  # 뒤로 미룬 증명의 머리
    # 이름 괄호와 지위 대괄호
    title = None
    status = None
    mt = re.match(r"\s*\((.*?)\)\s*(\[.*\])?\s*\.?\s*$", rest, re.S)
    if mt:
        title = mt.group(1)
        if mt.group(2):
            status = mt.group(2)[1:-1]
    else:
        mb = re.search(r"\[(.*)\]\s*\.?\s*$", rest, re.S)
        if mb:
            status = mb.group(1)
    return dict(kind=kind, label=lab, chap=chap, name=name, title=title, status=status, rest=rest.strip())

def main():
    out = {"files": {}, "heads": [], "labels_all": {}}
    for f in ORDER + APPX:
        p = CH / f"{f}.md"
        lines = p.read_text(encoding="utf-8").splitlines()
        secs = []
        heads = []
        cur_sec = None
        for i, ln in enumerate(lines, 1):
            ms = SEC.match(ln)
            if ms:
                cur_sec = ms.group(2)
                secs.append(dict(line=i, level=len(ms.group(1)), num=ms.group(2), title=ms.group(3)))
            h = parse_head(ln)
            if h:
                h.update(file=f, line=i, sec=cur_sec)
                heads.append(h)
            for lm in LABEL.finditer(ln):
                key = "{{%s:%s}}" % (lm.group(1), lm.group(2))
                out["labels_all"].setdefault(key, []).append(f"{f}:{i}")
        out["files"][f] = dict(nlines=len(lines), secs=secs, heads=heads)
        out["heads"].extend(heads)
    # 번호 매김: 장별로 머리 순서
    counters = {}
    for h in out["heads"]:
        c = h["chap"]
        counters[c] = counters.get(c, 0) + 1
        h["number"] = f"{c}.{counters[c]}"
    (ROOT / "scripts/수학검사2/_검토전체6_L14_index.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("heads:", len(out["heads"]))
    for f in ORDER:
        print(f, len(out["files"][f]["heads"]), [s["num"] for s in out["files"][f]["secs"] if s["level"] == 3])

if __name__ == "__main__":
    main()
