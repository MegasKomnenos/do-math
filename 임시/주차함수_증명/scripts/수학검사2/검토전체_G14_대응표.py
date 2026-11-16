# -*- coding: utf-8 -*-
"""G14: 라벨–번호 대응표(대조v2/라벨_번호_대응표_1114.md)와 장v2 본문의 진술 머리를 대조한다.
읽기만 한다. 출력: 본문 머리 목록(번호·종류·이름·절)과 표의 불일치."""
import os, re, sys
BASE = r"C:\math\임시\주차함수_증명"
CH = os.path.join(BASE, "장v2")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)(.*)$")
SEC_RE = re.compile(r"^### (\d+\.\d+)")
CHAP_RE = re.compile(r"^## (\d+)\.")

def chapter_files():
    out = []
    for i in range(1, 12):
        p = os.path.join(CH, f"장{i}.md")
        if os.path.exists(p):
            out.append(p)
        else:
            parts = sorted(n for n in os.listdir(CH) if re.fullmatch(rf"장{i}[A-Z]\.md", n))
            out += [os.path.join(CH, n) for n in parts]
    return out

heads = []  # (chapter, num, kind, label, name, sec, file, line)
counters = {}
chapter = None; sec = None
for f in chapter_files():
    with open(f, encoding="utf-8") as fh:
        for ln_no, ln in enumerate(fh, 1):
            m = CHAP_RE.match(ln)
            if m: chapter = int(m.group(1))
            m = SEC_RE.match(ln)
            if m: sec = m.group(1)
            m = HEAD_RE.match(ln)
            if m:
                kind, lab_ch, lab, rest = m.groups()
                counters.setdefault(chapter, 0); counters[chapter] += 1
                # name: leading "(…)" possibly with nested parens
                name = None
                rest = rest.strip()
                if rest.startswith("("):
                    depth = 0
                    for i, c in enumerate(rest):
                        if c == "(": depth += 1
                        elif c == ")":
                            depth -= 1
                            if depth == 0:
                                name = rest[1:i]; break
                heads.append((chapter, counters[chapter], kind, f"{lab_ch}:{lab}", name, sec, os.path.basename(f), ln_no, int(lab_ch) != chapter))

table = {}
TROW = re.compile(r"^\| `\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}` \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|$")
with open(os.path.join(BASE, "대조v2", "라벨_번호_대응표_1114.md"), encoding="utf-8") as fh:
    for ln_no, ln in enumerate(fh, 1):
        m = TROW.match(ln.rstrip("\n"))
        if m:
            ch, lab, kind, name, cur, old, sec = m.groups()
            table[f"{ch}:{lab}"] = dict(kind=kind, name=name, cur=cur, old=old, sec=sec, line=ln_no)

print(f"본문 머리 수: {len(heads)}; 표 행 수: {len(table)}")
seen = set()
for (chapter, num, kind, label, name, sec, fname, ln_no, mismatch_ch) in heads:
    seen.add(label)
    cur = f"{chapter}.{num}"
    if mismatch_ch:
        print(f"[라벨 장 불일치] {fname}:{ln_no} {label} 놓인 장 {chapter}")
    row = table.get(label)
    if row is None:
        print(f"[표에 없음] {fname}:{ln_no} {label} {kind} 현재번호 {cur} 절 {sec} 이름 {name!r}")
        continue
    probs = []
    if row["cur"] != cur: probs.append(f"번호 표 {row['cur']} ≠ 본문 {cur}")
    if row["kind"] != kind: probs.append(f"종류 표 {row['kind']} ≠ 본문 {kind}")
    if row["sec"] != sec: probs.append(f"절 표 {row['sec']} ≠ 본문 {sec}")
    tn = row["name"]
    bn = name if name is not None else "—"
    if tn != bn:
        probs.append(f"이름 표 {tn!r} ≠ 본문 {bn!r}")
    if probs:
        print(f"[불일치] {fname}:{ln_no} {label} (표 행 {row['line']}): " + " | ".join(probs))
for label, row in table.items():
    if label not in seen:
        print(f"[본문에 없음] 표 행 {row['line']} {label} {row}")
