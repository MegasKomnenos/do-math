# -*- coding: utf-8 -*-
"""R1b: 장6·7A·7B 진술마다 (1) 머리 선언 의존 라벨, (2) 본문이 인용하는 '오염' 라벨(계산 보조·계산 증거·문헌 인용·에 의존을 가진 진술),
(3) 선언했으나 본문이 인용하지 않는 라벨, (4) 본문이 인용하지만 선언하지 않은 오염 라벨, (5) 계산 보조 ↔ 부록 D 항목, (6) †와 작성자 판단. 읽기만."""
import io, os, re, sys
sys.path.insert(0, r"C:\math\임시\주차함수_증명\scripts")
from _의존_도달 import parse_chapters, parse_appendix_d, LABEL_RE, BASE
stmts = parse_chapters()
KEY = ("계산 보조", "계산 증거", "문헌 인용", "에 의존")
def status(s):
    m = re.search(r"\[(.*?)\]\.\*\*", s["head"])
    st = m.group(1) if m else ""
    return st.rsplit(";", 1)[0] if ";" in st else st
tainted = {k for k, s in stmts.items() if any(x in status(s) for x in KEY)}
ditems = parse_appendix_d()
d_by_label = {}
for nm, it in ditems.items():
    for l in it["labels"]:
        d_by_label.setdefault(l, []).append(nm)
# 부록 D 산술 등급
d_grade = {}
for nm, it in ditems.items():
    lines = io.open(os.path.join(BASE, it["file"]), encoding="utf-8").read().split("\n")
    g = ""
    for ln in lines[it["line"]:]:
        if ln.startswith("### D."):
            break
        if ln.startswith("**산술 등급.**") or ln.startswith("**산술.**"):
            g = ln
    d_grade[nm] = g
for k in sorted(stmts, key=lambda k: stmts[k]["order"]):
    if not (k.startswith("6:") or k.startswith("7:")):
        continue
    s = stmts[k]
    st = status(s)
    declared = set(s["head_labels"])
    body_t = s["body_labels"] & tainted
    undeclared = body_t - declared
    unused = declared - s["body_labels"]
    # 본문 텍스트에서 † 찾기
    lines = io.open(os.path.join(BASE, s["file"]), encoding="utf-8").read().split("\n")
    body = "\n".join(lines[s["line"]-1:s["body_end"]])
    dag = "†" in body
    print(f"\n{{{{{k}}}}} {s['kind']} [{st}] {s['file']}:{s['line']}")
    if declared: print("  선언:", ", ".join(sorted(declared)))
    if body_t: print("  본문 오염 인용:", ", ".join(sorted(body_t)))
    if undeclared: print("  !! 선언 없는 오염 인용:", ", ".join(sorted(undeclared)))
    if unused: print("  !! 선언했으나 본문 미인용:", ", ".join(sorted(unused)))
    if "계산 보조" in st or "계산 증거" in st:
        ds = d_by_label.get(k, [])
        print("  부록 D:", ", ".join(f"D:{d} [{d_grade[d]}]" for d in ds) if ds else "!! 없음")
    elif k in d_by_label:
        print("  !! 계산 표지 없는데 부록 D가 듦:", d_by_label[k])
    if ("작성자 판단" in st) != dag:
        print(f"  !! 작성자 판단={ '작성자 판단' in st }, †={dag}")
    if s["body_dlabels"]:
        print("  본문 D 인용:", ", ".join(sorted(s["body_dlabels"])))
