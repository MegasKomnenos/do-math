# Codex 모델 목록 갱신 timeout의 범위 조사와 진단 개선

context.md R7.2를 완료한다. 원 실행의 모델 목록 갱신 timeout은 최종 응답 제출·수락이 있었던 실행 안의 사건이다. 이를 모델 작업 전체 실패로 취급하지 않고 실제 관측 가능한 진단을 개선한다. 네트워크/공급자 내부 원인 미확정이라는 경계를 보존한다. 근거 없이 timeout을 늘리거나 모델 목록 확인을 제거해 해결했다고 선언하지 않는다.

정본 AGENTS.md와 이음새/시험 지침을 읽는다. `C:\math\.skill-workspace\parking-unimodality-20261021\audit\subcommand-failures.json`, execution-audit.json 및 연결된 work/runs의 원 CLI stderr/jsonl/worker-status/수락 기록을 읽기 전용으로 대조한다. timeout 발생 위치(제품/CLI manager/공급자), 판본과 확인 가능한 요청·반환·종료·경과 정보, 당시 없는 자료를 구별한다. 로컬 설치 CLI help/version/소스/기존 log에 접근할 수 있으면 필요한 부분만 읽되 비밀값은 출력·보존하지 않는다.

`worker_request`, `codex_worker`, `cli_worker`, `codex_adapter.LocalCLIAdapter/CodexExecAdapter`, model_call과 현재 진단/결과 보존 소비를 추적한다. 제품이 이미 stderr와 성공/실패를 충분히 분리하면 그 사실을 입증하고 실제 사용자/다음 운영 판단에서 빠진 진단 정보만 최소한으로 보완한다. 비치명 warning이 정상 완료를 실패·출력 수리·무조건 재시도로 바꾸지 않게 한다. 반대로 실제 CLI 작업 실패를 성공으로 삼키지 않는다. 단순 텍스트 한 줄로 공급자 원인이나 원격 종료를 확정하지 않는다.

제품 수정은 허용된 worker/adapter/관측 모듈과 해당 시험, `references/CLI-실행-계약.md` 및 자기 결과 문서에 한정한다. 새 결과 필드가 중앙 저장/스키마/출력 소비 수정을 요구하면 먼저 기존의 의미 있는 진단 경로 재사용 가능성을 검토한다. 범위 밖 코드 수정이 실제 필요한 구체적 원인은 report에 심볼·요구 변경과 함께 남겨 manager가 배정하도록 한다. 서비스 자체·외부 CLI/서버는 수정하지 않는다.

실제 증거의 replay나 최소 worker/adapter 시험으로 warning+정상 final/종료와 실제 실패의 구별 및 진단 보존을 확인한다. 원 timeout 재발을 만들려고 새 유료 모델 호출이나 장시간 네트워크 실패를 반복하지 않는다. 필요한 선택 시험만 한 프로세스로 실행한다. 문서만으로 끝내는 경우에도 가능한 제품 개선이 무엇이며 왜 코드 변경이 필요 없는지 실제 소비와 함께 설명한다.

`docs/do-math/flow-repair-20261021/codex-refresh-diagnostics.md`에 확인한 원인 범위, 구현 개선, 검증 명령/결과, 외부 원인 때문에 남은 한계와 추가로 필요한 자료를 남긴다. 미확정 외부 원인은 제품 개발 전체를 임의로 blocked로 만드는 근거가 아니다. 정본을 바꾼 경우 writing-skills SKILL.md/공식 생성기로 Codex 미러를 맞추되 다른 스킬/.agents/diff 변경은 제외한다. report.json에 실제 변경을 기록하고 서비스 report 검사를 수행한다. 원 연구/HOLD/예약은 유지한다.
