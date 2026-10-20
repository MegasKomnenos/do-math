# manager 0064 판단

g4-general의 유효한 두 시험 수리와 최종 실패 증거를 부분 수용했다. 정본 flows/test_submission_ingress_owner.py·test_engine_cli_conditional_journey.py와 공식미러 2개를 workspaces.py integrate로 충돌 없이 반영했다. report.status=partial은 보존한다. check.py report PASS와 integration의 실제4경로/제출 SHA를 확인했으며 제품 runtime 변경은 없다. G4는 미충족이다.

첫 수리는 확장 가족의 잘못된 생산자 검사 0회 기대를 현재 helper의 실제 호출 의무로 바꾼 것이다. OwnerIngressAssertions.reject_and_replay는 malformed 입력마다 실제 submission.producer_check의 정확 이슈를 단언한 뒤 중앙 수신/원내용 저장/소비1회/재전달을 확인한다. 현재 시험은 가족 수×item_shapes 수=15회와 전 호출의 helper caller를 각각 대조한다. 중앙 반려와 마지막 정상 수락을 보존한다. 둘째 수리는 scheduled_operator.execute가 기동 때 operator/startup.json을 게시하고 반환에 startup을 더하는 계약을 반영했다. run_engine의 latest-engine.json은 동작 결과이며, 두 파일/반환을 각각 전체 값으로 대조한다. 필드를 무시하는 부분집합 비교가 아니다.

원 focused1은1passed/exit0·공식18.6초, focused2는1passed/exit0·공식10.2초다. focused1의912PythonSHA 중 후속 CLI시험1파일은 제출판과 다르므로 별도 판본으로 유지한다. 마지막 full4의 912PythonSHA는 제출판과 전건 일치하고 changed_during_run=[]다. selected4288=중복·누락·여분 없는 실제4288행, counts는4262passed/14failed/9error/1skipped/2not_run, 별도fixture error1, complete=true/successful=false·관측exit1이다. complete는 보고 완결이며 성공이 아니다. 두 수리 ID는 이 full4에서도 모두 passed다. 공식4892.8초/외부4897.672초·소프트초과740행을 보존하며 시간만으로 기능 실패를 판정하지 않는다.

manager는 원 full4 report와 byte 사본 SHA, selected/실제 row/fixture counts, 직접 수정4파일 diff·미러2쌍, 현재 provider/operator 정의, 불변912Python 및 실행 시작 트리2410파일과 제출판 일치를 직접 대조했다. 실행 중 변한 비용캐시는 원자료에 보존 후 base복원됐다. task의 공식 mirror-submitted check는1375파일 드리프트 없음/exit0이며 파일 수는 do-math 트리와 다르다. manager 제품시험은0회다. 독립 계산은 verify_result.py·verification-review.json, 통합 후 현재 bytes는 integration-check.json에 있다. 과거 full1의 ceiling 누락 교정과 full2/full3의 수리 전 명시중단은 task 원자료에 보존하며 전체 성공으로 합산하지 않는다.

남은 실패는 정확한 full4/failures와 현재 소스에 연결해 두 작업으로 배정한다. 최종 원인과 수리는 해당 task가 직접 확인한다.

- g4-contracts: 측정/환경 skip 외18개 failed/error 행. 폐기 history/parent_execution_id·conversation_id fixture, 운영 처분 지급 input_bundle, 반복 판본 좌표, HOLD startup, 복구 후 활동 ready 기대를 실제 계약과 함께 수리한다. 같은 묶음에서 단언 helper6발견의 정의/소비자, 문서 함수 표기 두 곳/동일 원인3행, status.tasks[].waits의 비빈 응답 경계, provider 이행 원장의 옛 new_ids를 정리한다. 대규모 저장 helper 본문이 불변인 단순 이름/연결 수리는 정적 판정과 필요한 구조 확인으로 충분한지 판단한다. 전가족 재입증을 요구하지 않는다.
- g4-measurement: adapter meta의3failed/2error/2not_run와 fixture error1. 현재 repository_root는 git rev-parse, write_index는 HEAD를 요구하지만 서비스 사본에는 Git 메타데이터가 없다. 우선 자기 사본의 독립 Git 기준판을 준비해 기존 meta 시험을 실행한다. 이 환경 준비가 아직 입증된 성공은 아니다. 준비 뒤 실제 코드 결함이 남으면 관련 측정 구현/직접 소비자/최소 확인을 같은 task에서 수행한다.

Git 경계는 수단의 필요성을 먼저 재검토했다. 공용 C:/math를 자기 판본으로 쓰거나 ceiling을 해제하지 않는다. Git을 사용하는 측정 계약을 변경해 비Git fallback·가짜 HEAD·새 manifest 체계를 만들기 전에, 자기 workspace에 독립 .git/로컬 기준 commit을 만드는 가역적인 준비를 허용한다. workspaces.py:SKIP/files/snapshot은 .git을 제외함을 확인했다. 이 예외는 g4-measurement에 명시했으며 공용 Git 관리 금지는 유지한다. 자기 기준 commit은 main 판본/통과 증거가 아니므로 실제 실행 bytes SHA와 함께 보존한다. 향후 G4/G5의 준비 방식은 이 결과를 수용한 뒤 구체화한다. 제품의 비Git 지원을 새로운 사용자 요구로 가정하지 않는다.

작은 보완을 별도 문서 task로 더 나누지 않았다. 측정 meta 내부에 jobs2 호출이 있으므로 g4-contracts1슬롯/g4-measurement최대2슬롯으로 총3이하를 맞춘다. 두 task는 측정 runner/support와 fixture/runtime/문서의 쓰기 소유가 겹치지 않으며 g4-general만 실제 선행이다. 별도 시간 장벽·자원 프레임워크·가짜 depends_on을 추가하지 않았다. 기존78정의와 objective, 취소2건은 보존한다. inbox/state에는 실행 중 task가 없었고 배정 변경은 없다. worker 모델 gpt-6.1-sol/high·max_workers10을 유지한다.

unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported는 symlink 부재/생성 OSError를 사유와 함께 skip하는 현행 계약이다. full4의 WinError1314는 그 조건부 skip로 인정하되 passed/실제 outside_symlink 반려로 세지 않는다. 호스트 권한은 바꾸지 않았다. L01·Windows1314 실반려는 여전히 열린다.

사용자 저장 범위 지시/A22를 유지한다. 이번에는 전체 실행에서 관측한 구체적 실패를 고치며 84/84 가족·모든 필드/새reader/옛head를 새 완료 선행으로 되살리지 않는다. 기존 유효한 수리/원증거는 보존한다. 후속 두 결과를 수용한 통합판에서 기본 전체 일반 검사를 다시 완결하고, 그 최종판에 fresh T3와 G6~G8을 연결한다. 지금 G4 재실행을 선게시하지 않는 것은 미확인 수리 결과를 통과로 가정하지 않기 위해서다. G1~G3 최종 근거 연결·G5~G8·실경계와 최종review도 남는다. 상태는 active다.

공용 context/plan/seams와 두 objective를 완성한 후 queue.pending.json을 check.py queue로 검사한다. 검사한 같은 bytes를 queue.json으로 원자 교체하는 것이 이번 manager의 마지막 공용 변경이다. 제품 변경은 task에 맡겼으며 manager가 직접 편집한 것은 공용 기록/계획/배정뿐이다.
