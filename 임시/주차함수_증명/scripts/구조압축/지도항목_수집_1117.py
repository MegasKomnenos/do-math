# -*- coding: utf-8 -*-
"""구조 압축 캠페인 인계 파일에서 「지도」 절을 모아 지도 갱신 작업자(라운드14)의 재료 문서를 만든다.

입력: 대조v2/구조압축/인계_*.md 의 `### 지도…`/`## 지도…` 절(다음 같은 수준 머리 전까지). 기본은 라운드13(물결 3 끝) 뒤에 원고를 고친 단위만:
      H1·H3·U14–U17(물결 4), V1–V7a(9장 제거), W1–W9·X1–X4(제거 여파), V6. `--all`이면 전부.
출력: 대조v2/구조압축/_지도_재료_라운드14.md (덮어씀; 생성물).
사용: python -I scripts/구조압축/지도항목_수집_1117.py [--all]
"""
import io, os, re, glob, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "대조v2", "구조압축")
OUT = os.path.join(D, "_지도_재료_라운드14.md")
ALL = "--all" in sys.argv
AFTER13 = re.compile(r"^(V\d+a?|W\d+|X\d+|U1[4-7]|H[13])$")  # 라운드13(09:0x 파견)은 물결 3까지의 원고 — 물결 4(H1·H3·U14–U17)부터 든다

def unit_key(name):
    u = name[len("인계_"):-3]
    order = {"U": 0, "R": 1, "H": 2, "K": 3, "V": 4, "W": 5, "X": 6}
    m = re.match(r"([A-Z]+)(\d+)([a-z]?)", u)
    return (order.get(m.group(1)[0], 9), int(m.group(2)), m.group(3), u) if m else (9, 0, "", u)

sections = []
for p in sorted(glob.glob(os.path.join(D, "인계_*.md")), key=lambda p: unit_key(os.path.basename(p))):
    u = os.path.basename(p)[len("인계_"):-3]
    if not ALL and not AFTER13.match(u):
        continue
    lines = io.open(p, encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^(#{2,4}) (지도.*)$", lines[i])
        if m:
            level = len(m.group(1)); body = []
            j = i + 1
            while j < len(lines) and not re.match(r"^#{1,%d} " % level, lines[j]):
                body.append(lines[j]); j += 1
            txt = "\n".join(body).strip("\n")
            if txt:
                sections.append((u, m.group(2).strip(), txt))
            i = j
        else:
            i += 1

md = ["# 지도 갱신 라운드14 재료 — 물결 4 뒤·9장 제거·제거 여파 물결의 인계에서 모은 「지도」 절", "",
      "라운드13(물결 3 끝의 원고) 뒤에 원고를 고친 단위들의 인계에서 「지도」 절을 단위 차례로 그대로 옮긴 것이다(생성: `scripts/구조압축/지도항목_수집_1117.py`; 손으로 고치지 않는다 — 고칠 것은 원 인계에). "
      "행 번호와 장 번호·라벨 접두는 그 단위가 적은 시각의 것이다. 이 재료를 읽는 시점의 원고는 장 번호 전역 치환(10장→9장, 11장→10장; `{{10:`→`{{9:`, `{{11:`→`{{10:`; 파일 `장10.md`→`장9.md`, `부록D_장10.md`→`부록D_장9.md`, `장11.md`→`장10.md`) 뒤이므로, 아래의 `10:` 라벨은 현행 `9:`, `11장`은 현행 `10장`으로 읽는다. 현행 원고가 정본이다.", ""]
for u, title, txt in sections:
    md.append(f"## {u} — {title}"); md.append(""); md.append(txt); md.append("")
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
print("단위", len(sections), "→", OUT, os.path.getsize(OUT), "B")
for u, title, txt in sections:
    print(f"  {u}: {title} ({len(txt)}자)")
