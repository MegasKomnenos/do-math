"""Write the phase 017 management decision and bounded phase 018 assignment."""
import difflib
import json
from pathlib import Path

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; P=RUN/'phases/017'; N=RUN/'phases/018'
E='run:phases/017/tasks/t4-baseline-integration/evidence/'
M='run:phases/017/manager-evidence/'
OBJ='run:phases/018/tasks/job-cleanup/objective.md'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+'\n',encoding='utf-8',newline='\n')
def js(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2))
def section(text,id):
    start=text.index('## '+id+' ')
    end=text.find('\n## ',start+1)
    return start,len(text) if end<0 else end
def append_section(text,id,paragraph):
    start,end=section(text,id)
    return text[:end].rstrip()+'\n\n'+paragraph.strip()+'\n'+text[end:]

assert read(O/'verification.json')['task_artifacts_unchanged']==5919
assert not N.exists() and not (P/'manager.json').exists()
original={n:(RUN/n).read_text(encoding='utf-8-sig') for n in ('context.md','plan.md','seams.md')}
context=original['context.md']
context=append_section(context,'C2','''phase 017 t4-baseline-integration은 A1/A2/A4 pass·A3 fail의 partial로 검수했다. report 형식 검사 뒤 현재2675파일과 종료 해시, 시작과016 manager 판본의 전건 일치를 확인했고 변경은 허용된 양쪽 .timings-t3.json뿐이다. 정본/미러 두 exact 시험은 각각2passed/exit0이며 정본 companion의6fixture·30snapshot·16DB·30실제child를 다시 읽어 ordinary/literal/opens/import/coverage·명시 marker와 실제 merge를 대조했다. 네 전체 T4의 각295선택·고유row·실제exit와 각60worker 게시/원DB·adapter5개 분모를 확인했다. 최종 정본 c4는294passed/1error/exit1, 미러 m4는295passed/exit0이다.015의 정확12미통과는 새 양쪽 전체에서 passed지만 c4의 Job cleanup WinError32/5 때문에 전체 기능 합격은 아니다. 원task5919파일은 검산 전후 불변이다. 근거는 run:phases/017/manager-evidence/verification.json·review.md다. G4~G6/G8과 다른 의미·문서·L01 남김은 유지한다.''')
start,end=section(context,'C5')
part=context[start:end]
paragraph_start=part.index('\n\n')+2
paragraph_end=part.index('\n\n',paragraph_start)
part=part[:paragraph_start]+'''phase 001~017의 task 세션은 종료됐다.018 job-cleanup 단일 work가 실제 JobsContract의 정리 순서·종료 관측을 검증하고 필요한 fixture 수리, real/fake 관련 회귀, 고정된 최종 판본 양쪽 전체 T4를 순차 소유한다. 공유 시험 정본·캐시·미러를 고정해야 하므로 제품 수정 task를 병행하지 않는다. 새 전체 검사에 무관한 독립 조사 task를 추가해 입력/검수 비용을 늘리지 않는다. jobs1·전체worker3 이하·한 묶음씩을 유지한다. 제품 runtime/공유 인터페이스는 고정하고 범위를 넘는 결함은 정확 반례로 반환한다. 새 유료 공급자·예약 변경·학술 검색·기존 연구 운전은 배정하지 않는다.'''+part[paragraph_end:]
context=context[:start]+part+context[end:]
context=append_section(context,'C5','''017 F2의 실행 환경 반례를 다음 검사에 반영한다. parent TEMP/TMP/TMPDIR는 저장소 밖의 짧은 자기 전용 경로를 쓰고 git rev-parse가 상위 저장소를 찾지 않는지 확인한다. resource worker는 공식 output 아래 scratch를 다시 쓰므로 출력 경로도 짧게 정한다.017의 실제 probe cwd262자는 WinError267,241자는 정상0/반려1이었다. 이것은 이 환경의 관측이며 Windows 보편 상한이 아니다.018의 짧은 task 이름과 evidence/c4·m4를 사용하고 실제 최종 cwd를 확인한다. 긴 경로 실패를 제품 기대값 완화·skip·무조건 재시도로 처리하지 않는다.''')
context=append_section(context,'C8','''017의 gpt-6.1-sol/high 작업을 검수했다.018 job-cleanup에도 같은 사용자 지정 모델/effort를 명시한다. manager 설정과 제품 공급자 실호출 모델은 그대로 구별한다.''')
context=append_section(context,'C9','''017에서016의 과거910파일 입력을 실제 소비한 두 exact 비교를 검수했다. 공식 정본/미러 각2passed와 정본 companion raw의 literal 빈 label·입력 순서·읽기·분기·명시 shared marker·양 worker merge를 대조했다. P10/P11로 지칭하던 이 한정 비교의 미실행 남김은 종료한다. 미러 원fixture raw는 별도 보존되지 않았으며 같은 시험 바이트/공식 변환과 미러 공식 실행 범위에서만 정본 raw를 재사용한다. 네 역사 Temp 원보고 부재와 PR01 다른 slice의 미검토는 유지한다. 근거는 run:phases/017/manager-evidence/verification.json 및 rechecked-raw-verification.json이다.''')
context=context.replace('017의 실제 비교/전체 T4는 이 답변과 독립적으로 진행한다.', '017의 실제 비교/전체 T4 검수와018 Job cleanup 수리는 이 답변과 독립적이다.')
old='''provenance의 입력 준비는 완료됐고 두 exact 비교는 아직 미검사다. 검수된 baseline은 run:phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json에 결속된 pre-provenance/scripts910파일이다.017은 SHARED_INPUT_BASELINE_SCRIPTS로 이 절대 경로를 실제 소비하고 ordinary 결과/읽기·literal entered(빈 label 포함)/opens/import_opens·파일/context/line/arc와 명시 marker 차이·두worker raw union을 검증한다. TemporaryDirectory의 cleanup 전에 현재 실제 TestCase의 원관측을 자기 evidence로 보존한다. 원old 트리 개작이나 동등성 단언 완화는 허용하지 않는다. 이어 같은 제품 판본에서 정본/미러 전체 T4를 실제 선택/row/exit·각worker/adapter 자료까지 대조한다. 부분 회귀를 더해 전체 성공으로 읽지 않는다. 근거는016 manager verification.json·review.md와017 objective다. L01·다른 의미/문서 질문 및 G4~G6/G8은 유지한다.'''
new='''017에서 provenance의 두 exact 비교를 완료했다.016 baseline-manifest의 과거910파일은 전후 불변이고 현재 원바이트 SHA/Git blob과 일치한다. SHARED_INPUT_BASELINE_SCRIPTS가 실제30child에 전달됐고 old/current scripts 선택을 확인했다. 양쪽 공식 각2passed·skip0·exit0이며 정본의 현재 TestCase/WORKER/SNAPSHOT을 사용한6fixture의30snapshot·16DB와 실제 두 판본 merge를 검산했다. ordinary 결과/읽기·모든 literal label/pair(빈 label 포함)·opens/import·파일/context/line/arc 및 명시 marker 차이를 현재 단언과 대조했다. 정본 raw의 미러 재사용은 동일 시험 바이트·공식 변환과 별도 미러 공식 실행에 한정하며 미러 fixture raw를 보존했다고 주장하지 않는다.

017 전체 T4의 첫 내부 긴 TEMP 실행은289passed/4failed/2error/exit1이다. Git 없는 fixture가 상위 C:\\math를 찾는4실패와 SHA256 rev-list의 Filename too long2오류를 원trace/현재 입력에 대조했다. 같은 제품의 외부 짧은 TEMP 전체는294passed/1error로 Git6건이 통과했고 설치 probe cwd262자의 WinError267이 남았다. 기존 TestCase의 직접 긴/짧은 경로 대조는262자에서267,241자에서 정상0·반려1을 보였다. parent TEMP와 resource worker output을 함께 짧게 지정한 최종 c4/m4에서 이7ID는 모두 passed다. 두 초기 전체 실패를 소급 성공으로 바꾸거나 제품 수리로 기록하지 않는다. bootstrap2도 현재 passed지만 과거 WinError5 원인은 미확인이다.

최종 c4는295선택 중294passed·1error·exit1, m4는295passed·exit0이다. 정확 오류 ID는 boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once이며 재resume 반려 검사 뒤 TemporaryDirectory cleanup의 WinError32/5다. JobsContract.launch는 job.close를 디렉터리 정리 전에 등록하지만 종료를 기다리지 않는다. 현 WindowsJob.close는 핸들 닫기/kill-on-close 계약이며 root wait·빈Job 확인은 별도다. 종료와 cwd 해제의 경쟁은 가설이고 오류 순간 프로세스/핸들 소유는 미관측이다. 같은ID의 앞선 두 정본/미러 통과를 이 오류의 해소로 세지 않는다.018은 이 한정 cleanup 소비를 검증·수리하고 real/fake 계약과 실제 root/빈Job/cwd 해제를 확인한 뒤 양쪽 전체 T4를 새로 완결한다. runtime 계약 변경이 필요하면 후속 배정으로 반환한다.

네 전체 실행은 각각60worker의 실제 요청/소스875개·게시 artifact SHA·branch DB와 부모 합집합을 검산했고 adapter5개 측정complete다. 최종 c4/m4 도달은 각102/142이며 정보 보고다.015의 정확10실패/오류·2skip은 새 양쪽 전체에서 passed로 연결돼 그 남김을 닫는다. 측정 완전성·미러 성공과 정본 기능 오류는 구별한다. 근거는 run:phases/017/manager-evidence/verification.json·review.md와 원task 자료다. L01·다른 의미/문서 질문 및 G4~G6/G8은 유지한다.'''
assert old in context; context=context.replace(old,new)
context=append_section(context,'C12','''017 F3의 보존 사실을 검수했다. runtime 포함139입력·corpus144경로/150명시SHA·host8원자료/도구·과거910파일·index/pseudo/T3-store와01512/01610 비캐시 제품22경로는 불변이다. 전144경로 Git raw/clean, 공식 --check1336과 skill-only 원출력을 대조했다. 기존 승인된 실호출 성질을 같은 입력/도구 조건에서 한정 재사용한다. 제품22경로의 커밋은 c4 Job cleanup 오류의018 수리/전체 연결 검수까지 보류한다. 이번 관리 마감은 공용 인계·선별 원근거·018 배정·기억만 포함하며 원task 자료와22제품 바이트를 raw-evidence.zip으로 보존한다. 전건SHA·선별 추적 경로는 run:phases/017/manager-evidence/preservation.json에 둔다. 압축으로만 추적되는 scratch/중복snapshot의 원경로와 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있고 압축은 자동 복원 지시가 아니다.''')
assert original['context.md'].split('## C2 ')[0]==context.split('## C2 ')[0]
write(RUN/'context.md',context)

plan=original['plan.md'].replace('## phase 001~016의 결과와 현재 상태','## phase 001~017의 결과와 현재 상태')
anchor='최종 전체 관문은 아직 실행하지 않았다.'
insert='''017은 A1/A2/A4 pass·A3 fail의 partial로 검수했다. 양쪽 두 exact 비교와 정본 raw6fixture/30snapshot/16DB는 성공했고015의12미통과는 새 양쪽 전체에서 passed다. 최종 정본294passed/1error·미러295passed이므로 Job cleanup 오류가 남는다. 초기 내부TEMP Git6실패와 긴resource cwd267은 같은 소스의 환경 대조로 구분했으며 원실패는 유지한다.018은 cleanup 소비 수리와 새 전체 연결을 맡는다. '''
assert plan.count(anchor)==1; plan=plan.replace(anchor,insert+anchor)
s=plan.index('## 다음 phase: 017'); e=plan.index('## 가까운 후속 배정과 선행 관계',s)
plan=plan[:s]+'''## 다음 phase: 018

gpt-6.1-sol/high의 job-cleanup 단일 work를 배정한다.017 c4의 정확한 한 오류와 현재 JobsContract.launch cleanup, WindowsJob.close/terminate/wait/inspect의 계약을 읽고 종료·빈Job·cwd 해제의 관측을 보존한다. LIFO상 close가 먼저 호출된다는 사실은 종료 완료의 증거가 아니다. 기존 close를 동기적 barrier로 재정의하지 않고 시험이 소유한 Job의 정리 순서를 현 API로 고치는 것을 우선한다. 실제 반례/원인 대조와 real/fake 관련 검사를 수행한다. 역사 오류 순간 상태가 없으면 그 한계를 유지하며 재현되지 않는다는 이유로 빈번한 전체 재시도나 무결함 판정을 하지 않는다.

수리와 공식 미러 생성 후 같은 최종 제품·시험 판본에서 양쪽 전체 --tier T4 --jobs 1을 각각 완결한다. parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 자기 전용 경로로 하고 resource worker의 scratch를 줄이도록 자기 evidence/c4·m4를 쓴다. 실제 경로 길이·Git 비저장소 조건을 검증한다. 승인된016 과거 baseline을 공급해 exact2건이 skip되지 않게 한다. 선택/고유row/exit·worker 게시/원DB·adapter5개 정보와 소스 전후를 대조하고 실패를 측정complete로 가리지 않는다. JobsContract와 무관한 provenance/측정이 불변이면017의 정본 raw는 한정 재사용하고 같은 companion을 반복하지 않는다.

제품 runtime·요구·과거 baseline·공유 계측 계약은 고정한다. writes는 공유 Jobs fixture와 그 real/fake 검사·필요한 시험 운전 지침, 공식 대응 미러·비용캐시로 한정한다. 새 결함이 범위를 넘으면 정확 반례/필요파일/영향을 반환한다. 제품 수정과 고정판 전체 검사를 함께 소유해야 하므로 다른 제품 task는 병행하지 않는다. 총worker3 이하·한 묶음씩을 유지하고 새 유료 호출/실예약/학술 호출은 없다.015~016의22제품 마감은018 결과의 manager 검수 뒤 판단한다.

L01 Q1/Q2의 운전 프로필·출력 단위 결정은 계속 남는다. 답변 전에는 원문byte 기준과 미충족 판정을 유지한다. 전체일반/freshT3/전수변이·나머지 의미/문서·최종review는 기존 완료기준대로 남는다.

'''+plan[e:]
plan=plan.replace('정확baseline 비교/전체T4는017에 남긴다.','정확baseline 비교는017에서 통과했고 전체T4는 정본 Job cleanup 오류가 남아018에 넘긴다.')
plan=plan.replace('합22경로의 마감은 그 연결검수까지 대기한다. 근거는016 manager-evidence/verification.json·review.md다.',
                  '합22경로의 마감은018 수리·전체 연결 검수까지 대기한다. 근거는016 및017 manager-evidence/verification.json·review.md다.')
plan=plan.replace('016에서 정확10실패/오류와 관련 양쪽56건을 통과시켰다.017 전체 T4에서 결합 동작을 확인한다.',
                  '016의 정확10실패/오류는017 양쪽 전체 T4에서 모두passed로 검수해 닫았다. 새 Job cleanup 한 오류는018에서 처리한다.')
plan=plan.replace('016의Git원바이트910파일을017이 소비해 양쪽두정확시험과 cleanup 전 raw를 검증한다.',
                  '017에서910파일 실제소비·양쪽각2passed와 정본raw6fixture/30snapshot/16DB를 검수해 이 비교를 닫았다. PR01 다른slice는 유지한다.')
plan=plan.replace('역사raw4개부재/입력준비완료와 실행성공을 구별한다.',
                  '역사raw4개부재와 새 성공을 구별하며 미러 원fixture raw는 별도 보존되지 않았다는 한계를 유지한다.')
plan=plan.replace('017 단일work가 양쪽전체T4의 실제선택/row/exit·각worker·소스/미러와 측정 완전성을 검증한다. manager가22제품경로의마감을판단한다.',
                  '017 c4의294passed/1error와 m4의295passed·각60worker 측정complete를 검수했다.018이 정확cleanup 수리 뒤 양쪽 새전체를 완료하고 manager가22제품경로의마감을판단한다.')
write(RUN/'plan.md',plan)
seams=original['seams.md'].rstrip()+'''\n\n017의 두 exact 비교와 실제 T4 측정·게시 연결을 검수했다.018은 현 Jobs 포트의 launch/resume/terminate/wait/inspect/close를 사용하는 시험 fixture cleanup만 교정한다. close의 핸들 닫기/kill-on-close와 root/빈Job 종료 관측을 구별하며 제품 API 의미를 개정하지 않는다. real/fake 공유 fixture와 관련 시험·전체 T4를 한 task가 소유하므로 새 S 항목·provides/uses는 없다. runtime/계약 개정 필요성은 정확 반례로 다음 manager에 반환한다.\n'''
write(RUN/'seams.md',seams)

inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md',
    M+'verification.json',M+'review.md',M+'source-inspected.json',
    'run:phases/017/tasks/t4-baseline-integration/report.json',
    E+'job-cleanup-review.md',E+'administrative-observations.md',E+'c4/report.json',
    E+'c4/boundary-isolated-027/result.json',E+'c4/boundary-isolated-027/stderr.txt',
    E+'canonical-t4-short.command.json',E+'mirror-t4-short.command.json',
    E+'probe-long-observation.json',E+'probe-short-observation.json',E+'preservation.json',
    'run:phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json',
    'run:phases/016/tasks/t4-fixture-repair/report.json',
    'repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
    'repo:.claude/skills/do-math/scripts/이음새-정본.md','repo:docs/do-math/시험-재편-2026-09-29/설계.md',
    'repo:.claude/skills/do-math/scripts/tests/support/port_contracts/jobs.py',
    'repo:.claude/skills/do-math/scripts/tests/boundary/test_port_jobs.py',
    'repo:.claude/skills/do-math/scripts/tests/contracts/test_port_jobs.py',
    'repo:.claude/skills/do-math/scripts/tests/support/fakes/jobs.py',
    'repo:.claude/skills/do-math/scripts/do_math/windows_job.py',
    'repo:.claude/skills/do-math/scripts/do_math/ports/jobs.py',
    'repo:.claude/skills/do-math/scripts/tests/support/adapter_coverage.py',
    'repo:.claude/skills/do-math/scripts/run_tests.py',
    'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
suffixes=['scripts/tests/support/port_contracts/jobs.py','scripts/tests/boundary/test_port_jobs.py',
          'scripts/tests/contracts/test_port_jobs.py','scripts/tests/시험-지침.md',
          'scripts/tests/.timings.json','scripts/tests/.timings-t3.json']
writes=[tree+'/skills/do-math/'+p for tree in ('.claude','.agents') for p in suffixes]
js(N/'phase.json',{'kind':'work','purpose':'정본 전체 T4의 실제 Job cleanup 오류를 현 종료 계약에 맞춰 검증·수리하고, 짧고 격리된 실행 경로에서 양쪽 전체 T4를 완결한다.',
   'tasks':[{'id':'job-cleanup','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]})
objective=r'''## 목적과 역할

G3/G7의 마지막 확인된 T4 오류인 실제 JobsContract cleanup을 검증·수리한다.017의 두 exact 비교와015의12미통과 해소는 검수됐다. 최종 정본 c4는294passed/1error, 미러 m4는295passed였으며 측정은 양쪽 complete다. 이 work는 정확한 오류의 원인 대조·fixture 수정·관련 회귀와 최종 양쪽 전체 T4를 맡는다. 제품22경로의 커밋 판단은 후속 manager 책임이며 G4~G6/G8·다른 의미/문서/L01을 대신하지 않는다.

## 완료 조건

### A1 정확 오류와 종료 계약의 대조

017 manager source-inspected2675파일과 시작 상태를 대조하고 차이의 출처/영향을 기록한다. 실패 ID boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once의 실제 result/stderr, 앞선 동일 소스 통과와 미러 통과를 구별한다. JobsContract의 enterContext/addCleanup LIFO와 MARK child의 cwd, WindowsJob.close/terminate/wait/inspect, FakeJob·공유 계약을 읽는다. close의 kill-on-close와 종료 완료를 같은 사건으로 간주하지 않는다.

수리 전 자기 evidence의 작은 실제 Job 관측으로 PID/creation FILETIME·소유 Job·root signal·active count/process IDs·cwd와 cleanup 순서를 보존한다. 기존 실패 당시 상태는 없으므로 새 관측을 그 당시 상태로 서술하지 않는다. 시간 지연만 주입하거나 오류 문자열만으로 원인을 확정하지 말고 실제 미종료/종료 대조를 사용한다. 역사 오류의 재현 빈도를 추정하기 위해 전체 T4를 반복하지 않는다. 기존 실제 실패와 확인된 동기화 공백을 근거로 삼을 수 있으며 역사 race가 그대로 재현되지 않으면 그 사실을 밝힌다.

PR02의 해당 Job 소유/종료 slice만 Git 도입 diff·현재 소비·존재하는010/016 근거에 대조해 유지/교정 이유를 적는다. 전체 PR이나 없는 원보고 counts로 검토 범위를 넓히지 않는다.

### A2 실제 종료를 확인하는 최소 fixture 수리와 회귀

시험이 소유한 Job의 종료·빈Job을 확인한 뒤 핸들·TemporaryDirectory를 정리하도록 현 공개 API를 소비한다. JobsContract.launch의 공통 cleanup과 필요한 real/fake 시험만 최소 수정한다. already been resumed 반려, 시작 전 suspended, 정상 marker 실행, 시작 전 종료, 소유자/동명Job 식별 성질을 유지한다. close의 의미를 runtime에서 새 동기 barrier로 바꾸지 않는다. 핸들 해제는 오류 시에도 보장하되 원오류·종료 확인 실패를 숨기지 않는다.

실제 Windows Job에서 정리 전 root_signaled/active_processes/process_ids와 디렉터리 삭제의 성공을 연결한다. suspended·resumed·이미 종료된 시험 소유 Job 상태를 다루고 fake 쪽도 같은 계약을 따른다. 기존 시험으로 충분한 성질은 재사용하며 단순 구현 순서 복제만 검사하는 테스트를 늘리지 않는다. 외부 OS 경계를 대역으로 가려 실제 오류를 없애지 않는다. sleep만 추가·삭제오류 무시·skip·무조건retry·시간 초과를 성공 처리하는 수리는 금지한다. 관찰 대기에는 실제 종료 조건을 사용하고 시간 경과로 Job을 죽이는 새 정책을 도입하지 않는다.

정확 오류 ID와 boundary.test_port_jobs 및 contracts.test_port_jobs를 공식 runner로 검증한다. 두 모듈의 최종 선택·고유row·passed·exit0와 real/fake 차이, 새 반례가 있다면 수리 전후를 보존한다. 별도 원관측은 최종 동작의 증거이지 새 전체 실행을 대신하지 않는다.

### A3 최종 동일 판본의 양쪽 전체 T4

A2·공식 미러 생성 뒤 정본/미러 각각 --tier T4 --jobs 1 전체 선택을 완결한다. 현재 --list와 고유 실제 row가 전건 대응하고 failed/error/skipped/not_run가 없으며 실제 exit0여야 한다.295를 고정 분모로 쓰지 않는다.016의 별도910파일 baseline을 SHARED_INPUT_BASELINE_SCRIPTS로 공급해 exact2건이 실제로 실행되도록 한다.017 raw companion의 입력/현재 TestCase/WORKER/SNAPSHOT·계측이 불변이면 한정 재사용하며 다시 수집할 의무는 없다.

각 report/adapter-coverage·worker의 요청/run_id/소스/게시SHA·branch DB·부모 합집합과 현 adapter5개의 정보 분모를 확인한다. 정보 도달률의 일치/임계 통과는 요구하지 않는다. 측정complete와 기능합격은 별개다.017의 정확 cleanup 오류, 이전015의12미통과와017 환경7ID를 새 전체 row에 대응시킨다. 현재 소스와 도구/실행 전후해시·PID/시작·종료·exit·원자료를 보존한다. 기존 부분성공의 합산이나 미러 성공으로 정본 전체를 통과시키지 않는다.

### A4 환경·보존·인도와 후속 책임

parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 자기 전용 경로를 사용하고 git rev-parse --show-toplevel이 비저장소를 나타내는지 기록한다. resource worker는 output 하위 scratch를 다시 사용하므로 출력도 자기 evidence/c4·m4처럼 짧게 둔다. 현재 기존 installed probe의 실제 최종 cwd가017 성공 조건241자보다 길어지지 않는지 사전에 경로 구성을 확인한다.241자는 이 환경의 보수적 배정 조건이며 보편적인 Windows 상한으로 문서화하지 않는다. 관련 운전 지침에 parent TEMP와 resource output이 서로 다른 경로 조건이라는 실제 교훈을 필요한 만큼 반영한다. 전역 환경이나 OS 정책을 바꾸지 않는다.

수리 범위 밖 runtime139입력·corpus144경로/150명시SHA·host8원자료/도구·baseline910파일·index/pseudo/T3-store와015~016 제품22경로의 바이트를 보존한다. 이번 shared fixture 변경이 기존 실호출의 승인 성질에 영향을 주는지 명시한다. 미러는 공식 생성기의 사전 예상변경을 writes와 대조한 뒤 생성하고 --check/skill-only를 통과한다. 캐시는 성공 근거가 아니다. 이전 report·raw를 고치지 않으며 역사 실패/미관측 한계, G4~G6/G8·남은 의미/문서/L01·제품22경로 Git마감을 유지한다.

## 판단과 경계

변경은 phase writes의 Jobs 공유 fixture·그 real/fake 시험·시험 운전 지침 및 공식 대응 미러/캐시로 한정한다. runtime windows_job·ports·fakes 구현·runner·측정/과거 baseline·설계/요구·공유 계약·corpus·설치 신뢰/기존 연구·다른 phase·공용 문서·Git/기억·engine은 수정하지 않는다. runtime 계약 위반이 실제 원인이라 fixture만으로 해결할 수 없으면 최소 반례/필요파일/소비자 영향을 finding으로 반환하고 해당 A를 fail/not_run으로 기록한다. 별도 권한 요청 없이 허용 범위의 진단과 수리는 진행한다.

task가 소유한 실제 Job/프로세스·전용 임시 경로만 제어한다. 시스템 전체 프로세스 정리·기존 예약·유료 공급자/학술 호출·graphify 갱신·stage/commit/reset/checkout/push는 수행하지 않는다. 바뀌지 않은 전영역 재검토나 무관한 추가 개선은 이 work에 넣지 않는다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. -u -B와 공식 .claude/.agents/skills/do-math/scripts/run_tests.py를 사용한다. 정확 ID 및 boundary.test_port_jobs contracts.test_port_jobs --jobs 1 --output <자기 evidence의 짧은 새 경로>로 관련 검사를 수행한다. 이후 양쪽 전체 --tier T4 --jobs 1 --output <자기 evidence/c4 또는 m4>를 순차 수행한다. 실제 --list·명령·cwd·환경·선택·row·종료를 남긴다. baseline은 C:\math\docs\do-math\continuous-development-2026-10-13\phases\016\tasks\provenance-baseline\evidence\pre-provenance\scripts 이며 전후 manifest 해시를 확인한다.

총worker3 이하·한 묶음씩, 실행 중 제품/시험 판본 고정. result.json 진행 읽기는 do_math.file_io.read_bytes_shared를 사용한다. 도구 yield/관찰 대기 만료를 실제 실패/성공으로 읽지 않는다. 실패 시 해당 원자료를 보존하고 새 수정/명확한 대조 이유 없이 전체를 반복하지 않는다. 이전 성공 검사는 새 영향/실패가 있는 범위만 다시 수행한다. 마지막 지정 Python으로 check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 018 job-cleanup 을 통과하고 report 경로와 상태를 반환한다.
'''
write(N/'tasks/job-cleanup/objective.md',objective)
(N/'tasks/job-cleanup/evidence').mkdir(); (N/'logs').mkdir()

write(O/'review.md','''# phase 017 manager 검수

작업은 partial이다. A1/A2/A4의 지정 성과를 승인하고 A3의 fail을 유지한다. 보고 형식 검사와 실제 원자료 검산은 verify.py/verification.json에 있다. manager는 제품 시험을 다시 실행하거나 제품 파일을 수정하지 않았다.

현재2675소스와 task 종료, 시작과016 manager 판본이 전건 같다. 허용된 양쪽 .timings-t3.json만 변했다. 각 공식 보고의875 Python·소스 전후·실제 선택/고유row/exit를 확인했다. exact는 양쪽2passed다. 원companion 코드의 정상 unittest lifecycle/cleanup 직전 복사를 읽고 task 원자료를 수정하지 않는 재검산으로6fixture·30snapshot·16DB·30child를 대조했다. 현재 TestCase의 marker 단언도 직접 검산했다. 미러 원fixture raw를 보존한 것으로 확대하지 않는다.

네 전체의 각295선택과60worker의 요청·게시·SHA/DB 및 부모 도달·adapter5개 source 분모를 대조했다. 초기 내부TEMP 전체는289/4failed/2error, 외부TEMP 전체는294/1error, 짧은 최종정본은294/1error, 미러는295passed다. 원실패는 남긴다. Git6건과 installed probe 경로 오류는 같은 코드의 환경 대조로 해소됐고015의12미통과는 새 최종 양쪽passed다. 정본 c4의 Job cleanup WinError32/5는 여전히 기능 오류다.

현 close가 핸들을 닫는 동안 Job 종료를 기다리지 않고 shared fixture도 종료 확인 없이 임시 cwd를 삭제하는 코드 사실을 확인했다. 오류 순간 핸들/PID 상태는 없고 인과는 아직 가설이다.018은 기존 Job API를 소비하는 fixture의 종료 순서를 확인·수리하며 제품 runtime 의미를 변경하지 않는다. 실제 원인상 runtime 수리가 필요하면 새 반례로 반환한다. 수리 뒤 관련 real/fake와 최종 양쪽 전체 T4를 맡겼다. parent TEMP와 resource output 경로를 함께 통제한다.

baseline910파일의 전후 manifest·현재 SHA/Git blob, 기존139입력·corpus144/150명시SHA·Git clean·host8/도구·22제품·index/pseudo/T3-store는 보존됐다. 공식 생성/check1336/skill-only 원출력도 확인했다. 원task5919파일은 검산 전후 불변이다. 제품22경로는018 전체 연결 검수까지 보류하고 원바이트와 원task 자료를 archive로 보존한다. G4~G6/G8·L01 외부 결정·나머지 의미/문서 질문은 바꾸지 않는다.

공용 문서는 C2 검수 결과, C5 실행 환경/018 소유, C8 모델, C9 exact 비교의 한정 종료, C10 독립 작업의 현 상태, C11 T4 현재 오류/해소 범위, C12 보존/마감을 갱신했다. C1/G1~G8 원문은 바이트 의미를 유지했다. plan은017 입력소비/전체 실행을018 정확 수리/최종 연결로 바꾸었고 seams는 현 API 소비를 추가 설명했으며 S 계약 개정은 없다. 편집 차이는 common-docs.diff다.
''')
updates=[('C2','017 partial의 A1/A2/A4 성과와 A3 오류를 원자료 검산으로 추가한다.'),
 ('C5','018 단독 소유와 parent TEMP/resource output 경로 조건을 명시한다.'),
 ('C8','기존 사용자 지정 gpt-6.1-sol/high를018에도 적용한다.'),
 ('C9','두 exact 비교의 미실행 남김만 종결하고 PR01/역사raw/미러raw 한계를 보존한다.'),
 ('C10','L01 외부 결정과 독립적인 작업 상태를017 검수/018 수리로 최신화한다. 질문과 byte 기준은 유지한다.'),
 ('C11','baseline 비교·01512미통과 해소와017 환경 대조를 기록하고 새 Job cleanup 오류의 원인 가설/관측 한계·후속책임을 명시한다.'),
 ('C12','불변 입력·기존 실호출의 한정 재사용·원자료 보존과22제품 마감 대기를 갱신한다.')]
manager={'next':'018',
 'decision':'''017 report를 전문으로 읽고 형식 검사와 원자료 검산을 통과시켰다. A1/A2/A4를 승인하고 A3는 fail인 partial로 유지한다. 두 exact 비교는 양쪽 각2passed이고 정본6fixture/30snapshot/16DB/30child의 literal·읽기·분기·marker·merge를 실제 원자료에서 확인했다.015의10failed/error·2skip은 새 양쪽 전체에서 passed다. 최종 c4의294passed/1error와 m4의295passed를 합산해 정본 합격으로 만들지 않는다. 각60worker의 측정complete·adapter5개102/142 정보도 기능 오류와 별개다.

초기 내부TEMP의 Git6건과 resource cwd262자의267은 소스 불변의 외부TEMP/짧은output 대조로 처리됐고 원실패는 보존했다. c4의 정확 Job 재resume 시험은 TemporaryDirectory cleanup에서32/5가 났다. 현 close의 핸들 닫기/kill-on-close와 root/빈Job 확인은 서로 다른 계약이며 shared fixture에는 후자가 없다. 역사 오류 순간 상태는 없으므로 원인을 transient나 runtime 결함으로 확정하지 않는다.

018 job-cleanup은 실제 종료/정리 관측과 최소 shared fixture 수리, real/fake 회귀, 최종 양쪽 전체T4를 맡는다. 현 runtime·요구·baseline은 고정하고 필요한 계약 변경은 반례로 반환한다. parent TEMP와 resource output 경로 조건을 명시한다. 시험 소스/캐시/미러의 고정이 필요한 단일 변경이므로 병렬 제품 task를 두지 않는다. 현재 보고에 없는 무관한 조사 task를 추가하지 않는다. 기존139입력·144corpus·host8·910baseline·22제품 바이트와 승인 성질의 한정 재사용을 유지한다. 제품22경로는018 검수까지 보류하고 관리 인계·선별 근거·기억만 커밋한다. 최종review가 아니고 G4~G6/G8 및 다른 의미/문서/L01이 남아 next:null을 제출하지 않는다.''',
 'reports':[{'task':'t4-baseline-integration','state':'read','detail':'A1/A2/A4 pass·A3 fail의 partial을 원보고/현재 소스/각 공식 선택·row·exit/원DB·cleanup trace와 대조했다. 보고 자체는 유효하고 누락은 없다.',
             'evidence':['run:phases/017/tasks/t4-baseline-integration/report.json',M+'report-check.json',M+'verification.json',M+'review.md']}],
 'dispositions':[
  {'item':'017/t4-baseline-integration/F1','action':'resolve','destination':['run:context.md#C9','run:context.md#C11'],
   'reason':'두exact 성공과01512미통과 해소를 승인한다. 전체 T4의 남은 기능 오류는 F4로 명시 승계하며 이 사실 보고를 전체 합격으로 확대하지 않는다.',
   'evidence':[M+'verification.json',M+'rechecked-raw-verification.json',E+'c4/report.json',E+'m4/report.json']},
  {'item':'017/t4-baseline-integration/F2','action':'resolve','destination':['run:context.md#C5','run:context.md#C11',OBJ+'#A4'],
   'reason':'초기 환경 반례와 소스 불변의 새 대조를 승인하고 다음 실행 조건에 반영했다.262/241은 관측값이며 bootstrap의 과거5 원인은 미확인으로 유지한다.',
   'evidence':[M+'verification.json',E+'probe-long-observation.json',E+'probe-short-observation.json',E+'administrative-observations.md']},
  {'item':'017/t4-baseline-integration/F3','action':'resolve','destination':['run:context.md#C12',OBJ+'#A4'],
   'reason':'139입력·corpus144/150SHA·host8/도구·910baseline·22제품·index/store의 불변과미러/check를검산했다. 한정 재사용과 제품커밋 대기를 보존한다.',
   'evidence':[M+'verification.json',E+'preservation.json',E+'corpus-raw-clean.json']},
  {'item':'017/t4-baseline-integration/F4','action':'carry','destination':['run:context.md#C11','run:plan.md',OBJ],
   'reason':'정확 Job cleanup 오류가 실제 c4 결과에 남는다. 현 close 의미는 유지하면서018이 실제 상태 대조·공유 fixture 종료순서 수리·관련real/fake·최종양쪽전체를 책임진다. 역사 오류 순간 상태를 추측하지 않는다.',
   'evidence':[E+'c4/boundary-isolated-027/result.json',E+'c4/boundary-isolated-027/stderr.txt',E+'job-cleanup-review.md',M+'review.md',OBJ]}],
 'context_updates':[{'item':id,'action':'amend','destination':['run:context.md#'+id],'reason':reason,
                     'evidence':[M+'verification.json',M+'review.md',M+'common-docs.diff',OBJ]} for id,reason in updates],
 'plan_update':'017 exact 비교와01512미통과 남김을 검수해 닫고, 새 c4 Job cleanup 한 오류를018의 실제 상태 관측·fixture 수리·real/fake 회귀·최종 양쪽 전체T4에 배정했다. parent TEMP와resource output을 함께 짧게 통제한다. 동일판본/공유캐시 때문에 단일work다.22제품마감은 수리/연결 검수 뒤로 유지하며 L01·나머지의미/문서·G4~G6/G8·최종review의 선행관계는 유지한다.',
 'seam_updates':[], 'completion':None}
js(P/'manager.pending.json',manager)
diff=''
for n,old in original.items():
    now=(RUN/n).read_text(encoding='utf-8')
    diff+=''.join(difflib.unified_diff(old.splitlines(True),now.splitlines(True),fromfile=n+' before 017',tofile=n+' after 017'))
write(O/'common-docs.diff',diff)
print('Prepared phase 018/job-cleanup and manager.pending.json; common G criteria preserved.')
