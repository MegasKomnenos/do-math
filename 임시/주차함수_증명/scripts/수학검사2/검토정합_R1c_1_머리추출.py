# -*- coding: utf-8 -*-
"""R1c 정합 검토: 장8·9·10 진술 머리의 덧붙임 ↔ 본문 인용 ↔ 부록 D ↔ 11.2·11.4 표 (읽기만).

출력: 진술마다 지위 문자열, 선언 의존, 본문 인용 가운데 외부 입력(계산 보조·계산 증거·문헌 인용·에 의존)을 가진 진술,
선언했으나 본문이 인용하지 않는 진술, 외부 입력이 없는 진술에 대한 의존 선언, 계산 보조와 D 항목·11.2 행의 대응과 산술 등급,
작성자 판단 ↔ † 대응, 11.4 표의 언급.
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
parse_chapters = mod.parse_chapters
parse_appendix_d = mod.parse_appendix_d
LABEL_RE = mod.LABEL_RE
BASE = mod.BASE

stmts = parse_chapters()
ditems = parse_appendix_d()

STATUS_RE = re.compile(r"\[([^\[\]]*)\]\.\*\*")


def status_of(head):
    ms = STATUS_RE.findall(head)
    if not ms:
        return ""
    return ms[-1].split(";")[0].strip()


def flags(status):
    f = set()
    if "계산 보조" in status:
        f.add("계산 보조")
    if "계산 증거" in status:
        f.add("계산 증거")
    if "문헌 인용" in status:
        f.add("문헌 인용")
    if "작성자 판단" in status:
        f.add("작성자 판단")
    if "에 의존" in status:
        f.add("에 의존")
    return f


for k, s in stmts.items():
    s["status"] = status_of(s["head"])
    s["flags"] = flags(s["status"])
    s["grades"] = re.findall(r"계산 (?:보조|증거)\(([^)]*)\)", s["status"])

EXT = {k for k, s in stmts.items() if s["flags"] & {"계산 보조", "계산 증거", "문헌 인용", "에 의존"}}

# 본문 텍스트(†·문헌 이름 검색용)
def body_text(key):
    s = stmts[key]
    lines = mod.read_lines(os.path.join(BASE, s["file"]))
    txt = "\n".join(lines[s["line"] - 1:s["body_end"]])
    for d in s.get("defer", []):
        fname, ln = d.split(":")
        ls = mod.read_lines(os.path.join(BASE, fname))
        i = int(ln) - 1
        # 다음 머리까지
        j = i + 1
        while j < len(ls) and not (mod.HEAD_RE.match(ls[j]) or mod.DEFER_RE.match(ls[j])):
            j += 1
        txt += "\n" + "\n".join(ls[i:j])
    return txt


# 11.2 표
ch11 = mod.read_lines(os.path.join(BASE, "장11.md"))
rows_11_2 = {}
on = False
for ln in ch11:
    if ln.startswith("### 11.2"):
        on = True
        continue
    if ln.startswith("### 11.3"):
        break
    if on and ln.startswith("| 부록 D."):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        dm = re.search(r"\{\{D:([A-Za-z0-9\-]+)\}\}", cells[0])
        rows_11_2[dm.group(1)] = dict(stmts=set(f"{a}:{b}" for a, b in LABEL_RE.findall(cells[1])), grade=cells[2], where=cells[3], raw=ln)

# 11.4 표
rows_11_4 = []
on = False
for ln in ch11:
    if ln.startswith("### 11.4"):
        on = True
        continue
    if on and ln.startswith("| ") and not ln.startswith("| 문헌") and not ln.startswith("|---"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows_11_4.append(dict(lit=cells[0][:40], labels=set(f"{a}:{b}" for a, b in LABEL_RE.findall(cells[2])), where=cells[2]))

# D 항목 산술 등급
dgrade = {}
for name, it in ditems.items():
    ls = mod.read_lines(os.path.join(BASE, it["file"]))
    for ln in ls[it["line"]:]:
        if ln.startswith("### D."):
            break
        if ln.startswith("**산술 등급.**"):
            dgrade[name] = ln[len("**산술 등급.**"):].strip()
            break

TARGET = [k for k in stmts if k.split(":")[0] in ("8", "9", "10")]
TARGET.sort(key=lambda k: stmts[k]["order"])

print(f"대상 진술 {len(TARGET)}개 (장8·9·10)\n")
for k in TARGET:
    s = stmts[k]
    print(f"=== {{{{{k}}}}} {s['kind']} [{s['file']}:{s['line']}] 절 {s['section']}")
    print(f"  이름: {s['name']}")
    print(f"  지위: {s['status']}")
    declared = s["head_labels"]
    body = s["body_labels"]
    txt = body_text(k)
    # (1) 본문이 인용하는 외부 입력 진술 가운데 선언되지 않은 것
    undeclared = sorted((body & EXT) - declared)
    if undeclared:
        print(f"  [검토] 본문 인용 중 외부 입력 진술인데 머리에 선언 없음: {undeclared}")
    # (2) 선언했으나 본문이 인용하지 않는 것
    unused = sorted(declared - body)
    if unused:
        print(f"  [검토] 선언했으나 본문(머리 제외)이 인용하지 않음: {unused}")
    # (3) 외부 입력 없는 진술에 대한 의존 선언
    nonext = sorted(declared - EXT)
    if nonext:
        print(f"  [검토] 의존 선언했으나 그 진술에 외부 입력 없음: {nonext}")
    # (4) 계산 보조 ↔ D 항목 ↔ 11.2
    if "계산 보조" in s["flags"] or "계산 증거" in s["flags"]:
        ds = [n for n, it in ditems.items() if k in it["labels"]]
        print(f"  계산: 머리 등급 {s['grades']}; D 항목 {ds}; D 등급 {[dgrade.get(n, '?')[:60] for n in ds]}")
        r = [n for n, r in rows_11_2.items() if k in r["stmts"]]
        print(f"  11.2 행 {r}; 11.2 등급 {[rows_11_2[n]['grade'] for n in r]}; 쓰인 곳 {[rows_11_2[n]['where'] for n in r]}")
        if not ds:
            print("  [검토] 계산 보조/증거인데 D 항목 없음")
        if not r:
            print("  [검토] 계산 보조/증거인데 11.2 행 없음")
    else:
        ds = [n for n, it in ditems.items() if k in it["labels"]]
        r = [n for n, r in rows_11_2.items() if k in r["stmts"]]
        if ds or r:
            print(f"  [검토] 계산 표지 없는데 D 항목/11.2 행이 이 진술을 듦: D {ds}, 11.2 {r}")
    # (5) 작성자 판단 ↔ †
    has_dagger = "†" in txt
    if ("작성자 판단" in s["flags"]) != has_dagger:
        print(f"  [검토] 작성자 판단 표지 {'있음' if '작성자 판단' in s['flags'] else '없음'} / † {'있음' if has_dagger else '없음'}")
    # (6) 11.4
    lits = [r["lit"] for r in rows_11_4 if k in r["labels"]]
    if lits:
        print(f"  11.4 표가 듦: {lits}")
    names = []
    for nm in ("Robbins", "Jensen", "Euler", "Stirling", "Apostol", "Titchmarsh", "Cayley", "Lagrange", "Doob", "Wallis", "Knuth"):
        if nm in txt:
            names.append(nm)
    if names:
        print(f"  본문의 문헌 이름: {names}")
    if "문헌 인용" in s["flags"]:
        print(f"  [검토] 문헌 인용 표지 있음; 11.4 {lits}")
    print()

print("\n== 장8·9·10 D 항목의 라벨 ↔ 그 진술의 계산 표지 ==")
for name, it in sorted(ditems.items(), key=lambda kv: kv[1]["order"]):
    if not any(l.split(":")[0] in ("8", "9", "10") for l in it["labels"]):
        continue
    print(f"D.{{{{D:{name}}}}} [{it['file']}:{it['line']}] 라벨 {sorted(it['labels'])}; 등급 {dgrade.get(name, '?')[:80]}")
    for l in sorted(it["labels"]):
        st = stmts.get(l)
        if st is None:
            print(f"   [검토] 정의되지 않은 라벨 {l}")
            continue
        print(f"   {l}: {st['status']}")
    r = rows_11_2.get(name)
    print(f"   11.2: {sorted(r['stmts']) if r else '없음'} / {r['grade'] if r else ''} / {r['where'] if r else ''}")
