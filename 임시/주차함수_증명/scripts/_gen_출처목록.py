# -*- coding: utf-8 -*-
"""장별 명세(파견/명세v2/장N.json)의 모든 출처 좌표를 한 목록으로 뽑는다.

사전의 기록 대조 파견이 「들어올 기호의 완전성」을 볼 때 열어야 하는 절의 전수 목록이다.
출력: 파견/명세v2_출처목록.md — 기록 식별자별로 (파일, 절 또는 행 범위, 해소된 행 범위, 쓰는 라벨) 표.
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(ROOT, "파견", "명세v2")
sys.path.insert(0, HERE)
import importlib
gen = importlib.import_module("_gen_장v2_파견문")

rows = {}
for ch in range(1, 12):
    spec = json.load(io.open(os.path.join(SPEC, f"장{ch}.json"), encoding="utf-8"))
    for sec in spec["sections"]:
        for it in sec["items"]:
            for s in it.get("sources", []):
                try:
                    path = gen.source_path(s)
                    rng, how = gen.source_range(s, path)
                except FileNotFoundError:
                    rng, how = None, "폴더 없음"
                key = (s["record"], s.get("file", "exposition.md"), str(s.get("sec") or s.get("range")))
                rows.setdefault(key, {"range": rng, "labels": set(), "secs": set()})
                rows[key]["labels"].add(it["label"])
                rows[key]["secs"].add(sec["sec"])

out = ["# 둘째 판 명세의 출처 좌표 전수 목록\n",
       "장별 명세 열하나의 모든 출처(기록, 파일, 절 또는 행 범위)를 기록 식별자 순으로 모았다. 「해소된 행」은 파견문 생성기가 기록 머리에서 푼 행 범위다. 집필자가 여는 절이 정확히 이 목록이다.\n",
       "| 기록 | 파일 | 절/행 | 해소된 행 | 둘째 판 절 | 라벨 |", "|---|---|---|---|---|---|"]
for (rec, f, sec), v in sorted(rows.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
    rng = f"{v['range'][0]}–{v['range'][1]}" if v["range"] else "미해소"
    out.append(f"| [{rec}] | `{f}` | {sec} | {rng} | {', '.join(sorted(v['secs']))} | {', '.join('`'+l+'`' for l in sorted(v['labels']))} |")
out.append(f"\n출처 좌표 {len(rows)}개, 기록 {len({k[0] for k in rows})}개.\n")
P = os.path.join(ROOT, "파견", "명세v2_출처목록.md")
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("written", P, len(rows), "rows,", len({k[0] for k in rows}), "records")
