# -*- coding: utf-8 -*-
"""둘째 판 부록 A(기호표)·B(인용한 기록)·C(용어 대응표)를 장부 v2와 장 파일에서 생성한다.

사용: python 부록_v2.py [--base 376 --checked 394] [--dry]
출력: 장v2/부록A.md, 장v2/부록B.md, 장v2/부록C.md
- A: 장부 1.1(변수 글자)·1.2(전역 기호)에서 글자 | 뜻 | 정의 절 | 기록의 글자. 정의 절의 장 순. 본문(장 파일 전체)에 바탕 글자가 보이지 않는 행은 표준 출력에 적는다(세션 검토용).
- B: 장 파일·부록 D 조각(·부록 A·C)에 든 식별자 [rXXXXXXX] 전부. 기록 폴더·시각(events/<폴더>.json의 at, 없으면 review/assessment.json 수정 시각; KST)·record.json 제목. 시각 순.
- C: 3절(낱말 | 뜻 | 첫 정의 절 | 첫 판의 낱말)에서 영어 병기와 다른 이름을 가진 낱말, 4절(첫 판 진술 ↔ 기록의 결과 이름 ↔ 라벨; 기록 이름이 있는 행), 7절(이 글의 글자 | 기록 | 기록의 글자 | 이동).
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
LEDGER = os.path.join(ROOT, "장부_v2.md")
CHAP_DIR = os.path.join(ROOT, "장v2")


def section(text, start_marker, end_markers):
    i = text.index(start_marker)
    j = len(text)
    for m in end_markers:
        k = text.find(m, i + len(start_marker))
        if k != -1:
            j = min(j, k)
    return text[i:j]


def table_rows(sec_text):
    rows = []
    for ln in sec_text.split("\n"):
        if not ln.startswith("|") or ln.startswith("|---"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        rows.append(cells)
    return rows


def chapter_texts():
    texts = {}
    for p in sorted(glob.glob(os.path.join(CHAP_DIR, "*.md"))):
        name = os.path.basename(p)
        if name.startswith("_") or name in ("부록A.md", "부록B.md", "부록C.md"):
            continue
        texts[name] = io.open(p, encoding="utf-8").read()
    return texts


def sec_sort_key(sec):
    m = re.match(r"(\d+)(?:\.(\d+))?", sec or "")
    if not m:
        return (99, 99)
    return (int(m.group(1)), int(m.group(2) or 0))


MEMO = re.compile(r"첫 판|세션|집필|2차 대조|회수|지시|초안|결정 \d|파견|재대조|확인 요|판정 요|조립본|기록대조|설계 에이전트|집필자|씀 — ")


def clean(text):
    """사전의 뜻·비고 열에서 작업 메모(첫 판 참조, 세션 결정, 대조·회수 기록)를 걷어 낸다. 괄호 단위와 쌍반점 조각 단위로."""
    # 균형 잡힌 괄호 단위로 훑어, 작업 메모가 든 괄호(중첩 포함)를 통째로 지운다.
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "(":
            depth, j = 0, i
            while j < n:
                if text[j] == "(":
                    depth += 1
                elif text[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            seg = text[i:j + 1] if j < n else text[i:]
            if MEMO.search(seg):
                i = j + 1
                continue
            out.append(seg)
            i = j + 1
            continue
        out.append(ch)
        i += 1
    t = "".join(out)
    parts = [p for p in re.split(r"(?<!\$);\s*", t) if p.strip()]
    parts = [p for p in parts if not MEMO.search(p)] or parts[:1]
    t = "; ".join(p.strip() for p in parts)
    t = re.sub(r"\s+", " ", t).replace(" ,", ",").replace("( ", "(").strip(" ;,")
    return t


# ------------------------------------------------------------------ 부록 A
def build_A(ledger, body, prune=False):
    out = ["## 부록 A. 기호표", "",
           "본문에 나오는 전역 기호를 처음 정의된 절의 순서로 적는다. 열은 기호, 뜻, 처음 정의된 절, 그리고 같은 양을 연구 기록이 다른 글자로 적은 경우 그 글자와 식별자다. 증명 안에서만 쓰이는 국소 기호는 그 증명이 정의한다.", ""]
    s11 = section(ledger, "### 1.1 변수·지표 글자", ["### 1.2"])
    rows11 = [r for r in table_rows(s11) if len(r) >= 4 and r[0] != "글자"]
    out += ["### 변수와 지표 글자", "", "| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |", "|---|---|---|---|"]
    for r in rows11:
        out.append(f"| {r[0]} | {clean(r[1])} | 1.5 | — |")
    out.append("")
    s12 = section(ledger, "### 1.2 전역 기호", ["### 1.3"])
    rows12 = [r for r in table_rows(s12) if len(r) >= 7 and not r[0].startswith("글자")]
    missing = []
    by_ch = {}
    for r in rows12:
        glyph, meaning, sec, rec = r[0], r[2], r[3], r[6]
        ch = sec_sort_key(sec)[0]
        # 본문 출현 검사: 첫 $…$ 안의 바탕 토큰(백슬래시 명령 또는 글자)
        m = re.search(r"\$([^$]+)\$", glyph)
        tok = None
        if m:
            inner = m.group(1)
            mm = re.match(r"(\\[A-Za-z]+(?:\{[^}]*\})?|[A-Za-z])", inner)
            tok = mm.group(1) if mm else None
        present = (tok is None) or (tok in body)
        if not present:
            missing.append(glyph)
            if prune:
                continue
        by_ch.setdefault(ch, []).append((sec_sort_key(sec), glyph, meaning, sec, rec))
    for ch in sorted(by_ch):
        out += [f"### {ch}장에서 정의하는 기호", "", "| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |", "|---|---|---|---|"]
        for _, glyph, meaning, sec, rec in sorted(by_ch[ch], key=lambda t: t[0]):
            rec_cell = clean(rec) if rec and rec != "—" else "—"
            out.append(f"| {glyph} | {clean(meaning)} | {sec} | {rec_cell or '—'} |")
        out.append("")
    return "\n".join(out) + "\n", missing


# ------------------------------------------------------------------ 부록 B
def record_meta(rid, dirs):
    match = [d for d in dirs if d.startswith(rid)]
    if len(match) != 1:
        return None
    d = match[0]
    rec = json.load(io.open(os.path.join(KNOW, "records", d, "record.json"), encoding="utf-8"))
    at = None
    ev = os.path.join(KNOW, "events", d + ".json")
    if os.path.exists(ev):
        at = json.load(io.open(ev, encoding="utf-8")).get("at")
    if not at:
        ap = os.path.join(KNOW, "records", d, "review", "assessment.json")
        if os.path.exists(ap):
            at = os.path.getmtime(ap)
    when = datetime.datetime.fromtimestamp(at, KST).strftime("%m-%d %H:%M") if at else "—"
    title = rec.get("title", "").replace("|", "／").replace("\n", " ").strip()
    return at or 0, when, title, d


def build_B(texts, base, checked):
    ids = {}
    for name, text in texts.items():
        for br in re.finditer(r"\[([^\]]*)\]", text):
            for tok in re.findall(r"(?<![0-9a-zA-Z])r[0-9a-f]{7}(?![0-9a-zA-Z])", br.group(1)):
                ids.setdefault(tok, set()).add(name)
    dirs = os.listdir(os.path.join(KNOW, "records"))
    rows, missing = [], []
    for rid in sorted(ids):
        meta = record_meta(rid, dirs)
        if not meta:
            missing.append(rid)
            continue
        rows.append((meta[0], rid, meta[1], meta[2], meta[3]))
    rows.sort()
    out = ["## 부록 B. 인용한 기록", "",
           f"본문과 부록(계산 증거 자료, 기호표의 「기록의 글자」, 용어 대응표)이 대괄호로 인용한 연구 기록을 기록의 시각 순으로 적는다. 식별자는 기록 폴더 이름의 앞 여덟 글자, 곧 `r`과 그 뒤의 16진수 일곱 자리다. 기록은 이 글과 함께 보관되는 연구 인스턴스의 `knowledge/records/` 아래 폴더이며, 각 폴더의 `exposition.md`가 본문, `record.json`이 주장 목록, `review/`가 독립 검토다. "
           f"이 글의 기준은 지식 저장소의 판 {base}이고, 판 {checked}(2026-11-12)까지 아래 기록 어느 것에도 우려나 철회가 없음을 확인했다.", "",
           "| 식별자 | 기록의 시각 | 내용 | 폴더 |", "|---|---|---|---|"]
    for _, rid, when, title, d in rows:
        out.append(f"| {rid} | {when} | {title} | `{d}` |")
    out.append("")
    return "\n".join(out) + "\n", rows, missing


# ------------------------------------------------------------------ 부록 C
def build_C(ledger):
    out = ["## 부록 C. 용어 대응표", "",
           "이 글의 용어가 연구 기록의 용어와 다른 자리, 영어를 함께 적은 낱말, 기록이 결과에 붙인 이름과 이 글의 번호, 그리고 기록의 글자와 이 글의 글자의 대응을 적는다. 본문은 이 글의 용어와 번호만 쓴다.", ""]
    # 3절: 낱말
    s3 = section(ledger, "## 3. 낱말 사전", ["\n## 4."])
    rows3 = [r for r in table_rows(s3) if len(r) >= 4 and r[0] != "낱말"]
    out += ["### 낱말: 이 글의 용어와 기록의 용어", "", "| 이 글의 용어 | 기록의 용어 | 처음 정의된 절 |", "|---|---|---|"]
    for r in rows3:
        word, meaning, sec, old = r[0], r[1], r[2], r[3]
        eng = ", ".join(re.findall(r"\(([A-Za-z][A-Za-z\- ;,]+)\)", meaning + " " + word))
        old_c = clean(old.strip())
        if old_c in ("같음", "", "—") and not eng:
            continue
        word_c = word if not eng or eng in word else f"{word}({eng})"
        out.append(f"| {word_c} | {old_c if old_c not in ('같음', '') else '같음'} | {sec} |")
    out.append("")
    # 4절: 기록의 결과 이름 ↔ 라벨
    s4 = section(ledger, "## 4. 이름 사전", ["\n## 5."])
    rows4 = [r for r in table_rows(s4) if len(r) >= 6 and r[0] != "첫 판 번호"]
    out += ["### 기록이 결과에 붙인 이름과 이 글의 번호", "", "| 기록의 이름 | 이 글의 진술 | 이 글의 이름 |", "|---|---|---|"]
    for r in rows4:
        num, kind, name, recname, sec, label = r[:6]
        if not recname.strip() or label.strip() in ("—", "") or "{{" not in label or label.strip() == "{{}}":
            continue
        out.append(f"| {recname} | {kind} {label} | {name} |")
    out.append("")
    # 7절: 글자 대응
    s7 = section(ledger, "## 7. 기록 글자 대응", ["\n## 8."])
    rows7 = [r for r in table_rows(s7) if len(r) >= 4 and r[0] != "이 글의 글자"]
    out += ["### 기록의 글자와 이 글의 글자", "", "| 이 글의 글자 | 기록 | 기록의 글자 | 첨자·인수의 이동 |", "|---|---|---|---|"]
    for r in rows7:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {clean(r[3]) or '—'} |")
    out.append("")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="376")
    ap.add_argument("--checked", default="394")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--prune", action="store_true", help="본문에 바탕 토큰이 보이지 않는 1.2 행을 부록 A에서 뺀다")
    args = ap.parse_args()
    ledger = io.open(LEDGER, encoding="utf-8").read()
    texts = chapter_texts()
    body = "\n".join(texts.values())
    A, missing_A = build_A(ledger, body, prune=args.prune)
    C = build_C(ledger)
    # 부록 B는 본문·부록 D와 함께 부록 A·C(기록의 글자 대응)가 인용하는 식별자도 덮는다(불변식 2: 글 전체의 식별자 집합 = 부록 B).
    texts_all = dict(texts)
    texts_all["부록A.md"] = A
    texts_all["부록C.md"] = C
    B, rows_B, missing_B = build_B(texts_all, args.base, args.checked)
    print(f"부록 A: 본문에 바탕 토큰이 보이지 않는 1.2 행 {len(missing_A)}개" + (": " + "; ".join(missing_A[:40]) if missing_A else ""))
    print(f"부록 B: 식별자 {len(rows_B)}개" + (f", 폴더 없음 {missing_B}" if missing_B else ""))
    if args.dry:
        return 0
    for name, content in (("부록A.md", A), ("부록B.md", B), ("부록C.md", C)):
        io.open(os.path.join(CHAP_DIR, name), "w", encoding="utf-8", newline="\n").write(content)
        print("written", name, len(content), "bytes")
    return 0


if __name__ == "__main__":
    main()
