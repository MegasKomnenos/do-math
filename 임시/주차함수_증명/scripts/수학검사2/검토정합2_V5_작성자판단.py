# -*- coding: utf-8 -*-
"""V5 (ㅂ): 「작성자 판단」 머리 수의 전후 비교(사본 대 현재), 지운 라벨 고려."""
import io, os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
def heads(path):
    out = {}
    for l in io.open(path, encoding="utf-8"):
        m = HEAD.match(l)
        if m:
            out[f"{m.group(2)}:{m.group(3)}"] = (m.group(1), "작성자 판단" in l)
    return out
cur = {}
for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "장*.md"))):
    cur.update(heads(p))
pre = {}
for p in sorted(glob.glob(os.path.join(ROOT, "대조v2", "수학검사2", "전_정합1114", "장*.md"))):
    if os.path.basename(p) == "장부_v2.md": continue
    pre.update(heads(p))
for n in ("장4.md", "장8.md"):
    pre.update(heads(os.path.join(ROOT, "장v2", n)))
print("현재 머리", len(cur), "정의 제외", sum(1 for k,v in cur.items() if v[0] != "정의"))
print("사본 머리", len(pre), "정의 제외", sum(1 for k,v in pre.items() if v[0] != "정의"))
print("지워진 라벨", sorted(set(pre) - set(cur)))
print("새 라벨", sorted(set(cur) - set(pre)))
cur_f = {k for k,v in cur.items() if v[1]}
pre_f = {k for k,v in pre.items() if v[1]}
print("현재 작성자 판단", len(cur_f), "사본 작성자 판단", len(pre_f), "사본 중 지워진 것", sorted(pre_f - set(cur)))
print("새로 단 머리", len(cur_f - pre_f), sorted(cur_f - pre_f))
print("뺀 머리", sorted(pre_f - cur_f - (set(pre)-set(cur))))
