"""Prepare the reviewed shared state and next assignment; no product edits."""
from pathlib import Path
import difflib
import json

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'; O=Path(__file__).resolve().parent
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(p,v): p.write_text(v,encoding='utf-8')
v=json.loads((O/'verification.json').read_bytes()); assert v['result']=='pass'
before={n:(RUN/n).read_text(encoding='utf-8') for n in ('context.md','plan.md','seams.md')}
c=before['context.md']
def replace_once(body,old,new):
    assert body.count(old)==1,(old,body.count(old))
    return body.replace(old,new,1)
def replace_section(body,title,new):
    start=body.index(title); end=body.find('\n## ',start+len(title))
    if end<0: end=len(body)
    return body[:start]+new.rstrip()+'\n\n'+body[end:].lstrip('\n')
summary='''phase 013 scheduler-smoke는 A1~A4 complete로 검수했다. manager report 검사 후 현재2674파일과 종료 해시 전건 일치, 시작과012 manager 판본 동일, 허용22변경을 확인했다. 초기 live 세 실행의 error1은 역사 실패로 유지한다. 최종 live1passed·정본/미러 각33passed의 선택·고유row·실제exit와 각871 Python을 대조했다. 세 성공 표본의 각19판정·26명령 원바이트·291 snapshot 파일, 실제 operator/engine start와 시각 wake의 미실행267011에서 새 ticks/Ready/0 전이, 최종세null·HOLD/연구무부수효과를 확인했다. live-final의 wake PID9492는 실제 관측됐으므로 보고서의 포괄적 PID 미관측 문장은 최종 정본/미러 관련 실행에 한정한다. 원보고는 고치지 않는다. corpus 각21항목·62파일과124경로 Git raw/clean·기존19항목 보존을 검산했다. 근거는 run:phases/013/manager-evidence/verification.json·review.md다. held 설치/OS 경계의 완료이며 연구 운전·전체 G 완료는 아니다.'''
c=replace_once(c,'## C3 현재 정본과 이력의 역할',summary+'\n\n## C3 현재 정본과 이력의 역할')
old=c[c.index('phase 001~012의 task 세션은 종료됐고012의 Lean 실연쇄를 검수했다.'):c.index('\ndo-math 시험 프로세스는 전체 합계 worker 3 이하')]
new='''phase 001~013의 task 세션은 종료됐고013의 예약 실연쇄를 검수했다.014 scholarly-smoke는 기존 Codex/ModelRunner/worker에서 학술 MCP list_sources를 실제 호출하고 완료 응답·실행별 data-dir·종료와 녹화/재생을 한 task가 맡는다. corpus manifest·전건 구조 검사·생성기·비용 캐시와 유료 공급자 실행 자원을 공유하므로 다른 제품 수정/시험 task를 병행하지 않는다. jobs1·한 묶음씩 실행한다. 기존 공급자/host/Lean/예약의 불변 입력에서 승인된 성질만 재사용한다. 학술 자료 검색·fetch나 기존 연구 운전은 이 최소 연결 범위에 포함되지 않는다. T4 보고·문서/의미 질문·읽기 조건은 별도 후속 책임이다.
'''
c=replace_once(c,old,new)
c=replace_once(c,'012 lean-smoke의 gpt-6.1-sol/high 작업을 검수했고013 scheduler-smoke도 같은 설정으로 배정한다. 각 세션의 모델 정책은 C8의 사용자 지정과 같으며 제품 공급자 호출 설정과 구별한다.','012와013의 gpt-6.1-sol/high 작업을 검수했고014 scholarly-smoke도 같은 설정으로 배정한다. 각 세션의 모델 정책은 C8의 사용자 지정과 같으며 제품 공급자 호출 설정과 구별한다.014 제품 실호출은006의 검증된 Codex gpt-6-astra/low를 기본으로 사용하고 실제 도구 판본과 요청 설정을 기록한다.')
history='''013에서 0dd16a5e의 예약 포트 분리/real_ports 배선과 a0e6c2f4의 pythonw freeze Out-String·null/nonzero exit·빈 JSON 반려를 실제 diff·현재 소비자·양쪽33회귀로 대조했다. 이 예약 slice의 유지와 실제 OS 경계 추가 판단을 승인한다. 해당 raw 역사 report 위치를 task 입력/진행 기록에서 확인하지 못했다는 한계를 유지하며 부재의 원인이나 저장소 전체 부재를 단정하지 않는다. 다른 hunk와 PR02 전체는 미종결이다. 근거는 run:phases/013/tasks/scheduler-smoke/evidence/history-port.stdout·history-freeze.stdout·history-index.json·review.md와 manager 검수다.'''
c=replace_once(c,'## C10 문서 결속에서 남은 고정 범위',history+'\n\n## C10 문서 결속에서 남은 고정 범위')
c=replace_once(c,'013 예약 work도 이 답변과 독립적으로 진행한다.','013 예약 work도 완료했으며014 학술 최소 연결은 이 답변과 독립적으로 진행한다.')
old=c[c.index('실제 OS 예약 등록·발화·해제는013 scheduler-smoke에 배정한다.'):c.index('\n## C12 공급자 부분 성공과 원바이트 인도')]
new='''013에서 시험 소유의 실제 OS 예약 등록·pythonw 동결/발화·one-shot wake·취소·해제 범위를 닫았다. real_ports/PowerShellScheduler/operator_schedule.ps1·scheduled_operator.schedule·operator_bootstrap는 불변이다. 새 workspace의 HOLD가 상태 읽기/모델 호출보다 먼저 반환하는 현재 경로, 실제 action/인자·Interactive/Limited·operator PT2H/PT1H35M·engine PT0S·snapshot291파일을 대조했다. 최종 정본/미러 각33건은 새 설치/OS 실실행을 포함한다. 별도 직접 pythonw freeze/held stdout과 OS task의 실행 관측은 서로 다른 증거다.

세 성공 표본의 operator/engine/wake는 미실행267011/1999시각에서 새 LastRunTime ticks·Ready·LastTaskResult0으로 바뀌었다. wake에는 start 요청이 없고 XML의 시각 트리거와 WakeKey를 대조했다. 마지막 실제 status는 세null이고 자기 프로세스 부재·HOLD 불변·빈 repository·engine/recovery 미생성을 확인했다. 초기3error는 수정 전 helper/관찰 실패로 유지한다. live03은 확인된 소유 작업만 명시 해제했다. 서비스시각과 관찰 벽시계의 차이는 원인 미확인이며 정확 시간 지연 측정으로 사용하지 않는다. Operational 로그는 disabled이고 OS stdout은 미관측이다. task F2의 PID 미관측 표현은 정정한다. live-final await-wake 원출력에는 정확 live bootstrap/workspace의 pythonw PID9492가 있고, 최종 canonical-related/mirror-related에는 PID 관측이 없다. 이 정정은 원report 수정이나 새 OS 실행을 뜻하지 않는다. 근거는 run:phases/013/manager-evidence/verification.json·review.md와 원smoke/명령 자료다.

다음014는 실제 Codex worker가 격리된 scholarly 서버에 list_sources를 호출하고 성공 완료 응답을 받는 경계다. 기존 probe_cli의 scholarly_actual_tool은 시작 사건의 도구명만 확인하므로 단독으로 응답 성공을 입증하지 않는다. 새 smoke는 현재 native 완료 결과·실제 source 목록/상태·파일/checkpoint·로컬 종료를 확인한다. 이는 제품 코드 변경 없이 새 시험에서 보완할 검증 공백이며 학술 search/fetch 성공을 요구하지 않는다. 학술 MCP·T4 별도 adapter 분기·13-C/L01 조건과 G4~G6/G8 최종 관문은 여전히 남는다. 책임은 run:phases/014/tasks/scholarly-smoke/objective.md다.
'''
c=replace_once(c,old,new)
c+='''
013 F4의 불변 근거를 검수했다. runtime124·공급자3·host4·Lean4 입력과 host8원자료, 도구 조건은 유지됐고 기존19corpus 항목/verdict·110비manifest경로도 보존됐다. 새 scheduler 원녹화 두 항목과 현 parser 재생을 확인해 현재 각21항목·62파일·344100바이트, 총124경로의 명시 SHA·Git raw/clean·양쪽 바이트가 일치한다. --check1322와 skill-only를 확인했다. 새 정본/미러 관련33건을 과거 성공과 합산해 전체 관문으로 읽지 않는다. 검수된 제품·시험·지침·미러20경로를 이번 관리 커밋으로 마감하고 비용 캐시2개는 제외한다. 원 task 자료와 제품 원바이트는 raw-evidence.zip에 보존한다. 선별 원경로·압축 항목·SHA와 로컬 보관 범위는 run:phases/013/manager-evidence/preservation.json, 행정 수신은 로컬 commit.json에 둔다. 압축으로만 추적되는 scratch/중복 snapshot의 원경로는 정리 시 사라질 수 있으며 자동 복원 지시가 아니다.014 배정과 공용 문서·기억의 행정 추가는 제품 판본을 바꾸지 않는다.
'''
p=before['plan.md']
p=replace_once(p,'## phase 001~012의 결과와 현재 상태','## phase 001~013의 결과와 현재 상태')
p=replace_once(p,'최종 전체 관문은 아직 실행하지 않았다.','013 예약 A1~A4도 검수했다. 실제 held 등록/발화/wake/정리와 정본·미러 각33건을 승인했고, 초기3error 및 시계/OS stdout 관측 한계를 보존했다. live-final wake PID9492 원관측을 반영해 포괄적 미관측 표현만 정정했다. 최종 전체 관문은 아직 실행하지 않았다.')
start=p.index('## 다음 phase: 013'); end=p.index('## 가까운 후속 배정과 선행 관계',start)
p=p[:start]+'''## 다음 phase: 014

scholarly-smoke 단일 work를 gpt-6.1-sol/high로 배정한다. 기존 resolve_scholarly_server·ModelRunner/worker·실제 Codex/학술 서버를 통해 list_sources 한 번의 시작/성공 완료와 응답 내용을 확인한다. 실제 source 목록은 설치 서버의 registry/Source.summary와 대조하고 protocol_probe 파일·checkpoint·로컬 종료도 유지한다. probe_cli의 시작 도구명만으로 성공을 판정하지 않는다. 새 T5와 실제 native 원녹화·현재 parser 재생에 연결한다. 최소 정본 실호출 뒤 미러는 녹화/바이트·관련 오프라인 검사로 검증하며 새 실호출은 입력/호출 경로가 바뀌어 이전 증거를 쓸 수 없을 때만 판단한다. 제품 runtime이나 scholarly 서비스/설정 수리는 이 배정 밖이며 필요하면 정확 반례를 반환한다.

공유 corpus manifest·전건 구조 검사·공식 생성기·비용 캐시와 공급자/서버 자원을 한 task가 jobs1로 순차 소유한다. 현재 경계의 완료에 기여하지 않는 병렬 분석은 추가하지 않는다. 새 seam은 없고 입력·writes·A·검증은 run:phases/014/phase.json 및 objective다.013 제품20경로는 관련 회귀/미러 검수 뒤 현재 관리 마감에 포함한다.

L01의 Q1/Q2는 외부 결정으로 남는다. 공급자별 운전 host/tool/판본/model/호출 설정과 출력 byte 기준 유지 또는 도구 단위 개정을 확정해야 한다. 이미 상신한 단위 선택의 답변이 없으므로 원문 byte 기준과 미충족을 유지한다.011 문구 수리와012~013 경계 성공은 읽기 용량 인증이 아니며014 학술 작업은 이 답변과 독립적이다.

'''+p[end:]
p=replace_once(p,'012에서 Lean/Mathlib 실연쇄를 검수했고 그 제품20경로를 마감하며013 예약 경계로 진행한다. 근거는012 manager-evidence/verification.json·review.md다.','012 Lean/Mathlib 제품20경로는 a8fb1e41로 마감됐다.013 예약 실연쇄를 검수했고 제품20경로를 마감하며014 학술 MCP 경계로 진행한다. 근거는013 manager-evidence/verification.json·review.md다.')
p=replace_once(p,'013은 시험 이름의 실제 예약 등록·pythonw 발화·해제를 맡고 학술 list_sources는 그 뒤 별도 실제 경계로 배정한다.','013의 시험 이름 등록·pythonw 발화·해제도 검수했다.014는 Codex worker를 통한 학술 list_sources의 실제 성공 완료·결과와 격리·녹화/재생을 맡는다.')
p=replace_once(p,'설치 신뢰 승인/연구 검증은 이번 Lean smoke의 범위 밖이다.','설치 신뢰 승인/연구 검증은 Lean smoke 밖이고 held 예약 성공은 연구 운전 성공이 아니다. 학술 도구 시작 사건만으로 성공 응답을 판정하지 않는다.')
s=before['seams.md']+'''
013의 기존 예약 API 소비와 실제 OS 발화/정리·녹화 재생을 검수했다.014는 resolve_scholarly_server의 command/args, ModelRunner.run의 scholarly_server 및 worker의 실행별 scholarly-data 격리, native 도구 사건과 services/scholarly-mcp/server.py의 list_sources/ToolResult·registry.Source.summary를 소비한다. 시작 도구명과 완료 성공 응답은 구별한다. 새 시험·작은 지원 정의·corpus/reader·미러를 한 task가 소유하며 기존 제품 인터페이스를 개정하지 않으므로 S 항목·provides/uses는 추가하지 않는다. runtime·서버·공유 설정 변경이 필요하면 정확 반례와 후속 책임으로 반환한다.
'''
for n,b in [('context.md',c),('plan.md',p),('seams.md',s)]: text(RUN/n,b)
diff=''.join(''.join(difflib.unified_diff(before[n].splitlines(keepends=True),(RUN/n).read_text(encoding='utf-8').splitlines(keepends=True),fromfile=n+' before',tofile=n+' after')) for n in before)
text(O/'common-docs.diff',diff)

next_dir=RUN/'phases/014'; task=next_dir/'tasks/scholarly-smoke'
(task/'evidence').mkdir(parents=True,exist_ok=True); (next_dir/'logs').mkdir(parents=True,exist_ok=True)
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json','run:phases/006/tasks/codex-schema/report.json','run:phases/013/tasks/scheduler-smoke/report.json','run:phases/013/manager-evidence/verification.json','run:phases/013/manager-evidence/source-inspected.json','run:phases/013/manager-evidence/review.md']
inputs += ['repo:'+x for x in ['.claude/skills/do-math/AGENTS.md','.claude/skills/do-math/scripts/tests/시험-지침.md','.claude/skills/do-math/scripts/이음새-정본.md','.claude/skills/writing-skills/references/멀티런타임_동기화.md','docs/do-math/시험-재편-2026-09-29/설계.md','docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md','.claude/skills/do-math/scripts/probe_cli.py','.claude/skills/do-math/scripts/do_math/scholarly.py','.claude/skills/do-math/scripts/do_math/scholarly_config.py','.claude/skills/do-math/scripts/do_math/model_runner.py','.claude/skills/do-math/scripts/do_math/cli_worker.py','.claude/skills/do-math/scripts/do_math/codex_worker.py','.claude/skills/do-math/scripts/do_math/codex_adapter.py','.claude/skills/do-math/scripts/do_math/codex_stream.py','.claude/skills/do-math/scripts/tests/support/provider_live.py','.claude/skills/do-math/scripts/tests/unit/test_academic_scholarly_config.py','.claude/skills/do-math/scripts/tests/unit/test_academic_scholarly_validation.py','.claude/skills/do-math/scripts/tests/structure/test_corpus.py','.claude/skills/do-math/scripts/tests/unit/test_corpus_replay.py','.claude/skills/do-math/scripts/tests/contracts/test_doubles_follow_corpus.py','.claude/skills/do-math/scripts/tests/corpus/manifest.json','services/scholarly-mcp/server.py','services/scholarly-mcp/registry.py']]
paths=['scripts/tests/smoke/test_scholarly_live.py','scripts/tests/support/scholarly_live.py','scripts/tests/corpus/scholarly/','scripts/tests/corpus/manifest.json','scripts/tests/unit/test_corpus_replay.py','scripts/tests/structure/test_corpus.py','scripts/tests/시험-지침.md','scripts/tests/.timings.json']
writes=[tree+'/skills/do-math/'+x for tree in ('.claude','.agents') for x in paths]
save(next_dir/'phase.json',{'kind':'work','purpose':'013 예약 검수 뒤 G7의 실제 Codex worker→학술 MCP list_sources 성공 완료·결과·격리·녹화/재생 공백을 닫는다. 공유 corpus/생성기/캐시와 실호출을 한 task가 소유한다.','tasks':[{'id':'scholarly-smoke','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]})
text(task/'objective.md','''## 목적과 역할

G7의 학술 MCP 최소 실제 연결을 검증한다. 지금 corpus의 scholarly_config는 command/args 해석 녹화이고 실제 list_sources 성공이 아니다. probe_cli.run_case의 scholarly_actual_tool도 native 시작 사건의 도구명만 확인한다. 기존 제품의 Codex worker·실제 서버를 통해 성공 완료 응답을 확인하고, 현 T5와 원녹화 재생에 연결한다. 공급자 maintenance·host/Lean/예약 성공은 승인된 범위로 재사용한다. 새로운 학술 검색 기능이나 연구 운전을 구현하는 작업이 아니다.

## 완료 조건

### A1 실제 입력과 격리 경계를 확정

시작 소스를013 manager source-inspected와 대조한다. 현재 resolve_scholarly_server가 선택한 command/args와 해석 기준 파일, Codex 실행 파일/판본/SHA, 서버 실행 파일·Python/패키지 판본과 list_sources/registry 소스를 비밀 없이 기록한다. 다른 설정·환경·인증 파일 전문을 덤프하지 않는다. 실제 프로젝트 설정은 scholarly 테이블만 읽고 값은 현재 validator로 검증한다. 사용자·프로젝트 설정, 서비스·venv·설치·인증을 변경하지 않는다.

기존 ModelRunner/real_ports/worker/adapter/collector를 사용하고 worker의 실행별 scholarly-data 경로가 새 시험 workspace 안임을 실제 요청/worker snapshot/argv로 확인한다. 기존 probe_cli.run_case(files, scholarly=True)를 그대로 호출하고 그 결과를 추가 검증하는 방식 등 기존 경로를 우선 재사용한다. 제품 내부/실제 CLI/서버를 대역으로 바꾸거나 MCP 우회 호출만으로 제품 연결을 대신하지 않는다. 새 helper는 두 소비자가 공유할 검증이 있을 때만 둔다. 환경 부재나 runtime 결함이면 정확 실패·필요 조건과 후속 파일을 반환하고 해당 A를 pass로 만들지 않는다.

### A2 최소 실제 list_sources의 성공 완료와 종료를 T5로 확인

새 smoke.test_scholarly_live를 resource 격리와 T5 discovery에 연결한다. 정본에서 실제 Codex 호출 한 번을 기본으로 실행한다. 제품 실호출 기본은006에서 성공한 명시 model=gpt-6-astra, effort=low이며 CLI 경로/판본/실제 요청을 남긴다. 개발 task의 gpt-6.1-sol/high와 구별한다. 변경·실패로 새 호출이 필요하면 이유를 기록하고 최소화하며 성공한 동일 호출을 이유 없이 반복하지 않는다.

실제 list_sources 시작과 같은 요청의 성공 완료(native ID/server/tool/result 또는 현재 CLI의 대응 구조)를 연결한다. 요청 수락·도구명·모델의 성공 주장만으로 통과시키지 않는다. native 오류/isError·중단·응답 부재/파손은 실패다. 실제 응답의 status=ok와 sources의 유일한 ID 및 각 summary 필드를 설치 서버 registry/Source.summary의 현재 계약과 대조한다. 고정 개수/현재 출력 전체를 새 정본으로 복제하지 않는다. 공급자가 표현한 content/structuredContent를 구별하며 본문 전문 누락을 허용하지 않는다. MCP 초기화/도구 판본·서버 코드와 응답의 근거를 보존한다. 모든 자료원에 접근하거나 검색·fetch가 성공했다는 뜻으로 확대하지 않는다.

protocol_probe의 실제 파일/nonce·checkpoint·최종 구조화 결과, worker 요청/스냅샷과 native 원자료·종료 barrier/Job 회수를 확인한다. 호출은 list_sources 하나와 지정 로컬 파일 작업에 한정한다. 문헌 search/fetch·브라우저/로그인·다른 모델/에이전트 호출·기존 연구 재개는 하지 않는다. 실서버의 시험 데이터는 새 workspace에 두고 자기 자원을 회수한다. 인증/도구 조건 부재·응답 오류는 정확히 보고하며 시간만으로 실패/성공을 만들지 않는다.

### A3 실제 녹화와 현 parser의 재생·반례를 연결

실제 native stream/필요 최종 응답·stderr·요청/설정의 안전한 좌표·판본·시각·exit·SHA와 당시 판정을 corpus/scholarly에 추가한다. 원바이트를 재직렬화·발췌해 전체 원녹화로 표시하지 않는다. 필요 안전한 파생물은 원녹화와 별개로 출처/변환/제외 범위를 명시한다. 기존21항목/verdict·양쪽 비manifest122경로를 보존하고 manifest에는 새 항목만 추가한다. 민감한 환경값은 출하하지 않는다.

현재 codex_stream과 실제 수신 경계가 있는 경우 그 정의를 재사용해 녹화 재생을 연결한다. native MCP 결과에 제품 parser가 의미 판정을 제공하지 않으면 시험 전용 관찰자임을 밝히고 live와 replay가 공유하는 작은 정의를 사용한다. 새 범용 MCP parser나 제품 schema를 복제하지 않는다. 시작만 있음/오류 완료/누락·불완전 source 목록이 성공으로 판정되지 않는 의미 있는 반례를 기존 corpus 시험에 함께 검증한다. 정상 실제 녹화는 대조군이다. 생성 기대값을 같은 관찰자 결과만 복사해 정당화하지 않고 서버 계약/원자료와 대조한다.

양쪽 corpus 전건의 명시 SHA·파일 선언·5MiB 상한·Git raw/clean·미러 바이트와 corpus3모듈을 확인한다. scholarly_config의 기존 판정은 유지하며 실제 list_sources 녹화와 구별한다.

### A4 관련 회귀·이력·미러와 보고를 완결

설계3.3/4.5/5.1/8·9-C와 현 지침을 대조한다. 이번 입력/격리 경계의 과거 도입 commit은 git log로 좁혀 실제 diff·현재 소비자·존재하는 원보고만 확인한다. 이미 검수한003/006 공급자 slice를 전수 재검토하거나 없는 역사 counts를 새 성공으로 더하지 않는다. 검토 대상과 유지/추가/미확인 판단을 명시한다.

정본 새 T5 한 건, 관련 오프라인 unit.test_academic_scholarly_config, unit.test_academic_scholarly_validation, structure.test_corpus, unit.test_corpus_replay, contracts.test_doubles_follow_corpus, structure.test_test_smells, structure.test_boundary_invariants, structure.test_ports를 공식 runner로 실행한다. 기존 실제 입력/worker 배선에 새 변경이 있으면 해당 계약 선택만 추가한다. 선택/고유row/실제exit와 실행 전후 판본을 보존한다. skip/error/미실행을 통과로 세지 않는다. 전체 일반/T3/변이·기존 다른 T5는 실행하지 않는다.

지침에 실제 호출 설정·서버 조건·격리/정리·시작/완료 구별·녹화/관측 한계를 적는다. 공식 미러 생성 전 변경 계획을 writes에 대조하고 생성한다. 미러는 같은 관련 오프라인 선택·녹화 재생과 변환 바이트를 검증한다. 정본의 현재 실호출 경로와 미러의 변환 차이를 확인하고 재사용 범위를 명시한다. 미러의 유료 실호출은 기본으로 반복하지 않으며 오프라인 검사를 실제 미러 호출로 보고하지 않는다. 그 차이가 실호출 근거 재사용을 가리면 이유를 밝히고 필요한 최소 호출을 수행한다. 마지막 비용 캐시만 공식 동기화하고 --check/skill-only를 확인한다. 기존 runtime124·공급자/host/Lean/예약 입력과 원자료의 불변/도구 조건을 대조해 한정 재사용하고 다른 G의 미완료를 유지한다.

## 판단과 경계

phase.json의 새 smoke/helper·corpus/scholarly와 manifest·필요 최소 corpus 검사/reader·지침·캐시와 대응 미러만 수정한다. 제품 runtime/probe_cli/기존 공급자 smoke·scholarly 서버/registry·설정/설치·공용 문서·engine·원보고는 수정하지 않는다. runtime 또는 외부 서비스 수리가 필요하면 재현 입력·기대/실제·정확 후속 범위를 반환한다. 실제 서버 list_sources와 Codex 최소 실호출 및 자기 workspace 쓰기는 G7 범위에서 허용된다. 기존 연구·예약·다른 계정/서비스 변경, 권한 상승, Git stage/commit/reset/checkout/push·graphify 갱신은 하지 않는다. L01 운전 프로필·출력 단위 선택이나 전체 G 완료를 이 task가 결정하지 않는다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식 정본/미러 run_tests.py를 -u -B, 정확 선택, --jobs 1 --output <자기 evidence의 새 폴더>로 한 묶음씩 실행한다. --tier T5 --list는 discovery만 확인한다. 실제 실행/실호출/PID/시각/exit·요청/worker/native stdout/stderr·종료·원자료 SHA를 남긴다. 진행 중 result.json은 기존 read_bytes_shared로 읽는다. 실환경 검사를 못 하면 해당 A와 정확 외부 조건을 보고하고 독립 오프라인 작업은 완결한다. 시간은 소프트 기준이며 자동 timeout을 추가하지 않는다.

마지막 python -B services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 014 scholarly-smoke를 통과하고 report 경로/상태를 반환한다. T4 별도 adapter 보고·나머지 문서/의미 질문·L01·G4~G6/G8 및 최종 review는 후속 manager 책임이다.
''')

text(O/'review.md','''# phase 013 manager 검수

report를 전문으로 읽고 check.py report를 통과시킨 뒤 현재2674파일과 task 종료 해시,012 manager와 시작2658파일,허용22변경을 대조했다. 최종 live1·정본33·미러33 고유선택/row/실제exit0와 각각871 Python SHA가 일치한다. 초기3error와 당시 helper 차이는 역사 실패로 유지한다. 공식 --check1322파일을 재확인했고 skill-only 원출력/exit0를 확인했다.

각 성공 smoke의26명령 stdout/stderr SHA·명령 영수증·관찰 JSON,291 snapshot 파일·현재 정본/미러 원문, 정확 action/인자·사용자 principal·operator interval/limit와engine무제한을 확인했다. HOLD는 check/engine_start_guard에서 상태 읽기와 모델 호출 전에 반환한다. 별도 pythonw freeze/held stdout을 OS stdout으로 바꾸어 해석하지 않았다. 미실행267011에서 새 ticks/Ready/0으로의 전이와 wake의 one-shot XML/WakeKey·start 요청 부재를 대조했고 cancel/uninstall·마지막세null·자기프로세스부재·HOLD/빈repository·engine/recovery 미생성도 확인했다. live02/03 실패의 정리 결과를 확인했다. 새 실예약은 manager가 수행하지 않았다.

보고서 F2/narrative의 포괄적 PID 미관측은 정정한다. live-final의 await-wake 원출력에는 PID9492/parent1604·pythonw·정확 live bootstrap/workspace 명령이 2026-10-13T20:11:26.7176738Z에 기록돼 있다. 최종 canonical-related/mirror-related에는 PID 관측이 없다. 이 단일 관측을 모든 역할/실행의 PID 증명으로 확대하지 않는다. 서비스시각/관찰자 차이는 live-final -33/-40/-15초, canonical +2/-5/-41초, mirror -12/-19/+8초다. 원인은 미확인이다. 시각 차이를 수정하거나 정확 지연 보증으로 쓰지 않고 같은 새 작업의 전후 ticks·종료/소유/트리거로 발화를 판정한다. Operational로그 disabled와 OSstdout 미관측은 유지한다. 원task report는 불변이다.

기존19항목/verdict와110비manifest경로를 보존했다. 새2 status 원바이트는 원smoke 명령/출력·manifest/당시값과 같고 실제 PowerShellScheduler JSON 수신을 재생했다. 양쪽 각21항목/62파일의124경로 Git raw/clean·미러바이트·명시SHA가 일치한다. runtime124·공급자3·host4·Lean4입력과host8원자료·실행 파일 조건의 불변은 승인 성질의 재사용 근거다. 과거 0dd16a5e/a0e6c2f4의 좁은 예약 포트/freeze slice만 유지하며 원raw보고 위치 미확인과 다른hunk 미종결을 보존한다.

A1~A4와 F1~F4의 지정 성과를 승인한다. G4~G6/G8·학술/T4보고·읽기조건·나머지 의미/문서 의무는 미완료다. 다음014 단일 work는 기존 Codex/worker에서 scholarly list_sources 성공 완료/결과를 검사한다. probe_cli는 시작 도구명만 확인하므로 그대로 성공 근거로 삼지 않는다. 서버 계약·native 완료·격리·녹화/반례·오프라인 미러를 한 task가 소유한다. 제품 runtime/서비스 수리는 별도 반환 책임이다.

공용 문서는 C2/C5/C8/C9/C10/C11/C12의 현재 결과/한계/다음 책임만 갱신했다. G1~G8과 L01 외부결정, 기존 역사 근거·미해결 의무는 유지한다. common-docs.diff가 변경 전후 의미 대조다. seams는 새 제품 계약 없이014 소비 경계를 설명했다.20제품경로와 선별 원근거/원바이트 archive·다음 배정·기억을 관리 마감하며 캐시와 무관 변경은 제외한다.
''')
ev=['run:phases/013/manager-evidence/verification.json','run:phases/013/manager-evidence/review.md']
dispositions=[
 {'item':'013/scheduler-smoke/F1','action':'resolve','destination':['run:context.md#C11','run:plan.md'],'reason':'원명령/OS 상태/소유·정리와 현재 코드·양쪽33회귀로 held 예약 범위를 승인한다. 연구 운전과 다른 G7 성공으로 확대하지 않는다.','evidence':ev},
 {'item':'013/scheduler-smoke/F2','action':'resolve','destination':['run:context.md#C11'],'reason':'시계 차이 원인 미확인·OS stdout/Operational로그 한계를 유지하고 동일 task의 새ticks/종료로 판정한다. live-final wake PID9492 원관측을 확인했으므로 포괄적 PID미관측은 최종 related 두 실행에 한정해 정정한다. 원report는 보존한다. 원인조사/로그정책변경은 이 설치/OS 합격의 선행조건이 아니다.','evidence':ev+['run:phases/013/tasks/scheduler-smoke/evidence/live-final-observation.json']},
 {'item':'013/scheduler-smoke/F3','action':'resolve','destination':['run:context.md#C9'],'reason':'0dd16a5e/a0e6c2f4의 포트·freeze 해당diff/현재 소비자·회귀에 근거한 유지 판단을 승인한다. raw역사report 미확인·다른hunk/PR02 미종결을 보존한다.','evidence':ev+['run:phases/013/tasks/scheduler-smoke/evidence/history-port.stdout','run:phases/013/tasks/scheduler-smoke/evidence/history-freeze.stdout']},
 {'item':'013/scheduler-smoke/F4','action':'resolve','destination':['run:context.md#C12','run:plan.md'],'reason':'2674현재소스·22허용변경·runtime/기존입력·110비manifest 및124 corpus 경로를 대조해 한정 재사용과20제품경로 마감을 승인한다. 최종전체관문은 유지하고 학술 실제 완료응답을014에 배정한다.','evidence':ev+['run:phases/014/tasks/scholarly-smoke/objective.md']}]
reasons={'C2':'013 판본/회귀/OS검수 결과와 PID 표현 정정을 추가했다.','C5':'013 종료 뒤014의 공유 corpus/검사/실호출 자원과 단일 소유를 지정했다.','C8':'사용자 지정 task 모델을014에 유지하고 제품 호출 기본과 구별했다.','C9':'예약 포트/freeze의 좁은 역사 slice 유지와 미확인 한계를 추가했다.','C10':'L01 외부결정을 유지하고 독립013 완료/014 진행으로 현재화했다.','C11':'배정 상태를 검수된 예약 성질·시계/PID 한계로 교체하고 학술 성공 완료 검사 공백과014 책임을 명시했다.','C12':'원바이트/입력 불변·corpus/회귀와 관리 마감·보존 한계를 추가했다.'}
save(RUN/'phases/013/manager.pending.json',{'next':'014','decision':'scheduler-smoke의 A1~A4 complete를 지정 범위에서 승인한다. report 형식 검사와 실제 파일/원출력 검산으로 현재2674소스·허용22변경·최종정본/미러각33passed 및 실제 새예약/발화/정리·원녹화를 확인했다. 초기3error는 역사 실패다. live-final wake PID9492 원자료를 확인해 F2의 포괄적 PID미관측 표현만 정정하며 시계차이 원인 미확인·OS stdout 한계는 유지한다. 제품 코드/계약은 수정하지 않았다. 전체 G1~G8은 미완료이고 직전 phase도 work여서 종료할 수 없다.014는 기존 실제 Codex/학술 서버의 list_sources 성공 완료·목록·격리·녹화/재생을 담당한다. 시작 사건만 검사하는 probe_cli 한계를 task 입력에 명시했다. 공유 manifest/검사/캐시와 공급자 호출을 한 task로 순차 소유하며 이 단계의 종료에 기여하지 않는 병렬 분석은 추가하지 않는다. 기존 외부결정 L01과 다른 문서/의미 질문·T4/최종관문은 유지한다. 검수된20제품경로·관리자료·기억을 정확히 커밋하고 push하지 않는다.','reports':[{'task':'scheduler-smoke','state':'read','detail':'전문과 A1~A4/F1~F4를 읽고 report 검사를 통과했다. 원명령26개씩·snapshot291·OS전이/정리·현재해시/행/exit·corpus를 대조해 complete를 승인한다. PID 표현의 좁은 정정은 원보고를 고치지 않고 관리 판단에 남겼다.','evidence':['run:phases/013/tasks/scheduler-smoke/report.json','run:phases/013/manager-evidence/report-check.json']+ev}],'dispositions':dispositions,'context_updates':[{'item':cid,'action':'amend','destination':['run:context.md#'+cid],'reason':reason,'evidence':ev+['run:phases/013/manager-evidence/common-docs.diff']} for cid,reason in reasons.items()],'plan_update':'013 예약의 지정 남김을 검수 완료로 바꾸고014 scholarly-smoke를 배정했다. 성공완료응답/실제목록·격리·녹화/관련오프라인/미러의 A1~A4를 명시했다. 제품 runtime/서비스 수리는 별도 반환 책임이다.012 마감 a8fb1e41와013 제품20경로 마감을 연결하고 최종 G/L01·T4/문서/의미 질문을 유지한다.','seam_updates':[],'completion':None})
print('Prepared shared state, 014 scholarly-smoke and 013 manager.pending.json')
