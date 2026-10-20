# manager 0020: null 관계와 저장 크기 부분 결과 수용

이번 inbox의 r06-domain·r06-edges·r22-storage를 검수했다. inbox 시작 당시 실행 중인 r12-r13-fix·r15-r16의 정의와 입력은 유지한다. 이후 완료 사건은 다음 manager가 처리한다.

## 직접 확인과 통합

세 report 검사는 각각 PASS다. inspect_results.py/source-review.json은 baseline/base/workspace의 실제 변경10파일(새 시험 정본5·미러5), 미러 바이트, 캐시 복원, task별 기존 runtime124파일 불변, 공식 원보고/하위 result.json/선택ID·SHA를 대조했다. 변경된 시험5개 전체와 두 null 관계 설명, 저장88가족 표, 현재 실제 생산/소비 코드를 읽었다. workspaces.py integrate는4·4·2파일을 충돌 없이 반영했다. integration-check.json에서 공용 bytes를 다시 대조한다. manager의 제품 시험 재실행은0이다.

세 작업의 시작판 대비 공용 runtime 차이는 수용된 r14-fix의 model_runner/observation_transport/parallel 세 파일뿐이다. 0019의 실제 diff와 현행 _queue_intent_rework/_governance_control, review_cycle.start_review, review_engine._start_identity_review/_build_review_context, delegations._basis, governance._knowledge_import_basis/_owner_basis, payloads encode/seal_large를 읽었다. r14-fix는 관찰 조각/양보/같은 read 합치기를 바꾸며 이번 null 필드·반려 상태·저장 schema와 snapshot 생산 표현을 바꾸지 않는다. r21-r22는 시험/helper 변경으로 runtime 불변이다. 단, task 시험을 통합판 전체 실행으로 확대하지 않는다.

## r06-domain: 부분 수용, 실제 저장 결함과 한정 미결

M1/M2의 제출 실패/repair chain/봉인 read, 검토 pending answer/result와 manifest/restoration, basis의 미존재·현재성 비교를 현재 생산/소비에 연결했다. 실제 read_source caller가 prepare_role_input/submission._payload_issues임도 확인해 기존 caller 미발견 남김을 교정한다. focused-final은 unit1passed·task 관측exit0이고877 Python 해시가 제출판 해당 경로와 같다. 이후 sim1개가 추가됐다. 최초 unit fixture의 accepted receipt 누락은 교정됐다.

F1은 실제 미수리다. prepare_import의 checking/check 부재 상태는 validate_candidate를 통과한다. premature import_approval을 _governance_control이 정확 사유로 반려한 뒤 _reject_governance_import→_queue_intent_rework가 check_execution_id=None을 intent_repair에 넣는다. queue schema는 문자열 ID를 요구하므로 저장 검증이 실패한다. 제출된 sim은 정상 상태의 보존을 요구하는 올바른 실패 회귀이며 skip/expectedFailure/결함 기대값으로 바꾸지 않았다. import-counterexample은1error·task 관측exit1·878 Python SHA 제출판 일치다. 이는 공개 CLI/inbox/restart 전체 실행이 아니라 실제 domain 생산/반려/저장 검증의 재현이다.

이 실패 회귀도 부분 결과로 통합·수용한다. accepted는 F1 해결이나 전체 green을 뜻하지 않는다. r06-finish가 검사가 없는 반려에 불필요한 rework를 만들었는지부터 판단하고 필요한 수리·공개 게시/재시작 확인을 한 번에 맡는다. 문자열 schema를 nullable로 느슨하게 하거나 가짜 check ID를 만들지 않는다. 같은 함수의 source-changed-before-check 경로도 함께 판단한다.

domain M4의117행은 탐색 표현/중복 alias 후보이며117개 실제 null 필드라는 뜻이 아니다. raw 읽기 뒤 bytes/hash, list/dict construction, JSON 진단 전달처럼 이미 설명된 관계를 새 실행 의무로 바꾸지 않는다. 후속은 중복을 합치고 실제 nullable object의 남은 최종 소비만 판정한다. 모든 Python alias의 무한 완결 감사는 요구하지 않는다. unit0.312초·sim11.86초 소프트초과, 실패와 별도 판본은 보존한다.

## r06-edges: 배정 범위 수용

E01~E14는 snapshot의 미관측 null과 live 운전 guard, identity-free record/페이지 끝, 미완결 trace/CSV, provider wait/probe, self-check poll/rejected ID, 외부 sent 예외 ledger→실행/활동/restart, formal·OS·도구·예약 소비를 구별한다. snapshot provider_waits=null을 live start_guard에 보내는 실제 caller/API 의무가 없어 예방적 정규화를 추가하지 않은 판단을 수용한다. ordinary OSError의 필드 부재와 unexpected transport exception의 owner present-null도 구별한다. operator_schedule.ps1의 실제 생산은 원128 Python 목록 밖이라는 보완을 유지한다.

focused-1의 unit5passed와 corrected-1의 sim2passed는 별도 판본이다. corrected-1의878 Python SHA가 제출판과 같고, 앞 판본의 유일한 현행 Python 차이는 sim 모듈이다. 두 초기 sim fixture 오류는 교정됐다. 관측exit1/0·최종6.3초·fixture_counts/changed_during_run 없음과 미러 순서 오류를 보존한다. 최초 mirror 생성 중 early check가 실패했고 첫 시험과 겹쳤으므로 그때의 미러 전체 고정을 주장하지 않는다. 교정 mirror build/check 완료 뒤 sim2를 실행했고 최종 두쌍 bytes는 같다. 단일 최종판7passed로 합산하지 않는다. M3/M5·edge M4만 완료이며 R06 전체는 r06-finish로 남는다.

## r22-storage: 부분 수용, snapshot 중복 수리로 연결

StateContract88가족(map33/list9/singleton25/metadata21)을 실제 source-local 생산과 공통 봉투·manifest·큰 문자열 공유에 대응한 한정 판정을 수용한다. 새 academic.record_resolution 시험은 독립 text/artifact와1/10참조·inline/큰 UTF-8/escape를 실제 저장/load/read_record에 연결하며 전체 값/증거hash·원문1벌·사전 상한을 단언한다. final-3은1passed·task 관측exit0·1.0초·877 Python SHA 일치다. 이미 봉인한 artifact 재제출 fixture 오류와 교정 뒤 docstring 변경의 판본을 구별한다. 소프트초과는 실제4 snapshot 저장/복원 비용이며 크기·내용 단언을 축소하지 않았다.

F1은 start_review가 previous_reviews/turns/manifests를 복사하고 엔진이 이전 cycle도 남기는 구조다. 각 판본의 독립 본문 P바이트를 전부 원천으로 세어도 N판본에서 원천 NP 대비 본문 하한은 P*N*(N+1)/2다. 이는 정적 반례이며 새 N회 공개 운전의 측정값은 아니다. F2는 delegation basis, import owner basis와 pending review input이 구조 snapshot을 복제하는 경로다. 큰 문자열 codec만으로 작은 leaf가 많은 M바이트 구조의 K참조 O(KM)을 없애지 못한다. pending review_inputs는 수신/defer 때 제거된다는 한계도 유지한다.

r22-snapshots는 이 구조 복제 묶음의 생산·봉인·현재성·복원·schema와 직접 시험을 같이 맡는다. 기존 immutable source/record 참조로 충분한지 먼저 판단하고 새로운 일반 캐시/저장 체계를 전제하지 않는다. 원천 전문이나 검토 이력을 삭제하거나 revision 수를 제한해 비용을 맞추지 않는다. 모든 가족에5MB를 새로 넣는 작업이 아니다. r12-r13-fix의 실제 공개 위임 생산자와 새 schema가 필요하므로 그 수용 뒤 시작한다.

## 배정과 게시

r06-finish와 r22-snapshots는 r12-r13-fix의 현행 결과를 소비한다. null 수리는 governance_engine/core/context/진단 전송을, 저장 수리는 governance/delegations/review·저장 표현/schema를 소유한다. 같은 공용 제품 설명과 저장 시험의 수정은 저장 task에 둔다. 두 후속 간 의미 쓰기 교집합은0이며 r15-r16의 scheduler/parallel/call/formal 정산 쓰기도 건드리지 않는다. r06의 review alias 읽기는 시작판으로 판단하고 저장 후속이 변경한 해당 소비는 그 후속이 새 표현과 함께 확인한다. 그 사실만으로 둘 사이에 불필요한 종료 의존을 추가하지 않는다.

독립 r19-r20은 원래9-B의 공급자·비공급자 녹화 재생을 같은 manifest/직접 소비 시험 경계로 묶어 즉시 준비한다. 실제 원자료·지원 판본·독립 verdict→현재 parser/소비 연결을 확인하고 가까운 오프라인 공백을 수리한다. 앞003~018의 실제 녹화와 r21-r22의 Lean 규모 근거는 유효 범위만 재사용한다. 없는 native 경계는 합성 자료를 실제 녹화로 바꾸지 않고 필요한 정확 입력으로 남긴다. 새 외부 실호출이나 버전 업그레이드는 이 배정에 없다.

기존 구조44건은 실제 수정하는 가까운 발견만 함께 처리하고 나머지는 소유권 정리 뒤 한 묶음으로 남긴다. 원래 요구/보존/P2, B58/Temp 부재, G4~G8·L01 Q1/Q2/원문UTF-8·Windows1314 실반려 미검사는 종결하지 않는다. 현재 독립 작업이 있어 active를 유지한다. 공용 context/plan/seams와 objective를 먼저 완성하고 기존 배정 불변·쓰기 독립성을 확인한다. 별도 queue.pending.json을 check.py queue로 확인한 뒤 그 파일을 원자 교체해 마지막으로 게시한다.
