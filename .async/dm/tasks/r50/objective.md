# 운영자 기동 판본과 수리 보고의 실제 근거

사용자가 설치 판본이 다른 실행을 알아볼 수 있고 운영 AI의 수리 결과를 실제 판본·커밋 근거에 연결할 수 있게 한다. R50/12-A 중 독립 owner인 운영자/동결 설치/수리 보고는 조사·필요 구현·직접 검증을 이 task에서 마친다. 엔진 기동 경로는 고정 사본에서 읽고, core/engine 쪽에 필요한 정확한 변경만 후속 r49-startup에 넘긴다. r41이 이 파일을 수정 중이므로 그 결과를 읽거나 배정을 바꾸지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md와 requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json의 R50, requirement-state.json의 12-A와 직접 연결된 보존/P2 ID가 원문이다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md 12-A 및 단계-전환표의 current_work.operator_population_integration(B52)을 읽는다. 과거 PR 영역과 B52 원 diff/현재 소비/정확 원보고를 연결하되 기존 보고 부재·부분 범위는 보존한다. 원 12-A는 실행기/운영자 기동 경로의 설치본·정본 생성 결과/기록 manifest 해시 불일치 거부 또는 차이 보고와 운영 AI 수리 보고의 판본·커밋 필수 필드를 요구한다. 이름이 비슷한 capability/연구 프로필 판본으로 대신하지 않는다.

다음 유한 질문을 처리한다.

1. 실제 기동 진입점과 호출 연결을 먼저 찾는다. do_math.py/cli.main→ResearchEngine 초기화·설치 manifest, operator_bootstrap.main/freeze/verify_snapshot→scheduled_operator.main/check/run_engine/recovery, 실제 scheduler의 명령 생산을 구별한다. 일반 연구 실행기/운영자와 외부 공급자 CLI worker를 이름만으로 같은 모집단에 넣지 않는다. core의 시작 snapshot과 실행 중 _check_installation, 동결 bootstrap의 원 manifest와 live 대상 설치는 서로 무엇을 비교하는지 명시한다. 단순 형식 검사나 --version을 판본 대조로 세지 않는다.
2. 운영자 owner에서 현재 충분한 정상 생산→검사 근거를 유지한다. bootstrap의 bytes/목록/manifest·디렉터리 정체성/mark 캐시·손상과 live/frozen 기동을 현재 계약에 따라 확인한다. 실제 불일치가 정상 기동을 통과하거나 보고에서 사라지는 경로가 있으면 자기 writes 안에서 수리한다. 같은 원천으로 기대 해시와 관측 해시를 재생산하는 자가 확인을 피한다. 필요한 작은 파일 변화와 직접 호출로 확인하며 전체 설치 대형 복사를 불필요하게 반복하지 않는다.
3. supervision.OPERATOR_SCHEMA/repair_report_schema와 scheduled_operator.recovery의 실제 제출·저장·검증·결과 보고를 대조한다. manager가 현재 읽은 OPERATOR_SCHEMA에는 판본·커밋 필드가 없고 repair_report_schema도 이를 추가하지 않는다. 이것이 원문에 대한 공백인지 실제 다른 생산/수신 증거와 확인하고, 공백이면 한 계약을 생산자·프롬프트·수신자·직접 소비 fixture/시험에 적용해 마친다. 현행 설치 해시/봉인 입력/결과를 활용하고 필드 존재만으로 실제 판본 증명을 주장하지 않는다. 사용할 수 없는 Git 원천을 가짜 커밋으로 채우거나 task 사본을 임의 저장소로 만들지 않는다. 실제 source commit과 설치 bytes·미커밋 변화·연구 저장 snapshot의 의미를 구별하고 확인 한계를 보고한다. 기존 repaired/unresolved, 진단 근거/회귀 파일, HOLD·unknown 종료·lock/예약/재시작 책임은 보존한다.
4. 엔진 기동 연결의 남김은 evidence에 실제 경로/심볼·현재 입력과 기대/관측 의미·기존 단언·필요 owner/파일·소스 SHA로 남긴다. 충분하면 완료 근거를 인계하고, 불충분하면 r49-startup이 바로 구현할 수 있는 유한 공백을 인계한다. core_engine.py/engine.py/cli.py 및 r41 소유 파일은 읽기 전용이다. 허용된 운영자 수정과 검증을 마친 뒤 엔진 쪽 결과를 별도 구분한다. 전체 R50이 닫혔다고 주장하지 않는다.

정본 쓰기는 task.json의 operator_bootstrap.py·supervision/preflight/scheduled_operator/repair_execution과 지정 직접 시험/helper·미러다. 공유 이음새/CLI 설명과 엔진 변경은 r49-startup이 함께 마감하며, 필요한 설명을 보고에 정확히 남긴다. API·필드 형식은 이 배정이 미리 설계하지 않는다. 범위 밖으로 임의 확장하거나 진행 중 코드를 소비하지 않는다.

검증은 최소한으로 한다. 기존 증거가 충분하면 소스/단언·원보고의 불변 근거로 판단하고, 수정한 성질만 자기 workspace의 공식 run_tests.py --jobs 1로 확인한다. 실제 제품 경로와 외부 경계 대역을 사용한다. 외부 유료 모델·실Lean/HTTP/OS 예약·전체 일반/T3/변이/T4/T5를 실행하지 않는다. source 고정·선택/실제 row·exit·실패/준비 오류·판본 SHA·소프트 초과와 한계를 보존한다. 이미 충분한 검증을 반복하지 않고 정확성을 줄이거나 하드 timeout을 추가하지 않는다. 공식 mirror 생성/확인을 수행하고 비용 캐시 bytes는 evidence에 남긴 뒤 own base로 복원한다.

report.json에 수용 가능한 구현 결과, 유지한 성질, 정확한 엔진 후속과 미실행 범위를 기록한다. task 완료와 전체 R50/12-A·PR/K/P2 및 최종 G4~G8 완료를 구별한다. check.py report C:/math/.async/dm r50 PASS로 제출한다. 공용소스/다른 task/공용문서·queue·state/engine/Git index/graphify/기존 연구 운전은 수정하지 않는다.
