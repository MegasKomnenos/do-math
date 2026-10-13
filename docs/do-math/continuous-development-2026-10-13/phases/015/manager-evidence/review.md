# Phase 015 manager 검수

t4-adapter-report의 A1~A3 성과와 A4 fail/partial 판정을 승인한다. report 전문과 완료 조건을 읽고 report 검사를 통과한 뒤 현재2671파일을 task 종료와 대조했다. 시작2667파일은014 inspected의 skills/diff 부분과 같고16변경은 report/writes와 일치한다. 서로 다른 모집단2750/2667을 손실로 혼동하지 않는다. G1~G8 문면은 바꾸지 않았다.

관련 정본/미러 각70고유선택·70passed·exit0, 최종 T4 각295고유선택·283passed/6error/4failed/2skipped·exit1과 각875 Python 판본/전후 해시를 확인했다. 최종 --list는 실제 선택과 같다. 두 T4의60worker 각각에 대해 요청/실행 ID·875소스 시작/종료·artifact SHA와 실제 branch DB를 대조했고 부모 원adapter.data를 coverage로 다시 분석해5모듈의 행/분기/제외/소스SHA/합계를 확인했다. 정본102/142·미러101/142는 각 raw와 일치한다. 두 정보 수치를 같게 만들거나 분기 도달 임계 관문으로 바꾸지 않는다.

run_tests diff와 AdapterMeasurement/validate_publication을 읽었다. 실제 측정/병합을 유지하면서 누락·파손·다른 실행·판본을 반려하고 T3 index/store/gate를 T4에 쓰지 않는다. 시험의 실제 worker/Job과 known body 도달, 보고 자체의 거짓 도달 반례 및 incomplete/exit1 관측이70회귀에 포함된다. _stop의 자기 활성 해제/멱등 처리, T3 설정의 import 전 읽기와 _t3_plan pause 교정은 기존 incremental/parallel 실제 회귀에서 확인됐다. 새로운 runner 판본의 최종 전체 일반/fresh T3/전체 변이는 후속이다. 역사 D5/D6/D9/D11의 지정 slice 유지와 원raw 부재는 task 기록 범위로 인정하며 PR01 전체를 종결하지 않는다.

6개 Lean 오류는 installed_request의 지문/내용 모집단 차이를 현재 trust_inventory.record_errors가 반려한 결과다. 보존된 identity의 측정 없는 최소 재현도 같은 ValueError다. real-job fixture의 ok 추가 필드, writer-lock child의 backend 누락, archive child의 ports/env 부재를 현 원문과 실제 trace에서 확인했다. 이9건은 현 fixture 수리가 필요하며 제품 guard/실제 compiler/Job을 약화하는 근거가 아니다.

두 baseline skip은 과거 scripts 입력 부재이며 비교 성질은 미검사다. assert_baseline_capture는 ordinary·literal entries/opens/import opens/coverage와 명시 marker 차이를 비교하고 두 worker의 실제 union도 확인한다. 현재 root와 다른 경로만으로 과거 판본 자격이 생기지 않는다. 별도016 task가 Git 도입 diff·원문에 결속된 원바이트 트리를 준비하고 후속 연결 task가 실제 비교를 수행하도록 분리했다.

real_git_descendants의 최종 양쪽 trace는 store.publish/update-ref가 stdin을 DuplicateHandle하는 중 WinError6임을 확인했다. 같은 probe가 AttachConsole/FreeConsole 뒤 저장한다는 코드 관측은 인과 확정이 아니며016에 대조 재현을 맡긴다. 첫 bootstrap WinError5의 후속 통과도 transient 원인 확정으로 바꾸지 않는다. F6의 정본 중심 서술은 양쪽 실패라는 원row로 구체화하며 원report는 고치지 않는다.

139재사용 입력·144corpus 경로·host8원자료·도구SHA·index/pseudo는 보존됐다. corpus Git raw/clean, 공식 --check1336·skill-only를 다시 확인했다. 새 실호출이나 제품 시험을 manager가 실행하지 않았다.01512제품 경로는 전체 T4 연결 검수까지 커밋을 보류하되 원task 근거와 제품 raw를 archive에 결정화한다. 관리 인계·선별 근거·기억만 커밋한다.

016 t4-fixture-repair가 유일한 제품 편집/공식 시험/미러/캐시 소유자다. provenance-baseline은 불변 Git 객체/고정 원자료·상대 쓰기 밖 정의만 읽고 자기 evidence를 만들며 시험/제품 import를 하지 않는다. 서로의 미완성 산출물을 읽지 않아 독립적이다. 두 결과 검수 뒤 입력을 실제 소비하는 단일 후속 work에서 양쪽 전체 T4를 확인한다. 기존 L01 외부 결정·문서/의미 질문 및 최종 G4~G6/G8을 유지한다. 공용 문서의 추가/갱신 의미와 보존된 조건은 common-docs.diff로 대조했다.

관리 마감의 첫 staged diff 검사는 context의 EOF 빈 줄 하나로 exit2였다. 내용은 유지하고 빈 줄만 제거했다. 원 실패 수신은 로컬 staged-diff-check.json에 보존하며 공용 diff를 갱신한 뒤 게시된 manager.json을 후보로 handoff를 다시 검사한다. 제품/task 원자료와 manager 판단 JSON은 바뀌지 않는다.
