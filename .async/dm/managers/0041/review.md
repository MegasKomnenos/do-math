# manager 0041 결과 판정

keep-inputs를 수용한다. check.py report가 PASS/exit0이며 실제 변경과 원보고를 검수한 뒤 workspaces.py integrate로 정본8·미러8을 충돌 없이 통합했다. source-review.json은 16파일의 base/제출/통합 전 공용 SHA, 8미러쌍, 63심볼의 실제 AST와 파일 SHA, 비용캐시 own base 복원 및 runtime Python248파일 불변을 확인한다. manager의 제품 수정은 integrate를 통해서만 했고 제품 시험 재실행은 없다.

read_fixture_context는 top-level source_ref에 path가 없어도 실제 context_store.read_source를 호출해 정확한 반려를 받는다. 종전에는 path 존재 조건 때문에 참조를 건너뛰었다. PurposeAnswers의 goal_audit는 links와 identity_assessments가 모두 있고 평가 ID 집합이 지급된 link.assessment_id 집합과 같으며 모두 match일 때만 답한다. 빈 목록이나 무관한 match 평가를 허용하던 공백을 고쳤다. 유효한 현재성/형식 근거 선택은 제품 usable_links에 남고 대역이 재구현하지 않는다. 두 결함은 시험 helper의 공백이며 실제 runtime producer가 잘못된 입력을 생산했다는 주장은 아니다.

직접 시험은 원문 bytes/해시/길이/중첩 pointer와 task 결과·검토·두 이력, 구조계약·빈 보고·선택된 모델 평가·원문 전체·명시 관점·지급 grant/profile을 확인한다. 실제 ModelDouble을 통한 개정 봉인 반려와 호출별 Answer/정확 receipt·returncode 처리를 보완했다. PublicGitFlow는 설치 schema bytes와 immutable input bundle/issued schema, 실제 receiver input_hashes를 연결한다. 모델 대역에 별도 schema 검사를 추가하지 않았다. 기존 실제 동시 입장·owner 순차 저장·서로 다른 workspace와 source SHA/계약 비상속, read-tool의 held/reached 성질은 현재 정의·과거 지정 row 범위에서 재사용했다.

verification-review.json은 원보고12개의 SHA와 선택/고유 row·counts·기록된 해당 row를 대조한다. red-inputs는2failed, related-final은28선택/28고유 passed·complete/successful=true다. 최종889 Python SHA는 제출판과 전부 같고 fixture_counts/changed_during_run은 비었다. exit1/0은 task의 관측값이며 manager가 프로세스를 재실행한 값이 아니다. 최종50.2초와 소프트초과3건은 실제 context 준비·봉인/저장 검사를 보존한 비용으로 남긴다. B129 전체3988passed/1failed/1skipped, pythonw related-before의19passed/2fixture error 및 별도 교정2passed, 부재한 B36 Temp5개를 구별한다. 서로 다른 판본을 최종 통합판 전체 성공으로 합산하지 않는다.

K-27/29/30/31/32/46/48/49의 배정 범위는 충족·최종 통합판 증거 대기로 옮긴다. 전체 G2/G3·다른 K/P2·G4~G8·L01 및 Windows1314와 최종 review는 남는다.

inbox.running의 keep-storage/keep-evidence 배정과 시작 spec은 유지한다. 새 keep-contracts는 KEEP-TEST-CONTRACT의 여섯 K를 같은 시험 규칙·정본 소비 경계로 묶어 필요한 수리와 최소 확인까지 맡는다. keep-inputs의 fixture/시험, structure-finish의 반려 단언, keep-isolation의 지침을 직접 소비하므로 그 세 결과만 선행이다. 진행 중 저장·합성 증거 파일은 읽기 전용이며 비용캐시 외 writes는 겹치지 않는다. 각 공식 jobs1·동시시험worker3 이하를 유지한다. KEEP-REGRESSION-PROOF의 네 질문은 별도 남김이다.

공용 context/plan/seams와 새 objective를 먼저 완성하고 queue.pending.json을 검사한다. assignment-review.json에 기존 정의 보존과 독립 범위 확인을 남긴 뒤 검사한 pending 파일을 queue.json으로 원자 교체해 이번 공용 변경을 마친다. 이 세션 도중 발생한 다른 완료 사건은 다음 inbox에서 처리한다.
