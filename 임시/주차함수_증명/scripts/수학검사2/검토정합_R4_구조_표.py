# -*- coding: utf-8 -*-
"""R4 구조·표의 정합 검사(읽기만; 파일을 고치지 않는다).

사용: python -I scripts/수학검사2/검토정합_R4_구조_표.py [부분...]
부분: 구조표 | 11_3 | 11_4 | 지도 | 부록C | 전부(기본)

(ㄱ) 구조표_v2.md ↔ 장 파일: 절 이름, 행이 든 라벨·첫 판 번호의 실재, 절별 진술 수.
(ㄴ) 11.3절 세 표: 라벨 실재, 계산 진술·등급 ↔ 머리, 닿는 계산 진술의 누락, 「쓰는 자리」의 인용 검증, 고리 번호.
(ㄷ) 11.4절 표: 라벨 실재, 「문헌 인용」 머리 ↔ 표, 저자 이름의 본문 자리 ↔ 표의 「쓰인 자리」.
(ㄹ) 1.4절·장 도입의 라벨 실재와 「X가 Y를 쓴다」 주장의 간선 검증(일부).
(ㅁ) 장부 4절 ↔ 장 파일 머리, 부록 C 기록 이름 표 ↔ build_C 생성본, 의존지도 1.1절 ↔ 장부 4절 뺌 행.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import _의존_도달 as DEP  # noqa: E402
import 부록_v2 as APP  # noqa: E402

BASE = os.path.join(ROOT, "장v2")
LABEL_RE = DEP.LABEL_RE
KINDS = "정의|정리|명제|보조정리|따름정리"


def read(path):
    return io.open(path, encoding="utf-8").read()


def lines(path):
    return read(path).split("\n")


def sec_titles():
    """장 파일의 '### N.M 이름' → {('N.M'): 이름}, 장 제목 {'N': 이름}."""
    out = {}
    chap = {}
    for name in DEP.chapter_files("장"):
        for ln in lines(os.path.join(BASE, name)):
            m = re.match(r"^### (\d+\.\d+) (.*)$", ln)
            if m:
                out[m.group(1)] = m.group(2).strip()
            m = re.match(r"^## (\d+)\. (.*)$", ln)
            if m:
                chap[m.group(1)] = m.group(2).strip()
    return out, chap


def head_info(head):
    """머리 줄에서 (이름, 기록 이름, 표지 전체, 계산 등급 목록, 문헌 인용 여부, 작성자 판단 여부)."""
    nm = DEP.NAME_RE.match(head)
    name = nm.group(1) if nm else ""
    rec = ""
    if "; 기록 [" in name:
        name, rec = name.split("; 기록 [", 1)
        rec = "기록 [" + rec
    elif name.startswith("기록 ["):
        rec, name = name, ""
    m = re.search(r"\[([^\]]*)\]\.\*\*", head)
    tag = m.group(1) if m else ""
    grades = re.findall(r"계산 (?:보조|증거)\(([^)]*)\)", tag)
    return name.strip(), rec.strip(), tag, grades, ("문헌 인용" in tag), ("작성자 판단" in tag)


def norm_grade(g):
    g = g.replace(";", ",")
    parts = [p.strip() for p in g.split(",")]
    parts = [p for p in parts if p in ("정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석") or "인증 아님" in p]
    return frozenset(parts)


# ------------------------------------------------------------------ (ㄱ) 구조표
def check_구조표(stmts):
    print("\n==================== (ㄱ) 구조표_v2.md ↔ 장 파일 ====================")
    titles, chaps = sec_titles()
    text = lines(os.path.join(ROOT, "구조표_v2.md"))
    by_sec = {}
    for k, s in stmts.items():
        by_sec.setdefault(s["section"], []).append(k)
    # 1) 절 이름
    print("\n-- 절 이름 비교(구조표 1열 ↔ 장 파일 ###) --")
    seen_secs = set()
    rows = []
    cur_chap = None
    for i, ln in enumerate(text, 1):
        m = re.match(r"^## (\d+)\. (.*)$", ln)
        if m:
            cur_chap = m.group(1)
            if chaps.get(cur_chap) != m.group(2).strip():
                print(f"  [장 제목 다름] 구조표:{i} 「{m.group(2).strip()}」 ↔ 장 파일 「{chaps.get(cur_chap)}」")
        if ln.startswith("| ") and re.match(r"^\| (\d+\.\d+) ", ln):
            cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
            sec, rest = cells[0].split(" ", 1)
            seen_secs.add(sec)
            rows.append((i, sec, rest, cells))
            if sec not in titles:
                print(f"  [절 없음] 구조표:{i} {sec} 「{rest}」 — 장 파일에 ### {sec} 없음")
            elif titles[sec] != rest:
                print(f"  [절 이름 다름] 구조표:{i} {sec} 「{rest}」 ↔ 장 파일 「{titles[sec]}」")
    for sec in sorted(titles, key=APP.sec_sort_key):
        if sec not in seen_secs:
            print(f"  [구조표에 없는 절] 장 파일 ### {sec} {titles[sec]}")
    # 2) 라벨·첫 판 번호
    print("\n-- 행이 든 라벨의 실재(없는 라벨 = 집필 중 대체·삭제) --")
    all_labels = set(stmts)
    for i, sec, rest, cells in rows:
        chap = sec.split(".")[0]
        row_text = " | ".join(cells[1:])
        labs = [f"{a}:{b}" for a, b in LABEL_RE.findall(row_text)]
        missing = [l for l in labs if l not in all_labels]
        if missing:
            print(f"  구조표:{i} {sec}: 없는 라벨 {missing}")
        # 첫 판 번호
        nums = set()
        col = cells[1] if len(cells) > 1 else ""
        # 범위 a.b–a.c
        for m in re.finditer(r"(\d+)\.(\d+)[–-](\d+)\.(\d+)", col):
            a, b, c, d = map(int, m.groups())
            if a == c and chap in (str(a), str(int(chap))):
                for x in range(b, d + 1):
                    nums.add((a, x))
        # 「첫 판 A.B」 꼴의 번호(출처 열에 있는 것은 뺌). 구조표 2·4·8·9·10장 표는 2열에 첫 판 번호를 직접 적는다.
        for m in re.finditer(r"(?<![\d.])(\d+)\.(\d+)(?![\d.])", re.sub(r"\{\{[^}]*\}\}", "", col)):
            a, b = int(m.group(1)), int(m.group(2))
            nums.add((a, b))
        # 뺌 표시된 번호
        removed_nums = set()
        for m in re.finditer(r"((?:\d+\.\d+(?:[·,]\s*)?)+)[^.|]{0,40}?뺌", col):
            for n2 in re.findall(r"(\d+)\.(\d+)", m.group(1)):
                removed_nums.add((int(n2[0]), int(n2[1])))
        exists_old = {k for k in by_sec.get(sec, []) if ":old-" in k}
        # 이 절의 old 라벨
        sec_old = set()
        for k in exists_old:
            m = re.match(r"\d+:old-(\d+)-(\d+)$", k)
            if m:
                sec_old.add((int(m.group(1)), int(m.group(2))))
        # 첫 판 번호 후보 가운데 '첫 판 장'이 이 장 또는 첫판 대응 장인 것만
        first_chapters = {"1": {1}, "2": {2}, "3": {3}, "4": {4}, "5": {5}, "6": {6, 7, 8}, "7": {6}, "8": {6}, "9": {7}, "10": {8}, "11": set()}
        cand = {n for n in nums if n[0] in first_chapters.get(chap, set())}
        # 존재 확인
        for a, b in sorted(cand):
            lab = f"{chap}:old-{a}-{b}"
            if lab not in all_labels and (a, b) not in removed_nums:
                # 다른 장에 있는지
                where = [k for k in all_labels if k.endswith(f":old-{a}-{b}")]
                print(f"  구조표:{i} {sec}: 첫 판 {a}.{b} → `{{{{{lab}}}}}` 없음" + (f" (다른 장에 있음: {where})" if where else ""))
            elif lab in all_labels and stmts[lab]["section"] != sec and (a, b) not in removed_nums:
                print(f"  구조표:{i} {sec}: 첫 판 {a}.{b} `{{{{{lab}}}}}`는 절 {stmts[lab]['section']}에 있음")
        for a, b in sorted(removed_nums):
            lab = f"{chap}:old-{a}-{b}"
            if lab in all_labels:
                print(f"  구조표:{i} {sec}: 「뺌」으로 적힌 첫 판 {a}.{b}가 `{{{{{lab}}}}}`로 존재({stmts[lab]['section']})")
        # 「뺌」으로 적힌 새 라벨
        for m in re.finditer(r"(\{\{[^}]*\}\})[^|]{0,60}?뺌", col):
            l2 = m.group(1)[2:-2]
            if l2 in all_labels:
                print(f"  구조표:{i} {sec}: 「뺌」으로 적힌 {m.group(1)}가 존재({stmts[l2]['section']})")
    # 3) 절별 진술 수와 구조표에 없는 진술
    print("\n-- 절별 진술 수(장 파일) 와 구조표 행에 라벨·첫 판 번호로 적히지 않은 진술 --")
    for i, sec, rest, cells in rows:
        chap = sec.split(".")[0]
        col = " | ".join(cells[1:])
        labs = {f"{a}:{b}" for a, b in LABEL_RE.findall(col)}
        nums = set()
        for m in re.finditer(r"(\d+)\.(\d+)[–-](\d+)\.(\d+)", col):
            a, b, c, d = map(int, m.groups())
            if a == c:
                for x in range(b, d + 1):
                    nums.add(f"old-{a}-{x}")
        for m in re.finditer(r"(?<![\d.])(\d+)\.(\d+)(?![\d.])", re.sub(r"\{\{[^}]*\}\}", "", col)):
            nums.add(f"old-{m.group(1)}-{m.group(2)}")
        here = by_sec.get(sec, [])
        unlisted = [k for k in here if k not in labs and k.split(":", 1)[1] not in nums]
        kinds = {}
        for k in here:
            kinds[stmts[k]["kind"]] = kinds.get(stmts[k]["kind"], 0) + 1
        ks = ", ".join(f"{a} {b}" for a, b in sorted(kinds.items()))
        print(f"  {sec}: 진술 {len(here)}개({ks}); 구조표 행에 없는 것 {len(unlisted)}개" + (": " + ", ".join(unlisted) if unlisted and len(unlisted) <= 40 else ""))


# ------------------------------------------------------------------ (ㄴ) 11.3
def parse_11_tables():
    text = lines(os.path.join(BASE, "장11.md"))
    sec = None
    tables = {"11.3": [], "11.4": [], "11.2": []}
    cur = None
    for i, ln in enumerate(text, 1):
        m = re.match(r"^### (11\.\d)", ln)
        if m:
            sec = m.group(1)
            cur = None
            continue
        if sec in tables:
            if ln.startswith("**") and ln.endswith("**"):
                cur = ln.strip("*").rstrip(".")
            if ln.startswith("| ") and not ln.startswith("|---"):
                cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
                tables[sec].append((i, cur, cells))
    return tables


def grade_items(col):
    """'정리 {{a}}·{{b}}, 보조정리 {{c}}: 등급; ...' → [(label, 등급집합)]. '없음' → []."""
    out = []
    if col.strip() == "없음":
        return out
    # 괄호 안의 보충(부록 D …)은 등급 판정에서 제외
    col2 = re.sub(r"\((?:[^()]|\([^()]*\))*\)", "", col)
    for part in col2.split(";"):
        if ":" not in part:
            continue
        labs_part, grade = part.rsplit(":", 1)
        labs = [f"{a}:{b}" for a, b in LABEL_RE.findall(labs_part)]
        g = norm_grade(grade)
        for l in labs:
            out.append((l, g))
    return out


def cites(stmts, x, y):
    s = stmts.get(x)
    if not s:
        return None
    return y in (s["head_labels"] | s["body_labels"])


def check_11_3(stmts, seen):
    print("\n==================== (ㄴ) 11.3절 세 표 ====================")
    tables = parse_11_tables()
    rows = [r for r in tables["11.3"] if r[2][0] != "입력"]
    all_labels = set(stmts)
    listed_grade = {}
    print("\n-- 라벨 실재·도달 --")
    for i, tbl, cells in rows:
        labs = [f"{a}:{b}" for a, b in LABEL_RE.findall(" | ".join(cells))]
        for l in labs:
            if l not in all_labels:
                print(f"  장11:{i} [{tbl}] 없는 라벨 {{{{{l}}}}}")
            elif l not in seen:
                print(f"  장11:{i} [{tbl}] 주 정리에서 닿지 않는 진술 {{{{{l}}}}}({stmts[l]['kind']} {stmts[l]['name']})")
    print("\n-- 「계산 진술과 산술 등급」 열 ↔ 머리의 계산 보조·계산 증거 등급 --")
    for i, tbl, cells in rows:
        for l, g in grade_items(cells[1]):
            if l not in stmts:
                continue
            name, rec, tag, grades, lit, auth = head_info(stmts[l]["head"])
            hg = frozenset().union(*[norm_grade(x) for x in grades]) if grades else frozenset()
            if l in listed_grade:
                print(f"  장11:{i} [{tbl}] {{{{{l}}}}} 이미 앞 행({listed_grade[l]})에 적힘(「다시 적지 않았다」 규칙 위반)")
            listed_grade[l] = i
            if not grades:
                print(f"  장11:{i} [{tbl}] {{{{{l}}}}}({stmts[l]['kind']} {name}): 표는 등급 {sorted(g)}이나 머리에 계산 보조·계산 증거 없음 — 표지 [{tag}]")
            elif hg != g:
                print(f"  장11:{i} [{tbl}] {{{{{l}}}}}({stmts[l]['kind']} {name}): 표 등급 {sorted(g)} ↔ 머리 등급 {sorted(hg)} — 표지 [{tag}]")
    print("\n-- 주 정리에 닿는 진술 가운데 머리에 계산 보조·계산 증거가 있으나 11.3 어느 행의 2열에도 없는 것 --")
    for k in sorted(seen & all_labels, key=lambda k: stmts[k]["order"]):
        name, rec, tag, grades, lit, auth = head_info(stmts[k]["head"])
        if grades and k not in listed_grade:
            print(f"  {{{{{k}}}}} {stmts[k]['kind']} {name} [{tag}] ({stmts[k]['file']}:{stmts[k]['line']}, 절 {stmts[k]['section']})")
    print("\n-- 2열에 든 진술이 주 정리에 닿지 않거나 어느 표의 1열 입력에서도 거슬러 올라갈 수 없는 것(참고) --")
    # 입력 라벨에서 거슬러 올라가는 닫힘
    inputs = set()
    for i, tbl, cells in rows:
        inputs |= {f"{a}:{b}" for a, b in LABEL_RE.findall(cells[0])}
    closure, _ = DEP.reach(stmts, list(inputs))
    for l in listed_grade:
        if l in stmts and l not in closure and l not in inputs:
            print(f"  {{{{{l}}}}}는 1열 입력들의 의존 닫힘에 없음")
    print("\n-- 「쓰는 자리」 열의 인용 검증: 'X의 증명(Y)'·'X(Y)'는 X가 Y를 인용하는가; 괄호 없는 자리는 X가 1열 입력 가운데 하나라도 인용하는가 --")
    for i, tbl, cells in rows:
        input_labs = [f"{a}:{b}" for a, b in LABEL_RE.findall(cells[0])]
        use_cols = cells[2:] if tbl == "공유 입력" else cells[2:3]
        for ci, col in enumerate(use_cols):
            # 항목을 쉼표로 나누되 괄호 안 쉼표는 보존
            items = re.split(r",\s*(?![^()]*\))", col)
            for it in items:
                it = it.strip()
                if not it or it.startswith("10.") or it.startswith("없음"):
                    continue
                m = re.match(r"^(.*?)\(((?:[^()]|\([^()]*\))*)\)\s*$", it)
                xs_txt, ys_txt = (m.group(1), m.group(2)) if m else (it, "")
                xs = [f"{a}:{b}" for a, b in LABEL_RE.findall(xs_txt)]
                ys = [f"{a}:{b}" for a, b in LABEL_RE.findall(ys_txt)]
                if not xs:
                    continue
                if "둘 다" in ys_txt or "다섯 다" in ys_txt or "두 명제" in ys_txt or "세 정리" in xs_txt:
                    ys = input_labs
                if not ys:
                    ys = input_labs
                for x in xs:
                    if x not in stmts:
                        continue
                    ok = [y for y in ys if cites(stmts, x, y)]
                    if not ok:
                        print(f"  장11:{i} [{tbl}] 「{it[:90]}」: {{{{{x}}}}}({stmts[x]['kind']} {stmts[x]['name']})의 머리·증명 본문·미룬 증명이 {ys}를 인용하지 않음")
    print("\n-- 고리 좌표 --")
    for i, tbl, cells in rows:
        for m in re.finditer(r"10\.7절 (\S+?) 고리", " | ".join(cells)):
            print(f"  장11:{i} 「10.7절 {m.group(1)} 고리」")
    t10 = read(os.path.join(BASE, "장10.md"))
    for w in ["첫째", "둘째", "셋째", "넷째", "다섯째", "여섯째"]:
        n = len(re.findall(rf"{w} 고리", t10))
        print(f"  장10에 「{w} 고리」 {n}곳")


# ------------------------------------------------------------------ (ㄷ) 11.4
AUTHORS = ["Konheim", "Weiss", "Foata", "Riordan", "Celano", "Aguilar", "Stanley", "Knuth", "Flajolet", "Sedgewick", "Robbins",
           "Petersson", "Janson", "Ibragimov", "Graham", "Patashnik", "Ahlfors", "Fortuin", "Kasteleyn", "Ginibre", "Jensen", "Wallis",
           "Corless", "Gonnet", "Tanner", "Grimmett", "Harris", "Comtet", "Apostol", "Titchmarsh", "Pollak", "Fekete", "Fleurat",
           "Bonferroni", "Borel–Tanner", "Faà di Bruno", "Euler–Maclaurin", "Euler 합", "Cauchy", "Lagrange", "Cayley", "Stirling",
           "Lambert", "Hermite", "Bernstein", "Taylor", "Abel", "Fritsch", "Carlson", "Markov", "Chebyshev", "Hoeffding", "Chernoff",
           "Bernoulli", "Otter", "Rényi", "Kolmogorov", "Lebesgue", "Fubini", "Tonelli", "Dini", "Weierstrass", "Rouché", "Hadamard",
           "Pringsheim", "Darboux", "Newton", "Leibniz", "Gauss", "Laplace", "Riemann", "Hölder", "Cauchy–Schwarz", "Minkowski",
           "Chu–Vandermonde", "Vandermonde", "Dyck", "Catalan", "Erdős", "Flajolet–Odlyzko", "Odlyzko", "Hwang", "Chassaing", "Louchard",
           "Marckert", "Aldous", "Pitman", "Tweedie", "Haight", "Breiman", "Dwass", "Rogers", "Pólya", "Szegő", "Hardy", "Littlewood"]


def locate(stmts, fname, ln_no):
    """줄 번호가 속한 진술(머리부터 본문 끝까지) 또는 절."""
    best = None
    for k, s in stmts.items():
        if s["file"] == fname and s["line"] <= ln_no <= s["body_end"]:
            if best is None or s["line"] > stmts[best]["line"]:
                best = k
    return best


def check_11_4(stmts, seen):
    print("\n==================== (ㄷ) 11.4절 표 ↔ 본문의 문헌 인용 ====================")
    tables = parse_11_tables()
    rows = [r for r in tables["11.4"] if r[2][0] != "문헌"]
    all_labels = set(stmts)
    listed = {}
    listed_secs = {}
    for i, lit, cells in rows:
        for l in [f"{a}:{b}" for a, b in LABEL_RE.findall(cells[2])]:
            if l not in all_labels:
                print(f"  장11:{i} 없는 라벨 {{{{{l}}}}} — {cells[0][:50]}")
            listed.setdefault(l, []).append(cells[0].split(",")[0])
        for m in re.finditer(r"(\d+\.\d+)절", cells[2]):
            listed_secs.setdefault(m.group(1), []).append(cells[0].split(",")[0])
        for m in re.finditer(r"부록 D\.\{\{D:([^}]*)\}\}", cells[2]):
            listed.setdefault("D:" + m.group(1), []).append(cells[0].split(",")[0])
    print("\n-- 머리에 「문헌 인용」이 있는 진술 ↔ 11.4 --")
    for k in sorted(all_labels, key=lambda k: stmts[k]["order"]):
        name, rec, tag, grades, lit, auth = head_info(stmts[k]["head"])
        if lit:
            print(f"  {{{{{k}}}}} {stmts[k]['kind']} {name} [{tag}] → 11.4에 {'있음: ' + str(listed[k]) if k in listed else '없음'}")
    print("\n-- 식별자 자리 「표준」인 머리 --")
    for k in sorted(all_labels, key=lambda k: stmts[k]["order"]):
        if re.search(r";\s*표준\]", stmts[k]["head"]):
            print(f"  {{{{{k}}}}} {stmts[k]['kind']} {stmts[k]['name']} ({stmts[k]['file']}:{stmts[k]['line']}) → 11.4에 {'있음: ' + str(listed[k]) if k in listed else '없음'}")
    print("\n-- 본문·부록 D에서 저자·정리 이름이 나오는 줄의 자리 ↔ 11.4 「쓰인 자리」 --")
    files = DEP.chapter_files("장") + DEP.chapter_files("부록D_장")
    d_items = DEP.parse_appendix_d()
    for fname in files:
        if fname == "장11.md":
            continue
        txt = lines(os.path.join(BASE, fname))
        sec = ""
        cur_d = None
        for ln_no, ln in enumerate(txt, 1):
            m = re.match(r"^### (\d+\.\d+)", ln)
            if m:
                sec = m.group(1)
            m = DEP.D_HEAD_RE.match(ln)
            if m:
                cur_d = "D:" + m.group(1)
            hits = [a for a in AUTHORS if a in ln]
            if not hits:
                continue
            if fname.startswith("부록D"):
                where = cur_d
                ok = where in listed
                print(f"  {fname}:{ln_no} [{where}] {hits} → 11.4 {'있음 ' + str(listed.get(where)) if ok else '없음'} | {ln[:110]}")
            else:
                k = locate(stmts, fname, ln_no)
                ok_stmt = k in listed if k else False
                ok_sec = sec in listed_secs
                flag = "진술 있음 " + str(listed.get(k)) if ok_stmt else ("절 있음 " + str(listed_secs.get(sec)) if ok_sec else "없음")
                print(f"  {fname}:{ln_no} [절 {sec}; 진술 {k}] {hits} → 11.4 {flag} | {ln[:110]}")


# ------------------------------------------------------------------ (ㄹ) 1.4·도입
def check_지도(stmts, seen):
    print("\n==================== (ㄹ) 1.4절·장 도입의 라벨 실재와 간선 주장 ====================")
    all_labels = set(stmts)
    # 1.4절
    t1 = lines(os.path.join(BASE, "장1.md"))
    s, e = None, None
    for i, ln in enumerate(t1):
        if ln.startswith("### 1.4"):
            s = i
        if ln.startswith("### 1.5"):
            e = i
    intro = {"장1.md:1.4": t1[s:e]}
    for name in DEP.chapter_files("장"):
        txt = lines(os.path.join(BASE, name))
        end = next((i for i, ln in enumerate(txt) if ln.startswith("### ")), len(txt))
        if end > 0 and txt[0].startswith("## "):
            intro[name + ":도입"] = txt[:end]
    for key, body in intro.items():
        labs = {f"{a}:{b}" for ln in body for a, b in LABEL_RE.findall(ln)}
        miss = sorted(l for l in labs if l not in all_labels)
        unreached = sorted(l for l in labs if l in all_labels and l not in seen)
        print(f"  {key}: 라벨 {len(labs)}개; 없는 라벨 {miss}; 주 정리에 닿지 않는 라벨 {unreached}")
    # 1.4·도입에서 시작점 수치 주장 ↔ 머리
    print("\n-- 1.4절의 범위 주장 ↔ 진술 머리/본문 (손으로 대조할 발췌) --")
    for k in ["6:V-all", "7:old-6-21", "7:old-6-22", "7:polar-W", "7:qstar-columns", "7:old-6-13", "8:old-6-33", "8:old-6-29", "9:old-7-45", "10:old-8-10", "10:old-8-36", "5:old-5-13", "5:old-5-2", "5:old-5-1", "4:old-4-5", "3:old-3-6", "7:old-6-9", "7:qstar-implies-wlflat", "7:src-plus", "7:old-6-20"]:
        s = stmts.get(k)
        if s:
            txt = lines(os.path.join(BASE, s["file"]))
            stmt_text = " ".join(txt[s["line"] - 1:s["line"] + 2])
            print(f"  {{{{{k}}}}} ({s['file']}:{s['line']}): {stmt_text[:420]}")


# ------------------------------------------------------------------ (ㅁ) 장부 4절·부록 C·의존지도 1.1
def ledger_rows4():
    ledger = read(os.path.join(ROOT, "장부_v2.md"))
    s4 = APP.section(ledger, "## 4. 이름 사전", ["\n## 5."])
    rows = [r for r in APP.table_rows(s4) if len(r) >= 6 and r[0] != "첫 판 번호"]
    return ledger, rows


def check_부록C(stmts):
    print("\n==================== (ㅁ) 장부 4절 ↔ 장 파일 머리, 부록 C ↔ build_C, 의존지도 1.1 ↔ 장부 뺌 ====================")
    ledger, rows = ledger_rows4()
    all_labels = set(stmts)
    live = [r for r in rows if r[4].strip() != "뺌"]
    removed = [r for r in rows if r[4].strip() == "뺌"]
    print(f"  장부 4절: 현행 행 {len(live)}개, 뺌 행 {len(removed)}개; 장 파일 진술 {len(stmts)}개")
    print("\n-- 장부 4절 현행 행 ↔ 장 파일 머리(종류·이름·기록 이름·절) --")
    seen_rows = set()
    for r in live:
        num, kind, name, recname, sec, label = [c.strip() for c in r[:6]]
        m = LABEL_RE.search(label)
        if not m:
            print(f"  [라벨 없는 행] {r}")
            continue
        l = f"{m.group(1)}:{m.group(2)}"
        seen_rows.add(l)
        if l not in all_labels:
            print(f"  [장 파일에 없음] 장부 {num} {kind} {name} {label}")
            continue
        s = stmts[l]
        hname, hrec, tag, grades, lit, auth = head_info(s["head"])
        probs = []
        if s["kind"] != kind:
            probs.append(f"종류 장부 {kind} ↔ 머리 {s['kind']}")
        if (hname or "") != name:
            probs.append(f"이름 장부 「{name}」 ↔ 머리 「{hname}」")
        if (hrec or "") != recname:
            probs.append(f"기록 이름 장부 「{recname}」 ↔ 머리 「{hrec}」")
        if s["section"] != sec:
            probs.append(f"절 장부 {sec} ↔ 파일 {s['section']}")
        # 첫 판 번호와 old 라벨
        mo = re.match(r"old-(\d+)-(\d+)$", m.group(2))
        if mo and num != f"{mo.group(1)}.{mo.group(2)}":
            probs.append(f"첫 판 번호 {num} ↔ 라벨 old-{mo.group(1)}-{mo.group(2)}")
        if not mo and num not in ("—", ""):
            probs.append(f"새 라벨인데 첫 판 번호 {num}")
        if probs:
            print(f"  {{{{{l}}}}}: " + "; ".join(probs))
    for l in sorted(all_labels - seen_rows, key=lambda k: stmts[k]["order"]):
        print(f"  [장부 4절에 없는 진술] {{{{{l}}}}} {stmts[l]['kind']} {stmts[l]['name']} ({stmts[l]['file']}:{stmts[l]['line']})")
    print("\n-- 장부 4절 뺌 행의 라벨이 장 파일에 있는가 --")
    for r in removed:
        m = re.search(r"\((\d+):([A-Za-z][A-Za-z0-9\-]*)\)", r[5])
        if m:
            l = f"{m.group(1)}:{m.group(2)}"
            if l in all_labels:
                print(f"  [뺌 행인데 존재] {r}")
    # 부록 C 기록 이름 표 ↔ build_C
    print("\n-- 부록 C 기록 이름 표 ↔ build_C 생성본 --")
    gen = APP.build_C(ledger)
    gsec = APP.section(gen, "### 기록이 결과에 붙인 이름과 이 글의 번호", ["\n### "])
    cur = read(os.path.join(BASE, "부록C.md"))
    csec = APP.section(cur, "### 기록이 결과에 붙인 이름과 이 글의 번호", ["\n### "])
    grows = [r for r in APP.table_rows(gsec) if r[0] != "기록의 이름"]
    crows = [r for r in APP.table_rows(csec) if r[0] != "기록의 이름"]
    gset = {tuple(r) for r in grows}
    cset = {tuple(r) for r in crows}
    print(f"  생성본 {len(grows)}행, 현재 판 {len(crows)}행")
    gl = {LABEL_RE.search(r[1]).group(0): r for r in grows if LABEL_RE.search(r[1])}
    cl = {}
    for r in crows:
        m = LABEL_RE.search(r[1])
        if m:
            cl.setdefault(m.group(0), []).append(r)
    for r in grows:
        if tuple(r) not in cset:
            m = LABEL_RE.search(r[1])
            alt = cl.get(m.group(0)) if m else None
            print(f"  [생성본에만] {' | '.join(r)}" + (f"  ← 현재 판 같은 라벨 행: {[' | '.join(a) for a in alt]}" if alt else ""))
    for r in crows:
        if tuple(r) not in gset:
            m = LABEL_RE.search(r[1])
            alt = gl.get(m.group(0)) if m else None
            print(f"  [현재 판에만] {' | '.join(r)}" + (f"  ← 생성본 같은 라벨 행: {' | '.join(alt)}" if alt else ""))
    # 부록 C 기록 이름 표의 라벨 실재와 종류
    for r in crows:
        m = LABEL_RE.search(r[1])
        if not m:
            print(f"  [부록 C 라벨 없음] {r}")
            continue
        l = f"{m.group(1)}:{m.group(2)}"
        if l not in all_labels:
            print(f"  [부록 C: 장 파일에 없는 라벨] {' | '.join(r)}")
            continue
        kind = r[1].split(" ")[0]
        if kind != stmts[l]["kind"]:
            print(f"  [부록 C 종류 다름] {' | '.join(r)} ↔ 머리 {stmts[l]['kind']}")
        hname, hrec, *_ = head_info(stmts[l]["head"])
        if hrec != r[0]:
            print(f"  [부록 C 기록 이름 ↔ 머리] {r[0]} ↔ 머리 「{hrec}」 ({l})")
        if hname != r[2]:
            print(f"  [부록 C 이 글의 이름 ↔ 머리] 「{r[2]}」 ↔ 머리 「{hname}」 ({l})")
    # 머리에 기록 이름이 있는데 부록 C에 없는 진술
    for k in sorted(all_labels, key=lambda k: stmts[k]["order"]):
        hname, hrec, *_ = head_info(stmts[k]["head"])
        if hrec and f"{{{{{k}}}}}" not in cl:
            print(f"  [머리에 기록 이름 있으나 부록 C에 없음] {{{{{k}}}}} {stmts[k]['kind']} {hname}; {hrec}")
    # 의존지도 1.1 ↔ 장부 뺌
    print("\n-- 의존지도 1.1절 ↔ 장부 4절 뺌 행 --")
    dm = read(os.path.join(ROOT, "의존지도_v2.md"))
    s11 = APP.section(dm, "### 1.1 뺌·대체된 라벨", ["\n## 2."])
    drows = [r for r in APP.table_rows(s11) if r[0] != "라벨"]
    print(f"  의존지도 1.1 행 {len(drows)}개; 장부 뺌 행 {len(removed)}개")
    ledger_removed = {}
    for r in removed:
        m = re.search(r"\((\d+):([A-Za-z][A-Za-z0-9\-]*)\)", r[5])
        ledger_removed[f"{m.group(1)}:{m.group(2)}" if m else "(라벨 없음) " + r[0]] = r
    dmap = {}
    for r in drows:
        m = LABEL_RE.search(r[0])
        key = f"{m.group(1)}:{m.group(2)}" if m else r[0]
        dmap[key] = r
        if m and key in set(stmts):
            print(f"  [1.1에 있으나 장 파일에 존재] {key}")
        says_ledger = "장부 4절" in r[2] and "뺌 행 없음" not in r[2]
        in_ledger = key in ledger_removed
        if says_ledger != in_ledger:
            print(f"  [1.1 처리 열 ↔ 장부] {key}: 처리 열 「{r[2]}」 ↔ 장부 뺌 행 {'있음' if in_ledger else '없음'}")
        if in_ledger:
            lr = ledger_removed[key]
            # 요지 열에 장부의 이름이 들어 있는가
            if lr[2].strip() and lr[2].strip() not in r[1]:
                print(f"  [1.1 요지 ↔ 장부 이름] {key}: 1.1 「{r[1]}」 ↔ 장부 「{lr[1]} {lr[2]}; {lr[3]}」")
    for key in ledger_removed:
        if key not in dmap and not key.startswith("(라벨 없음)"):
            print(f"  [장부 뺌 행인데 1.1에 없음] {key}: {ledger_removed[key]}")
    if "(라벨 없음) 8.38" in ledger_removed and not any("8.38" in r[0] for r in drows):
        print("  [장부 뺌 8.38이 1.1에 없음]")


def main():
    parts = set(sys.argv[1:]) or {"전부"}
    stmts = DEP.parse_chapters()
    seen, via = DEP.reach(stmts, DEP.ROOTS)
    print(f"진술 {len(stmts)}개, 닿음 {len(seen & set(stmts))}개")
    if parts & {"전부", "구조표"}:
        check_구조표(stmts)
    if parts & {"전부", "11_3"}:
        check_11_3(stmts, seen)
    if parts & {"전부", "11_4"}:
        check_11_4(stmts, seen)
    if parts & {"전부", "지도"}:
        check_지도(stmts, seen)
    if parts & {"전부", "부록C"}:
        check_부록C(stmts)


if __name__ == "__main__":
    main()
