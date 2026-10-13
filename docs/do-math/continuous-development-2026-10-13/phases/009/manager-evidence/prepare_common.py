"""Update current common knowledge with an inspectable semantic diff."""
import difflib
import json
from pathlib import Path
ROOT=Path(r'C:\math')
RUN=ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
before={n:(RUN/n).read_text(encoding='utf-8-sig') for n in ('context.md','plan.md','seams.md')}
def once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new)
def paragraph(text,start,new):
    a=text.index(start)
    b=text.index('\n\n',a)
    return text[:a]+new+text[b:]
c=before['context.md']
c=once(c,'## C3 현재 정본과 이력의 역할','''phase 009 document-callable은 A1~A3 complete로 검수했다. report 검사 후 현재2640파일과 종료 해시 전건 일치, 시작과008 종료 동일, 허용된 문서2·캐시2 변경만 있음을 확인했다. 원문에는 함수명 뒤 (...) 다섯 바이트만 추가됐다. 실제 callable·필드 검사와 nonexistent/noncallable 반려를 유지한 채 정본110·미러89 선택/고유row가 전건 passed·exit0이며008의 정확4실패가 양쪽 새 passed row에 연결된다. 각865개 Python과 문서의 실행 전후/현재 해시도 일치한다. task의 첫 mirror 계획 exit1은 개행 처리 오류로 제품 변화0이었고 수정 뒤 성공했다. manager 검산 첫 실행의 누락 인자 TypeError도 관리 스크립트만 고쳐 재검산했다. 검수 HEAD는 0af5dd66368b7409899b6eed5b04523db43db4c5, 근거는 run:phases/009/manager-evidence/verification.json·review.md다.008의 partial 원보고는 보존하고 그 F1/A5 남김만 새 근거로 닫는다. 전체 G 완료가 아니다.

## C3 현재 정본과 이력의 역할''')
c=paragraph(c,'phase 001의 독립 분석 세 task와 phase 002~008의 단일 work task는 종료됐다.','''phase 001~009는 종료됐고009의 문서4실패 해소를 검수했다.010은 host-smoke와 reading-limits 두 work task를 병렬 배정한다. host-smoke만 host 시험·공유화 대상3개 boundary·시험 지침·미러·비용 캐시를 쓰며 공식 검사를 jobs1·한 묶음씩 실행한다. reading-limits는 writes=[]로 고정된 SKILL/운전 문서·contracts/context_store/cli_worker 및 호스트 읽기 계약만 조사한다. 변경 중인 시험·지침·캐시·미러와 host 결과를 입력으로 쓰지 않고 공식 시험·유료 호출·생성기를 실행하지 않는다. 두 task는 DB/포트/잠금·임시 출력도 공유하지 않는다. 후속 Lean·예약·학술은 개별 실제 연쇄로 배정하며 이 phase의 미완성 구현에 기대지 않는다.''')
c=once(c,'phase 008은 A1~A4를 승인하고 A5의 기존 문서4실패를009로 넘긴 partial이다.','phase 008은 A1~A4를 승인한 partial이고 A5의 문서4실패는009의 A1~A3 complete로 해소했다.010의 두 task도 gpt-6.1-sol/high로 배정한다.')
c=paragraph(c,'008 F1과 A5는 미해결이다.','''008 F1/A5의 전건 관련 회귀 남김은009에서 해소됐다. CLI-실행-계약의 bare dotted 함수명을 provider_final.output_contract(...)로 교정해 기존 function_reference_issues의 실제 callable 검사에 연결했다. helper/schema/unknown/defer/runtime/시험 소스는 바꾸지 않았다. 정본110·미러89 선택은008과 같고 정확4실패가 모두 passed이며 현재 소스와 원보고 판본을 manager가 대조했다. P01 운영/복구와 N03-003 설치 설명의 지정 성과 및 관련 회귀를 닫고008~009 변경 단위를 마감한다. N03의 다른 절·P02~P11은 그대로 남는다. 근거는 run:phases/009/manager-evidence/verification.json·review.md다.''')
c=once(c,'P01의 검수된 지정 성과와009의 회귀 남김, P02 원자료/과제 결과','P01과009에서 종료한 지정 회귀, P02 원자료/과제 결과')
c=once(c,'G7의 설치 CLI/실호출 확인 때 호스트의 실제 출력 절단·읽기 설정을 함께 조사한다.','010 reading-limits가 현재 host/tool/version/read-call별 권위 있는 한도와 실제 절단·구간 회수 근거를 조사한다. 제품 구현이나 유료 호출과 독립화했고 확인 불가능한 경계는 정확한 외부 결정으로 반환한다.')
c=once(c,'## C12 공급자 부분 성공과 원바이트 인도','''010 host-smoke는 기존 실제 Job·pythonw boundary 경로를 확인해 공식 T5의 해당 설치 연쇄를 연결한다. 새 스모크·필요한 공유화·원실행 녹화만 맡고 runtime/공급자/corpus 계약은 바꾸지 않는다. 실제 OS 예약 등록·발화·해제, Lean/Mathlib, 학술 MCP와 T4 별도 adapter 분기는 이후 책임이다.010 reading-limits의 조사 완료는13-C 충족과 구별한다. 구체적 A/쓰기/선택은 run:phases/010/phase.json과 두 objective다.

## C12 공급자 부분 성공과 원바이트 인도''')
c+='''
009 F2의 보존 사실을 검수했다. 현재 runtime124·smoke입력3·양쪽 corpus102경로와 속성/생성 규칙은008과 같아 기존 실호출 및 명시SHA/Git clean의 한정 근거를 유지한다. --check1305파일·skill-only verified의 원출력과 판본도 확인했다.008~009의 승인된 제품·시험·문서·미러28경로를 이번 관리 마감에 포함하고 비용 캐시2개는 제외한다. 원근거의 raw archive와 Git staged blob은 별도로 대조한다. 정확 경로·해시·추적/로컬 보존 구분은 run:phases/009/manager-evidence/preservation.json, 행정 수신은 로컬 commit.json에 둔다. 제품 바이트를 고치지 않은 관리 커밋은 기존 검증을 무효화하지 않는다. G4~G6/G8 최종 관문, 나머지 문서/의미 질문과 G7 실연쇄는010 및 후속 계획으로 유지한다.
'''
p=before['plan.md']
p=once(p,'## phase 001~008의 결과와 현재 상태','## phase 001~009의 결과와 현재 상태')
p=once(p,'008은 운영/복구와 설치 지정 성과 A1~A4를 검수했지만 기존 CLI 함수 표기 때문에 A5가 실패한 partial이다.','008은 운영/복구와 설치 지정 성과 A1~A4를 검수한 partial이며 그 A5의 기존 CLI 함수 표기4실패는009의 A1~A3 complete로 해소했다.')
a=p.index('## 다음 phase: 009')
b=p.index('## 가까운 후속 배정과 선행 관계',a)
p=p[:a]+'''## 다음 phase: 010

host-smoke와 reading-limits를 독립 work task로 배정한다. 두 task는 gpt-6.1-sol/high다.

- host-smoke는 G7의 실제 Windows Job 작업자 연쇄·자손 종료와 pythonw 부모의 PowerShell/제품 출력 회수를 기존 경계에서 공식 T5에 연결한다. 새 host 시험과 필요한 공유화·사용법·미러·캐시만 소유하고 jobs1로 한 검사 묶음씩 실행한다. 공급자 유료 호출·runtime 수정·OS 예약 변경은 하지 않는다.
- reading-limits는 L01/13-C의 현재 운전 host/tool/version/read-call·한도 단위·절단 규칙과 구간 회수 근거를 조사한다. writes=[]이며 고정된 운전 문서/CLI 코드와 호스트 자료만 읽는다. host-smoke가 바꾸는 시험·지침·미러·캐시나 그 결과에 의존하지 않고 제품 시험/생성기/모델 세션을 실행하지 않는다. 조사 완료와 요구 충족을 구별해 확인 불가능한 조건은 정확히 반환한다.

상대 task의 미완성 결과를 소비하지 않고 실행 자원·파일을 공유하지 않아 병렬화한다. Lean/예약/학술은 별도의 실제 연쇄로 다음 결과에 맞춰 배정한다. 정확한 입력·A·쓰기·검사는 run:phases/010/phase.json과 각 objective에 있다.

'''+p[b:]
p=once(p,'007 공급자 변경 단위는 커밋됐고008 지정 성과를 검수했다.009가 전건 문서4실패를 해소하면008~009의 문서·시험 변경을 함께 마감하고 G7의 개별 실제 연쇄 배정을 정한다.','007 공급자 변경은 커밋됐고009의 정본110/미러89 전건 통과로008~009 문서·시험 변경28경로를 이번 관리 마감에 포함한다.009의 검수 근거는 manager-evidence/verification.json·review.md다.010에서 Job/pythonw와 L01을 독립 진행한다.')
p=once(p,'| G7 Job/Lean/예약/학술 및 L01 | 공급자 최소 경계와 구별해 실제 Job/pythonw, Lean/Mathlib, 시험 전용 예약 등록·발화·해제, 학술 list_sources를 기존 실제 경로로 검증한다. L01은 현재 Codex/Claude 운전 read-call의 host·판본·절단 규칙·한도 단위를 특정한다. | 개별 실제 연쇄로 한 문맥에서 끝나는 task를 만든다. 역할 stdin을 운전 출력 한도로 대체하지 않는다. byte/token 권위 근거가 없으면 결정 질문을 남긴다. |','''| G7 Job/pythonw와 L01 |010 host-smoke가 실제 OS 작업자/출력/정리 연쇄를 T5에 연결하고 reading-limits가 현재 운전 읽기 계약의 한도·단위를 조사한다. | 두 task는 독립이다. 역할 stdin을 운전 출력 한도로 대체하지 않고 byte/token 근거 미상은 정확한 결정 질문으로 남긴다. |
| G7 Lean/예약/학술 | 실제 Lean/Mathlib, 시험 전용 예약 등록·발화·해제, 학술 list_sources를 기존 실제 경로로 각각 검증한다. |010 결과 뒤 실제 경계별 배정. Job/pythonw 성공이나 예약 cmdlet 대역의 결과로 대체하지 않는다. |''')
p=once(p,'| G1/G3 문서 P01 및 전건 회귀 | 008의 운영/복구 실제 반환·파일·반례 성과는 검수했다.009가 기존 CLI 함수 표기를 교정하고 전건 관련 회귀4실패를 새 판본에서 닫는다. | B133/B132~B134 및008 단언 유지. 제품 커밋은009 검수 뒤. |','| G1/G3 문서 P01 및 전건 회귀 |008 지정 성과와009 정본110/미러89 전건 통과를 검수해 이 부분을 닫았다. | B132~B134 및008 단언 유지. 최종 전체 판본 연결은 G4~G6/G8에 남는다. |')
p=once(p,'| G1/G8 문서 N03 지정 문장 | 008에서 installation_root 전달 설명과 양쪽 bootstrap-info2건을 검수했다.009 뒤 같은 문서 변경 단위의 인도 근거에 연결한다. | 옛 전역은 복원하지 않는다. N03 다른 절은 계속 미검토. |','| G1/G8 문서 N03 지정 문장 |008의 installation_root 전달 설명·bootstrap-info2건과009 회귀를 검수해 같은 문서 변경 단위로 인도한다. | 옛 전역은 복원하지 않는다. N03 다른 절은 계속 미검토. |')
s=before['seams.md']+'''
009는 기존 함수 참조 표기만 교정해 정본110·미러89 전건 관련 회귀를 통과했고 manager가 원자료/현재 소스를 대조했다. 제품 경계 계약의 개정은 없다.010 host-smoke는 기존 windows_job/Jobs·실제 worker·console_python/PowerShell 출력 계약을 소비하며 테스트 공유화는 한 task 내부다.010 reading-limits는 고정된 운전 문서·CLI 입력 경로와 외부 호스트 읽기 계약을 독립 조사한다. 서로의 결과를 제공/소비하지 않아 S 항목을 새로 만들지 않는다. runtime 경계 변경이 필요하면 별도 finding과 후속 배정으로 돌린다.
'''
diff=''
for name,value in [('context.md',c),('plan.md',p),('seams.md',s)]:
    diff+=''.join(difflib.unified_diff(before[name].splitlines(True),value.splitlines(True),fromfile=name+'.before',tofile=name))
    (RUN/name).write_text(value,encoding='utf-8',newline='')
(OUT/'common-state.diff').write_text(diff,encoding='utf-8',newline='')
(OUT/'review.md').write_text('''# phase 009 manager 검수

report 전문과 objective A1~A3를 읽고 공용 문서 갱신 전에 report 검사를 통과했다. verify.py는 종료2640파일을 현재 디스크와 전건 대조했고 시작이008 종료와 같은지,4변경이 writes/report에 맞는지 확인했다. 정본 문서의 차이는 함수명 뒤 (...) 다섯 바이트뿐이다. 실제 함수 참조 검사와 상태 필드 검사, nonexistent/noncallable 반려가 그대로 성립한다.

정본110·미러89의 실제 보고·고유 row·선택·exit0·시작/종료를 대조했다.008과 선택 ID가 같고 원실패4건 모두 양쪽 passed다.865개 Python과 문서 판본은 실행 전후/현재가 같다.008의 운영/복구 실제 객체·저장 파일·정상/오류/null/부재·교란 단언은 소스 불변과 새 선택 성공으로 보존한다.008의 partial 보고와 원실패는 바꾸지 않는다.

task의 첫 mirror 계획 검산 exit1은 Windows 개행 처리 누락이었고 변화0과 후속 성공을 확인했다. manager verify.py 첫 실행은 unowned_field_references의 schemas 인자를 누락해 TypeError로 끝났고, 현 함수 시그니처에 맞춰 관리 스크립트만 수정했다. 이후 검산 exit0이며 제품 수정/시험 재실행은 없다. 이 보조 스크립트 오류를 제품 실패로 세지 않는다.

runtime124·smoke입력3·corpus102경로 및 규칙/속성은008과 같아 승인된 실호출·Git clean 근거를 재사용한다. 원 --check1305파일과 skill-only verified의 실제 exit/소스도 확인했다. Git 제품 변경은008~009 승인된28경로와 정확히 같다. 캐시2개는 커밋하지 않는다. 제품 raw와 staged clean 바이트는 preservation.json 및 마감 기록으로 구별한다.

F1은008 F1/A5 해소 사실로 종결하고 C2/C10/plan에 반영한다. F2는 보존 사실로 종결하되 전체 관문·다른 문서/G7 책임은 C11/C12/plan에 유지한다. G4~G6/G8과 G7 전체는 아직 완료되지 않아 next:null이 아니다.010의 host T5 작업과 L01 고정 자료 조사는 제품 쓰기·소비·시험/캐시 충돌 없이 독립화했다. 원문13-C의 byte 의무를 token 상한으로 임의 대체할 권한은 주지 않는다.

common-state.diff를 갱신 전후 대조한다. C1의 G1~G8·C3/C4/C6/C7/C9와 기존 역사 근거·예외를 보존했다. 변경 C2는009 검수 추가, C5는010 독립성/자원 소유, C8은009 완료와 동일 모델 적용, C10은008 회귀 남김 종결/L01 배정, C11은host 범위/다른 G7 책임, C12는보존 사실/28파일 마감이다. plan은009 다음 행동을010 두 task로 교체하고 종료된 P01/N03 지정 문장을 최종 판본 연결로 넘겼다. seams는 새 경계 계약 없이010 책임만 추가했다.
''',encoding='utf-8',newline='')
ev=['run:phases/009/manager-evidence/verification.json','run:phases/009/manager-evidence/review.md']
manager={'next':'010',
 'decision':'009의 A1~A3 complete를 승인한다. 정본110·미러89의 선택/실제 row/exit·현재2640소스와 함수 표기5바이트만의 변화를 검산했다.008의 정확4실패가 양쪽 passed로 연결돼008 F1/A5 남김은 해소됐고 partial 원보고는 보존한다. runtime124·smoke3·corpus102와 속성/생성 규칙 불변에 한해 기존 실호출·Git clean 근거를 재사용한다.008~009 제품28경로와 이번 인계/기억을 관리 마감하며 캐시와 무관 dirty는 제외한다.\n\n전체 G1~G8은 미완료다.010 host-smoke는 실제 Job·pythonw T5 연쇄를 기존 코드로 연결하며 시험·미러·캐시의 유일한 소유자다. reading-limits는 고정된 운전 문서/CLI와 호스트 읽기 계약의 L01 조사만 하며 제품 수정·공식 시험·유료 호출을 하지 않는다. 서로 미완성 결과/공유 DB·포트·캐시를 소비하지 않아 병렬화한다. Lean/예약/학술·T4 분기와 나머지 문서/의미 질문·최종 관문은 plan에 남긴다. 읽기 조사의 완료를13-C 충족으로 간주하지 않는다.',
 'reports':[{'task':'document-callable','state':'read','detail':'전문과 A1~A3·findings F1/F2·모든 checks를 읽고 report 검사 통과 뒤 실제 원보고/소스와 대조했다. 두 보조 검산의 오류는 각각 task/manager 스크립트 문제로 제품 변화 없이 해소됐다.','evidence':['run:phases/009/tasks/document-callable/report.json','run:phases/009/manager-evidence/report-check.json']+ev}],
 'dispositions':[
  {'item':'009/document-callable/F1','action':'resolve','destination':['run:context.md#C2','run:context.md#C10','run:plan.md'],'reason':'동일 선택의 원실패4건이 양쪽 모두 passed이고 현재 소스/검사기가 그대로여서008 F1/A5를 새 근거로 해소했다.008 partial 기록은 보존한다.','evidence':ev},
  {'item':'009/document-callable/F2','action':'resolve','destination':['run:context.md#C11','run:context.md#C12','run:plan.md'],'reason':'runtime·smoke·corpus와 규칙/속성의 바이트 보존을 실제 파일에서 확인해 보존 사실은 종결한다. 한정 재사용은 유지하고 다른 G7 및 최종 관문은010과 후속 계획에 남겨 전체 성공으로 확대하지 않는다.','evidence':ev}],
 'context_updates':[],
 'plan_update':'009 전건 관련 회귀 완료로 P01/N03 지정 변경을 마감하고010 host-smoke·reading-limits를 독립 배정했다. 파일 소비와 실행 자원까지 분리했고 같은 task 안의 실제 연결/미러 검증 책임을 명시했다. 남은 Lean/예약/학술·문서/의미 질문·G4~G8 순서와 기존 제외/역사 근거는 보존한다. 의미 차이는 manager-evidence/common-state.diff 및 review.md에서 대조했다.',
 'seam_updates':[],'completion':None}
reasons={'C2':'009 A1~A3 검수·현재 소스/원보고 판본과 보조 검산 한계를 추가했다.',
         'C5':'009 단일 수리 종료를010 두 task의 독립 입력/쓰기/시험·캐시 소유로 교체했다.',
         'C8':'009 완료와010의 기존 지정 모델 사용을 반영했다. 모델 정책은 바꾸지 않았다.',
         'C10':'008 F1/A5를009 새 근거로 종결하고 P01/N03 지정 성과와 다른 미검토 범위를 구별했다. L01의 독립 조사 책임을 지정했다.',
         'C11':'010 host-smoke의 정확한 실경계와 후속 Lean/예약/학술·T4 책임을 추가했다.',
         'C12':'009 불변 검수에 따른 한정 재사용과008~009 승인 제품28파일의 관리 마감·보존 경계를 추가했다.'}
for item,reason in reasons.items():
    manager['context_updates'].append({'item':item,'action':'amend','destination':['run:context.md#'+item],'reason':reason,'evidence':ev+['run:phases/009/manager-evidence/common-state.diff']})
(RUN/'phases/009/manager.pending.json').write_text(json.dumps(manager,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
print('Common state and pending manager prepared; inspect diff.')

