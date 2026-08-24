# -*- coding: utf-8 -*-
"""조각.py — 조각의 구간 연산·판독·적용 엔진. 규약의 정본은 계약/조각.md다.

내부 좌표는 2배 정수다: 행 n은 2n, 행 n과 n+1 사이의 틈은 2n+1이다.
구간은 [시작2, 끝2] 닫힌 구간이고 시작2 ≤ 끝2다. 반정수 연산을 정수로 닫아
부동소수 비교를 없앤다.

담는 것 다섯:

- 좌표 표기의 해석·재생: `parse_좌표` / `format_좌표` — 표기 둘
  (`<경로> <a>~<b>행` / `<경로> 행 <n> 뒤`)은 계약/조각.md 2절이 닫는다
- 교차와 정규화: `intersects` — 공식 하나(max(시작) ≤ min(끝)) /
  `normalize` — 교차하는 구간의 병합(계약/조각.md 4·6절)
- 항목 절의 칸 분해: `split_cells` — `### <칸>` 제목 줄(울타리 밖)로 절
  본문을 가른다. 조각 칸(`### 조각 <k> — <좌표>`)의 동적 이름 때문에
  vrlib.parse_cells(닫힌 이름 목록)를 쓰지 못한다
- 조각 칸의 판독: `parse_조각_cell` — 라벨 줄(`원래:`·`대체:`·
  `대체: 원래대로`)과 코드 울타리 블록의 짝(계약/조각.md 3절)
- 적용 엔진: `apply_pieces` — 파일 하나의 줄 목록에 서로소 조각 목록을
  시작이 큰 것부터 역순 반영(계약/조각.md 7절).

조각 사전의 키는 여섯이다: 파일 / 시작2 / 끝2 / 표기(좌표 줄 축자) /
원래(구간 축자, 틈이면 None) / 대체(대체 문면, 미정이면 None).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_구간_RE = re.compile(r"^(?P<path>.+?) (?P<a>\d+)~(?P<b>\d+)행$")
_틈_RE = re.compile(r"^(?P<path>.+?) 행 (?P<n>\d+) 뒤$")


def parse_좌표(s: str) -> tuple[str, int, int] | None:
    """좌표 표기 하나를 (경로, 시작2, 끝2)로 해석한다. 표기 밖이면 None이다.

    `<경로> <a>~<b>행`(1 ≤ a ≤ b)은 (경로, 2a, 2b), `<경로> 행 <n> 뒤`(n ≥ 0)는
    (경로, 2n+1, 2n+1)이다. a > b나 a = 0은 표기 위반이라 None이다.
    """
    s = s.strip()
    m = _구간_RE.match(s)
    if m:
        a, b = int(m.group("a")), int(m.group("b"))
        if a < 1 or b < a:
            return None
        return m.group("path"), 2 * a, 2 * b
    m = _틈_RE.match(s)
    if m:
        n = int(m.group("n"))
        return m.group("path"), 2 * n + 1, 2 * n + 1
    return None


def format_좌표(path: str, s2: int, e2: int) -> str:
    """(경로, 시작2, 끝2)를 계약/조각.md 2절의 표기로 되돌린다.

    정수 구간은 `<경로> <a>~<b>행`, 틈 점 구간은 `<경로> 행 <n> 뒤`다.
    정규화가 만드는 구간은 양끝이 정수(교차 병합의 결과가 실재 행에서 시작·끝)
    이거나 틈 점이므로, 그 밖의 꼴(반정수 한쪽 끝)은 ValueError다.
    """
    if s2 % 2 == 1 and s2 == e2:
        return f"{path} 행 {(s2 - 1) // 2} 뒤"
    if s2 % 2 == 0 and e2 % 2 == 0:
        return f"{path} {s2 // 2}~{e2 // 2}행"
    raise ValueError(f"표기로 되돌릴 수 없는 구간: [{s2}, {e2}]")


def intersects(s1: int, e1: int, s2: int, e2: int) -> bool:
    """두 구간의 교차. 공식 하나: max(시작) ≤ min(끝) (계약/조각.md 4절)."""
    return max(s1, s2) <= min(e1, e2)


def normalize(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """구간 목록에서 교차하는 것끼리 병합해 시작 오름차순으로 준다.

    교차 판정은 intersects다 — 잇닿기만 한 구간([6, 6]과 [8, 10] = 3행과 4~5행)은
    병합하지 않는다.
    """
    out: list[list[int]] = []
    for s, e in sorted(spans):
        if out and intersects(out[-1][0], out[-1][1], s, e):
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [(s, e) for s, e in out]


def span_text(lines: list[str], s2: int, e2: int) -> str | None:
    """사본 줄 목록에서 정수 구간 [s2, e2]의 축자를 준다. 틈 점 구간은 None이다.

    구간이 파일 행 수를 벗어나면 ValueError다.
    """
    if s2 % 2 == 1:
        return None
    a, b = s2 // 2, e2 // 2
    if a < 1 or b > len(lines):
        raise ValueError(f"행 범위 밖 구간: {a}~{b}행 (파일 {len(lines)}행)")
    return "\n".join(lines[a - 1:b])


# ---------------------------------------------------------------- 칸 분해

_칸제목_RE = re.compile(r"^### (?P<name>.+?)\s*$")
_조각칸_RE = re.compile(r"^조각 (?P<k>\d+) — (?P<좌표>.+)$")
_FENCE_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")


def _fence_open(line: str) -> str | None:
    m = _FENCE_RE.match(line.strip())
    if not m:
        return None
    marker, rest = m.group(1), m.group(2)
    if marker[0] == "`" and "`" in rest:
        return None
    return marker


def _fence_close(line: str, open_marker: str) -> bool:
    s = line.strip()
    ch = open_marker[0]
    n = len(s) - len(s.lstrip(ch))
    return n >= len(open_marker) and s[n:].strip() == ""


@dataclass
class Cell:
    """`### <칸>` 칸 하나. line은 제목 줄의 절 안 상대 행(1-based)이다."""

    name: str
    body: str
    line: int


def split_cells(body: str) -> tuple[list[str], list[Cell]]:
    """절 본문을 (첫 칸 앞의 머리 줄들, 칸 목록)으로 가른다.

    칸 마커는 울타리 밖의 `### <칸이름>` 제목 줄 하나다(계약이 닫은 직렬화).
    볼드·평문 콜론 변이와 `####` 이하 제목은 마커가 아니다. 조각 칸의 동적
    이름(`조각 <k> — <좌표>`)을 받으므로 이름 목록을 닫지 않는다.
    """
    head: list[str] = []
    cells: list[Cell] = []
    cur: Cell | None = None
    buf: list[str] = []
    open_marker: str | None = None

    def close():
        nonlocal cur, buf
        if cur is not None:
            cur.body = "\n".join(buf).strip("\n")
            cells.append(cur)
        cur, buf = None, []

    for no, line in enumerate(body.split("\n"), start=1):
        if open_marker is None:
            marker = _fence_open(line)
            if marker is not None:
                open_marker = marker
            else:
                m = _칸제목_RE.match(line)
                if m:
                    close()
                    cur = Cell(name=m.group("name").strip(), body="", line=no)
                    continue
        else:
            if _fence_close(line, open_marker):
                open_marker = None
        if cur is None:
            head.append(line)
        else:
            buf.append(line)
    close()
    return head, cells


def 조각칸_이름(name: str) -> tuple[int, str] | None:
    """칸 이름이 조각 칸(`조각 <k> — <좌표>`)이면 (k, 좌표 표기)를 준다."""
    m = _조각칸_RE.match(name)
    if m:
        return int(m.group("k")), m.group("좌표").strip()
    return None


# ---------------------------------------------------------------- 조각 칸 판독

_라벨_RE = re.compile(r"^(?P<label>원래|대체):\s*(?P<rest>.*)$")


def parse_조각_cell(body: str) -> tuple[dict[str, str | None], list[str]]:
    """조각 칸 본문을 ({"원래": …, "대체": …}, 오류 목록)으로 판독한다.

    서식은 계약/조각.md 3절이다: 라벨 줄(`원래:`·`대체:`) 바로 뒤에 코드 울타리
    블록 하나가 온다. `대체: 원래대로`(계약/병합.md)는 블록 없이 값
    "원래대로"로 선다. 사전에 없는 라벨은 그 칸에 그 블록이 없다는 뜻이다.
    오류는 좌표 없는 산문 서술이다 — 라벨 중복, 라벨 없는 블록, 블록 없는
    라벨, 「원래대로」 밖의 인라인 값.
    """
    values: dict[str, str | None] = {}
    errors: list[str] = []
    pending: str | None = None
    open_marker: str | None = None
    buf: list[str] = []
    for line in body.split("\n"):
        if open_marker is not None:
            if _fence_close(line, open_marker):
                open_marker = None
                if pending is None:
                    errors.append("라벨 없는 코드 블록")
                else:
                    values[pending] = "\n".join(buf)
                    pending = None
                buf = []
            else:
                buf.append(line)
            continue
        m = _라벨_RE.match(line.strip())
        if m:
            if pending is not None:
                errors.append(f"블록 없는 라벨: {pending}")
                pending = None
            label, rest = m.group("label"), m.group("rest").strip()
            if label in values:
                errors.append(f"라벨 중복: {label}")
                continue
            if rest == "원래대로" and label == "대체":
                values["대체"] = "원래대로"
            elif rest:
                errors.append(f"라벨 줄의 인라인 값: {label}: {rest}")
            else:
                pending = label
            continue
        marker = _fence_open(line)
        if marker is not None:
            open_marker = marker
            buf = []
    if pending is not None:
        errors.append(f"블록 없는 라벨: {pending}")
    if open_marker is not None:
        errors.append("닫히지 않은 코드 울타리")
    return values, errors


# ---------------------------------------------------------------- 적용 엔진

def apply_pieces(lines: list[str], pieces: list[dict]) -> list[str]:
    """파일 하나의 줄 목록에 조각 목록을 반영한 새 줄 목록을 준다.

    조각은 서로소여야 한다(호출자가 검사한다). 시작이 큰 것부터 역순으로
    반영하므로 앞선 쓰기가 뒤 조각의 좌표를 밀지 않는다(계약/조각.md 7절).
    대체 None(병합의 「원래대로」 해소 전)은 ValueError다 — 호출자가 해소를
    마친 조각만 넘긴다.
    """
    out = list(lines)
    ordered = sorted(pieces, key=lambda p: p["시작2"], reverse=True)
    for p in ordered:
        if p["대체"] is None:
            raise ValueError(f"대체 미해소 조각: {p.get('표기')}")
        repl = p["대체"].split("\n") if p["대체"] != "" else []
        s2, e2 = p["시작2"], p["끝2"]
        if s2 % 2 == 1:                      # 틈 삽입 — 행 n 뒤
            n = (s2 - 1) // 2
            out[n:n] = repl
        else:                                # 정수 구간 치환
            out[s2 // 2 - 1:e2 // 2] = repl
    return out
