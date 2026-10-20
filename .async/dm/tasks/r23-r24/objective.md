# 목적과 완료할 결과

원래 R23/R24·10-B의 저장/호스트 호출 계수와 안정 idle 비용을 같은 시험·계측 경계에서 판단한다. 실제 제품 경로의 읽기·쓰기·해시·경로 해석·깊은 복사 계수가 선언한 한도 안에 있고, 비용을 줄이는 과정에서 입력·결과·검사를 생략하지 않았는지 확인한다. 충분한 기존 근거는 유지하고 실제 공백의 수리·관련 최소 확인·미러를 한 task에서 끝낸다. 성능 전수 측정이나 새 비용 관리 체계를 만들지 않는다.

## 입력과 범위

SESSION_JSON의 workspace와 inputs/context.md·plan.md·seams.md 및 task.json을 따른다. C:/math 공용 소스와 다른 task 기록은 읽기 전용이다. depends_on=[]이며 r09/r14-fix/r06/r12-r13-fix의 종료나 중간 결과가 필요하지 않다. 자기 시작판에서 판단하고 직접 소비한 runtime 심볼의 SHA를 남긴다.

원문은 C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의 10-B 및 A-18/B-03/B-27/D-08/D-10이다. 같은 실행 전환표와 C:/math/docs/do-math/continuous-development-2026-10-13/phases/001/tasks/closure-map/evidence/{requirement-state,tracking-state,prior-review-state,evidence-catalog}.json에서 R23/R24와 이 비용 성질의 정확 원보고·보존 항목을 읽는다. 모든 K/PR을 전수 검토하지 않는다.

현재 주 소비자는 tests/flows/test_storage_installation_costs.py, sim/test_storage_owner_costs.py, unit/test_storage_cost_counts.py다. storage_obligations.COST_CASES는 모집단과 한도 선언이며 실행 증거가 아니다. support/storage_cost_owner.py, storage_git.py, storage_probes.py의 실제 계측과 provider_probes.ObservedCalls·storage_files.audit_events를 함께 읽는다. runtime의 Repository/GitStateStore, trust_inventory, lifecycle_engine._refresh_readiness와 실제 scheduler idle 경로가 생산/소비 정본이다.

쓰기는 세 시험과 전용 비용 helper·미러, 실제 재현한 해당 비용/내용 결함에 한정한 repository.py/git_store.py/trust_inventory.py/lifecycle_engine.py/setup_lean.py다. 공유 helper storage_git/storage_probes/storage_obligations는 비용 관련 부분만 바꾸고 다른 소비의 의미를 보존한다. 공통 Sim·provider_probes·storage_files·record_builders, core/scheduler/parallel·관찰·제출·schema는 읽기 전용이다. scheduler idle 자체 수리가 필요하면 정확 재현과 필요한 쓰기를 남기고 독립 범위는 끝낸다.

## 판단과 수리

1. 다섯 사례의 실제 입력·계측 구간·제품 호출·내용 단언을 연결한다. 현재 export의 N=3/64/65/1043, query의 N=3/16/17/200와 새 reader, trust의 N=6/56230 파일, readiness의 N=2/100, idle k=1/10은 원문과 현행 계약으로 판단한다. 56230개 소형 fixture는 원문의 파일 수 축이며 8.55GB 실내용 재생이 아니다. 비용을 이유로 축·경계·입력량을 줄이지 않는다.
2. export의 ceil(N/64)+2 Git 연산·파일쓰기 N, byte batch 경계/큰 단일 파일, query의 일치/불일치·페이지·해시/읽기 계수, trust의 파일당 실제 읽기/해시와 구조 검사 open/hash/resolve 0, readiness의 전체 상태 deepcopy 0·평가 결과 N을 실제 호출과 독립 기대값에 대응한다. 계측이 결과를 바꾸거나 호출을 우회하지 않는지 확인한다. 숫자만 맞고 파일·JSON·해시·순서·원 입력 내용이 누락되는 시험을 수리한다.
3. idle은 공개 watch의 초기 정착 뒤 k번 안정 구간에 새 commit이 0인지, head/queue/executions/Job 착수가 유지되는지, 뒤 공개 pause가 실제 반환과 저장을 만드는지 확인한다. 준비 중/실행 중 정상 점유나 필요한 종료 정산을 idle로 오인해 제거하지 않는다. r11/r14의 다른 종료·진행성 증거는 비용 의무의 대체물이 아니다.
4. 과거 최적화가 현재 실행 경로와 검사를 보존했는지 해당 diff·정확 단언·원보고를 대조한다. 없는 Temp 보고의 수치를 성공에 더하지 않는다. 검사가 충분하면 코드를 바꾸지 않고 그 이유를 기록한다. 공백이 있으면 기존 시험/helper에서 관련 정상 대조와 반례를 보완한다. 실제 runtime 결함은 허용된 해당 생산/소비 파일에서 필요한 최소 수리와 검증까지 처리한다. 숫자 한도 상향이나 결과 생략으로 통과시키지 않는다.

## 최소 확인과 보고

정적으로 충분한 성질을 재실행하지 않는다. 새 수리의 실제 동작은 공식 run_tests.py --jobs 1의 가장 작은 직접 소비 선택으로 확인한다. 공용 계측 helper 변경이 다른 직접 소비를 바꾸면 필요한 대표만 포함한다. 56230파일 전체 실행은 해당 불확실성 해소에 실제 필요할 때만 수행하며 이미 충분한 원보고/코드 근거 대신 관례적으로 반복하지 않는다. 벽시계 시간은 소프트 기준이고 계수 한도와 구별한다.

소스 고정·선택/실제 row·exit·판본·원 실패/최종 결과를 보존한다. 공식 build_skill_mirrors.py --target .agents 및 --check로 미러를 맞추고 비용 캐시는 evidence 보존 뒤 base로 복원한다. report에는 각 원문 사례의 실제 경계·계측/내용 증거·유지/수리/미확인·최종 판본 대기를 연결한다. R21/R22 크기, 전체 G4~G8·PR/K/P2, L01·Windows1314는 종결하지 않는다. check.py report C:/math/.async/dm r23-r24로 형식을 확인한다. 공용 문서/queue/state·다른 task·base/inputs·engine·Git index·graphify를 수정하지 않는다.
