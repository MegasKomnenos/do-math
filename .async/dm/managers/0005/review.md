# r02-fix 검수와 R04 후속 배정

r02-fix의 F1 수리를 수용한다. 실제 base/workspace diff와 task의 diff가 같고, 보고된 여섯 변경 경로가 허용 범위 안이다. 비캐시는 정본 시험 두 파일과 미러 두 파일이며 두 비용 캐시의 변화는 contracts.test_pairs 항목뿐이다. 공용소스가 task base와 일치한 상태에서 workspaces.py integrate가 여섯 파일을 충돌 없이 반영했다. integration.json과 source-review.json이 근거다.

## 확인한 결과와 한계

worker_request_run은 research_work AI 프로필을 명시적으로 고르고 dispatched ticket·prompt seal을 전달한다. host 제한이 있는 경우 기존 host_capacity_fixture와 resume 전 on_started 게시를 사용한다. 실제 ModelRunner가 저장한 request.json과 adapter의 snapshot을 읽고 기존 ProviderJobs가 실제 두 worker.run을 실행한다. 대역은 Job·CLI spawn 경계에 있다. Pair.samples의 반환은 직접 재조립한 요청이 아니다.

두 공급자의 각20 유효 입력, 정확 identity/profile_ref·limits·control·schema 의미·scholarly 인자·lock을 단언한다. 서로 다른 lock 프로필의 참조는 각 자기 profile에 먼저 대조하고 서로 다름도 확인한다. 이후 전송효과 비교에서만 profile_ref와 실행별 evidence 경로를 제외하며 workspace/control/tools는 유지한다. Codex argv/stdin 무효과와 Claude True의 정확 제한, scholarly args 0/1/여럿이 실제 worker CLI까지 연결된다. 기존 필수+선택 역방향과 결과8표본의 단언은 유지됐다. runtime 변경은 없다.

원 red 보고는 두 공급자에서 saved prompt 부재가 드러난 하나의 failed 시험 row다. 최종 공식 보고와 하위 결과의 선택6ID·고유6row·passed6이 일치하며 complete/successful은 true, fixture 오류·실행 중 소스 변경은 없다. task가 기록한 종료값은0이다. 최종 보고의 Python875개 SHA가 제출 workspace와 전부 일치하고 변경 시험/캐시3쌍의 미러 바이트도 같다. 전체 미러 생성/검사 성공은 task 기록을 재사용하고 관리 마감의 읽기 전용 --check로 통합판을 확인한다. manager의 새 제품 시험은0이다. 세부는 source-review.json이다.

최종 관련 모듈9.8초와 네 ID의0.2초 소프트 기준 초과는 실제 경로를 연결하는 비용으로 보고한다. 이를 속도 개선으로 해석하지 않는다. 40입력은 여섯 공식 row 안의 조합이며 40개 공식 시험으로 합산하지 않는다. 실제 외부 모델·Windows Job·학술 서버 성공을 입증한 것도 아니다.

R02/1-A 요청 가족의 F1은 해결됐고 F2는 최종 판본 실행 대기다. K-78 요청 slice와 PR18의 해당 필드/lock 성질만 유지한다. 다른 요청·저장 가족, 전체 K/P2, G4~G8, 029 설치/prompt 판본 한계, L01 Q1/Q2·UTF-8 byte 미충족, Windows1314 symlink 실제 반려 미검사는 남는다.

## 후속 선택

기존 R04는 조건 enum·반복 한도 다섯 키의 소비·러너 영수증 JSON 연결의 좁은 질문이다. 현재 pairs와 저장 필드/반복 hold 시험을 함께 읽어 충분한 성질은 유지하고 확인된 시험 공백은 같은 task에서 수리하게 한다. 관련 PR18 slice도 같은 정의/소비자에 한정해 처리한다. 결과8표본은 재사용하며 R05/R06의 전체 값/null 모집단을 추가하지 않는다. 이 배정은 새 사용자 기능을 임의로 만드는 것이 아니라 남은 원래 1-A 의무를 마치는 작업이다.

r04는 수용한 r02-fix의 pairs와 단언을 이어받으므로 이것만 선행으로 둔다. 쓰기는 pairs·test_pairs·test_storage_fields·test_repetition_hold_contract 및 각 미러로 닫는다. r07-fix·r18-fix와 의미 있는 변경 경로가 겹치지 않으며 두 실행 중 배정은 유지한다. 공식 비용 캐시는 자기 evidence 보존 뒤 base로 복원한다. 현재 runtime 결함은 확인하지 않았으므로 범위 밖 결함은 정확 입력·위치·영향을 보고하게 한다.

context·plan·seams와 objective를 먼저 완성하고 임시 queue에 accepted r02-fix와 새 r04를 추가한다. 원래 여섯 task 정의를 보존하고 check.py queue를 통과한 파일을 마지막으로 queue.json에 원자 교체한다. 상태는 active다. 이 inbox 이후 다른 worker의 완료 사건은 다음 manager가 처리한다.
