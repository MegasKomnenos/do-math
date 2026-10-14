from work import *
verified=json.loads((E/'verification.json').read_text(encoding='utf-8'))
prefix='run:phases/022/tasks/review-delivery/evidence/'
def ev(*paths): return [prefix+p for p in paths]
def accepted(identifier,detail,*paths):
    return {'id':identifier,'result':'pass','detail':detail,'evidence':ev(*paths)}
changes=[]
for path in verified['changes']:
    name=Path(path).name
    if name.startswith('.timings'):
        detail='공식 관련 검사 비용 캐시와 마지막 정본→미러 동기화의 실행 부산물.'
    elif name=='review_cycle.py':
        detail='현재/이전 proposal 원메시지를 기존 정확 source_ref로 지급하여 role_review.proposal의 현재 전문 단일 지급을 보장한다. 원 turns/manifest/봉인 형식은 보존한다.'
    elif name=='doc_code.py':
        detail='P07 result/retry AST 반환 추정을 실제 submission_check/repair 경계로 교체하고 값 없는 문서 검사를 반려한다.'
    elif name=='engine_context.py':
        detail='실제 check의 정확 후보·모드·실행·정규 해시·check ID와 route repair의 원문·범위에 문서 필드를 결속한다.'
    elif name=='test_doc_code.py':
        detail='P07 실제 입력 필수·소유 혼동/필드 누락·정확 defer/담당 method 누락 반례를 추가하고 기존 다른 소유자 검사를 보존한다.'
    elif name=='test_submission_checks.py':
        detail='실제 정상/실패 check_submission 반환을 문서와 정확 입력 해시에 연결하며 passed 누락/반전·다른 후보/실행/모드/check 차용을 반려한다.'
    elif name=='test_repair_routing.py':
        detail='실제 queue/wait repair와 최종 역할 입력·반려 원문 파일을 정확 실행·후보·활동·수리범위에 연결하고 원문/소유/범위 손상 사본을 반려한다.'
    elif name=='test_submission_review_inputs.py':
        detail='기존 실제 다섯 단계 입력 검사에 최종 반환 전체의 독립 전문 개수=1과 원 source 파일/manifest의 정확 바이트·SHA·크기·판본 단언을 추가한다.'
    elif name=='test_review_engine_transcripts.py':
        detail='현재 전문의 정확 source_ref/원봉인 보존·물질화 사본 부재 재생성·변조 파일의 정확 복원 진단을 실제 엔진에서 확인한다.'
    elif name=='test_review_engine_stages.py':
        detail='제안 판본 변경의 기존 실제 엔진 시험에 이전 제안 원메시지의 정확 파일·해시·크기·판본 복원과 새 전문의 구별을 추가한다.'
    else:
        detail='기존 전건 문서 순회에서 P07 두 소유자만 실제 담당 검사로 위임한다. 해당 시험 자신의 기존 소유자·실패 단언은 유지한다.'
    if path.startswith('.agents/'):
        detail='공식 생성기의 대응 미러. '+detail
    changes.append({'path':path,'detail':detail})
checks=[]
labels=['temp-check','red','red-doc','focus','corrected','mirror-build','c','m',
        'history','sections','preservation','diff','diff-corrected','diff-check','cache-sync','mirror-check','skill-only','audit']
for name in labels:
    process=json.loads((E/(name+'-process.json')).read_text(encoding='utf-8'))
    code=process['exit_code']
    assert code is not None
    result='fail' if name=='diff' else 'pass'
    if name in ('red','red-doc'):
        assert code==1
        detail=('계약 기대 전문 개수1과 실제2의 단일 row 실패를 의도대로 관측했다.' if name=='red' else
            '두 P07 owner가 실제 값 없이 문서를 통과시키는 반례를 한 method의 두 실패 subTest/exit1로 의도대로 관측했다.')
    elif name=='diff':
        assert code==1
        detail='증거 diff 작성의 Git blob/작업파일 개행 동등 가정이 시작 SHA와 달라 실패했다. 제품/원자료는 바꾸지 않았다. diff-corrected에서 검증된 LF/CRLF 바이트 실현만 사용해 전28비캐시 경로의 시작 SHA 일치를 확인했다.'
    elif name in ('c','m'):
        assert code==0
        suite=verified['suites'][name]
        detail=f"최종 {suite['selected']}선택/고유row, {suite['counts']['passed']}passed·Windows1314 권한1skip·실제exit0. {suite['source_sha256_count']} Python과 비캐시 소스 전후/현재 SHA가 같고 전문 단일 지급의 실제최종 반환 {suite['final_proposal_returns']}개가 전부 기대1이다. skip은passed가 아니고 지정관련선택은전체일반/T3/변이/T4/T5관문이 아니다."
    else:
        assert code==0
        detail='명령의 실제argv/cwd/환경/PID/시각/종료와 소스전후, stdout/stderr를 보존했다. 업무 판정은 연결한 실제 자료와 binding-review.md에 설명한다.'
    checks.append({'command':subprocess.list2cmdline(process['argv']),'cwd':'repo:.',
        'result':result,'exit_code':code,'evidence':ev(name+'-process.json',name+'.stdout',name+'.stderr'),
        'detail':detail})
suite=verified['suites']['c']
report={
 'status':'complete',
 'narrative':f"021 F1의 현재 제안 전문중복을 원봉인과 정확복원을 유지하며 수리했고 P07의 실제 제출 검사/반려 원문/최종입력 결속과 배정된 네 문서 절의 이름·의미 판정을 수행했다. 시작 skills/diff2675파일은021 manager와전건같으며 기존dirty는보존했다. 변경은{len(changes)}경로(28비캐시·비용캐시2)이고 제품runtime은양쪽review_cycle.py뿐이다. review_engine/context_store의기존물질화/공유seat검사를그대로사용하므로별도runtime수정은필요하지않았다. 수리전red는실제최종반환2!=1, red-doc은실제값없는두owner통과반례로실패했다. 최종양쪽같은{suite['selected']}선택/고유row는각{suite['counts']['passed']}passed·권한1skip·exit0이며각875Python/비캐시전후SHA가같다. 양쪽실제최종검토반환각80개의전문개수는전부1이다. 정상/손상/부재·이전판본·가시성·정확ref·수리범위와기존P01~P05/B130~B134소유단언을유지했다. 상세원자료와배선은binding-review.md,current-sections/section-name-decisions,verification.json이다.\n\nP07의result/retry두AST추정을실제반환/입력검사로교체했다. passed/capture_eligible/중앙접수/편입/수학승인은구별하며not_checked를성공으로바꾸지않는다. 반환사본의필드/실행/후보/check/수리범위교란과잘못된defer담당을반려한다. B112/B113의관련hunk와존재7원보고SHA를대조했고다른hunk/PR24전체의미검토는유지한다. 네문서절의247개절별고유inline이름은현재문장/실제소유자또는구체적비코드·경로표현으로판정했지만다른packet의전체의미인증은이번성과로대체하지않는다.\n\n139실호출입력중138불변/정본review_cycle1변경,고정runtime-T4 258경로중양쪽review_cycle2변경을명시했다. 새설치support.zip/tool_sha256도이모듈을포함해바뀌므로과거전체설치의바이트동등성은주장하지않는다. 변하지않은공급자전송/worker·Job/host·Lean·held예약·학술최소호출의승인성질만한정재사용하고영향받는검토/포장/복원slice는새관련회귀로교체한다. corpus144경로/150명시SHA/Gitraw-clean·host8자료·도구5·baseline910원바이트/Gitblob과021원task242파일은불변이다. 제품문서는불변이지만runtime수리는향후검토prompt바이트를바꾼다. 공식미러15갱신·마지막캐시동기화·--check1336·skill-only를완료했다. G4권한skip,다른packet/L01,최종전체일반/freshT3/전수변이/G7최종판연결/제품수정없는최종review는후속책임이다. task complete는이배정A1~A5완료이며개발전체완료가아니다.\n\n증거diff의초기Git개행가정오류는실제exit1을보존했고, 시작SHA에맞는검증된LF/CRLF실현으로도우미만교정한exit0과정확task diff를보존했다. 반복관문·새유료/예약/학술실호출·연구재개/삭제·graphify갱신·Gitstage/commit/reset/checkout/push는수행하지않았다.",
 'acceptance':[
   accepted('A1','현재원문/생산/봉인/포장·정확두map·원담당/판본/ref를대조하고기존실제단계시험에독립기대1을넣어수리전2!=1을재현했다. 시작2675파일SHA일치와기존dirty보존을확인했다.',
       'start-comparison.json','git-status.stdout','input-audit.json','red/report.json','red.stderr','current-sections.json','task-changes.diff'),
   accepted('A2','현재/이전proposal메시지는정확참조파일로원문을회수하고현재전문은role_review.proposal에한번만지급된다. 원turns/manifest/봉인과다섯단계·재개/판본변경·동료비노출·정확ref/고정질문·물질화부재/손상진단을보존했다. 최종양쪽실제반환각80개가독립기대1이다.',
       'c-proposal-observation.json','m-proposal-observation.json','c/report.json','m/report.json','focus/report.json','corrected/report.json','binding-review.md'),
   accepted('A3','P07 result/retry AST두결속을실제check_submission반환과route의queue/wait·최종역할입력/정확원문파일검사로교체했다. 정상/실패/not_checked·capture/접수/편입구별과필드누락·다른후보/실행/check/수리범위·import_check차용반려,정확defer/담당누락반례와기존소유단언을유지했다.',
       'p07-packet.json','p07-bindings.json','red-doc/report.json','red-doc.stderr','c/report.json','m/report.json','history-verification.json','binding-review.md'),
   accepted('A4','현재제목으로네절을고정하고각inline이름의문장·정확소유자/함수·비코드/경로제외이유와기존성질의재사용/미검사한계를247행에기록했다. 이번수리/결속의원본문은유지하며이름목록을전체의미인증으로바꾸지않았다. 다른packet의전체의미검증이필요한정확이름/문장/질문은F5로반환했으며네절밖N모집단완료를주장하지않는다.',
       'current-sections.json','section-name-decisions.json','sections-process.json','binding-review.md'),
   accepted('A5','기존270선택의모듈범위와배정추가7모듈을보존한같은최종364선택을양쪽에서완결했다. 각363passed/권한1skip/exit0·각875Python·비캐시전후/현재SHA와원반례green을확인했다. 허용된미러생성/캐시동기화/--check/skill-only와범위·역사보존/영향판정을완료했다. skip및최종전체관문은명시남김이다.',
       'verification.json','related-selection.json','preservation.json','mirror-plan.json','mirror-build.stdout','cache-sync.json','mirror-check.stdout','skill-only.stdout','change-coordinates.json')],
 'changes':changes,'seams':[],
 'findings':[
   {'id':'F1','kind':'decision','detail':'021전문중복은현재proposal메시지도기존source_ref로지급하는최소runtime수리로해소했다. 원메시지/manifest/입력봉인형식을바꾸지않고review_engine의기존정확물질화와context_store의공유seat검사를사용한다. 실제최종반환의독립기대값1을제품회귀에넣어생산값자기비교의한계를해소했다.',
    'evidence':ev('red.stderr','c-proposal-observation.json','m-proposal-observation.json','task-changes.diff','binding-review.md'),
    'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G3','run:plan.md'],
    'next_action':'manager가021F1/A2의남김을새반례green과원봉인/복원근거로처분하고보류된02126비캐시제품및이번28비캐시제품의정확합집합을검수·마감한다.'},
   {'id':'F2','kind':'fact','detail':'P07의두AST반환추정은B112repair와B113submission_check도입hunk에대응한다. 실제반환/입력검사로교체했고존재원보고7개SHA와현재다른owner/별칭/callable단언을유지했다. PR24전체나다른packet의완료는아니다.',
    'evidence':ev('history-verification.json','binding-review.md','c/report.json','m/report.json'),
    'affects':['run:context.md#C9','run:context.md#C10','run:context.md#G2','run:context.md#G3'],
    'next_action':'P07지정남김과PR24의이한정slice교체판정만반영하고다른producer/hunk와부재원보고의역사counts를새성공으로합산하지않는다.'},
   {'id':'F3','kind':'fact','detail':'139실호출입력중정본review_cycle1파일및258고정runtime/T4중양쪽2파일이변경됐다. 새설치support.zip/tool_sha256도변경대상이다. 나머지138입력/256경계와144corpus/150SHA/Gitraw-clean·8host·5tools·910baseline·021원task242파일은불변이다. 기존최소실호출은변하지않은하위경계성질만재사용하며영향받는검토/포장/복원은새회귀근거를사용한다.',
    'evidence':ev('preservation.json','verification.json','task-changes.diff','binding-review.md'),
    'affects':['run:context.md#C12','run:context.md#G4','run:context.md#G5','run:context.md#G6','run:context.md#G7','run:context.md#G8'],
    'next_action':'최종고정판전체일반/freshT3/전수변이와G7/T4의최종판연결·제품수정없는review를계속배정한다. 역사전체T4/동결설치/모델독해의최종소스동등성을일괄주장하지않고이번runtime영향을근거별로판정한다.'},
   {'id':'F4','kind':'issue','detail':'최종양쪽의unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported는기존Windows1314심볼릭링크생성권한으로각1skipped다. 실제탈출반려는미검사이며363passed에포함하지않았다.',
    'evidence':ev('verification.json','c/report.json','m/report.json','c.stderr','m.stderr'),
    'affects':['run:context.md#G4','run:plan.md'],
    'next_action':'G4최종기본전체에서원문상환경조건의정당성과실제미검사를별도로판정하며skip을통과로세지않는다.'},
   {'id':'F5','kind':'question','detail':'네절의이름소유는판정했지만다른packet의전체동작인증은아니다. N01-237의input_overflow_retry_resolved/failed·question_links와N02-002의input_overflow_requests/input_overflow_resolutions(현재N01행699·N02행21)은input_recovery/일반계획프로필선택·사용자retry의허용모집단/현재성/원질문연결을검토해야한다. N01-260의scope/replay_safety/repair_target은disposition_schema/운영처분의정확종료·재개권한이고N02-014의impact_set/previous_hashes/revision_requests/revision_resolutions는계산된영향/거버넌스적용소유다. 이번선택의검토제안overflow·수리/구조검사만으로전체인증할지,기존관련의미근거가충분한지의판정이남는다. 정확문장과소유자및기존검사한계는section-name-decisions의해당행에있다.',
    'evidence':ev('current-sections.json','section-name-decisions.json','binding-review.md','p07-packet.json'),
    'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G3','run:plan.md'],
    'next_action':'기존P09/P11조건·대기와P06/P10거버넌스/적용묶음에이정확절/이름을결합하고현재시험/원보고로남은의미질문을유지·교정·해소한다. 필요파일이이번writes밖이라runtime을확장하지않았다. 새전역어휘존재나247행목록을네절전체/전체N완료증거로쓰지않는다.'}],
 'checks':checks}
save('../report.json',report)
print(report['status'],'acceptance',len(report['acceptance']),'changes',len(changes),'checks',len(checks))
