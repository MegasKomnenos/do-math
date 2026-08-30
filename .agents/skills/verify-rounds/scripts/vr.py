# -*- coding: utf-8 -*-
"""vr.py — verify-rounds 공식 스크립트 진입점.

호출: `python .agents/skills/verify-rounds/scripts/vr.py <하위명령> [옵션]`
실행 좌표는 저장소 루트이고, 저장소 상대 경로 인자는 그 좌표에서 푼다.
인자는 한국어 장옵션이고 단축 옵션과 기본값은 없다.

종료 코드: 0 성공(stdout에 수치 요약, 0건도 수치로) / 1 어긋남(stderr에
파일·행·기대·실측 좌표) / 2 사용·환경 오류(인자 결손·파일 부재·판독 불가).

하위명령 열아홉을 SKILL.md §5.7 표의 차례로 싣는다:

- 준비: 앵커 / 사본
- 수리: 영역검산 / 재정박 / 수리판독 / 수리검산
- 병합: 묶음 / 병합검산 / 병합자검산
- 심사: 심사지급 / 지급검산 / 상한 / 분할 / 심사집계 / 심사검산
- 적용: 적용
- 장부·판정: 장부머리 / 장부갱신 / 종료집계

각 하위명령의 입력 서식·인자·산출은 그 cmd_* 함수의 docstring이 닫는다.
공용 파서(frontmatter·절 분할·심사 산출 파서)는 vrlib.py, 조각의 구간
연산·판독·적용은 조각.py다.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vrlib  # noqa: E402
import 조각 as 조각lib  # noqa: E402


# ---------------------------------------------------------------- 공용

def _require_relative(paths: list[str]) -> None:
    """저장소 상대 경로 계약을 강제한다. 절대 경로는 사본의 구조 미러를 깨므로 UsageError다."""
    for p in paths:
        if Path(p).is_absolute():
            raise vrlib.UsageError(f"절대 경로는 받지 않음(저장소 상대 경로 계약): {p}")


def _copy_set(sources: list[str], single_dst: Path, dir_dst: Path) -> tuple[int, int]:
    """산출물 목록을 사본 규칙(하나면 single_dst, 여럿이면 dir_dst/<상대 경로>)으로 뜬다.

    바이트 그대로 복사한다. (건수, 바이트 합)을 준다. 절대 경로와 원본 부재는 UsageError다.
    """
    _require_relative(sources)
    for src in sources:
        if not Path(src).is_file():
            raise vrlib.UsageError(f"산출물 파일 부재: {src}")
    total = 0
    if len(sources) == 1:
        src = Path(sources[0])
        single_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, single_dst)
        total += single_dst.stat().st_size
    else:
        for s in sources:
            src = Path(s)
            dst = dir_dst / src
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            total += dst.stat().st_size
    return len(sources), total


def _round_dir(args) -> Path:
    return Path(getattr(args, "런")) / f"라운드{getattr(args, '라운드')}"


def _outputs(args) -> list[str]:
    """`--동결`이 가리키는 동결문의 「산출물」 절에서 산출물 경로 전건을 읽는다.

    산출물 목록의 정본은 동결문 하나다(SKILL.md §7 0단계) — 세션이 같은 목록을
    인자로 다시 적지 않으므로 목록 두 벌의 어긋남이 서지 않는다.
    """
    return vrlib.parse_frozen_outputs(getattr(args, "동결"))


def _copies(args, outputs: list[str]) -> list[str]:
    """그 라운드의 사본 경로 전건을 런·라운드·산출물 목록에서 파생한다.

    파생 규칙은 `사본` 하위명령의 배치 규칙과 같다 — 산출물이 하나면
    `라운드N/사본.<확장자>`, 여럿이면 `라운드N/사본/<저장소 상대 경로>`다.
    파생한 경로 중 없는 파일이 있으면 UsageError(exit 2)다.
    """
    round_dir = _round_dir(args)
    if len(outputs) == 1:
        paths = [round_dir / f"사본{Path(outputs[0]).suffix}"]
    else:
        paths = [round_dir / "사본" / p for p in outputs]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise vrlib.UsageError(
            f"사본 파일 부재({len(missing)}건, 첫째: {missing[0]}) — "
            f"`사본` 하위명령을 먼저 실행한다")
    return [p.as_posix() for p in paths]


def _고정지급(런) -> list[str]:
    """심사 파견의 고정 지급 경로 다섯을 파생한다(SKILL.md §4.2-7).

    공통 계약 둘·산출 계약·GLOSSARY는 이 스크립트의 스킬
    루트에서 파생하므로 정본과 미러 중 실행된 쪽을 가리킨다. 다섯째는
    `<런>/동결.md`다. 없는 파일이 있으면 UsageError(exit 2)다.
    """
    root = Path(__file__).resolve().parent.parent
    paths = [root / "계약" / "심사.md", root / "계약" / "조각.md",
             root / "계약" / "산출.md", root / "GLOSSARY.md",
             Path(런) / "동결.md"]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise vrlib.UsageError(f"고정 지급 파일 부재: {missing[0]}")
    return [p.as_posix() for p in paths]


def _load_json(path) -> dict:
    """JSON 파일을 읽는다. 부재·판독 불가·JSON 아님은 UsageError(exit 2)다."""
    text = vrlib.read_text(path)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise vrlib.UsageError(f"JSON 판독 불가: {path} ({e})") from e


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    vrlib.write_text(path, json.dumps(data, ensure_ascii=False, indent=1) + "\n")


def _resolve_copy(copies: list[str], path: str, where: str) -> str:
    """저장소 상대 경로 path에 대응하는 사본 파일 하나를 고른다.

    사본이 하나면 전 경로가 그 사본이다. 여럿이면 경로를 뒤끝으로 담는
    사본 하나가 대응하고, 대응이 없거나 둘 이상이면 UsageError다.
    """
    if len(copies) == 1:
        return copies[0]
    norm = path.replace("\\", "/")
    hits = [c for c in copies
            if c.replace("\\", "/") == norm or c.replace("\\", "/").endswith("/" + norm)]
    if len(hits) != 1:
        raise vrlib.UsageError(f"{where} 경로 {path}에 대응하는 사본이 {len(hits)}개")
    return hits[0]


def _fence_for(*texts: str) -> str:
    """내용에 든 백틱 런보다 긴 코드 울타리를 고른다."""
    n = 3
    for t in texts:
        for run in re.findall(r"`+", t or ""):
            n = max(n, len(run) + 1)
    return "`" * n


def _natural_key(item_id: str):
    """항목 ID를 (문자·수 교대) 자연 정렬 키로 바꾼다."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", item_id)]


_묶음ID_RE = re.compile(r"^R\d+-M\d+$")


# ---------------------------------------------------------------- 준비

def cmd_앵커(args) -> int:
    """앵커 — SKILL.md §7 0단계 5항. 첫 라운드 전 산출물 사본을 뜬다.

    인자: --런 <작업 디렉토리> / --동결 <동결.md>. 산출물 목록은 동결문
    「산출물」 절의 `- <저장소 상대 경로>` 줄 전건이다.
    산출: 산출물이 파일 하나면 `<런>/앵커.<확장자>`, 여럿이면 `<런>/앵커/` 아래
    저장소 상대 경로 그대로. 앵커는 읽기 전용이므로 `<런>`에 앵커(파일이든
    디렉토리든)가 이미 있으면 뜨지 않고 exit 1이다.
    stdout: 「앵커 N건, 합 M바이트」.
    """
    run_dir = Path(getattr(args, "런"))
    existing = list(run_dir.glob("앵커*")) if run_dir.is_dir() else []
    if existing:
        m = vrlib.Mismatch(file=str(existing[0]), line=None,
                           expected="앵커 없음(앵커는 읽기 전용, 런마다 한 번 뜬다)",
                           actual="이미 존재")
        return vrlib.emit([m], [])
    sources = _outputs(args)
    suffix = Path(sources[0]).suffix
    n, total = _copy_set(sources, run_dir / f"앵커{suffix}", run_dir / "앵커")
    return vrlib.emit([], [f"앵커 {n}건, 합 {total}바이트"])


def cmd_사본(args) -> int:
    """사본 — SKILL.md §7 「라운드 준비 — 매 라운드」. 라운드 시작 시 산출물 사본을 뜬다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --동결 <동결.md>. 산출물 목록은
    동결문 「산출물」 절의 `- <저장소 상대 경로>` 줄 전건이다.
    산출: `<런>/라운드N/`이 없으면 만들고, 산출물이 파일 하나면 `라운드N/사본.<확장자>`,
    여럿이면 `라운드N/사본/` 아래 저장소 상대 경로 그대로. 이미 있으면 새 원본으로
    덮는다(§4.4 라운드 재시작 경로). 이 배치 규칙이 다른 하위명령의 사본 경로
    파생 규칙이다 — 사본 경로를 인자로 받는 하위명령은 없다.
    stdout: 「사본 N건, 합 M바이트 — 라운드N」.
    """
    round_dir = _round_dir(args)
    sources = _outputs(args)
    suffix = Path(sources[0]).suffix
    n, total = _copy_set(sources, round_dir / f"사본{suffix}", round_dir / "사본")
    return vrlib.emit([], [f"사본 {n}건, 합 {total}바이트 — 라운드{getattr(args, '라운드')}"])


# ---------------------------------------------------------------- 수리

_영역_구간_RE = re.compile(r"^- (?P<path>\S+)(?: 행 (?P<a>\d+)-(?P<b>\d+))?$")


def cmd_영역검산(args) -> int:
    """영역검산 — SKILL.md §7 1단계 「영역 검산」. 영역의 합집합·비중첩을 검사한다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --동결 <동결.md> /
    --명세 <영역 명세 파일>. 산출물 목록은 동결문 「산출물」 절에서 읽고, 사본
    경로는 런·라운드·산출물 목록에서 파생한다(`사본` 하위명령의 배치 규칙).

    명세 파일 서식(닫힌 서식, 위반은 exit 1):
      frontmatter에 `영역: <N>`(영역 수, 정수). 영역마다 `## <영역 이름>` 절 하나.
      절 본문의 줄은 빈 줄·구간 줄·축자 줄이다. 구간 줄은 둘 중 하나다:
        `- <산출물 원본 경로>`               (그 파일 전체)
        `- <산출물 원본 경로> 행 <시작>-<끝>` (1-based 양끝 포함 행 범위)
      재정박 확장 서식의 축자 줄(`시작 축자:`·`끝 축자:`)은 구간 부속으로
      받아 무시한다 — 같은 _영역명세.md를 재정박과 이 명령이 함께 쓴다.

    사본 대응: 구간 경로는 산출물 원본 경로이고, 행 수는 대응 사본에서 잰다.
    행은 개행 하나로 가르고 개행으로 끝난 파일의 마지막 빈 원소는 세지 않는다 —
    재정박·수리판독·적용이 좌표를 재는 셈법과 같다(vrlib.coord_lines).
    산출물이 하나면 전 경로가 그 사본이고, 여럿이면 경로를 뒤끝으로 담는 사본
    하나가 대응한다(재정박·수리판독과 같은 규칙). 대응이 없으면 exit 1이다.

    재정박 대응: 같은 라운드의 `<런>/라운드N/_재정박.json`이 있으면 행 범위
    구간은 명세의 동결행 대신 그 파일의 라운드행을 사용한다. 영역 이름·경로·
    동결행이 명세와 정확히 대응하지 않으면 exit 1이다. 재정박 파일이 없으면
    명세의 행 범위를 그대로 쓴다.

    검사: ① frontmatter 영역 수 = 실측 절 수 ② 구간 경로가 사본에 대응한다
    ③ 행 범위가 대응 사본의 행 수 안이다 ④ 구간 합집합 = 사본 전건(빠진 행
    없음) ⑤ 서로 비중첩(겹친 행 없음). 어긋나면 exit 1과 좌표.
    stdout(통과): 「통과 — 영역 N개, 산출물 M파일, 총 L행」과 영역별 「구간 K건, 행 수」.
    """
    spec_path = getattr(args, "명세")
    copies = _copies(args, _outputs(args))
    text = vrlib.read_text(spec_path)
    fm, _ = vrlib.parse_frontmatter(text)
    sections = vrlib.split_sections(text)
    mismatches: list[vrlib.Mismatch] = []

    try:
        declared = vrlib.fm_int(fm, "영역")
    except ValueError:
        declared = None
        mismatches.append(vrlib.Mismatch(
            file=str(spec_path), line=1, expected="영역: <정수>",
            actual=f"영역: {fm.get('영역')}"))
    if declared is None and "영역" not in fm:
        mismatches.append(vrlib.Mismatch(
            file=str(spec_path), line=1, expected="frontmatter에 영역: <N>",
            actual="영역 키 없음"))
    elif declared is not None and declared != len(sections):
        mismatches.append(vrlib.Mismatch(
            file=str(spec_path), line=1, expected=str(declared),
            actual=str(len(sections))))

    line_counts = {c: len(vrlib.coord_lines(vrlib.read_text(c))[0]) for c in copies}
    reanchor_path = _round_dir(args) / "_재정박.json"
    reanchored: dict[tuple[str, str, int, int], tuple[int, int]] | None = None
    if reanchor_path.is_file():
        data = _load_json(reanchor_path)
        if data.get("라운드") != getattr(args, "라운드"):
            raise vrlib.UsageError(
                f"재정박 라운드 불일치: {reanchor_path} "
                f"(기대 {getattr(args, '라운드')}, 실측 {data.get('라운드')})")
        reanchored = {}
        try:
            for area in data["영역"]:
                for span in area["구간"]:
                    frozen = span["동결행"]
                    current = span["라운드행"]
                    key = (area["이름"], span["경로"], int(frozen[0]), int(frozen[1]))
                    if key in reanchored:
                        raise vrlib.UsageError(f"재정박 구간 중복: {reanchor_path} ({key})")
                    reanchored[key] = (int(current[0]), int(current[1]))
        except (KeyError, TypeError, ValueError, IndexError) as e:
            raise vrlib.UsageError(f"재정박 서식 불일치: {reanchor_path}") from e
    used_reanchors: set[tuple[str, str, int, int]] = set()
    # 사본 → 행 번호 → 덮은 영역 이름 목록
    coverage = {c: {i: [] for i in range(1, n + 1)} for c, n in line_counts.items()}
    area_stats: list[tuple[str, int, int]] = []  # (영역 이름, 구간 수, 행 수)

    for sec in sections:
        spans = 0
        rows = 0
        for offset, raw in enumerate(sec.body.split("\n")):
            line_no = sec.start_line + 1 + offset
            s = raw.strip()
            if not s:
                continue
            if _축자_RE.match(s):
                continue  # 재정박 확장 서식의 축자 줄 — 구간 부속
            m = _영역_구간_RE.match(s)
            if not m:
                mismatches.append(vrlib.Mismatch(
                    file=str(spec_path), line=line_no,
                    expected="- <경로>[ 행 <시작>-<끝>] 또는 축자 줄", actual=s))
                continue
            path = m.group("path")
            try:
                copy = _resolve_copy(copies, path, f"{spec_path}:{line_no} 구간")
            except vrlib.UsageError:
                mismatches.append(vrlib.Mismatch(
                    file=str(spec_path), line=line_no,
                    expected="사본에 대응하는 산출물 원본 경로", actual=path))
                continue
            n = line_counts[copy]
            if m.group("a") is None and n == 0:
                # 0행 파일의 전체 파일 구간 — 덮을 행이 없는 유효한 빈 구간
                spans += 1
                continue
            if m.group("a") is None:
                a, b = 1, n
            else:
                frozen_a, frozen_b = int(m.group("a")), int(m.group("b"))
                key = (sec.title, path, frozen_a, frozen_b)
                if reanchored is not None:
                    current = reanchored.get(key)
                    if current is None:
                        mismatches.append(vrlib.Mismatch(
                            file=str(reanchor_path), line=None,
                            expected=f"재정박 구간 {key}", actual="없음"))
                        continue
                    used_reanchors.add(key)
                    a, b = current
                else:
                    a, b = frozen_a, frozen_b
            if a < 1 or b < a or b > n:
                mismatches.append(vrlib.Mismatch(
                    file=str(spec_path), line=line_no,
                    expected=f"1-{n} 안의 행 범위", actual=f"{a}-{b}"))
                continue
            spans += 1
            rows += b - a + 1
            for i in range(a, b + 1):
                coverage[copy][i].append(sec.title)
        area_stats.append((sec.title, spans, rows))

    if reanchored is not None:
        for key in sorted(set(reanchored) - used_reanchors):
            mismatches.append(vrlib.Mismatch(
                file=str(reanchor_path), line=None,
                expected="명세에 대응하는 재정박 구간", actual=f"남음 {key}"))

    def runs(nums):
        """정렬된 행 번호 목록을 (시작, 끝) 연속 구간 목록으로 접는다."""
        out = []
        for i in nums:
            if out and i == out[-1][1] + 1:
                out[-1][1] = i
            else:
                out.append([i, i])
        return out

    if not mismatches:  # 구간이 온전할 때만 합집합·비중첩을 잰다
        for copy in copies:
            missing = sorted(i for i, owners in coverage[copy].items() if not owners)
            for a, b in runs(missing):
                mismatches.append(vrlib.Mismatch(
                    file=copy, line=a, expected="영역 배정", actual=f"빠짐 {a}-{b}행"))
            overlapped = sorted(i for i, owners in coverage[copy].items() if len(owners) > 1)
            for a, b in runs(overlapped):
                owners = sorted(set(coverage[copy][a]))
                mismatches.append(vrlib.Mismatch(
                    file=copy, line=a, expected="비중첩",
                    actual=f"겹침 {a}-{b}행 (영역 {'·'.join(owners)})"))

    total_rows = sum(line_counts.values())
    lines = [f"통과 — 영역 {len(sections)}개, 산출물 {len(copies)}파일, 총 {total_rows}행"]
    for title, spans, rows in area_stats:
        lines.append(f"영역 {title}: 구간 {spans}건, {rows}행")
    return vrlib.emit(mismatches, lines)


_축자_RE = re.compile(r"^(?P<kind>시작|끝) 축자:(?P<value>.*)$")


def cmd_재정박(args) -> int:
    """재정박 — SKILL.md §7 1단계 「재정박」. 행 범위 영역의 축자를
    그 라운드 사본에서 찾아 그 라운드의 행 번호로 바꾼다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --동결 <동결.md> /
    --명세 <확장 영역 명세 파일>. 산출물 목록은 동결문 「산출물」 절에서 읽고,
    사본 경로는 런·라운드·산출물 목록에서 파생한다.

    확장 명세 서식(닫힌 서식, 위반은 exit 1): 영역검산의 명세 서식
    (frontmatter `영역: <N>`, 영역마다 `## <영역 이름>` 절, 구간 줄
    `- <경로>` 또는 `- <경로> 행 <시작>-<끝>`)에 행 범위 구간마다 바로 아래
    두 줄을 더한다. 들여쓰기는 자유고 줄 머리 서식은 축자다:
      시작 축자: <시작 행의 전문>
      끝 축자: <끝 행의 전문>
    콜론 뒤 한 칸 다음부터 줄 끝까지가 축자다. 파일 전체 구간(`- <경로>`)에는
    축자 줄을 두지 않는다. 행 범위의 수치는 동결문 시점 행 번호이고 이 명령은
    그 수치를 대조 없이 「동결행」으로 옮긴다.

    사본 대응: 산출물이 하나면 전 구간이 그 사본에서 정박한다. 여럿이면 구간
    경로를 뒤끝으로 담는(예: `사본/<구간 경로>`) 사본 하나가 대응하고, 대응이
    없거나 둘 이상이면 exit 1과 좌표다(영역검산·수리판독과 같은 처분).

    검사: frontmatter 영역 수 = 실측 절 수. 축자마다 사본에서 행 전체 일치로
    정확히 1회 — 없음·2회 이상·명세 결손(행 범위 구간의 축자 줄 결손, 빈
    축자)은 exit 1과 좌표다(§8 신호 6 재료). 재정박된 시작 행이 끝 행보다
    뒤면 exit 1이다.

    산출: `<런>/라운드N/_재정박.json` — {"라운드", "영역": [{"이름", "구간":
    [{"경로", "사본", "동결행": [a,b], "라운드행": [a2,b2]}]}]}. 행 범위 구간만
    담는다. stdout: 구간마다 「영역 <이름>: <경로> 행 a-b → a2-b2」와
    「재정박 K구간, 영역 N개」. 행 범위 구간이 없으면 「재정박 0구간」이다.
    """
    spec_path = getattr(args, "명세")
    copies = _copies(args, _outputs(args))
    text = vrlib.read_text(spec_path)
    fm, _ = vrlib.parse_frontmatter(text)
    sections = vrlib.split_sections(text)
    mismatches: list[vrlib.Mismatch] = vrlib.check_count(spec_path, fm, "영역", len(sections))

    copy_lines = {c: vrlib.coord_lines(vrlib.read_text(c))[0] for c in copies}

    def anchor(copy: str, verbatim: str) -> int | None:
        rows = [i for i, ln in enumerate(copy_lines[copy], start=1) if ln == verbatim]
        if len(rows) != 1:
            mismatches.append(vrlib.Mismatch(
                file=str(copy), line=None,
                expected=f"축자 「{verbatim}」 1회", actual=f"{len(rows)}회"))
            return None
        return rows[0]

    areas: list[dict] = []
    span_count = 0
    stdout_lines: list[str] = []
    for sec in sections:
        spans: list[dict] = []
        pending: dict | None = None  # 축자를 기다리는 행 범위 구간

        def close_pending():
            nonlocal pending, span_count
            if pending is None:
                return
            missing = [k for k in ("시작", "끝") if k not in pending["축자"]]
            for kind in missing:
                mismatches.append(vrlib.Mismatch(
                    file=str(spec_path), line=pending["line"],
                    expected=f"{kind} 축자: <행 전문>", actual="없음"))
            copy = None
            if not missing:
                try:
                    copy = _resolve_copy(copies, pending["경로"],
                                         f"{spec_path}:{pending['line']} 구간")
                except vrlib.UsageError:
                    mismatches.append(vrlib.Mismatch(
                        file=str(spec_path), line=pending["line"],
                        expected="사본에 대응하는 산출물 원본 경로",
                        actual=pending["경로"]))
            if copy is not None:
                a2 = anchor(copy, pending["축자"]["시작"])
                b2 = anchor(copy, pending["축자"]["끝"])
                if a2 is not None and b2 is not None:
                    if a2 > b2:
                        mismatches.append(vrlib.Mismatch(
                            file=str(copy), line=a2,
                            expected="시작 행 ≤ 끝 행", actual=f"{a2} > {b2}"))
                    else:
                        span_count += 1
                        spans.append({"경로": pending["경로"], "사본": copy,
                                      "동결행": pending["동결행"], "라운드행": [a2, b2]})
                        stdout_lines.append(
                            f"영역 {sec.title}: {pending['경로']} 행 "
                            f"{pending['동결행'][0]}-{pending['동결행'][1]} → {a2}-{b2}")
            pending = None

        for offset, raw in enumerate(sec.body.split("\n")):
            line_no = sec.start_line + 1 + offset
            s = raw.strip()
            if not s:
                continue
            m = _축자_RE.match(raw.lstrip())
            if m:
                if pending is None:
                    mismatches.append(vrlib.Mismatch(
                        file=str(spec_path), line=line_no,
                        expected="행 범위 구간 아래의 축자 줄", actual=s))
                    continue
                value = m.group("value")
                if value.startswith(" "):
                    value = value[1:]
                if not value:
                    mismatches.append(vrlib.Mismatch(
                        file=str(spec_path), line=line_no,
                        expected=f"{m.group('kind')} 축자: <행 전문>", actual="빈 축자"))
                    continue
                pending["축자"][m.group("kind")] = value
                if len(pending["축자"]) == 2:
                    close_pending()
                continue
            close_pending()
            m = _영역_구간_RE.match(s)
            if not m:
                mismatches.append(vrlib.Mismatch(
                    file=str(spec_path), line=line_no,
                    expected="- <경로>[ 행 <시작>-<끝>] 또는 시작·끝 축자 줄", actual=s))
                continue
            if m.group("a") is None:
                continue  # 파일 전체 구간은 재정박 대상이 아니다
            pending = {"경로": m.group("path"), "line": line_no,
                       "동결행": [int(m.group("a")), int(m.group("b"))], "축자": {}}
        close_pending()
        areas.append({"이름": sec.title, "구간": spans})

    if mismatches:
        return vrlib.emit(mismatches, [])
    out_dir = _round_dir(args)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "_재정박.json",
                {"라운드": getattr(args, "라운드"), "영역": areas})
    stdout_lines.append(f"재정박 {span_count}구간, 영역 {len(sections)}개")
    return vrlib.emit([], stdout_lines)


_수리기_RE = re.compile(r"수리_(\d+)")
수리_칸 = ("위치", "기준", "영향", "결합", "상신", "발견")


def _수리절_판독(path: str, sec: vrlib.Section, copies: list[str],
             copy_lines: dict[str, list[str]], outputs: list[str],
             mismatches: list[vrlib.Mismatch]) -> dict | None:
    """수리 산출의 항목 절 하나를 판독한다. 서식은 계약/수리.md·계약/조각.md다.

    반환: {"제목", "위치", "기준", "영향", "상신"(내용 또는 None), "발견"(내용 또는 None),
    "결합제목"(목록), "조각"(조각 사전 목록)} 또는 서식 위반이면 None(어긋남은
    mismatches에 쌓는다). 검사 넷: 조각 경로 ∈ outputs(산출물 원본 경로 전건),
    좌표의 사본 대응·행 수 안(틈은 n ≤ 사본 행 수), 원래 축자의 사본 실측
    대조, 항목 안 조각 쌍의 서로소(계약/조각.md 1절 — 같은 틈 중복 포함).
    """
    head, cells = 조각lib.split_cells(sec.body)
    found: dict[str, str] = {}
    pieces: list[dict] = []
    piece_numbers: list[int] = []
    ok = True
    for cell in cells:
        line_no = sec.start_line + cell.line
        pk = 조각lib.조각칸_이름(cell.name)
        if pk is not None:
            k, 표기 = pk
            parsed = 조각lib.parse_좌표(표기)
            if parsed is None:
                mismatches.append(vrlib.Mismatch(
                    file=path, line=line_no,
                    expected="조각 좌표 표기(계약/조각.md 2절)", actual=표기))
                ok = False
                continue
            fpath, s2, e2 = parsed
            if fpath not in outputs:
                mismatches.append(vrlib.Mismatch(
                    file=path, line=line_no,
                    expected="산출물 원본 경로(계약/조각.md 2절 — 사본 경로 금지)",
                    actual=fpath))
                ok = False
                continue
            values, errors = 조각lib.parse_조각_cell(cell.body)
            for err in errors:
                mismatches.append(vrlib.Mismatch(
                    file=path, line=line_no, expected="조각 칸 서식(계약/조각.md 3절)",
                    actual=err))
            if errors:
                ok = False
                continue
            if values.get("대체") == "원래대로":
                mismatches.append(vrlib.Mismatch(
                    file=path, line=line_no,
                    expected="대체 문면 블록(「원래대로」는 병합 산출 전용)",
                    actual="대체: 원래대로"))
                ok = False
                continue
            if "대체" not in values:
                mismatches.append(vrlib.Mismatch(
                    file=path, line=line_no, expected="대체: 블록", actual="없음"))
                ok = False
                continue
            try:
                copy = _resolve_copy(copies, fpath, f"{path}:{line_no} 조각")
            except vrlib.UsageError:
                mismatches.append(vrlib.Mismatch(
                    file=path, line=line_no,
                    expected="조각 경로에 대응하는 사본", actual=f"{fpath} 대응 없음"))
                ok = False
                continue
            if copy not in copy_lines:
                copy_lines[copy], _ = vrlib.coord_lines(vrlib.read_text(copy))
            if s2 % 2 == 1:                      # 틈 삽입
                if "원래" in values:
                    mismatches.append(vrlib.Mismatch(
                        file=path, line=line_no,
                        expected="틈 삽입 조각에 원래 블록 없음", actual="원래: 블록 실재"))
                    ok = False
                    continue
                n = (s2 - 1) // 2
                if n > len(copy_lines[copy]):
                    mismatches.append(vrlib.Mismatch(
                        file=path, line=line_no,
                        expected=f"틈 n ≤ 사본 행 수 {len(copy_lines[copy])}",
                        actual=f"행 {n} 뒤"))
                    ok = False
                    continue
                원래 = None
            else:
                if "원래" not in values:
                    mismatches.append(vrlib.Mismatch(
                        file=path, line=line_no, expected="원래: 블록", actual="없음"))
                    ok = False
                    continue
                try:
                    실측 = 조각lib.span_text(copy_lines[copy], s2, e2)
                except ValueError as e:
                    mismatches.append(vrlib.Mismatch(
                        file=path, line=line_no, expected="사본 행 범위 안 구간",
                        actual=str(e)))
                    ok = False
                    continue
                if values["원래"] != 실측:
                    mismatches.append(vrlib.Mismatch(
                        file=path, line=line_no,
                        expected=f"원래 축자 = 사본 {표기} 실측", actual="불일치"))
                    ok = False
                    continue
                원래 = values["원래"]
            piece_numbers.append(k)
            pieces.append({"파일": fpath, "시작2": s2, "끝2": e2, "표기": 표기,
                           "원래": 원래, "대체": values["대체"]})
            continue
        if cell.name not in 수리_칸:
            mismatches.append(vrlib.Mismatch(
                file=path, line=line_no,
                expected="칸 이름 여섯(계약/수리.md) 또는 조각 칸", actual=cell.name))
            ok = False
            continue
        found[cell.name] = cell.body
    for name in ("위치", "기준", "영향"):
        if name not in found:
            mismatches.append(vrlib.Mismatch(
                file=path, line=sec.start_line,
                expected=f"{sec.title}의 ### {name} 칸", actual="없음"))
            ok = False
    상신 = found.get("상신")
    발견 = found.get("발견")
    if 상신 is not None and pieces:
        mismatches.append(vrlib.Mismatch(
            file=path, line=sec.start_line,
            expected="조각 칸 또는 상신 칸 하나(혼용 금지)", actual="둘 다 실재"))
        ok = False
    if 발견 is not None and pieces:
        mismatches.append(vrlib.Mismatch(
            file=path, line=sec.start_line,
            expected="조각 칸 또는 발견 칸 하나(혼용 금지)", actual="둘 다 실재"))
        ok = False
    if 발견 is not None and 상신 is not None:
        mismatches.append(vrlib.Mismatch(
            file=path, line=sec.start_line,
            expected="상신 칸 또는 발견 칸 하나(혼용 금지)", actual="둘 다 실재"))
        ok = False
    if 상신 is None and 발견 is None and not pieces:
        mismatches.append(vrlib.Mismatch(
            file=path, line=sec.start_line,
            expected=f"{sec.title}의 조각 칸 하나 이상 또는 상신 칸 또는 발견 칸", actual="없음"))
        ok = False
    결합제목: list[str] = []
    if "결합" in found:
        for ln in found["결합"].split("\n"):
            s = ln.strip()
            if not s:
                continue
            m = re.match(r"^- (.+)$", s)
            if not m:
                mismatches.append(vrlib.Mismatch(
                    file=path, line=sec.start_line,
                    expected="결합 칸 줄 서식 `- <상대 항목의 절 제목 축자>`", actual=s))
                ok = False
                continue
            결합제목.append(m.group(1).strip())
    if piece_numbers != list(range(1, len(piece_numbers) + 1)):
        mismatches.append(vrlib.Mismatch(
            file=path, line=sec.start_line,
            expected="조각 순번 1부터 항목 안 조각 수까지 연속",
            actual=" · ".join(str(k) for k in piece_numbers) or "없음"))
        ok = False
    for i, a in enumerate(pieces):
        for b in pieces[i + 1:]:
            if a["파일"] == b["파일"] and 조각lib.intersects(
                    a["시작2"], a["끝2"], b["시작2"], b["끝2"]):
                mismatches.append(vrlib.Mismatch(
                    file=path, line=sec.start_line,
                    expected="항목 안 조각 쌍마다 서로소(계약/조각.md 1절)",
                    actual=f"{a['표기']} ↔ {b['표기']}"))
                ok = False
    if not ok:
        return None
    return {"제목": sec.title, "위치": found["위치"], "기준": found["기준"],
            "영향": found["영향"], "상신": 상신, "발견": 발견, "결합제목": 결합제목, "조각": pieces}


def _수리산출_검산(args, paths: list[str]) -> tuple[list[tuple[str, int, list[dict]]],
                                                   list[dict], list[vrlib.Mismatch]]:
    """수리 산출을 판독하고 ID·결합을 검산한다. 파일은 쓰지 않는다."""
    outputs = _outputs(args)
    copies = _copies(args, outputs)
    _require_relative(outputs)
    copy_lines: dict[str, list[str]] = {}
    mismatches: list[vrlib.Mismatch] = []
    라운드 = getattr(args, "라운드")

    수리별: list[tuple[str, int, list[dict]]] = []
    for path in paths:
        text = vrlib.read_text(path)
        fm, _ = vrlib.parse_frontmatter(text)
        if fm.get("유형") != "수리":
            mismatches.append(vrlib.Mismatch(
                file=path, line=1, expected="유형: 수리", actual=f"유형: {fm.get('유형')}"))
        if ("영역" in fm) == ("관점" in fm):
            mismatches.append(vrlib.Mismatch(
                file=path, line=1, expected="영역: 또는 관점: 키 하나",
                actual="둘 다 있거나 둘 다 없음"))
        m = _수리기_RE.search(Path(path).stem)
        if not m:
            raise vrlib.UsageError(f"파일 이름에서 기 번호를 읽지 못함: {path}")
        기 = int(m.group(1))
        structure = list(vrlib.iter_lines_fenced(text.split("\n")))
        h1 = [(no, line[2:].strip()) for no, line, fenced in structure
              if not fenced and line.startswith("# ")]
        if len(h1) != 1 or h1[0][1] != "수행 기록":
            actual = " / ".join(title for _no, title in h1) or "H1 절 없음"
            mismatches.append(vrlib.Mismatch(
                file=path, line=None,
                expected="항목 뒤 `# 수행 기록` 절 하나로 종단",
                actual=actual))
        sections = vrlib.split_sections(text, stop_at_h1=True)
        mismatches += vrlib.check_count(path, fm, "항목", len(sections))
        절들 = []
        for sec in sections:
            row = _수리절_판독(path, sec, copies, copy_lines, outputs, mismatches)
            if row is not None:
                row["파일"] = path
                절들.append(row)
        수리별.append((path, 기, 절들))
    if mismatches:
        return 수리별, [], mismatches

    항목들: list[dict] = []
    for path, 기, 절들 in 수리별:
        for row in 절들:
            row["기"] = 기
            항목들.append(row)
    for n, row in enumerate(항목들, start=1):
        row["id"] = f"R{라운드}-{n:02d}"
    제목색인: dict[tuple[int, str], list[str]] = {}
    for row in 항목들:
        제목색인.setdefault((row["기"], row["제목"]), []).append(row["id"])
    for row in 항목들:
        결합: list[str] = []
        for 제목 in row["결합제목"]:
            hits = 제목색인.get((row["기"], 제목), [])
            if len(hits) != 1:
                mismatches.append(vrlib.Mismatch(
                    file=row["파일"], line=None,
                    expected=f"결합 지목 「{제목}」이 같은 기의 항목 제목 1건과 일치",
                    actual=f"{len(hits)}건"))
                continue
            if hits[0] != row["id"]:
                결합.append(hits[0])
        row["결합"] = sorted(set(결합), key=_natural_key)
    ID색인 = {row["id"]: row for row in 항목들}
    for row in 항목들:
        if not row["결합"]:
            continue
        if not row["조각"]:
            mismatches.append(vrlib.Mismatch(
                file=row["파일"], line=None,
                expected="결합 고지는 조각 있는 항목 사이(계약/수리.md)",
                actual=f"{row['id']}({'상신 제안' if row['상신'] is not None else '발견'})의 결합 칸"))
            continue
        for other in row["결합"]:
            if not ID색인[other]["조각"]:
                mismatches.append(vrlib.Mismatch(
                    file=row["파일"], line=None,
                    expected="결합 고지는 조각 있는 항목 사이(계약/수리.md)",
                    actual=f"{row['id']} → {other}({'상신 제안' if ID색인[other]['상신'] is not None else '발견'})"))
    return 수리별, 항목들, mismatches


def cmd_수리검산(args) -> int:
    """수리검산 — 수리자 한 기의 산출을 판독한다. 어떤 파일도 만들거나 바꾸지 않는다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --동결 <동결.md> /
    --수리 <수리 산출 파일> 하나.

    검사: 수리판독과 같은 frontmatter·항목 칸·조각 경로·좌표·원래 축자·
    항목 안 서로소·결합 고지 검사를 그 수리 산출 하나에 수행한다.

    stdout: 수리 기 번호와 항목·조각·상신 제안·결합 간선 수. 파일 산출은 없다.
    """
    수리별, 항목들, mismatches = _수리산출_검산(args, [getattr(args, "수리")])
    if mismatches:
        return vrlib.emit(mismatches, [])
    path, 기, 절들 = 수리별[0]
    결합간선 = {tuple(sorted((r["id"], other), key=_natural_key))
            for r in 항목들 for other in r["결합"]}
    return vrlib.emit([], [
        f"수리 {기}기 ({Path(path).name}): 항목 {len(절들)}건",
        f"조각 {sum(len(r['조각']) for r in 항목들)}건, "
        f"상신 제안 {sum(1 for r in 항목들 if r['상신'] is not None)}건, "
        f"발견 {sum(1 for r in 항목들 if r['발견'] is not None)}건, "
        f"결합 간선 {len(결합간선)}건",
    ])


def cmd_수리판독(args) -> int:
    """수리판독 — SKILL.md §7 1단계 「판독」. 수리 산출 전건을 읽어 항목 정본을 세운다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --동결 <동결.md> /
    --수리 <수리 산출 파일> (반복, 파견 순서대로). 산출물 목록은 동결문
    「산출물」 절에서 읽고, 사본 경로는 런·라운드·산출물 목록에서 파생한다
    (대응 규칙은 재정박과 같다).

    입력 서식: 계약/수리.md의 산출 서식. frontmatter 유형·영역|관점·항목,
    항목마다 `## <제목>` 절과 칸들(위치·기준·영향 필수, 조각 칸 하나 이상
    또는 상신 칸, 결합 칸 선택), `# 수행 기록` 종단. 기 번호는 파일 이름의
    `수리_<기>`에서 읽는다.

    하는 것: ① frontmatter 검산(§5.5) ② 조각 검증 — 경로 ∈ 산출물 목록(사본
    경로를 적으면 어긋남), 좌표의 사본 대응·행 수 안(틈은 n ≤ 사본 행 수),
    원래 축자의 사본 실측 대조, 항목 안 조각 쌍의 서로소(같은 틈 중복 포함)
    ③ 항목마다 `R<라운드>-<순번>` ID 부여(파일 순서 × 절 순서) ④ 결합 고지의
    절 제목을 같은 기의 항목 ID로 해소 — 해소 불가와 상신 제안 항목(조각 0)
    지목은 exit 1 ⑤ 항목 전건의 `항목.md`·`_항목.json` 조립. 어긋남이
    하나라도 있으면 산출 파일을 쓰지 않고 exit 1이다 — §5.3 검산 절차로
    처리한다.

    산출: `<런>/라운드N/항목.md` — frontmatter `항목: <N>`, 항목마다
    `## <항목 ID>` 절(제목 줄, 위치·기준·영향 칸, 결합 칸(있을 때), 조각
    칸들 또는 상신 칸). `<런>/라운드N/_항목.json` — {라운드, 항목: [{id,
    제목, 기, 상신, 결합, 조각}]}. stdout: 기별 항목 수와
    항목·조각·상신·결합 수치 요약.
    """
    라운드 = getattr(args, "라운드")
    수리별, 항목들, mismatches = _수리산출_검산(args, getattr(args, "수리"))
    if mismatches:
        return vrlib.emit(mismatches, [])

    # 항목.md 조립
    out_lines = ["---", f"항목: {len(항목들)}", "---", ""]
    for row in 항목들:
        out_lines += [f"## {row['id']}", f"제목: {row['제목']}", ""]
        for name in ("위치", "기준", "영향"):
            out_lines += [f"### {name}", row[name], ""]
        if row["결합"]:
            out_lines += ["### 결합"] + [f"- {i}" for i in row["결합"]] + [""]
        if row["상신"] is not None:
            out_lines += ["### 상신", row["상신"], ""]
        if row["발견"] is not None:
            out_lines += ["### 발견", row["발견"], ""]
        for k, p in enumerate(row["조각"], start=1):
            out_lines.append(f"### 조각 {k} — {p['표기']}")
            fence = _fence_for(p["원래"] or "", p["대체"])
            if p["원래"] is not None:
                out_lines += ["원래:", fence, p["원래"], fence]
            out_lines += ["대체:", fence, p["대체"], fence, ""]
    round_dir = _round_dir(args)
    round_dir.mkdir(parents=True, exist_ok=True)
    vrlib.write_text(round_dir / "항목.md", "\n".join(out_lines).rstrip("\n") + "\n")

    _write_json(round_dir / "_항목.json", {"라운드": 라운드, "항목": [
        {"id": r["id"], "제목": r["제목"], "기": r["기"],
         "상신": r["상신"] is not None, "발견": r["발견"] is not None,
         "결합": r["결합"], "조각": r["조각"]}
        for r in 항목들]})

    결합간선 = {tuple(sorted((r["id"], o), key=_natural_key))
            for r in 항목들 for o in r["결합"]}
    lines = [f"항목 {len(항목들)}건"]
    for path, 기, 절들 in 수리별:
        lines.append(f"수리 {기}기 ({Path(path).name}): 항목 {len(절들)}건")
    lines += [
        f"조각 {sum(len(r['조각']) for r in 항목들)}건, "
        f"상신 제안 {sum(1 for r in 항목들 if r['상신'] is not None)}건, "
        f"발견 {sum(1 for r in 항목들 if r['발견'] is not None)}건, "
        f"결합 간선 {len(결합간선)}건",
        f"산출: {round_dir / '항목.md'} / {round_dir / '_항목.json'}",
    ]
    return vrlib.emit([], lines)


# ---------------------------------------------------------------- 병합

def cmd_묶음(args) -> int:
    """묶음 — SKILL.md §7 2단계 「묶음 형성」. 간선을 이행 폐쇄하고 병합 지급을 만든다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --동결 <동결.md>. 산출물
    목록은 동결문 「산출물」 절에서 읽고, 사본 경로는 런·라운드·산출물
    목록에서 파생한다. 입력은
    `<런>/라운드N/_항목.json`과 `항목.md`(수리판독 산출)다. 검산 둘:
    항목.md frontmatter `항목:` 대 실측 절 수(§5.5), 조각 경로 ∈ 산출물 목록.

    간선 둘: ① 교차 — 서로 다른 항목의 조각이 같은 파일에서 교차(공식은
    계약/조각.md 4절) ② 결합 — 수리자 고지(_항목.json의 결합). 상신 제안
    항목(조각 0)은 간선을 만들지 않는다(수리판독이 상신 항목 지목을 이미
    막는다). 두 간선을 합쳐 이행 폐쇄하고, 크기 2 이상의 연결 성분마다
    `R<라운드>-M<순번>` ID를 붙인다(순번은 구성 항목의 자연 정렬 최솟값 순).

    정규화: 묶음마다 구성 조각 전건을 파일별로 모아 교차하는 구간을 하나로
    합친다(계약/조각.md 6절). 정수 구간의 원래 축자는 사본에서 다시 뜬다.

    산출: 묶음마다 `병합지급_<묶음ID>.md` — frontmatter(묶음·구성·조각 수),
    `# 구성 항목` 아래 구성 항목 절 전문(항목.md 원문 줄 그대로), `# 조각 목록`
    아래 정규화 조각 칸들(원래 축자만, 틈은 라벨 없음). `_묶음.json` —
    {라운드, 묶음: [{id, 구성, 조각}], 단독: [항목 ID]}.
    stdout: 간선·묶음·단독 수치와 묶음별 구성.
    """
    round_dir = _round_dir(args)
    라운드 = getattr(args, "라운드")
    outputs = _outputs(args)
    copies = _copies(args, outputs)
    data = _load_json(round_dir / "_항목.json")
    항목들 = data.get("항목", [])
    항목색인 = {r["id"]: r for r in 항목들}

    항목md경로 = round_dir / "항목.md"
    항목md문 = vrlib.read_text(항목md경로)
    md_fm, _ = vrlib.parse_frontmatter(항목md문)
    mismatches = vrlib.check_count(항목md경로, md_fm, "항목",
                                   len(vrlib.split_sections(항목md문)))
    for r in 항목들:
        for p in r["조각"]:
            if p["파일"] not in outputs:
                mismatches.append(vrlib.Mismatch(
                    file=str(round_dir / "_항목.json"), line=None,
                    expected="조각 경로 ∈ 동결문 산출물 목록", actual=f"{r['id']}: {p['파일']}"))
    if mismatches:
        return vrlib.emit(mismatches, [])

    parent: dict[str, str] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    유효 = [r for r in 항목들 if r["조각"]]
    교차간선: list[tuple[str, str]] = []
    for i, a in enumerate(유효):
        for b in 유효[i + 1:]:
            hit = any(pa["파일"] == pb["파일"] and 조각lib.intersects(
                pa["시작2"], pa["끝2"], pb["시작2"], pb["끝2"])
                for pa in a["조각"] for pb in b["조각"])
            if hit:
                교차간선.append((a["id"], b["id"]))
    결합간선: list[tuple[str, str]] = []
    조각있음 = {r["id"] for r in 유효}
    for r in 항목들:
        for o in r.get("결합", []):
            if r["id"] in 조각있음 and o in 조각있음:
                pair = tuple(sorted((r["id"], o), key=_natural_key))
                if pair not in 결합간선:
                    결합간선.append(pair)
    for a, b in 교차간선 + 결합간선:
        union(a, b)

    comps: dict[str, list[str]] = {}
    for node in list(parent):
        comps.setdefault(find(node), []).append(node)
    members_list = sorted(
        (sorted(m, key=_natural_key) for m in comps.values() if len(m) >= 2),
        key=lambda m: _natural_key(m[0]))
    묶인 = {i for m in members_list for i in m}
    단독 = [r["id"] for r in 항목들 if r["id"] not in 묶인]

    md_lines, md_slices = vrlib.section_slices(항목md문)
    절구간 = {t: (i, j) for t, i, j in md_slices}

    copy_lines: dict[str, list[str]] = {}
    묶음들: list[dict] = []
    out_paths: list[str] = []
    for n, members in enumerate(members_list, start=1):
        bid = f"R{라운드}-M{n}"
        by_file: dict[str, list[tuple[int, int]]] = {}
        for mid in members:
            for p in 항목색인[mid]["조각"]:
                by_file.setdefault(p["파일"], []).append((p["시작2"], p["끝2"]))
        pieces: list[dict] = []
        for fpath in sorted(by_file):
            for s2, e2 in 조각lib.normalize(by_file[fpath]):
                표기 = 조각lib.format_좌표(fpath, s2, e2)
                if s2 % 2 == 0:
                    copy = _resolve_copy(copies, fpath, f"{bid} 조각")
                    if copy not in copy_lines:
                        copy_lines[copy], _ = vrlib.coord_lines(vrlib.read_text(copy))
                    원래 = 조각lib.span_text(copy_lines[copy], s2, e2)
                else:
                    원래 = None
                pieces.append({"파일": fpath, "시작2": s2, "끝2": e2,
                               "표기": 표기, "원래": 원래, "대체": None})
        묶음들.append({"id": bid, "구성": members, "조각": pieces})

        out = ["---", f"묶음: {bid}", f"구성: {' · '.join(members)}",
               f"조각: {len(pieces)}", "---", "", "# 구성 항목", ""]
        for mid in members:
            if mid not in 절구간:
                raise vrlib.UsageError(f"항목.md에 절 부재: {mid}")
            i, j = 절구간[mid]
            seg = md_lines[i:j]
            while seg and not seg[-1].strip():
                seg.pop()
            out += seg + [""]
        out += ["# 조각 목록", ""]
        for k, p in enumerate(pieces, start=1):
            out.append(f"### 조각 {k} — {p['표기']}")
            if p["원래"] is not None:
                fence = _fence_for(p["원래"])
                out += ["원래:", fence, p["원래"], fence]
            out.append("")
        dst = round_dir / f"병합지급_{bid}.md"
        vrlib.write_text(dst, "\n".join(out).rstrip("\n") + "\n")
        out_paths.append(str(dst))

    _write_json(round_dir / "_묶음.json",
                {"라운드": 라운드, "묶음": 묶음들, "단독": 단독})
    lines = [f"묶음 {len(묶음들)}건 (교차 간선 {len(교차간선)}건, "
             f"결합 간선 {len(결합간선)}건), 단독 {len(단독)}건"]
    for m in 묶음들:
        lines.append(f"{m['id']}: {' · '.join(m['구성'])} — 조각 {len(m['조각'])}건")
    lines += [f"산출: {p}" for p in out_paths]
    lines.append(f"산출: {round_dir / '_묶음.json'}")
    return vrlib.emit([], lines)


병합_칸 = ("위치", "기준", "영향", "근거")


def _병합지급_정보(path: str) -> dict:
    """병합 지급 파일에서 묶음 ID·구성·조각 키와 원래 축자를 읽는다."""
    text = vrlib.read_text(path)
    fm, _ = vrlib.parse_frontmatter(text)
    bid = fm.get("묶음")
    if not bid:
        raise vrlib.UsageError(f"병합 지급 frontmatter에 묶음 키 없음: {path}")
    sections = {s.title: s for s in vrlib.split_sections(text, prefix="# ")}
    if "조각 목록" not in sections:
        raise vrlib.UsageError(f"병합 지급에 # 조각 목록 절 없음: {path}")
    _head, cells = 조각lib.split_cells(sections["조각 목록"].body)
    pieces: list[dict] = []
    for cell in cells:
        pk = 조각lib.조각칸_이름(cell.name)
        if pk is None:
            raise vrlib.UsageError(f"병합 지급 조각 목록에 조각 밖 칸: {cell.name}")
        _k, 표기 = pk
        parsed = 조각lib.parse_좌표(표기)
        if parsed is None:
            raise vrlib.UsageError(f"병합 지급의 조각 좌표가 어긋남: {표기}")
        fpath, s2, e2 = parsed
        values, errors = 조각lib.parse_조각_cell(cell.body)
        if errors:
            raise vrlib.UsageError(f"병합 지급 조각 칸이 어긋남: {표기} — {' · '.join(errors)}")
        원래 = values.get("원래")
        if s2 % 2 == 0 and 원래 is None:
            raise vrlib.UsageError(f"병합 지급 정수 조각에 원래 블록 없음: {표기}")
        pieces.append({"파일": fpath, "시작2": s2, "끝2": e2,
                       "표기": 표기, "원래": 원래, "대체": None})
    try:
        declared = vrlib.fm_int(fm, "조각")
    except ValueError as e:
        raise vrlib.UsageError(f"병합 지급의 조각 수가 정수가 아님: {path}") from e
    if declared != len(pieces):
        raise vrlib.UsageError(
            f"병합 지급의 조각 수 불일치: frontmatter {declared}, 실측 {len(pieces)}")
    구성 = [x.strip() for x in fm.get("구성", "").split("·") if x.strip()]
    return {"id": bid, "구성": 구성, "조각": pieces}


def cmd_병합검산(args) -> int:
    """병합검산 — SKILL.md §7 2단계 「검산」. 병합 산출을 지급 키와 대조해 판독한다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --결번 <묶음ID> (반복 가능 —
    §5.3 병합 결번 경로. 그 묶음을 대조·산출에서 뺀다). 입력은 `_묶음.json`과
    결번 아닌 묶음마다 `<런>/라운드N/병합_<묶음ID>.md`(계약/병합.md의 산출
    서식)다. _묶음.json에 없는 --결번 값은 exit 2다.

    검사(위반은 exit 1과 좌표): ① frontmatter 유형·묶음 ID·조각 수(§5.5)
    ② `## <묶음ID>` 절 하나 ③ 위치·기준·영향·근거 칸 실재 ④ 조각 칸의 좌표
    키 = 지급 키 전건(초과·누락·중복·표기 불일치) ⑤ 조각마다 대체 블록 실재 —
    `대체: 원래대로`는 지급의 원래 축자로 해소하고(틈은 빈 대체), 원래 블록의
    옮겨 적기는 금지 위반이다.

    산출: `<런>/라운드N/_병합.json` — {라운드, 묶음: [{id, 구성, 위치, 기준,
    영향, 근거, 조각(대체 해소 완료)}]}. 결번 묶음은 담지 않는다.
    stdout: 묶음·조각·결번 수치 요약.
    """
    round_dir = _round_dir(args)
    지급 = getattr(args, "지급", None)
    if 지급 is not None:
        단건정보 = _병합지급_정보(지급)
        묶음정보 = {"라운드": getattr(args, "라운드"), "묶음": [단건정보]}
        단건 = 단건정보["id"]
    else:
        묶음정보 = _load_json(round_dir / "_묶음.json")
        단건 = None
    결번 = list(dict.fromkeys(getattr(args, "결번", None) or []))
    있는ID = {m["id"] for m in 묶음정보.get("묶음", [])}
    for bid in 결번:
        if bid not in 있는ID:
            raise vrlib.UsageError(f"_묶음.json에 없는 결번 묶음: {bid}")
    mismatches: list[vrlib.Mismatch] = []
    결과: list[dict] = []
    for m in 묶음정보.get("묶음", []):
        bid = m["id"]
        if 단건 is not None and bid != 단건:
            continue
        if bid in 결번:
            continue
        path = Path(getattr(args, "병합")) if 단건 is not None else round_dir / f"병합_{bid}.md"
        if not path.is_file():
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=None, expected="병합 산출 실재", actual="없음"))
            continue
        text = vrlib.read_text(path)
        fm, _ = vrlib.parse_frontmatter(text)
        if fm.get("유형") != "병합":
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=1, expected="유형: 병합",
                actual=f"유형: {fm.get('유형')}"))
        if fm.get("묶음") != bid:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=1, expected=f"묶음: {bid}",
                actual=f"묶음: {fm.get('묶음')}"))
        sections = vrlib.split_sections(text)
        if len(sections) != 1 or sections[0].title != bid:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=1, expected=f"`## {bid}` 절 하나",
                actual=f"절 {len(sections)}개"))
            continue
        sec = sections[0]
        head, cells = 조각lib.split_cells(sec.body)
        found: dict[str, str] = {}
        산출조각: dict[str, dict] = {}
        for cell in cells:
            line_no = sec.start_line + cell.line
            pk = 조각lib.조각칸_이름(cell.name)
            if pk is not None:
                _k, 표기 = pk
                values, errors = 조각lib.parse_조각_cell(cell.body)
                for err in errors:
                    mismatches.append(vrlib.Mismatch(
                        file=str(path), line=line_no,
                        expected="조각 칸 서식(계약/조각.md 3절)", actual=err))
                if "원래" in values:
                    mismatches.append(vrlib.Mismatch(
                        file=str(path), line=line_no,
                        expected="원래 블록 없음(지급이 정본, 옮겨 적기 금지)",
                        actual="원래: 블록 실재"))
                if 표기 in 산출조각:
                    mismatches.append(vrlib.Mismatch(
                        file=str(path), line=line_no,
                        expected="지급 키마다 조각 칸 하나",
                        actual=f"키 중복 「{표기}」"))
                    continue
                산출조각[표기] = values
                continue
            if cell.name in 병합_칸:
                found[cell.name] = cell.body
            else:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=line_no,
                    expected="칸 이름 넷(계약/병합.md) 또는 조각 칸", actual=cell.name))
        for name in 병합_칸:
            if name not in found:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=sec.start_line,
                    expected=f"### {name} 칸", actual="없음"))
        지급키 = [p["표기"] for p in m["조각"]]
        vrlib_mm = vrlib.check_count(path, fm, "조각", len(산출조각))
        mismatches += vrlib_mm
        for 표기 in 지급키:
            if 표기 not in 산출조각:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=None,
                    expected=f"지급 조각 키 「{표기}」", actual="없음"))
        for 표기 in 산출조각:
            if 표기 not in 지급키:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=None,
                    expected="지급 키 안의 조각만", actual=f"지급 밖 키 「{표기}」"))
        pieces: list[dict] = []
        for p in m["조각"]:
            values = 산출조각.get(p["표기"])
            if values is None:
                continue
            대체 = values.get("대체")
            if 대체 is None:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=None,
                    expected=f"「{p['표기']}」의 대체 블록 또는 대체: 원래대로",
                    actual="없음"))
                continue
            if 대체 == "원래대로":
                대체 = p["원래"] if p["원래"] is not None else ""
            pieces.append({**p, "대체": 대체})
        결과.append({"id": bid, "구성": m["구성"],
                   "위치": found.get("위치", ""), "기준": found.get("기준", ""),
                   "영향": found.get("영향", ""), "근거": found.get("근거", ""),
                   "조각": pieces})
    if mismatches:
        return vrlib.emit(mismatches, [])
    if 단건 is not None:
        row = 결과[0]
        return vrlib.emit([], [f"병합 {row['id']}: 조각 {len(row['조각'])}건"])
    _write_json(round_dir / "_병합.json",
                {"라운드": 묶음정보.get("라운드"), "묶음": 결과})
    lines = [f"병합 {len(결과)}건, 조각 {sum(len(r['조각']) for r in 결과)}건, "
             f"결번 {len(결번)}건",
             f"산출: {round_dir / '_병합.json'}"]
    return vrlib.emit([], lines)


def cmd_병합자검산(args) -> int:
    """병합자검산 — 병합자 한 기의 산출을 읽기 전용으로 검산한다.

    인자: --런 <작업 디렉토리> / --라운드 <N> /
    --지급 <병합 지급 파일> / --병합 <병합 산출 파일>.

    검사: 병합검산과 같은 frontmatter·절·필수 칸·지급 키·조각 서식을
    지정한 묶음 하나에 수행한다. 파일 산출은 없다.
    """
    return cmd_병합검산(args)


# ---------------------------------------------------------------- 심사

def cmd_심사지급(args) -> int:
    """심사지급 — SKILL.md §7 3단계 「지급 조립」. 심사 대상 전건을 한 파일로 모은다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --결번 <묶음ID> (반복 가능 —
    §5.3 병합 결번 경로. 그 묶음과 구성 항목을 심사 대상에서 뺀다). 입력은
    `항목.md`·`_묶음.json`·`_병합.json`(묶음 0건이면 `_병합.json` 없이 돈다)이다.
    검산: 항목.md frontmatter `항목:` 대 실측 절 수(§5.5, 어긋나면 exit 1).
    _묶음.json에 없는 --결번 값과 결번 아닌 묶음의 `_병합.json` 부재는 exit 2다.

    산출: `<런>/라운드N/심사대상.md` — frontmatter `항목: <N>`(단독 + 결번
    아닌 묶음 수). 단독 항목은 항목.md의 절 전문을 원문 줄 그대로 옮긴다.
    묶음 항목은 `## <묶음ID>` 절로 세우고 구성 줄, 병합 산출의 위치·기준·영향·
    근거 칸, 조각 칸(원래는 지급 정본, 대체는 해소 값)을 담는다. 항목 출처
    (기 번호)는 싣지 않는다.
    stdout: 「심사 대상 N건 — 단독 a, 병합 b」와 「결번 묶음 c건 (구성 항목 d건 제외)」.
    """
    round_dir = _round_dir(args)
    묶음정보 = _load_json(round_dir / "_묶음.json")
    단독 = 묶음정보.get("단독", [])
    결번 = list(dict.fromkeys(getattr(args, "결번") or []))
    있는ID = {m["id"] for m in 묶음정보.get("묶음", [])}
    for bid in 결번:
        if bid not in 있는ID:
            raise vrlib.UsageError(f"_묶음.json에 없는 결번 묶음: {bid}")
    묶음들 = [m for m in 묶음정보.get("묶음", []) if m["id"] not in 결번]
    결번구성 = sum(len(m["구성"]) for m in 묶음정보.get("묶음", [])
               if m["id"] in 결번)
    병합들 = []
    if 묶음들:
        병합들 = _load_json(round_dir / "_병합.json").get("묶음", [])
    병합색인 = {r["id"]: r for r in 병합들}
    for m in 묶음들:
        if m["id"] not in 병합색인:
            raise vrlib.UsageError(f"_병합.json에 묶음 부재: {m['id']}")

    항목md경로 = round_dir / "항목.md"
    항목md = vrlib.read_text(항목md경로)
    md_fm, _ = vrlib.parse_frontmatter(항목md)
    mismatches = vrlib.check_count(항목md경로, md_fm, "항목",
                                   len(vrlib.split_sections(항목md)))
    if mismatches:
        return vrlib.emit(mismatches, [])
    md_lines, md_slices = vrlib.section_slices(항목md)
    절구간 = {t: (i, j) for t, i, j in md_slices}

    out = ["---", f"항목: {len(단독) + len(묶음들)}", "---", ""]
    for iid in 단독:
        if iid not in 절구간:
            raise vrlib.UsageError(f"항목.md에 절 부재: {iid}")
        i, j = 절구간[iid]
        seg = md_lines[i:j]
        while seg and not seg[-1].strip():
            seg.pop()
        out += seg + [""]
    for m in 묶음들:
        r = 병합색인[m["id"]]
        out += [f"## {r['id']}", f"구성: {' · '.join(r['구성'])}", ""]
        for name in 병합_칸:
            out += [f"### {name}", r[name], ""]
        for k, p in enumerate(r["조각"], start=1):
            out.append(f"### 조각 {k} — {p['표기']}")
            fence = _fence_for(p["원래"] or "", p["대체"] or "")
            if p["원래"] is not None:
                out += ["원래:", fence, p["원래"], fence]
            out += ["대체:", fence, p["대체"], fence, ""]
    dst = round_dir / "심사대상.md"
    vrlib.write_text(dst, "\n".join(out).rstrip("\n") + "\n")
    return vrlib.emit([], [
        f"심사 대상 {len(단독) + len(묶음들)}건 — 단독 {len(단독)}, 병합 {len(묶음들)}",
        f"결번 묶음 {len(결번)}건 (구성 항목 {결번구성}건 제외)",
        f"산출: {dst}"])


def cmd_지급검산(args) -> int:
    """지급검산 — SKILL.md §5.5 「지급 전 검산」.

    인자: --파일 <입력 파일> / --기대 <N> (선택).
    검사: 파일 frontmatter의 `항목: <N>`(필수 키, 정수)과 실측 `## ` 절 수를
    대조한다. 울타리 안의 `## ` 줄은 절이 아니다. --기대를 주면 실측을 그 값과도
    대조한다. 어긋나면 exit 1과 좌표, 키 부재·비정수도 exit 1이다.
    stdout(통과): 「항목 N건 — frontmatter N = 실측 N[ = 기대 N]」.
    """
    path = getattr(args, "파일")
    text = vrlib.read_text(path)
    fm, _ = vrlib.parse_frontmatter(text)
    actual = len(vrlib.split_sections(text))
    mismatches: list[vrlib.Mismatch] = []
    try:
        declared = vrlib.fm_int(fm, "항목")
    except ValueError:
        declared = None
        mismatches.append(vrlib.Mismatch(
            file=str(path), line=1, expected="항목: <정수>",
            actual=f"항목: {fm.get('항목')}"))
    else:
        if declared is None:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=1, expected="frontmatter에 항목: <N>",
                actual="항목 키 없음"))
        elif declared != actual:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=1, expected=str(declared), actual=str(actual)))
    expected_n = getattr(args, "기대")
    if expected_n is not None and expected_n != actual:
        mismatches.append(vrlib.Mismatch(
            file=str(path), line=1, expected=str(expected_n), actual=str(actual)))
    summary = f"항목 {actual}건 — frontmatter {declared} = 실측 {actual}"
    if expected_n is not None:
        summary += f" = 기대 {expected_n}"
    return vrlib.emit(mismatches, [summary])


def cmd_상한(args) -> int:
    """상한 — SKILL.md §7 심사 분할 규칙과 §4.2-7. 측정·산정만 하고 분할은 하지 않는다.

    인자: --런 <작업 디렉토리> / --항목수 <N> /
    --지급 <파일 경로> (반복, 배치 가변 지급) / --항목상한 <N> /
    --입력상한 <N>. 두 상한의 0은 무제한이다(§4.2-5).

    고정 지급 목록은 인자가 아니라 파생값이다. SKILL.md §4.2-7이 공통 계약 둘,
    산출 계약, GLOSSARY, 동결문 다섯으로 닫는다. 앞 넷은 이
    스크립트의 스킬 루트에서, 동결문은 `<런>/동결.md`에서 파생한다. 산출물 원본과
    기준 원문은 좌표로만 주는 참조 대상이라 어느 쪽에도 들지 않는다. 파생 파일 중 없는
    파일이 있으면 UsageError(exit 2)다.
    산정: 항목상한 요구 분할 = ceil(항목수/항목상한). 고정 지급은 배치마다 실리므로
    입력상한 요구 분할 = ceil(가변 바이트 / (입력상한 - 고정 바이트)). 배치 수 =
    두 분할 수 중 큰 쪽. 고정 바이트가 단독으로 입력상한 이상이면(가변을 실을
    자리가 없으므로 같음도 포함) §8 신호 5이고 입력상한 요구 분할과 배치 수는
    「산정 불가」다. 바이트는 디스크 크기(십진)다.
    stdout: 항목수 / 고정지급·지급 바이트 / 합 / 두 분할 수 / 배치 수 /
    고정지급 단독 초과 여부의 수치 목록. 산정 결과와 무관하게 측정이 되면 exit 0이다.
    """
    def sizes(paths):
        total = 0
        for p in paths:
            f = Path(p)
            if not f.is_file():
                raise vrlib.UsageError(f"파일 부재: {p}")
            total += f.stat().st_size
        return total

    items = getattr(args, "항목수")
    fixed_paths = _고정지급(getattr(args, "런"))
    var_paths = getattr(args, "지급") or []
    item_cap = getattr(args, "항목상한")
    byte_cap = getattr(args, "입력상한")
    fixed = sizes(fixed_paths)
    var = sizes(var_paths)

    k_items = 1 if item_cap == 0 else max(1, math.ceil(items / item_cap))
    fixed_over = byte_cap > 0 and fixed >= byte_cap
    if byte_cap == 0:
        k_bytes: int | None = 1
    elif fixed_over:
        k_bytes = None
    else:
        k_bytes = max(1, math.ceil(var / (byte_cap - fixed))) if var > 0 else 1
    batches = "산정 불가" if k_bytes is None else str(max(k_items, k_bytes))
    lines = [
        f"항목수: {items}",
        f"고정지급: {len(fixed_paths)}파일 {fixed}바이트",
        f"지급: {len(var_paths)}파일 {var}바이트",
        f"합: {fixed + var}바이트",
        f"항목상한 요구 분할: {k_items}",
        f"입력상한 요구 분할: {'산정 불가' if k_bytes is None else k_bytes}",
        f"배치 수: {batches}",
        f"고정지급 단독 초과: {'예 (§8 신호 5)' if fixed_over else '아니오'}",
    ]
    return vrlib.emit([], lines)


def cmd_분할(args) -> int:
    """분할 — SKILL.md §7 심사 분할 규칙. 항목 파일을 배치 파일 전건으로 가른다.

    인자: --파일 <입력 파일> (항목마다 `## <항목 ID>` 절, frontmatter
    `항목: <N>`) / --배치수 <N> (분할 규칙이 정한 배치 수 — 산정은 상한
    명령의 몫이다).

    검사: frontmatter `항목` = 실측 절 수. 배치수만큼 빈 배치 없이 세울 수
    있는가(못 세우면 exit 1).

    산출: `<원래 이름>_배치<k>.md` 전건(1부터, 원래 파일 옆에). 각 배치는
    원래 frontmatter에서 `항목:` 값만 실측으로 바꾸고, 머리글(frontmatter와
    첫 절 사이)을 축자로 옮기며, 항목 절을 원문 줄 그대로 담는다. 항목을
    균등에 가깝게 가르되 항목 절을 가르지 않는다. 울타리 안 `## ` 줄은 절
    경계가 아니다.

    stdout: 배치마다 「배치k: 항목 n, m바이트」와 「배치 N개, 항목 합 M」.
    """
    path = getattr(args, "파일")
    n_batches = getattr(args, "배치수")
    text = vrlib.read_text(path)
    fm, body_start = vrlib.parse_frontmatter(text)
    lines, slices = vrlib.section_slices(text)
    mismatches = vrlib.check_count(path, fm, "항목", len(slices))
    if mismatches:
        return vrlib.emit(mismatches, [])

    ids = [t for t, _i, _j in slices]
    if n_batches > len(ids) or n_batches < 1:
        return vrlib.emit([vrlib.Mismatch(
            file=str(path), line=1,
            expected=f"배치 {n_batches}개를 빈 배치 없이 세울 항목 수",
            actual=f"항목 {len(ids)}건")], [])

    batches: list[list[int]] = []
    idx = 0
    items_left = len(ids)
    for left in range(n_batches, 0, -1):
        take = math.ceil(items_left / left)
        batches.append(list(range(idx, idx + take)))
        idx += take
        items_left -= take

    src = Path(path)
    fm_lines = lines[:body_start - 1]
    head_lines = lines[body_start - 1:slices[0][1]] if slices else []
    out_lines: list[str] = []
    for k, batch in enumerate(batches, start=1):
        fm_out = [f"항목: {len(batch)}" if re.match(r"^항목\s*:", ln) else ln
                  for ln in fm_lines]
        parts = fm_out + head_lines
        for s in batch:
            _title, i, j = slices[s]
            seg = lines[i:j]
            while seg and not seg[-1].strip():
                seg.pop()
            parts += seg + [""]
        dst = src.with_name(f"{src.stem}_배치{k}{src.suffix}")
        vrlib.write_text(dst, "\n".join(parts).rstrip("\n") + "\n")
        out_lines.append(f"배치{k}: 항목 {len(batch)}, {dst.stat().st_size}바이트")
    out_lines.append(f"배치 {len(batches)}개, 항목 합 {len(ids)}")
    return vrlib.emit([], out_lines)


# 심사 판정 절의 칸 이름 전건. 정본은 계약/심사.md 「산출 서식」이다.
심사_칸 = ("실측", "사유", "원인", "크기", "클래스", "상신안", "검토전개 실익")

# 판정 절의 필수 칸. 계약/심사.md 「산출 서식」이 판정 값마다 닫는다.
심사_필수칸 = {
    "기각": ("실측", "사유"),
    "승인": ("실측", "원인", "크기", "클래스"),
}


def _심사파일(path: str) -> tuple[int, dict, list[vrlib.Mismatch]]:
    """심사 산출 파일(계약/심사.md 서식) 하나를 판독한다.

    반환: (기 번호, 항목 사전, 어긋남 목록). 판독은 vrlib.parse_review_text다.
    항목 사전은 절 제목의 항목 ID → {"판정", "처분", "승계", "사유"}이고, 그
    키 집합이 이 파견이 판정한 항목의 목록이다(계약/심사.md 「산출 서식」).
    아래를 어긋남 목록에 담는다. frontmatter `유형` 값이 「심사」가 아닌 것,
    `심사자 번호` 부재·비정수, `승인`+`기각` 합과 실측 절 수의 어긋남(§5.5
    산출 판독의 대조), 판정 줄 부재·어휘 밖 값, 승인 절의 처분 줄 부재·어휘
    밖 값, 판정 절의 필수 칸 부재·빈 칸이다. 필수 칸은 기각이 실측·사유이고,
    승인이 실측·원인·크기·클래스다. 「사용자에게 올린다」는 상신안을 더 요구한다.
    발견 항목의 승인은 처분과 무관하게 검토전개 실익을 더 요구한다. 발견 여부는
    심사 대상이나 `_항목.json`과 대조한다(계약/심사.md 「산출 서식」).
    """
    text = vrlib.read_text(path)
    fm, secs, _best = vrlib.parse_review_text(text)
    mismatches: list[vrlib.Mismatch] = []
    if fm.get("유형") != "심사":
        mismatches.append(vrlib.Mismatch(
            file=str(path), line=1, expected="유형: 심사",
            actual=f"유형: {fm.get('유형')}"))
    기 = 0
    try:
        v = vrlib.fm_int(fm, "심사자 번호")
    except ValueError:
        v = None
    if v is None:
        mismatches.append(vrlib.Mismatch(
            file=str(path), line=1, expected="frontmatter에 심사자 번호: <N>",
            actual=f"심사자 번호: {fm.get('심사자 번호')}"))
    else:
        기 = v
    mismatches += vrlib.check_review_counts(path, fm, len(secs))
    if not fm.get("읽은 범위", "").strip():
        mismatches.append(vrlib.Mismatch(
            file=str(path), line=1,
            expected="frontmatter에 읽은 범위: <목록>",
            actual=f"읽은 범위: {fm.get('읽은 범위')}"))

    items: dict[str, dict] = {}
    for sec in secs:
        판정, 처분, 승계 = sec["판정"], sec["처분"], sec["승계"]
        if 판정 is None:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=sec["line"],
                expected="판정: 승인 또는 판정: 기각", actual=f"{sec['id']} 판정 줄 없음"))
            continue
        if 판정 not in ("승인", "기각"):
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=sec["line"],
                expected="판정 값 승인·기각", actual=판정))
            continue
        if 판정 == "승인":
            if 처분 is None:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=sec["line"],
                    expected=f"{sec['id']} 승인 절의 처분: <값>", actual="처분 줄 없음"))
            elif 처분 not in vrlib.DISPOSITIONS:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=sec["line"],
                    expected="처분 값 셋 중 하나(계약/심사.md)", actual=처분))
        칸 = vrlib.parse_cells(sec["body"], 심사_칸)
        for name in 심사_필수칸[판정]:
            if not 칸.get(name, "").strip():
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=sec["line"],
                    expected=f"{sec['id']} {판정} 절의 ### {name} 칸(계약/심사.md)",
                    actual="없음" if name not in 칸 else "빈 칸"))
        if 판정 == "승인":
            처분별칸 = {
                "사용자에게 올린다": "상신안",
                "호출자에게 전달": "검토전개 실익",
            }.get(처분)
            if 처분별칸 and not 칸.get(처분별칸, "").strip():
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=sec["line"],
                    expected=f"{sec['id']} 처분 「{처분}」의 ### {처분별칸} 칸(계약/심사.md)",
                    actual="없음" if 처분별칸 not in 칸 else "빈 칸"))
        items[sec["id"]] = {
            "판정": 판정, "처분": 처분, "승계": 승계,
            "사유": 칸.get("사유", "").strip() if 판정 == "기각" else "",
            "검토전개 실익": 칸.get("검토전개 실익", "").strip(),
        }
    return 기, items, mismatches


def cmd_심사검산(args) -> int:
    """심사검산 — 저장된 심사 산출 하나를 읽기 전용으로 검산한다.

    인자: --심사 <심사 산출 파일> / --기 <심사자 번호> /
    --대상 <그 파견의 심사 대상 파일> 또는 --항목 <재개 항목 ID>(반복).

    검사: 심사 산출의 frontmatter·판정·처분 서식, 심사자 번호, 심사 대상의
    frontmatter, 판정 항목 집합과 심사 대상 항목 집합의 일치. 파일 산출은 없다.
    """
    심사경로 = getattr(args, "심사")
    기, items, mismatches = _심사파일(심사경로)
    대상경로 = getattr(args, "대상", None)
    if 대상경로 is not None:
        대상문 = vrlib.read_text(대상경로)
        대상절 = vrlib.split_sections(대상문)
        fm, _ = vrlib.parse_frontmatter(대상문)
        mismatches += vrlib.check_count(대상경로, fm, "항목", len(대상절))
        전건 = {s.title for s in 대상절}
        발견전건 = {
            s.title for s in 대상절
            if vrlib.parse_cells(s.body, ("발견",)).get("발견", "").strip()
        }
    else:
        전건 = set(getattr(args, "항목") or [])
        발견전건 = set()
    기대기 = getattr(args, "기")
    if 기 != 기대기:
        mismatches.append(vrlib.Mismatch(
            file=심사경로, line=1, expected=f"심사자 번호: {기대기}",
            actual=f"심사자 번호: {기}"))
    실측 = set(items)
    if 실측 != 전건:
        남은 = " · ".join(sorted(전건 - 실측, key=_natural_key)) or "없음"
        초과 = " · ".join(sorted(실측 - 전건, key=_natural_key)) or "없음"
        mismatches.append(vrlib.Mismatch(
            file=심사경로, line=None,
            expected=f"판정 항목 = 심사 대상 {len(전건)}건",
            actual=f"판정 {len(실측)}건 — 남은 항목: {남은} / 대상 밖: {초과}"))
    for iid in sorted(발견전건 & 실측, key=_natural_key):
        row = items[iid]
        if row["판정"] == "승인" and not row["검토전개 실익"]:
            mismatches.append(vrlib.Mismatch(
                file=심사경로, line=None,
                expected=f"{iid}(발견) 승인 절의 ### 검토전개 실익 칸",
                actual="없음 또는 빈 칸"))
    if mismatches:
        return vrlib.emit(mismatches, [])
    승인 = sum(1 for row in items.values() if row["판정"] == "승인")
    기각 = sum(1 for row in items.values() if row["판정"] == "기각")
    return vrlib.emit([], [f"심사 {기}기: 판정 {len(items)}건, 승인 {승인}건, 기각 {기각}건"])


def cmd_심사집계(args) -> int:
    """심사집계 — SKILL.md §7 3단계 「집계」와 §5.3 덮개 검산.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --대상 <심사대상.md> /
    --심사 <심사 산출 파일> (반복) / --정족 <N> / --기수 <N> /
    --기각보관 <디렉토리> (선택) / --보관출처 <문자열> (선택, --기각보관과 함께
    준다). 한 기의 산출이 여러 파일이면(배치 분할, §5.6 재개) 그 파일 전건을
    --심사에 싣는다 — 기 번호는 frontmatter `심사자 번호`에서 읽고 같은 기의
    판정을 합친다.

    기각 보관: --기각보관과 --보관출처를 함께 주면, 기각 또는 「승인하되
    고치지 않는다」로 확정된 항목의 원문(`심사대상.md` 같은 ID 본문 축자)·판정(확정·승인기·
    기각기·처분)·근거(기각 사유 또는 처분기록)를
    `<디렉토리>/<출처>-라운드<N>.md`에 쓴다. 항목이 0건이어도 파일은 둔다.
    둘 중 하나만 주면 exit 2(UsageError)다.

    입력 서식: 심사대상.md는 frontmatter `항목: <N>`과 `## <항목 ID>` 절 전건.
    심사 산출은 `계약/심사.md`의 산출 서식이다. 판정·처분·승계 줄은 계약이
    닫은 `<키>: <값>` 반각 축자만 받는다. 닫힌 서식 위반은 exit 1이다.

    하는 것: ① 심사대상.md `항목` 대 실측 절 수 검산, 심사 파일마다
    `승인`+`기각` 대 실측 절 수 검산, 같은 기의 두 산출 파일이 같은 항목을
    거듭 판정했는지 검사 ② 기마다 덮개 검산 — 기 1~기수마다
    그 기의 판정 절이 덮은 항목 집합 = 대상 전건. 심사에는 결번이 없다
    (§5.3) — 덮지 못한 항목은 어긋남이고, 그 ID 목록이 §5.6 재개의 입력이다
    ③ 항목마다 승인 수·정족 판정 ④ 승인 항목의 처분 보수 병합(사용자에게
    올린다 > 승인하되 고치지 않는다 > 수리한다) — 어휘 밖 처분 값은 ①에서
    어긋남으로 잡히고 병합에 참여하지 않는다 ⑤ 상신 제안 항목(_항목.json의
    상신 참)의 처분 「수리한다」는 어휘 위반(exit 1) — 적용할 문면이 없다
    ⑥ `승계:` 줄 수집 ⑦ 기각 판정의 `### 사유` 칸 수집 ⑧ `--기각보관`과
    `--보관출처`가 있으면 기각·무처분 항목의 원문과 심사 기록을 보관한다.

    산출: `<런>/라운드N/_심사집계.json` — {라운드, 기수, 정족, 항목수,
    항목: [{id, 승인수, 승인기, 기각기, 확정, 처분, 처분기록, 승계,
    기각사유, 실익기록}], 승계, 수리, 무처분, 상신, 기각}. 어긋남이 있으면 산출 없이
    exit 1이다 — 어긋난 집계가 적용에 읽히지 않는다.
    stdout: 항목·기별 덮개·확정 수치 요약.
    """
    기각보관 = getattr(args, "기각보관", None)
    보관출처 = getattr(args, "보관출처", None)
    if bool(기각보관) != bool(보관출처):
        raise vrlib.UsageError("--기각보관과 --보관출처는 함께 준다")

    대상경로 = getattr(args, "대상")
    대상문 = vrlib.read_text(대상경로)
    대상절 = vrlib.split_sections(대상문)
    대상들 = [s.title for s in 대상절]
    fm, _ = vrlib.parse_frontmatter(대상문)
    mismatches = vrlib.check_count(대상경로, fm, "항목", len(대상절))

    round_dir = _round_dir(args)
    out = round_dir / "_심사집계.json"
    try:
        out.unlink(missing_ok=True)
    except OSError as e:
        raise vrlib.UsageError(
            f"이전 심사 집계를 지우지 못함: {out} ({e})") from e
    상신항목: set[str] = set()
    발견항목: set[str] = set()
    항목json = round_dir / "_항목.json"
    if 항목json.is_file():
        항목목록 = _load_json(항목json).get("항목", [])
        상신항목 = {r["id"] for r in 항목목록 if r.get("상신")}
        발견항목 = {r["id"] for r in 항목목록 if r.get("발견")}

    기수 = getattr(args, "기수")
    정족 = getattr(args, "정족")

    관측: dict[int, dict[str, dict]] = {}          # 기 → 항목 ID → 기록
    for path in getattr(args, "심사"):
        기, items, mm = _심사파일(path)
        mismatches.extend(mm)
        if 기 == 0:
            continue
        if not 1 <= 기 <= 기수:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=1,
                expected=f"심사자 번호 1~{기수}", actual=f"심사자 번호: {기}"))
            continue
        앞선 = 관측.setdefault(기, {})
        for iid in items:
            if iid in 앞선:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=None,
                    expected=f"기 {기}의 항목 {iid} 판정 1회",
                    actual="같은 기의 앞선 산출 파일이 이미 판정"))
            if iid not in 대상들:
                mismatches.append(vrlib.Mismatch(
                    file=str(path), line=None,
                    expected="심사대상.md에 실재하는 항목 ID", actual=iid))
        앞선.update(items)

    # 기마다 덮개 검산 — 배치 경계와 무관하게 판정한 항목 집합으로만 잰다
    # (§5.3 심사 결번 없음). 남은 항목 목록이 §5.6 재개의 입력이다.
    전건 = set(대상들)
    for 기 in range(1, 기수 + 1):
        실측 = set(관측.get(기, {}))
        if 실측 != 전건:
            남은 = " · ".join(sorted(전건 - 실측, key=_natural_key)) or "없음"
            초과 = " · ".join(sorted(실측 - 전건, key=_natural_key)) or "없음"
            mismatches.append(vrlib.Mismatch(
                file=str(대상경로), line=None,
                expected=f"기 {기}의 덮개 = 심사 대상 {len(전건)}건",
                actual=f"덮개 {len(실측)}건 — 남은 항목: {남은} / 대상 밖: {초과}"))

    # 항목별 집계
    rows = []
    수리, 무처분, 상신, 전달, 기각 = [], [], [], [], []
    승계목록 = []
    for iid in 대상들:
        판정들 = {기: 관측[기][iid] for 기 in 관측 if iid in 관측[기]}
        승인기 = sorted(기 for 기, d in 판정들.items() if d["판정"] == "승인")
        기각기 = sorted(기 for 기, d in 판정들.items() if d["판정"] == "기각")
        # 어휘 밖 처분 값은 _심사파일이 어긋남으로 이미 잡았다 — 병합에 넣지 않는다
        처분기록 = {기: 판정들[기]["처분"] for 기 in 승인기
                if 판정들[기]["처분"] in vrlib.DISPOSITIONS}
        기각사유 = {기: 판정들[기]["사유"] for 기 in 기각기 if 판정들[기]["사유"]}
        실익기록 = {기: 판정들[기]["검토전개 실익"] for 기 in 승인기
                if 판정들[기]["검토전개 실익"]}
        if iid in 상신항목:
            for 기, v in 처분기록.items():
                if v in ("수리한다", "호출자에게 전달"):
                    mismatches.append(vrlib.Mismatch(
                        file=str(대상경로), line=None,
                        expected=f"{iid}(상신 제안)의 처분은 둘(계약/심사.md)",
                        actual=f"기 {기}: {v}"))
        elif iid in 발견항목:
            for 기 in 승인기:
                if not 판정들[기]["검토전개 실익"]:
                    mismatches.append(vrlib.Mismatch(
                        file=str(대상경로), line=None,
                        expected=f"{iid}(발견) 승인 기 {기}의 검토전개 실익",
                        actual="없음 또는 빈 칸"))
            for 기, v in 처분기록.items():
                if v in ("수리한다", "사용자에게 올린다"):
                    mismatches.append(vrlib.Mismatch(
                        file=str(대상경로), line=None,
                        expected=f"{iid}(발견)의 처분은 둘 — 호출자에게 전달·승인하되 고치지 않는다(계약/심사.md)",
                        actual=f"기 {기}: {v}"))
        else:
            for 기, v in 처분기록.items():
                if v == "호출자에게 전달":
                    mismatches.append(vrlib.Mismatch(
                        file=str(대상경로), line=None,
                        expected=f"{iid}의 처분 — 「호출자에게 전달」은 발견 항목에만 선다(계약/심사.md)",
                        actual=f"기 {기}: {v}"))
        확정 = "승인" if len(승인기) >= 정족 else "기각"
        처분 = None
        if 확정 == "승인":
            for value in vrlib.DISPOSITIONS:                    # 보수 병합
                if value in 처분기록.values():
                    처분 = value
                    break
            {"수리한다": 수리, "승인하되 고치지 않는다": 무처분,
             "사용자에게 올린다": 상신, "호출자에게 전달": 전달}.get(처분, []).append(iid)
        else:
            기각.append(iid)
        for 기 in 승인기:
            if 판정들[기]["승계"]:
                승계목록.append({"항목": iid, "기": 기, "내용": 판정들[기]["승계"]})
        rows.append({
            "id": iid, "승인수": len(승인기), "승인기": 승인기, "기각기": 기각기,
            "확정": 확정, "처분": 처분,
            "처분기록": {str(k): v for k, v in sorted(처분기록.items())},
            "승계": [e for e in 승계목록 if e["항목"] == iid],
            "기각사유": {str(k): v for k, v in sorted(기각사유.items())},
            "실익기록": {str(k): v for k, v in sorted(실익기록.items())},
        })

    if mismatches:
        # 어긋난 집계를 파일로 남기면 적용이 그대로 읽는다 — 산출 없이 반환한다
        return vrlib.emit(mismatches, [])
    data = {
        "라운드": getattr(args, "라운드"), "기수": 기수, "정족": 정족,
        "항목수": len(대상들), "항목": rows, "승계": 승계목록,
        "수리": 수리, "무처분": 무처분, "상신": 상신, "전달": 전달, "기각": 기각,
    }
    lines = [
        f"항목 {len(대상들)}건, 기수 {기수}, 정족 {정족}",
        *[f"기 {기}: 덮개 {len(관측.get(기, {}))}건" for 기 in range(1, 기수 + 1)],
        f"승인 {len(수리) + len(무처분) + len(상신) + len(전달)}건 — 수리 {len(수리)} · "
        f"무처분 {len(무처분)} · 상신 {len(상신)} · 전달 {len(전달)} / 기각 {len(기각)}건",
        f"승계 {len(승계목록)}건",
        f"산출: {out}",
    ]
    if 기각보관:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", 보관출처):
            raise vrlib.UsageError(f"보관출처 어휘 위반: {보관출처}")
        대상원문맵 = {s.title: s.body for s in 대상절}
        보관대상 = 기각 + 무처분
        보관경로 = Path(기각보관) / f"{보관출처}-라운드{getattr(args, '라운드')}.md"
        blocks = [
            "---", "유형: 기각보관", f"출처: {보관출처}",
            f"라운드: {getattr(args, '라운드')}", f"항목: {len(보관대상)}", "---", "",
            f"# 기각 보관 — {보관출처} 라운드{getattr(args, '라운드')}", "",
        ]
        if not 보관대상:
            blocks.append("없음")
        else:
            row색인 = {r["id"]: r for r in rows}
            for iid in 보관대상:
                row = row색인[iid]
                blocks.append(f"## {iid}")
                blocks.append("")
                blocks.append("### 원문")
                blocks.append(대상원문맵[iid])
                blocks.append("")
                blocks.append("### 판정")
                blocks.append(
                    f"확정: {row['확정']} · 승인기 {row['승인기']} · "
                    f"기각기 {row['기각기']} · 처분: {row['처분'] or '없음'}")
                blocks.append(f"최종 판정: {row['확정']}")
                if row["처분"]:
                    blocks.append(f"최종 처분: {row['처분']}")
                blocks.append("")
                blocks.append("### 근거")
                if row["기각사유"]:
                    for 기, 사유 in row["기각사유"].items():
                        blocks.append(f"- 기 {기}: {사유}")
                elif row["처분기록"]:
                    for 기, 처분값 in row["처분기록"].items():
                        blocks.append(f"- 기 {기}: {처분값}")
                else:
                    blocks.append("없음")
                blocks.append("")
        try:
            보관경로.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return vrlib.emit([vrlib.Mismatch(
                file=str(보관경로), line=None,
                expected="기각 보관 디렉터리 생성", actual=str(e))], [])
        try:
            보관경로.write_text("\n".join(blocks), encoding="utf-8")
        except OSError as e:
            return vrlib.emit([vrlib.Mismatch(
                file=str(보관경로), line=None,
                expected="기각 보관 파일 쓰기", actual=str(e))], [])
        lines.append(f"기각 보관: {보관경로} — {len(보관대상)}건")

    _write_json(out, data)
    return vrlib.emit([], lines)


# ---------------------------------------------------------------- 적용

def cmd_적용(args) -> int:
    """적용 — SKILL.md §7 4단계. 확정 「수리한다」 항목의 조각을 산출물에 반영한다.

    인자: --런 <작업 디렉토리> / --라운드 <N> / --추가 <항목 ID> (반복 가능,
    §8 처리로 「수리한다」가 된 항목) / --제외 <항목 ID> (반복 가능) / --강제.
    입력은 `_항목.json`·`_심사집계.json`과(묶음이 있으면) `_병합.json`이다.
    `_적용.json`이 이미 있으면 재실행을 거부한다(exit 2) —
    틈 삽입은 재실행 시 중복 반영되므로 멱등이 아니다. §7 4단계 중단 복구
    (사본 되돌림) 뒤의 재실행만 --강제로 우회한다.

    반영 집합: (_심사집계.json의 수리 목록 ∪ --추가) − --제외. 묶음 ID는
    _병합.json의 조각을, 단독 항목은 _항목.json의 조각을 쓴다.

    검사(위반은 exit 1, 어떤 파일도 바꾸지 않는다): ① 반영 집합의 ID 실재와
    조각 실재 — 조각 0(상신 제안 항목)이 반영 집합에 들면 어긋남이다(적용할
    문면이 없다) ② 조각 전건이 쌍마다 서로소(계약/조각.md 7절의 전제 —
    같은 틈 중복 포함, 예외 없음) ③ 정수 구간마다 산출물 실물의 현재 축자 =
    조각의 원래 축자. ③의 어긋남은 런 밖 편집이나 스크립트 결함의 신호다 —
    §8 신호 6 재료.

    반영: 파일마다 시작이 큰 조각부터 역순으로 바꾼다. 전건 검증을 마친 뒤에만
    파일을 쓴다. 쓰기 도중 OS 오류가 나면 exit 2와 함께 쓰기를 마친 파일
    목록을 stderr에 낸다 — 복구는 SKILL.md §7 4단계 「중단 복구」다.

    산출: `<런>/라운드N/_적용.json` — {라운드, 적용: [항목 ID], 조각수,
    파일: [경로]}. stdout: 항목·조각·파일 수치 요약(0건도 수치로).
    """
    round_dir = _round_dir(args)
    적용경로 = round_dir / "_적용.json"
    if 적용경로.is_file() and not getattr(args, "강제"):
        raise vrlib.UsageError(
            f"_적용.json 실재 — 이 라운드는 이미 적용됐다(틈 삽입은 재실행 시 "
            f"중복 반영). 중단 복구 뒤라면 --강제로 재실행한다: {적용경로}")
    집계 = _load_json(round_dir / "_심사집계.json")
    항목색인 = {r["id"]: r for r in _load_json(round_dir / "_항목.json").get("항목", [])}
    묶음경로 = round_dir / "_병합.json"
    병합색인: dict[str, dict] = {}
    if 묶음경로.is_file():
        병합색인 = {r["id"]: r for r in _load_json(묶음경로).get("묶음", [])}

    ids = list(dict.fromkeys(집계.get("수리", []) + (getattr(args, "추가") or [])))
    for x in getattr(args, "제외") or []:
        if x in ids:
            ids.remove(x)
    mismatches: list[vrlib.Mismatch] = []
    pieces: list[dict] = []
    for iid in ids:
        if _묶음ID_RE.match(iid):
            src = 병합색인.get(iid)
        else:
            src = 항목색인.get(iid)
        if src is None:
            mismatches.append(vrlib.Mismatch(
                file=str(round_dir), line=None,
                expected=f"반영 항목 {iid}의 조각 정본", actual="없음"))
            continue
        if not src["조각"]:
            mismatches.append(vrlib.Mismatch(
                file=str(round_dir / "_항목.json"), line=None,
                expected=f"반영 항목 {iid}의 조각 1건 이상",
                actual="조각 0 (상신 제안 항목 — 적용할 문면 없음)"))
            continue
        for p in src["조각"]:
            if p["시작2"] % 2 == 1 and p["대체"] == "":
                continue  # 빈 틈 삽입은 반영할 것이 없다
            pieces.append({**p, "id": iid})
    if mismatches:
        return vrlib.emit(mismatches, [])

    # 서로소 검사 — 공식 하나, 같은 틈 중복 포함 예외 없음(계약/조각.md 4·7절)
    by_file: dict[str, list[dict]] = {}
    for p in pieces:
        by_file.setdefault(p["파일"], []).append(p)
    for fpath, plist in by_file.items():
        plist.sort(key=lambda p: (p["시작2"], p["끝2"]))
        for a, b in zip(plist, plist[1:]):
            if 조각lib.intersects(a["시작2"], a["끝2"], b["시작2"], b["끝2"]):
                mismatches.append(vrlib.Mismatch(
                    file=fpath, line=None,
                    expected="반영 조각 전건 서로소(계약/조각.md 7절)",
                    actual=f"{a['id']} {a['표기']} ↔ {b['id']} {b['표기']}"))
    if mismatches:
        return vrlib.emit(mismatches, [])

    # 축자 대조 — 전건 통과 후에만 쓴다
    file_lines: dict[str, list[str]] = {}
    file_trailing: dict[str, bool] = {}
    for fpath in by_file:
        file_lines[fpath], file_trailing[fpath] = vrlib.coord_lines(
            vrlib.read_text(fpath))
    for fpath, plist in by_file.items():
        for p in plist:
            if p["시작2"] % 2 == 1:
                n = (p["시작2"] - 1) // 2
                if n > len(file_lines[fpath]):
                    mismatches.append(vrlib.Mismatch(
                        file=fpath, line=None,
                        expected=f"{p['표기']} 행 범위 안",
                        actual=f"행 {n} 뒤 (파일 {len(file_lines[fpath])}행)"))
                continue
            try:
                실측 = 조각lib.span_text(file_lines[fpath], p["시작2"], p["끝2"])
            except ValueError as e:
                mismatches.append(vrlib.Mismatch(
                    file=fpath, line=None, expected=f"{p['표기']} 행 범위 안",
                    actual=str(e)))
                continue
            if 실측 != p["원래"]:
                mismatches.append(vrlib.Mismatch(
                    file=fpath, line=p["시작2"] // 2,
                    expected=f"{p['id']} {p['표기']}의 원래 축자 = 실물",
                    actual="불일치 (§8 신호 6 재료)"))
    if mismatches:
        return vrlib.emit(mismatches, [])

    written: list[str] = []
    try:
        for fpath, plist in by_file.items():
            new_lines = 조각lib.apply_pieces(file_lines[fpath], plist)
            text = "\n".join(new_lines)
            if file_trailing[fpath]:
                text += "\n"
            vrlib.write_text(fpath, text)
            written.append(fpath)
    except OSError as e:
        raise vrlib.UsageError(
            f"쓰기 실패: {fpath} ({e}) — 쓰기를 마친 파일: "
            f"{' · '.join(written) or '없음'}. 복구는 SKILL.md §7 4단계 중단 복구") from e

    _write_json(round_dir / "_적용.json", {
        "라운드": getattr(args, "라운드"), "적용": ids,
        "조각수": len(pieces), "파일": sorted(by_file)})
    return vrlib.emit([], [
        f"적용 {len(ids)}건, 조각 {len(pieces)}건, 파일 {len(by_file)}건",
        f"산출: {round_dir / '_적용.json'}"])


# ---------------------------------------------------------------- 장부

def _append_into_section(lines: list[str], title: str,
                         extra: list[str]) -> list[str]:
    """`## <title>` 절 끝에 extra 줄을 덧붙인다. 절의 「(해당 시 기재)」 자리표시
    줄은 지운다. 절이 없으면 파일 끝에 새 절을 만든다."""
    span = vrlib.find_section(lines, title)
    if span is None:
        body = lines[:]
        while body and body[-1].strip() == "":
            body.pop()
        return body + ["", f"## {title}", ""] + extra + [""]
    s, e = span
    sec = [ln for ln in lines[s:e] if ln.strip() != "(해당 시 기재)"]
    while sec and sec[-1].strip() == "":
        sec.pop()
    return lines[:s] + sec + extra + [""] + lines[e:]


_머리_필수 = ["파라미터 전건", "상한 측정값 대조", "영역 검산 결과"]
_머리_선택 = ["모델 배정 변경", "파라미터·배정의 도중 변경"]


def cmd_장부머리(args) -> int:
    """장부머리 — references/장부.md의 라운드 머리 기재.

    인자: --장부 <장부.md> / --라운드 <N> / --재료 <라운드 머리 재료 파일>.

    재료 파일 서식(이 하위명령이 정의): `## ` 절 이름은 다섯으로 닫는다 —
    필수 셋 「파라미터 전건」·「상한 측정값 대조」·「영역 검산 결과」,
    선택 둘 「모델 배정 변경」·「파라미터·배정의 도중 변경」(있을 때만 둔다).
    절 본문이 그 자리의 기재 내용이다. 필수 절 부재와 다섯 밖의 절 이름은
    exit 1이다.

    하는 것: 장부에 `## 라운드 <N> — 라운드 머리` 절을 만들거나 치환한다.
    절 본문은 재료 절마다 `- <절 이름>: <본문>` 한 자리다(여러 줄이면 이어지는
    줄을 두 칸 들여 잇는다). 절이 없으면 「라운드 <N> — 」 접두의 마지막 절
    뒤에, 그 접두의 절도 없으면 파일 끝에 넣는다. 다른 절은 바이트 그대로 둔다.

    stdout: 「라운드 머리 기재 — 자리 K곳」.
    """
    재료경로 = getattr(args, "재료")
    재료문 = vrlib.read_text(재료경로)
    secs = {s.title: s for s in vrlib.split_sections(재료문)}
    mismatches: list[vrlib.Mismatch] = []
    for title in secs:
        if title not in _머리_필수 + _머리_선택:
            mismatches.append(vrlib.Mismatch(
                file=str(재료경로), line=secs[title].start_line,
                expected="닫힌 절 이름 다섯(장부머리 docstring)", actual=title))
    for title in _머리_필수:
        if title not in secs:
            mismatches.append(vrlib.Mismatch(
                file=str(재료경로), line=1,
                expected=f"필수 절 「{title}」", actual="없음"))
    if mismatches:
        return vrlib.emit(mismatches, [])

    라운드 = getattr(args, "라운드")
    new = [f"## 라운드 {라운드} — 라운드 머리", ""]
    자리 = 0
    for title in _머리_필수 + _머리_선택:
        if title not in secs:
            continue
        content = [ln for ln in secs[title].body.split("\n") if ln.strip()]
        first = content[0] if content else "없음"
        new.append(f"- {title}: {first}")
        new.extend(f"  {ln}" for ln in content[1:])
        자리 += 1
    new.append("")

    장부경로 = getattr(args, "장부")
    lines = vrlib.read_text(장부경로).split("\n")
    lines = vrlib.replace_section(lines, f"라운드 {라운드} — 라운드 머리", new,
                                  after_prefix=f"라운드 {라운드} — ")
    vrlib.write_text(장부경로, "\n".join(lines))
    return vrlib.emit([], [f"라운드 머리 기재 — 자리 {자리}곳"])


def _본표_행_갱신(lines: list[str], 라운드: int, item_id: str,
              심사: str | None, 처분: str | None, 상태: str | None,
              mismatches: list[vrlib.Mismatch], 장부경로: str) -> None:
    """본표에서 ID가 전체 일치하는 행 하나의 칸을 바꾼다. 행 부재는 어긋남이다.

    ID 대조는 첫 칸의 축자 전체 일치다 — 접두 탐색이 R1-1 갱신으로 R1-12 행을
    오염시킨 실물 사고를 막는다. None인 칸은 두고, 바꾸는 행 밖의 줄은 바이트
    그대로 둔다. 본표 행은 여섯 열(ID/위치/요지/심사/처분/상태)이다.
    """
    span = vrlib.find_section(lines, f"라운드 {라운드} — 본표")
    if span is None:
        mismatches.append(vrlib.Mismatch(
            file=장부경로, line=None,
            expected=f"라운드 {라운드} — 본표 절", actual="없음"))
        return
    s, e = span
    for i in range(s + 1, e):
        line = lines[i]
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if not cells or cells[0].strip("`") != item_id:
            continue
        if len(cells) != 6:
            mismatches.append(vrlib.Mismatch(
                file=장부경로, line=i + 1,
                expected="본표 열 여섯(ID/위치/요지/심사/처분/상태)",
                actual=f"열 {len(cells)}"))
            return
        for idx, value in ((3, 심사), (4, 처분), (5, 상태)):
            if value is not None:
                cells[idx] = value
        lines[i] = "| " + " | ".join(cells) + " |"
        return
    mismatches.append(vrlib.Mismatch(
        file=장부경로, line=None,
        expected=f"본표 행 {item_id}", actual="없음"))


def _묶음_구성(lines: list[str], 라운드: int, bundle_id: str,
           mismatches: list[vrlib.Mismatch], 장부경로: str) -> list[str]:
    """장부 묶음 구성표에서 묶음 ID의 구성 항목 ID 전건을 준다."""
    span = vrlib.find_section(lines, f"라운드 {라운드} — 묶음 구성표")
    if span is None:
        mismatches.append(vrlib.Mismatch(
            file=장부경로, line=None,
            expected=f"라운드 {라운드} — 묶음 구성표 절", actual="없음"))
        return []
    for i in range(span[0] + 1, span[1]):
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))]
        if len(cells) >= 2 and cells[0] == bundle_id:
            return re.findall(r"R\d+-\d+", cells[1])
    mismatches.append(vrlib.Mismatch(
        file=장부경로, line=None,
        expected=f"묶음 구성표 행 {bundle_id}", actual="없음"))
    return []


def cmd_장부갱신(args) -> int:
    """장부갱신 — SKILL.md §7의 장부 기재 전건. 본표 서식은 references/장부.md다.

    인자: --장부 <장부.md> / --라운드 <N> / --모드 <제기|묶음|심사|적용> /
    --입력 <모드별 입력 파일>. 본표 행은 여섯 열(ID/위치/요지/심사/처분/상태)
    이고 행 대조는 ID 전체 일치다. 치환 실패·행 부재·절 부재는 exit 1과
    좌표이고, 그때 장부는 바꾸지 않는다(전건 성립 시에만 쓴다).

    모드 제기 — 입력은 `_항목.json`(수리판독 산출). 「라운드 <N> — 본표」 절을
    만들거나 치환한다. 항목마다 위치(첫 조각 좌표 또는 「상신 제안」·「발견」), 요지
    (제목), 심사·처분 「—」, 상태 「제기」 행을 세운다.

    모드 묶음 — 입력은 `_묶음.json`(묶음 산출). 「라운드 <N> — 묶음 구성표」
    절(묶음 ID/구성 항목/조각 수)을 만들거나 치환하고, 구성 항목 행의 상태를
    「병합」으로 바꾼다.

    모드 심사 — 입력은 `_심사집계.json`(심사집계 산출). 항목마다 심사 칸을
    「승인수/기수」로, 처분 칸을 확정 처분의 축자로(GLOSSARY 「처분」), 상태
    칸을 확정에 따라 적는다: 기각 → 처분 「—」·상태 「기각」 / 수리한다 →
    상태 「수리확정」 / 승인하되 고치지 않는다 → 상태 「무처분」 /
    사용자에게 올린다 → 상태 「상신」 / 호출자에게 전달 → 상태 「전달」. 묶음 ID는 묶음
    구성표의 구성 항목 행 전건에 전파한다. 기각 사유를 「라운드 <N> — 사유 절」
    에 덧붙인다(재실행하면 중복 기재된다 — 치환이 아니라 추가다).

    모드 적용 — 입력은 `_적용.json`(적용 산출). 반영 항목의 상태를 「적용」으로
    적고, 묶음 ID는 구성 항목 행 전건에 전파한다.

    stdout: 모드별 수치 요약(갱신 행 수·기재 건수, 0건도 수치로).
    """
    장부경로 = getattr(args, "장부")
    라운드 = getattr(args, "라운드")
    모드 = getattr(args, "모드")
    입력 = getattr(args, "입력")
    lines = vrlib.read_text(장부경로).split("\n")
    mismatches: list[vrlib.Mismatch] = []
    summary: list[str] = []

    if 모드 == "제기":
        항목들 = _load_json(입력).get("항목", [])
        new = [f"## 라운드 {라운드} — 본표", "",
               "| ID | 위치 | 요지 | 심사 | 처분 | 상태 |",
               "|---|---|---|---|---|---|"]
        for r in 항목들:
            위치 = (r["조각"][0]["표기"] if r["조각"]
                  else ("발견" if r.get("발견") else "상신 제안"))
            요지 = r["제목"].replace("|", "\\|")
            new.append(f"| {r['id']} | {위치} | {요지} | — | — | 제기 |")
        new.append("")
        lines = vrlib.replace_section(lines, f"라운드 {라운드} — 본표", new,
                                      after_prefix=f"라운드 {라운드} — ")
        summary = [f"본표 {len(항목들)}행"]

    elif 모드 == "묶음":
        data = _load_json(입력)
        묶음들 = data.get("묶음", [])
        new = [f"## 라운드 {라운드} — 묶음 구성표", "",
               "| 묶음 ID | 구성 항목 | 조각 수 |", "|---|---|---|"]
        for m in 묶음들:
            new.append(f"| {m['id']} | {' · '.join(m['구성'])} | {len(m['조각'])} |")
        new.append("")
        lines = vrlib.replace_section(lines, f"라운드 {라운드} — 묶음 구성표", new,
                                      after_prefix=f"라운드 {라운드} — ")
        전파 = 0
        for m in 묶음들:
            for member in m["구성"]:
                _본표_행_갱신(lines, 라운드, member, None, None, "병합",
                          mismatches, 장부경로)
                전파 += 1
        summary = [f"묶음 구성표 {len(묶음들)}행, 구성 전파 {전파}행"]

    elif 모드 == "심사":
        data = _load_json(입력)
        항목들 = data.get("항목", [])
        if "항목수" in data and data["항목수"] != len(항목들):
            mismatches.append(vrlib.Mismatch(
                file=str(입력), line=None, expected=str(data["항목수"]),
                actual=f"항목 목록 {len(항목들)}건"))
        기수 = data["기수"]
        사유줄: list[str] = []
        for r in 항목들:
            심사 = f"{r['승인수']}/{기수}"
            if r["확정"] == "기각":
                처분, 상태 = "—", "기각"
            elif r["처분"] == "수리한다":
                처분, 상태 = "수리한다", "수리확정"
            elif r["처분"] == "승인하되 고치지 않는다":
                처분, 상태 = "승인하되 고치지 않는다", "무처분"
            elif r["처분"] == "사용자에게 올린다":
                처분, 상태 = "사용자에게 올린다", "상신"
            elif r["처분"] == "호출자에게 전달":
                처분, 상태 = "호출자에게 전달", "전달"
            else:
                mismatches.append(vrlib.Mismatch(
                    file=str(입력), line=None,
                    expected="처분 값 넷 중 하나", actual=f"{r['id']}: {r['처분']}"))
                continue
            targets = ([r["id"]] if not _묶음ID_RE.match(r["id"])
                       else _묶음_구성(lines, 라운드, r["id"], mismatches, 장부경로))
            for t in targets:
                _본표_행_갱신(lines, 라운드, t, 심사, 처분, 상태,
                          mismatches, 장부경로)
            if r["확정"] == "기각":
                사유줄.append(f"- **{r['id']}** (승인 {r['승인수']}/{기수})")
                for 기, 사유 in sorted(r.get("기각사유", {}).items(),
                                   key=lambda kv: int(kv[0])):
                    사유줄.append(f"  - {기}기: {사유.splitlines()[0]}")
        if 사유줄:
            lines = _append_into_section(lines, f"라운드 {라운드} — 사유 절", 사유줄)
        summary = [f"본표 갱신 {len(항목들)}건, 기각 사유 "
                   f"{sum(1 for r in 항목들 if r['확정'] == '기각')}건"]

    elif 모드 == "적용":
        data = _load_json(입력)
        ids = data.get("적용", [])
        갱신 = 0
        for iid in ids:
            targets = ([iid] if not _묶음ID_RE.match(iid)
                       else _묶음_구성(lines, 라운드, iid, mismatches, 장부경로))
            for t in targets:
                _본표_행_갱신(lines, 라운드, t, None, None, "적용",
                          mismatches, 장부경로)
                갱신 += 1
        summary = [f"적용 {len(ids)}건, 본표 갱신 {갱신}행"]

    else:
        raise vrlib.UsageError(f"--모드 값은 제기·묶음·심사·적용: {모드}")

    if mismatches:
        return vrlib.emit(mismatches, [])
    vrlib.write_text(장부경로, "\n".join(lines))
    return vrlib.emit([], summary)


# ---------------------------------------------------------------- 라운드 판정

def cmd_종료집계(args) -> int:
    """종료집계 — SKILL.md §7 라운드 판정. 적용 건수를 세어 판정을 내고 결산을 기재한다.

    인자: --장부 <장부.md> / --라운드 <N> / --하한 <N> / --상한 <N> / --연속영 <N>.
    파라미터 셋은 그 런의 `라운드_하한`·`라운드_상한`·`종료_연속영` 확정 값이다.

    계수(닫힌 서식, 위반은 exit 1과 좌표): 장부의 `## 라운드 <N> — 본표` 절에서
    상태 열이 「적용」인 행을 센다 — 행 서식은 vrlib parse_ledger_table docstring이
    닫는다. 그 절이 없으면 exit 1이다. 라운드 1..N-1의 적용 건수는
    `## 라운드 <k> — 결산` 절의 「적용 <수>」 첫 출현에서 회수한다 —
    「미적용 <수>」처럼 앞에 한글이 붙은 출현은 세지 않는다. 절이 없거나 그
    수가 없으면 exit 1이다.

    판정 순서(SKILL.md §7 축자): ① 라운드 수 < 하한 → 다음 라운드
    ② 적용 0이 연속영 회 연속(이번 라운드에서 거슬러 센다) → 종료
    ③ 라운드 수 ≥ 상한 → 종료 ④ 그 밖 → 다음 라운드.

    장부 기재: 판정과 함께 `## 라운드 <N> — 결산` 절을 만들거나 치환한다 —
    본표에서 센 상태별 건수(「<상태> <수>」 축자, 적용이 첫 줄), 합, 판정.
    이 기재가 다음 라운드 종료집계의 회수 원천이다(references/장부.md 결산 절).
    다른 절은 바이트 그대로 둔다.

    stdout: 「판정: 다음 라운드|종료 — 판정 순서 <n>항」과 근거 수치(이번
    라운드 적용 건수 — 0건도 수치, 적용 이력, 적용 0 연속 횟수, 하한·상한·
    연속영 값), 「결산 기재 — 라운드 <N>」.
    """
    path = getattr(args, "장부")
    round_no = getattr(args, "라운드")
    low = getattr(args, "하한")
    high = getattr(args, "상한")
    zeros_needed = getattr(args, "연속영")
    text = vrlib.read_text(path)
    sections = {s.title: s for s in vrlib.split_sections(text)}
    mismatches: list[vrlib.Mismatch] = []

    main_title = f"라운드 {round_no} — 본표"
    if main_title not in sections:
        mismatches.append(vrlib.Mismatch(
            file=str(path), line=None, expected=f"「{main_title}」 절", actual="없음"))
        return vrlib.emit(mismatches, [])
    rows = vrlib.parse_ledger_table(sections[main_title], path, mismatches)
    if mismatches:
        return vrlib.emit(mismatches, [])
    applied_now = sum(1 for r in rows if r["상태"] == "적용")

    history: list[int] = []
    for k in range(1, round_no):
        title = f"라운드 {k} — 결산"
        if title not in sections:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=None, expected=f"「{title}」 절", actual="없음"))
            continue
        m = re.search(r"(?<![가-힣])적용\s*(\d+)", sections[title].body)
        if m is None:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=sections[title].start_line,
                expected="결산의 「적용 <수>」", actual="없음"))
            continue
        history.append(int(m.group(1)))
    if mismatches:
        return vrlib.emit(mismatches, [])
    history.append(applied_now)

    zeros = 0
    for n in reversed(history):
        if n != 0:
            break
        zeros += 1

    if round_no < low:
        verdict, clause = "다음 라운드", "1항"
        basis = f"라운드 수 {round_no} < 하한 {low}"
    elif zeros >= zeros_needed:
        verdict, clause = "종료", "2항"
        basis = f"적용 0 연속 {zeros}회 ≥ 연속영 {zeros_needed}"
    elif round_no >= high:
        verdict, clause = "종료", "3항"
        basis = f"라운드 수 {round_no} ≥ 상한 {high}"
    else:
        verdict, clause = "다음 라운드", "4항"
        basis = "1~3항 불성립"

    # 결산 기재 — 「적용 <수>」가 이 절의 첫 출현이도록 적용을 첫 줄에 둔다
    상태순 = ["적용", "수리확정", "무처분", "상신", "전달", "기각", "결번", "병합", "제기"]
    허용상태 = set(상태순)
    for r in rows:
        if r["상태"] not in 허용상태:
            mismatches.append(vrlib.Mismatch(
                file=str(path), line=r["행"], expected="장부 상태 여덟",
                actual=f"상태 {r['상태']}"))
    if mismatches:
        return vrlib.emit(mismatches, [])
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["상태"]] = counts.get(r["상태"], 0) + 1
    new = [f"## 라운드 {round_no} — 결산", ""]
    for name in 상태순 + sorted(set(counts) - set(상태순)):
        new.append(f"- {name} {counts.get(name, 0)}")
    new += [f"- 합 {len(rows)} (본표 행 수)",
            f"- 판정: {verdict} — 판정 순서 {clause} ({basis})", ""]
    ledger_lines = text.split("\n")
    결산제목 = f"라운드 {round_no} — 결산"
    span = vrlib.find_section(ledger_lines, 결산제목)
    if span is not None:
        ledger_lines = ledger_lines[:span[0]] + new + ledger_lines[span[1]:]
    else:
        marks = [(i, t) for i, t in vrlib._section_marks(ledger_lines)
                 if t.startswith(f"라운드 {round_no} — ")]
        last_start = marks[-1][0]
        all_marks = vrlib._section_marks(ledger_lines)
        insert_at = len(ledger_lines)
        for k, (i, _t) in enumerate(all_marks):
            if i == last_start:
                if k + 1 < len(all_marks):
                    insert_at = all_marks[k + 1][0]
                break
        ledger_lines = ledger_lines[:insert_at] + new + ledger_lines[insert_at:]
    vrlib.write_text(path, "\n".join(ledger_lines))

    lines = [
        f"판정: {verdict} — 판정 순서 {clause} ({basis})",
        f"라운드 {round_no} 적용 {applied_now}건 (본표 행 {len(rows)}건 중)",
        "적용 이력: " + " / ".join(f"라운드{i} {n}" for i, n in enumerate(history, start=1)),
        f"적용 0 연속 {zeros}회 — 하한 {low}, 상한 {high}, 연속영 {zeros_needed}",
        f"결산 기재 — 라운드 {round_no}",
    ]
    return vrlib.emit([], lines)


# ---------------------------------------------------------------- 진입점

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vr.py",
        description="verify-rounds 공식 스크립트. 하위명령별 계약은 각 함수 docstring이 닫는다.")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, help_text, func, run_round=False):
        p = sub.add_parser(name, help=help_text, description=func.__doc__,
                           formatter_class=argparse.RawDescriptionHelpFormatter)
        if run_round:
            p.add_argument("--런", required=True)
            p.add_argument("--라운드", type=int, required=True)
        p.set_defaults(func=func)
        return p

    p = add("앵커", "0단계 앵커 뜨기", cmd_앵커)
    p.add_argument("--런", required=True)
    p.add_argument("--동결", required=True)

    p = add("사본", "라운드 준비 사본 뜨기", cmd_사본, run_round=True)
    p.add_argument("--동결", required=True)

    p = add("영역검산", "수리 영역 합집합·비중첩 검산", cmd_영역검산,
            run_round=True)
    p.add_argument("--동결", required=True)
    p.add_argument("--명세", required=True)

    p = add("재정박", "행 범위 영역의 라운드 재정박", cmd_재정박, run_round=True)
    p.add_argument("--동결", required=True)
    p.add_argument("--명세", required=True)

    p = add("수리판독", "수리 산출 판독·ID 부여·항목.md 조립", cmd_수리판독,
            run_round=True)
    p.add_argument("--동결", required=True)
    p.add_argument("--수리", action="append", required=True)

    p = add("수리검산", "수리 산출 한 파일의 읽기 전용 검산", cmd_수리검산,
            run_round=True)
    p.add_argument("--동결", required=True)
    p.add_argument("--수리", required=True)

    p = add("묶음", "교차·결합 이행 폐쇄와 병합 지급 생성", cmd_묶음, run_round=True)
    p.add_argument("--동결", required=True)

    p = add("병합검산", "병합 산출의 조각 키 대조·판독", cmd_병합검산, run_round=True)
    p.add_argument("--결번", action="append")

    p = add("병합자검산", "병합 산출 한 파일의 읽기 전용 검산", cmd_병합자검산,
            run_round=True)
    p.add_argument("--지급", required=True)
    p.add_argument("--병합", required=True)

    p = add("심사지급", "심사대상.md 조립", cmd_심사지급, run_round=True)
    p.add_argument("--결번", action="append")

    p = add("지급검산", "§5.5 지급 전 검산", cmd_지급검산)
    p.add_argument("--파일", required=True)
    p.add_argument("--기대", type=int)

    p = add("상한", "심사 분할 상한 측정·배치 수 산정", cmd_상한)
    p.add_argument("--런", required=True)
    p.add_argument("--항목수", type=int, required=True)
    p.add_argument("--지급", action="append")
    p.add_argument("--항목상한", type=int, required=True)
    p.add_argument("--입력상한", type=int, required=True)

    p = add("분할", "심사 입력 파일의 배치 분할", cmd_분할)
    p.add_argument("--파일", required=True)
    p.add_argument("--배치수", type=int, required=True)

    p = add("심사집계", "정족·처분 보수 병합·기마다 검산", cmd_심사집계,
            run_round=True)
    p.add_argument("--대상", required=True)
    p.add_argument("--심사", action="append", required=True)
    p.add_argument("--정족", type=int, required=True)
    p.add_argument("--기수", type=int, required=True)
    p.add_argument("--기각보관")
    p.add_argument("--보관출처")

    p = add("심사검산", "심사 산출 한 파일의 읽기 전용 검산", cmd_심사검산)
    p.add_argument("--심사", required=True)
    expected = p.add_mutually_exclusive_group(required=True)
    expected.add_argument("--대상")
    expected.add_argument("--항목", action="append")
    p.add_argument("--기", type=int, required=True)

    p = add("적용", "승인 조각의 서로소 검사·축자 대조·역순 반영", cmd_적용,
            run_round=True)
    p.add_argument("--추가", action="append")
    p.add_argument("--제외", action="append")
    p.add_argument("--강제", action="store_true")

    p = add("장부머리", "장부 라운드 머리 기재", cmd_장부머리)
    p.add_argument("--장부", required=True)
    p.add_argument("--라운드", type=int, required=True)
    p.add_argument("--재료", required=True)

    p = add("장부갱신", "본표·묶음 구성표·상태 갱신", cmd_장부갱신)
    p.add_argument("--장부", required=True)
    p.add_argument("--라운드", type=int, required=True)
    p.add_argument("--모드", required=True)
    p.add_argument("--입력", required=True)

    p = add("종료집계", "적용 계수·라운드 판정·결산 기재", cmd_종료집계)
    p.add_argument("--장부", required=True)
    p.add_argument("--라운드", type=int, required=True)
    p.add_argument("--하한", type=int, required=True)
    p.add_argument("--상한", type=int, required=True)
    p.add_argument("--연속영", type=int, required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except vrlib.UsageError as e:
        print(f"오류: {e}", file=sys.stderr)
        return vrlib.EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
