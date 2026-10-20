# 실행기 격리가 프로세스 소유와 실제 종료 결과를 보존하게 한다

사용자는 시험 보고로 실제 작업자와 그 자식의 종료 여부를 판단할 수 있어야 한다. KEEP-ISOLATION의 K-10/11/24/28/61/66을 현행 실행기·Windows Job·직접 시험에 대응하고, 충분한 기존 근거를 재사용하며 확인된 공백의 수리와 필요한 확인을 함께 마친다. keep-runner의 수용된 선택·결과 보고 13개 K 성질을 보존한다. 전체 OS/Lean/공급자 시험이나 새 실행 제한 체계를 만드는 작업이 아니다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원자료 C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json의 KEEP-ISOLATION과 requirement-state.json의 지정 K, prior-review-state.json의 직접 관련 PR01/PR02 slice를 읽는다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md의 원문과 단계-전환표 preservation, 현재 migration/dispositions/runner.json·kernel.knowledge.json을 대조한다. 과거 local_job_runner·timeout 수단은 최신 사용자 지시와 현재 정의로 판정한다. 시간 경과에 따른 시험/작업자 강제종료를 재도입하지 않는다.

## 판정할 유한 질문

1. K-10/11: test_categories.isolation_for와 run_tests의 클래스 묶음→_isolated→_worker→wait_for_worker/_empty/_exit_code 연결에서 lean/resource의 실제 귀속, 클래스/메서드 표지, scratch TMP/TEMP/TMPDIR, stdout/stderr·progress의 보존, 원 native exit와 보고를 합치는 의미를 확인한다. root만 종료하고 소유 자식이 남았을 때 완료로 세지 않으며 실제 오류/사용자 중단의 미완료 시험은 not_run으로 남는지 본다. complete와 successful, 준비 skip과 worker 오류를 구별하고 마지막 선택/실제 row도 확인한다. 제품 Lean의 계산 계약과 시험 예산·시나리오 관측 상한을 구별한다.
2. K-28: 역사 local_job_runner의 시작 보고1회·정확 소유·활성 자식 잔류 반려가 현행 어디에서 제공되는지 현재 WindowsJob/실제 경계시험으로 판정한다. 옛 '10초'를 복원하지 않는다. 바깥 공식 resource Job과 제품이 생성하는 안쪽 Job의 현재 책임이 다르면 그 차이와 이유를 명시한다. 내포 자체를 결함이나 필수라고 미리 정하지 않는다. 실제 OS 성질을 확인할 때는 제품 WindowsJob을 대역으로 지우지 않고 이미 충분한 원보고·현행 불변성을 우선 사용한다.
3. K-24/61/66: 해당 격리 경계의 자식이 필요한 이유와 분류를 r18의 boundary-map/현행 직접시험에 연결한다. 프로세스·셸 종료·Job/소유·시동이 대상일 때 실제 자식을 쓰고 순수/인프로세스 동작에 불필요한 실환경을 요구하지 않는 성질을 확인한다. Lean 명령은 provider_inputs.actual_command와 설치 시험의 실제 환경 변수 소비를 따라가며 snapshot에 도구가 없는 사실을 제품 실패로 세지 않는다. 실Lean 표지와 실제 프로세스/자원 표지, 주 작업트리 toolchain의 읽기전용 경로 규칙을 현재 지침에 연결한다. 전 제품 자식 호출을 새로 전수 감사하거나 도구 설치를 바꾸지 않는다.

각 K ID별 실제 정의·정확 단언·원보고/판본·현재 충족 또는 구체적 남김을 남긴다. keep-runner의 단위 입력 wait/label 성공은 실 OS 실행 증거가 아니다. 기존 boundary.test_runner_native_exit는 실제 worker가 successful JSON 뒤 native exit7로 끝나는 표본이며 이 종류의 직접 근거와 합성 Job 상태 시험을 구별한다. 직접 관련 과거 변경은 실제 diff·현재 소비자·원보고로 판단하고 임시 원보고가 없으면 부재를 그대로 적는다.

## 범위와 최소 검증

수리는 task.json의 run_tests/test_categories/windows_job, runner 직접 시험·필요 helper, 지정 Job/Lean 경계시험·시험 지침과 미러 안에서 한다. core/lifecycle/knowledge/operator와 sim/engine_purpose helper, branch_gate/selection/mutation/t3_store는 읽기만 한다. 별도 registry나 중복 Job 추상화를 만들지 않는다. 관련 scope 밖 결함은 파일·입력·관측·필요 변경으로 인계한다. 실행 중/미수용 r44-fix·r49-startup 또는 keep-templates 결과를 소비하지 않는다.

정적 확인으로 충분하면 제품 실행 없이 마친다. 추가 실행이 필요한 경우 공식 run_tests.py --jobs 1의 최소 ID를 사용한다. 실제 프로세스 증거가 필요한 지정 질문은 소유한 폐기용 Python 자식/Job만 사용하고 검사 대상이 아닌 공급자·Lean·예약·CPU/메모리 부하 실험으로 확장하지 않는다. 자기 자식의 식별/핸들을 통해 정리하며 기존 worker나 연구 프로세스를 종료하지 않는다. 전체 일반/T3/변이/T4/T5와 외부 모델/실Lean/예약 호출은 하지 않는다. 시간 초과를 성공이나 변이 포착으로 세지 않는다.

selected/실제 row·fixture/초기 실패·exit·source SHA·실행중 변경·소프트 초과와 실경계/대역 경계를 보존한다. 비용 캐시 관측을 evidence에 보존한 뒤 own base로 복원하고 공식 미러 생성/check를 한다. report.json을 check.py report C:/math/.async/dm keep-isolation PASS로 제출한다. 지정6개 K 판정과 G2/G3·G7 전체 완료는 구별한다. 공용 소스/문서/queue/state·engine·Git index·graphify·기존 연구 운전은 수정하지 않는다.
