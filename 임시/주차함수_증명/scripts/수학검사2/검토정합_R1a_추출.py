# -*- coding: utf-8 -*-
"""R1a 정합 검토: 장1·2·3·4·5A·5B 진술 머리 ↔ 증명 본문 ↔ 부록 D·11장 표·장부 4절·부록 C. 읽기만 한다."""
import io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
import importlib.util
spec = importlib.util.spec_from_file_location("dd", os.path.join(ROOT, "scripts", "_의존_도달.py"))
dd = importlib.util.module_from_spec(spec); spec.loader.exec_module(dd)
BASE = os.path.join(ROOT, "장v2")
LABEL_RE = dd.LABEL_RE
MY_FILES = {"장1.md", "장2.md", "장3.md", "장4.md", "장5A.md", "장5B.md"}

stmts = dd.parse_chapters()
ditems = dd.parse_appendix_d()
dgrade = {}
for name in dd.chapter_files("부록D_장"):
    cur = None
    for ln in dd.read_lines(os.path.join(BASE, name)):
        m = dd.D_HEAD_RE.match(ln)
        if m:
            cur = m.group(1); continue
        if cur and ln.startswith("**산술 등급.**"):
            dgrade[cur] = ln[len("**산술 등급.**"):].strip()

def status_of(head):
    m = re.search(r"\[([^\[\]]*)\]\.\*\*", head)
    return m.group(1) if m else ""

def name_of(head):
    m = dd.NAME_RE.match(head)
    return m.group(1) if m else ""

EXT = re.compile(r"계산 증거|계산 보조|문헌 인용|에 의존")
def is_ext(key):
    s = stmts.get(key)
    return bool(s and EXT.search(status_of(s["head"])))

def body_text(key):
    s = stmts[key]
    lines = dd.read_lines(os.path.join(BASE, s["file"]))
    txt = "\n".join(lines[s["line"]:s["body_end"]])
    for d in s.get("defer", []):
        f, ln = d.rsplit(":", 1); ln = int(ln)
        L = dd.read_lines(os.path.join(BASE, f))
        end = len(L)
        for t in range(ln, len(L)):
            if dd.HEAD_RE.match(L[t]) or dd.DEFER_RE.match(L[t]):
                end = t; break
        txt += "\n" + "\n".join(L[ln-1:end])
    return txt

L11 = dd.read_lines(os.path.join(BASE, "장11.md"))
sec = None; rows112 = []; rows113 = []; rows114 = []
for ln in L11:
    if ln.startswith("### 11.2"):
        sec = "2"; continue
    if ln.startswith("### 11.3"):
        sec = "3"; continue
    if ln.startswith("### 11.4"):
        sec = "4"; continue
    if ln.startswith("|") and not ln.startswith("|---"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if sec == "2" and cells[0].startswith("부록 D."):
            rows112.append(cells)
        elif sec == "3":
            rows113.append(cells)
        elif sec == "4":
            rows114.append(cells)

def table_rows(path, start_pat, stop_pat):
    on = False; out = []
    for ln in dd.read_lines(path):
        if re.match(start_pat, ln):
            on = True; continue
        if on and re.match(stop_pat, ln):
            break
        if on and ln.startswith("|") and not ln.startswith("|---"):
            out.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return out

ledger4 = table_rows(os.path.join(ROOT, "장부_v2.md"), r"^## 4\. ", r"^## 5\. ")
appC = table_rows(os.path.join(BASE, "부록C.md"), r"^### 기록이 결과에 붙인 이름", r"^### 기록의 글자")
l4_by_label = {}
for r in ledger4:
    if len(r) >= 6:
        m = LABEL_RE.search(r[5])
        if m:
            l4_by_label[f"{m.group(1)}:{m.group(2)}"] = r
c_by_label = {}
for r in appC:
    if len(r) >= 3:
        m = LABEL_RE.search(r[1])
        if m:
            c_by_label.setdefault(f"{m.group(1)}:{m.group(2)}", []).append(r)

mine = [k for k, s in stmts.items() if s["file"] in MY_FILES]
mine.sort(key=lambda k: stmts[k]["order"])
print(f"내 영역 진술 수: {len(mine)}  (전체 {len(stmts)}); D 항목 {len(ditems)}; 11.2 행 {len(rows112)}")

print("\n==== A. 머리 목록 ====")
for k in mine:
    s = stmts[k]
    print(f"{s['file']}:{s['line']} {s['kind']} {{{{{k}}}}} ({name_of(s['head'])}) [{status_of(s['head'])}]")

print("\n==== B1. 계산 보조·계산 증거 ↔ 부록 D·11.2 ====")
for k in mine:
    s = stmts[k]; st = status_of(s["head"])
    grades = re.findall(r"계산 (증거|보조)\(([^)]*)\)", st)
    dref = [d for d, it in ditems.items() if k in it["labels"]]
    r112 = [r for r in rows112 if k in r[1]]
    body = body_text(k)
    dl = sorted(set(re.findall(r"\{\{D:([A-Za-z0-9\-]+)\}\}", body)))
    if grades or dref or r112 or dl:
        print(f"-- {{{{{k}}}}} {s['file']}:{s['line']} 머리: {st}")
        for d in dref:
            print(f"   D.{d} ({ditems[d]['file']}:{ditems[d]['line']}) 등급: {dgrade.get(d)}")
            print(f"      머리줄: {ditems[d]['title'][:160]}")
            print(f"      확인줄: {ditems[d]['verify'][:160]}")
        for r in r112:
            print(f"   11.2행: {r[0]} | {r[1]} | {r[2]} | {r[3]}")
        if grades and not dref:
            print("   !! 계산 표지가 있으나 D 항목 없음")
        if dref and not grades:
            print("   !! D 항목이 있으나 머리에 계산 표지 없음")
        if r112 and not grades:
            print("   !! 11.2 행이 있으나 머리에 계산 표지 없음")
        if dref and not r112:
            print("   !! D 항목이 있으나 11.2 행 없음")
        print(f"   본문의 D 인용: {dl}")

print("\n==== B2. 「에 의존」 선언 ↔ 본문 인용 ====")
for k in mine:
    s = stmts[k]; st = status_of(s["head"])
    decl = set()
    for dep in re.findall(r"([^;\[\]]*?에 의존)", st):
        decl.update(f"{a}:{b}" for a, b in LABEL_RE.findall(dep))
    body = body_text(k)
    cited = set(f"{a}:{b}" for a, b in LABEL_RE.findall(body)) - {k}
    ext_cited = {c for c in cited if is_ext(c)}
    undeclared = ext_cited - decl
    unused = decl - cited
    if decl or ext_cited:
        print(f"-- {{{{{k}}}}} {s['file']}:{s['line']} {s['kind']} ({name_of(s['head'])}) [{st[:70]}]")
        print(f"   선언: {sorted(decl)}")
        if unused:
            print(f"   !! 선언했으나 본문에 인용 없음: {sorted(unused)}")
        if undeclared:
            print("   ?? 본문이 인용하는 외부표지 진술인데 미선언: " + ", ".join(f"{c}[{status_of(stmts[c]['head'])[:70]}]" for c in sorted(undeclared)))

print("\n==== B3. 문헌 인용 ↔ 11.4 ====")
lab114 = {}
for r in rows114:
    for a, b in LABEL_RE.findall(" | ".join(r)):
        lab114.setdefault(f"{a}:{b}", []).append(r[0][:60])
for k in mine:
    st = status_of(stmts[k]["head"])
    if "문헌 인용" in st or k in lab114:
        print(f"-- {{{{{k}}}}} {stmts[k]['file']}:{stmts[k]['line']} 머리 문헌 인용={'문헌 인용' in st} / 11.4 행: {lab114.get(k)}")
print("11.4 표 전체 행:")
for r in rows114:
    print("   " + " | ".join(r)[:400])

print("\n==== B4. 작성자 판단 ↔ † ====")
for k in mine:
    s = stmts[k]; st = status_of(s["head"])
    body = body_text(k)
    has_dag = "†" in body
    if ("작성자 판단" in st) != has_dag:
        print(f"!! {{{{{k}}}}} {s['file']}:{s['line']} 머리 작성자판단={'작성자 판단' in st} 본문 †={has_dag}")
    elif "작성자 판단" in st:
        print(f"ok {{{{{k}}}}} {s['file']}:{s['line']} †수={body.count('†')}")
for f in sorted(MY_FILES):
    for i, ln in enumerate(dd.read_lines(os.path.join(BASE, f)), 1):
        if "†" in ln:
            print(f"   † 자리: {f}:{i}: {ln[:110]}")

print("\n==== B5. 머리 괄호 「기록 […]의 이름」 ↔ 장부 4절 ↔ 부록 C ====")
for k in mine:
    s = stmts[k]; nm = name_of(s["head"])
    m2 = re.search(r"[;,] *(기록 .*)$", nm) or re.search(r"\((기록 .*)\)$", nm)
    rec_txt = m2.group(1).strip() if m2 else ""
    this_name = nm[:m2.start()].strip() if m2 else nm
    l4 = l4_by_label.get(k); cs = c_by_label.get(k, [])
    probs = []
    if l4 is None:
        probs.append("장부4절에 행 없음")
    else:
        if (l4[3] or "") != rec_txt:
            probs.append(f"장부4절 기록이름 불일치: 장부=「{l4[3]}」 머리=「{rec_txt}」")
        if (l4[2] or "") != this_name:
            probs.append(f"장부4절 이글이름 불일치: 장부=「{l4[2]}」 머리=「{this_name}」")
        if l4[1] != s["kind"]:
            probs.append(f"장부4절 종류 불일치: {l4[1]} vs {s['kind']}")
        if l4[4] != s["section"]:
            probs.append(f"장부4절 절 불일치: {l4[4]} vs {s['section']}")
    if rec_txt:
        if not cs:
            probs.append("부록C 이름표에 행 없음")
        else:
            for c in cs:
                if c[0] != rec_txt:
                    probs.append(f"부록C 기록이름 불일치: C=「{c[0]}」 머리=「{rec_txt}」")
                if c[2] != this_name:
                    probs.append(f"부록C 이글이름 불일치: C=「{c[2]}」 머리=「{this_name}」")
                if not c[1].startswith(s["kind"]):
                    probs.append(f"부록C 종류 불일치: {c[1]} vs {s['kind']}")
    elif cs:
        probs.append(f"머리에 기록 이름 없는데 부록C에 행: {cs}")
    if probs:
        print(f"-- {{{{{k}}}}} {s['file']}:{s['line']} 괄호=「{nm}」")
        for p in probs:
            print("   !!", p)
for lab, r in l4_by_label.items():
    if lab.split(":")[0] in {"1", "2", "3", "4", "5"} and lab not in stmts:
        print(f"   장부4절 라벨이 장 파일에 없음: {lab} {r}")
for lab, rs in c_by_label.items():
    if lab.split(":")[0] in {"1", "2", "3", "4", "5"} and lab not in stmts:
        print(f"   부록C 라벨이 장 파일에 없음: {lab} {rs}")

print("\n==== B6. 뺀 개념 낱말 잔존(장1–5B) ====")
KW = ["102항", "꼬리 오목성", r"\bTC\b", "피벗", "문턱 예산", "예산 분해", "무게 성장", "동률의 나머지",
      r"\\mathcal E\b", r"\\mathcal\{E\}", "S∞", r"S_\\infty", "lm-core", "moment-band", "moment-window", "머묾 항등식",
      "젊은 경로", "cumulant-bounds", "mass-envelope", "old-5-29", "old-5-35", "old-5-36", "old-5-37", "old-2-42",
      "rational-cert", "sharp-546", "tail-poly", r"old-5-3\}", "old-5-6", "old-6-17", "V-core", "S-infinity",
      "체류", "판정 사슬", "블록", "윤곽 핵", "윤곽값", "멈춤 확률", "꼬리의 상한", "순증가"]
for f in sorted(MY_FILES):
    for i, ln in enumerate(dd.read_lines(os.path.join(BASE, f)), 1):
        for kw in KW:
            if re.search(kw, ln):
                print(f"{f}:{i} [{kw}] {ln[:170]}")

print("\n==== B7. 11.3 표 중 내 영역 라벨 ====")
for r in rows113:
    labs = [f"{a}:{b}" for a, b in LABEL_RE.findall(" | ".join(r))]
    if any(l.split(":")[0] in {"1", "2", "3", "4", "5"} for l in labs):
        print(" | ".join(r)[:400])

print("\n==== B8. 머리가 인용하는 라벨 중 정의되지 않은 것 ====")
for k in mine:
    s = stmts[k]
    for c in s["head_labels"] | s["body_labels"]:
        if c not in stmts:
            print(f"!! {{{{{k}}}}} {s['file']}:{s['line']} → 없는 라벨 {c}")
