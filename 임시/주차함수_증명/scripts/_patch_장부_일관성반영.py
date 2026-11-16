# -*- coding: utf-8 -*-
"""일관성 검토 셋(ㄱ·ㄴ·ㄷ)의 반영 — 사전 `장부_v2.md` 쪽 수정(세션 결정 68·69·70). 멱등.

- 1.2 rb_m 행: 정의 절 5.2 → 2.9, 쓰이는 장에 2·3 추가, 뜻 열의 작업 메모 정리(결정 68).
- 1.3: 3.4 묶음의 $\\varepsilon_m$(Robbins 오차) 제거; 7.5 묶음의 $\\mathfrak l^\\sharp$·$R^\\sharp$ 제거;
       9.3 묶음의 $\\mathfrak e^\\sharp_{\\mathrm{AR}}$ → $\\bar{\\mathfrak d}_k$; 9.6 묶음 행($\\mathfrak j_y$, $\\upsilon_{\\mathrm T}$)과
       10.3 묶음 행($m^{\\mathrm w}$) 삭제(결정 70; ㄴ #13).
- 3절: 「덮개 칸」·「전환 구간」 행 삭제, 「격자점」·「용량 응답」·「둘째 큰 나무」·「기울인 차분」을 목록 행에서 제거(결정 69; ㄴ #12).
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장부_v2.md")
DRY = "--dry" in sys.argv

s = io.open(P, encoding="utf-8").read()
orig = s
lines = s.split("\n")
log = []


class _Skip(Exception):
    pass


def find_one(pred, what):
    idx = [i for i, l in enumerate(lines) if pred(l)]
    if len(idx) == 0:
        log.append((what, "(이미 없음 — 건너뜀)", ""))
        raise _Skip()
    if len(idx) != 1:
        raise SystemExit(f"{what}: 기대 1행, 실제 {len(idx)}행 → {idx[:5]}")
    return idx[0]


def step(fn):
    try:
        fn()
    except _Skip:
        pass


# 1) rb_m 행 (1.2)
sec13 = find_one(lambda l: l.startswith("### 1.3 국소 기호"), "1.3 머리")
i = find_one(lambda l, _s=sec13: l.startswith("| $\\mathrm{rb}_m$ |") and lines.index(l) < _s, "rb_m 행(1.2)")
cells = lines[i].split(" | ")
# cells: ['| $\\mathrm{rb}_m$', 'rb·로마체 이름', '<뜻>', '<정의 절>', '<쓰이는 장>', ...]
cells[2] = re.sub(r"\(처음 부르는 5\.2가 정의한다[^)]*\)", "(2.9절의 첫 사용 자리에서 정의한다 — 세션 결정 68; 3.6·5.2·9.1은 이 글자를 쓴다)", cells[2])
if cells[3].strip() == "5.2":
    cells[3] = "2.9"
ch = [c.strip() for c in cells[4].split(",")]
for extra in ("2", "3"):
    if extra not in ch:
        ch.append(extra)
cells[4] = ", ".join(sorted(ch, key=lambda x: int(x) if x.isdigit() else 99))
new = " | ".join(cells)
log.append(("rb_m", lines[i], new))
lines[i] = new

# 2) 1.3 묶음들
i = find_one(lambda l: "$\\varepsilon_m$(Robbins 오차)" in l, "3.4 묶음 행")
new = lines[i].replace("$\\varepsilon_m$(Robbins 오차); ", "").replace("; $\\varepsilon_m$(Robbins 오차)", "")
log.append(("3.4 묶음", lines[i], new))
lines[i] = new

i = find_one(lambda l: "\\mathfrak l^\\sharp=j-1" in l, "7.5 묶음 행")
new = re.sub(r"\$\\mathfrak l\^\\sharp=j-1\$,?\s*\$R\^\\sharp=m-j\$\([^)]*\)[;,]?\s*", "", lines[i])
new = re.sub(r"\$\\mathfrak l\^\\sharp=j-1\$,?\s*\$R\^\\sharp=m-j\$[;,]?\s*", "", new)
if new == lines[i]:
    raise SystemExit("7.5 묶음: 치환 실패 — 행을 눈으로 볼 것:\n" + lines[i][:400])
log.append(("7.5 묶음", lines[i], new))
lines[i] = new

i = find_one(lambda l: "\\mathfrak e^\\sharp_{\\mathrm{AR}}" in l and "|" in l[:2], "9.3 묶음 행")
new = lines[i].replace("$\\mathfrak e^\\sharp_{\\mathrm{AR}}=6.62/\\sqrt k$", "$\\bar{\\mathfrak d}_k=6.62/\\sqrt k$")
if new == lines[i]:
    new = lines[i].replace("\\mathfrak e^\\sharp_{\\mathrm{AR}}", "\\bar{\\mathfrak d}_k")
log.append(("9.3 묶음", lines[i], new))
lines[i] = new

for key, what in (("$\\mathfrak j_y=A_y(1/e)-A_{y-1}(1/e)$", "9.6 묶음 행"), ("| $m^{\\mathrm w}$((가)의 창 끝) |", "10.3 묶음 행")):
    idx = [k for k, l in enumerate(lines) if l.startswith("| ") and key in l]
    if len(idx) == 1:
        log.append((what + " 삭제", lines[idx[0]], ""))
        del lines[idx[0]]
    elif len(idx) == 0:
        log.append((what, "(이미 없음)", ""))
    else:
        raise SystemExit(f"{what}: 여러 행 {idx}")

# 3) 3절 낱말
for key, what in (("| 덮개 칸 |", "3절 덮개 칸"), ("| 전환 구간 |", "3절 전환 구간")):
    idx = [k for k, l in enumerate(lines) if l.startswith(key)]
    if len(idx) == 1:
        log.append((what + " 삭제", lines[idx[0]], ""))
        del lines[idx[0]]
    elif len(idx) == 0:
        log.append((what, "(이미 없음)", ""))
    else:
        raise SystemExit(f"{what}: 여러 행 {idx}")

i = find_one(lambda l: l.startswith("| 격자, 격자점 |"), "3절 격자 행")
new = lines[i].replace("| 격자, 격자점 |", "| 격자 |", 1)
log.append(("3절 격자", lines[i], new))
lines[i] = new

i = find_one(lambda l: l.startswith("| 기록의 표지, Green 원자, 쌍별 판정, 모멘트 재귀, 용량 응답 |"), "3절 7.4 도구 이름 행")
new = lines[i].replace(", 용량 응답 |", " |", 1)
log.append(("3절 용량 응답", lines[i], new))
lines[i] = new

i = find_one(lambda l: l.startswith("| 구획, 구획 하계, 거대 나무, 창×창 쌍, 쌍의 무게, $k$-단조성, 한 변수 확인, 둘째 큰 나무 |"), "3절 9.5 도구 이름 행")
new = lines[i].replace(", 둘째 큰 나무 |", " |", 1)
log.append(("3절 둘째 큰 나무", lines[i], new))
lines[i] = new

i = find_one(lambda l: l.startswith("| 기울인 무게, 기울인 차분 |"), "3절 기울인 행")
new = lines[i].replace("| 기울인 무게, 기울인 차분 | $\\mathfrak U_N=\\mathfrak a_Nz^N$, $\\mathcal D_N$ |", "| 기울인 무게 | $\\mathfrak U_N=\\mathfrak a_Nz^N$ |", 1)
if new == lines[i]:
    raise SystemExit("기울인 행: 치환 실패\n" + lines[i][:300])
log.append(("3절 기울인 차분", lines[i], new))
lines[i] = new

out = "\n".join(lines)
for what, a, b in log:
    print(f"[{what}]")
    print("  -", a[:260])
    if b:
        print("  +", b[:260])
if DRY:
    print("(dry run; 파일은 바꾸지 않음)")
elif out != orig:
    io.open(P, "w", encoding="utf-8", newline="\n").write(out)
    print("patched 장부_v2.md")
else:
    print("unchanged")
