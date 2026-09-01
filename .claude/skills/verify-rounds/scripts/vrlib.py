# -*- coding: utf-8 -*-
"""verify-rounds 공용 파서 모듈.

vr.py의 하위명령 전건이 이 모듈로 런 산출 파일을 읽는다. 담는 것은 여덟이다:

- frontmatter 파싱: `parse_frontmatter` / 수 키의 정수 해석 `fm_int` /
  수 키 대 실측의 검산 `check_count`·`check_review_counts`
- 울타리 인식 절 분할: `split_sections` — ```와 ~~~ 안의 `## ` 줄은 절 경계가 아니다.
  `stop_at_h1=True`면 울타리 밖 첫 `# ` 줄에서 분할을 멈춘다
- 절 구간 도구: `section_slices`(원문 줄 구간)·`find_section`·`replace_section`
- 칸 마커 인식: `parse_cells` — 계약(계약/수리.md·병합.md·심사.md 「산출
  서식」)이 닫은 `### <칸이름>` 제목 줄 하나만 마커다. 볼드·평문 콜론·평문
  대시 변이와 `####` 이하 제목(칸 내부 제목)은 마커가 아니다. 조각 칸처럼
  이름이 동적인 칸의 분해는 조각.py `split_cells`가 맡는다
- 심사 산출 파서 가족: 키 줄 해석 `parse_status_line`(판정·처분·결합·승계 —
  계약이 닫은 `<키>: <값>` 반각 축자만 받는다), 파일 판독
  `parse_review_text`(frontmatter·판정 절·`# 최선` 줄), 처분 어휘 `DISPOSITIONS`
- 좌표 줄 목록: `coord_lines` — 개행 종료 파일의 유령 마지막 원소를 뺀다
- 장부 본표 판독: `parse_ledger_table` (references/장부.md 본표 절의 열 여섯)
- 어긋남 좌표와 종료 규약: `Mismatch` / `emit` / `UsageError`

종료 코드 규약: exit 0 성공(stdout 수치 요약), exit 1 어긋남(stderr 좌표),
exit 2 사용·환경 오류. `emit`이 0/1을, `UsageError`가 2를 나른다.

파일 입출력은 utf-8을 명시한다. `read_text`가 파일의 개행 스타일(CRLF·LF)을
감지해 접어 읽고, `write_text`가 같은 경로에 그 스타일을 복원해 쓴다.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_USAGE = 2


class UsageError(Exception):
    """사용·환경 오류(인자 결손·파일 부재·판독 불가). vr.py가 exit 2로 바꾼다."""


@dataclass
class Mismatch:
    """어긋남 하나의 좌표. line이 없는 어긋남(파일 단위)은 None을 둔다."""

    file: str
    line: int | None
    expected: str
    actual: str

    def format(self) -> str:
        pos = str(self.line) if self.line is not None else "-"
        return f"{self.file}:{pos} 기대={self.expected} 실측={self.actual}"


def emit(mismatches: Sequence[Mismatch], success_lines: Sequence[str]) -> int:
    """어긋남이 있으면 stderr에 좌표 전건을 내고 1을, 없으면 stdout에 수치 요약을 내고 0을 준다."""
    if mismatches:
        for m in mismatches:
            print(m.format(), file=sys.stderr)
        return EXIT_MISMATCH
    for line in success_lines:
        print(line)
    return EXIT_OK


# 파일 경로 → 개행 스타일("\r\n" 또는 "\n"). read_text가 감지하고 write_text가 복원한다.
_NEWLINE_STYLE: dict[str, str] = {}


def _style_key(path) -> str:
    return str(Path(path).resolve())


def read_text(path) -> str:
    """utf-8로 파일을 읽어 개행을 "\\n"으로 접어 준다. 부재·판독 불가는 UsageError(exit 2 사유)다.

    파일의 개행 스타일(CRLF면 파일 단위 단일 스타일 가정)을 기억해 두고,
    같은 경로의 write_text가 그 스타일로 복원한다.
    """
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            raw = f.read()
    except OSError as e:
        raise UsageError(f"파일을 읽지 못함: {path} ({e})") from e
    except UnicodeDecodeError as e:
        raise UsageError(f"utf-8 판독 불가: {path} ({e})") from e
    _NEWLINE_STYLE[_style_key(path)] = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n")


def write_text(path, text: str) -> None:
    """utf-8로 파일을 쓴다. read_text가 기억한 그 경로의 개행 스타일을 복원한다.

    읽은 적 없는 경로(새 산출 파일)는 "\\n"으로 쓴다.
    """
    style = _NEWLINE_STYLE.get(_style_key(path), "\n")
    if style != "\n":
        text = text.replace("\n", style)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def coord_lines(text: str) -> tuple[list[str], bool]:
    """좌표·축자의 대상이 되는 줄 목록과 끝 개행 여부를 준다.

    개행으로 끝나는 파일을 split("\\n")하면 마지막에 빈 원소(유령 행)가 서서
    행 수가 1 크게 잡힌다 — 그 원소를 빼고, 끝 개행 여부를 따로 준다.
    빈 파일은 ([], False)다.
    """
    if text == "":
        return [], False
    trailing = text.endswith("\n")
    lines = text.split("\n")
    if trailing:
        lines.pop()
    return lines, trailing


# ---------------------------------------------------------------- frontmatter

def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """머리의 `---` frontmatter를 (키→값 문자열 사전, 본문 시작 행 번호 1-based)로 준다.

    frontmatter가 없으면 ({}, 1)이다. 값은 문자열 그대로 두고 정수 해석은 fm_int가 한다.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, 1
    fm: dict[str, str] = {}
    last_key: str | None = None
    for i, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fm, i + 1
        if line[:1].isspace() and line.strip().startswith("- ") and last_key:
            # 블록 목록 값(YAML 시퀀스): 직전 키의 값에 항목을 잇는다
            item = line.strip()[2:].strip()
            fm[last_key] = f"{fm[last_key]}, {item}" if fm[last_key] else item
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
            last_key = key.strip()
    return {}, 1  # 닫는 ---가 없으면 frontmatter가 아니다


def fm_int(fm: dict[str, str], key: str) -> int | None:
    """수 키(`항목`·`영역`·`조각`·`심사자 번호`·`승인`·`기각`)를 정수로 해석한다.

    키가 없으면 None, 값이 정수가 아니면 ValueError다.
    """
    if key not in fm:
        return None
    value = fm[key].strip()
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"frontmatter 키 「{key}」의 값이 정수가 아님: {value!r}")


# ---------------------------------------------------------------- 울타리와 절

_FENCE_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")


def _fence_open(line: str) -> str | None:
    """줄이 울타리 여는 줄이면 울타리 문자열(``` 등)을, 아니면 None을 준다."""
    m = _FENCE_RE.match(line.strip())
    if not m:
        return None
    marker, rest = m.group(1), m.group(2)
    if marker[0] == "`" and "`" in rest:
        return None  # 백틱 울타리의 정보 문자열에 백틱은 오지 못한다
    return marker


def _fence_close(line: str, open_marker: str) -> bool:
    """줄이 open_marker를 닫는 울타리인가. 같은 문자, 같은 길이 이상, 뒤는 공백뿐이다."""
    s = line.strip()
    ch = open_marker[0]
    n = len(s) - len(s.lstrip(ch))
    return n >= len(open_marker) and s[n:].strip() == ""


def iter_lines_fenced(lines: Iterable[str]):
    """(행 번호 1-based, 줄, 울타리 안 여부)를 낸다. 울타리 여닫는 줄 자체는 울타리 안으로 센다."""
    open_marker: str | None = None
    for no, line in enumerate(lines, start=1):
        if open_marker is None:
            marker = _fence_open(line)
            if marker is not None:
                open_marker = marker
                yield no, line, True
                continue
            yield no, line, False
        else:
            if _fence_close(line, open_marker):
                open_marker = None
                yield no, line, True
                continue
            yield no, line, True


@dataclass
class Section:
    """`## <절 제목>` 절 하나. start_line은 제목 줄의 1-based 행 번호다."""

    title: str
    body: str
    start_line: int


def split_sections(text: str, prefix: str = "## ",
                   stop_at_h1: bool = False) -> list[Section]:
    """울타리를 인식하며 텍스트를 `## <절 제목>` 단위로 가른다.

    울타리(```·~~~) 안의 `## ` 줄은 절 경계가 아니다. 첫 절 앞의 머리글은 버린다.
    stop_at_h1=True면 울타리 밖 첫 `# ` 줄(h1)에서 분할을 멈춘다 — 그 줄부터
    문서 끝까지는 어느 절에도 들지 않는다(계약/수리.md의 `# 수행 기록` 종단).
    """
    sections: list[Section] = []
    cur: Section | None = None
    body_lines: list[str] = []

    def close():
        nonlocal cur, body_lines
        if cur is not None:
            cur.body = "\n".join(body_lines)
            sections.append(cur)
        cur, body_lines = None, []

    for no, line, fenced in iter_lines_fenced(text.split("\n")):
        if stop_at_h1 and not fenced and line.startswith("# "):
            break
        if not fenced and line.startswith(prefix):
            close()
            cur = Section(title=line[len(prefix):].strip(), body="", start_line=no)
            continue
        if cur is not None:
            body_lines.append(line)
    close()
    return sections


# ---------------------------------------------------------------- 칸 마커

def match_cell_marker(line: str, name: str) -> str | None:
    """줄이 칸 name의 마커면 \"\"을, 아니면 None을 준다.

    계약(계약/수리.md·병합.md·심사.md 「산출 서식」)이 닫은 직렬화 하나만
    받는다: `### <칸이름>` — 제목 층 정확히 3, 제목 줄에 인라인 내용 없음.
    볼드(`**칸**`)·평문 콜론(`칸:`)·평문 대시(`칸 —`)·전각 콜론 변이는 마커가
    아니라 본문이고, `####` 이하 제목은 칸 내부 제목이므로 마커가 아니다.
    칸 이름으로 시작하기만 하는 본문 줄도 마커가 아니다.
    """
    s = line.strip()
    if re.match(r"^###\s+" + re.escape(name) + r"\s*$", s):
        return ""
    return None


def parse_cells(body: str, names: Sequence[str]) -> dict[str, str]:
    """절 본문에서 칸 이름→내용을 뽑는다.

    마커는 `### <칸이름>` 제목 줄 하나다(match_cell_marker). 마커 다음 줄부터
    다음 마커 직전까지가 그 칸의 내용이다. 울타리 안 줄은 마커로 보지 않는다.
    같은 칸이 두 번 나오면 내용을 개행으로 잇는다. 본문에 없는 칸은 사전에
    없다 — 부재 검사는 호출자가 한다.
    """
    cells: dict[str, list[str]] = {}
    cur: str | None = None
    for _no, line, fenced in iter_lines_fenced(body.split("\n")):
        if not fenced:
            hit = next((name for name in names
                        if match_cell_marker(line, name) is not None), None)
            if hit is not None:
                cur = hit
                cells.setdefault(cur, [])
                continue
        if cur is not None:
            cells[cur].append(line)
    return {name: "\n".join(parts).strip("\n") for name, parts in cells.items()}


# ---------------------------------------------------------------- 절 구간

def _section_marks(lines: Sequence[str]) -> list[tuple[int, str]]:
    """`## ` 절 제목 줄의 (0-based 줄 인덱스, 제목) 목록. 울타리 안 줄은 절 경계가 아니다."""
    marks: list[tuple[int, str]] = []
    for no, line, fenced in iter_lines_fenced(lines):
        if not fenced and line.startswith("## "):
            marks.append((no - 1, line[3:].strip()))
    return marks


def section_slices(text: str) -> tuple[list[str], list[tuple[str, int, int]]]:
    """텍스트를 (줄 목록, [(절 제목, 시작 줄 인덱스, 끝 줄 인덱스)])로 준다.

    절 전문을 원문 줄 그대로 옮기는 하위명령이 쓴다 — split_sections는 본문만 준다.
    구간은 0-based 반열림 [시작, 끝)이고 `## ` 제목 줄을 포함한다.
    울타리(```·~~~) 안의 `## ` 줄은 절 경계가 아니다.
    """
    lines = text.split("\n")
    marks = _section_marks(lines)
    out: list[tuple[str, int, int]] = []
    for k, (i, title) in enumerate(marks):
        j = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
        out.append((title, i, j))
    return lines, out


def find_section(lines: list[str], title: str) -> tuple[int, int] | None:
    """줄 목록에서 `## <title>` 절의 (제목 줄 색인, 절 끝 색인)을 준다. 0-based,
    끝은 배타 경계다. 울타리 안의 `## ` 줄은 절 경계가 아니다. 없으면 None이다."""
    marks = _section_marks(lines)
    for k, (i, t) in enumerate(marks):
        if t == title:
            end = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
            return i, end
    return None


def parse_frozen_outputs(path) -> list[str]:
    """동결문의 `## 산출물` 절에서 산출물 경로 전건을 읽는다(SKILL.md §7 0단계).

    절 본문의 `- <저장소 상대 경로>` 줄이 목록이고, 그 서식 밖의 줄은 무시한다
    (절 머리의 산문 한 줄을 허용한다). 경로는 백틱을 벗겨 받는다. 절이 없거나
    구간 줄이 하나도 없거나 절대 경로가 섞이면 UsageError(exit 2)다.
    """
    text = read_text(path)
    lines, _ = coord_lines(text)
    span = find_section(lines, "산출물")
    if span is None:
        raise UsageError(f"동결문에 `## 산출물` 절이 없음: {path}")
    out: list[str] = []
    for line in lines[span[0] + 1:span[1]]:
        s = line.strip()
        if not s.startswith("- "):
            continue
        p = s[2:].strip().strip("`").strip()
        if not p:
            continue
        parsed = Path(p)
        if parsed.is_absolute() or ".." in parsed.parts:
            raise UsageError(
                f"동결문 산출물 절의 저장소 밖 경로(저장소 상대 경로 계약): {p}")
        out.append(p)
    if not out:
        raise UsageError(
            f"동결문 산출물 절에 `- <경로>` 줄이 없음: {path}")
    dup = [p for p in out if out.count(p) > 1]
    if dup:
        raise UsageError(f"동결문 산출물 절의 중복 경로: {sorted(set(dup))[0]}")
    return out


def replace_section(lines: list[str], title: str, new_lines: list[str],
                    after_prefix: str | None = None) -> list[str]:
    """`## <title>` 절을 new_lines로 치환한 줄 목록을 준다.

    절이 없으면 새로 넣는다 — after_prefix가 주어지고 그 접두의 절이 있으면
    그 접두의 마지막 절 뒤에, 아니면 파일 끝에 넣는다. 그래서 같은 접두의
    절들이 만들어진 차례로 서고, 장부의 라운드 절이 references/장부.md
    「절 목록」의 유형 차례를 따른다. 다른 절의 줄은 바이트 그대로 둔다.
    """
    span = find_section(lines, title)
    if span is not None:
        s, e = span
        return lines[:s] + new_lines + lines[e:]
    insert_at = len(lines)
    if after_prefix is not None:
        marks = _section_marks(lines)
        for k, (_i, t) in enumerate(marks):
            if t.startswith(after_prefix):
                insert_at = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
    return lines[:insert_at] + new_lines + lines[insert_at:]


# ---------------------------------------------------------------- 심사 산출 파서

def parse_status_line(line: str, name: str) -> str | None:
    """줄이 `<name>: <값>` 줄이면 값을, 아니면 None을 준다.

    계약(계약/심사.md 「산출 서식」)이 닫은 축자 `<name>: <값>` 하나만 받는다 —
    반각 콜론과 뒤이은 공백 한 칸. 계약이 금지한 서식(볼드 감쌈, 전각 콜론,
    공백 없는 `<name>:<값>`, 목록 표지)은 키 줄로 서지 않는다. 값의 볼드도
    벗기지 않고 그대로 준다 — 닫힌 어휘 대조가 하류에서 거른다.
    """
    m = re.match(r"^" + re.escape(name) + r": (.*)$", line.strip())
    if m:
        return m.group(1).strip()
    return None


STATUS_KEYS = ("판정", "처분", "결합", "승계")

_최선줄_RE = re.compile(r"^(\S+): (.+)$")


def parse_review_text(text: str) -> tuple[dict[str, str], list[dict], list[dict]]:
    """심사 산출 하나를 (frontmatter, 판정 절 목록, 최선 줄 목록)으로 판독한다.

    최선 줄과 결합·처분 밖 키의 판독 경로는 서식 방어용으로 남긴 것이고, 현행
    계약(계약/심사.md)은 판정·처분·승계 세 키만 쓴다.

    계약이 닫은 서식을 축자로 강제한다: 판정 절 제목은 `## <항목 ID>` 한 줄이고,
    `#` 층 제목은 판정 절 밖의 절(공통 실측 절·`# 최선`)을 연다. `## 판정` 아래
    `### <항목 ID>` 같은 제목 층 변이는 판정 절로 서지 않는다 — 그 `##` 절이 항목
    ID 절이 아니게 되어 호출자의 검산(대상 대조·판정 절 부재)이 exit 1을 낸다.
    판정·처분·결합·승계 줄은 parse_status_line이 닫은 `<키>: <값>` 반각 축자만
    받는다 — 볼드 감쌈·전각 콜론·목록 표지 줄은 키 줄로 서지 않아 호출자의
    검산(판정 줄 부재)이 exit 1을 낸다. 울타리(```·~~~) 안의 제목·키 줄은 읽지
    않는다.

    판정 절 항목은 사전이다: {"id", "line"(제목 행 1-based), "body"(절 전문),
    "본문"(첫 판정 줄을 뺀 절 본문), "판정", "처분", "결합", "승계"(각 키 줄의
    첫 값, 없으면 None), "판정수"(판정 줄 출현 수)}. 최선 줄 목록의 원소는
    {"line", "raw", "겨냥", "지목"}이고 `# 최선` 절의 비공백 줄마다 하나다 —
    `<겨냥 ID>: <값>` 반각 축자 꼴이 아니면(전각 콜론 포함) 겨냥이 None이고,
    값 「없음」은 지목 빈 목록, ` · ` 복수 병기는 지목 목록으로 편다.
    """
    fm, _ = parse_frontmatter(text)
    sections: list[dict] = []
    best: list[dict] = []
    cur: dict | None = None
    in_best = False
    for no, line, fenced in iter_lines_fenced(text.split("\n")):
        if not fenced:
            if line.startswith("## "):
                cur = {"id": line[3:].strip(), "line": no, "_lines": []}
                sections.append(cur)
                in_best = False
                continue
            if line.startswith("# "):
                cur = None
                in_best = line[2:].strip() == "최선"
                continue
            if in_best:
                s = line.strip()
                if s:
                    m = _최선줄_RE.match(s)
                    if m:
                        vals = [] if m.group(2).strip() == "없음" else [
                            x.strip() for x in m.group(2).split("·") if x.strip()]
                        best.append({"line": no, "raw": s,
                                     "겨냥": m.group(1), "지목": vals})
                    else:
                        best.append({"line": no, "raw": s, "겨냥": None, "지목": []})
                continue
        if cur is not None:
            cur["_lines"].append((line, fenced))
    for sec in sections:
        keys: dict[str, str] = {}
        count = 0
        body_lines: list[str] = []
        본문_lines: list[str] = []
        removed_first = False
        for line, fenced in sec.pop("_lines"):
            body_lines.append(line)
            is_판정 = False
            if not fenced:
                for key in STATUS_KEYS:
                    value = parse_status_line(line, key)
                    if value is not None:
                        if key == "판정":
                            count += 1
                            is_판정 = True
                        keys.setdefault(key, value)
                        break
            if is_판정 and not removed_first:
                removed_first = True
                continue
            본문_lines.append(line)
        sec["body"] = "\n".join(body_lines)
        sec["본문"] = "\n".join(본문_lines).strip("\n")
        for key in STATUS_KEYS:
            sec[key] = keys.get(key)
        sec["판정수"] = count
    return fm, sections, best


def check_count(path, fm: dict[str, str], key: str, actual: int) -> list[Mismatch]:
    """frontmatter 수 키 하나(`항목`·`영역`·`조각`)를 실측 절 수와 대조한다."""
    try:
        declared = fm_int(fm, key)
    except ValueError:
        return [Mismatch(file=str(path), line=1,
                         expected=f"{key}: <정수>", actual=f"{key}: {fm.get(key)}")]
    if declared is None:
        return [Mismatch(file=str(path), line=1,
                         expected=f"frontmatter에 {key}: <N>", actual=f"{key} 키 없음")]
    if declared != actual:
        return [Mismatch(file=str(path), line=1,
                         expected=str(declared), actual=str(actual))]
    return []


def check_review_counts(path, fm: dict[str, str], actual: int) -> list[Mismatch]:
    """심사 산출 frontmatter의 `승인`+`기각` 합을 실측 판정 절 수와 대조한다.

    합이 실측과 다르거나 키가 없거나 정수가 아니면 어긋남 좌표를 준다.
    """
    mismatches: list[Mismatch] = []
    total = 0
    for key in ("승인", "기각"):
        try:
            value = fm_int(fm, key)
        except ValueError:
            value = None
        if value is None:
            mismatches.append(Mismatch(
                file=str(path), line=1,
                expected=f"frontmatter에 {key}: <정수>", actual=f"{key}: {fm.get(key)}"))
        else:
            total += value
    if not mismatches and total != actual:
        mismatches.append(Mismatch(
            file=str(path), line=1, expected=str(total), actual=str(actual)))
    return mismatches


# 처분의 보수 순서(SKILL.md §7 3단계). 앞이 더 보수적이고, 이 넷 밖은 어휘 위반이다.
# 「호출자에게 전달」은 발견 항목에만 선다 — 항목 종류별 허용은 심사집계가 본다.
DISPOSITIONS = ("사용자에게 올린다", "호출자에게 전달", "승인하되 고치지 않는다", "수리한다")


# ---------------------------------------------------------------- 장부 본표

_표구분_RE = re.compile(r"^:?-+:?$")


def parse_ledger_table(section: Section, path, mismatches: list[Mismatch]) -> list[dict]:
    """장부 본표 절 하나를 행 목록으로 판독한다. 서식은 `references/장부.md`의 본표 절이다.

    행은 열 여섯(ID/위치/요지/심사/처분/상태)이고, 머리 행과 구분 행
    (`|---|…`)은 행으로 세지 않는다. 칸을 가르는 것은 앞에 역빗금이 없는 `|`
    하나이고, 칸 안의 `\\|`는 칸 경계가 아니다. 첫 6열 행이 머리 행이고 첫 칸이
    「ID」가 아니면 Mismatch다(머리 행 부재 — 첫 데이터 행이 머리로 사라지는 결함의
    거부, exit 1 사유). 열 수가 여섯이 아닌 표 줄은 Mismatch로 쌓는다(행 서식
    위반, exit 1 사유). 표 줄이 하나도 없으면 Mismatch다.
    행마다 {"ID","위치","요지","심사","처분","상태","행"(1-based)}을 준다.
    """
    rows: list[dict] = []
    header_seen = False
    table_lines = 0
    keys = ("ID", "위치", "요지", "심사", "처분", "상태")
    for offset, raw in enumerate(section.body.split("\n")):
        line_no = section.start_line + 1 + offset
        s = raw.strip()
        if not s.startswith("|"):
            continue
        table_lines += 1
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", s.strip("|"))]
        if all(_표구분_RE.match(c) for c in cells if c):
            continue
        if len(cells) != 6:
            mismatches.append(Mismatch(
                file=str(path), line=line_no, expected="본표 열 여섯", actual=f"열 {len(cells)}"))
            continue
        if not header_seen:
            header_seen = True  # 머리 행
            if cells[0] != "ID":
                mismatches.append(Mismatch(
                    file=str(path), line=line_no,
                    expected="본표 머리 행 첫 칸 「ID」", actual=cells[0]))
            continue
        row = dict(zip(keys, cells))
        row["ID"] = row["ID"].strip("`")
        row["행"] = line_no
        rows.append(row)
    if table_lines == 0:
        mismatches.append(Mismatch(
            file=str(path), line=section.start_line, expected="본표 표(| 행)", actual="없음"))
    return rows
