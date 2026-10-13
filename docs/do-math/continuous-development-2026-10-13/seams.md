# 현재 경계 계약의 사용

phase 001의 독립 분석과 phase 002~004의 work는 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring, 공급자 호출은 기존 contracts.action_schema·ModelRunner.run·real_ports·adapter/parser가 정본이다. 공급자 부분 성공·미러 치환 수리·Git 속성 남김은 context C12에 있다.

phase 005의 단일 task는 정본 `do-math/scripts/tests/corpus/.gitattributes`의 manifest text 예외와 공식 생성 사본을 고친다. 입력은 현재 corpus 원바이트·Git 속성·기존 verbatim 규칙이며 기대 결과는 manifest·녹화의 SHA 불변과 양쪽 실제 Git clean 경로의 object ID 동등성이다. 생성 경계의 정본은 `.agents/diff/_rules.json`, `writing-skills/scripts/build_skill_mirrors.py`의 transform/build_target과 `writing-skills/references/멀티런타임_동기화.md`다. 한 task가 속성·생성·실제 Git 필터를 확인하며 새 독립 인터페이스나 분리된 제공자/소비자를 만들지 않는다. provides/uses는 빈 목록이고 새 S 항목은 없다. report의 형식은 서비스 protocol.md가 직접 규정한다.

제품의 기존 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. 자연어로 새 인터페이스 사본을 만들지 않는다.

후속 phase에서 외부 제공자/소비자를 분리 배정할 필요가 생기면 manager가 먼저 해당 S 항목을 만든다. 실제 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 제공자/소비자, 공유 검사와 실제 연결 검증 책임을 기록한다. 같은 인터페이스는 같은 S ID로 개정하고 근거 참조를 끊지 않는다. 제품 내부 구현 선택을 불필요한 seam으로 승격하지 않는다.
