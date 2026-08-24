"""오케 적재량 판독기 — 서브에이전트 트랜스크립트에서 현재 컨텍스트 적재를 읽는다.

도달 판정은 오케의 자기 근사가 아니라 메인의 기계 실측이다(`SKILL.md` 「메인의 임무
넷」 4항). 교대 임계 120k와 모델 예산 상한(`dag_measure.BUDGETS`)은 섞지 않으며, 이
스크립트는 둘 중 어느 값도 갖지 않는다.

판독 경로: 열쇠 하나로 `<세션>/subagents/agent-<id>.meta.json`을 역탐색해 짝
`agent-<id>.jsonl`을 특정하고, 마지막 assistant 행 `message.usage`의
(input_tokens + cache_creation_input_tokens + cache_read_input_tokens)를 읽는다.
이 합이 그 에이전트의 현재 컨텍스트 적재다.

**열쇠는 둘이고 정확히 하나를 준다.** `--description`은 메인이 Agent 호출에 직접 써
넣는 값이라 메인이 아는 유일한 열쇠다(오케의 규정 문자열은 `do-dag 오케 <국면명>` —
`SKILL.md`). `--tool-use-id`는 하네스 내부 값이라 그것을 볼 수 있는 주체만 쓴다.
여럿이 걸리면 하나를 고르지 않고 오류로 돌려준다.

description의 유일성은 `SKILL.md`가 **국면 안에서만** 요구하므로 검색 범위도 국면으로
좁힌다. 좁히지 않으면 예전에 같은 국면명을 쓴 런의 오케가 함께 걸린다.

    --phase <국면명>   마커(`.sdd/dag/marker.json`)의 그 국면 `opened_at` 이후만 본다
    --since <ISO8601>  하한을 직접 준다(마커 밖 상황·닫힌 국면의 사후 판독)

좁히고도 둘 이상이면 여전히 오류다 — 그때는 차수(`#2`)를 빠뜨린 것이다. 하한 비교는
meta 파일의 mtime으로 하고, 메인이 국면을 연 뒤 오케를 쏘므로 1기 오케도 하한 안에
든다(`SKILL.md` 「1. 오케 파견」).

이 스크립트는 읽기만 한다. 임계 도달 판정과 교대 지시는 메인의 몫이다.

사용:
    python agent_usage.py --description "do-dag 오케 <국면명>" --phase <국면명>
    python agent_usage.py --description "do-dag 오케 <국면명>" --phase <국면명> --json
    python agent_usage.py --description "..." --since 2026-07-28T00:00:00Z
    python agent_usage.py --tool-use-id toolu_xxx
    (트랜스크립트 루트 기본값: ~/.claude/projects/<현재 프로젝트 경로의 munge>)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

SUM_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")

# meta 파일의 키 넷 중 열쇠가 되는 둘. 나머지는 agentType·spawnDepth다.
KEYS = {"tool_use_id": "toolUseId", "description": "description"}


class NoUsageError(RuntimeError):
    """트랜스크립트에 usage 실린 assistant 행이 없다."""


class AmbiguousKeyError(RuntimeError):
    """열쇠 하나에 에이전트가 여럿 걸렸다. 좁히는 것은 부르는 쪽의 일이다."""


def munge_project_dir(project_dir: str) -> str:
    """하네스 관례: 경로의 비영숫자를 전부 '-'로 치환한다."""
    return re.sub(r"[^0-9A-Za-z]", "-", str(project_dir))


def default_transcripts_root(project_dir: str | None = None) -> Path:
    project_dir = project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path.home() / ".claude" / "projects" / munge_project_dir(project_dir)


def parse_since(value: str) -> float:
    """ISO8601 하한을 epoch 초로. `Z`도 받는다."""
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    stamp = datetime.fromisoformat(text)
    if stamp.tzinfo is None:
        stamp = stamp.astimezone()
    return stamp.timestamp()


def phase_opened_at(phase: str, project_dir: str | None = None) -> float:
    """마커가 기록한 그 국면의 개설 시각(epoch 초).

    올리는 예외는 넷이다. 국면이 활성이 아니면 `KeyError`, 마커가 없거나 읽을 수 없으면
    `OSError`, 마커가 JSON이 아니면 `json.JSONDecodeError`, `opened_at`이 ISO8601이
    아니면 `ValueError`다. 넷 다 부르는 쪽이 `--since`로 하한을 직접 주어야 하는
    상태이고, `main`이 넷을 한 자리에서 잡는다.
    """
    root = Path(project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    marker = root / ".sdd" / "dag" / "marker.json"
    data = json.loads(marker.read_text(encoding="utf-8"))
    opened = ((data.get("active_phases") or {}).get(phase) or {}).get("opened_at")
    if not opened:
        raise KeyError(phase)
    return parse_since(opened)


def find_agent_matches(
    transcripts_root: Path, meta_key: str, value: str, since: float | None = None
) -> list[Path]:
    """그 열쇠가 일치하는 meta.json들의 짝 jsonl 전부. 정렬은 경로순이다.

    `since`(epoch 초)를 주면 그보다 오래된 meta는 세지 않는다.
    """
    hits: list[Path] = []
    for meta_path in sorted(transcripts_root.glob("*/subagents/agent-*.meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            stale = since is not None and meta_path.stat().st_mtime < since
        except (OSError, json.JSONDecodeError):
            continue
        if stale:
            continue
        if meta.get(meta_key) == value:
            jsonl = meta_path.with_name(meta_path.name.replace(".meta.json", ".jsonl"))
            if jsonl.exists():
                hits.append(jsonl)
    return hits


def find_agent_transcript(
    transcripts_root: Path,
    tool_use_id: str | None = None,
    *,
    description: str | None = None,
    since: float | None = None,
) -> Path | None:
    """열쇠 하나로 트랜스크립트를 특정한다. 없으면 None, 여럿이면 예외."""
    meta_key, value = (
        (KEYS["description"], description) if description is not None
        else (KEYS["tool_use_id"], tool_use_id)
    )
    hits = find_agent_matches(transcripts_root, meta_key, value, since)
    if len(hits) > 1:
        scope = "" if since is None else " (하한 적용 뒤에도)"
        raise AmbiguousKeyError(
            f"{meta_key} '{value}'에 에이전트 {len(hits)}기가 걸렸다{scope}:\n  "
            + "\n  ".join(str(h) for h in hits)
            + "\n  차수(`#2`)를 붙이거나 --phase·--since로 범위를 좁힌다."
        )
    return hits[0] if hits else None


def read_usage(transcript: Path) -> dict:
    """마지막 assistant 행의 usage와 합산 적재를 돌려준다."""
    last_usage = None
    with transcript.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") != "assistant":
                continue
            usage = (row.get("message") or {}).get("usage")
            if usage:
                last_usage = usage
    if last_usage is None:
        raise NoUsageError(f"usage 실린 assistant 행이 없다: {transcript}")
    total = sum(int(last_usage.get(k) or 0) for k in SUM_KEYS)
    return {"context_tokens": total, "usage": last_usage, "transcript": str(transcript)}


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    key = p.add_mutually_exclusive_group(required=True)
    key.add_argument("--description", help="Agent 호출에 써 넣은 description 축자")
    key.add_argument("--tool-use-id", help="하네스 내부 값. 볼 수 있는 주체만 쓴다")
    p.add_argument("--project-dir", help="트랜스크립트 루트 유도용 프로젝트 경로")
    p.add_argument("--transcripts-root", help="트랜스크립트 루트 직접 지정(유도 우회)")
    scope = p.add_mutually_exclusive_group()
    scope.add_argument("--phase", help="이 국면의 마커 개설 시각 이후만 본다")
    scope.add_argument("--since", help="검색 하한을 ISO8601로 직접 준다")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    root = Path(args.transcripts_root) if args.transcripts_root else default_transcripts_root(args.project_dir)
    meta_key, value = (
        (KEYS["description"], args.description) if args.description is not None
        else (KEYS["tool_use_id"], args.tool_use_id)
    )
    since = None
    if args.since:
        try:
            since = parse_since(args.since)
        except ValueError as exc:
            print(f"[agent_usage] --since를 읽을 수 없다: {exc}")
            return 1
    elif args.phase:
        try:
            since = phase_opened_at(args.phase, args.project_dir)
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            print(
                f"[agent_usage] 마커에서 국면 '{args.phase}'의 개설 시각을 읽지 못했다: {exc}"
                " — 닫힌 국면이면 --since로 하한을 직접 준다"
            )
            return 1
    try:
        transcript = find_agent_transcript(
            root, args.tool_use_id, description=args.description, since=since
        )
    except AmbiguousKeyError as exc:
        print(f"[agent_usage] {exc}")
        return 1
    if transcript is None:
        bound = "" if since is None else f" (하한 {args.since or args.phase} 이후)"
        print(f"[agent_usage] {meta_key} '{value}' 을 {root} 아래에서 찾지 못했다{bound}")
        return 1
    try:
        result = read_usage(transcript)
    except NoUsageError as exc:
        print(f"[agent_usage] {exc}")
        return 1
    result["key"] = meta_key
    result["value"] = value
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        u = result["usage"]
        parts = " + ".join(str(int(u.get(k) or 0)) for k in SUM_KEYS)
        print(f"[agent_usage] {value}: 적재 {result['context_tokens']:,} 토큰 ({parts})")
        print(f"[agent_usage] 트랜스크립트: {result['transcript']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
