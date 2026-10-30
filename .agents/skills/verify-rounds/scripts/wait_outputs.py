"""반환 파일 대기 — codex 백그라운드 실행의 포그라운드 대기 호출.

인자 경로 전건이 「비어 있지 않은 파일」로 서면 「완료」를 내고 exit 0. 디렉토리는
항목 유무와 관계없이 완료로 보지 않는다. 30초 간격 검사 스무 번(호출 하나가 약
570초 — Bash 도구 최대 timeout 600초 안) 안에 서지 않으면 남은 경로를
「대기:」로 내고 exit 3 — 부르는 쪽이 같은 호출을 다시 낸다. 인자가 없으면 exit 2.
호출 하나가 Bash 도구 기본 timeout 120초를 넘으므로 부르는 쪽이 `timeout: 600000`을 준다.

호출 계약의 정본은 verify-rounds `SKILL.md` §5.6이다.
"""

import pathlib
import sys
import time

CHECKS = 20
INTERVAL = 30  # 초. (CHECKS - 1) × INTERVAL = 570초로 Bash 최대 timeout 600초 안이다

def 섰다(p: pathlib.Path) -> bool:
    """크기가 0보다 큰 파일만 완료로 본다."""
    return p.is_file() and p.stat().st_size > 0


def main(argv: list[str]) -> int:
    if not argv:
        print("사용: wait_outputs.py <반환 파일> ...", file=sys.stderr)
        return 2
    paths = [pathlib.Path(p) for p in argv]
    for i in range(CHECKS):
        missing = [str(p) for p in paths if not 섰다(p)]
        if not missing:
            print("완료")
            return 0
        if i < CHECKS - 1:
            time.sleep(INTERVAL)
    print("대기:", *missing)
    return 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
