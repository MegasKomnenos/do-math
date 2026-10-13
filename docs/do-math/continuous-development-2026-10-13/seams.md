# 현재 경계 계약의 사용

phase 001의 독립 분석, phase 002 변이 정상 기준 수리와 phase 003 공급자 smoke 작업은 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring, 공급자 호출은 기존 contracts.action_schema·ModelRunner.run·real_ports·adapter/parser가 정본이다. phase 003의 부분 성공과 두 실패는 context C12에 있다.

phase 004의 단일 task는 `.agents/diff/_rules.json`과 `writing-skills/scripts/build_skill_mirrors.py`의 기존 transform/build_target을 사용해 corpus 원자료의 축자 생성을 수리한다. 입력은 정본 파일 바이트와 기존 규칙, 결과는 생성 미러이며 의미는 `writing-skills/references/멀티런타임_동기화.md`와 실제 코드로 확인한다. 한 task가 규칙과 생성 결과·양쪽 소비를 검증하므로 새 독립 인터페이스나 분리된 제공자/소비자를 만들지 않는다. provides/uses는 빈 목록이고 새 S 항목은 없다. report의 형식은 서비스 protocol.md가 직접 규정한다.

제품의 기존 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. 자연어로 새 인터페이스 사본을 만들지 않는다.

후속 phase에서 외부 제공자/소비자를 분리 배정할 필요가 생기면 manager가 먼저 해당 S 항목을 만든다. 실제 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 제공자/소비자, 공유 검사와 실제 연결 검증 책임을 기록한다. 같은 인터페이스는 같은 S ID로 개정하고 근거 참조를 끊지 않는다. 제품 내부 구현 선택을 불필요한 seam으로 승격하지 않는다.
