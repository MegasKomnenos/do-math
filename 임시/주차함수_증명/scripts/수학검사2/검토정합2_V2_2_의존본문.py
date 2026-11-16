# -*- coding: utf-8 -*-
"""정합 검토 2차 V2: 오늘 「…에 의존」이 바뀐 머리마다, 선언한 라벨을 증명 본문이 어느 문장에서 부르는지 뽑는다. 읽기만 한다.
또 이전 사본에서 †가 있는 증명의 머리(표지 없던 것)를 세어 37과 견준다.
사용: python -I scripts/수학검사2/검토정합2_V2_2_의존본문.py"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
M = importlib.import_module("검토정합2_V2_1_머리")

CHANGED = ["5:old-5-7", "5:old-5-12", "5:old-5-11", "5:old-5-15", "5:kernel-sandwich", "5:old-5-18",
           "7:green-atom", "7:vertical-nu", "7:theorem-C-moment", "7:hazard-floor", "7:integer-strips",
           "9:old-7-25", "9:old-7-28", "9:old-7-30", "9:old-7-31", "9:old-7-32", "9:old-7-33", "9:old-7-39", "9:old-7-35", "9:old-7-45", "9:old-7-44",
           "10:old-8-37", "10:old-8-8", "10:old-8-10", "10:old-8-14", "10:reduction-ga"]


def main():
    cur = M.parse(M.CUR)
    old = M.parse(M.OLD, fallback=M.CUR)
    for k in CHANGED:
        s = cur[k]; o = old.get(k)
        decl = M.deps_of(s["bracket"])
        odecl = M.deps_of(o["bracket"]) if o else set()
        print(f"\n######## {k} [{s['file']}:{s['line']}] 본문 {len(s['body_strict'])}줄" + (f" (미룬 증명 {s.get('defer')})" if s.get("defer") else ""))
        print("  전:", o["bracket"] if o else "-")
        print("  후:", s["bracket"])
        print("  더함:", sorted(decl - odecl), "뺌:", sorted(odecl - decl))
        for d in sorted(decl):
            hits = [ln for ln in s["body_strict"] if "{{" + d + "}}" in ln]
            tag = "더함" if d in decl - odecl else "기존"
            xflag = "X" if (d in cur and M.is_X(cur[d])) else "비X"
            print(f"  - {d} ({tag}, {xflag}; {cur[d]['kind'] if d in cur else '?'}): 본문 인용 {len(hits)}줄")
            for h in hits[:4]:
                i = h.find("{{" + d + "}}")
                print("      …" + h[max(0, i - 160):i + 120].replace("\n", " ") + "…")
        # 뺀 것은 본문에 남아 있는가
        for d in sorted(odecl - decl):
            hits = [ln for ln in s["body_strict"] if "{{" + d + "}}" in ln]
            print(f"  - (뺌) {d}: 본문 인용 {len(hits)}줄" + ("" if not hits else " — " + hits[0][max(0, hits[0].find('{{' + d) - 120):hits[0].find('{{' + d) + 80]))
        # 본문이 부르는 X형 가운데 선언 없는 것
        xs = {u for u in s["labels_strict"] if u in cur and M.is_X(cur[u]) and cur[u]["kind"] != "정의"}
        if xs - decl:
            print("  ! 본문이 부르는 X형인데 선언 없음:", sorted(xs - decl))
            for d in sorted(xs - decl):
                for h in [ln for ln in s["body_strict"] if "{{" + d + "}}" in ln][:2]:
                    i = h.find("{{" + d + "}}")
                    print("      …" + h[max(0, i - 160):i + 100] + "…")
    # 이전 사본에서 †가 있는 증명의 머리(표지 없던 것)
    print("\n######## 이전 사본: †가 있는 증명인데 머리에 표지 없던 것")
    cand = sorted((k for k, s in old.items() if s["dagger_strict"] and "작성자 판단" not in s["bracket"]), key=lambda k: old[k]["order"])
    print(len(cand), cand)
    now_flag = {k for k, s in cur.items() if "작성자 판단" in s["bracket"]}
    old_flag = {k for k, s in old.items() if "작성자 판단" in s["bracket"]}
    print("오늘 더한 표지:", len(now_flag - old_flag), sorted(now_flag - old_flag, key=lambda k: cur[k]["order"]))
    print("후보인데 표지 없음:", [k for k in cand if k not in now_flag])
    print("표지 더했는데 후보 아님:", sorted((now_flag - old_flag) - set(cand)))


if __name__ == "__main__":
    main()
