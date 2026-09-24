# 수학 연구 작업 공간

이 저장소에는 수학 연구 공간과 do-math 실행 스킬, 지원 서비스, 설계·검증 문서, 작업 기억을 둔다. 2026-09-14에는 이전 연구 실행 상태를 정리했다. 그 뒤 시작하는 새 연구는 과거 탐사·수집·실험의 결과, 완료 판정과 대기 작업을 자동으로 이어받지 않는다.

## 진입점

- [연구 공간과 보존 입력](research/README.md)
- [do-math 사용 안내](.claude/skills/do-math/README.md)
- [학술자료 MCP](services/scholarly-mcp/README.md)
- [Jev CLI 사용 안내](services/jev-cli/README.md)
- [do-math 교육 자료](docs/learning/do-math/MISSION.md)
- [보편 연구 개념](CONTEXT.md)과 [도구 통합 설계](docs/do-math/통합-설계.md)
- [작업 기억 색인](기억/색인.md)
- [키 반복 도구](virtual-f-key-repeater/README.md)

## 현재 디렉터리의 역할

- `.claude/skills/`는 스킬의 수기 편집 정본이고 `.agents/skills/`는 Codex용 생성 사본이다. 사본은 [생성 절차](.claude/skills/writing-skills/references/멀티런타임_동기화.md)에 따라 동기화한다.
- `docs/`에는 설계, 구현 경과와 검증 기록을 둔다. 선별해 보존한 do-math 정적 검토 보고서와 그 고정 소스 근거는 `docs/do-math/review-evidence/`에 있다.
- `research/`에는 연구 입력과 결과를, `services/`에는 독립 도구를, `기억/`에는 커밋과 결합한 작업 기억을 둔다.
- `임시/`에는 Git이 추적하는 검증 자료와 Git에서 제외한 로컬 근거가 함께 있다. `docs/do-math/implementation-v5/traceability.json`이 가리키는 역사적 실행 사본은 해시 검사를 위해 이 저장소의 `임시/`에 유지한다.
- `.skill-workspace/`는 도구체인과 로컬 실행 기반을 담는다. `.codex/reviews/`의 원시 검토 실행 출력은 Git에서 제외하며, 보존할 보고서와 근거는 `docs/`로 선별한다. `.credentials/`는 로컬 인증 정보다.

## 2026-09-14 정리 이력

당시의 `dag/`, `experiments/`, `.sdd/`, `임시/`와 연구 수집·판독·실행 디렉터리를 작업 트리에서 제거했다. 공통 스킬·서비스·설계·검증 기록·작업 기억은 보존했다. 교육 자료는 `docs/learning/do-math/`에 모았다. 현재 `임시/`의 검증 자료와 로컬 근거는 그 뒤에 생긴 것이다.

일괄 삭제가 자동 승인 정책에 의해 거부되어, 제거 대상의 실물은 이 호스트의 `C:\math-retired-20260914`에 원래 상대 경로로 보관했다. 이 폴더는 Git 커밋·푸시에 포함되지 않으며 디스크 공간은 회수하지 않았다. 과거 문서의 연구·임시 파일 경로는 이 보관 폴더 또는 정리 전 Git 이력의 좌표다.

인증 정보와 서비스 자료·검증 근거, Lean 도구체인은 로컬에 유지한다. 실행 중인 서비스의 Python 환경도 유지한다. 2026-09-14 당시 `.skill-workspace/`에 있던 도구체인 외 과거 실행 자료는 위 보관 폴더로 옮겼다.
