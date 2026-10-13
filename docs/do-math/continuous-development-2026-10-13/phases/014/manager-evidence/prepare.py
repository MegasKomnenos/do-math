"""Prepare phase 015 and narrowly amend shared current knowledge."""
from pathlib import Path
import difflib
import json
import re

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'; O=Path(__file__).parent
def read(p): return json.loads(p.read_bytes())
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8')
def js(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert (O/'verification.json').is_file()
v=read(O/'verification.json')
before={n:(RUN/n).read_text(encoding='utf-8-sig') for n in ['context.md','plan.md','seams.md']}
def append_section(text, section, paragraph):
    pattern=rf'(## {section} .*?)(?=\n## C\d+ |\Z)'
    result,n=re.subn(pattern,lambda m:m[1].rstrip()+'\n\n'+paragraph+'\n\n',text,flags=re.S)
    assert n==1,section
    return result
summary='phase 014 scholarly-smoke는 A1~A4 complete로 검수했다. manager report 검사 뒤 시작2726·종료2750파일, 이전013 검수본의 모든 경로 보존과 현재 종료 해시 전건 일치를 확인했다. 허용34변경(비용 캐시2 포함)은 report/writes와 같다. 초기 error1·failed1은 역사 실패로 남기고 최종 정본 T5 1passed/exit0·16판정과 최종 정본/미러 각46고유선택·46passed/exit0 및 각873 Python을 대조했다. 실제 세 CLI 호출은 각각 list_sources 한 요청이며 최종 native의 같은 ID 시작/완료·status=ok와49summary·양 본문, worker/argv/schema·nonce/final·로컬 종료를 확인했다. 초기 structured_content 부재 관측은 잘못된 키 조회였고 원report를 보존한 채 같은 원바이트와 현재 관찰자/최종 offline으로 정정됐다. corpus 각22항목·72파일·409886바이트 및144경로 raw/clean을 검산했다. 근거는 run:phases/014/manager-evidence/verification.json·review.md다. 지정 학술 목록 경계의 완료이며 search/fetch·전체 G 완료가 아니다.'
c=append_section(before['context.md'],'C2',summary)
old=c.split('## C5 병렬 실행과 검증 자원\n\n')[1].split('\n\n')[0]
new='phase 001~014의 task 세션은 종료됐고014 학술 최소 연결을 검수했다.015 t4-adapter-report는 공식 runner의 T4 단독 측정·격리 worker 수집·adapter 보고와 해당 회귀를 한 task가 맡는다. runner/측정 공유 정의·전건 경계 실행·미러 생성기·비용 캐시가 겹치므로 제품 수정/시험을 병행하지 않는다. jobs1을 기본으로 하고 작은 병렬 경로 확인도 전체 worker3 이하·한 묶음씩 실행한다. T4의 status/루프백/임시 Git/로컬 Job·Lean 등 기존 읽기 또는 시험 전용 경계만 사용한다. 새 유료 공급자·예약 변경·학술 검색·연구 운전은 필요하지 않다. 기존 공급자/host/Lean/예약/학술은 불변 입력에서 승인된 성질만 재사용한다. 문서/의미 질문·L01 조건은 후속 책임이다.'
c=c.replace(old,new,1)
c=append_section(c,'C8','014 scholarly-smoke의 gpt-6.1-sol/high 수행을 검수했고015 t4-adapter-report도 같은 설정으로 배정한다.014의 제품 실호출 세 번은 gpt-6-astra/low 요청이며 실제 모델명은 미보고다.015에는 새 유료 실호출을 배정하지 않는다.')
c=append_section(c,'C9','014에서 d03f7d90의 scholarly closed command/args·실행별 data-dir,98ac7e5f의 files scholarly probe,b48dab8f의 worker_request/argv_inputs 정본 이동 slice를 actual diff·현 소비자·존재 원보고와 대조했다. 기존 분리와 입력/격리 계약을 유지하고 성공 완료 의미 검사를 추가한 판단을 승인한다. operator-probe.json은 서술 역사 근거로 존재하지만 그 native stdout/original_result_path는 현재 없다. 역사 counts를 새 성공에 더하지 않으며 다른 hunk·연구 운전·전체 PR은 미종결이다. 근거는 run:phases/014/tasks/scholarly-smoke/evidence/history-original-reports.json·review.md 및 manager 검수다.')
c=c.replace('013 예약 work도 완료했으며014 학술 최소 연결은 이 답변과 독립적으로 진행한다.','013 예약과014 학술 최소 연결도 완료했으며015 T4 보고는 이 답변과 독립적으로 진행한다.')
old=c.split('다음014는 실제 Codex worker가')[1].split('\n\n')[0]
c=c.replace('다음014는 실제 Codex worker가'+old,
'014에서 실제 Codex worker와 설정 서버의 list_sources 성공 완료를 검수했다. 같은 native ID/server/tool의 시작/완료·error=null과 status=ok 전체49summary를 설치 registry/Source.summary에 대조했다.49는 관측값이며 고정 모집단이 아니다. Codex의 native structured_content와 text content가 전부 같음을 원자료와 현재 관찰자로 확인했다. 초기 camelCase 조회의 부재 표시는 원report에 남기고 최종 offline 근거로 보완한다. MCP handshake/협상 protocolVersion/wire isError는 별도 미관측이며 패키지 판본을 그 증거로 대체하지 않는다. worker snapshot·argv 해시·실행별 scholarly-data·파일/checkpoint/final과 confirmed/root-signaled/빈 Job을 확인했다. list_sources는 ArtifactStore._write를 호출하지 않아 data 디렉터리 생성 부재가 정상이다. 초기 bytes 직렬화와 디렉터리 존재 단언의 실패를 유지한다. search/fetch·자료원 계정 접근·원격 종료·실제 모델명/비용까지 확대하지 않는다. 근거는 run:phases/014/manager-evidence/verification.json·review.md와 원task 자료다.\n\n남은 T4 보고의 공백을 현재 run_tests.py에서 재확인했다. Measurement는 T3 조건에서만 생성되고 resource/lean 클래스의 _isolated 호출은 measure를 전달하지 않는다.015는 T4 단독의 실제 boundary 선택과 격리 worker 분기 자료를 수집해 현 LAYERS adapter 전체를 별도 보고한다. 분기 도달률은 통과 임계값이 아니며 측정 누락은 완전한 보고로 처리하지 않는다. T3 모집단·선택 색인·증분 저장소에 T4를 섞지 않는다. 책임은 run:phases/015/tasks/t4-adapter-report/objective.md다.13-C/L01·나머지 문서/의미 질문과 G4~G6/G8 최종 관문도 남는다.')
c=append_section(c,'C12','014 F2/F4의 원자료 보존과 한정 재사용을 검수했다. runtime124를 포함한139입력·host8원자료·도구 SHA, 기존21corpus 항목/verdict와122비manifest 경로가 유지됐다. 성공 녹화1항목·10원파일을 추가했고 현재 각22항목72파일409886바이트·75명시SHA 및144경로 Git raw/clean·미러 바이트가 일치한다. 공식 --check1334파일과 양쪽46회귀가 통과했다.129공식 변환 입력과 미러 offline은 정본 실호출의 한정 재사용이며 새 미러 유료호출0이다. 초기 두 공식 실패와 structured-content 오관측은 소급 수정하지 않는다. 이번 검수 제품·시험·지침·미러32경로를 관리 커밋으로 마감하고 비용 캐시2개는 제외한다. 원task 자료와32제품 원바이트는 raw-evidence.zip에 보존한다. 선별 추적 경로·압축 항목·SHA는 run:phases/014/manager-evidence/preservation.json에, stage/commit 행정 수신은 로컬 commit.json에 둔다. 압축으로만 추적되는 scratch 원경로와 행정 수신은 로컬 정리로 사라질 수 있으며 압축은 자동 복원 지시가 아니다.015 배정·공용 문서·기억 추가는 검증한 제품 바이트를 바꾸지 않는다.')
assert c.split('## C2 ')[0]==before['context.md'].split('## C2 ')[0]
write(RUN/'context.md',c)

p=before['plan.md'].replace('## phase 001~013의 결과와 현재 상태','## phase 001~014의 결과와 현재 상태')
p=p.replace('최종 전체 관문은 아직 실행하지 않았다.','014 학술 A1~A4도 검수했다. 최종 T5 1건·양쪽46회귀, 동일 native의 완료/양 본문/registry/격리와144corpus 경로를 승인했고 초기 두 실패·오관측의 적용 범위를 보존했다. 최종 전체 관문은 아직 실행하지 않았다.',1)
a=p.index('## 다음 phase: 014'); b=p.index('## 가까운 후속 배정과 선행 관계')
p=p[:a]+'''## 다음 phase: 015

t4-adapter-report 단일 work를 gpt-6.1-sol/high로 배정한다. 설계5.5의 남은 T4 adapter 분기 보고를 공식 run_tests.py에 연결한다. 현재 T4는 Measurement를 만들지 않으며 lean/resource 격리 클래스도 측정 자료를 반환하지 않는다. 기존 실행/Job/정상 결과 경로를 유지하며 현재 LAYERS의 adapter5개를 빠짐없이 보고하고 실제 worker 측정과 부모 병합·누락 처리를 검증한다. 도달률을 임계 관문으로 만들지 않고 보고의 완전성과 시험 성공을 구별한다. T3의 대상·fresh 선택·저장소·색인·변이 정상 기준은 보존한다.

공식 runner·측정 정의·회귀·전체 T4 실행·미러/비용 캐시를 한 task가 순차 소유한다. 같은 runner가 모든 시험의 실행과 결과를 통제하므로 독립 제품 수정/시험 task를 함께 배정하지 않는다. 새 seam은 없으며 범위와 A는 run:phases/015/phase.json 및 objective다. 정본과 미러 T4 전건 및 지정 runner/branch 회귀를 수행하고 전체 일반/T3/변이와 새 T5 유료호출은 후속 관문에 남긴다.014의 검수된32제품경로는 현재 관리 마감에 포함한다.

L01의 Q1/Q2는 외부 결정으로 남는다. 공급자별 운전 host/tool/판본/model/호출 설정과 출력 byte 기준 유지 또는 도구 단위 개정을 확정해야 한다. 이미 상신한 선택의 답변이 없으므로 원문 byte 기준과 미충족을 유지한다.011 문구 수리와012~014 경계 성공은 읽기 용량 인증이 아니며015 보고 작업은 이 답변과 독립적이다.

'''+p[b:]
p=p.replace('013 예약 실연쇄를 검수했고 제품20경로를 마감하며014 학술 MCP 경계로 진행한다. 근거는013 manager-evidence/verification.json·review.md다.','013 예약 제품20경로는 8d0ade6c으로 마감됐다.014 학술 최소 연결을 검수했고 제품32경로를 마감하며015 T4 보고로 진행한다. 근거는014 manager-evidence/verification.json·review.md다.')
p=p.replace('014는 Codex worker를 통한 학술 list_sources의 실제 성공 완료·결과와 격리·녹화/재생을 맡는다.','014의 Codex worker를 통한 list_sources 성공 완료·전체 결과와 격리·녹화/재생도 검수했다. 각 경계의 최종 판본 재사용 조건을 유지한다.')
p=p.replace('T4 단독 전체 boundary 선택에 별도 adapter 분기 측정을 연결해 실제 보고를 만든다.','015에서 T4 단독 전체 boundary 선택·격리 worker를 측정하고 현 adapter 전체의 분기 보고와 누락 처리를 완결한다.')
write(RUN/'plan.md',p)
seam=before['seams.md'].rstrip()+'''\n\n014의 기존 scholarly API 소비·성공 완료/양 본문·격리와 녹화 재생을 검수했다.015는 run_tests.py의 main/_isolated/_worker/결과 집계와 tests/support/branch_gate.py의 측정/저장/병합 정의, do_math.layers.LAYERS를 기준으로 T4 보고를 연결한다. 시험 결과와 측정 완전성·분기 도달 보고는 구별하고 T3 gate·선택 색인·증분 저장소 의미를 유지한다. 같은 task가 생산자/소비자·회귀를 함께 수정하므로 별도 S 항목이나 provides/uses는 추가하지 않는다. 새 보고 형식의 정본은 구현의 실제 선언과 검증으로 두며 자연어의 중복 schema를 만들지 않는다.015 task가 지침과 생산/소비 시험을 같은 변경으로 맞춘다.\n'''
write(RUN/'seams.md',seam)
diff=''.join(''.join(difflib.unified_diff(before[n].splitlines(True),(RUN/n).read_text(encoding='utf-8').splitlines(True),fromfile=n+' before',tofile=n+' after')) for n in before)
write(O/'common-docs.diff',diff)

next_root=RUN/'phases/015'; objective=next_root/'tasks/t4-adapter-report/objective.md'
assert not (next_root/'phase.json').exists()
files=['run_tests.py','tests/support/branch_gate.py','tests/support/adapter_coverage.py','tests/unit/test_runner_tiers.py','tests/unit/test_runner_regressions.py','tests/unit/test_branch_gate.py','tests/unit/test_adapter_coverage.py','tests/시험-지침.md','tests/.timings.json','tests/.timings-t3.json']
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json','run:phases/002/tasks/mutation-baseline/report.json','run:phases/014/tasks/scholarly-smoke/report.json','run:phases/014/manager-evidence/verification.json','run:phases/014/manager-evidence/source-inspected.json','run:phases/014/manager-evidence/review.md',
'repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/이음새-정본.md','repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs += ['repo:.claude/skills/do-math/scripts/'+p for p in ['run_tests.py','test_categories.py','do_math/layers.py','tests/시험-지침.md','tests/support/branch_gate.py','tests/support/t3_store.py','tests/unit/test_runner_tiers.py','tests/unit/test_runner_regressions.py','tests/unit/test_branch_gate.py']]
js(next_root/'phase.json',{'kind':'work','purpose':'014 학술 경계 검수 뒤 설계5.5의 T4 단독 adapter 분기 보고 공백을 공식 runner와 실제 격리 worker/병합 경로에 연결한다. T3 관문·색인·저장소 의미를 보존한다.','tasks':[{'id':'t4-adapter-report','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':[tree+'/skills/do-math/scripts/'+p for tree in ['.claude','.agents'] for p in files],'provides':[],'uses':[]}]})
write(objective,'''## 목적과 역할

G7과 설계5.5의 T4 adapter 분기 보고를 완결한다. 현재 run_tests.main은 T3에만 Measurement를 생성하며 resource/lean 클래스의 _isolated에는 measure가 전달되지 않는다. T4의 실제 경계 시험이 성공해도 adapter 도달 보고는 없다. 기존 공식 runner·coverage 자료 처리·Job 격리를 재사용해 T4 단독 선택에서 실제 측정/보고를 만들고, 자료 누락을 드러내는 시험과 실제 T4 전건을 연결한다. 새 제품 동작이나 도달률 관문을 만드는 작업이 아니다.

## 완료 조건

### A1 현재 경로와 실패를 확정

014 manager source-inspected와 시작 판본을 대조한다. 설계5.1/5.5/8, gate-readiness의 T4 남김, 현재 TIERS·LAYERS·main/_isolated/_worker와 Measurement의 start/save/merge/finish를 읽고 무엇이 측정되지 않는지 실제 실행으로 재현한다. 작은 기존 boundary 선택에 --tier T4를 주어 시험 성공과 adapter 보고 부재를 구별하거나, 그 실제 경로를 소비하는 새 회귀의 red를 보존한다. 기대값은 LAYERS adapter 분류·현재 coverage 분석과 지정 시험이 실행한 분기에서 얻고 보고의 구현값을 그대로 복제하지 않는다.

관련 과거 runner/Measurement 도입은 git log로 이 변경에 필요한 slice만 좁혀 actual diff·현재 소비자·존재 원보고를 대조한다.002 정상 기준 수리와 기존 T3/D5/D6/D9/D11 의미를 유지하며 없는 역사 counts를 새 성공에 합산하지 않는다. 새 의미 문제는 해당 원문 G와 구체적 반례로 반환한다.

### A2 공식 T4의 실제 측정과 별도 보고

--tier T4 단독 실행에서 선택된 boundary의 인프로세스·lean/resource 격리 worker를 실제로 측정하고 부모가 해당 실행의 자료를 합친다. 현재 LAYERS에서 adapter로 분류한 파일 전부(현재5개)를 열거하고 파일/소스 판본·실행/미실행 분기·누락/제외 및 합계를 추적 가능하게 보고한다. 도달0인 파일도 사라지지 않는다. coverage의 실제 분석과 사유 있는 제외 계약을 사용하며 source에서 분모를 얻는다. 제품의 임의 외부 자식/PowerShell/Lean 내부까지 Python 측정됐다고 보고하지 않는다.

분기 도달률은 정보 보고이며 임계값이나 새로운 G로 만들지 않는다. 시험 성공·skip/fail/error/not_run과 측정의 완전성을 구별한다. 필요한 worker 자료의 부재·파손·다른 실행/판본 자료를 정상 측정 또는 도달0으로 숨기지 않고 불완전 사유와 원경로를 남긴다. 자료가 불완전한 실행을 완전한 T4 보고로 승인할 수 없게 한다. 실제 시험 실패와 runner exit의 기존 의미도 유지한다.

측정은 시험의 실제 실행을 관찰해야 한다. 부모의 보고 직렬화나 자체 파일 읽기를 시험이 실행한 분기로 세지 않는다. worker 자료는 자기 새 출력 폴더에 두고 Job/실제 종료·오류 보존·시간 자동 종료 없음의 계약을 유지한다. 새 옵션이나 중복 측정기를 늘리기 전에 기존 작은 정의를 재사용한다. 필요하면 허용된 adapter_coverage.py에 T4 전용 보고 정의를 두고 생산자와 소비자 시험이 같은 정본을 쓰게 한다.

T4 단독은 T3 gate·선택 색인·증분 저장소·pseudo_tested/변이 결과를 갱신하지 않는다. T3의 1/2/3층 gate 및 fresh 선택을 바꾸지 않는다. 여러 tier 합집합에서 T4 자료가 T3 분모/선택 색인에 섞이지 않는 동작을 명시하고 회귀로 확인한다. 기본 전체 일반 선택과 위치 인자/교집합·모르는 ID/빈 선택 반려·부분 T3 색인 보호도 유지한다. 새 보고 key/파일의 구체 형식은 구현 재량이며 실제 코드와 지침·검사가 정본이다.

### A3 실제 worker 반례와 관련 회귀

기존 공식 runner를 거치는 작은 실제 child/격리 표본으로 측정이 worker의 알려진 분기를 포함하는지 확인한다. T4 측정 부재 red와 교정 green을 보존한다. 자료 누락/파손 또는 판본 불일치에서 완전 보고가 나오지 않는 음성 사례, 미도달 파일 포함, 보고 작업에 의한 거짓 도달 방지, 시험 실패/건너뜀·실행 누락을 가리지 않는 결과를 검증한다. 대역이 필요하면 외부 실패 주입에 한정하고 실제 측정·병합·보고를 대역으로 가리지 않는다.

공식 runner로 unit.test_runner_tiers, unit.test_runner_regressions, unit.test_branch_gate와 새 unit.test_adapter_coverage(만들었을 때)를 실행한다. 관련 T3 store/index/정상 기준 회귀는 이 모듈의 기존 선택을 재사용하며 변경이 직접 영향을 주는 정확 ID만 추가한다. 전체 T3/변이를 회귀 대신 실행하지 않는다. jobs1 및 작은 jobs2 경로를 실제 지원 범위에 맞춰 확인하되 전체 동시 worker3 이하·한 묶음씩 지킨다. 제품 do_math와 기존 boundary 시험은 이번 writes 밖이므로 외부 결함이면 원자료와 후속 범위를 반환하고 억지 기대값 수리는 하지 않는다.

### A4 T4 전건·미러·인도 근거

교정 뒤 정본과 공식 미러 각각 --tier T4 --jobs 1의 전체 기본 boundary 선택을 완결한다. --list 모집단, 실행 선택/고유row/실제exit, 정상/오류/skip/not_run과 실행 전후 소스, 측정 worker 목록과 보고된 adapter 모집단을 대조한다. 원자료와 실제 보고 파일을 자기 evidence에 보존한다. 환경 때문에 실행할 수 없는 항목은 정확 조건을 밝히고 해당 A를 통과로 만들지 않는다. 필요한 수리 없이 이미 성공한 전건을 반복하지 않는다.

지침에 T4 측정 범위·격리/병합·미도달/불완전 해석·T3와의 구분을 적는다. 공식 미러 생성의 사전 변경 범위를 writes에 맞추고 생성한다. 양쪽 지정 runner/branch 회귀와 T4를 확인한 뒤 마지막 비용 캐시만 동기화하고 --check/skill-only를 통과한다. 기존 runtime/공급자·host·Lean·예약·학술 입력/녹화 바이트의 보존을 확인해 승인된 실제 호출의 재사용 범위를 명시한다. runner 변경은 최종 G4/G5 실행 판본과 증분 T3 무효화 판단에 영향을 준다는 점을 기록한다. 최종 일반/fresh T3/전체 변이·문서/의미 질문·L01·최종 review는 후속 manager 책임이다.

## 판단과 경계

phase.json의 runner·측정/보고 지원 정의·정확 회귀 파일·시험 지침·비용 캐시와 대응 미러만 수정한다. do_math runtime/layers·기존 boundary/smoke·corpus·설정/설치·engine·공용 문서·원보고는 고치지 않는다. 정본 문서의 요구를 낮추거나 adapter 도달률을 관문으로 바꾸지 않는다. 기존 도구/실제 포트/Job 및 T4의 읽기 status·시험 전용 임시 자원은 사용한다. 새 유료 모델/학술 검색·실예약 변경·기존 연구 재개·권한 상승·Git stage/commit/reset/checkout/push·graphify 갱신은 하지 않는다. 원문과 구현의 차이가 쓰기 범위를 넘으면 최소 반례·정확 파일·필요 조치를 보고하고 독립 가능한 나머지는 완결한다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 모든 시험은 공식 정본/미러 run_tests.py에 -u -B와 정확 ID 또는 --tier T4, --jobs 1, --output <자기 evidence의 새 폴더>를 사용한다. 작은 병렬 확인은 --jobs 2이며 전체 worker3 이하다. 한 검사 묶음씩 실행하고 실행 중 제품/시험 트리를 고정한다. 실제 command/PID/시작/종료/exit·선택/row·원로그와 소스 SHA를 보존한다. 대기 도구의 yield는 실행 실패가 아니다. 진행 result.json은 기존 read_bytes_shared로 읽는다. 시간은 소프트 기준이며 timeout/재시도/측정 누락을 성공으로 바꾸지 않는다.

마지막 Python -B services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 015 t4-adapter-report를 통과하고 report 경로와 상태를 반환한다.
''')
(next_root/'logs').mkdir(exist_ok=True); (objective.parent/'evidence').mkdir(exist_ok=True)

write(O/'review.md','''# Phase 014 manager 검수

scholarly-smoke의 A1~A4를 지정 범위에서 승인한다. report 형식 검사 뒤 종료2750파일과 현재 해시, 시작2726파일 및013 manager의 기존 경로, 허용34변경을 대조했다.7개 공식 보고의 선택/고유row/실제exit·소스 전후를 확인했고 최종 양쪽46건/873 Python은 현재 판본과 같다. live-final 뒤 observer/replay가 바뀐 범위는 호출 입력/runtime 변화와 구별한다.

최종 원native에서 정확 한 scholarly/list_sources의 시작/완료 ID·arguments={}·completed/error=null, status=ok와49개 전체summary를 registry 자료에 대조했다. text와 native structured_content는 같고 서버 list_sources/Source.summary의 현재 코드를 확인했다. 최초 camelCase 조회의 부재 표시는 원smoke에 남아 있다. 현재 observer와 양쪽 최종 offline이 같은 성공 녹화를 다시 검사하므로 별도 유료 호출 없이 그 관측을 정정할 수 있다. 초기 bytes 직렬화 error와 lazy ArtifactStore 디렉터리 단언 failed는 그대로 보존한다. server.py가 목록만 반환하고 ArtifactStore._write에서만 mkdir하므로 존재 단언 제거는 제품 오류 은폐가 아니다.

worker 요청/argv·stdin/schema 해시·workspace scholarly-data·nonce/final·confirmed/root-signaled/빈 Job을 독립 대조했다. exact checkpoint는 task의 보존 원자료/16판정과 실제 helper가 고정 기대값을 검사한 경로를 확인했다. 성공 호출1개와 세 실제 CLI 실행을 구별한다. wire 초기화/negotiated protocolVersion/isError, 실제 모델명·비용·원격 종료는 미관측이며 목록의 verification 값은 이번 search/fetch 인증이 아니다.

15파생 음성 사례가 실제 원녹화 대조군을 사용하고 정확 반려 원인을 검사함을 소스 diff와 최종 row에서 확인했다. registry 기대값은 installed_registry의 실제 서버 Python/Source.summary에서 왔다. 원 promotion10파일과 corpus 바이트, 기존21항목/verdict·122비manifest경로, 각75SHA·전체144경로 raw/clean 및 공식 --check1334를 대조했다. runtime124 포함139입력·host8원자료/도구 SHA는 보존됐다. 공식 미러 회귀와 변환은 한정 재사용이며 미러 live를 새로 실행하지 않았다.

d03f7d90/98ac7e5f/b48dab8f의 지정 입력·격리·worker 정의 이동은 actual diff와 현재 소비·존재 operator-probe 서술 보고를 확인한 범위에서 유지한다. 사라진 native 경로와 역사 counts는 현재 완료 근거에 포함하지 않는다. 다른 hunk나 전체 PR을 닫지 않는다.

다음015는 설계5.5의 T4 adapter 보고다. 현재 main의 T3 전용 Measurement 생성과 resource/lean _isolated의 측정 전달 부재를 직접 확인했다. 현재 adapter5개를 전부 보고하고 격리 자료를 실제로 병합하되 도달률을 관문으로 만들지 않도록 배정한다. 같은 runner/측정·캐시/미러·전체 T4를 공유하므로 독립성이 없는 병렬 work를 추가하지 않는다. L01 외부 결정, 다른 문서/의미 질문, G4~G6/G8과 최종 review는 유지한다. G1~G8 문면은 변경하지 않았다.

공용 문서의 C2는014 검수 근거를 추가했고 C5/C8은015 책임/모델로 갱신했다. C9는 한정 이력 처분, C10은외부결정과독립작업의현재상태, C11은학술남김종결과T4구체공백, C12는보존/커밋범위를 반영했다. plan의014 배정을015로 교체했고 기존 나머지 남김·원문 조건은 보존했다. seams에는 단일 task의 기존정의소비를 기록하며 S 계약개정은없다. 편집 차이는 common-docs.diff다.
''')
base='run:phases/014/manager-evidence/'
evidence=[base+'verification.json',base+'review.md']
dest=lambda cid:['run:context.md#'+cid]
manager={'next':'015','decision':'014 scholarly-smoke의 A1~A4를 report 검사와 원자료/현재 판본 대조 후 승인한다. 최종 T5 1건과 양쪽46회귀는 지정 학술 목록 경계의 증거다. 초기 두 실패·structured_content 오관측은 보존하고 같은 raw의 현재 검사로 해소한다. 세 실제 호출·미러 새 호출0·wire/비용/원격 종료 한계를 유지한다. 모든 findings를 해당 범위로 종결하되 전체 G의 완료로 확대하지 않는다. 다음015는 실제 T4 adapter 보고 공백을 runner/격리 worker/부모 병합에 연결하는 단일 work다. 공유 runner·측정·캐시·미러 때문에 동시 제품 task는 독립적이지 않다. 코드 수정은 task가 맡으며 manager는32제품경로의 검수/원자료 보존·공용 인계·기억/로컬 커밋만 수행한다. G4~G6/G8·문서/의미 질문·L01 외부 결정을 유지하므로 next:null 조건은 충족하지 않는다.',
'reports':[{'task':'scholarly-smoke','state':'read','detail':'전문을 읽고 report 검사 PASS. A1~A4 pass를 지정 성질로 승인했다. 종료2750소스·34변경/writes·7실행 선택/row/exit·native/registry/worker·corpus와 현재 미러를 검수했다.','evidence':['run:phases/014/tasks/scholarly-smoke/report.json',base+'report-check.json',*evidence]}],
'dispositions':[], 'context_updates':[], 'plan_update':'014의 지정 학술 경계를 완료 상태로 갱신하고015 단일 t4-adapter-report를 배정했다. T4 전건/격리 측정·누락 보고와 T3 독립성, 관련 회귀/미러 책임을 명시했다. 실제 경계의 승인 범위와 전체 일반→fresh T3→전체 함수 변이→최종 review의 선행 관계, 문서/의미 질문 및 L01 외부 결정은 보존했다. G 기준의 변경은 없다. 편집 전후는 manager-evidence/common-docs.diff로 대조했다.', 'seam_updates':[], 'completion':None}
reasons=[('F1','C11','native 시작/성공 완료·전체 registry/양 본문·격리/로컬 종료를 대조하여 list_sources 경계를 닫았다. 관측 밖 wire/원격/검색·비용은 완료로 확대하지 않는다.'),('F2','C12','초기 실패와 잘못된 키 관측은 원보고 그대로 유지하고 동일 raw의 현 observer·최종46회귀로 해소했다. 성공 호출을 다시 실행할 변경 근거가 없다.'),('F3','C9','지정 입력/격리/worker 정본 이동 slice만 유지한다. 존재 서술 보고와 없는 원native를 구별하고 다른 hunk/전체 PR은 미종결로 유지한다.'),('F4','C12','139입력·기존 corpus/원자료 불변과 양쪽46회귀·144 raw/clean·미러 확인을 검수했다.32제품경로/선별 근거/원바이트 archive를 관리 마감하며 다른 관문은 계속 남는다.')]
for fid,cid,reason in reasons: manager['dispositions'].append({'item':'014/scholarly-smoke/'+fid,'action':'resolve','destination':dest(cid),'reason':reason,'evidence':evidence})
for cid,reason in [('C2','014의 현재판본/실행/원자료 검수 결과를 추가하며 과거 partial을 보존한다.'),('C5','014 종료 뒤015 runner/측정 공유 자원의 순차 소유와 실제 T4 범위를 지정한다.'),('C8','사용자 지정 gpt-6.1-sol/high를015에 유지하고 제품 호출 모델과 구별한다.'),('C9','학술 지정 이력 slice의 유지와 역사 raw 부재 한계를 추가한다.'),('C10','L01 외부 결정은 유지하고 독립014 완료/015 진행 상태만 갱신한다.'),('C11','학술 완료 응답 공백을 현재 증거로 닫고 T4 단독·격리 측정 공백 및 다음 책임을 구체화한다.'),('C12','초기실패/오관측 보존·최종범위·기존근거 재사용·32경로 마감과 raw 추적 범위를 기록한다.')]:
    manager['context_updates'].append({'item':cid,'action':'amend','destination':dest(cid),'reason':reason,'evidence':evidence+[base+'common-docs.diff']})
js(RUN/'phases/014/manager.pending.json',manager)
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0563.md'
write(R/'기억/layer1/M-0564.md','''---
id: M-0564
layer: 1
title: 학술 완료 응답을 검수하고 T4 분기 보고를 배정함
convention_version: 27
---

## 맥락

014는 Codex worker가 실제 학술 MCP list_sources를 완료하고 전체 자료원 요약을 받는 경계를 맡았다. 기존 probe는 도구 시작 이름만 보았으므로 새 live/replay 관찰자가 같은 ID의 성공 완료와 registry.Source.summary를 검사했다. manager는 native text와 structured_content 전체가 같음을 직접 대조했다. 목록에 있는 과거 verification 문자열은 이번 계정 접근이나 search/fetch 성공의 증거가 아니다.

## 판단의 조건

초기 관찰자는 camelCase 키를 읽어 structured 본문을 부재로 기록했다. 원smoke와 처음 offline 보고는 보존하고, 같은 원바이트를 현 observer와 최종 양쪽46건으로 재검사해 관측을 정정했다. 호출 입력과 runtime이 같으므로 정정에 새 유료 호출은 필요하지 않았다. 초기 bytes 직렬화와 lazy data 디렉터리 단언의 두 실패도 성공으로 소급하지 않았다. 디렉터리는 ArtifactStore._write에서 만들어지고 list_sources는 그 경로를 쓰지 않는다. 기대 동작은 폴더 존재라는 대리 표지보다 실제 서버 원문에서 정했다.

## 다음 책임과 보존

015는 T4 단독 실행의 adapter 분기 보고를 맡는다. 현재 runner는 T3에만 Measurement를 만들고 격리 resource/lean 호출에는 측정을 전달하지 않는다. 부모만 측정해 보고서 파일을 만드는 것으로 이 공백을 닫지 않도록 실제 child 자료·병합·누락 반례를 배정했다. 도달률은 정보 보고이며 임계 관문이 아니다. T3의 gate/선택 색인/증분 저장소와 분리한다.

추적 진입점은 `docs/do-math/continuous-development-2026-10-13/phases/014/manager.json`, `manager-evidence/verification.json`, `review.md`, `preservation.json`과015 objective다. 원task 자료와32제품경로 원바이트는 `raw-evidence.zip`에도 보존한다. 압축으로만 추적되는 scratch 원경로와 stage/commit 행정 수신은 로컬 보관이며 정리로 사라질 수 있다. 압축은 자동 복원 지시가 아니다. 최종 일반/fresh T3/변이/review와 문서/의미 질문·L01 외부 결정은 계속 남는다.
''')
index=R/'기억/색인.md'; s=index.read_text(encoding='utf-8'); assert 'M-0564' not in s
write(index,s.replace('## layer-1\n','## layer-1\n\n- M-0564 [학술 완료 응답을 검수하고 T4 분기 보고를 배정함] -- 같은 native의 양 본문 정정·양쪽46건 승인, T4 격리 측정과 T3 분리 책임\n',1))
print('Prepared 015 and pending 014; preserved all G criteria and unrelated common knowledge')
