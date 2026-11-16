# -*- coding: utf-8 -*-
"""R1c 보조 검사(읽기만).
(1) 장8·9·10 본문이 인용하는 앞 장 진술의 지위 문자열.
(2) 모든 장에서 「…에 의존」 선언 대상 가운데 외부 입력(계산 보조·계산 증거·문헌 인용·에 의존)이 없는 진술 — 관행 확인.
(3) 결정 73·91·97로 뺀 개념의 낱말이 장8·9·10 본문에 남았는지.
(4) 장8·9·10 머리 괄호의 (이 글의 이름; 기록 이름) ↔ 장부 4절 ↔ 부록 C 기록 이름 표.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
mod = importlib.import_module("_의존_도달")
stmts = mod.parse_chapters()
LABEL_RE = mod.LABEL_RE
BASE = mod.BASE

STATUS_RE = re.compile(r"\[([^\[\]]*)\]\.\*\*")


def status_of(head):
    ms = STATUS_RE.findall(head)
    return ms[-1].split(";")[0].strip() if ms else ""


def ext(status):
    return any(w in status for w in ("계산 보조", "계산 증거", "문헌 인용", "에 의존"))


for k, s in stmts.items():
    s["status"] = status_of(s["head"])

print("== (1) 장8·9·10이 인용하는 앞 장(2–7) 진술의 지위 ==")
cited = set()
for k, s in stmts.items():
    if k.split(":")[0] in ("8", "9", "10"):
        cited |= {l for l in (s["head_labels"] | s["body_labels"]) if l.split(":")[0] not in ("8", "9", "10")}
for l in sorted(cited, key=lambda x: (int(x.split(":")[0]), x)):
    st = stmts.get(l)
    print(f"  {l}: {'(없음)' if st is None else st['status']}  {'[외부입력]' if st and ext(st['status']) else ''}")

print("\n== (2) 의존 선언 대상 가운데 외부 입력 없는 진술(전 장) ==")
DEP_RE = re.compile(r"((?:[^,\[\];]*?)에 의존)")
cnt = 0
for k, s in sorted(stmts.items(), key=lambda kv: kv[1]["order"]):
    for dep in DEP_RE.findall(s["status"]):
        for a, b in LABEL_RE.findall(dep):
            t = f"{a}:{b}"
            ts = stmts.get(t)
            if ts is None:
                print(f"  {k}: 의존 대상 {t} 정의 없음")
                continue
            if not ext(ts["status"]):
                cnt += 1
                print(f"  {k} [{s['file']}:{s['line']}] → {t} ({ts['kind']}; 지위 「{ts['status']}」)")
print(f"  합계 {cnt}건")

print("\n== (3) 뺀 개념 낱말의 잔존(장8·9·10 본문) ==")
WORDS = ["마지막 102항", "102항", "꼬리 오목성", "TC", "피벗", "문턱 예산", "예산 분해", "무게 성장", "동률의 나머지",
         "\\mathcal E", "S∞", "S_\\infty", "lm-core", "moment-band", "moment-window", "머묾 항등식", "젊은 경로",
         "old-8-5", "old-8-7", "old-8-27", "old-8-29", "old-7-43", "8.38", "첫 차수 생존 법칙", "정리 FO", "V-핵심", "pivot",
         "체류", "판정 사슬", "윤곽", "블록", "순증가", "멈춤 확률", "젊은"]
for name in ("장8.md", "장9.md", "장10.md", "장11.md"):
    lines = mod.read_lines(os.path.join(BASE, name))
    for i, ln in enumerate(lines, 1):
        for w in WORDS:
            if w in ln:
                # 문맥 60자
                j = ln.find(w)
                print(f"  {name}:{i} 「{w}」 … {ln[max(0, j-50):j+60]!r}")

print("\n== (4) 머리 괄호 ↔ 장부 4절 ↔ 부록 C ==")
ledger = mod.read_lines(os.path.join(ROOT, "장부_v2.md"))
rows4 = {}
on = False
for ln in ledger:
    if ln.startswith("## 4."):
        on = True
        continue
    if on and ln.startswith("## 5."):
        break
    if on and ln.startswith("| ") and LABEL_RE.search(ln):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 6:
            m = LABEL_RE.search(cells[5])
            if m:
                rows4[f"{m.group(1)}:{m.group(2)}"] = dict(first=cells[0], kind=cells[1], name=cells[2], rec=cells[3], sec=cells[4])
appC = mod.read_lines(os.path.join(BASE, "부록C.md"))
rowsC = {}
on = False
for ln in appC:
    if ln.startswith("### 기록이 결과에 붙인 이름"):
        on = True
        continue
    if on and ln.startswith("### "):
        break
    if on and ln.startswith("| ") and LABEL_RE.search(ln):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        m = LABEL_RE.search(cells[1])
        if m:
            rowsC[f"{m.group(1)}:{m.group(2)}"] = dict(rec=cells[0], kind_lab=cells[1], name=cells[2])
NAME_RE = mod.NAME_RE
bad = 0
for k, s in sorted(stmts.items(), key=lambda kv: kv[1]["order"]):
    if k.split(":")[0] not in ("8", "9", "10"):
        continue
    nm = NAME_RE.match(s["head"])
    full = nm.group(1) if nm else ""
    if "; 기록" in full:
        this_name, rec = full.split("; ", 1)
    elif full.startswith("기록 ["):
        this_name, rec = full, full
    else:
        this_name, rec = full, ""
    r4 = rows4.get(k)
    rC = rowsC.get(k)
    probs = []
    if r4 is None:
        probs.append("장부 4절에 행 없음")
    else:
        if r4["name"] != this_name:
            probs.append(f"4절 이름 「{r4['name']}」 ≠ 머리 「{this_name}」")
        if r4["rec"] != rec:
            probs.append(f"4절 기록 이름 「{r4['rec']}」 ≠ 머리 「{rec}」")
        if r4["kind"] != s["kind"]:
            probs.append(f"4절 종류 「{r4['kind']}」 ≠ 머리 「{s['kind']}」")
        if r4["sec"] != s["section"]:
            probs.append(f"4절 절 「{r4['sec']}」 ≠ 실제 「{s['section']}」")
    if rec:
        if rC is None:
            probs.append("부록 C 이름 표에 행 없음(기록 이름 있음)")
        else:
            if rC["rec"] != rec:
                probs.append(f"C 기록 이름 「{rC['rec']}」 ≠ 머리 「{rec}」")
            if rC["name"] != this_name:
                probs.append(f"C 이 글 이름 「{rC['name']}」 ≠ 머리 「{this_name}」")
            if not rC["kind_lab"].startswith(s["kind"] + " "):
                probs.append(f"C 종류 「{rC['kind_lab']}」 ≠ 「{s['kind']}」")
    else:
        if rC is not None:
            probs.append(f"기록 이름 없는데 C에 행 있음: {rC}")
    if probs:
        bad += 1
        print(f"  {k} [{s['file']}:{s['line']}] 괄호=「{full}」")
        for p in probs:
            print(f"     - {p}")
print(f"  어긋남 {bad}건 (장8·9·10 진술 {sum(1 for k in stmts if k.split(':')[0] in ('8','9','10'))}개)")
# 뺌 행과 C
print("\n  장부 4절 「뺌」 행:")
for ln in ledger:
    if "| 뺌 |" in ln:
        print("   ", ln.strip()[:160])
