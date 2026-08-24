"""DAG 국면 마커 — 기계가 읽어야 하는 최소 사실만 담는 공용 제어 파일.

마커는 파견표가 아니다. 저장소의 활성 DAG 국면과 임시 커밋 허용 상태를 훅에 알려
주는 것이 전부이고, 국면의 상태·계수·검증 회계의 정본은 파견표
(`.sdd/dag/<국면>/파견표.md`)로 남는다.

    active_phases     지금 도는 국면들            (비면 무국면)
    commit_grants     발급된 임시 커밋 허가       (각각 만료 시각을 갖는다)
    merge_lease       메인 체크아웃 병합권 하나   (소유자와 만료 시각)

앞의 둘은 복수다 — 국면 A가 도는 동안 B를 열 수 있고, 두 싱크의 grant는 서로를 덮지
않는다. **lease는 단수다** — 지키는 자원이 메인 체크아웃의 인덱스 하나뿐이다. 만료된
lease는 다음 획득이 회수한다.

관문이 지키는 것은 메인 체크아웃의 공유 이력이다. 활성 국면의 노드 브랜치를
체크아웃한 격리 트리 안의 커밋은 grant 없이 통과한다(`gate_decision`).

실패 방향: 마커를 읽을 수 없으면(손상·권한) 게이트는 **차단**한다. 탈출은
`close --all` 한 번이고, 차단 문면이 그 경로를 상시 병기한다.

사용:
    python dag_marker.py status
    python dag_marker.py open  --phase <국면id>
    python dag_marker.py allow --minutes 30 --reason "노드 N-1 병합"   # grant ID를 발급
    python dag_marker.py clear-token --grant <grantID>   # --all 로 전부 해제
    python dag_marker.py lease --acquire --owner <행번호> [--minutes 30]  # 0=획득 1=점유중
    python dag_marker.py lease --release --owner <행번호>
    python dag_marker.py lease --status
    python dag_marker.py close --phase <국면id>          # 잔존 회수 + 그 국면만 닫는다
    python dag_marker.py close --all                     # 마커를 통째로 비운다(탈출)
    python dag_marker.py sweep --phase <국면id>   # 회수만. 0=잔존 없음 1=잔존 있음
    python dag_marker.py worktree-open --phase <국면id> --row <행> --base <SHA>
    python dag_marker.py gate            # pre-commit 훅 본체. 0=통과 1=차단
    python dag_marker.py install-hook    # .git/hooks/pre-commit 설치(전 worktree 공통)

노드 격리(worktree)의 명명은 국면과 행 번호의 순수 함수다. 생성하는 전개, 병합하는
싱크, 회수하는 종결이 서로 좌표를 주고받지 않고 각자 재도출한다.

이름은 경로와 Git ref 양쪽으로 파생하므로 **두 문법의 교집합**만 받는다
(`validate_phase`·`validate_row`).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

MARKER_RELPATH = Path(".sdd") / "dag" / "marker.json"
LOCK_RELPATH = Path(".sdd") / "dag" / "marker.lock"
LOCK_STALE_SECONDS = 60
WT_ROOT_ENV = "DAG_WT_ROOT"
BRANCH_PREFIX = "dag"
# 격리 트리 이름에서 국면과 행을 가르는 문자. 두 이름 문법이 함께 막는 것이라야
# 좌표가 단사다 — `-`는 둘 다 마디에 받으므로 국면 `a-1`의 행 `2`와 국면 `a`의 행
# `1-2`가 한 경로로 붕괴한다.
WT_SEP = "+"

BLOCK_MESSAGE = """[dag pre-commit] 활성 국면 {phases} — 커밋 허용 grant가 없다.
  노드 병합 커밋:  python {script} allow --minutes 30 --reason "노드 <id> 병합"
  국면 무관 커밋:  python {script} allow --minutes 10 --reason "<사유>"
  국면이 이미 끝났으면: python {script} close --phase <국면id>
  (상태·계수의 정본은 파견표다: {ledgers})"""

UNREADABLE_MESSAGE = """[dag pre-commit] 마커 파일을 읽을 수 없다 — 국면 진행 여부 불명이라 차단한다.
  경로: {path}
  원인: {err}
  해제: python {script} close --all      (국면이 없으면 이것으로 마커를 비운다)"""


class WorktreeConflict(Exception):
    """격리 트리를 안전하게 열 수 없다. 기계는 지우지 않고 처분을 넘긴다."""


class MarkerUnreadable(ValueError):
    """마커를 읽을 수 없다. 판독 불가의 처분을 한 어휘로 모은다.

    `ValueError`로 서는 것은 `main`의 공통 그물이 이미 그 어휘를 받기 때문이다.
    권한 거부·잠긴 파일이 `OSError` 그대로 오르면 그 그물에 걸리지 않아 여섯 호출이
    트레이스백으로 끝나고, `_report_unreadable`이 병기하는 `close --all` 탈출 경로가
    나오지 않는다.
    """


# --- 이름 문법 ------------------------------------------------------------
#
# 국면명과 행 번호는 격리 좌표(【격리좌표 · 경로는 <dag-wt 루트>/<국면>+<행> · 브랜치는 dag/<국면>/<행>】) 양쪽으로 파생하므로 둘 다 **두 문법의
# 교집합** 안에 있어야 한다. 슬래시가 특히 위험하다 — 국면 `a/b`는 브랜치
# `dag/a/b/2`를 만들지만 관문은 `dag/` 뒤 첫 슬래시까지만 국면으로 읽어 `a`로 자른다.
#
# 아래 생성 블록의 값은 `전거/`가 정본이고 `dag_facts.py --render`가 채운다.
# 손으로 고치지 않는다 — 고칠 자리는 전거 항목이다. 한 사실이 사람이 읽는 요지와
# 기계가 집행하는 패턴 두 표기로 살고 한 항목의 기계값은 하나이므로 사전으로 든다.
# 【생성 이름문법】
_NAME = {"요지": "글자·숫자·`_`·`-`만 쓴다(64자 이하). 경로 구분자·공백·`.`·`..`·제어 문자와 Git ref 금지 문자(`~^:?*[\\`)는 경로와 브랜치 이름을 함께 깨뜨린다", "패턴": "^[\\w-]{1,64}$"}
# 【끝】

# 아래 둘은 사전에서 파생한다. 값을 여기 다시 적으면 그것이 두 번째 정본이 된다.
NAME_RULE = _NAME["요지"]
PHASE_RE = re.compile(_NAME["패턴"], re.UNICODE)

# 행 번호는 위 문법에 마디 구분자를 더 받는다. 64자 상한이 없는 별개 문법이다.
# 꼬리의 `(?<!\.lock)`은 Git ref 문법 몫이다 — ref 마디는 `.lock`으로 끝날 수 없고,
# 행 번호는 브랜치 `dag/<국면>/<행>`의 마지막 마디가 된다. 이것이 빠지면 검증을
# 통과한 값이 `git worktree add`에서 뒤늦게 깨져 수리 좌표가 행 번호를 가리키지 못한다.
ROW_RE = re.compile(r"^[\w-]+(?:\.[\w-]+)*(?<!\.lock)$", re.UNICODE)


def validate_phase(name: str) -> str:
    """국면명을 문법으로 거른다. 어긋나면 ValueError."""
    if not name or not PHASE_RE.fullmatch(name):
        raise ValueError(f"국면명 '{name}'이 문법 밖이다 — {NAME_RULE}")
    return name


def validate_row(row: str) -> str:
    """행 번호를 문법으로 거른다. 마디 구분자 `.`만 더 받는다."""
    if not row or not ROW_RE.fullmatch(row):
        raise ValueError(
            f"행 번호 '{row}'가 문법 밖이다 — 마디는 글자·숫자·`_`·`-`이고"
            " 구분자는 `.` 하나이며, 끝이 `.lock`일 수 없다(Git ref 문법)"
        )
    return row


def project_root() -> Path:
    """저장소 루트. CLAUDE_PROJECT_DIR 우선, 없으면 `.git` 실재로 위로 걸어 찾는다.

    pre-commit 훅에는 이 파일의 절대 경로가 박히므로, 링크된 worktree에서 커밋해도
    해석되는 루트는 주 체크아웃 하나다.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for cand in [here, *here.parents]:
        if (cand / ".git").exists():
            return cand
    return here.parents[4]


def marker_path(root: Path | None = None) -> Path:
    return (root or project_root()) / MARKER_RELPATH


def lock_path(root: Path | None = None) -> Path:
    return (root or project_root()) / LOCK_RELPATH


def _drop_lock(root: Path | None = None) -> None:
    try:
        lock_path(root).unlink()
    except FileNotFoundError:
        pass


@contextmanager
def marker_lock(root: Path | None = None):
    """마커의 읽고-고쳐-쓰기를 직렬화한다. 남겨진 락은 나이로 파기한다."""
    path = lock_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(100):
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                stale = (time.time() - path.stat().st_mtime) > LOCK_STALE_SECONDS
            except OSError:
                stale = True
            if stale:
                _drop_lock(root)
            else:
                time.sleep(0.05)
            continue
        try:
            os.write(fd, str(os.getpid()).encode())
        finally:
            os.close(fd)
        try:
            yield
        finally:
            _drop_lock(root)
        return
    raise TimeoutError(f"마커 락을 얻지 못했다: {path}")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize(data: dict) -> dict:
    """단일 국면 시절의 마커를 복수 형태로 읽는다. 쓰기는 언제나 복수 형태다."""
    try:
        nxt = int(data.get("next_grant") or 1)
    except (TypeError, ValueError):
        nxt = 1
    lease = data.get("merge_lease")
    out = {
        "active_phases": dict(data.get("active_phases") or {}),
        "commit_grants": dict(data.get("commit_grants") or {}),
        # lease 키가 없는 마커는 빈 lease로 읽는다.
        "merge_lease": dict(lease) if isinstance(lease, dict) else {},
        "next_grant": max(nxt, 1),
    }
    legacy_phase = data.get("phase")
    if legacy_phase and legacy_phase not in out["active_phases"]:
        out["active_phases"][legacy_phase] = {"opened_at": data.get("opened_at", "")}
    legacy_until = data.get("commit_ok_until")
    if legacy_until and not out["commit_grants"]:
        out["commit_grants"]["grant-1"] = {
            "until": legacy_until, "reason": data.get("commit_reason", "")
        }
    return out


def load(root: Path | None = None) -> dict:
    """마커를 읽는다. 부재는 무국면(빈 형태)이고, 판독 불가는 예외다.

    게이트가 둘을 다르게 처분하므로 가르는 것이 이 함수의 계약이다.

    **읽기의 `OSError`도 판독 불가다.** 권한 거부·잠긴 파일을 `MarkerUnreadable`로
    바꿔 던진다. 그대로 올리면 `main`의 공통 그물이 받지 못해 `open`·`allow`·
    `clear-token`·`lease --acquire`·`lease --release`·`close --phase` 여섯이
    트레이스백으로 끝난다(실측).
    """
    path = marker_path(root)
    try:
        if not path.exists():
            return _normalize({})
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MarkerUnreadable(exc) from exc
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("마커 최상위가 객체가 아니다")
    return _normalize(data)


def save(data: dict, root: Path | None = None) -> Path:
    path = marker_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(_normalize(data), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(body, encoding="utf-8")
    os.replace(tmp, path)
    return path


def active_phases(data: dict) -> dict:
    return data.get("active_phases") or {}


def _deadline(grant: dict) -> datetime | None:
    try:
        return datetime.strptime(grant["until"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except (KeyError, TypeError, ValueError):
        return None


def fresh_grants(data: dict, now: datetime | None = None) -> dict:
    """만료되지 않은 grant만. 형식이 깨진 grant는 만료로 읽는다(차단 방향)."""
    at = now or _now()
    out = {}
    for gid, grant in (data.get("commit_grants") or {}).items():
        if not isinstance(grant, dict):
            continue
        deadline = _deadline(grant)
        if deadline and at < deadline:
            out[gid] = grant
    return out


def fresh_lease(data: dict, now: datetime | None = None) -> dict:
    """유효한 병합 lease. 만료·형식 파손은 빈 lease로 읽는다(회수 방향)."""
    lease = data.get("merge_lease") or {}
    if not isinstance(lease, dict) or not lease.get("owner"):
        return {}
    deadline = _deadline(lease)
    if deadline and (now or _now()) < deadline:
        return dict(lease)
    return {}


def gate_decision(
    data: dict, now: datetime | None = None, isolated_branch: str | None = None
) -> tuple[int, str]:
    """(종료값, 문면). 0=통과.

    관문이 지키는 것은 **메인 체크아웃의 공유 이력**이다. 격리 안의 커밋은 grant 없이
    통과한다 — 노드 브랜치의 커밋은 싱크가 병합하기 전까지 아무 데도 닿지 않는다.

    `isolated_branch`는 커밋이 일어나는 곳에서 실측된 값이고, 통과 조건은 그것이
    활성 국면의 노드 브랜치(`dag/<활성 국면>/<행>`)라는 것 하나다. 메인 체크아웃의
    커밋·분리 HEAD·이름이 다른 브랜치·이미 닫힌 국면의 잔재 트리는 여전히 막힌다.
    """
    phases = active_phases(data)
    if not phases:
        return 0, ""
    if fresh_grants(data, now):
        return 0, ""
    if isolated_branch and isolated_branch.startswith(f"{BRANCH_PREFIX}/"):
        # 통과 조건은 `dag/<활성 국면>/<행>` 하나다. 행 마디가 없거나 `ROW_RE` 밖이면
        # `worktree_open`이 만들 수 없는 이름이므로 격리 예외를 주지 않는다 — 관문은
        # 만든 주체가 아니라 실측된 브랜치 이름만 본다.
        phase, sep, row = isolated_branch[len(BRANCH_PREFIX) + 1:].partition("/")
        if sep and phase in phases and ROW_RE.fullmatch(row):
            return 0, ""
    names = sorted(phases)
    return 1, BLOCK_MESSAGE.format(
        phases=" · ".join(f"'{p}'" for p in names),
        script=Path(__file__).resolve(),
        ledgers=" · ".join(f".sdd/dag/{p}/파견표.md" for p in names),
    )


# --- 노드 격리(worktree) ------------------------------------------------


def wt_root() -> Path:
    """노드 worktree들이 사는 곳. 저장소 밖·동기화 밖이다.

    `DAG_WT_ROOT`는 시험용 seam이다.
    """
    env = os.environ.get(WT_ROOT_ENV)
    if env:
        return Path(env)
    local = os.environ.get("LOCALAPPDATA")
    return (Path(local) / "dag-wt") if local else (Path.home() / ".dag-wt")


def wt_path(phase: str, row: str) -> Path:
    return wt_root() / f"{validate_phase(phase)}{WT_SEP}{validate_row(row)}"


def branch_name(phase: str, row: str) -> str:
    return f"{BRANCH_PREFIX}/{validate_phase(phase)}/{validate_row(row)}"


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def _linked_worktrees(root: Path) -> list[dict]:
    """주 체크아웃을 뺀 링크된 worktree 목록. [{path, branch}]"""
    out = _git(root, "worktree", "list", "--porcelain").stdout
    entries: list[dict] = []
    cur: dict = {}
    for line in out.splitlines():
        if line.startswith("worktree "):
            if cur:
                entries.append(cur)
            cur = {"path": line[len("worktree "):].strip(), "branch": ""}
        elif line.startswith("branch ") and cur:
            cur["branch"] = line[len("branch "):].strip().replace("refs/heads/", "", 1)
    if cur:
        entries.append(cur)
    root_resolved = root.resolve()
    return [e for e in entries if Path(e["path"]).resolve() != root_resolved]


def isolated_commit_branch(cwd: Path | None = None) -> str | None:
    """지금 커밋이 일어나는 곳이 노드 격리 트리인가. 그렇다면 그 브랜치 이름.

    판별식은 둘의 곱이다.

    1. **링크된 worktree인가** — `--absolute-git-dir`(그 트리 전용 디렉토리)와
       `--git-common-dir`(공유 디렉토리)가 갈리는가. 주 체크아웃에서는 둘이 같으므로
       메인 체크아웃의 커밋은 이 문을 통과할 수 없다.
    2. **브랜치를 체크아웃했는가** — `symbolic-ref HEAD`. 분리 HEAD는 이름이 없어
       국면 소속을 판정할 수 없으므로 통과하지 않는다.

    이름이 `dag/<국면>/<행>`인지와 그 국면이 활성인지는 `gate_decision`이 판정한다.
    여기서는 실측만 한다.

    git이 없거나 저장소 밖이면 None이다 — 판정 불가는 통과가 아니라 평시 처분으로
    돌아간다.
    """
    cwd = Path(cwd) if cwd else Path.cwd()

    def _out(*args: str) -> str:
        result = _git(cwd, *args)
        return result.stdout.strip() if result.returncode == 0 else ""

    git_dir, common = _out("rev-parse", "--absolute-git-dir"), _out("rev-parse", "--git-common-dir")
    if not git_dir or not common:
        return None
    common_path = Path(common) if Path(common).is_absolute() else cwd / common
    try:
        if Path(git_dir).resolve() == common_path.resolve():
            return None  # 주 체크아웃
    except OSError:
        return None
    return _out("symbolic-ref", "--quiet", "--short", "HEAD") or None


def _branch_list(root: Path, *args: str) -> list[str]:
    out = _git(root, "branch", *args, "--format=%(refname:short)").stdout
    return [line.strip() for line in out.splitlines() if line.strip()]


def _assert_base(root: Path, branch: str, base: str) -> None:
    """동결된 base 위에 선 브랜치인가. 아니면 열지 않는다."""
    if _git(root, "rev-parse", "--verify", f"{base}^{{commit}}").returncode != 0:
        raise WorktreeConflict(f"base 커밋을 해석할 수 없다: {base}")
    if _git(root, "merge-base", "--is-ancestor", base, branch).returncode != 0:
        raise WorktreeConflict(
            f"브랜치 {branch}가 base {base} 위에 서 있지 않다 — 삭제하지 않고 멈춘다"
        )


def worktree_open(phase: str, row: str, base: str, root: Path | None = None) -> dict:
    """격리 트리를 연다. 생성·재사용·복구의 셋으로 닫히고, 나머지는 예외다.

    미등록 경로·다른 체크아웃·base 불일치는 지우지 않는다 — 채록 판단은 기계 몫이
    아니다.
    """
    root = root or project_root()
    path = wt_path(phase, row)
    branch = branch_name(phase, row)
    path.parent.mkdir(parents=True, exist_ok=True)
    _git(root, "worktree", "prune")

    registered = {
        Path(e["path"]).resolve(): e["branch"] for e in _linked_worktrees(root)
    }
    here = registered.get(path.resolve())
    if here is not None:
        if here != branch:
            raise WorktreeConflict(
                f"경로가 다른 브랜치에 체크아웃되어 있다: {path} → {here or '(분리 HEAD)'}"
            )
        _assert_base(root, branch, base)
        return {"action": "재사용", "path": str(path), "branch": branch}

    if path.exists() and any(path.iterdir()):
        raise WorktreeConflict(f"등록되지 않은 경로가 이미 있다: {path}")

    if _branch_list(root, "--list", branch):
        _assert_base(root, branch, base)
        result = _git(root, "worktree", "add", str(path), branch)
        action = "복구"
    else:
        result = _git(root, "worktree", "add", "-b", branch, str(path), base)
        action = "생성"
    if result.returncode != 0:
        raise WorktreeConflict(f"git worktree add 실패: {result.stderr.strip()}")
    return {"action": action, "path": str(path), "branch": branch}


def sweep(phase: str, root: Path | None = None) -> dict:
    """국면의 잔존 트리·브랜치를 회수한다. 남긴 것은 지우지 않고 보고한다.

    남기는 사유의 열거는 전거 【sweep · 잔존 0이 될 때까지 돌린다 · 남긴 것은 지우지 않고 보고한다】이 진다 — 여기 다시
    적으면 두 자리가 각자 늙는다. 정상 종결한 노드의 브랜치는 싱크가 지우므로 여기
    오는 것은 싱크가 못 돈 잔재다.
    """
    root = root or project_root()
    prefix = f"{BRANCH_PREFIX}/{validate_phase(phase)}/"
    report = {
        "removed_worktrees": [], "kept_worktrees": [],
        "deleted_branches": [], "kept_branches": [], "kept_branch_reason": {},
    }
    _git(root, "worktree", "prune")
    # 등록 브랜치가 국면을 명시하면 그것이 소속이다. 이름 판별은 등록이 없는 트리에만
    # 쓰고, 그 이름의 국면 마디는 `wt_path`에서 도출한다 — 구분자를 여기서 다시 적으면
    # 좌표식이 두 자리에 살고, 남의 국면명이 그 접두에 걸려 도는 트리가 회수된다.
    head = wt_path(phase, "0").name.removesuffix("0")
    for entry in _linked_worktrees(root):
        path = Path(entry["path"])
        by_branch = entry["branch"].startswith(prefix)
        by_path = (
            not entry["branch"].startswith(f"{BRANCH_PREFIX}/")
            and path.name.startswith(head)
            and path.parent.resolve() == wt_root().resolve()
        )
        if not (by_branch or by_path):
            continue
        if not path.exists():
            continue
        if _git(path, "status", "--porcelain").stdout.strip():
            report["kept_worktrees"].append(str(path))
            continue
        if _git(root, "worktree", "remove", str(path)).returncode == 0:
            report["removed_worktrees"].append(str(path))
        else:
            report["kept_worktrees"].append(str(path))
    merged = set(_branch_list(root, "--merged", "HEAD", "--list", f"{prefix}*"))
    for branch in _branch_list(root, "--list", f"{prefix}*"):
        if branch not in merged:
            reason = "병합되지 않은 커밋이 있다"
        elif _git(root, "branch", "-d", branch).returncode == 0:
            report["deleted_branches"].append(branch)
            continue
        else:
            reason = "트리가 남아 있어 체크아웃 중이다"
        report["kept_branches"].append(branch)
        report["kept_branch_reason"][branch] = reason
    return report


def _foreign_tree(root: Path, tree: Path) -> bool:
    """트리가 다른 저장소 소속의 worktree인가.

    dag-wt 루트는 저장소 간 공유라, `.git` 링크의 gitdir가 이 저장소의 `.git` 밖을
    가리키는 트리는 이 저장소의 잔재가 아니다. 링크 부재·판독 불가·서식 밖은
    False다 — 소속을 판정하지 못하면 고지 쪽으로 기운다.
    """
    try:
        text = (tree / ".git").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    m = re.match(r"gitdir:\s*(.+)", text.strip())
    if not m:
        return False
    gitdir = Path(m.group(1).strip()).resolve()
    own = (root / ".git").resolve()
    return gitdir != own and own not in gitdir.parents


def leftovers(root: Path | None = None) -> dict:
    """중단된 국면이 남긴 격리 잔재.

    **활성 국면의 트리·브랜치는 잔재가 아니다** — 도는 런의 정상 자산이라 제외한다.
    **다른 저장소 소속의 트리도 잔재가 아니다**(`_foreign_tree`).
    마커를 못 읽으면 아무것도 제외하지 않는다(고지 쪽으로 기운다).

    읽기 전용이다 — 발견은 세션 훅이 하고 처분은 사람이 한다.
    """
    root = root or project_root()
    try:
        active = set(active_phases(load(root)))
    except (OSError, ValueError, json.JSONDecodeError):
        active = set()
    prefix = f"{BRANCH_PREFIX}/"
    branches = [
        b for b in _branch_list(root, "--list", f"{prefix}*")
        if b[len(prefix):].partition("/")[0] not in active
    ]
    trees = []
    base = wt_root()
    if base.is_dir():
        # `wt_path` 경유로 도출하지 않는다 — 그 경로는 `validate_phase`를 타서, 문법
        # 밖 국면명을 담은 마커가 예외로 고지 전체를 죽인다(위 도크스트링의 실패
        # 방향 위반). `WT_SEP` 직접 참조는 정본 상수 하나를 읽는 것이라 이중 정본이
        # 아니고, 문법 밖 국면명은 어느 트리와도 맞지 않아 고지 쪽으로 기운다.
        heads = [f"{ph}{WT_SEP}" for ph in active]
        trees = sorted(
            str(p) for p in base.iterdir()
            if p.is_dir()
            and not any(p.name.startswith(h) for h in heads)
            and not _foreign_tree(root, p)
        )
    return {"worktrees": trees, "branches": branches}


def _print_sweep(phase: str, report: dict) -> bool:
    """보고를 출력하고 잔존 유무를 돌려준다."""
    for path in report["removed_worktrees"]:
        print(f"[dag] worktree 회수: {path}")
    for branch in report["deleted_branches"]:
        print(f"[dag] 브랜치 회수: {branch}")
    kept = report["kept_worktrees"] + report["kept_branches"]
    for path in report["kept_worktrees"]:
        print(f"[dag] 잔존 — 미커밋 산출이 있어 남겼다: {path}")
    for branch in report["kept_branches"]:
        reason = report.get("kept_branch_reason", {}).get(branch, "삭제가 거부됐다")
        print(f"[dag] 잔존 — {reason}: {branch}")
    if kept:
        print(f"[dag] 국면 '{phase}' 잔존 {len(kept)}건 — 채록 후 수동 처분한다.")
    return bool(kept)


# --- 명령 ---------------------------------------------------------------


def _new_grant_id(data: dict, grants: dict) -> str:
    """번호는 단조 증가한다 — 만료로 비워진 번호를 다시 쓰면, ID를 쥐고 있던 싱크의
    뒤늦은 `clear-token`이 같은 번호를 받은 남의 grant를 해제한다."""
    n = int(data.get("next_grant") or 1)
    while f"grant-{n}" in grants:
        n += 1
    data["next_grant"] = n + 1
    return f"grant-{n}"


def _report_unreadable(exc: Exception) -> int:
    """판독 불가의 처분은 명령마다 같다 — 탈출 경로를 항상 병기한다."""
    sys.stderr.write(
        UNREADABLE_MESSAGE.format(
            path=marker_path(), err=exc, script=Path(__file__).resolve()
        )
        + "\n"
    )
    return 1


def cmd_status(args) -> int:
    try:
        data = load()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _report_unreadable(exc)
    phases = active_phases(data)
    if not phases:
        print("[dag] 활성 국면 없음")
        return 0
    for name in sorted(phases):
        print(f"[dag] 활성 국면 '{name}' (개설 {phases[name].get('opened_at', '?')})")
        print(f"[dag] 상태 정본: .sdd/dag/{name}/파견표.md")
    fresh = fresh_grants(data)
    if fresh:
        for gid in sorted(fresh):
            print(f"[dag] 커밋 grant {gid} 유효 — {fresh[gid]['until']} ({fresh[gid].get('reason', '')})")
    else:
        print("[dag] 유효한 커밋 grant 없음 — 커밋 차단 상태")
    lease = fresh_lease(data)
    if lease:
        print(f"[dag] 병합 lease 점유 — {lease['owner']} (만료 {lease['until']})")
    return 0


def cmd_open(args) -> int:
    with marker_lock():
        data = load()
        phases = active_phases(data)
        resumed = args.phase in phases
        if not resumed:
            phases[args.phase] = {"opened_at": _iso(_now())}
        data["active_phases"] = phases
        path = save(data)
    verb = "재개" if resumed else "개설"
    print(f"[dag] 국면 '{args.phase}' {verb} — 마커 {path}")
    return 0


def cmd_close(args) -> int:
    if args.all:
        # 회수는 락 밖에서 돈다 — 락을 쥔 채 수 초를 쓰면 병합 중인 싱크의 `allow`가
        # 대기 예산을 넘긴다.
        try:
            names = sorted(active_phases(load()))
        except (OSError, ValueError, json.JSONDecodeError):
            names = []
        for name in names:
            try:
                _print_sweep(name, sweep(name))
            except Exception as exc:  # 회수 실패가 탈출 경로를 막지 않는다.
                print(f"[dag] 회수를 건너뛴다 ({type(exc).__name__}: {exc}) — 잔재는 수동 확인한다.")
        with marker_lock():
            # grant ID의 일련번호는 넘긴다. 되감으면 `close --all` 전에 ID를 받아
            # 둔 싱크의 뒤늦은 `clear-token`이 같은 번호를 받은 새 grant를 해제한다
            # (`_new_grant_id`).
            try:
                serial = int(load().get("next_grant") or 1)
            except (OSError, ValueError, json.JSONDecodeError):
                serial = 1
            save({"next_grant": serial})
        print("[dag] 마커를 비웠다(무국면). 커밋 차단 해제.")
        return 0

    try:
        _print_sweep(args.phase, sweep(args.phase))
    except Exception as exc:
        print(f"[dag] 회수를 건너뛴다 ({type(exc).__name__}: {exc}) — 잔재는 수동 확인한다.")
    with marker_lock():
        data = load()
        phases = active_phases(data)
        phases.pop(args.phase, None)
        data["active_phases"] = phases
        if not phases:
            # grant도 lease도 국면에 속하지 않는다. 마지막 국면이 닫히면 함께 소멸한다.
            data["commit_grants"] = {}
            data["merge_lease"] = {}
        save(data)
        remaining = sorted(phases)
    if remaining:
        print(f"[dag] 국면 '{args.phase}' 종결. 남은 활성 국면: {' · '.join(remaining)}")
    else:
        print(f"[dag] 국면 '{args.phase}' 종결 — 활성 국면 없음. 커밋 차단 해제.")
    return 0


def cmd_sweep(args) -> int:
    """회수만 한다. 종결 행이 exit 0으로 잔존 0을 판정하는 자리다."""
    return 1 if _print_sweep(args.phase, sweep(args.phase)) else 0


def cmd_allow(args) -> int:
    with marker_lock():
        data = load()
        if not active_phases(data):
            print("[dag] 활성 국면이 없다 — grant가 필요 없다.")
            return 0
        grants = fresh_grants(data)  # 만료분은 여기서 소거된다
        gid = _new_grant_id(data, grants)
        until = _iso(_now() + timedelta(minutes=args.minutes))
        grants[gid] = {"until": until, "reason": args.reason}
        data["commit_grants"] = grants
        save(data)
    print(f"[dag] 커밋 grant {gid} 발급 {args.minutes}분 — {until} ({args.reason})")
    print(f"[dag] 해제: python {Path(__file__).resolve()} clear-token --grant {gid}")
    return 0


def cmd_lease(args) -> int:
    """메인 체크아웃 병합권. 0=획득(또는 해제·조회 성공), 1=남이 점유 중."""
    if args.status:
        try:
            lease = fresh_lease(load())
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return _report_unreadable(exc)
        if lease:
            print(f"[dag] 병합 lease 점유 — {lease['owner']} (만료 {lease['until']})")
        else:
            print("[dag] 병합 lease 비어 있음")
        return 0

    with marker_lock():
        data = load()
        held = fresh_lease(data)
        if args.release:
            if not held:
                print("[dag] 병합 lease가 비어 있다 — 해제할 것이 없다.")
                return 0
            if held["owner"] != args.owner:
                print(f"[dag] 병합 lease는 {held['owner']}의 것이다 — {args.owner}가 해제하지 않는다.")
                return 1
            data["merge_lease"] = {}
            save(data)
            print(f"[dag] 병합 lease 해제 — {args.owner}")
            return 0

        if held and held["owner"] != args.owner:
            print(f"[dag] 병합 lease를 {held['owner']}가 점유 중이다 (만료 {held['until']}).")
            print("[dag] 메인 체크아웃에 손대지 말고 `대기`로 반환한다 — 오케가 다시 쏜다.")
            return 1
        until = _iso(_now() + timedelta(minutes=args.minutes))
        data["merge_lease"] = {"owner": args.owner, "until": until}
        save(data)
    # 같은 소유자의 재획득은 연장이다.
    print(f"[dag] 병합 lease 획득 — {args.owner} {args.minutes}분 (만료 {until})")
    print(f"[dag] 해제: python {Path(__file__).resolve()} lease --release --owner {args.owner}")
    return 0


def cmd_clear_token(args) -> int:
    with marker_lock():
        data = load()
        grants = dict(data.get("commit_grants") or {})
        if args.all:
            data["commit_grants"] = {}
            save(data)
            print("[dag] 커밋 grant 전부 해제.")
            return 0
        if args.grant not in grants:
            print(f"[dag] 그런 grant가 없다: {args.grant} (남은 grant: {' · '.join(sorted(grants)) or '없음'})")
            return 1
        grants.pop(args.grant)
        data["commit_grants"] = grants
        save(data)
        remaining = sorted(grants)
    print(f"[dag] 커밋 grant {args.grant} 해제." + (f" 남은 grant: {' · '.join(remaining)}" if remaining else ""))
    return 0


def cmd_worktree_open(args) -> int:
    try:
        result = worktree_open(args.phase, args.row, args.base)
    except WorktreeConflict as exc:
        print(f"[dag] worktree 예외 — 열지 않았다: {exc}")
        return 1
    print(f"[dag] worktree {result['action']}: {result['path']}")
    print(f"[dag] 브랜치: {result['branch']}")
    return 0


def cmd_gate(args) -> int:
    try:
        data = load()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _report_unreadable(exc)
    code, message = gate_decision(data, isolated_branch=isolated_commit_branch())
    if message:
        sys.stderr.write(message + "\n")
    return code


def cmd_install_hook(args) -> int:
    """주 저장소 `.git/hooks/pre-commit`에 얇은 shim을 설치한다.

    링크된 worktree들은 `$GIT_COMMON_DIR/hooks`를 공유하므로 1회 설치로 전부 덮인다.
    """
    common = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        capture_output=True, text=True, check=True, cwd=str(project_root()),
    ).stdout.strip()
    hooks_dir = (project_root() / common).resolve() if not Path(common).is_absolute() else Path(common)
    hooks_dir = hooks_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    target = hooks_dir / "pre-commit"
    if target.exists() and not args.force:
        print(f"[dag] 이미 존재한다: {target} (덮어쓰려면 --force)")
        return 1
    shim = (
        "#!/bin/sh\n"
        "# dag 국면 커밋 관문. 정본: .claude/skills/do-dag/scripts/dag_marker.py\n"
        f'exec python "{Path(__file__).resolve().as_posix()}" gate\n'
    )
    target.write_text(shim, encoding="utf-8", newline="\n")
    try:
        os.chmod(target, 0o755)
    except OSError:
        pass
    print(f"[dag] 설치 완료: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    o = sub.add_parser("open"); o.add_argument("--phase", required=True); o.set_defaults(func=cmd_open)
    c = sub.add_parser("close")
    c.add_argument("--phase")
    c.add_argument("--all", action="store_true", help="활성 국면 전부를 닫고 마커를 비운다")
    c.set_defaults(func=cmd_close)
    a = sub.add_parser("allow")
    a.add_argument("--minutes", type=int, default=30)
    a.add_argument("--reason", default="")
    a.set_defaults(func=cmd_allow)
    ls = sub.add_parser("lease")
    ls.add_argument("--acquire", action="store_true")
    ls.add_argument("--release", action="store_true")
    ls.add_argument("--status", action="store_true")
    ls.add_argument("--owner", help="행 번호. 획득·해제에 필요하다")
    ls.add_argument("--minutes", type=int, default=30)
    ls.set_defaults(func=cmd_lease)
    t = sub.add_parser("clear-token")
    t.add_argument("--grant")
    t.add_argument("--all", action="store_true", help="발급된 grant 전부 해제")
    t.set_defaults(func=cmd_clear_token)
    s = sub.add_parser("sweep"); s.add_argument("--phase", required=True)
    s.set_defaults(func=cmd_sweep)
    w = sub.add_parser("worktree-open")
    w.add_argument("--phase", required=True)
    w.add_argument("--row", required=True)
    w.add_argument("--base", required=True, help="동결할 base 커밋(통상 메인 체크아웃 HEAD SHA)")
    w.set_defaults(func=cmd_worktree_open)
    sub.add_parser("gate").set_defaults(func=cmd_gate)
    i = sub.add_parser("install-hook"); i.add_argument("--force", action="store_true")
    i.set_defaults(func=cmd_install_hook)
    return p


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    parser = build_parser()
    args = parser.parse_args(argv)
    # 이름 문법은 어느 명령보다 앞선다.
    for attr, check in (("phase", validate_phase), ("row", validate_row)):
        value = getattr(args, attr, None)
        if value is not None:
            try:
                check(value)
            except ValueError as exc:
                parser.error(str(exc))
    if args.cmd == "close" and not (args.phase or args.all):
        parser.error("close에는 --phase 또는 --all이 필요하다")
    if args.cmd == "clear-token" and not (args.grant or args.all):
        parser.error("clear-token에는 --grant 또는 --all이 필요하다")
    if args.cmd == "lease":
        modes = [args.acquire, args.release, args.status]
        if sum(bool(m) for m in modes) != 1:
            parser.error("lease에는 --acquire · --release · --status 중 정확히 하나가 필요하다")
        if not args.status and not args.owner:
            parser.error("lease --acquire · --release에는 --owner(행 번호)가 필요하다")
    try:
        return args.func(args)
    except TimeoutError as exc:
        sys.stderr.write(f"[dag] {exc} — 다른 명령이 마커를 쓰고 있다. 잠시 뒤 다시 돌린다.\n")
        return 1
    except (ValueError, json.JSONDecodeError) as exc:
        return _report_unreadable(exc)


if __name__ == "__main__":
    raise SystemExit(main())
