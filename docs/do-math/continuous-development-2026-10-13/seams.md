# 현재 경계 계약의 사용

phase 001의 독립 분석과 phase 002~005의 work는 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring이 정본이다. 공급자 호출의 원 의미는 기존 contracts.action_schema·ModelRunner.run·model_call.classify_run·real_ports·adapter/parser가 정의한다. 공급자 부분 성공과 phase 004~005의 미러·Git 수리 결과는 context C12에 있다.

phase 006의 한 task가 Codex 전달과 수신을 함께 수리한다. 원 역할 schema의 선택 필드 부재/null/값·검증 의미는 유지한다. 현재 ModelRunner.run의 비결박 경로가 output.schema.json을 CLI에 전달하고 model_call.classify_run이 final을 원 schema로 검사한다. 연구 control_binding 경로는 별도의 중앙 제출 계약을 사용한다. 새 공급자 표현이 필요하면 task가 코드의 한 소유 위치에서 정의하고 실제 전달/수신·원자료·원 schema 검증을 함께 확인한다. 원 schema 약화, native final/worker hash 결속 제거, 연구 제출 경로 변경은 이번 재량이 아니다. 구현 전인 표현을 이미 충족한 새 계약처럼 쓰지 않는다.

하나의 task가 같은 경계의 제공/소비·관련 회귀·실제 Codex 호출·녹화/미러까지 맡으므로 이번에 독립 task 간 새 인터페이스를 배정하지 않는다. provides/uses는 빈 목록이며 S 항목을 추가하지 않는다. report의 형식은 서비스 protocol.md가 직접 규정한다. 최종 모델 호출과 원자료 보존의 상세 완료 조건은 phase 006 objective에 있다.

corpus 생성의 정본은 `.agents/diff/_rules.json`, `writing-skills/scripts/build_skill_mirrors.py`의 transform/build_target과 `writing-skills/references/멀티런타임_동기화.md`다. phase 004의 verbatim과 phase 005의 하위 manifest -text 규칙을 유지한다. 새 녹화 뒤 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 결과를 확인한다.

제품의 기존 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. 자연어로 새 인터페이스 사본을 만들지 않는다.

후속 phase에서 외부 제공자/소비자를 분리 배정할 필요가 생기면 manager가 먼저 해당 S 항목을 만든다. 실제 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 제공자/소비자, 공유 검사와 실제 연결 검증 책임을 기록한다. 같은 인터페이스는 같은 S ID로 개정하고 근거 참조를 끊지 않는다. 제품 내부 구현 선택을 불필요한 seam으로 승격하지 않는다.
