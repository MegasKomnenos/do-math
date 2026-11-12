# -*- coding: utf-8 -*-
"""부록 B의 재료: 장 파일(과 부록 A·C가 있으면 그것들)에 나오는 식별자 전부를 모아
기록 폴더·공표 시각(한국 표준시)·record.json의 title을 표로 낸다.

사용: python 부록B_자료.py [--out 경로]   (저장소 루트에서)
출력: Markdown 표(식별자 | 공표 시각 | 제목 전문 | 폴더). 부록 B 집필자는 제목을 한 줄로 줄여 쓴다.
"""
import argparse
import datetime
import glob
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KNOW = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge"
KST = datetime.timezone(datetime.timedelta(hours=9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "대조", "부록B_자료.md"))
    args = ap.parse_args()
    ids = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "장", "*.md"))):
        name = os.path.basename(path)
        if name in ("부록B.md",):
            continue
        text = io.open(path, encoding="utf-8").read()
        for br in re.finditer(r"\[([^\]]*)\]", text):
            for tok in re.findall(r"(?<![0-9a-zA-Z])r[0-9a-f]{7}(?![0-9a-zA-Z])", br.group(1)):
                ids.setdefault(tok, set()).add(name)
    dirs = os.listdir(os.path.join(KNOW, "records"))
    rows = []
    missing = []
    for rid in sorted(ids):
        match = [d for d in dirs if d.startswith(rid)]
        if len(match) != 1:
            missing.append((rid, match))
            continue
        d = match[0]
        rec = json.load(io.open(os.path.join(KNOW, "records", d, "record.json"), encoding="utf-8"))
        ev_path = os.path.join(KNOW, "events", d + ".json")
        at = None
        if os.path.exists(ev_path):
            at = json.load(io.open(ev_path, encoding="utf-8")).get("at")
        when = datetime.datetime.fromtimestamp(at, KST).strftime("%m-%d %H:%M") if at else "(사건 파일 없음)"
        rows.append((at or 0, rid, when, rec.get("title", "").replace("|", "／").replace("\n", " "), d, ", ".join(sorted(ids[rid]))))
    rows.sort()
    out = ["# 부록 B 재료(스크립트 산출; 공표 시각 순)", "",
           f"식별자 {len(rows)}개. 장 파일의 `[rXXXXXXX]` 전부. 시각은 events/<폴더>.json의 at(유닉스 초)을 UTC+9로 바꾼 것.", "",
           "| 식별자 | 공표 시각(KST) | record.json title(전문) | 폴더 | 인용한 장 파일 |", "|---|---|---|---|---|"]
    for at, rid, when, title, d, files in rows:
        out.append(f"| {rid} | {when} | {title} | {d} | {files} |")
    if missing:
        out += ["", "## 폴더를 찾지 못한 식별자"] + [f"- {rid}: {m}" for rid, m in missing]
    io.open(args.out, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print(f"식별자 {len(rows)}개, 미해결 {len(missing)}개 → {args.out}")
    for rid, m in missing:
        print("  미해결:", rid, m)


if __name__ == "__main__":
    main()
