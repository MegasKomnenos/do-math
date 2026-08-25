"""실측기 — 결정론 측정 7종의 단일 백엔드.

에이전트가 계수·좌표·표 구조·동문성·귀속·소요 견적을 즉석 셸로 재구현하는 대신
여기를 호출한다.

    count   파일들 × 패턴 → 파일별 계수 + 히트 문맥
    anchor  축자 문자열 → 현재 행 번호와 유일/다중/부재 판정
    table   마크다운 표의 열 계수(이스케이프 파이프 `\\|` 처리 내장)
    same    파일들의 내용 해시 군집 — 기본은 개행·꼬리 공백 정규화, --raw는 바이트 비교
    attrib  worktree 변경 목록 ↔ 귀속 목록 대조
    changes HEAD 대비 현존 변경 파일과 삭제 경로 분리
    budget  읽기 + 하네스 기저 + 도구 왕복 + 출력 유보 → 모델 예산 판정

모든 하위명령은 공통 증거 블록을 낸다 — 명령 축자·시각·대상 해시·결과·문맥.
보고의 실측 주장은 이 블록의 붙여넣기로만 성립한다(`계약/공통.md`).

사용:
    python dag_measure.py count  --pattern "문자열" --files "행/*.md" [--regex] [--root DIR]
    python dag_measure.py anchor --text "축자" --file 행/2.md [--root DIR]
    python dag_measure.py table  --file 이음새.md [--root DIR]
    python dag_measure.py same   --files "행/*.d/z.md" [--raw] [--root DIR]
    python dag_measure.py attrib --worktree PATH --attributed "a.py,b.md" [--allow-untracked]
    python dag_measure.py changes --worktree PATH [--base HEAD]
    python dag_measure.py budget --files "행/2.md,기준선.md" --model opus
                                 [--writes BYTES] [--pending BYTES] [--root DIR]

`budget`의 견적은 읽기 목록만이 아니다. 한 에이전트의 문맥은 읽기·하네스 기저·
도구 왕복·자기 출력 재유입으로 차고, 저작 행에서는 출력이 최대 항이다.
저작량을 알면 `--writes`로 바이트를 준다 — 생략하면 하한이 들어간다.
선행이 저작할 산출을 읽어야 하는데 그것이 아직 없으면 `--pending`으로 바이트를
준다. 한 저작 행의 `--writes`가 그 산출을 소비하는 행의 `--pending`이다.
"""

from __future__ import annotations

import argparse
import glob as globmod
import hashlib
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

# 아래 생성 블록의 값은 `전거/`가 정본이고 `dag_facts.py --render`가 채운다.
# 【생성 예산】
BUDGETS = {"sonnet": 200_000, "opus": 250_000, "fable": 250_000, "gpt-5.6-sol": 250_000, "gpt-5.6-terra": 250_000, "gpt-5.6-luna": 250_000}
# 【끝】
CONTEXT_TRIM = 120

# --- 견적 계수 (2026-07-27 트랜스크립트 적합) ------------------------------
#
# 소요 견적 = 읽기 + 하네스 기저 + 도구 왕복 + 출력 유보. 네 항이 다 든다.
# 재적합할 때의 항등식: `문맥 증분 = 직전 출력 + 도구 결과`.

# 문자 계열별 단가. 5클러스터·70,738tok 최소제곱 적합, 잔차 ±6%.
# Read 적재의 행번호 접두 비용은 계수에 흡수돼 있다.
WIDE_TOK = 1.9  # CJK·한글 등 넓은 문자, 자당
NARROW_TOK = 0.2  # ASCII·기호, 자당(≈5자/토큰)

# 바이트만 아는 대상(측정 시점 미존재 정본)의 적재 단가.
READ_BYTES_PER_TOKEN = 1.9

# 하네스 기저 — 시스템 프롬프트·툴 스키마·deferred 툴 목록·스킬 목록. 모델 무관.
HARNESS_FLOOR = 28_000

# 도구 왕복 — 읽기 목록 밖에서 문맥에 드는 것: 셸·검색 결과, 편집 회신,
# 자식 파견문을 설계하며 돌리는 실측기 출력.
TOOL_TRAFFIC = 10_000

# 출력 유보 — 출력 토큰은 문맥에 1:1로 재유입된다. 하한은 읽기 위주 행의 관측 최소치.
OUTPUT_FLOOR = 35_000
AUTHOR_BYTES_PER_TOKEN = 2.0  # 저작물(한국어 행 파일)의 바이트당 내용 토큰
THINK_FACTOR = 1.9  # 저작 내용 토큰 대 총 출력 토큰(사고 포함)


def est_text(text: str) -> int:
    """문자 계열별 단가로 적재 토큰을 견적한다."""
    wide = sum(1 for ch in text if unicodedata.east_asian_width(ch) in ("W", "F"))
    return round(WIDE_TOK * wide + NARROW_TOK * (len(text) - wide))


def est_file(path: Path) -> int:
    return est_text(path.read_text(encoding="utf-8", errors="replace"))


def est_pending(pending: int) -> int:
    """측정 시점 미존재 정본의 적재 견적. 바이트만 아는 대상에 쓴다."""
    return round(pending / READ_BYTES_PER_TOKEN)


def est_output(writes: int) -> int:
    """저작 예상 바이트 → 출력 유보 토큰."""
    return max(OUTPUT_FLOOR, round(THINK_FACTOR * writes / AUTHOR_BYTES_PER_TOKEN))


def est_required(reads: int, writes: int) -> int:
    """한 에이전트가 완주에 쓸 문맥 견적."""
    return reads + HARNESS_FLOOR + TOOL_TRAFFIC + est_output(writes)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _expand(spec: str, root: Path) -> tuple[list[Path], list[str]]:
    """쉼표 구분 + 글롭. (정렬된 실재 파일, 아무것도 가리키지 못한 조각).

    미해석 조각을 함께 돌려주는 것이 계약의 절반이다.
    """
    out: list[Path] = []
    missing: list[str] = []
    for part in (p.strip() for p in spec.split(",") if p.strip()):
        cand = root / part
        if cand.is_file():
            out.append(cand)
            continue
        hits = [Path(m) for m in globmod.glob(str(root / part), recursive=True) if Path(m).is_file()]
        if hits:
            out.extend(hits)
        else:
            missing.append(part)
    seen, uniq = set(), []
    for p in sorted(out):
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq, missing


def _unresolved(missing: list[str]) -> list[str]:
    """증거 블록에 실을 미해석 고지. 없으면 줄을 늘리지 않는다."""
    return [f"미해석: {' · '.join(missing)}"] if missing else []


def _target_hash(paths: list[Path]) -> str:
    h = hashlib.sha1()
    for p in paths:
        h.update(str(p).encode("utf-8"))
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def _quote(arg: str) -> str:
    """공백이 든 인자를 따옴표에 담는다. 담지 않으면 붙여넣은 명령이 다른 인자열이 된다."""
    return f'"{arg}"' if any(ch.isspace() for ch in arg) else arg


def block(kind: str, argv: list[str], target: str, lines: list[str]) -> str:
    head = [
        f"[실측기 {kind}]",
        f"명령: python dag_measure.py {' '.join(_quote(a) for a in argv)}",
        f"시각: {_now()}",
        f"대상해시: sha1:{target}",
    ]
    return "\n".join(head + lines + ["[/실측기]"])


# --- count ---------------------------------------------------------------


def run_count(pattern: str, paths: list[Path], root: Path, regex: bool) -> list[str]:
    rx = re.compile(pattern if regex else re.escape(pattern))
    lines: list[str] = []
    total = 0
    for p in paths:
        hits = []
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if rx.search(line):
                hits.append((i, line.strip()[:CONTEXT_TRIM]))
        total += len(hits)
        lines.append(f"{_rel(p, root)}: {len(hits)}")
        for i, ctx in hits:
            lines.append(f"  :{i}: {ctx}")
    lines.append(f"합계: {total} ({len(paths)}파일)")
    return lines


# --- anchor --------------------------------------------------------------


def run_anchor(text: str, path: Path, root: Path) -> list[str]:
    hits = [
        i
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
        if text in line
    ]
    verdict = "부재" if not hits else ("유일" if len(hits) == 1 else f"다중 {len(hits)}")
    lines = [f"{_rel(path, root)}: {verdict}"]
    lines += [f"  :{i}" for i in hits]
    return lines


# --- table ---------------------------------------------------------------

_ESCAPED_PIPE = re.compile(r"\\\|")


def _cols(row: str) -> int:
    """이스케이프 파이프를 걷어낸 실제 열 계수."""
    return len(_ESCAPED_PIPE.sub("", row).strip().strip("|").split("|"))


def run_table(path: Path, root: Path) -> list[str]:
    lines: list[str] = [f"{_rel(path, root)}:"]
    header_cols = None
    table_no = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = raw.strip()
        if not line.startswith("|"):
            header_cols = None
            continue
        cells = _ESCAPED_PIPE.sub("", line).strip("|").split("|")
        is_rule = all(set(c.strip()) <= set("-: ") for c in cells)
        if header_cols is None and not is_rule:
            table_no += 1
            header_cols = _cols(line)
            lines.append(f"  표{table_no} (:{i}): 머리 {header_cols}열")
            continue
        if is_rule:
            continue
        n = _cols(line)
        if header_cols is not None and n != header_cols:
            lines.append(f"    :{i}: {n}열 — 머리와 불일치")
    if table_no == 0:
        lines.append("  표 없음")
    else:
        lines.append(f"  판정: 표 {table_no}개, 불일치 행은 위에 열거(없으면 전건 일치)")
    return lines


# --- same ----------------------------------------------------------------


def run_same(paths: list[Path], root: Path, normalize: bool) -> list[str]:
    groups: dict[str, list[str]] = {}
    for p in paths:
        body = p.read_bytes()
        if normalize:
            body = b"\n".join(line.rstrip() for line in body.replace(b"\r\n", b"\n").split(b"\n"))
        h = hashlib.sha1(body).hexdigest()[:12]
        groups.setdefault(h, []).append(_rel(p, root))
    lines = []
    for h, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"sha1:{h} — {len(members)}파일")
        lines += [f"  {m}" for m in members]
    verdict = "동문" if len(groups) == 1 else f"갈림 {len(groups)}군"
    lines.append(f"판정: {verdict}")
    return lines


# --- attrib --------------------------------------------------------------


def run_attrib(worktree: Path, attributed: list[str], allow_untracked: bool) -> list[str]:
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", "status", "--porcelain=v1", "-z"],
        cwd=str(worktree), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        return [f"git status 실패: {proc.stderr.strip()}"]
    changed: list[str] = []
    records = proc.stdout.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        status, path = record[:2], record[3:]
        renamed = status[:1] == "R" or status[1:2] == "R"
        copied = status[:1] == "C" or status[1:2] == "C"
        previous = ""
        if renamed or copied:
            if index >= len(records) or not records[index]:
                return ["git status 판독 실패: 이름 변경 또는 복사의 이전 경로가 없다"]
            previous = records[index]
            index += 1
        if status == "??" and allow_untracked:
            continue
        changed.append(path)
        if renamed:
            changed.append(previous)
    attr = {a.strip().replace("\\", "/") for a in attributed if a.strip()}
    changed_norm = [c.replace("\\", "/") for c in changed]
    unattributed = [c for c in changed_norm if c not in attr]
    unchanged_attr = sorted(attr - set(changed_norm))
    lines = [f"변경 {len(changed_norm)} / 귀속 {len(attr)}"]
    lines.append(f"미귀속 편집: {len(unattributed)}")
    lines += [f"  {c}" for c in unattributed]
    lines.append(f"귀속됐으나 무변경: {len(unchanged_attr)}")
    lines += [f"  {c}" for c in unchanged_attr]
    lines.append(f"판정: {'전건 귀속' if not unattributed else '미귀속 잔존'}")
    return lines


# --- changes -------------------------------------------------------------


def _git_z(worktree: Path, args: list[str]) -> list[str]:
    """NUL 구분 Git 출력을 경로 안전하게 판독한다."""
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=str(worktree), capture_output=True,
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} 실패: {detail}")
    return [part.decode("utf-8", errors="strict") for part in proc.stdout.split(b"\0") if part]


def run_changes(worktree: Path, base: str) -> tuple[list[str], bool]:
    """base 대비 현존 파일과 삭제 경로를 가른다.

    tracked 변경은 base와 작업트리 전체를 비교해 staged·unstaged를 함께 센다.
    미추적·비무시 파일은 별도 Git 목록으로 합친다. 파일 삭제와 이름 변경의 옛
    경로는 verify-rounds가 사본으로 뜰 수 없으므로 삭제 집합으로 남긴다.
    """
    tokens = _git_z(worktree, ["diff", "--name-status", "-z", "--no-renames", base, "--"])
    existing: set[str] = set()
    deleted: set[str] = set()
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if "\t" in token:
            status, path = token.split("\t", 1)
            i += 1
        else:
            if i + 1 >= len(tokens):
                raise RuntimeError(f"git diff --name-status 판독 불가: {token!r}")
            status, path = token, tokens[i + 1]
            i += 2
        path = path.replace("\\", "/")
        if status.startswith("D") or not (worktree / path).is_file():
            deleted.add(path)
        else:
            existing.add(path)

    for path in _git_z(worktree, ["ls-files", "--others", "--exclude-standard", "-z"]):
        normalized = path.replace("\\", "/")
        if (worktree / normalized).is_file():
            existing.add(normalized)

    existing -= deleted
    lines = [f"현존 {len(existing)}"]
    lines += [f"  {path}" for path in sorted(existing)]
    lines.append(f"삭제 {len(deleted)}")
    lines += [f"  {path}" for path in sorted(deleted)]
    lines.append(f"판정: {'삭제대상' if deleted else '검증가능'}")
    return lines, bool(deleted)


# --- budget --------------------------------------------------------------


def run_budget(paths: list[Path], root: Path, model: str, writes: int = 0,
               pending: int = 0) -> list[str]:
    budget = BUDGETS.get(model)
    lines = []
    reads = 0
    for p in paths:
        est = est_file(p)
        reads += est
        lines.append(f"{_rel(p, root)}: ~{est:,}tok")
    if pending > 0:
        est = est_pending(pending)
        reads += est
        lines.append(f"미존재 정본: ~{est:,}tok ({pending:,}바이트 — 측정 시점 미존재)")
    output = est_output(writes)
    required = est_required(reads, writes)
    lines.append(f"읽기 합계: ~{reads:,}tok (문자계열 단가 견적)")
    lines.append(f"하네스 기저: ~{HARNESS_FLOOR:,}tok (시스템 프롬프트·툴 스키마·스킬 목록 — 실측 상수)")
    lines.append(f"도구 왕복: ~{TOOL_TRAFFIC:,}tok (셸·검색 결과, 편집 회신 — 실측 상수)")
    if writes <= 0:
        why = "하한 — 저작 예상 미지정"
    elif output <= OUTPUT_FLOOR:
        why = f"하한 — 저작 예상 {writes:,}바이트는 하한 미달"
    else:
        why = f"저작 예상 {writes:,}바이트 × 사고 {THINK_FACTOR}배"
    lines.append(f"출력 유보: ~{output:,}tok ({why})")
    lines.append(f"소요 견적: ~{required:,}tok")
    if budget:
        verdict = "예산 안" if required <= budget else "예산 초과 — 저작 시점에 쪼갠다"
        lines.append(f"판정: {model} {budget:,} 대비 {verdict}")
    else:
        lines.append(f"판정: 미지 모델 '{model}' — 예산표 {sorted(BUDGETS)}")
    return lines


# --- CLI -----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("count")
    c.add_argument("--pattern", required=True)
    c.add_argument("--files", required=True)
    c.add_argument("--regex", action="store_true")
    c.add_argument("--root", default=".")

    a = sub.add_parser("anchor")
    a.add_argument("--text", required=True)
    a.add_argument("--file", required=True)
    a.add_argument("--root", default=".")

    t = sub.add_parser("table")
    t.add_argument("--file", required=True)
    t.add_argument("--root", default=".")

    s = sub.add_parser("same")
    s.add_argument("--files", required=True)
    s.add_argument("--raw", action="store_true", help="정규화 없이 바이트 그대로")
    s.add_argument("--root", default=".")

    at = sub.add_parser("attrib")
    at.add_argument("--worktree", required=True)
    at.add_argument("--attributed", required=True, help="쉼표 구분 경로 목록")
    at.add_argument("--allow-untracked", action="store_true")

    ch = sub.add_parser("changes")
    ch.add_argument("--worktree", required=True)
    ch.add_argument("--base", default="HEAD")

    b = sub.add_parser("budget")
    b.add_argument("--files", required=True)
    b.add_argument("--model", required=True)
    b.add_argument("--writes", type=int, default=0,
                   help="저작 예상 바이트 — 출력 유보 산정용(생략하면 실측 하한)")
    b.add_argument("--pending", type=int, default=0,
                   help="측정 시점 미존재 정본의 바이트 — 선행이 저작할 산출을 소비할 때")
    b.add_argument("--root", default=".")

    args = p.parse_args(argv)
    root = Path(getattr(args, "root", ".")).resolve()

    if args.cmd == "count":
        paths, missing = _expand(args.files, root)
        if not paths:
            print(block("count", argv, "0" * 12, [f"대상 0파일 — '{args.files}'는 아무것도 가리키지 않는다"]))
            return 1
        print(block("count", argv, _target_hash(paths),
                    _unresolved(missing) + run_count(args.pattern, paths, root, args.regex)))
    elif args.cmd == "anchor":
        path = root / args.file
        if not path.is_file():
            print(block("anchor", argv, "0" * 12, [f"파일 부재: {args.file}"]))
            return 1
        print(block("anchor", argv, _target_hash([path]), run_anchor(args.text, path, root)))
    elif args.cmd == "table":
        path = root / args.file
        if not path.is_file():
            print(block("table", argv, "0" * 12, [f"파일 부재: {args.file}"]))
            return 1
        print(block("table", argv, _target_hash([path]), run_table(path, root)))
    elif args.cmd == "same":
        paths, missing = _expand(args.files, root)
        if not paths:
            print(block("same", argv, "0" * 12, [f"대상 0파일 — '{args.files}'는 아무것도 가리키지 않는다"]))
            return 1
        print(block("same", argv, _target_hash(paths),
                    _unresolved(missing) + run_same(paths, root, not args.raw)))
    elif args.cmd == "attrib":
        wt = Path(args.worktree)
        if not wt.is_dir():
            print(block("attrib", argv, "0" * 12, [f"worktree 부재: {args.worktree}"]))
            return 1
        print(block("attrib", argv, "-" * 12, run_attrib(wt, args.attributed.split(","), args.allow_untracked)))
    elif args.cmd == "changes":
        wt = Path(args.worktree)
        if not wt.is_dir():
            print(block("changes", argv, "0" * 12, [f"worktree 부재: {args.worktree}"]))
            return 1
        try:
            lines, has_deleted = run_changes(wt, args.base)
        except RuntimeError as exc:
            print(block("changes", argv, "0" * 12, [str(exc)]))
            return 1
        print(block("changes", argv, "-" * 12, lines))
        return 1 if has_deleted else 0
    elif args.cmd == "budget":
        paths, missing = _expand(args.files, root)
        if not paths:
            print(block("budget", argv, "0" * 12, [f"대상 0파일 — '{args.files}'는 아무것도 가리키지 않는다"]))
            return 1
        print(block("budget", argv, _target_hash(paths),
                    _unresolved(missing)
                    + run_budget(paths, root, args.model, args.writes, args.pending)))
        # 예산표 밖 모델은 판정을 내지 못한다 — 다른 실패와 같은 코드로 낸다.
        return 0 if args.model in BUDGETS else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
