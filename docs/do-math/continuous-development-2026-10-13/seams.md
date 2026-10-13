# 현재 경계 계약의 사용

phase 001의 독립 분석과 phase 002~007의 work는 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring이 정본이다. 공급자 호출의 의미는 contracts.action_schema·ModelRunner.run·model_call.classify_run·real_ports·adapter/parser가 정의한다. 현재 결과와 남김은 context C11/C12에 있다.

phase 006의 비결박 경로는 중앙 제출 control_binding 없이 CLI 최종 응답을 직접 받는 ModelRunner 호출이다. 이 Codex 전송의 정본은 do_math/provider_final.py의 output_contract·semantic_output이다. ModelRunner가 원 schema를 output.schema.json에 보존하고 전송 schema를 transport.schema.json으로 넘긴다. source_request·worker snapshot/hash·native final과 종료는 기존 수집 경계를 거쳐야 한다. classify_run은 전송을 해석한 의미 값을 canonical 검사와 원 schema로 검증한다. 선택 필드 부재/null/값과 원 제약은 유지한다. Claude는 직접 JSON을, control_binding은 별도 중앙 제출 계약을 유지한다. 코드 정의를 자연어의 별도 schema로 복제하지 않는다.

phase 007은 같은 경계의 fixture와 pair를 수리했고 manager가 지정 회귀를 검수했다. 제품 runtime은 불변이다. phase 008은 기존 _context 반환의 operational_evidence/recovery_materials를 문서와 실제 반환 검사로 연결한다. 일반 재개 restore_continuation과 동일한 필드명을 사용하더라도 다른 생산자다. 원자료의 정상/복원 오류/null/부재를 각 실제 객체에서 확인한다. 독립-운영의 설치 경로 설명도 현재 operator_bootstrap.main과 scheduled_operator.main 경계로 교정한다. 제품 계약 개정이나 새 task 사이 인터페이스가 없어 provides/uses는 빈 목록으로 유지하며 S 항목을 추가하지 않는다.

corpus 생성의 정본은 `.agents/diff/_rules.json`, `writing-skills/scripts/build_skill_mirrors.py`의 transform/build_target과 `writing-skills/references/멀티런타임_동기화.md`다. phase 004의 verbatim과005의 하위 manifest -text를 유지한다.007은 새 녹화 없이 기존 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 및 미러 생성 일치를 확인했다. 008도 corpus를 수정하지 않으며 허용된 문서·시험 사본만 공식 생성한다.

제품 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. report 형식은 서비스 protocol.md가 직접 규정한다. 후속 phase에서 외부 제공자/소비자를 분리 배정하려면 manager가 먼저 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 공유 검사와 실제 연결 책임을 해당 S 항목에 정한다. 같은 인터페이스는 같은 S ID를 유지하며 제품 내부 선택을 불필요한 seam으로 승격하지 않는다.
