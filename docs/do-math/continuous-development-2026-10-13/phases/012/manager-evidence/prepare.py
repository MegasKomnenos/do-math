from pathlib import Path
from difflib import unified_diff
import json
import re

REPO=Path('C:/math')
RUN=REPO/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def insert_before(text,heading,paragraph):
    assert text.count(heading)==1
    return text.replace(heading,paragraph+'\n\n'+heading)
before={n:(RUN/n).read_text(encoding='utf-8') for n in ('context.md','plan.md','seams.md')}
context=before['context.md']
context=insert_before(context,'## C3 현재 정본과 이력의 역할','phase 012 lean-smoke는 A1~A4 complete로 검수했다. report 형식 검사 뒤 현재 2658파일과 종료 해시 전건 일치, 시작과011 manager 판본 동일, 허용22변경을 확인했다. 초기 live 두 건의 error1은 역사 실패로 유지한다. 최종 정본/미러 T5 각1passed, 관련 각48passed의 선택·고유row·실제exit0와 각869 Python 및 전후 소스를 대조했다. 실제 Mathlib 대표 컴파일과 정상 full32의존·타입 오류, 각20판정·5Job 종료, 설치 입력 바이트·11094판단파일 메타데이터 불변을 원자료로 확인했다. corpus 각19항목·56파일과 총112경로의 Git raw/clean, 새 원출력71704바이트와 기존18항목 보존을 검산했다. 근거는 run:phases/012/manager-evidence/verification.json·review.md다. 지정 Lean 경계의 완료이며 G 전체나 설치 신뢰 승인은 아니다.')
old=context.split('## C5 병렬 실행과 검증 자원\n\n',1)[1].split('\n\n',1)[0]
new='phase 001~012의 task 세션은 종료됐고012의 Lean 실연쇄를 검수했다.013 scheduler-smoke는 실제 예약 등록·pythonw 발화·해제, 녹화/재생과 미러를 한 task로 맡는다. corpus manifest·시험 전건 구조 검사·생성기·비용 캐시 및 실제 OS 예약 자원을 공유하므로 다른 제품 수정/시험 task를 병행하지 않는다. jobs1·한 묶음씩 실행한다. 자기 evidence/scratch의 새 workspace와 충돌 없는 시험 이름만 사용하며 기존 연구·예약에는 접근하지 않는다. 기존 Lean/host/공급자는 불변 경로의 승인 성질만 재사용한다. 학술·T4 보고·문서/의미 질문은 별도 후속 책임이다.'
context=context.replace(old,new,1)
context=insert_before(context,'## C9 요구별 상태와 과거 검토의 재사용 범위','012 lean-smoke의 gpt-6.1-sol/high 작업을 검수했고013 scheduler-smoke도 같은 설정으로 배정한다. 각 세션의 모델 정책은 C8의 사용자 지정과 같으며 제품 공급자 호출 설정과 구별한다.')
context=insert_before(context,'## C10 문서 결속에서 남은 고정 범위','012에서 B38/8afa57c7의 formal/setup Git 포트 slice를 실제 diff·현재 함수·원보고 selector와 대조했다. 필수 git_backend 전달, backend identity별 memo, None root·미추적 입력·.lake 제외 및 stop/오류 계약을 유지한다. 관련8개 sim과 실제 Lean 경로가 새 근거이며 원보고10개가 현재 없다는 한계를 유지한다. 이 slice의 유지 판단을 승인하지만 PR02 전체와 다른 B38 소비자까지 완료로 올리지 않는다. 근거는 run:phases/012/tasks/lean-smoke/evidence/history-b38.stdout·history-original-reports.json·review.md 및 manager 검수다.')
context=context.replace('외부 결정과 독립적인011 문구 수리는 완료했고012 Lean work를 계속한다.','외부 결정과 독립적인011 문구 수리와012 Lean work는 완료했다.013 예약 work도 이 답변과 독립적으로 진행한다.')
old=context.split('실제 OS예약등록/발화/해제, 학술MCP와 T4별도adapter분기는 후속책임이다.',1)[1].split('\n\n## C12',1)[0]
context=context.replace('실제 OS예약등록/발화/해제, 학술MCP와 T4별도adapter분기는 후속책임이다.'+old,
'''012에서 기존 portable Lean4.32.0/Lake5.0.0/Mathlib v4.32.0의 실제 대표 컴파일과 verifier 정상·타입 오류를 T5로 연결했다. 각 설치의9의존 HEAD와 manifest revision, 실행 파일 SHA 및 입력/신뢰 기록 불변을 확인했다. 정상 선언2개의 정확 서명·빈 공리·full32의존 증거를 원출력에서 재생했고 오류는 exit1/failed/lean rejected와 타입 진단이다. 초기 도우미 오류2건을 성공으로 소급하지 않으며 live-final의79.4초/미러84.4초만 최종 완료 근거다. 대표 컴파일의308.3초/21.2초 차이는 캐시 조건이 다른 관찰이며 코드 최적화나 시간 제한 근거가 아니다. 설치 신뢰 채택·연구 저장/평가를 수행한 것으로 확대하지 않는다. 근거는 run:phases/012/manager-evidence/verification.json·review.md 및 task 원자료다.

실제 OS 예약 등록·발화·해제는013 scheduler-smoke에 배정한다. 현재 PowerShellScheduler/operator_schedule.ps1·scheduled_operator.schedule·operator_bootstrap를 유지하고 시험 소유의 새 workspace/HOLD·충돌 없는 작업 이름으로 실제 pythonw 발화를 관찰한다. 설치 freeze의 JSON 수집과 OS 실행의 새 LastRunTime/LastTaskResult·정확 action을 구별하며 status 또는 start 요청 수락만으로 발화 성공을 세지 않는다. 학술 MCP·T4 별도 adapter 분기·13-C/L01 조건과 G4~G6/G8의 최종 관문은 남는다.012와 기존 성공을 합산해 전체 성공으로 만들지 않는다. 다음 책임은 run:phases/013/tasks/scheduler-smoke/objective.md다.''',1)
context+='''
012 F3의 불변 근거를 검수했다. runtime124·공급자 입력3·host 입력과8원자료의 바이트는 같고 기존 corpus18항목/verdict·100비manifest 경로도 유지됐다. 새 full Lean 녹화와 재생만 추가해 현재 corpus는 각19항목·56파일·320687바이트다. 총112경로의 명시 SHA·Git raw/clean·양쪽 바이트와 공식 --check1314파일을 확인했다. 이전 실호출은 기존 승인 성질과 도구 조건 안에서만 재사용하며 이번에 새 host/공급자 호출은 없다.012의 검수된 제품·시험·지침·미러20경로를 이번 관리 커밋으로 마감하고 비용 캐시2개는 제외한다. 원 task report/evidence와 제품 원바이트는 raw-evidence.zip에 보존하며 선별 원경로와 압축 항목·SHA는 run:phases/012/manager-evidence/preservation.json에 둔다. 압축으로만 추적되는 scratch/중복 snapshot의 원경로와 stage/commit 수신은 로컬 보관으로 정리 시 사라질 수 있다. 압축은 자동 복원 지시가 아니다.013 배정과 공용 문서·기억의 행정 추가는 제품 검증 판본을 바꾸지 않는다.
'''
plan=before['plan.md'].replace('## phase 001~011의 결과와 현재 상태','## phase 001~012의 결과와 현재 상태',1)
plan=plan.replace('최종 전체 관문은 아직 실행하지 않았다. 현재 상태의 근거는', '012의 Lean 실연쇄 A1~A4도 검수했다. 실제 대표 컴파일·verifier 정상/full 증거·타입 오류 및 정본/미러 각1 T5와 각48 회귀가 통과했다. 초기 두 도우미 오류는 역사 실패로 보존하며 설치 신뢰 승인으로 확대하지 않는다. 최종 전체 관문은 아직 실행하지 않았다. 현재 상태의 근거는',1)
a=plan.index('## 다음 phase: 012'); b=plan.index('## 가까운 후속 배정과 선행 관계',a)
plan=plan[:a]+'''## 다음 phase: 013

scheduler-smoke 단일 work를 gpt-6.1-sol/high로 배정한다. 실제 PowerShellScheduler·예약 어댑터·bootstrap을 통해 시험 이름의 등록, pythonw 발화, wake 예약/취소와 해제를 확인하고 현재 T5·실제 녹화/재생에 연결한다. 시험 소유의 새 workspace와 HOLD를 써서 기존 연구나 유료 모델 호출로 이어지지 않게 한다. OS 등록 권한·실제 발화 조건이 없거나 runtime 수리가 필요하면 원자료와 정확한 미충족 조건을 반환한다. 기계 정책·권한·제품 runtime은 이 task가 변경하지 않는다.

corpus manifest·전건 구조 검사·공식 생성기·비용 캐시 및 OS 작업 목록을 공유하므로 한 task가 jobs1로 순차 소유한다. 현재 한정된 경계의 완료에 기여하지 않는 병렬 분석을 추가하지 않는다. 새 seam은 없으며 입력·writes·A·검증은 run:phases/013/phase.json 및 objective다.012 제품20경로는 관련 회귀/미러 검수 뒤 현재 관리 마감에 포함한다.

L01의 Q1/Q2는 외부 결정으로 남는다. 실제 공급자별 운전 host/tool/판본/model/호출 설정과 출력 byte 기준 유지 또는 도구 단위 개정을 확정해야 한다. 이미 상신한 단위 선택의 답변이 없으므로 원문 byte 기준과 미충족을 유지한다.011 문구 수리나012 Lean 성공은 읽기 용량 인증이 아니며013 예약 작업은 이 답변과 독립적이다.

'''+plan[b:]
plan=plan.replace('010~011 제품 단위를 마감하며012에서 Lean/Mathlib 실연쇄를 연결한다. 근거는011 manager-evidence/verification.json·review.md다.', '010~011 제품20경로는011 관리 커밋571d282c로 마감됐다.012에서 Lean/Mathlib 실연쇄를 검수했고 그 제품20경로를 마감하며013 예약 경계로 진행한다. 근거는012 manager-evidence/verification.json·review.md다.',1)
plan=plan.replace('| G7 Lean/예약/학술 |012에서 실제 Lean/Mathlib 컴파일·verifier·녹화/재생을 맡는다. 시험 전용 예약 등록·발화·해제와 학술 list_sources는 각각 후속 실제 경계로 배정한다. | 공유 manifest/캐시·생성기 의존을 순차화한다. Job/pythonw 성공·예약 cmdlet 대역·도구 판본만으로 대신하지 않는다. |','| G7 Lean/예약/학술 |012의 실제 Mathlib·정상/오류·full 녹화/재생을 검수해 지정 Lean 범위를 닫았다.013은 시험 이름의 실제 예약 등록·pythonw 발화·해제를 맡고 학술 list_sources는 그 뒤 별도 실제 경계로 배정한다. | 공유 manifest/캐시·생성기 의존을 순차화한다. Job/pythonw 성공·예약 cmdlet 대역·도구 판본만으로 대신하지 않는다. 설치 신뢰 승인/연구 검증은 이번 Lean smoke의 범위 밖이다. |',1)
seams=before['seams.md']+'''
012 Lean/Mathlib의 기존 API 소비와 새 full 녹화/재생을 검수했다.013은 기존 PowerShellScheduler.run → operator_schedule.ps1, scheduled_operator.schedule/hold와 operator_bootstrap의 실제 OS 경계를 소비한다. 인자·Task-View 반환·실패의 정본은 이 코드와 ports/scheduler.py 및 현 계약 시험이며 별도 schema나 새 의미를 만들지 않는다. smoke/helper·corpus·미러를 한 task가 소유하므로 S 항목과 provides/uses는 추가하지 않는다. task 이름의 부재 확인·자기 소유 증거·정리는 외부 부수 효과의 범위이며 기존 예약/연구를 변경할 권한이 아니다. runtime/OS 권한 변경이 필요하면 후속 판단으로 반환한다.
'''
for n,text in [('context.md',context),('plan.md',plan),('seams.md',seams)]:
    (RUN/n).write_text(text,encoding='utf-8')
(OUT/'common-docs.diff').write_text(''.join(''.join(unified_diff(before[n].splitlines(keepends=True),(RUN/n).read_text(encoding='utf-8').splitlines(keepends=True),fromfile='before/'+n,tofile='after/'+n)) for n in before),encoding='utf-8')

phase=RUN/'phases/013'; assert not phase.exists()
(phase/'tasks/scheduler-smoke/evidence').mkdir(parents=True)
(phase/'logs').mkdir()
repo_inputs=['.claude/skills/do-math/AGENTS.md','.claude/skills/do-math/scripts/tests/시험-지침.md','.claude/skills/do-math/scripts/이음새-정본.md','.claude/skills/writing-skills/references/멀티런타임_동기화.md','docs/do-math/시험-재편-2026-09-29/설계.md','docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md','.claude/skills/do-math/scripts/operator_schedule.ps1','.claude/skills/do-math/scripts/operator_bootstrap.py','.claude/skills/do-math/scripts/do_math/powershell_scheduler.py','.claude/skills/do-math/scripts/do_math/scheduled_operator.py','.claude/skills/do-math/scripts/do_math/supervision.py','.claude/skills/do-math/scripts/do_math/ports/scheduler.py','.claude/skills/do-math/scripts/tests/boundary/test_operator_schedule_adapter.py','.claude/skills/do-math/scripts/tests/boundary/test_port_scheduler.py','.claude/skills/do-math/scripts/tests/contracts/test_port_scheduler.py','.claude/skills/do-math/scripts/tests/support/port_contracts/scheduler.py','.claude/skills/do-math/scripts/tests/support/entry.py','.claude/skills/do-math/scripts/tests/support/host_live.py','.claude/skills/do-math/scripts/tests/structure/test_corpus.py','.claude/skills/do-math/scripts/tests/unit/test_corpus_replay.py','.claude/skills/do-math/scripts/tests/corpus/manifest.json']
run_inputs=['sources/user-decisions.md','sources/model-policy-2026-10-14.md','phases/001/tasks/gate-readiness/evidence/gate-readiness.json','phases/010/tasks/host-smoke/evidence/review.md','phases/012/tasks/lean-smoke/report.json','phases/012/manager-evidence/verification.json','phases/012/manager-evidence/source-inspected.json','phases/012/manager-evidence/review.md']
parts=['smoke/test_scheduler_live.py','support/scheduler_live.py','corpus/scheduler/','corpus/manifest.json','unit/test_corpus_replay.py','시험-지침.md','.timings.json']
writes=[tree+'/skills/do-math/scripts/tests/'+part for tree in ('.claude','.agents') for part in parts]
save(phase/'phase.json',{'kind':'work','purpose':'012의 Lean 실연쇄 검수 뒤 G7의 시험 전용 실제 OS 예약 등록·pythonw 발화·해제와 녹화/재생을 연결한다. 공유 corpus/생성기/캐시와 OS 자원을 한 task가 소유한다.','tasks':[{'id':'scheduler-smoke','model':'gpt-6.1-sol','effort':'high','inputs':['run:'+p for p in run_inputs]+['repo:'+p for p in repo_inputs],'writes':writes,'provides':[],'uses':[]}]})
objective='''## 목적과 역할

G7의 실제 OS 예약 경계를 닫는다. 설계 8절의 T5는 시험 이름의 등록·pythonw 발화·해제를 요구한다. 현재 boundary.test_port_scheduler는 status만 실제 호출하며, boundary.test_operator_schedule_adapter의 등록 시험은 cmdlet 대역이다.010의 실제 pythonw 출력·Job 성공과012 Lean 성공으로 이 공백을 대신하지 않는다. 기존 제품 포트·PowerShell 어댑터·bootstrap을 그대로 사용해 최소 T5와 실제 예약 조회 녹화/재생을 추가한다.

이번 work는 새로운 시험·작은 helper·scheduler corpus/필요 최소 reader·지침·미러에 한정한다. runtime 결함이나 OS 조건이 드러나면 반례와 정확한 후속 범위를 반환한다. 학술·유료 공급자·Lean 재실행·L01 결정을 함께 묶지 않는다.

## 완료 조건

### A1 시험 소유 등록과 실제 설치 freeze를 확인

시작 소스와012 manager source-inspected를 대조하고 Windows/PowerShell/Python/pythonw의 경로·판본·SHA, Task Scheduler 서비스·현재 사용자 실행 조건을 비밀 없이 기록한다. 환경 전체나 인증 자료는 덤프하지 않는다. 자기 evidence 또는 공식 scratch 아래 새 repository 좌표와 workspace·새 instance 식별자를 사용한다. `supervision.task_names`가 만든 정확 세 이름이 OS에 모두 없음을 실제 status로 확인한 후에만 생성한다. 기존 이름이 있으면 덮지 말고 충돌 없는 새 좌표를 택한다. 생성 요청/성공과 cleanup 대상 이름을 실행 전에 자기 근거에 남긴다.

현재 `real_ports`와 `scheduled_operator.schedule`를 통해 실제 `PowerShellScheduler.run`·`operator_schedule.ps1`의 install을 실행한다. cmdlet·runner·bootstrap·스케줄러 포트를 대역으로 교체하지 않는다. 실제 pythonw freeze의 stdout JSON과 exit, manifest·snapshot 파일·등록 action/인자/WorkingDirectory·현재 Interactive/Limited principal·설정을 확인한다. engine의 무제한 실행 설정과 operator의 현행 설정 의미를 보존한다. 유효한 현 인자로 interval/timeout을 지정하며 새 제한을 제품에 추가하지 않는다.

새 workspace에는 현재 제품 `scheduled_operator.hold`로 HOLD를 먼저 기록하고 시험 동안 유지한다. 이는 공개 제품의 모델 호출 전 보류 경로를 사용해 OS 발화만 검사하기 위한 입력이다. 기존 연구를 생성·재개하거나 실제 모델 호출로 진행하지 않는다. 설치 freeze가 복제하는 것은 현재 제품이며 bootstrap을 합성 실행 파일로 바꾸지 않는다. 현 held 경로가 외부 호출을 막는지 코드와 필요한 자기 입력 대조로 확인한 뒤 실제 작업을 시작한다.

### A2 T5에서 실제 pythonw 발화·wake·해제를 입증

`smoke.test_scheduler_live`를 공식 T5 discovery와 `resource` 격리에 연결한다. install한 자기 operator/engine의 start 동작과 가까운 미래의 one-shot wake 등록을 실제 경로로 실행한다. wake는 실제 OS 시각 트리거로 발화해야 하며 직접 함수 호출이나 start 요청 수락으로 대체하지 않는다. `WakeAt/WakeKey`, task 이름·XML/action의 pythonw 및 live/frozen bootstrap 좌표, 등록·실행 전후의 실제 시각·상태·LastRunTime/LastTaskResult 등 원자료를 결속한다. 직전 결과0을 재사용하지 말고 이번 발화의 새 실행·종료를 관찰한다. 가능한 프로세스/작업 이벤트·PID/command 근거도 보존하되 관측하지 못한 stdout이나 내부 결과를 꾸미지 않는다. freeze에서 수집한 stdout과 OS task의 실행 관측을 구별한다.

보류된 실제 bootstrap의 정상 종료와 외부 모델/기존 연구에 부수 효과가 없음을 확인한다. 모델-free held 경로 성공은 연구 엔진의 실제 운전 성공을 뜻하지 않는다. 예약 조회만 성공하거나 권한 거부·환경 부재·발화 미관측이면 해당 A는 pass가 아니다. 실제 오류/환경 조건과 필요한 결정만 보고하고 권한 상승·서비스 설정·계정 정책을 변경하지 않는다.

자기 wake에 cancel-wake를 적용하고, 성공/실패 모두 finally에서 자기 세 task만 uninstall한다. cleanup 전 이름뿐 아니라 시험의 action/workspace 소유 증거도 확인한다. 실행 중이면 자기 것으로 결속된 작업/프로세스만 종료·회수하고 마지막 실제 status의 세 null과 자기 자원 종료를 확인한다. 다른 예약의 중지·재등록·해제를 하지 않는다. 소유 자원 정리에 실패하면 정확 이름·상태·오류와 필요한 후속 조치를 최우선 finding으로 남긴다. 시간은 소프트 기준이며 관찰 도구의 대기 만료를 성공·실패·변이 포착으로 바꾸지 않는다. 새 hard timeout을 도입하지 않는다.

### A3 새 실제 예약 녹화와 현재 parser를 연결

기존 scheduler_json reader와 manifest 계약을 읽고 실제 등록 상태와 해제 후 부재 상태를 작은 원출력 녹화로 추가한다. 정확 argv/cwd·판본·시각·exit·시험 이름·원바이트 SHA와 녹화 당시 판정을 결속한다. 재생은 현 `PowerShellScheduler`의 JSON 수신 경계를 사용한다. 가능하면 기존 reader를 그대로 사용하며 새 실제 입력이 요구할 때만 최소 확장한다. OS 관측 보조자료와 출하 corpus의 범위를 명시하고, 합성 출력이나 재직렬화 JSON을 원녹화라고 쓰지 않는다.

현재19항목·양쪽56파일·총112경로의 기존 비manifest 바이트/항목/verdict는 보존하고 manifest에는 새 항목만 추가한다. 기존 Lean full/preview·공급자 판정을 유지한다. 양쪽 corpus 전건의 명시 SHA·파일 선언·5MiB 상한·Git raw/clean·생성 바이트와 corpus3모듈을 확인한다. 유효한 등록이 불가능하면 부재/실패 자료만으로 실제 발화 완료를 주장하지 않는다.

### A4 관련 회귀·이력·미러와 인계를 완결

원문 설계3.3/4.5/5.1/8과 결함 범주9-C, 현 시험 지침을 대조한다. `0dd16a5e`의 예약 포트 분리 및 `a0e6c2f4`의 예약/pythonw freeze 수리 중 이번 경계의 실제 diff·현재 소비자·존재하는 원보고만 검토한다. 이 두 commit의 다른 Lean/도메인/저장 변경은 범위 밖이다. 현재 boundary 단언과010의 승인된 pythonw 성질은 유지하며 없는 역사 보고 counts를 새 성공으로 합산하지 않는다.

최종 정본 새 scheduler T5, `boundary.test_port_scheduler`, `boundary.test_operator_schedule_adapter`, `contracts.test_port_scheduler`, `structure.test_corpus`, `unit.test_corpus_replay`, `contracts.test_doubles_follow_corpus`, `structure.test_test_smells`, `structure.test_boundary_invariants`, `structure.test_ports`를 공식 runner로 확인한다. 새 helper가 실제 소비하는 계약에 꼭 필요한 선택만 추가한다. 선택/고유row/실제exit와 실행 전후 해시를 보존하며 skip/error/미실행을 pass로 세지 않는다. 전체 일반/T3/변이는 실행하지 않는다.

지침에 OS 권한·로그온 조건·시험 이름/소유 범위·보류 입력의 의미·실행 원자료·실패시 정리·한계를 적는다. 공식 생성기의 사전 계획을 writes에 대조하고 생성한다. 미러의 새 scheduler 실실행과 같은 관련 회귀를 순차 완료한 뒤 비용 캐시만 공식 재동기화하고 --check/skill-only를 확인한다. 기존 runtime124·공급자 입력3·host/Lean 입력·corpus의 불변과 도구 조건을 대조해 기존 승인 근거를 한정 재사용한다. 각 A, 외부 부수 효과와 정리, 미충족 조건·나머지 G를 report에 남긴다.

## 판단과 경계

모델은 gpt-6.1-sol/high. phase.json의 신규 smoke/helper·scheduler corpus/manifest·필요 최소 replay·시험 지침·캐시와 대응 미러만 수정한다. 제품 runtime·PS 어댑터·bootstrap·기존 boundary·생성 규칙/속성·공용 문서·engine·원보고는 수정하지 않는다. 실제 제품 결함이면 반례를 남기고 후속 work에 필요한 정확 파일/조건을 제안한다. 무관한 개선을 따라가지 않는다.

원문 G7에 따른 시험 소유 OS task의 생성·발화·취소·해제와 자기 workspace/snapshot 쓰기는 허용된다. 대상은 시작 때 부재를 확인한 새 좌표의 정확 세 task다. 기존 예약·연구·계정/서비스 설정 변경, 권한 상승, 설치/다운로드, 유료 호출, Git stage/commit/reset/checkout/push 및 graphify 갱신은 하지 않는다. 현재 코드·계약에서 확인 가능한 판단은 직접 해결한다. 계약/권한 개정이 필요하면 해당 부분만 미완료로 보고하고 가능한 독립 산출물은 완결한다. L01 Q1/Q2는 이 task가 결정하지 않는다.

## 검증 방법

cwd `C:\\math`, Python `C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`. 정본/미러 공식 run_tests.py에 `-u -B`, 정확 선택과 `--jobs 1 --output <자기 evidence의 새 폴더>`를 사용한다. `--tier T5 --list`로 discovery만 확인하며 전체 T5를 실행해 공급자·Lean을 재호출하지 않는다. 동시에 한 검사 묶음만 실행하고 제품/시험 소스를 고정한다.

실제 argv/cwd/PID/시각/exit·stdout/stderr, OS task before/after·정리와 원자료 SHA를 보존한다. 진행 중 result.json은 기존 read_bytes_shared로 읽는다. 생성/실행 권한 거부는 원자료에 근거해 A 실패 또는 not_run과 finding을 연결한다. 자기 자원 cleanup은 실패 뒤에도 수행한다. 마지막 `python -B services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 013 scheduler-smoke`를 통과하고 report 경로와 상태를 반환한다. 학술·T4 adapter 보고·문서/의미 질문·G4~G6/G8 및 최종 review는 후속 manager의 책임이다.
'''
(phase/'tasks/scheduler-smoke/objective.md').write_text(objective,encoding='utf-8')

review='''# phase 012 관리 검수

lean-smoke의 A1~A4 complete를 승인한다. report 형식 검사 뒤 현재2658파일·종료 해시와 파일 집합,011 manager/시작 해시 동일, 허용22변경 및 report 대응을 확인했다. 초기 live-01/02의 error1·exit1은 역사 실패 그대로다. 마지막 정본/미러 T5 각1passed와 관련 각48passed·exit0, 각869 Python과 실행 전후 해시를 원보고에서 대조했다. 재실행한 유료/Lean/host 호출은 없고 manager의 확인은 원자료 검산과 순수 parser 재생이다.

기존 Lean4.32.0/Lake5.0.0/Mathlib v4.32.0에서 setup_lean의 대표 프로그램이 실제 import Mathlib·rfl·norm_num을 컴파일했다. 실제 identity와9의존 HEAD/manifest revision, 실행 파일/설치 입력 SHA,11094판단파일 전후 메타데이터와 신뢰 기록 바이트를 확인했다. 정상 선언의 수학적 내용과 미리 적은 서명에서 기대값을 얻으며 빈 공리·full32의존·정확 compiled input을 원out으로 재생했다. 타입 오류는 실제 exit1/failed/lean rejected와 진단에 연결된다. 각5Job의 request/status/실제 종료 관측과20판정, workspace 정리를 대조했다. 설치 신뢰 승인이나 연구 저장/평가 성공은 이 근거가 말하지 않는다.

새 corpus는 정상 원out71704바이트와 source/compiled input/빈 stderr의 원복사다. 제품이 줄인 stdout과 원out SHA가 다른 이유가 provenance에 기록돼 있다. full 옵션은 새 항목에만 명시돼 기존 두 Lean preview 및 다른18항목/verdict를 보존한다. 현재 각19항목·56파일·320687바이트, 총112경로 raw/clean·명시 SHA·양쪽 바이트와1314파일 --check를 확인했다. runtime124·공급자 입력3·host 입력/8원자료는 불변이고 승인된 성질만 재사용한다. 초기 도우미 타입/Calls 오류와 Mathlib 표기 교정은 최종 코드에 반영됐으며 과거 실패를 성공으로 다시 쓰지 않았다.

B38/8afa57c7의 formal/setup hunk를 현재 필수 git_backend 전달·identity별 memo·None/미추적/.lake 제외와 대조했다. 관련8 sim과 실제 경계 근거로 이 slice를 유지한다. 원보고10개가 현재 없는 한계와 PR02 전체 미종결을 유지한다. objective의 설계5.6은 현 설계에 없는 위치이며 실제3.3/4.5/5.1/8과9-C 내용으로 판정했다. 요구나 G를 줄이는 해석은 하지 않았다.

013은 단일 scheduler-smoke다. 현 실제 포트/PS/동결 bootstrap과 pythonw를 사용하고 새 시험 workspace의 제품 HOLD로 유료/기존 연구 경로를 차단한다. task 이름의 시작 부재·소유 action·등록/발화/해제 원자료와 마지막 부재를 요구한다. start 수락·옛 결과0·status만으로 발화를 인정하지 않는다. OS 정책/권한이나 runtime 수리는 이 task의 재량이 아니다. corpus/생성기/캐시와 OS 자원을 공유하므로 제품 task를 병렬 배정하지 않는다. 학술·T4 보고·나머지 문서/의미 질문·L01 외부결정·최종 관문은 남는다.

common-docs.diff에서 공용 갱신 전후를 대조했다. C2에012 검수, C5에013 자원 소유, C8에모델, C9에B38 한정 유지, C10에L01 미정과 독립 진행, C11에Lean 종결/예약 책임, C12에112경로와제품20경로 마감을 반영했다. 기존 C/G 의미·완료 기준·역사 예외와 미해결 조건은 보존한다. seam의 동작 변경이나 새 S는 없다. 다음 phase/objective와 관리 기록·기억을 먼저 확정하고 handoff 검사 뒤 manager.json 게시·정확 stage/commit 순서로 마감한다. 원보고/원자료는 수정하지 않는다.
'''
(OUT/'review.md').write_text(review,encoding='utf-8')
ref=lambda p:'run:phases/012/'+p
ver=ref('manager-evidence/verification.json'); rev=ref('manager-evidence/review.md')
updates=[]
for item,reason in [('C2','012의 실제 검수와 초기 실패/최종 성공의 구별을 추가했다.'),('C5','종료된012의 소유를013 예약 단일 task와 OS 자원 범위로 갱신했다.'),('C8','사용자 모델 정책을 유지하고012 검수 및013 배정을 기록했다.'),('C9','B38 formal/setup 지정 slice의 유지와 원보고 부재 한계를 추가했다.'),('C10','L01 외부결정과 원문 byte 기준을 유지하면서 독립 진행을013으로 갱신했다.'),('C11','실제 Lean 지정 범위를 종결하고 예약 work와 남은 G7/전체 관문을 구별했다.'),('C12','기존 실호출 재사용과 새19항목/112경로 원바이트,제품20경로 관리 마감을 반영했다.')]:
    updates.append({'item':item,'action':'amend','destination':['run:context.md#'+item],'reason':reason,'evidence':[ver,rev,ref('manager-evidence/common-docs.diff')]})
manager={'next':'013','decision':'012 lean-smoke의 A1~A4 complete를 원파일·현재 해시·실제 exit/row·OS Job 자료에 대조해 승인한다. 초기 두 도우미 오류는 실패로 보존하고 최종 양쪽 Lean1·회귀48만 새 성공 근거로 삼는다. 실제 Mathlib 대표 컴파일과 정상/오류·full증거·112 corpus 경로 및 기존18항목 보존을 검수했다. 설치 신뢰 승인이나 전체 G 완료는 아니다.\n\nF1의 지정 Lean 남김을 닫고 F2의 B38 한정 유지 및 원보고10개 부재를 C9에 반영한다. F3의 불변 경로 재사용·새 녹화 바이트와 관리 마감을 승인한다. 다음013은 시험 소유의 실제 예약 등록·pythonw 발화·해제와 녹화/재생 work다. 새 workspace/HOLD와 충돌 없는 세 task 이름으로 기존 연구·유료 호출을 방지하고 실제 발화/정리를 검증한다. 공유 OS/manifest/구조 검사/미러/캐시 때문에 단일 task가 순차 소유한다. L01 Q1/Q2의 외부 결정은 바꾸지 않으며013은 독립적이다.\n\n원문 모집단·보존 의무·나머지 문서/의미 질문·학술/T4·G4~G6/G8과 최종 review는 남는다. 직전 phase는 work이므로 개발 완료를 선언하지 않는다. 제품20경로와 선별 원자료/원바이트 archive·공용 문서·013 배정·기억을 handoff 통과 뒤 정확 범위로 로컬 커밋한다. 별도 작업트리 변경과 비용 캐시는 포함하지 않고 push하지 않는다.','reports':[{'task':'lean-smoke','state':'read','detail':'report 전문을 읽고 manager report 검사를 통과했다. 현재2658파일/허용22변경·6공식 실행과 초기 실패/최종 성공·각20판정/5Job·원녹화·기존 항목을 대조했다. 모든A pass를 지정 범위에서 승인한다.','evidence':[ref('tasks/lean-smoke/report.json'),ref('manager-evidence/report-check.stdout.log'),ver,rev]}],'dispositions':[
{'item':'012/lean-smoke/F1','action':'resolve','destination':['run:context.md#C11','run:plan.md'],'reason':'대표 Mathlib/정상 full32/오류와 실제 Job 원자료·판본을 대조해 지정 Lean 범위를 닫았다. 설치 신뢰 채택이나 다른 G7 완료는 아니며 실제 예약은013으로 배정했다.','evidence':[ver,rev,'run:phases/013/tasks/scheduler-smoke/objective.md']},
{'item':'012/lean-smoke/F2','action':'resolve','destination':['run:context.md#C9'],'reason':'실제8afa57c7 formal/setup diff·현재 필수 포트·관련8sim·실환경을 대조해 이 slice를 유지한다. 원보고10개 부재와 PR02 다른 slice/최종 판본 책임은 보존했다.','evidence':[ver,rev,ref('tasks/lean-smoke/evidence/history-b38.stdout'),ref('tasks/lean-smoke/evidence/history-original-reports.json')]},
{'item':'012/lean-smoke/F3','action':'resolve','destination':['run:context.md#C12','run:plan.md'],'reason':'runtime124·공급자입력3·host 입력/8원자료·기존100비manifest경로/18항목을 확인했다.112경로와 새full녹화 바이트/미러를 승인하고 검수된20제품경로를 관리 마감한다. 전체 관문 합산은 하지 않는다.','evidence':[ver,rev,ref('manager-evidence/git-clean-observation.json'),ref('manager-evidence/preservation.json')]}],
'context_updates':updates,'plan_update':'012 Lean 지정 work를 종료하고013 실제 예약 work를 배정했다.012 제품20경로의 관리 마감, 실호출 재사용 조건과 설치 신뢰 승인 제외를 연결했다. L01 외부결정·학술·T4 adapter 보고·문서/의미 질문과 최종 전체 일반→fresh T3→전체 함수 변이→review 순서는 유지한다. 공유 manifest/생성기/캐시·OS 자원의 충돌을 피하도록 한 task가 소유한다.','seam_updates':[],'completion':None}
save(RUN/'phases/012/manager.pending.json',manager)

version=int(re.search(r'^convention_version: (\d+)',(REPO/'기억/세칙.md').read_text(encoding='utf-8'),re.M).group(1))
nodes=list((REPO/'기억/layer1').glob('M-*.md')); number=max(int(p.stem[2:]) for p in nodes)+1
assert number==562
node=REPO/'기억/layer1/M-0562.md'; assert not node.exists()
node.write_text(f'''---
id: M-0562
layer: 1
title: Lean 실연쇄를 검수하고 시험 전용 예약 경계를 배정함
convention_version: {version}
---

## 맥락

012는 설치가 보인다는 사실과 실제 Mathlib 컴파일을 구별하는 작업이었다. manager는 정본/미러의 실제 대표 프로그램, 정상 두 선언의 full32의존 증거와 짝 타입 오류를 원 request/out/status·서명·판본에 대조했다. 초기 도우미 타입/Calls 오류 두 건은 실패로 보존하고 최종 T5 각1·관련각48만 새 성공으로 승인했다. 관찰된 설치 입력/신뢰 기록 불변은 설치를 승인하거나 연구 증거를 채택했다는 뜻이 아니다.

## 판단의 조건

정상 verifier의 stdout은 의존 본문을 해시로 줄인 제품 결과다. 출하 녹화는 Job spool에서 보존한 원out71704바이트이며 둘의 SHA가 다르다. 관리 검산은 원out의 parser 재생과 compiled input을 확인하고 기존 두 Lean preview와 새 full 항목의 범위를 구별했다. 원출력과 최종 제품 표현 중 어느 것을 보존했는지 적지 않으면 정확한 해시 비교도 엉뚱한 두 파일을 비교하게 된다.

대표 컴파일308.3초와21.2초는 파일 캐시 조건이 다른 관찰이다. 이를 코드 최적화 성과나 시간 제한 근거로 읽지 않았다. B38의 Git 포트 도입 slice도 현재 코드와8sim/실환경으로 유지하되, 없는 원보고10개의 counts를 새 실행에 더하지 않았다. 현재2658파일·허용22변경·112 corpus 경로를 검산했고 검수된20제품경로만 관리 커밋에 포함한다.

## 보존과 다음 책임

추적 진입점은 `docs/do-math/continuous-development-2026-10-13/phases/012/manager.json`, `manager-evidence/review.md`, `verification.json`, `preservation.json`과013 objective다. 원 task 자료와 제품 바이트는 `raw-evidence.zip`에도 보존한다. 일부 scratch/중복 snapshot은 압축으로만 추적되고 원경로와 stage/commit 수신은 로컬 보관이라 정리로 사라질 수 있다. 자동 복원 지시가 아니다.

013의 예약 work는 실제 포트/PowerShell/동결 bootstrap과 pythonw를 쓴다. 새 시험 workspace의 제품 HOLD로 외부 모델/기존 연구 경로를 막고, 부재를 확인한 정확 세 task의 등록·새 발화·종료·해제를 확인한다. start 수락과 이전 LastTaskResult0을 실제 발화로 오인하지 않게 실행 시각/action을 결속한다. 공유 corpus·미러·캐시와 OS 자원을 한 task가 소유한다. 학술·T4 보고·문서/의미 질문·L01 외부결정·최종 일반/T3/변이/review는 계속 남는다.
''',encoding='utf-8')
index=REPO/'기억/색인.md'; text=index.read_text(encoding='utf-8'); assert 'M-0562' not in text
line='- M-0562 [Lean 실연쇄를 검수하고 시험 전용 예약 경계를 배정함] -- 실제 Mathlib·full 증거·오류와112 corpus 경로 승인, 설치 신뢰와 구별·013 OS 발화/정리 배정\n'
text=text.replace('## layer-1\n','## layer-1\n\n'+line,1)
index.write_text(text,encoding='utf-8')
print('Prepared 013, common documents, review, pending manager and M-0562.')
