from work import *
V=json.loads((E/'verification.json').read_text(encoding='utf-8'))
PREFIX='run:phases/024/tasks/document-waits/evidence/'
def refs(*names):return [PREFIX+name for name in names]
acceptance=[
 {'id':'A1','result':'pass','detail':'시작 skills/diff 2675파일이 023 source-inspected와 전건 동일하며 기존 dirty를 보존했다. P09/P11의 역사 문장을 현재 제목/행/owner에 연결했고 두 AST가 실제 경계 없이 승인되는 red 두 subTest 실패를 보존했다. 실제 source/currentness/평가기와 실제 engine/clock의 독립 기대를 사용한다. 관련 B110~B114/D-06 diff·존재 원보고7SHA 및 기존 helper 보존을 대조했다.',
  'evidence':refs('start-comparison.json','inputs-read.json','change-coordinates.json','red/report.json','red.stderr','history-verification.json','binding-review.md')},
 {'id':'A2','result':'pass','detail':'actual evaluate_condition/decision_is_current로 사용자 source 현재성·부재/무효·과제 범위·bool/int/float·value 부재/null·전체 change fallback을 구별했다. 양성 입력 문서 검사는 optional value를 필수 출력으로 만들지 않는다. kind/target/field의 추가 의미를 추론하지 않으며 basis·정확 오류·ready/not_ready·표/JSON 문법의 기존 검사와 새 누락/오기/차용 반례를 유지했다. 최종 양쪽 같은 ID가 passed다.',
  'evidence':refs('c2/report.json','m/report.json','c2-observations.json','m-observations.json','changes.diff','binding-review.md')},
 {'id':'A3','result':'pass','detail':'실제 _plan_settle_waits/_dispatchable·Sim clock과 실제 review 등록/전이로 queue 표현, 최초 시각 유지, 299/300/301초, requested_by/recovery, queue 제거와 오래된 wait 제거를 검사했다. 실제 준비 응답 수락 후 초기 사건 소비도 검사한다. 문서값 부재/차용/변조 및 언급 삭제/없는 필드 반례가 반려된다. D-06 조건·예외 표와 기존 장벽 제거를 유지하며 timeout이나 정책 추론기를 추가하지 않았다.',
  'evidence':refs('c2/report.json','m/report.json','c2-observations.json','m-observations.json','D-06.diff','binding-review.md')},
 {'id':'A4','result':'pass','detail':'지정 N 세 구간의 정확8문장을 현재 소비자/검사에 연결했다. 공개 retry 수락의 비해소·pause/resume 비해소·재포장 성공/실패·원artifact/기존 사용자 해소 보존, planner의 허용 profile/현재성/역할 제한 및 실제 수행 연쇄를 유지했다. 운영 retry에 live predecessor와 봉인 manifest 불일치의 정확 반례·queue 무변경을 보완하고, 현재 활동/새 공간/프로필·권한·관문과 설치 repair 별도 권한을 기존 소비/검사에 대조했다. lexical policy5이름/8문장을 정의·owner와 유지 판정에 연결했으며 전체 정책 의미나 N 절 전체의 완료를 주장하지 않는다.',
  'evidence':refs('section-semantic-review.json','policy-name-decisions.json','history-verification.json','change-coordinates.json','c2/report.json','m/report.json','binding-review.md')},
 {'id':'A5','result':'pass','detail':'실제 문서 순회6모듈과 변경 영향/직접소비/기존 전문 단일 지급·복원을 선택하여 양쪽 동일254선택/고유row 전부passed·exit0, 각875Python과 비캐시 전후불변을 확인했다. 관찰된 각107실제 반환과 각18제안최종입력의 전문1을 검산했다. 사전15미러변경 범위/공식생성·캐시·최종--check1336·skill-only를 완료했다.139실호출입력/258고정경계·corpus144/SHA150/Gitraw-clean·host8/tools5·baseline910/원task891보존을 확인했다. resource exact1추가관측의 actual CLI cwd141자를 raw audit로 확인했다. 이번 선택에는 symlink 시험이 없으며 과거1314미검사·최종전체관문은 남는다.',
  'evidence':refs('selection-decisions.json','verification.json','c2-process.json','m-process.json','preservation.json','prior-task-preservation.json','resource-cwd-confirmed.json','temp-parent-git.json','mirror-plan.json','mirror-build.stdout','final-mirror-check.stdout','skill-only.stdout','binding-review.md')}
]
changes=[]
for path in V['changes']:
    name=Path(path).name
    if name=='.timings.json':detail='공식 검사 비용 캐시. 정본/미러의 마지막 동기화 결과이며 제품 판정 소스가 아니다.'
    elif name=='doc_code.py':detail='P09 change/P11 plan_settle_wait AST 추정을 두 실제 경계 표지·값 검사로 교체하고 명시 위임을 추가한다. 다른 owner와 남은 AST helper는 유지한다.'
    elif name=='engine_context.py':detail='실제 양성 입력/대기 필드와 문서 소비 존재, 독립 기대값 및 필드 자료형을 대조하는 한정 assert_wait_documents를 추가한다. 기존 helper 함수는 불변이다.'
    elif name=='test_doc_code.py':detail='두 실제 owner 요구·위임·다른 owner 비우회·정확 담당 호출과 누락/오기/없는 메서드 반례를 검사한다. 전체 문서 순회에 명시 위임을 연결한다.'
    elif name=='test_planning_conditions.py':detail='실제 평가/현재성의 type·부재/null/fallback·source·scope·정확 basis/error와 실제 입력 문서/누락/변조 반례를 추가한다.'
    elif name=='test_scheduling_session_slots.py':detail='실제 queue wait와 문서, running review/queue 제거·최초시각·정확 상한·우회/오래된wait, 값/문서손상과 초기사건 수락후소비를 검사한다.'
    elif name=='test_engine_input_recovery.py':detail='기존 공개 flow에 retry 수락직후 open·일반pause/resume 비해소·원source artifact 바이트보존 단언을 보완한다.'
    elif name=='test_scheduling_recovery_dispositions.py':detail='기존 actual fresh-input retry 앞에 live predecessor와 봉인 manifest 불일치 반려·queue 무변경을 검사한다.'
    elif name=='과제-착수조건.md':detail='value 키 부재의 전체 change fallback과 null/true 대1의 자료형 구별을 현재 조건 연산 문장에 명시한다.'
    elif name=='CLI-실행-계약.md':detail='계획 정산의 queue 표현·최초 시각 유지·kind/since/limit·상한 동일시각/queue제거의 해소·오래된wait제거를 명시한다.'
    else:detail='기존 실제 문서 순회가 두 새 owner의 실제 검사 담당에 명시 위임하도록 연결한다. 기존 실제 반환/owner 단언은 유지한다.'
    if path.startswith('.agents/') and name!='.timings.json':detail='공식 생성기의 대응 미러. '+detail
    changes.append({'path':path,'detail':detail})
findings=[
 {'id':'F1','kind':'fact','detail':'P09/P11의 지정 AST 입력/반환 결속 공백을 두 실제 owner 검사로 해소했다. 정본/미러 같은254개가 전부passed이며 실제 반환107/최종 제안입력18개를 확인했다. 변경은28비캐시 제품/시험/문서/미러와비용캐시2개이고 runtime은 불변이다. task 완료를 G 전체나 PR24 전체 완료로 확대하지 않는다.',
  'evidence':refs('verification.json','change-coordinates.json','history-verification.json','binding-review.md'),
  'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G2','run:context.md#G3','run:plan.md'],
  'next_action':'manager가 P09/P11 및 정확 N 문장8개의 지정 남김을 새근거에 연결하고, 이28비캐시경로의 인도/관리마감을 판단한다.'},
 {'id':'F2','kind':'decision','detail':'conversation_loss_policy/disconnect_policy/model_policy/external_policy/adopt_default_review_policy의 현문장8회와실제정의·owner를 확인해 유지한다. lexical 존재 통과는 전체 의미 인증이 아니다. model_policy의 module defaults와 잠금불일치 failure kind를 구별한다. N01-237/N02-002/N01-260의 지정8문장 밖 전체절, P08/TRUST·다른N/L01/PR24는 열어 둔다.',
  'evidence':refs('policy-name-decisions.json','section-semantic-review.json','binding-review.md'),
  'affects':['run:context.md#C10','run:plan.md','run:context.md#G1','run:context.md#G3'],
  'next_action':'각 실제 소유자의 남은 의미 검토를 기존 계획의 정확 범위로 유지한다. 이름 존재나 이번8문장의 완료로 해당 정책 전체·N절 전체·L01을 닫지 않는다.'},
 {'id':'F3','kind':'fact','detail':'023 기준139실호출입력/258고정경계·corpus144/명시SHA150/Gitraw-clean·host8/tools5·baseline910/원task891은불변이다. 두문서문단 변경은미래역할prompt와설치문서해시에영향을주므로 과거실호출은승인된불변하위경계만재사용한다. 이번254선택에symlink시험은없으며기존1314조건부미검사는남는다. 최종전체일반/freshT3/전수변이/G7최종판연결/최종review는미실행이다.',
  'evidence':refs('preservation.json','prior-task-preservation.json','verification.json','final-mirror-check.stdout','skill-only.stdout','binding-review.md'),
  'affects':['run:context.md#C12','run:context.md#G4','run:context.md#G5','run:context.md#G6','run:context.md#G7','run:context.md#G8','run:plan.md'],
  'next_action':'기존 실호출의 승인된불변성질만재사용하고문서판본영향/1314미검사및미실행최종관문을후속에보존한다.'},
 {'id':'F4','kind':'fact','detail':'원 red/focus/corrected/c와 보조 후처리/차이 검산 실패를 보존했다. focus의helper/fixture문제와corrected의basis.status기대누락은실제계약에맞게교정됐다. c의관찰도구는공통decorator를actual producer로오인해19error/25failed/62not_run을만들었고inspect.unwrap만고친같은제품875Python/254선택의c2가전부passed다. 추가resource1시험은passed/worker0이나Windowsargv문자열을목록으로본후처리가실패했고raw를재검산했다. 시작문서혼합개행/Gitclean차이는raw/SHA검산으로해결했으며작업트리를복원하지않았다.',
  'evidence':refs('verification.json','c/report.json','c2/report.json','run_suite_initial.py','resource-cwd-confirmed.json','cwd-confirmation.stderr','cwd-verified.stdout','diff-coordinates.json','binding-review.md'),
  'affects':['run:context.md#C2','run:context.md#G3','run:plan.md'],
  'next_action':'초기실패를역사기록으로보존하고최종같은ID/같은제품판본의통과와구별한다. 이관찰/후처리문제를제품runtime결함으로재배정하지않는다.'}
]
checks=[]
for path in sorted(E.glob('*-process.json')):
    label=path.name.removesuffix('-process.json')
    value=json.loads(path.read_text(encoding='utf-8'))
    expected_red=label=='red'
    result='pass' if value['exit_code']==0 or expected_red else 'fail'
    detail='실제 argv/cwd/명시 환경/PID/UTC 시작·종료/exit·stdout/stderr 및 skills/diff 전후 SHA를 보존했다.'
    if expected_red:detail+=' 기대exit1과두owner의무입력통과반례두subTest실패를관찰해red검증은성공이다.'
    if label in ('c2','m'):detail+=' 동일254선택/고유row 전부passed·exit0 및각875Python/비캐시전후불변.최종전체관문은아니다.'
    if result=='fail':detail+=' 자기helper/fixture/observer/후처리 또는비교가정의미완성시도다. 원실패와수정뒤의같은ID/원바이트검산관계는binding-review.md와F4에설명한다.'
    checks.append({'command':subprocess.list2cmdline(value['argv']),'cwd':'repo:.','result':result,
        'exit_code':value['exit_code'],'evidence':refs(path.name,label+'.stdout',label+'.stderr'),'detail':detail})
report={'status':'complete',
 'narrative':'024 document-waits의 A1~A5를 완료했다. P09/P11의 AST 이름 결속을 실제결정입력/배정대기·독립기대·명시문서담당으로교체하고조건자료형/부재/null/현재성·queue/시각/해소와지정N8문장의기존소비를연결했다. 두문서단락을정확히보충했으며runtime/스키마/포트/runner/Job fixture/corpus를변경하지않았다. B110~B114/D-06의관련hunk와존재원보고7SHA를대조했고기존helper·PURE/P01~P07/P10·전문1/봉인복원보증을유지했다. 최종정본/미러동일254선택은전부passed/exit0이며875Python판본/전후소스가고정됐다. 사전미러범위·공식생성/캐시/최종--check1336/skill-only와보존모집단을검산했다. 원실패는고치거나성공에합산하지않았다. 실제자식cwd미관측은resource1의추가raw관측으로해결했고141자를확인했다. 새문서의미래prompt영향,lexical정책전체의미미검토,기존1314symlink미검사및최종전체관문/다른P08/TRUST/N/L01은구별해후속으로남긴다. 상세판정과조건/예외는binding-review.md가설명하고원보고/process/관찰JSON이근거다.',
 'acceptance':acceptance,'changes':changes,'seams':[],'findings':findings,'checks':checks}
(E.parent/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Report complete',len(changes),'changes',len(checks),'recorded commands')
