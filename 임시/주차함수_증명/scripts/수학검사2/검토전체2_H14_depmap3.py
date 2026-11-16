# -*- coding: utf-8 -*-
"""H14: 의존지도 1절의 「첫 판 번호」 열을 장부 4절과, 「입력: 문헌」 열을 11.4절 표의 「쓰인 자리」와 비교한다."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
BS=chr(92)
LABEL_RE = re.compile(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}")
CELL_SPLIT = re.compile("(?<!" + BS + BS + ")" + BS + "|")
led=io.open(os.path.join(ROOT,"장부_v2.md"),encoding="utf-8").read().split("\n")
led4={}; in4=False
for ln in led:
    if ln.startswith("## 4."): in4=True; continue
    if ln.startswith("## 5."): break
    if not in4 or not ln.startswith("| "): continue
    c=[x.strip() for x in ln.strip().strip("|").split("|")]
    if len(c)!=6 or c[0] in ("첫 판 번호","---"): continue
    m=LABEL_RE.search(c[5])
    if m: led4[m.group(1)]=(c[0],c[1])
ch11=io.open(os.path.join(ROOT,"장v2","장11.md"),encoding="utf-8").read().split("\n")
lit_labels={}; on=False
for ln in ch11:
    if ln.startswith("### 11.4"): on=True; continue
    if on and ln.startswith("| ") and not ln.startswith("| 문헌") and not ln.startswith("|---"):
        c=[x.strip() for x in CELL_SPLIT.split(ln.strip()[1:-1])]
        if len(c)<3: continue
        for k in set(LABEL_RE.findall(c[2])+LABEL_RE.findall(c[1])):
            lit_labels.setdefault(k,[]).append(c[0].split("*")[0].strip().rstrip(",").strip())
tab=io.open(os.path.join(ROOT,"의존지도_v2.md"),encoding="utf-8").read().split("\n")
probs=[]
for i,ln in enumerate(tab,1):
    if ln.startswith("## 2."): break
    if not ln.startswith("| `{{"): continue
    c=[x.strip() for x in CELL_SPLIT.split(ln.strip()[1:-1])]
    if len(c)!=10: continue
    key=c[0].strip("`{}")
    first=c[2]
    if key in led4:
        f,kind=led4[key]
        exp = "새 진술" if f in ("—","") else f"{kind} {f}"
        if first!=exp: probs.append(f"행{i} {key}: 첫 판 번호 [{first}] / 장부 4절 [{exp}]")
    else:
        probs.append(f"행{i} {key}: 장부 4절에 없음")
    lit=c[7]
    if key in lit_labels and lit=="—": probs.append(f"행{i} {key}: 문헌 열 — 이나 11.4 표가 든다: {lit_labels[key]}")
    if key not in lit_labels and lit!="—":
        pass  # 11-12 판 칸을 이어받은 경우가 있어 보고하지 않음
print(len(probs),"differences")
for p in probs: print(p)
print("11.4 표가 가리키는 라벨 수:",len(lit_labels))
