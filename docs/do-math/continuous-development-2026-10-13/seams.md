# 현재 경계 계약의 사용

phase 001의 독립 분석과 phase 002~006의 work는 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring이 정본이다. 공급자 호출의 의미는 contracts.action_schema·ModelRunner.run·model_call.classify_run·real_ports·adapter/parser가 정의한다. 현재 결과와 남김은 context C11/C12에 있다.

phase 006이 구현한 Codex 비결박 전송의 정본은 do_math/provider_final.py의 output_contract·semantic_output이다. ModelRunner가 원 schema를 output.schema.json에 보존하고 전송 schema를 transport.schema.json으로 넘긴다. source_request·worker snapshot/hash·native final과 종료는 기존 수집 경계를 거쳐야 한다. classify_run은 전송을 해석한 의미 값을 canonical 검사와 원 schema로 검증한다. 선택 필드 부재/null/값과 원 제약은 유지한다. Claude는 직접 JSON을, control_binding은 별도 중앙 제출 계약을 유지한다. 코드 정의를 자연어의 별도 schema로 복제하지 않는다.

phase 007은 제품 runtime을 고정하고 같은 경계를 소비하는 시험 fixture와 실제 분기 검증을 한 task가 수리한다. 원 schema와 CLI 전송 schema를 구별하고, pair가 저장 가능한 실패만 검사하면서 성공 표본을 잃는 문제를 닫는다. 외부 CLI/Job 대역은 현 계약을 따르며 실제 runner·collector·수신/저장기를 가리지 않는다. provides/uses는 빈 목록이고 독립 task 간 새 인터페이스를 배정하지 않으므로 S 항목을 추가하지 않는다. 이번 공통 설명 갱신은 이미 구현된 정본과 후속 검증 책임의 반영이며 제품 계약 개정이 아니다.

corpus 생성의 정본은 `.agents/diff/_rules.json`, `writing-skills/scripts/build_skill_mirrors.py`의 transform/build_target과 `writing-skills/references/멀티런타임_동기화.md`다. phase 004의 verbatim과005의 하위 manifest -text를 유지한다.007은 새 녹화를 만들지 않고 기존 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 및 미러 생성 일치를 확인한다.

제품 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. report 형식은 서비스 protocol.md가 직접 규정한다. 후속 phase에서 외부 제공자/소비자를 분리 배정하려면 manager가 먼저 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 공유 검사와 실제 연결 책임을 해당 S 항목에 정한다. 같은 인터페이스는 같은 S ID를 유지하며 제품 내부 선택을 불필요한 seam으로 승격하지 않는다.
