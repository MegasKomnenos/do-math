# phase 006 manager 판단

codex-schema의 partial을 승인하고 phase 007 provider-consumers를 배정한다. A1/A2/A4의 Codex 전달 수리와 대표 실호출은 근거가 있다. A3/A5의 관련 회귀는 직접 소비 11건의 실패와 저장 pair의 성공 표본 공백 때문에 완료되지 않았다. 이 구별을 유지하며 개발 완료를 선언하지 않는다.

## 원자료와 현재 판본

공용 문서를 수정하기 전에 report 전문을 읽고 report 검사를 통과했다. `verification.json`과 `report-check.json`이 검수 좌표다. 시작 소스 2,624개는 phase 005 종료와 같았고 종료 2,640개는 현재 원파일과 전부 같았다. 실제 변경 50개가 report changes 및 writes에 정확히 대응했다. 현재 HEAD는 9c917b644360ebdb0d6fd0e0cc8ef3191f4956b8이다.

공식 원보고 9묶음의 selected, 고유 row, counts와 실제 명령의 exit를 대조했다. 수리 전 1실패, 의미 회귀 6통과, 관련 67건 중 5실패, 수정한 4건의 통과, 의미 보강 6통과를 각각 원결과로 유지한다. 직접 소비 45건은 34통과·11실패다. 정본 corpus 18통과와 미러 14통과는 각각 최종 Python 865개와 동일한 판본이다. 다른 중간 보고의 최종 소스 차이는 verification의 changed_since에 남겼다. 이 부분 결과를 합산해 최종 전체 일반 성공으로 만들지 않는다.

Codex 새 실호출은 공식 1선택·1통과·exit 0이며 11개 판정이 전부 참이다. 원파일에서 봉투 안의 의미 output, 원 schema와 전송 schema 설명의 동등성, worker schema hash와 snapshot, prompt, raw final과 선택 final, nonce 파일과 checkpoint를 확인했다. 실제 명령·worker 상태와 원자료는 live 및 promotion에 보존돼 있다. live 이후 runtime 124개와 smoke helper는 불변이고 이후 Python 수정은 corpus 검사 3모듈뿐이다. 비용·실제 모델명·내부 요청 수는 미보고 상태로 유지한다.

기존 17개 manifest 항목과 녹화 파일은 유지됐고 새 Codex 성공만 추가됐다. 양쪽 corpus는 각각 18항목·51파일·223,685바이트·50개 명시 SHA 참조다. manager가 현재 102개 경로의 Git raw/clean을 실제 `/` 상대 경로 argv로 대조했으며 불일치는 없다. 작업트리/clean 결과를 제품의 staged blob이나 커밋 성공으로 확대하지 않는다. 공식 생성기 `--check`의 1,305파일 일치와 skill-only verified는 task의 실제 exit 0 및 불변 소스에 결속한다.

관리 검산 스크립트의 첫 두 실행은 역사 recording에 bytes가 항상 있다는 가정과 worker 상태의 키를 exit_code로 읽은 오류 때문에 각각 KeyError였다. 실제 schema에서는 bytes가 선택적이고 worker 키는 cli_exit_code다. 현재 정본을 확인해 보조 검산을 고친 뒤 실제 exit 0을 얻었다. 이는 관리 도구의 입력 가정 오류이며 제품 시험의 성공/실패 수에 포함하지 않는다.

## 발견 처분과 다음 범위

F1은 resolve다. 원 역할 schema를 보존하는 문자열 봉투와 최종 의미 검증을 현재 코드에서 확인했고 새 실호출이 원 거부를 해소했다. 원 schema의 제약과 native final/worker/종료 결속을 제거하지 않았다. G7 전체로 확대하지 않으며 원 Codex HTTP 400은 역사 실패로 유지한다.

F2는 carry다. 9개 probe·1개 repair·1개 native storage 실패를 원 traceback과 fixture에 대조했다. operator_finish_scene와 operator_probe_inputs의 schema 가정, 명시 raw final, 원 schema와 CLI schema를 같게 보던 단언을 함께 수정해야 한다. 정적 조회에서 같은 도우미를 쓰는 cross_installation의 repair_outcome 최상위 가정도 확인했다. 이는 task가 보고한 chunk 사례와 함께 미실행 범위로 배정하며 추가 실제 실패 수로 세지 않는다. malformed raw의 구체적인 collector 반려와 정상 final 대조군도 유지해야 한다.

F3도 carry다. pairs의 합성 collected 입력은 source_request를 만들지 않는다. 현재 classify_run이 그 요청에서 공급자를 판별하므로 두 공급자의 비결박 표본은 output_validation으로 끝난다. test_pairs는 저장 가능성만 보아 그 결과를 받아들인다. phase 007은 실제 collector 계약에 맞는 표본과 실제 status·output·collection/error_kind 단언을 연결한다. 성공 표본이 실패가 되어도 통과하는 현 상태를 수리 전 새 단언으로 포착하게 했다.

F4는 resolve다. 기존 Claude 원자료의 현재 수신 결과, 동일 prompt/schema, 변경되지 않은 worker/tool 12모듈, 경로·버전/help 관찰로 한정 재사용을 승인한다. 과거 CLI 바이너리 SHA는 미기록이며 바이트 동등성을 주장하지 않는다. 새 Claude/background 호출은 없고 기존 background의 passed=false 및 승인된 성질의 경계도 유지한다.

phase 007은 제품 runtime을 읽기 전용으로 두고 fixture와 직접 소비 시험을 수정한다. 동일 support helper, 시험 템플릿·캐시·생성기를 함께 쓰므로 하나의 task로 묶었다. 읽기 검토를 병렬로 추가해 미완성 fixture의 결과를 기다리게 하지 않는다. 완료 고정판의 독립 최종 review에는 병렬성을 사용할 수 있다. 다음 task를 실제로 시작하는 책임은 run.py에 있다.

## 공용 문서와 관리 보존

context C2/C5/C8/C9/C11/C12를 갱신하고 C1/C3/C4/C6/C7/C10 및 G1~G8은 그대로 보존했다. B49의 전달·반려·수치·종료 slice는 실제 diff, 현재 소비자 및 새 관련 회귀로 한정 검토했다. 두 Temp 원보고가 없는 사실을 유지하고 역사 counts는 새 근거로 합산하지 않았다. plan은 Codex 대표 호출을 검수된 결과로 옮기고 007의 정확한 수정·회귀 책임을 기록했다. 다른 문서·의미 질문과 실제 Job/Lean/예약/학술/L01·전체 일반/T3/변이·최종 review는 남는다. seams는 구현된 코드 정본과 시험 소비 책임을 설명하도록 갱신했으며 S 항목이나 제품 계약을 새로 개정하지 않았다. `common-docs.diff`와 `common-docs-review.json`에 전후 대조를 남겼다.

관련 회귀를 완료하기 전이므로 공급자 제품 후보를 작업트리에 둔다. 이번 관리 기록, task 원보고와 필요한 원자료, 다음 배정 및 기억 노드만 커밋한다. 이번 50변경의 원바이트는 pending-products.zip으로 별도 보존했다. archive는 실패가 남은 후보이며 승인된 제품 판본이나 자동 복원 지시가 아니다. 보존할 파일과 로컬에 남길 중복 자료는 preservation.json에 명시한다.
