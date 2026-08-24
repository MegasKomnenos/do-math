"""SessionStart·UserPromptSubmit 주입 — 활성 국면마다 이름과 파견표 좌표를 출력하고, 유효한 grant와 병합 lease도 고지한다.

주입하는 것은 **좌표뿐**이다. 상태·계수를 여기에 렌더하지 않는다 — 그 정본은
파견표이고, 요약해 주입하면 요약과 실물이 갈리는 이중 정본이 생긴다.

실패 방향: **항상 exit 0 + 고지**(사용자 확정). 배제하더라도 그 사실을 남긴다.

활성 국면이 없으면 국면 좌표를 출력하지 않는다. 격리 잔재 고지는 활성 국면의 유무와 마커 판독의 성패에 앞서 돈다. 훅 등록은 `.claude/settings.json`의 `SessionStart`와 `UserPromptSubmit`에서 확인한다. `dag_marker.py status`는 마커의 활성 국면·grant·lease만 확인한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _report_leftovers(dag_marker) -> None:
    """중단된 국면이 남긴 격리 잔재를 고지한다.

    트리가 저장소 밖에 살아 `git status`에 보이지 않으므로 이 채널이 유일한 고지다.
    활성 국면의 트리는 `leftovers()`가 제외한다. 무잔재면 무출력이다.
    """
    try:
        found = dag_marker.leftovers()
    except Exception as exc:
        print(f"[dag] 격리 잔재를 조회하지 못했다 ({type(exc).__name__}: {exc})")
        return
    for path in found["worktrees"]:
        print(f"[dag] 격리 잔재 worktree: {path}")
    for branch in found["branches"]:
        print(f"[dag] 격리 잔재 브랜치: {branch}")
    if found["worktrees"] or found["branches"]:
        print("[dag] 회수: python <do-dag scripts>/dag_marker.py sweep --phase <국면id>")


def _report_grants(dag_marker, data) -> None:
    fresh = dag_marker.fresh_grants(data)
    if not fresh:
        print("[dag] 유효한 커밋 grant 없음 — pre-commit이 커밋을 차단한다")
        return
    for gid in sorted(fresh):
        print(f"[dag] 커밋 grant {gid} 유효 — {fresh[gid]['until']} ({fresh[gid].get('reason', '')})")


def _report_lease(dag_marker, data) -> None:
    """점유 중인 병합 lease만 고지한다."""
    lease = dag_marker.fresh_lease(data)
    if lease:
        print(f"[dag] 병합 lease 점유 — {lease['owner']} (만료 {lease['until']})")
        print("[dag] 메인 체크아웃의 인덱스를 건드리지 않는다")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    try:
        import dag_marker
    except Exception as exc:  # 코어 부재·구문 오류까지 포함. 침묵하지 않고 고지만 한다.
        print(f"[dag] 국면 마커 모듈을 열지 못했다 — 주입 생략 ({type(exc).__name__}: {exc})")
        return 0

    _report_leftovers(dag_marker)

    try:
        data = dag_marker.load()
    except Exception as exc:
        print(f"[dag] 국면 마커를 읽지 못했다 — 주입 생략 ({type(exc).__name__}: {exc})")
        print(f"[dag] 마커 경로: {dag_marker.marker_path()}")
        return 0

    try:
        phases = dag_marker.active_phases(data)
        if not phases:
            return 0

        root = dag_marker.project_root()
        for name in sorted(phases):
            print(f"[dag] 활성 국면 '{name}' (개설 {phases[name].get('opened_at', '?')})")
            print(
                f"[dag] 상태·계수의 정본은 파견표다: "
                f"{root / '.sdd' / 'dag' / name / '파견표.md'}"
            )
        _report_grants(dag_marker, data)
        _report_lease(dag_marker, data)
    except Exception as exc:
        print(f"[dag] 마커 내용을 처리하지 못했다: {type(exc).__name__}: {exc}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
