"""Prepare phase 017 and preserve the semantic diff of common current documents."""
import difflib
import json
from pathlib import Path

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8',newline='\n')
def save(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def add_to_section(text,section,body):
    start=text.index('## '+section+' ')
    end=text.find('\n## ',start+1)
    if end<0: end=len(text)
    return text[:end].rstrip()+'\n\n'+body+'\n'+text[end:]

assert not (RUN/'phases/017').exists()
assert read(O/'verification.json')['current_matches_task']
before={p:(RUN/p).read_text(encoding='utf-8-sig') for p in ('context.md','plan.md','seams.md')}
context=before['context.md']
context=add_to_section(context,'C2',
'''phase 016의 두 task를 complete로 검수했다. manager가 두 report 형식 검사 뒤 현재2675파일과 fixture task 종료 해시의 전건 일치, 이전015 모집단2671파일과 시작의 동일성을 확인했다. 추가4개는 이전 snapshot에서 제외한 양쪽 T3-store이며 새 제품 변경이 아니다. fixture의12변경(정본5·미러5·비용캐시2)은 writes/report와 같고, 양쪽 경계21·unit/structure35 선택/고유row/exit0와 각875 Python 및 실행 전후를 대조했다. 이전 정확10error/failed와 bootstrap2가 새 passed row에 연결된다. 양쪽 각9worker 게시·요청·소스/artifact SHA와 OS 원핸들/종료를 확인했다. provenance는 도입bbe64043의 첫 부모010b0597에서 추출한910파일·9901995바이트·901blob을 새 Git 조회로 전건 검산했다. 입력 준비 완료는 두 실제 비교 성공이 아니다. 검수 HEAD는 72684c76ed5d282279de5de956523ea17ffd4e40이며 근거는 run:phases/016/manager-evidence/verification.json·review.md와 두 원report다. 전체 T4와 최종 G 관문은 미수행이다.''')
start=context.index('phase 001~015의 task 세션은')
end=context.index('\n\n',start)
context=context[:start]+'''phase 001~016의 task 세션은 종료됐고016의 fixture/OS 수리와 과거 비교 입력 준비를 각각 검수했다.017 t4-baseline-integration 한 work가 실제 두 비교와 양쪽 전체 T4, raw 관측 보존을 순차 소유한다. 현재/과거 소스와 공유 캐시·미러를 고정해야 하는 연결 검증이므로 같은 phase에 제품 수정 task를 병행하지 않는다. 변경 가능한 제품 경로는 양쪽 비용캐시4개뿐이며 새 결함은 반례와 정확 후속 범위로 반환한다. jobs1·총worker3 이하·한 묶음씩을 유지한다. 다른 과거 보고/제품/설치·Git index를 수정하지 않고, 새 유료 공급자·예약 변경·학술 검색·기존 연구 운전은 수행하지 않는다. 기존 실경계의 승인된 성질 재사용과 L01 외부 결정·최종 관문은 유지한다.'''+context[end:]
context=add_to_section(context,'C8',
'''016 두 task의 gpt-6.1-sol/high 수행을 검수했다.017 t4-baseline-integration에도 같은 사용자 지정 모델/effort를 명시한다. 이는 개발 실행 모델이며 제품 공급자 실호출은 새로 배정하지 않는다.''')
context=add_to_section(context,'C9',
'''016은5d8db87a/bd3ae53f의 설치 fixture·포트 수축,3b37e80c의 실제 Job 관측,c4ba50b4의 writer lock,23cc4df3의 Git/자손 콘솔,407db136의 archive checker 및8afa57c7의 필수 backend slice를 현재 diff/소비와010~012의 한정 검수에 대조했다. 실제 compiler/저장/currentness/identity·잠금 반려/정상 획득·Unicode 바이트를 유지하고 현재 입력/포트/관측 fixture만 교정한 판단을 승인한다. 다른 PR/hunk나 부재 원보고 counts는 새 성공으로 올리지 않는다. provenance 도입bbe64043의 실제 첫 부모010b0597와 도입 M-0472의 동일 baseline 기록을 확인했다. B56 네 Temp 원보고는 현재 해당 경로에 없고 역사2passed15.2초는 새 비교 근거가 아니다. 이 비교의 P10/P11은 정확 시험/역사 표기이며 requirement-state103row의 ID나 문서 후속 packet P10/P11이 아니다. 원문 진입점은 설계5.3~5.5/A29·PR01/B56와 K-05/K-06이다. 이전 objective의 requirement-state P10/P11 경로 표현은 이 범위로 정정하며 원배정은 수정하지 않는다. 근거는016 두 task review.md·history-review.json·history-selection.json·requirement-trace.json과 manager 검수다. PR01 전체 종결은 아니다.''')
context=context.replace('015 T4 측정은 검수됐고016의 fixture/OS 문제와 과거 비교 입력 준비는 이 답변과 독립적으로 진행한다.',
                        '015 T4 측정과016의 fixture/OS 수리·과거 입력 준비를 검수했고017의 실제 비교/전체 T4는 이 답변과 독립적으로 진행한다.')
context=add_to_section(context,'C11',
'''016에서015의 정확9fixture와 WinError6 남김을 새 근거로 해소했다. installed_request는 현재 trust_inventory producer의 실제 지문/content11094파일 모집단·원바이트를 사용하며 clean-build validation/연구 채택 권한은 여전히 합성이다. 설치 공유 신뢰 기록을 승인/수정하지 않는다. 실제 compiler/저장/authoritative 소비의 범위는 원시험대로 유지한다. observation은 ok의 의미 schema와 Codex 문자열 전송을 같이 맞췄고, lock/archive child는 자기 real_ports를 전달한다. 양쪽21+35는 전건passed이며 이전10실패와 정확 대응한다.

WinError6은 일반 child에서는 재현되지 않았고 실제 Job의 control은 null stdin/exit0, 원 AttachConsole/FreeConsole 관측은 invalid nonnull stdin/exit1·DuplicateHandle 실패였다. 시험의 콘솔 관측만 별도 pythonw child로 분리해 저장 stdin을 보존하고 실제 Git/자손·hidden console 양성 대조·visible=[]·binary readback을 유지했다. 별도 수리 관측의 실제 exit0/root_signaled/빈Job도 검수했다. 제품 Git runtime은 불변이다. bootstrap-info2는 현재 양쪽passed이나015 첫 WinError5의 원인은 미확인이다.017 전체 T4에서 재현되면 정확 trace/OS 조건으로 처리하며 무조건 retry/skip을 하지 않는다. 초기 진단의 없는 Job API/개행 계획/count-row 혼동 오류는 원exit1과 함께 보존하고 제품 실패와 구별한다.

provenance의 입력 준비는 완료됐고 두 exact 비교는 아직 미검사다. 검수된 baseline은 run:phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json에 결속된 pre-provenance/scripts910파일이다.017은 SHARED_INPUT_BASELINE_SCRIPTS로 이 절대 경로를 실제 소비하고 ordinary 결과/읽기·literal entered(빈 label 포함)/opens/import_opens·파일/context/line/arc와 명시 marker 차이·두worker raw union을 검증한다. TemporaryDirectory의 cleanup 전에 현재 실제 TestCase의 원관측을 자기 evidence로 보존한다. 원old 트리 개작이나 동등성 단언 완화는 허용하지 않는다. 이어 같은 제품 판본에서 정본/미러 전체 T4를 실제 선택/row/exit·각worker/adapter 자료까지 대조한다. 부분 회귀를 더해 전체 성공으로 읽지 않는다. 근거는016 manager verification.json·review.md와017 objective다. L01·다른 의미/문서 질문 및 G4~G6/G8은 유지한다.''')
context=add_to_section(context,'C12',
'''016 F3의 보존 사실을 검수했다.015의12제품 경로, runtime 포함139실호출 입력·144corpus 경로·8host 원자료·도구SHA·index/pseudo/T3-store는 불변이다. 전144경로 Git raw/clean과 공식 --check1336/skill-only 및 관련 양쪽56passed를 확인했다. 기존 실호출은 불변 경로/도구의 승인된 성질만 재사용하며 새 유료/예약 호출은 없다.01512경로와01610비캐시 제품경로, 합22경로의 커밋은017 전체 T4 연결 검수 뒤 판단한다. 이번 관리 마감은 공용 인계·두 원보고/선별 근거·017 배정·기억만 포함한다. 두 task 원자료(과거910파일 포함)와22제품 원바이트는 raw-evidence.zip으로 보존하고 전건 SHA/선별 추적 경로는 run:phases/016/manager-evidence/preservation.json에 둔다. 원경로 중 압축으로만 추적하는 scratch/중복 snapshot과 stage/commit 행정 수신은 로컬 보관이며 정리로 사라질 수 있다. 압축은 자동 복원 지시가 아니다.017 배정·관리 기록은 제품 검증 판본이나 G 완료 조건을 바꾸지 않는다.''')

plan=before['plan.md'].replace('## phase 001~015의 결과와 현재 상태','## phase 001~016의 결과와 현재 상태')
plan=plan.replace('최종 T4 각295건의283통과·6오류·4실패·2skip은 미해결이며 측정 complete와 구별한다.',
'''015 당시 최종 T4 각295건의283통과·6오류·4실패·2skip은 역사 실패로 유지한다.016 두task는complete로 검수했고 정확10fixture/OS 실패가 양쪽 지정56passed로 해소됐다. Git 입력910파일 준비는 성공했으나 두 실제 비교와 양쪽 전체 T4는017 책임이다. 측정complete·부분회귀·입력준비와 전체기능 합격을 구별한다.''')
start=plan.index('## 다음 phase: 016'); end=plan.index('## 가까운 후속 배정과 선행 관계',start)
plan=plan[:start]+'''## 다음 phase: 017

gpt-6.1-sol/high의 t4-baseline-integration 단일 work를 배정한다.016 fixture 수리 판본과 Git 첫 부모010b0597의 별도910파일 입력을 실제 연결한다. 환경변수 SHARED_INPUT_BASELINE_SCRIPTS의 값/하위 전달·전후manifest/소스/도구를 기록하고 정본·미러의 두 정확 비교를 공식 runner로 수행한다. ordinary/측정 보존·명시 marker 차이·두worker raw union을 현재 TestCase/실제 child 자료에 대조한다. 임시 fixture 삭제 전 raw를 확보하는 한정 companion을 자기 evidence에 두며 제품 시험/기대값을 복제하지 않는다.

이어서 같은 제품·시험 판본에서 양쪽 --tier T4 --jobs 1 전체 선택을 각각 완결한다. 실제 선택/고유row/exit·worker 요청과 게시/원DB·adapter5개 분모/합집합·complete를 대조한다. 정본과 미러 도달률이 같거나 임계값을 넘을 필요는 없으나 기능 실패/skip/미실행은 숨기지 않는다. bootstrap WinError5가 재현되면 원trace/OS조건을 보존한다. 두 비교의 빠른 선행 실행과 전체 T4의 계측 포함 연결은 검증 목적이 다르다. 이미 검수한016의56관련 회귀는 새 이유 없이 반복하지 않는다.

변경 가능한 제품 범위는 양쪽 비용캐시4개뿐이다. 구현/요구/기대값/과거baseline은 고정하고 새 결함은 정확 반례·필요파일을 다음 work로 반환한다. 검사 중 소스/공유캐시·미러 판본 충돌을 피하도록 다른 제품 task를 병행하지 않는다. 한 묶음씩 jobs1·총worker3 이하를 유지하고 마지막 공식 생성의 예상변경이 캐시뿐인지 확인한 뒤 --check/skill-only를 수행한다.01512제품과01610제품의Git마감은 새 전체연결 결과의 manager 검수 뒤 판단하며 현재 원바이트는016 archive에 보존한다.

L01 Q1/Q2의 운전 프로필·출력 단위 결정은 계속 남는다. 답변 전에는 원문 byte 기준과 미충족 판정을 유지하고017의 독립 연결 검증을 진행한다. 전체일반/freshT3/전체변이·남은의미/문서·최종review는 이 작업 밖의 원래 완료기준으로 유지한다.

'''+plan[end:]
plan=plan.replace('015 T4 측정과70회귀는 검수했으나 기능/입력/OS 남김을016으로 넘긴다.015 제품12경로는 후속 전체 T4 연결 검수까지 대기한다. 근거는015 manager-evidence/verification.json·review.md다.',
'''015 T4 측정과016 fixture/OS 수리를 검수했다.016의Gitbaseline910파일과 새 양쪽56회귀를 승인하되 정확baseline 비교/전체T4는017에 남긴다.01512·01610비캐시 제품, 합22경로의 마감은 그 연결검수까지 대기한다. 근거는016 manager-evidence/verification.json·review.md다.''')
plan=plan.replace('| G1/G3/G7 T4 fixture·OS 실패 | 016 t4-fixture-repair가 정확 오류6·실패4의 입력/OS 원인을 다루고 관련 정본/미러 회귀를 확인한다. | runtime/설치 신뢰 검사를 낮추지 않는다. OS 원인 미확인·초기 bootstrap 실패도 후속 상태를 명시한다. |',
'''| G1/G3/G7 T4 fixture·OS 실패 | 016에서 정확10실패/오류와 관련 양쪽56건을 통과시켰다.017 전체 T4에서 결합 동작을 확인한다. | Git WinError6은 관측자의 stdin 부수효과였다. 제품runtime/신뢰guard는 유지했고 과거bootstrap WinError5 원인은 미확인이다. |''')
plan=plan.replace('| G2/G3/G7 P10/P11 비교 입력 | 016 provenance-baseline이 불변 Git 이력에 결속된 별도 scripts 트리·manifest를 준비한다. | 같은 phase에는 시험/제품 import를 하지 않는다. 준비 완료는 두 exact-baseline 성질의 통과가 아니다. |',
'''| G2/G3/G7 P10/P11 실제 비교 | 016의Git원바이트910파일을017이 소비해 양쪽두정확시험과 cleanup 전 raw를 검증한다. | P10/P11은 여기서 역사/정확시험 표기이며 requirement-state ID나 문서packet과 다르다. 역사raw4개부재/입력준비완료와 실행성공을 구별한다. |''')
plan=plan.replace('| G7 T4 실제 연결과015 제품 마감 | 016 두 결과가 준비되면 후속 단일 work가 정확 baseline 두 비교와 양쪽 전체 T4를 실행하고 선택/row/exit·각 worker·소스/미러를 대조한다. | 부분 회귀의 합산은 전체 성공이 아니다. 별도 입력을 현재 root로 위장하거나 skip을 pass로 세지 않는다. |',
'''| G7 T4 실제 연결과015~016 제품 마감 | 017 단일work가 양쪽전체T4의 실제선택/row/exit·각worker·소스/미러와 측정 완전성을 검증한다. manager가22제품경로의마감을판단한다. | 부분합산은전체성공이아니다. 미해결실패/skip은정확후속work로넘기며G4~G8전체완료로확대하지않는다. |''')
seams=before['seams.md'].rstrip()+'''

016은 현재 fixture 소비만 교정했고 Git과 과거 입력 원바이트를 검수했다.017은 기존 SHARED_INPUT_BASELINE_SCRIPTS 소비·TestCase/WORKER/SNAPSHOT·run_tests/AdapterMeasurement의 실제 연결을 검증한다. 두 task 사이 새 인터페이스를 구현하지 않고 한 task가 고정된 제공/소비를 함께 실행하므로 S 항목·provides/uses는 추가하지 않는다. 의미/형식/오류의 정본은 기존 코드와015 측정 정의이며 과거910파일을 새 제품 계약이나 호환 분기로 만들지 않는다.
'''
for p,text in [('context.md',context),('plan.md',plan),('seams.md',seams)]: write(RUN/p,text)
diff=''.join(''.join(difflib.unified_diff(before[p].splitlines(True),(RUN/p).read_text(encoding='utf-8').splitlines(True),fromfile=p+' before 016',tofile=p+' after 016')) for p in before)
write(O/'common-docs.diff',diff)
assert before['context.md'].split('## C2 ')[0]==context.split('## C2 ')[0]

task='t4-baseline-integration'
base='phases/017/tasks/'+task
inputs=[
 'run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md',
 'run:phases/016/manager-evidence/verification.json','run:phases/016/manager-evidence/review.md',
 'run:phases/016/manager-evidence/source-inspected.json',
 'run:phases/016/tasks/t4-fixture-repair/report.json','run:phases/016/tasks/t4-fixture-repair/evidence/review.md',
 'run:phases/016/tasks/provenance-baseline/report.json','run:phases/016/tasks/provenance-baseline/evidence/review.md',
 'run:phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json',
 'run:phases/016/tasks/provenance-baseline/evidence/baseline-verification.json',
 'run:phases/016/tasks/provenance-baseline/evidence/api-static-verification.json',
 'run:phases/016/tasks/provenance-baseline/evidence/requirement-trace.json',
 'run:phases/015/tasks/t4-adapter-report/report.json','run:phases/015/manager-evidence/verification.json',
 'repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
 'repo:.claude/skills/do-math/scripts/이음새-정본.md',
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md',
 'repo:.claude/skills/do-math/scripts/tests/boundary/test_shared_input_provenance.py',
 'repo:.claude/skills/do-math/scripts/tests/support/branch_gate.py',
 'repo:.claude/skills/do-math/scripts/tests/support/t3_store.py',
 'repo:.claude/skills/do-math/scripts/tests/support/adapter_coverage.py',
 'repo:.claude/skills/do-math/scripts/run_tests.py',
 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
writes=[tree+'/skills/do-math/scripts/tests/'+file for tree in ('.claude','.agents') for file in ('.timings.json','.timings-t3.json')]
save(RUN/'phases/017/phase.json',{'kind':'work','purpose':'016의현계약fixture수리와Git과거입력을실제연결하여두exact비교/원관측과양쪽전체T4를검증한다. 제품22경로마감과후속판단에필요한실제결과를확보한다.',
 'tasks':[{'id':task,'model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]})
write(RUN/base/'objective.md',r'''## 목적과 역할

G2/G3/G7의 두 exact-baseline 비교와 양쪽 전체 T4 연결을 완료한다.015 측정/70회귀와016의 현계약 fixture·OS 수리/양쪽56회귀 및 Git baseline 준비는 검수됐다. 부분 회귀와 입력 준비를 실제 전체 결과로 연결하는 단일 work다.015~016 비캐시 제품22경로의 커밋 판단은 다음 manager가 맡는다. 전체일반/freshT3/전체변이·최종review를 대신하지 않는다.

## 완료 조건

### A1 검수된 입력·판본과 실행 조건 결속

016 manager source-inspected2675파일과 시작 상태를 대조한다. 차이가 있으면 출처/영향을 확인하며 이전 통과를 현재 판본에 자동 승계하지 않는다. canonical과 mirror의 Python/시험/문서, tool/Python/coverage, 실제cwd/argv/환경값을 기록한다. baseline-manifest의 pre-fix0b4a2ebcdce03e37f3f4077c658b606933971fba·도입bbe64043·910파일을 별도 절대 경로와 전건SHA/Gitblob으로 확인한다. 기록 루트의 phases/016/tasks/provenance-baseline/evidence/pre-provenance/scripts가 승인된 입력이다. 같은 phase의 새 결과를 기다리는 의존은 없다.

현재 test_shared_input_provenance의 두 exact 메서드·assert_baseline_capture·WORKER/SNAPSHOT/merge와016 review의 성질을 읽는다. P10/P11은 여기서 정확시험/역사 표기이며 requirement-state나 문서packet의ID가 아니다. 네역사Temp원보고부재·역사counts 한계와 현bootstrap원인미확인을 유지한다.

### A2 두 정확 비교의 공식 실행과 실제 raw

SHARED_INPUT_BASELINE_SCRIPTS를 승인된 절대경로로 설정하고 하위 실제 실행에서도 소비됨을 기록한다. 정본/미러 각각 다음 두ID를 공식runner로 먼저 실행해 선택2/고유row2/passed2/skip0와exit0를 확인한다.

- boundary.test_shared_input_provenance.SharedInputProvenanceTests.test_exact_baseline_literal_entries_opens_and_coverage_with_explicit_marker_differences
- boundary.test_shared_input_provenance.SharedInputProvenanceTests.test_exact_baseline_two_worker_raw_union

ordinary old/new와 measured old/new의 실제결과/읽기횟수·순서, 모든literal entered label(빈label 포함)/pair·opens/import_opens와coverage 파일/context/lines/arcs, 명시 shared marker 차이를 검사한다. 두worker 각각의input-a/input-b 관측과 각판본 실제merge가 자기raw union 및old/new literal 동등성에 맞아야 한다. 총도달률·옛counts·정적API분석만으로 대신하지 않는다.

공식시험의 임시fixture는 cleanup으로 사라진다. 최소한 정본의현재실제TestCase와동일child프로그램을 사용하는 별도근거companion을 자기evidence에 만들고 정규unittest lifecycle의cleanup 직전 실제fixture/run/result/snapshot/coverage.data/opened/entered를 복사·해시해 보존한다. 실패해도 가능한raw를 보존하고 실제결과를 그대로 보고한다. 기대값/비교알고리즘·fixture를 새로 구현하거나 결과를 성공으로 가공하지 않는다. 자신이 소유한TEMP/TMP와fresh process만 사용하고 제품/과거트리를 바꾸지 않는다. 정본raw를미러에재사용할때는공식변환과실제파일차이/시험정의를대조해범위를설명한다. 원raw를재대조할수없는축은미관측으로밝힌다. companion은공식runner통과와별도근거다.

### A3 동일 판본 양쪽 전체 T4와 측정 완전성

A2와같은제품판본에서 정본과미러 각각 --tier T4 --jobs 1 전체선택을완결한다.015의295개를고정분모로쓰지않고현선택모집단과고유실제row가전건대응하며error/failed/skipped/not_run가없고실제exit0인지확인한다. A2의개별실행과전체T4계측아래연결은서로다른검증이다. 일부성공의합산으로전체실행을대체하지않는다.

보고t4_adapter/adapter-coverage.json, 각worker의실제requested/run_id/소스전후/게시·artifactSHA/branchDB와부모합집합·adapter5개정보분모를대조한다. 원합집합을현source/coverage설정으로재분석하고정보도달과기능합격을구별한다. 양쪽도달률동일이나임계통과를요구하지않는다. T3 branch gate/선택색인/증분저장소 의미와섞지않는다.015의10실패/2skip 및016정확통과를새전체row에연결한다. bootstrap WinError5가재현되면child/trace/OS조건을보존하며무조건retry/skip으로가리지않는다.

### A4 보존·공식 미러와 후속 판단 인계

실행전후현재소스·과거baseline·runtime139실호출입력·corpus144원경로/명시SHA/Gitraw-clean·host8원자료/도구조건·01512제품/01610제품 바이트를대조한다. 검증된성질과한정재사용조건을구분하고유료/실예약호출을추가하지않는다. 공식미러생성은사전계획의예상변경이배정비용캐시4개범위뿐일때수행하고 --check/skill-only를확인한다. 무관드리프트를덮지않는다. 원report/raw/실제process/시작·종료·exit·SHA를보존한다.

발견시실패의기대/실제·최소반례·필요수리파일·무효화근거를반환한다. 구현/시험단언/옛baseline의수리는이배정밖이다. A2/A3미충족은fail/not_run과partial/blocked로정확히보고하며완료처럼인계하지않는다. 이전task보고와현재기록을고치지않는다. 최종일반/freshT3/함수전수변이·문서/의미/L01·최종review와Git마감의후속책임을유지한다.

## 판단과 경계

writes는 양쪽 .timings.json/.timings-t3.json뿐이다. 이값은공식실행/생성의부산물이며실행성공근거가아니다. 자기evidence의companion/원자료는작성가능하다. 제품/시험/runner/측정/설계·원기대값·과거910파일·공용문서·다른task자료·engine·설치/신뢰기록·corpus·index/pseudo/T3-store·Git/기억은수정하지않는다. 현재fixture가실행하는실compiler/Job/Git와시험전용공간만사용한다. 설치신뢰승인/기존연구재개·유료공급자/실예약변경·학술검색·graphify갱신·stage/commit/reset/checkout/push는수행하지않는다. 실패때쓰기범위를임의확대하지않는다.

## 검증 방법

cwd C:\math. Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. 환경변수는 C:\math\docs\do-math\continuous-development-2026-10-13\phases\016\tasks\provenance-baseline\evidence\pre-provenance\scripts 를가리킨다. 양쪽 .claude/.agents/skills/do-math/scripts/run_tests.py를 -u -B로사용한다. 정확두ID는 --jobs 1 --output <자기evidence새폴더>, 전체는 --tier T4 --jobs 1 --output <별도새폴더>다. 실제선택은공식 --list와원report로대조한다. companion도한묶음씩수행하며총worker3이하를유지한다. 실행중제품/시험소스는고정한다.

실제argv/cwd·비밀없는baseline환경값·PID/시작/종료/exit와전후해시를기록한다. result.json 진행읽기는do_math.file_io.read_bytes_shared를사용한다. 도구yield/관찰대기/시간경과를실패나성공으로해석하지않는다. 현재시험내기존한계에막히면원trace와영향을반환하고시간초과를검증통과로세지않는다. 이미검수한016의56관련시험은새변경/실패/증거무효화근거없이반복하지않는다. 마지막 check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 017 t4-baseline-integration 을통과하고report경로와상태를반환한다.
''')
(RUN/base/'evidence').mkdir()
(RUN/'phases/017/logs').mkdir()

write(O/'review.md', '''# phase 016 검수와 다음 판단

두 report는 manager의 형식 검사를 통과했고 배정된 A를 완료했다. verification.json은 작업자 검산을 다시 호출하지 않고 현재2675파일, 작업 전후12변경/writes, 양쪽21+35의 선택·고유row·실제exit·875Python, 각9worker 게시·요청·artifactSHA를 원파일에서 대조한 결과다.0152671과0162675의 차이는 양쪽 T3-store4개를 snapshot에 포함한 차이이며 시작부터 존재했다. 실제 옛10error/failed 전부와 bootstrap2가 새passed에 연결된다. 원report/실패를 재작성하지 않았다.

실제 diff에서 installed_request의 지문/content 모집단을 현재 producer로 맞추고 validation/채택 권한의 합성 경계를 유지했음을 확인했다.11094파일 기록의 원SHA와 지문/content key 동일 및 보존된5표본을 확인했다. 새 full Mathlib나 설치 신뢰 승인으로 확대하지 않는다. Codex 의미/전송schema, WriterLock의필수backend와해제후획득, archive child의자기포트/exit0 수리는 기존 정확 결과를 유지한다.

일반 child의 성공과 실제 Job의 WinError6은 조건이 다르다. control은nullstdin/exit0이고 원관측은AttachConsole/FreeConsole뒤invalidnonnullstdin/exit1·DuplicateHandle이었다. 관측자분리 후 실제Git/자손·hiddenconsole양성·visible=[]·binaryreadback과exit0/빈Job을 확인했다. 제품Git은 변경되지 않았다. bootstrap현재2passed는 과거WinError5원인규명이 아니므로017전체실행의관측조건으로 유지한다. 초기 보조도구의 exit_code/poll API오류와개행/count-row오류는 실제exit1을 보존한다.

baseline의도입bbe64043첫부모010b0597·scripts tree와실제도입M-0472의동일선택을Git에서확인했다.910경로/9901995바이트/901고유blob을새ls-tree/cat-file로전건재검산했다. 현재시험의assert_baseline_capture/두exact메서드를읽고ordinary/literal(빈label)/open/import/전체coverage·marker/두workerunion의보존범위를확인했다. 이는정적자격과바이트검증이며실제비교가아니다. requirement-state에없는P10/P11을원문ID처럼읽지않고역사/정확시험표기로정정했다. 네역사Temp보고부재는016원기록과C9에유지한다.

새전체T4를추가하기전두exact비교를공식양쪽runner로확인하고정본의현재TestCase원raw를cleanup전에보존한다. 전체T4는해당비교도계측아래다시소비하므로공식전체결과가필요하다. 공유소스/캐시를고정하는실행이어서017은한task다. productwrites는비용캐시뿐이며실패하면최소반례를다음work로넘긴다.01512·01610제품의커밋은새연결결과검수까지대기하고현재원바이트는archive로보존한다.

공용문서diff를검토했다. C1/G1~G8과기존조건/예외는불변이다. C2는016검수추가,C5는종료된016동시실행설명을017단일실행조건으로교체,C8은지정모델,C9는fixture검토/식별자정정,C10은L01결정과독립인현재행동만갱신,C11은새해소와아직미검사인실제비교/전체T4,C12는保존/22제품대기를추가했다. plan의다음배정/가까운세행을이결과로갱신하고나머지의미/문서/최종관문을보존했다. seams에는기존정본소비만추가했고S계약개정은없다.
'''.replace('保존','보존'))

v='run:phases/016/manager-evidence/verification.json'; review='run:phases/016/manager-evidence/review.md'; objective='run:'+base+'/objective.md'
findings=[
 {'item':'016/t4-fixture-repair/F1','action':'resolve','destination':['run:context.md#C11',objective],
  'reason':'정확10실패는양쪽새passed와원핸들/수리diff로해소했다. 부분회귀와전체T4를구별하여017에연결책임을남긴다.','evidence':[v,review]},
 {'item':'016/t4-fixture-repair/F2','action':'carry','destination':['run:context.md#C11',objective],
  'reason':'bootstrap현재양쪽2passed는승인하되과거WinError5원인미확인은유지한다.017전체에서재현되면정확trace/OS조건으로판정한다.','evidence':[v,review]},
 {'item':'016/t4-fixture-repair/F3','action':'resolve','destination':['run:context.md#C2','run:context.md#C12','run:plan.md'],
  'reason':'139입력/144corpus/host8/도구/01512제품보존을현재와원자료로확인했다.2675모집단차이와합성validation경계를명시하고22제품마감은017검수까지대기한다.','evidence':[v,review]},
 {'item':'016/provenance-baseline/F1','action':'carry','destination':['run:context.md#C11',objective],
  'reason':'도입부모·원기록·910Gitblob원바이트의입력자격을검수했다. 실제비교/wholeT4는미수행이므로017의정확raw/공식연결검증으로배정한다.','evidence':[v,'run:phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json']},
 {'item':'016/provenance-baseline/F2','action':'resolve','destination':['run:context.md#C9',objective],
  'reason':'네역사보고의해당경로부재와P10/P11namespace정정을받아들인다.역사counts를새성공에합산하지않고현재exact시험/G2/G3/G7진입점으로연결했다.','evidence':['run:phases/016/tasks/provenance-baseline/evidence/historical-report-availability.json','run:phases/016/tasks/provenance-baseline/evidence/requirement-trace.json',review]}]
updates={
 'C2':'016두complete의근거와2675/2671모집단,부분회귀/입력준비의한계를추가했다.',
 'C5':'종료된016분업의현재실행설명을017단일연결/판본고정/캐시소유로교체했다.기존worker상한은유지한다.',
 'C8':'사용자지정모델을017에승계하며제품유료호출과구별했다.',
 'C9':'지정fixture도입slice유지/교정과원baseline자격·역사raw부재·P10/P11식별자정정을추가했다.',
 'C10':'L01질문/byte요구를그대로두고독립적으로진행하는현재행동을017로갱신했다.',
 'C11':'정확10실패해소와관찰자핸들인과를추가하고bootstrap원인미확인·실제baseline비교/전체T4책임을보존했다.',
 'C12':'기존실호출한정재사용·22제품대기·원자료archive및추적/로컬범위를추가했다.'}
save(RUN/'phases/016/manager.pending.json',{
 'next':'017',
 'decision':'두task는자기A를완료했으며manager가원보고/현재2675소스·허용12변경·양쪽각56passed/실제exit·9worker씩게시와OS핸들을대조했다. fixture9와WinError6은해소됐고제품runtime/신뢰검사는불변이다. bootstrap과거WinError5원인은현재통과와구별해남긴다. provenance는실제도입첫부모와M-0472·910Git원바이트를확인했지만실제비교를실행하지않았다. 두report는이경계에서상충하지않는다. 다음017은고정된두산출물을소비하는exact비교/raw보존·양쪽전체T4의단일work다. 공유소스/캐시의독립실행을보장하기위해동일phase에제품변경task를두지않는다. 새반례는writes밖수리로그대로반환한다. 원G/문서/의미/L01과최종관문은남아개발종료를선언하지않는다.015~016제품22경로는연결검수까지대기하고이번에는인계·선별근거·기억만마감한다.',
 'reports':[{'task':task,'state':'read','detail':'report검사통과후전문을읽고원근거와현재파일을검수했다. '+detail,
             'evidence':['run:phases/016/tasks/'+task+'/report.json',v,'run:phases/016/manager-evidence/'+task+'-report-check.json']}
            for task,detail in [('t4-fixture-repair','A1~A4 complete를지정회귀범위에서승인하며전체T4와과거bootstrap원인규명으로확대하지않는다.'),('provenance-baseline','A1~A3 complete는Git입력준비의완료다.실제exact비교와G충족을뜻하지않는다.')]],
 'dispositions':findings,
 'context_updates':[{'item':k,'action':'amend','destination':['run:context.md#'+k],'reason':reason,
                     'evidence':[v,review,'run:phases/016/manager-evidence/common-docs.diff']} for k,reason in updates.items()],
 'plan_update':'016두결과검수와F처분을반영하고017의두exact/raw및양쪽전체T4단일연결work를배정했다.검사전후판본고정/캐시범위·실패반환·22제품커밋대기를명시했다.나머지의미/문서/L01/최종일반·freshT3·전수변이·review계획과G는보존했다.',
 'seam_updates':[], 'completion':None})
print('Prepared 017, common-docs.diff, review.md, and manager.pending.json; not published.')
