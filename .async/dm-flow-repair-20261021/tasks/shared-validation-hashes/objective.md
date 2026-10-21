# 공통 검사 입력과 해시 오류·현재성 분류 수리

## 맡은 결과와 경계

context.md R4~R5를 구현·필요한 검증까지 완료한다. 같은 잘못된 제출을 작업자 사전 검사, 중앙 접수, 실제 적용에서 공통 규칙으로 반려하고 출력 수리로 보내며, 실제 내용·사용 효력·권한 변경은 그 원인에 맞는 별도 처리로 연결한다. 기존 공통 함수가 있다는 사실을 보존하고, 상속 체계나 모든 검사에 적용하는 새 프레임워크를 도입할 이유로 확대하지 않는다.

정본 AGENTS.md, `scripts/이음새-정본.md`, `scripts/tests/시험-지침.md`, 공용 seams와 context를 읽는다. 원자료는 `C:\math\.skill-workspace\parking-unimodality-20261021\audit\reproduce_causes.py`, reproduction-results.json, snapshot 및 work/runs의 EX-01M5D0ZPXND4CN3VV67DA6HGB2 보존 입력·응답과 관련 감사 보고다. 자료는 읽기 전용이며 시험 입력은 복사해 쓴다.

## 구현할 행동

- `context_store`의 역할 과제 상세와 검사 문맥을 만드는 경로를 추적한다. 계획 역할의 전체 과제 catalog를 유지하면서 공통 검사에 필요한 정확한 의미의 `content_sha256`을 제공한다. 단지 이번 한 입력에 수작업 해시를 넣는 수리가 아니다. 값 부재·미지 대상·잘못된 선언과 실제 전제 변경을 구별한다.
- `integration.inspect_bundles`, `bundle_impact_request`, `apply_bundles`, `submission`/submission_tool의 사전·접수·preview와 core_engine 실제 수신을 연결한다. 같은 구조·참조·고정 입력 해시 조건은 한 구현을 호출하게 하고, 적용 시 live 판본·영향·권한·CAS 같은 추가 검사는 각 위치에 둔다. 두 위치에 같은 해시 누락 규칙을 복제하지 않는다. 공통 판단의 필수 입력 부재가 검사를 우회하지 못하게 한다.
- `input_basis.CurrentnessChanged`는 이미 존재하는 명시적 실제 전제 변경 신호다. 누락된 previous_hashes나 제출 구조 오류를 단계 이름이 currentness라는 이유로 `integration.currentness`/`premises_changed`로 보내지 않는다. 실제 변경은 정확한 입력/권한 대조와 오류 의미에 따라 판정한다. 권한 상실과 사용자 정지에 관한 적용 경계는 유지한다. 저장·환경·게시 실패를 생산자 출력 오류로 덮지 않는다.
- `failure_kind`, `submission_outcome`, core_engine의 출력 수리/재판단/게시 대기 소비까지 확인한다. 잘못된 응답을 새 입력 전제로 판단하는 실행을 열었던 결함을 고친다. R2~R3 개정 처분/운영 질문의 새 도메인 동작은 설계/후속 작업의 소유이며 이 작업에서 별도로 설계하지 않는다.

공통 입력과 오류의 정본을 바꿨다면 실제 정의와 소비자를 코드 주석 또는 `scripts/이음새-정본.md`에 갱신하고 `docs/do-math/flow-repair-20261021/shared-validation-hashes.md`에 확인 결과를 남긴다. 허용된 코드 파일만 수정한다. 추가 파일의 수정이 실제로 필요하면 이유와 정확한 후속 범위를 보고한다.

## 완료 판단에 필요한 최소 확인

기존 시험을 먼저 찾고 결함 재현을 추가/보강해 원판의 실패와 수리판의 통과를 확인한다. 같은 실제 소비 입력에서 (1) missing previous_hashes, (2) 올바른 고정 해시, (3) 실제 내용/사용 효력 변경, (4) 권한 상실의 공통 판단과 위치별 결과·후속 소유자를 대조한다. 모든 조합의 전체 실행을 반복할 필요는 없지만, 실제 입력 생성과 중앙/적용 소비가 연결됐다는 근거는 필요하다. 감사 원 입력이 현행 계약에 해당하는 부분과 새 시험이 직접 구성한 부분을 구별한다. 코드만으로 확인한 소비자는 정적 확인으로 남긴다.

작업자는 동시에 시험 프로세스 하나만 실행한다. 변경 성질과 고친 영역의 선택 시험만 수행하며 전체 회귀는 후속 통합 단계에 맡긴다. 실행 중 자기 소스는 편집하지 않는다. 새로운 자료는 task evidence에 보존하고 원 연구/HOLD/예약을 건드리지 않는다.

정본을 고친 뒤 공식 writing-skills SKILL.md와 `scripts/build_skill_mirrors.py`를 읽고 공식 생성기로 Codex do-math 사본을 맞춘다. 생성 중 다른 스킬 변화가 나오면 통합 대상에 포함하지 않는다. `.agents/diff` 기준 변경은 이번 배정에 없으며 실제 필요한 사유를 보고한다. report.json의 변경 목록은 실제와 일치시켜 서비스 report 검사로 확인한다. 설계·원인·직접 확인한 결과·미확인 범위를 남기고 전체 개발 완료라고 표현하지 않는다.
