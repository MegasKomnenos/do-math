# do-math 작업 흐름 수리 기록

개발은 2026-10-21 08:19 KST에 최종 독립 검토와 manager 수용을 마치고 종료됐다. 공용 맥락·계획·인터페이스, 사용자 원문, queue·설정, task 지시·보고·통합 기록, manager 판단과 최종 검토서는 Git에 보존한다. 현재 결과는 [plan.md](plan.md)와 [context.md](context.md), 최종 검토는 [assessment.md](tasks/final-contract-review/assessment.md)에서 확인한다.

`objects/`, 각 task의 `baseline.json`·`result.json`·`archive.json`·`cleanup.json`, 상세 `evidence/`, CLI 로그와 `runtime/`는 이 호스트의 로컬 보관 자료다. 정확한 복원과 검증에 필요한 자료이므로 재생성 가능한 캐시로 취급하지 않는다. Git clone만으로 이 자료들까지 복원되지는 않으며, 이관할 때는 기록 디렉터리를 별도로 백업해야 한다. task 작업 사본은 서비스가 보관을 확인한 뒤 이미 제거했다.

수리 전 원인 조사는 [연구 보고서](../../research/parking-unimodality-audit-2026-10-21/원인-분석.md)에 있다. 그 보고서의 코드 설명은 수리 전 구현과 실행을 대상으로 한다. 원 구현은 주 저장소의 `9c2dfca4fe89f52dedc1be45490b5adcda79ea79`에서, 원 실행과 감사 자료는 로컬 `C:\math\.skill-workspace\parking-unimodality-20261021\`에서 확인한다. 현재 제품의 판단 근거는 이번 개발의 최종 검토다.

원 수학 연구 인스턴스의 HOLD/paused는 유지했다. 기록 정리에서 연구나 개발 서비스를 재시작하지 않았다. 확인 범위는 보존된 선택 시험·통합 확인·독립 검토와 소스 판본 대조다. 여러 판본의 최신 관측을 모은 4618 passed/1 skipped는 최종 판본의 한 번의 전체 회귀가 아니다. 새 코드의 실제 연구 운전과 외부 Codex timeout의 하위 원인은 아직 확인하지 않았다.
