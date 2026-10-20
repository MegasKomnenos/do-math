# mutation-parallel 수용과 개선판 G6 배정

mutation-parallel의 정본6·미러6 총12파일을 공식 integrate로 충돌 없이 통합·수용한다. 실행 개선과 필요한 직접 확인은 완료됐으며 전체 G6는 아직 실행하지 않았다. 새 g6p-run에 개선판의 실제 전체 실행을 배정한다. 기존 g6-run은 사용자 중단·취소·미수용으로 보존한다.

## 판단 근거와 확인 범위

protocol의 manager 절차, 공용 context/plan/seams의 현재 상태·사용자 목적·G1~G8·관련 인터페이스, inbox/queue/state, mutation-parallel·5모듈T3·저장범위·사본정리 지시와 사용자 원결정/문서묶음 지시를 읽었다. inbox.completed는 mutation-parallel/exit0 하나이고 inbox.running 및 확인한 state의 running은0이다. 기존121배정과 objective를 변경하지 않는다.

task objective/report와 evidence/judgment.md·changes.diff·실행 원자료를 대조했다. 공식 restore로 baseline의 정본6경로를 이 manager의 baseline-review에 복원하고 실제 diff를 accepted-diff.txt로 남겼다.12경로의 baseline/공용/결과 SHA와6미러쌍을 확인했으며, 공용은 모두 시작판과 같아 충돌이 없었다. integrate의12경로와 제출목록이 같고 통합 후 bytes도 수용판과 같다. baseline은 검수용 복원이며 과거 task 디렉터리를 바꾸지 않았다.

`mutation.run`의 함수 계획 pool·baseline lock/Future·execute·listing 게시, `_child_run`의 Job 소유·취소·실제exit, main의 native stream capture와 CLI 검사를 읽었다. 한 계획은 child 하나씩 실행하므로 jobs가 변이/정상 합계 상한이고, 정상 선택의 소유 Future만 실제 child를 실행한다. 기존 실패후보 정상 확인·retry·합집합·failfast·정상실패/오류 분류를 유지한다. 취소/예외는 Job terminate와 root/후손 대기를 거치고, 명시 중단 보고는 listing을 바꾸지 않는다. runner의 공통 종료/exit 심볼로 정리했으며 T3 호출부와 시험·설명도 함께 바뀌었다. 명령간 cache·자동 함수재개·별도 서비스는 없다.

초기 공식 보고의 선택41/고유row41/41passed·exit0과 최종 보고의 선택15/고유row15/15passed·exit0·실행중 소스불변을 직접 대조했다. 최종4개 변경 Python SHA는 최종 실행 시작판과 같다. 초기28unit은 최종 native 출력/경계 관측 보완의 영향 밖이라는 작업자 분석을 재사용한다. 최종15는 경계13과 runner 무시간제한/후손대기2이며 초기 경계13과 겹친다. 두 판본을56독립시험으로 합산하지 않는다. 초기 소프트 예산 초과2건은 원보고대로 남긴다.

최종 작은4함수 fixture의 serial/parallel 보고,10개의 실제 spec/result/attempt/output과 본문 timestamp/PID를 대조했다. 각각 killed3/survived1·정상passed1개 공유·독립attempt5개·실제 동시수1/3이고 동일 선택/판정이다. 기존 동등 사유/unrelated 항목은 보존되고 killed 과거 항목은 제거됐다. 보고시간2.9/2.0초는 이 fixture의 관측이며 전체1645함수의 성능이나 완료시간을 예측하지 않는다. 명시중단 원보고4 execution_error·baseline없음·3개 CancelledError attempt·listing3항목 보존과3 Job의 root_signaled/active0/PID공집합을 확인했다.

검수 코드는 verify_result.py, 결과는 verification-review.json이다. manager 제품시험 재실행은0이다. 작업자의 전체미러1384파일/check exit0와 초기unit 재사용 범위를 근거로 사용했으며 전체일반/T3/T4/T5/G6·실공급자·설치·예약을 새로 검증하지 않았다. 이 제한된 근거는 실행 개선을 수용하기에 충분하고 전체 제품 관문을 닫는 근거는 아니다.

## 후속의 목적과 범위

g6p-run은 mutation-parallel을 직접 선행으로 삼는다. g6-inputs/g5-remainder가 그 선행에 포함되므로 별도 문서연결이나 전수준비 장벽이 없다. 기존 g6-run population의123모듈/1677함수·20묶음·4515시험 원색인을 재사용한다. 원색인 SHA와20묶음이 존재함을 직접 확인했다. g5-remainder의 추가15고유ID는 중단판 population에 이미 반영돼 있다. execution-arguments.json은 기존 --base/--every/--only/--test를 모두 유지하고 --jobs 3과 새 C:/g6p-g6p-run/b01..b20 출력만 적용한다. 실행자가 새 경로 충돌/현재delta·자기Git ancestry를 확인한다. 함수 수는 quota가 아니다.

20명령은 하나씩 실행하고 명령 내부 변이·정상 child 합계3개로 총시험3슬롯을 배정한다. 다른 시험 명령을 동시에 실행하지 않으며 일반 확인은 명령 종료 뒤 정확 ID/jobs1로 수행한다. 한 작업자가 listing·공유시험/helper 수리·최종미러를 소유한다. 같은 정상 선택의 공유는 명령 안에만 유효하다. 중단 뒤 새 output에서 미완료 묶음을 실행하며, 원자료가 있는 output을 비우지 않는다. 이전 b01에는 최종보고가 없으므로 성공/포착으로 쓰지 않는다. 다른 완결batch 재사용은 source/선택/정상/exit 유효성을 판단한다.

manager0100이 확인한 `references/과제-착수조건.md:89`의 callable 표기 실패를 g6p-run의 실행 준비에 묶었다. 기존 doc_code 계약에 맞게 문서/미러를 고치고 정확한 ReportProjections 정상시험을 확인한다. 함수 존재와 원실패는0100 근거를 재사용하며 이를 새 runtime 결함이나 저장 전가족 누락으로 확대하지 않는다. 실제 G6에서 발견하는 관련 수리·필요 확인·설명·미러도 같은 작업이다. 현재 새로 확인한 독립 기능 결함이 없어 별도 조사 task는 추가하지 않는다. G1~G3 최종연결은 실제 G6 변화와 결과를 소비해야 하며 G6의 선행이 아니다.

저장 A22 지시는 충분한 공통 보장의 재사용과 구체적 문서 실패의 최소 수리에 적용했다. 가족별quota·반복실호출·새 장기감사를 추가하지 않는다. 최신5모듈 관련 추가T3만 허용하고 전체T3 반복은 배정하지 않는다. 기존 G4/전체T3와 부분판본, G5 환경6arc/10행·전체index/자동store제약, G1~G3 최종연결·남은G7/G8·L01/공급자 조건은 미해결로 유지한다. 개선만으로 전체목표를 완료하지 않는다.

## 게시

공용 context/plan/seams에 현재 구현·후속 사용 계약과 판단 한계를 먼저 갱신한다. 기존0100 현재 안내는 당시 이력으로 표시하고 중복 빈 줄만 정리해 본문 의미와 과거 근거를 유지한다. 새 objective·입력·20argv·handoff를 완성한 뒤 queue.pending.json을 만든다. 후보는122정의·accepted116·취소5·미해결g6p-run1·active다. 기존121정의/objective는 불변이다.

공식 `check.py queue RECORDS QUEUE_PENDING_FILE`의 결과와 후보 SHA를 queue-check.json에 기록한다. 검사를 통과한 동일 후보를 queue.json으로 원자 교체하는 것이 마지막 공용 변경이다. 수용된 mutation-parallel의 workspace 정리는 manager 종료 뒤 실행기에 맡긴다. 미수용 g6-run·원b01·기존 연구와 graphify는 유지한다.
