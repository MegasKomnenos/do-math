"""Prepare the next independent work assignments and the current manager decision."""
import difflib
import json
from pathlib import Path

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8',newline='\n')
def dump(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
before={n:(RUN/n).read_text(encoding='utf-8-sig') for n in ('context.md','plan.md','seams.md')}
v=read(O/'verification.json')
assert v['current_matches_task'] and len(v['changes'])==16
c=before['context.md']
def append_section(text,cid,paragraph):
    start=text.index('## '+cid+' '); end=text.find('\n## C',start+1)
    if end<0: end=len(text)
    return text[:end].rstrip()+'\n\n'+paragraph+'\n\n'+text[end:].lstrip()
c=append_section(c,'C2','phase 015 t4-adapter-report는 A1~A3 pass·A4 fail의 partial로 검수했다. report 검사 뒤 task 시작2667·종료2671파일과 현재 전건 일치, 허용16변경을 확인했다. 시작 모집단은014 inspected2750 중 skills/diff 부분이며 서로 다른 모집단의 숫자를 혼합하지 않는다. 최종 관련 정본/미러 각70선택·70passed·exit0와 각875 Python, 최종 T4 각295선택·고유row·283passed/6error/4failed/2skipped·exit1 및 소스 전후를 대조했다. 양쪽 각60worker의 실제 요청·판본·게시 SHA·branch DB, adapter5개의 원합집합 재분석을 확인했다. 측정 complete=true와 정본102/142·미러101/142 정보 도달은 기능 합격이 아니다. 근거는 run:phases/015/manager-evidence/verification.json·review.md다. 초기 실패와 정확 남김은 C11에 유지하며 G 전체 완료가 아니다.')
start=c.index('phase 001~014의 task 세션은 종료됐고014 학술 최소 연결을 검수했다.')
end=c.index('\n\ndo-math 시험 프로세스는',start)
c=c[:start]+'''phase 001~015의 task 세션은 종료됐고015의 T4 측정 성과와 기능 미충족을 구별해 검수했다.016은 t4-fixture-repair와 provenance-baseline 두 독립 work다. 전자는 지정 fixture·OS 오류의 재현/수리·관련 검사·미러/비용 캐시를 단독 소유한다. 후자는 불변 Git 객체와015 원자료, 쓰기 대상이 아닌 shared-input 시험 정의만 읽어 자기 evidence에 과거 비교 트리/manifest를 준비한다. 후자는 제품 import·시험·미러·공유 캐시/설치·Git index 쓰기를 하지 않으며 전자의 작업 중 판본이나 결과를 기다리지 않는다. 실제 시험은 전자만 한 묶음씩 jobs1, 총worker3 이하로 수행한다. 두 산출물의 실제 연결과 양쪽 전체 T4는 다음 manager가 검수 뒤 순차 배정한다. 새 유료 공급자·예약 변경·학술 검색·기존 연구 운전은 필요하지 않다. 기존 실경계는 불변 입력에서 승인된 성질만 재사용하고 L01 외부 결정과 최종 관문은 유지한다.'''+c[end:]
c=append_section(c,'C8','015의 gpt-6.1-sol/high 수행을 검수했고016의 t4-fixture-repair와 provenance-baseline도 같은 사용자 지정 모델/effort로 배정한다. 후자는 코드 실행 없는 입력 준비이며 전자만 공식 제품 시험을 수행한다. 제품 공급자 실호출 모델을 새로 지정하지 않는다.')
c=append_section(c,'C9','015는b0d90537의 D5 자체 입출력 정지/D6 누락 worker 반려,bbe64043의 비용/공동 passed 소비와f56a2772의 시간 종료 제거를 actual diff·현재 소비 및002 근거와 대조했다. 이 한정 runner/측정 slice의 유지와 T4 보고 추가를 승인한다. 새 _read_json의 측정 전 import와 repo 내부 records.json 자기 의존은 이번 work의 실제 T3 반례로 교정됐고 양쪽70회귀에 기존 incremental/parallel 경계가 포함된다. 전체-T3-2026-10-03.json은 존재하는 역사 요약이고 연결된 raw는 부재라는 한계를 유지한다. 과거 counts를 새 성공에 더하거나 PR01 전체/provenance 검토를 닫지 않는다.015 F3의 두 baseline 비교 입력은016 provenance-baseline이 Git 도입 전후와 P10/P11에 결속해 준비하며 실제 비교는 후속 연결 작업 책임이다. 근거는015 task review.md·history-measurement.diff·history-runner.diff·history-timeout.diff 및 manager 검수다.')
c=c.replace('013 예약과014 학술 최소 연결도 완료했으며015 T4 보고는 이 답변과 독립적으로 진행한다.','013 예약과014 학술 최소 연결도 완료했다.015 T4 측정은 검수됐고016의 fixture/OS 문제와 과거 비교 입력 준비는 이 답변과 독립적으로 진행한다.')
c=c.replace('T4 단독은 Measurement를 만들지 않아 adapter 분기 보고가 없다. 별도 T4 측정 수리를 배정하며 최종 T3 모집단에 T4를 섞어 해결하지 않는다.','phase 001~014 당시 T4 단독은 Measurement를 만들지 않아 adapter 분기 보고가 없었다. 이 공백은015에서 실제 worker 수집/병합으로 해소됐다. 아래의 기능 실패·baseline 부재를 별도로 처리하며 최종 T3 모집단에 T4를 섞지 않는다.')
old='남은 T4 보고의 공백을 현재 run_tests.py에서 재확인했다.'
start=c.index(old); end=c.index('\n\n## C12',start)
c=c[:start]+'''015에서 T4 보고 공백을 해소했다. AdapterMeasurement는 기존 Measurement/coverage·D5 pause를 재사용하고 현 LAYERS adapter5개를 도달0까지 소스 분모로 보고한다. worker 게시와 수신은 같은 validate_publication으로 실행 ID·요청·소스 판본·artifact SHA/branch DB를 검사하며 누락/파손은 incomplete와 exit1이다. 실제 jobs1/jobs2·누락/외부자료·거짓 도달·fail/skip/not_run, T3 합집합 분리와 기존 T3 incremental/parallel 회귀를 검수했다. 각60worker와 최종 양쪽 adapter 원합집합을 독립 재분석했다. 정본102/142와 미러101/142는 각 실제 보고와 일치하는 정보이며 같은 값이나 임계 통과를 요구하지 않는다. branch_gate._stop의 자기 활성 상태/멱등 정지와 _t3_plan의 unmeasured, 설정의 측정 전 제품 import 제거도 지정 회귀로 확인했다. 새 runner/branch_gate는 기존 T3 저장소 무효화 대상이며 최종 fresh G5를 대체할 수 없다.

015의 최종 T4는 양쪽 각각295건 중283passed·6error·4failed·2skipped다. 설치 Lean을 쓰는 formal_consumer4·lean_storage2는 installed_request가 nonempty fingerprint와 empty content를 조합해 record_errors의 모집단 검사에서 반려된다. 보존된 identity를 사용한 측정 없는 fixture 최소 재현도 같은 ValueError이며 제품 검사는 유지한다. RealJobObservation은 선언하지 않은 ok를 닫힌 object schema로 반환하고, WriterLock child는 ResearchRepository의 필수 backend를 누락해 TypeError, archive preview child는 ports/env 부재로 NameError다.016 t4-fixture-repair가 현재 공개 producer/전송/포트 계약에 fixture를 맞추고 정확 실패 ID와 관련 검사를 확인한다. 약한 기대값·구형 fallback·대역으로 실제 compiler/Job/저장 경로를 가리지 않는다.

SharedInputProvenanceTests의 두 exact-baseline 시험은 SHARED_INPUT_BASELINE_SCRIPTS가 없어 skip됐다. P10/P11의 literal entry/open/import-open/coverage 보존과 명시 marker 차이·두 worker raw union은 미검사다.016 provenance-baseline은 실제 도입 diff/원보고와 연결되는 별도 pre-fix scripts 트리를 자기 evidence에 Git 바이트로 준비한다. 현재 트리를 과거 기준으로 복제하거나 과거 요약 counts를 실행 증거로 사용하지 않는다. 수리 task와 독립인 정적 입력 준비이며 두 비교의 공식 실행과 전체 T4는 두 결과 검수 뒤 후속 연결 작업에 배정한다.

OS 관측도 미해결로 유지한다. 첫 정본 전건의 bootstrap freeze staging.rename WinError5는 최종 양쪽 동일 ID에서 통과했으나 원인이나 transient 여부는 미확인이다. real_git_descendants는 첫 정본에서 통과하고 최종 정본·미러에서는 store.publish/update-ref가 stdin handle을 DuplicateHandle하는 중 WinError6으로 실패했다. 현재 probe는 같은 pythonw에서 AttachConsole/FreeConsole 뒤 저장을 수행한다는 코드 사실을 확인했으나 인과는 아직 가설이다.016 t4-fixture-repair가 정확 ID·child/OS handle 조건·정상 대조로 판별하며 제품 수리가 쓰기 범위를 넘으면 최소 반례를 반환한다. 이전 failed/error를 소급 pass로 바꾸지 않는다. 근거는015 manager verification.json·review.md 및 task 원report다.13-C/L01·다른 문서/의미 질문과 G4~G6/G8 최종 관문은 남는다.'''+c[end:]
c=append_section(c,'C12','015 F5의 보존 사실을 검수했다. runtime 포함139입력·corpus144경로·host8원자료·도구 SHA와 index/pseudo 목록은 불변이며 전144경로 Git raw/clean을 확인했다. 공식 --check1336과 skill-only 및 양쪽70회귀를 승인된 성질로 유지한다.015의12개 제품/시험/지침/미러 경로(16변경 중 비용캐시4 제외)는 전체 T4 실패/skip 해소와 연결 검수 뒤 커밋하도록 대기한다. 이번 관리 커밋에는 공용 인계·선별 원근거·기억만 담고 현재12제품 원바이트와 task 원자료를 raw-evidence.zip에 보존한다. 추적 범위/항목 SHA는 run:phases/015/manager-evidence/preservation.json에, stage/commit 행정 수신은 로컬 commit.json에 둔다. 압축으로만 추적되는 scratch 원경로와 행정 수신은 정리로 사라질 수 있으며 압축은 자동 복원 지시가 아니다.016 배정은 기존 성공을 전체 G 합격으로 바꾸지 않는다.')
assert c.split('## C2 ')[0]==before['context.md'].split('## C2 ')[0]
write(RUN/'context.md',c)

p=before['plan.md'].replace('## phase 001~014의 결과와 현재 상태','## phase 001~015의 결과와 현재 상태',1)
p=p.replace('최종 전체 관문은 아직 실행하지 않았다. 현재 상태의 근거는', '015는 T4 측정·양쪽70회귀를 검수한 partial이다. 최종 T4 각295건의283통과·6오류·4실패·2skip은 미해결이며 측정 complete와 구별한다. 최종 전체 관문은 아직 실행하지 않았다. 현재 상태의 근거는',1)
start=p.index('## 다음 phase: 015'); end=p.index('## 가까운 후속 배정과 선행 관계',start)
p=p[:start]+'''## 다음 phase: 016

gpt-6.1-sol/high의 독립 work 두 개를 배정한다. t4-fixture-repair는015 F2/F6의 현 계약과 다른 fixture 네 경로 및 pythonw/Git 핸들 관측을 재현·수리한다. 설치 baseline 내용/지문, Codex 의미/전송 schema, 필수 backend와 archive child의 실포트/환경을 현재 정본에 맞추고 기존 정확 단언·실제 compiler/Job/저장을 유지한다. OS 오류는 정상 대조와 실제 handle 상태로 원인을 판별하며 bootstrap WinError5의 후속 통과를 원인 규명으로 읽지 않는다. 정확 실패 ID와 한정 관련 회귀, 공식 미러·캐시를 이 task만 소유한다.

provenance-baseline은015 F3의 P10/P11 두 skip에 필요한 pre-provenance-fix scripts 트리를 Git 이력과 원보고에 결속해 자기 evidence에 준비한다. 제품·시험 소스를 수정하거나 import/실행하지 않고 불변 Git 객체,015 보존 원자료와 상대가 쓰지 않는 shared-input 시험만 읽는다. 비교 트리의 Git blob·SHA·파일 모집단과 선택 이유, 후속 SHARED_INPUT_BASELINE_SCRIPTS 명령을 넘긴다. 입력 준비 완료를 비교 성공으로 보고하지 않는다.

전자는 유일한 공식 시험 실행자이며 jobs1·전체worker3 이하·한 묶음씩 수행한다. 후자는 공유 미러/캐시/DB/포트/설치/Git index를 건드리지 않는다. 서로의 미완성 산출물을 사용하거나 기다리지 않으므로 같은 phase에 배정한다. 전체 T4는 과거 비교 입력까지 준비된 뒤 후속 단일 연결 작업에서 정본·미러 각각 완결한다.015의12제품 경로는 그 검수까지 미커밋으로 두되 원바이트를 관리 archive에 보존한다. 새 S 계약은 없으며 두 objective가 실제 후속 책임과 준비 한계를 정한다.

L01 Q1/Q2의 운전 프로필·출력 단위 결정은 계속 남는다. 답변 전에는 원문 byte 기준과 미충족 판정을 유지하고016의 독립 작업을 진행한다.

'''+p[end:]
p=p.replace('014 학술 최소 연결을 검수했고 제품32경로를 마감하며015 T4 보고로 진행한다. 근거는014 manager-evidence/verification.json·review.md다.', '014 학술 제품32경로는 eb701074로 마감됐다.015 T4 측정과70회귀는 검수했으나 기능/입력/OS 남김을016으로 넘긴다.015 제품12경로는 후속 전체 T4 연결 검수까지 대기한다. 근거는015 manager-evidence/verification.json·review.md다.')
p=p.replace('| G7 T4 adapter 보고 | 015에서 T4 단독 전체 boundary 선택·격리 worker를 측정하고 현 adapter 전체의 분기 보고와 누락 처리를 완결한다. | 설계5.5상 보고이며 통과 임계 관문으로 바꾸지 않는다. 최종 T3 선택과 분리한다. |', '''| G7 T4 adapter 보고 | 015의 실제 측정/게시/병합과 현 adapter 전체 정보 보고를 검수했다. 각60worker·원DB 재분석과 양쪽70회귀를 유지한다. | 도달률은 임계 관문이 아니다. T4 기능 실패/skip 및 G5 fresh 최종 판본은 별개다. |
| G1/G3/G7 T4 fixture·OS 실패 | 016 t4-fixture-repair가 정확 오류6·실패4의 입력/OS 원인을 다루고 관련 정본/미러 회귀를 확인한다. | runtime/설치 신뢰 검사를 낮추지 않는다. OS 원인 미확인·초기 bootstrap 실패도 후속 상태를 명시한다. |
| G2/G3/G7 P10/P11 비교 입력 | 016 provenance-baseline이 불변 Git 이력에 결속된 별도 scripts 트리·manifest를 준비한다. | 같은 phase에는 시험/제품 import를 하지 않는다. 준비 완료는 두 exact-baseline 성질의 통과가 아니다. |
| G7 T4 실제 연결과015 제품 마감 | 016 두 결과가 준비되면 후속 단일 work가 정확 baseline 두 비교와 양쪽 전체 T4를 실행하고 선택/row/exit·각 worker·소스/미러를 대조한다. | 부분 회귀의 합산은 전체 성공이 아니다. 별도 입력을 현재 root로 위장하거나 skip을 pass로 세지 않는다. |''')
write(RUN/'plan.md',p)
seam=before['seams.md'].rstrip()+'''\n\n015의 T4 보고 정의는 tests/support/adapter_coverage.py의 AdapterMeasurement·validate_publication과 run_tests의 실제 소비가 정본이다. manager는 실제 worker 자료와 양쪽70회귀를 검수했고 T3 의미는 유지했다.016 t4-fixture-repair는 기존 trust_inventory/ModelRunner/ResearchRepository/formal/실포트 계약의 fixture 소비만 고친다. provenance-baseline은 Git 원바이트 입력을 자기 evidence에 준비하며 같은 phase의 다른 task와 제공/소비하지 않는다. SHARED_INPUT_BASELINE_SCRIPTS의 실제 소비는 기존 test_shared_input_provenance.py가 정의하고 후속 연결 task가 맡는다. 제품 인터페이스 개정이나 병렬 제공자/소비자 분리가 없어 S 항목과 provides/uses는 추가하지 않는다.\n'''
write(RUN/'seams.md',seam)
diff=''.join(''.join(difflib.unified_diff(before[n].splitlines(True),(RUN/n).read_text(encoding='utf-8').splitlines(True),fromfile=n+' before',tofile=n+' after')) for n in before)
write(O/'common-docs.diff',diff)

N=RUN/'phases/016'
assert not (N/'phase.json').exists()
common=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:phases/015/tasks/t4-adapter-report/report.json','run:phases/015/manager-evidence/verification.json','run:phases/015/manager-evidence/review.md','run:phases/015/manager-evidence/source-inspected.json','repo:.claude/skills/do-math/AGENTS.md','repo:docs/do-math/시험-재편-2026-09-29/설계.md']
files=['tests/support/knowledge_roundtrip.py','tests/support/knowledge_installed_lean.py','tests/support/trust_inputs.py',
       'tests/boundary/test_knowledge_formal_consumer.py','tests/boundary/test_knowledge_lean_storage.py',
       'tests/boundary/test_observation_real_job.py','tests/boundary/test_scheduling_host_processes.py',
       'tests/boundary/test_scheduling_background_processes.py','tests/boundary/test_submission_lean_preview.py',
       'tests/boundary/test_operator_bootstrap_info.py','tests/.timings.json','tests/.timings-t3.json']
prefix='repo:.claude/skills/do-math/scripts/'
repair_inputs=common+['run:phases/015/tasks/t4-adapter-report/evidence/fixture-reproduction.json','run:phases/015/tasks/t4-adapter-report/evidence/review.md','run:phases/010/tasks/host-smoke/report.json','run:phases/011/tasks/regression-reading/report.json','run:phases/012/tasks/lean-smoke/report.json','repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']+[prefix+p for p in files if '/.timings' not in p]+[prefix+p for p in ['이음새-정본.md','tests/시험-지침.md','do_math/trust_inventory.py','do_math/provider_final.py','do_math/repository.py','do_math/formal.py','do_math/git_process.py']]
baseline_inputs=common+['run:phases/001/tasks/closure-map/evidence/prior-review-state.json','run:phases/001/tasks/closure-map/evidence/requirement-state.json','run:phases/015/tasks/t4-adapter-report/evidence/history-original-observation.json','run:phases/015/tasks/t4-adapter-report/evidence/review.md',prefix+'tests/boundary/test_shared_input_provenance.py',prefix+'tests/support/branch_gate.py',prefix+'tests/support/t3_store.py']
dump(N/'phase.json',{'kind':'work','purpose':'015의 측정 성과를 보존하며 T4 기능 실패의 fixture/OS 수리와 P10/P11 과거 비교 입력 준비를 독립 수행한다. 전체 T4 연결은 두 결과 검수 뒤 배정한다.',
    'tasks':[{'id':'t4-fixture-repair','model':'gpt-6.1-sol','effort':'high','inputs':repair_inputs,
              'writes':[tree+'/skills/do-math/scripts/'+p for tree in ('.claude','.agents') for p in files],'provides':[],'uses':[]},
             {'id':'provenance-baseline','model':'gpt-6.1-sol','effort':'high','inputs':baseline_inputs,'writes':[],'provides':[],'uses':[]}]})
write(N/'tasks/t4-fixture-repair/objective.md','''## 목적과 역할

015는 T4 측정을 구현했으나 양쪽295건에서6error·4failed·2skip이 남았다. 이 task는 G1/G3/G7의 정확6error·4failed를 현 계약에 맞는 fixture와 실제 OS 관측으로 해결한다.015의 runner/측정 성과는 유지한다. 병렬 provenance-baseline은 과거 비교 입력만 준비하며 그 산출물을 이 task에서 읽거나 기다리지 않는다. 전체 T4와 두 skip 비교는 후속 연결 task 책임이다.

## 완료 조건

### A1 시작 판본과 반례의 실제 원인

015 manager source-inspected와 시작 소스를 대조하고 verification.suites의 정확 ID/원trace를 읽는다. formal_consumer4·lean_storage2는 installed_request의 nonempty fingerprint/empty content, observation_real_job은 미선언 ok/닫힌 schema, WriterLock child는 backend 부재, archive preview child는 ports/env 부재다. 현재 공개 정의와 fixture 입력에서 각각 확인하고 기존 원red가 현재 소스와 같으면 재사용한다. 불명확하거나 새 음성 단언이 필요할 때만 최소 red를 수행한다. 소스·원보고·실행 관측과 추론을 구별한다. 해당 fixture/콘솔 도입 Git diff와 기존010~012 검수의 관련 slice만 대조해 유지/교정 범위를 정한다. PR 전체나 사라진 원보고 counts를 새로 승인하지 않는다.

### A2 현재 계약의 fixture 수리와 정확 성공

installed_request의 기록은 실제 identity의 fingerprint/content 모집단 및 원바이트 의미에 맞는 현재 producer로 만든다. 신뢰 승인·설치 기록을 바꾸거나 content 검사를 무력화하지 않는다. 이미 있는 support/trust_inputs·knowledge_installed_lean의 정본을 재사용하고 의미가 같은 규칙을 복제하지 않는다. 합성 부분과 실제 compiler/저장/authoritative consumer 경계를 명시한다. observation fixture는 원 의미 schema와 현재 Codex 전송/수신을 함께 맞추며 실제 Job 종료·지연 batch 적용과 ok=true 단언을 유지한다. WriterLock의 자식도 현재 필수 backend를 전달해 실제 lock 경쟁과 해제 후 획득을 검사한다. zip preview 자식은 필요한 실포트/환경을 자기 프로세스에서 구성해 실제 archive formal의 동일 checker bytes와 errors=[]를 검증한다. TypeError/NameError나 failed 상태를 정상 기대값으로 바꾸지 않는다.

정확9개 fixture 오류/실패가 새 공식 row에서 passed여야 한다. 해당 기존 시험의 결과/근거/현재성·바이트·identity·실제 Job/컴파일 단언을 보존한다. 쓰기 범위 안에서 필요한 최소 보강만 허용한다. 제품 runtime 변경이 필요한 반례는 별도로 반환하고 해당 A를 통과로 만들지 않는다.

### A3 Windows 관측의 원인 판별과 재검증

015 F6의 real_git_descendants는 첫 정본에서 passed, 최종 양쪽에서 store.publish/update-ref의 stdin DuplicateHandle WinError6이었다. 현재 같은 pythonw probe가 AttachConsole/FreeConsole 뒤 저장하는 순서가 있지만 원인은 아직 가설이다. 정확 ID의 child stdout/stderr·핸들 관측과 정상 대조를 보존하고 실제 제품 실패인지 시험 관찰자의 부수 효과인지 판별한다. 관측을 별도 자기 child로 분리하거나 명시 I/O를 쓰는 수리는 계약/원인 근거가 있을 때만 수행한다. 실제 Git/자손·양성 console 대조·visible window 없음·binary 저장 성질을 대역이나 무조건 retry/skip으로 가리지 않는다. 원인이 범위 안이면 수리 후 정확 ID를 검증하고 원인이 runtime에 있으면 최소 재현·필요 파일·기대/실제를 반환한다.

bootstrap-info의 첫 WinError5와 최종 양쪽 passed를 구별한다. 지정 관련 묶음에서 두 bootstrap-info ID와 실제 freeze/원설치·manifest·반려를 확인한다. 관측 결과가 통과하면 새 근거의 범위만 인정하며 과거 원인 규명을 주장하지 않는다. 재현되는 결함이면 범위 안 수리 또는 정확 후속 조치로 보고한다.

### A4 지정 회귀·미러·보존 인계

정본과 공식 미러에서 다음 모듈의 실제 선택/고유row/exit·소스 전후를 확인한다: boundary.test_knowledge_formal_consumer, boundary.test_knowledge_lean_storage, boundary.test_observation_real_job, boundary.test_scheduling_host_processes, boundary.test_scheduling_background_processes, boundary.test_submission_lean_preview, boundary.test_operator_bootstrap_info. support fixture를 직접 검증하는 기존 unit.test_trust_environment, unit.test_knowledge_storage_roundtrip 및 structure.test_test_smells를 포함한다. 단순 참조 검색 전체를 새 실행 범위로 만들지 않는다. 바뀐 fixture의 추가 직접 소비자는 AST/정의·import를 확인하고 새 구체적 위험이 있을 때 정확 ID만 추가한다. 같은 소스의 이미 성공한 관련 묶음을 이유 없이 반복하지 않는다.

공식 미러 생성 전 예상 변경을 writes와 대조하고 정본/미러의 지정 회귀 뒤 비용 캐시만 동기화해 --check와 skill-only를 확인한다. runtime·015 runner/측정·공급자/host/Lean/예약/학술 입력·corpus 원바이트의 보존과 기존 실호출 재사용 한계를 기록한다.015의12제품 원바이트 archive와 현재 변경을 구별하고 Git 마감은 manager에 맡긴다. P10/P11 두 비교와 정본/미러 전체 T4, 전체 일반/fresh T3/변이·최종 review는 수행하지 않았음을 명시하고 후속 연결 책임을 넘긴다.

## 판단과 경계

phase.json의 정확 fixture/경계 시험·비용 캐시와 공식 대응 미러만 수정한다. 필요한 helper의 내부 구현은 현재 공개 검사를 만족하는 범위에서 재량이다. runtime·runner·측정·corpus·설치 신뢰 기록·제품 요구·서비스·공용 문서·다른 task 자료·과거 보고는 변경하지 않는다. 실제 compiler/Job/Git·시험 전용 새 workspace와 임시 프로세스는 사용할 수 있다. 유료 공급자·실예약 변경·학술 검색·기존 연구 재개·권한 상승·graphify·Git stage/commit/reset/checkout/push는 하지 않는다. 과거 baseline task는 시험/제품 import를 하지 않으므로 이 task가 공식 시험/미러/캐시의 유일한 소유자다.

## 검증 방법

cwd C:\\math. Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식 정본/미러 scripts/run_tests.py를 -u -B, 정확 ID/모듈, --jobs 1, --output <자기 evidence 새 폴더>로 사용한다. T4 측정도 확인할 때 boundary 선택에 --tier T4를 붙이고 unit/structure는 별도 명령으로 실행한다. 총 worker3 이하, 한 묶음씩, 실행 중 제품/시험 소스 고정. command/PID/시작/종료/exit·전후 SHA와 원보고/실제 child 관측을 보존한다. 진행 result는 read_bytes_shared로 읽으며 대기 도구 yield나 시간 경과로 실패/성공을 만들지 않는다. 실패는 원인 확인 후 필요한 경우만 재실행한다. 마지막 check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 016 t4-fixture-repair를 통과하고 report 경로/상태를 반환한다.
''')
write(N/'tasks/provenance-baseline/objective.md','''## 목적과 역할

G2/G3/G7의 P10/P11 두 exact-baseline 비교는 별도 pre-provenance-fix scripts 입력이 없어015에서 skip됐다. 이 task는 비교에 쓸 실제 과거 판본을 Git 원본과 원문 요구에 결속해 자기 evidence에 준비하는 한정 조사/입력 구축이다. 제품 실행이나 비교 통과를 맡지 않는다. 병렬 fixture 수리와 독립적으로 Git 불변 객체/015 원자료와 상대 쓰기 범위 밖의 shared-input 시험만 읽고 후속 연결 task가 사용할 입력을 반환한다.

## 완료 조건

### A1 비교 성질과 역사 판본 확정

test_shared_input_provenance.py의 assert_baseline_capture·두 exact_baseline 시험과 PROBE/SNAPSHOT/WORKER/merge를 읽고 보존할 ordinary outcome/read 횟수, literal entered/open/import_open·coverage의 파일/context/행/arc, 명시 marker 차이 및 두 worker 합집합을 설명한다. prior-review-state의 PR01 관련 slice와 requirement-state의 P10/P11 원문 경로, Git log/show의 도입 diff 및 존재 원보고를 따라 pre-fix 후보 commit을 확정한다. 단순히 현재보다 오래된 커밋이나 다른 디렉터리라는 이유로 baseline을 정하지 않는다. 고친 provenance 동작의 도입 직전 실제 API를 갖추는지 source로 대조하고 없어진 원보고의 위치/한계를 기록한다. 필요한 입력 판본을 해소할 수 없으면 blocked/partial과 정확 원인을 보고한다.

### A2 별도 과거 scripts 트리와 바이트 검증

선택한 불변 Git commit의 scripts 파일을 자기 evidence 아래 새 pre-provenance/scripts에 추출한다. checkout/reset/worktree·현재 제품 파일의 과거 교체는 하지 않는다. git ls-tree/show/cat-file/archive 등 읽기만 사용하며 저장소 밖 절대 경로/..·symlink 재분석 이탈을 허용하지 않는다. 전건 파일 경로·Git blob·SHA256·추출 명령/선택 commit과 도입 commit을 manifest로 기록하고 실제 추출 bytes를 Git 객체와 대조한다. 비교에 필요한 support/runner/제품 import 의존 파일은 원래 트리 그대로 포함하며 현재 파일을 섞거나 옛 코드를 현재 API에 맞게 고치지 않는다. 현재 root나 현재 사본을 pre-fix라고 이름만 바꾸지 않는다. 과거 연구 인스턴스·삭제된 사용자 자료를 복원하는 작업이 아니다.

tree가 현재 SCRIPTS와 다른 절대 경로이고 필수 run_tests.py·tests/support/branch_gate.py·t3_store.py 등 시험 소비 파일이 존재함을 검사한다. 정적 AST/텍스트/파일 해시 검사는 가능하지만 현재/과거 제품 import·시험 실행은 하지 않는다. tree와 manifest를 자기 evidence에 보존하며 원자료를 재작성하지 않는다.

### A3 실제 비교의 후속 책임과 실행 입력 인계

후속 연결 task가 설정할 SHARED_INPUT_BASELINE_SCRIPTS의 절대 경로, 정본/미러 공식 runner의 두 정확 ID 명령, 기대되는 skip0·실제 old/new 관측과 소스/도구 판본 기록 방법을 review.md에 준다. 코드에서 확인된 API 차이·비교 실패 가능성은 사실/가정으로 구별한다. 정상 도달이나 비교 성공은 실행 전에는 주장하지 않는다. 현재015 원자료의 skip·역사 raw 부재와 최종 G2/G7 미충족을 그대로 유지한다. 선택한 역사 입력이 정책상 제외되거나 바뀌어야 한다는 결론이면 원문·위임 근거와 상실되는 성질을 명시하고 임의로 skip을 승인하지 않는다.

## 판단과 경계

writes는 빈 목록이다. 자기 report/evidence의 트리·manifest·조사 자료만 만든다. 제품/시험·공용 context/plan/seams·다른 task/evidence·Git index·미러/캐시/설치·engine·기억을 수정하지 않는다. 상대가 수정하는 현재 fixture나 실행 결과를 읽어 판단하지 않는다. 현재 branch_gate/t3_store/shared-input 정의는 상대 writes 밖이고015 source-inspected와 해시를 대조해 읽을 수 있다. 그 외 현재 제품 의존을 조사할 때는 고정한 Git blob 또는015 보존 자료를 사용한다. 공식 시험·pytest/unittest·제품 import·실제 Job/Lean/예약·유료 호출을 실행하지 않아 공유 시험 자원을 점유하지 않는다. 모델은 사용자 지정 gpt-6.1-sol/high다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. git log/show/ls-tree/cat-file의 실제 argv·exit와 필요한 원출력, 추출 파일의 전건 blob/SHA 대응을 evidence에 기록한다. scripts 트리 파일 목록·선택 commit·현재 비교 대상의 고정 해시를 대조한다. 경계가 불확실하면 파일을 고치지 않고 finding으로 반환한다. 실행 성질은 후속 task의 공식 두 비교와 전체 T4가 확인하므로 이 작업의 완료는 입력 준비 완료다. 마지막 check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 016 provenance-baseline을 통과하고 report 경로/상태를 반환한다.
''')
(N/'logs').mkdir(exist_ok=True)
for tid in ('t4-fixture-repair','provenance-baseline'): (N/'tasks'/tid/'evidence').mkdir(exist_ok=True)

write(O/'review.md','''# Phase 015 manager 검수

t4-adapter-report의 A1~A3 성과와 A4 fail/partial 판정을 승인한다. report 전문과 완료 조건을 읽고 report 검사를 통과한 뒤 현재2671파일을 task 종료와 대조했다. 시작2667파일은014 inspected의 skills/diff 부분과 같고16변경은 report/writes와 일치한다. 서로 다른 모집단2750/2667을 손실로 혼동하지 않는다. G1~G8 문면은 바꾸지 않았다.

관련 정본/미러 각70고유선택·70passed·exit0, 최종 T4 각295고유선택·283passed/6error/4failed/2skipped·exit1과 각875 Python 판본/전후 해시를 확인했다. 최종 --list는 실제 선택과 같다. 두 T4의60worker 각각에 대해 요청/실행 ID·875소스 시작/종료·artifact SHA와 실제 branch DB를 대조했고 부모 원adapter.data를 coverage로 다시 분석해5모듈의 행/분기/제외/소스SHA/합계를 확인했다. 정본102/142·미러101/142는 각 raw와 일치한다. 두 정보 수치를 같게 만들거나 분기 도달 임계 관문으로 바꾸지 않는다.

run_tests diff와 AdapterMeasurement/validate_publication을 읽었다. 실제 측정/병합을 유지하면서 누락·파손·다른 실행·판본을 반려하고 T3 index/store/gate를 T4에 쓰지 않는다. 시험의 실제 worker/Job과 known body 도달, 보고 자체의 거짓 도달 반례 및 incomplete/exit1 관측이70회귀에 포함된다. _stop의 자기 활성 해제/멱등 처리, T3 설정의 import 전 읽기와 _t3_plan pause 교정은 기존 incremental/parallel 실제 회귀에서 확인됐다. 새로운 runner 판본의 최종 전체 일반/fresh T3/전체 변이는 후속이다. 역사 D5/D6/D9/D11의 지정 slice 유지와 원raw 부재는 task 기록 범위로 인정하며 PR01 전체를 종결하지 않는다.

6개 Lean 오류는 installed_request의 지문/내용 모집단 차이를 현재 trust_inventory.record_errors가 반려한 결과다. 보존된 identity의 측정 없는 최소 재현도 같은 ValueError다. real-job fixture의 ok 추가 필드, writer-lock child의 backend 누락, archive child의 ports/env 부재를 현 원문과 실제 trace에서 확인했다. 이9건은 현 fixture 수리가 필요하며 제품 guard/실제 compiler/Job을 약화하는 근거가 아니다.

두 baseline skip은 과거 scripts 입력 부재이며 비교 성질은 미검사다. assert_baseline_capture는 ordinary·literal entries/opens/import opens/coverage와 명시 marker 차이를 비교하고 두 worker의 실제 union도 확인한다. 현재 root와 다른 경로만으로 과거 판본 자격이 생기지 않는다. 별도016 task가 Git 도입 diff·원문에 결속된 원바이트 트리를 준비하고 후속 연결 task가 실제 비교를 수행하도록 분리했다.

real_git_descendants의 최종 양쪽 trace는 store.publish/update-ref가 stdin을 DuplicateHandle하는 중 WinError6임을 확인했다. 같은 probe가 AttachConsole/FreeConsole 뒤 저장한다는 코드 관측은 인과 확정이 아니며016에 대조 재현을 맡긴다. 첫 bootstrap WinError5의 후속 통과도 transient 원인 확정으로 바꾸지 않는다. F6의 정본 중심 서술은 양쪽 실패라는 원row로 구체화하며 원report는 고치지 않는다.

139재사용 입력·144corpus 경로·host8원자료·도구SHA·index/pseudo는 보존됐다. corpus Git raw/clean, 공식 --check1336·skill-only를 다시 확인했다. 새 실호출이나 제품 시험을 manager가 실행하지 않았다.01512제품 경로는 전체 T4 연결 검수까지 커밋을 보류하되 원task 근거와 제품 raw를 archive에 결정화한다. 관리 인계·선별 근거·기억만 커밋한다.

016 t4-fixture-repair가 유일한 제품 편집/공식 시험/미러/캐시 소유자다. provenance-baseline은 불변 Git 객체/고정 원자료·상대 쓰기 밖 정의만 읽고 자기 evidence를 만들며 시험/제품 import를 하지 않는다. 서로의 미완성 산출물을 읽지 않아 독립적이다. 두 결과 검수 뒤 입력을 실제 소비하는 단일 후속 work에서 양쪽 전체 T4를 확인한다. 기존 L01 외부 결정·문서/의미 질문 및 최종 G4~G6/G8을 유지한다. 공용 문서의 추가/갱신 의미와 보존된 조건은 common-docs.diff로 대조했다.
''')
base='run:phases/015/manager-evidence/'
ev=[base+'verification.json',base+'review.md']
manager={'next':'016','decision':'015 report를 형식 검사와 실제 소스/원자료 대조 후 partial로 검수한다. A1~A3의 실제 T4 측정·T3 보존과 양쪽70회귀는 승인하지만 A4의 양쪽295건 중6error/4failed/2skip을 성공으로 만들지 않는다. 측정 complete와 기능 결과를 분리하고16허용변경·각60worker/원DB·139입력/144corpus 보존을 확인했다.016은 현 fixture/OS 실패 수리와 과거 baseline 입력 준비를 독립 배정한다. 전자만 제품 시험/미러/캐시를 사용하고 후자는 Git 불변 객체/고정 자료만 읽으므로 공유 실행 환경의 충돌이 없다. 후속 실제 두 비교와 전체 T4는 두 결과 검수 뒤 단일 연결 작업이 맡는다. manager는 제품을 고치지 않고12제품 raw를 보존하며 관리 인계/기억만 커밋한다. L01·나머지 문서/의미 질문·최종 전체 관문과 review가 남아 개발 완료 조건은 충족하지 않는다.',
         'reports':[{'task':'t4-adapter-report','state':'read','detail':'전문과 A1~A4를 읽고 report PASS. A1~A3 pass와 A4 fail의 partial을 승인한다. source2671·허용16변경, 최종4실행의 선택/row/exit/소스, T4 raw·worker, fixture 원trace 및 보존 조건을 대조했다.','evidence':['run:phases/015/tasks/t4-adapter-report/report.json',base+'report-check.json',*ev]}],
         'dispositions':[],'context_updates':[],
         'plan_update':'015의 실제 측정/지정 회귀를 승인하고 기능 실패·baseline 입력 부재·OS 문제를 각각016의 두 독립 task에 배정했다. 제품 수리/공식 시험 소유와 읽기 전용 역사 입력 준비를 분리해 병렬 가능성을 확보했다. 두 결과 뒤 전체 T4 실제 연결 및015제품 마감을 명시하고 G 기준·일반→fresh T3→전체 변이→review, L01 외부 결정·기존 문서/의미 남김을 보존했다. 공용 편집 전후는 common-docs.diff다.',
         'seam_updates':[],'completion':None}
for fid,action,dest,reason in [
    ('F1','resolve',['run:context.md#C11'],'actual runner/각60worker와 원DB 재분석으로 T4 측정 공백을 닫는다. 기능 실패/skip은 별도 미충족으로 유지한다.'),
    ('F2','carry',['run:context.md#C11','run:phases/016/tasks/t4-fixture-repair/objective.md'],'9건의 fixture 오류/실패를 현 record/schema/backend/실포트 정의와 trace에서 확인했다. 기존 guard/실경로 보존 수리와 정확 회귀를 배정한다.'),
    ('F3','carry',['run:context.md#C11','run:phases/016/tasks/provenance-baseline/objective.md','run:plan.md'],'비교 입력 부재는 정당한 통과가 아니다. Git 이력에 결속된 별도 pre-fix 트리를 준비하고 실제 두 비교/전체 T4는 후속 연결 task가 맡는다.'),
    ('F4','resolve',['run:context.md#C9','run:context.md#C11'],'새 설정의 import 순서와 store bookkeeping을 교정한 diff·기존 incremental/parallel·양쪽70회귀를 확인했다. 과거 raw 부재와 새 runner의 fresh 최종 관문 책임은 유지한다.'),
    ('F5','resolve',['run:context.md#C12'],'139입력·144corpus raw/clean·host8/도구SHA·공식미러를 확인했다. 한정 재사용과 원바이트 archive/관리 커밋을 승인하며12제품 경로는 T4 연결 검수까지 대기한다.'),
    ('F6','carry',['run:context.md#C11','run:phases/016/tasks/t4-fixture-repair/objective.md'],'최종 양쪽 stdin DuplicateHandle WinError6을 확인했다. AttachConsole/FreeConsole과의 인과는 가설이며 정확 OS 대조 재현을 배정한다. bootstrap 후속 통과와 역사 오류는 구별한다.')]:
    manager['dispositions'].append({'item':'015/t4-adapter-report/'+fid,'action':action,'destination':dest,'reason':reason,'evidence':ev+['run:phases/015/tasks/t4-adapter-report/report.json']})
for cid,reason in [('C2','015 검수의 현재판본/선택/결과를 추가하며 역사 partial을 보존한다.'),('C5','016의 제품 실행 단독 소유와 불변 입력 준비의 독립성·후속 연결 책임으로 갱신한다.'),('C8','사용자 지정 모델/effort를016 두 task에 유지한다.'),('C9','runner/측정의 한정 이력 처분과 P10/P11 입력 준비 책임을 추가한다.'),('C10','L01 조건을 유지하고 독립 work의 현재 상태만 갱신한다.'),('C11','T4 측정 공백 문장을 역사 상태로 옮기고 해소 근거 및 fixture/baseline/OS의 정확 남김을 기록한다.'),('C12','기존 실경계의 한정 재사용과12제품 커밋 대기·원바이트 archive/관리 추적 범위를 기록한다.')]:
    manager['context_updates'].append({'item':cid,'action':'amend','destination':['run:context.md#'+cid],'reason':reason,'evidence':ev+[base+'common-docs.diff']})
dump(RUN/'phases/015/manager.pending.json',manager)
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0564.md'
write(R/'기억/layer1/M-0565.md','''---
id: M-0565
layer: 1
title: T4 측정 성과와 기능 실패를 나누어 후속 수리와 비교 입력 준비를 배정함
convention_version: 27
---

## 맥락

015는 T4 단독 실행에서 adapter 분기를 실제 worker까지 측정하고 보고했다. 양쪽295개 시험의 측정은 complete였지만283개만 통과했고6오류·4실패·2skip이 남았다. manager는 각60worker의 요청·소스 판본·게시SHA와 원coverage DB를 대조하고 부모 합집합을 재분석했다. 정보 도달102/142와101/142가 달라도 각각의 원측정과 같으면 보고로 유효하다. 기능 합격을 대신하지 않는다.

## 다음 판단을 바꾸는 조건

아홉 fixture 문제는 제품의 지문/내용 모집단 guard, 닫힌 출력 schema, 필수 backend와 child 포트/환경을 현재 시험 입력이 따르지 못한 결과다. 이미 원trace와 현재 소스가 같은 반례는 이유 없이 다시 계산하지 않고 수리에 넘긴다. 별도 pythonw probe의 WinError6은 실제 stdin DuplicateHandle에서 발생했다. AttachConsole/FreeConsole 뒤 저장하는 순서는 코드에서 확인됐지만 인과는 아직 가설이므로 대조 재현을 배정했다. 첫 bootstrap 오류의 후속 통과만으로 transient 원인을 확정하지 않았다.

두 skip은 과거 provenance 수리 전 scripts가 없어서 생겼다. fixture 수리와 달리 이 입력은 Git 불변 객체로 준비할 수 있다.016의 두 task를 나누되 역사 입력 담당은 제품 import/시험/미러/캐시를 쓰지 않게 했다. 현재 코드를 함께 실행하는 분업 대신 한 작업만 실제 시험을 소유하므로 공유 머신과 판본 충돌을 피하면서 입력 준비를 병행한다. 두 결과를 실제로 연결하는 책임은 다음 단일 work에 남긴다. 준비 완료와 비교 통과는 다르다.

## 보존과 한계

추적 진입점은 `docs/do-math/continuous-development-2026-10-13/phases/015/manager.json`, `manager-evidence/verification.json`, `review.md`, `preservation.json`과016 두 objective다. T4 기능/입력 문제가 남아01512제품 경로는 후속 연결 검수까지 커밋하지 않는다. 원task 근거와12제품 raw는 `raw-evidence.zip`에 보존하고 관리 인계/기억만 커밋한다. 압축으로만 추적되는 scratch 원경로와 stage/commit 행정 수신은 로컬 보관이며 정리로 사라질 수 있다. 압축은 자동 복원 지시가 아니다. 기존 G 기준과 L01 외부 결정·문서/의미 질문·최종 일반/fresh T3/변이/review는 유지한다.
''')
index=R/'기억/색인.md'; s=index.read_text(encoding='utf-8'); assert 'M-0565' not in s
write(index,s.replace('## layer-1\n','## layer-1\n\n- M-0565 [T4 측정 성과와 기능 실패를 나누어 후속 수리와 비교 입력 준비를 배정함] -- 실제60worker 검수·기능12미통과 유지, 시험 단독 소유와 Git 입력 준비 병행\n',1))
print('Prepared phase 016 and manager.pending.json; G1-G8 unchanged.')
