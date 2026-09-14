# 수학 연구 작업 공간

2026-09-14에 기존 연구 실행 상태를 정리했다. 새 연구는 빈 상태에서 시작한다. 과거 탐사·수집·실험의 결과, 완료 판정과 대기 작업을 자동으로 이어받지 않는다.

## 진입점

- [연구 공간과 보존 입력](research/README.md)
- [do-math 사용 안내](.claude/skills/do-math/README.md)
- [학술자료 MCP](services/scholarly-mcp/README.md)
- [do-math 교육 자료](docs/learning/do-math/MISSION.md)
- [보편 연구 개념](CONTEXT.md)과 [도구 통합 설계](docs/do-math/통합-설계.md)
- [작업 기억 색인](기억/색인.md)
- [키 반복 도구](virtual-f-key-repeater/README.md)

## 정리 범위

기존 `dag/`, `experiments/`, `.sdd/`, `임시/`와 연구 수집·판독·실행 디렉터리를 작업 트리에서 제거했다. 공통 스킬·서비스·설계·검증 기록·작업 기억은 보존했다. 교육 자료는 `docs/learning/do-math/`에 모았다.

일괄 삭제가 자동 승인 정책에 의해 거부되어, 제거 대상의 실물은 이 호스트의 `C:\math-retired-20260914`에 원래 상대 경로로 보관했다. 이 폴더는 Git 커밋·푸시에 포함되지 않으며 디스크 공간은 회수하지 않았다. 과거 문서의 연구·임시 파일 경로는 이 보관 폴더 또는 정리 전 Git 이력의 좌표다.

인증 정보와 실행 중 서비스의 Python 환경, 서비스 자료·검증 근거, Lean 도구체인은 로컬 실행 기반으로 유지한다. `.skill-workspace/`의 도구체인 외 과거 실행 자료도 위 보관 폴더로 옮겼다. Windows 접근 권한 때문에 이동할 수 없는 임시 폴더 두 개는 해당 위치에 남아 있다: `.skill-workspace/do-math-hook-probe-wck5bjg6/`, `docs/do-math/구현-검증-2026-09-14/elevated-cli-profile/do-math-codex-ntiwy50w/`.
