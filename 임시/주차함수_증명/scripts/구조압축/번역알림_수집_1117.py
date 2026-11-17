# -*- coding: utf-8 -*-
"""구조 압축 캠페인(2026-11-17)의 모든 인계 파일에서 「번역」 절을 모아 번역 알림 문서를 만든다(U18 재료).

입력: 대조v2/구조압축/인계_*.md 의 `### 번역…` 또는 `## 번역…` 절(다음 같은 수준 머리 전까지).
출력: 대조v2/구조압축/번역_알림_1117.md (덮어씀; 생성물).
사용: python -I scripts/구조압축/번역알림_수집_1117.py
"""
import io, os, re, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "대조v2", "구조압축")
OUT = os.path.join(D, "번역_알림_1117.md")

def unit_key(name):
    u = name[len("인계_"):-3]
    order = {"U": 0, "R": 1, "H": 2, "K": 3, "V": 4, "W": 5, "X": 6}
    m = re.match(r"([A-Z]+)(\d+)([a-z]?)", u)
    return (order.get(m.group(1)[0], 9), int(m.group(2)), m.group(3), u) if m else (9, 0, "", u)

sections = []
for p in sorted(glob.glob(os.path.join(D, "인계_*.md")), key=lambda p: unit_key(os.path.basename(p))):
    u = os.path.basename(p)[len("인계_"):-3]
    lines = io.open(p, encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^(#{2,4}) (번역.*)$", lines[i])
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

md = ["# 번역 알림 — 구조 압축 캠페인(2026-11-17)의 인계에서 모은 「번역」 절", "",
      "영어판(`영어/장v2_en/`)은 이 캠페인 동안 손대지 않았다. 아래는 각 수리·점검 단위의 인계 파일에서 「번역」 절을 단위 차례로 그대로 옮긴 것이다(생성: `scripts/구조압축/번역알림_수집_1117.py`; 손으로 고치지 않는다 — 고칠 것은 원 인계에). "
      "행 번호는 그 단위가 적은 시각의 한국어판 행이고, 뒤 단위가 같은 파일을 더 고쳤으면 당겨졌을 수 있다(W1 인계 덧붙임의 1장 −4행 등). 장 번호·라벨 접두는 9장 제거 뒤 전역 치환(10→9, 11→10) 전의 것이다 — 영어판도 같은 치환과 `장9.md`·`부록D_장9.md` 삭제, `장10.md`→`장9.md`·`부록D_장10.md`→`부록D_장9.md`·`장11.md`→`장10.md` 개명, 0바이트 조각 `부록D_장5B.md`·`부록D_장6.md` 삭제가 필요하다. "
      "9장 제거 자체(V1–V5)와 제거 여파(W1–W9)로 바뀐 자리는 한국어판 전체를 다시 대조하는 것이 빠를 수 있다 — 현행 한국어판이 정본이다.", ""]
for u, title, txt in sections:
    md.append(f"## {u} — {title}"); md.append(""); md.append(txt); md.append("")
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
print("단위", len(sections), "→", OUT, os.path.getsize(OUT), "B")
for u, title, txt in sections:
    print(f"  {u}: {title} ({len(txt)}자)")
