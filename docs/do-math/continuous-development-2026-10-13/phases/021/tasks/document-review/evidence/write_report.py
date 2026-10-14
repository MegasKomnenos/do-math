from work import *
base='run:phases/021/tasks/document-review/evidence/'
def refs(*names):return [base+name for name in names]
verified=json.loads((E/'verification.json').read_text(encoding='utf-8'))
assert verified['suites']['c']['selected']==verified['suites']['m']['selected']==270
assert verified['suites']['c']['counts']==verified['suites']['m']['counts']=={'passed':269,'skipped':1}
probe=json.loads((E/'proposal-observation.json').read_text())
assert not probe['satisfied'] and probe['official_exit_code']==0
assert probe['returns'][-1]['stage']=='answer' and probe['returns'][-1]['count']==2
details={
'A1':'시작 skills/diff 2675파일은020 manager source-inspected와 전건 SHA가 같다. 기존 dirty 변경은 시작에 포함됐으며 이번 task에 귀속하지 않는다. P04/P05 현재 제목·행·sources=review_sources 별칭을 context_for→검토 준비→_context→최종포장과 고정request→물질화→최종조사의 실제 소유에 연결했다. 비공개 동료판단/봉인결과 및 일반research_sources와 고정원자료를 구별했다. B110~B114 actualdiff·현재소비와 존재7원보고 SHA를 대조해 B113/B114의 네owner AST slice를 실제 반환검사로 교체하고 나머지owner·별칭·callable 검사·원단언은 유지했다. PR24 전체의 종결이 아니다.',
'A2':'실제 단계별 context_for/_prepare_review_context/_context/prepare_role_input, 원finding의 정확ref·담당, 실제 고정질문id/digest/question/proposal_digest와inline/artifact의ref/local_path/SHA/bytes/snapshot·고정원문을 확인했다. 기존 두고정질문 flow의 실제 최종포장반환을 sys.monitoring으로 관찰했고 생산/포장/물질화 함수를 교체하지 않았다. 실제Git 정상/복원실패 및 일반게시 뒤 원snapshot 바이트도 확인했다. 그러나 현재 제안의 단일 지급은 실패했다: answer/initial-0의 실제최종포장반환에 context.role_review.proposal과 context.role_review.self_messages[0].content가 같은 전문을 포함한다(기대1/실제2). 별도probe의 공식row는passed/exit0이지만 추가 의미단언은exit1이다. runtime context_for/_record_review_input은writes밖이어서수리하지 않았으며F1의좁은후속work가필요하다. 최상위proposal부재만으로 전체중복방지를충족했다고쓰지않는다.',
'A3':'수리전red 한method의네owner subTest가 모두ValueError not raised로실패했다. 같은method가최종양쪽에서passed이며실제입력없는검사는기본반려한다. 반환후사본의proposal/조건부metadata/ref/question/digest/local_path/SHA/bytes삭제·변경, 다른stage/slot/동일localID발견ref·다른원자료ref/경로/snapshot·일반research_sources키·같은바이트복사경로의차용을반려한다. 빈pending/source배열은원소필드양성증거로쓰지않는다. 실제workspace파일손상/부재와제품의Git복원실패·materialized_content_mismatch좌표를구별했다. 기존봉인전동료비노출·원담당·잘못된request/proposal/원자료반려와P01~P03/B130~B134/다른owner음성단언을유지했다. owner/defer오기·누락·문서검사없는method·다른owner동시건너뜀도반려한다. 생산추정네binding만제거했으며범용추론기/전역담당등록부는추가하지않았다.',
'A4':'최종정본/미러같은270선택·고유row가완결됐고각269passed/기존Windows1314 symlink1skipped/실제exit0이다. 실패/오류/미실행은없지만이공식green을A2충족으로확대하지않는다. 각875Python과실행tree의비캐시전후해시는같다. 계획14경로의공식생성·마지막캐시동기화·--check1336파일일치·skill-only를통과했다. 실제28변경은정본13시험/helper·미러13·비용캐시2로writes안이다. runtime139입력·corpus144경로/150명시SHA/Gitraw-clean·host8/도구5·baseline910/Gitblob·고정runtime/T4 258경로를보존했다. 제품문서를변경하지않았으며역사실호출의승인성질만재사용한다. skip은통과/실제탈출반려로세지않고G4에남긴다. P06~P11/TRUST/N·L01 Q1/Q2·G4~G6/G8은후속책임이다.'}
ev={
'A1':refs('start-comparison.json','input-audit.json','current-bindings.json','history-verification.json','B113-p04-p05.diff','B114-p04-p05.diff','binding-review.md'),
'A2':refs('proposal-observation.json','proposal-return-14.json','proposal-probe-process.json','proposal-probe.stderr','binding-review.md','c/report.json','m/report.json'),
'A3':refs('red/report.json','red.stderr','c/report.json','m/report.json','binding-review.md','proposal-observation.json'),
'A4':refs('verification.json','preservation.json','mirror-plan.json','mirror-build-process.json','cache-sync-process.json','mirror-check-process.json','skill-only-process.json','c/report.json','m/report.json','temp-check.json')}
named={
'doc_code.py':'네검토owner를실제입력경계로전환하고정확owner defer·실제필드순회를추가했다. 마지막소비가없어진반환AST/소비키추정과미사용import를제거했다.',
'engine_context.py':'실제자리/고정조사반환과소유cycle/request/원자료바이트를문서에결속하고정확manifest참조파일읽기·최종포장반환관찰을추가했다.',
'test_doc_code.py':'수리전네반례와최종기본반려·개별defer·빈배열/별칭·담당method/실제검사호출누락음성검사를추가하고일반순회를명시담당에위임했다.',
'test_submission_review_inputs.py':'실제기존opened_sim/쟁점경로의scope/initial/organize/judge/answer최종자리입력·정확finding소유와필드삭제반례를검사한다. 전체전문중복은별도probe에서미충족으로보고한다.',
'test_review_research_owner_contract.py':'기존고정질문/게시후snapshot시험에실제문서·원자료바이트대조와필드삭제·교차소유·같은바이트다른경로·손상/부재반례를연결했다.',
'test_review_cycle_stages.py':'기존blindness와organizer의실제반환을문서검사에연결하고같은localID를쓴다른자리ref차용을반려한다.',
'test_review_research_flows.py':'기존두고정질문flow에서실제최종포장반환과정확원자료를관찰하며두담당검사의실행을확인한다.',
'test_review_source_restoration.py':'실제Git정상원자료반환의문서/바이트결속과물질화손상의slot/ref/snapshot/path/기대·관측SHA진단을추가했다.'}
changes=[]
for path in verified['changes']:
    name=Path(path).name
    if name.startswith('.timings'):detail='공식실행의비용캐시와마지막정본/미러동기화. 의미/단언을변경하지않는다.'
    else:detail=named.get(name,'기존전건문서순회에네검토owner의정확defer를추가했다. 이파일의원래실제반환/음성단언은유지한다.')
    if path.startswith('.agents/') and not name.startswith('.timings'):detail='공식생성기의정본변환사본: '+detail
    changes.append({'path':path,'detail':detail})
checks=[]
labels=['temp-check','red','focus','corrected','corrected2','corrected3','corrected4','focused-final','c','proposal-probe','mirror-plan','mirror-build','m','preservation','cache-sync','mirror-check','skill-only','audit','save-diff','final-inspection']
for label in labels:
    path=E/(label+'-process.json')
    if not path.exists():continue
    process=json.loads(path.read_text())
    code=process['exit_code'];assert isinstance(code,int)
    result='pass' if code==0 else 'fail'
    note='실제argv/cwd/환경/PID/시각/종료와소스전후를보존했다.'
    if label=='red':result='pass';note='수리전네필드의실제입력없는통과공백을같은한method의4subTest실패/exit1로확인했다. 제품합격이아니다.'
    if label in ('focus','corrected','corrected2','corrected3'):
        note+=' 직접ReviewScene을전체포장장면으로사용한자신의fixture가정(title/id/goal_status/adopted governance)과초기defer누락오류다. 불완전보충을제거하고공개활성Sim에최종입력검사를옮긴corrected4및최종같은ID의passed와대조한다.'
    if label=='proposal-probe':note='공식좁은선택은1passed/exit0이지만실제최종반환의제안전문사본수기대1/실제2를관찰해추가의미단언이exit1이다. A2미충족의제품반례이며감시함수/생산함수를교체하지않았다.'
    if label in ('c','m'):note+=' 같은270선택/고유row,269passed/권한1skip/exit0. skip은passed가아니며A2전문중복조건은별도미충족이다. 약600초의정본관련범위실행은전체일반/T3/변이관문이아니다.'
    evidence=refs(label+'-process.json',label+'.stdout',label+'.stderr')
    if (E/label/'report.json').exists():evidence+=refs(label+'/report.json')
    checks.append({'command':subprocess.list2cmdline(process['argv']),'cwd':'repo:.','result':result,'exit_code':code,'evidence':evidence,'detail':note})
report={
'status':'partial',
'narrative':'P04/P05 네문서owner의AST/소비키반환추정을실제검토반환·고정원자료물질화·최종포장검사로교체했다. 시작2675파일은020검수본과같고변경28경로는허용된시험/helper·공식미러·비용캐시뿐이다. runtime/API/원schema/거버넌스·가시성/공용계약/engine/runner/adapter/Jobfixture/corpus/제품문서는변경하지않았다. A1/A3/A4는완료했으나A2는현재제안전문의중첩중복때문에미충족이다.\n\n실제answer/initial-0의최종포장반환에는동일전문이role_review.proposal과role_review.self_messages[0].content에두번있다. 기존검사의최상위proposal부재단언을전체중복방지로과장하지않고반환사건관찰·원context/manifest·실패단언을보존했다. 수리에필요한context_for/_record_review_input은writes밖이므로F1로정확후속work를반환한다. 기대값을2로바꾸거나문서약속을약화하지않았다.\n\n수리전네반례red·초기연결fixture/defer오류·교정근거를보존했다. 최종양쪽같은270선택은각269passed/기존symlink권한1skip/exit0이고각875Python/실행tree소스전후가같다. 공식green은A2충족이나제품전체합격이아니다. 실제원자료의삭제/교차소유/파일손상·부재와제품의좌표있는Git/물질화복원실패를구별했고P01~P03/B130~B134/다른owner단언을유지했다.\n\n공식생성·마지막캐시동기화/check/skill-only·보존검사를끝냈다. runtime/실호출139입력·corpus144경로/150명시SHA·host8자료/도구5·baseline910/Gitblob·runtime/T4고정258경로는불변이다. 새유료/예약/학술호출·Git마감·기존연구운전·graphify갱신은없다. 역사실호출은불변경계의승인성질만한정재사용한다. P04단일지급수리와나머지P/N/TRUST/L01·최종G관문은manager의후속책임이다.',
'acceptance':[{'id':key,'result':'fail' if key=='A2' else 'pass','detail':detail,'evidence':ev[key]} for key,detail in details.items()],
'changes':changes,'seams':[],
'findings':[
 {'id':'F1','kind':'issue','detail':'A2의제안전문한번지급조건이실제answer/initial-0최종포장반환에서실패했다. proposal-observation의15반환중마지막은같은현재전문이role_review.proposal과role_review.self_messages[0].content에있어기대1/실제2다. 공식기존row는passed지만추가의미단언은exit1이다. _record_review_input의현재proposal메시지와context_for의현재판본전문보존이원인경로이며두runtime파일은writes밖이다. 현재최상위부재검사만으로는이중첩복제를검출하지못했다.','evidence':refs('proposal-observation.json','proposal-return-14.json','proposal-probe-process.json','proposal-probe.stderr','binding-review.md'),'affects':['run:phases/021/tasks/document-review/objective.md#A2','run:context.md#G1','run:context.md#G3','run:context.md#C10','repo:.claude/skills/do-math/scripts/do_math/review_cycle.py','repo:.claude/skills/do-math/scripts/do_math/review_engine.py','repo:.claude/skills/do-math/references/CLI-실행-계약.md'],'next_action':'현재전문을한번제공하되원메시지봉인/이전판본복원·stage가시성을보존하는좁은runtime work를배정한다. context_for와_record_review_input의책임을대조하고공유expected seat view/최종포장일치를유지한다. probe의기대1단언을제품회귀에편입한뒤정확단계/관련양쪽회귀와미러를재검증한다. A2와P04완료를보류한다.'},
 {'id':'F2','kind':'decision','detail':'B113의role_review/review_research와B114의pending_findings/review_sources반환추정을실제반환·포장·원자료검사로교체했다. B110의다른owner/B111~B112의명시소유/별칭/callable 및다른packet소비는유지한다. actualdiff/현재소비/존재7원보고SHA를확인했고역사counts를새성공에합산하지않았다. 필드결속수리의유효성과F1의단일지급미충족을구별하며PR24전체를종결하지않는다.','evidence':refs('history-verification.json','B113-p04-p05.diff','B114-p04-p05.diff','binding-review.md'),'affects':['run:context.md#C9','run:context.md#C10'],'next_action':'지정필드결속수리를유지하고F1후속수리와P06~P11/PR24의다른slice책임을별도로남긴다.'},
 {'id':'F3','kind':'fact','detail':'runtime139입력·corpus144경로/150명시SHA/Gitraw-clean·host8자료/도구5·baseline910바이트/Gitblob·고정runtime/T4 258경로를보존했다. 제품문서를변경하지않아이번task로문서prompt판본이바뀌지않는다. 이전실호출의승인성질만불변경계조건에서재사용하며새호출/준수성공이나G전체완료를주장하지않는다.','evidence':refs('preservation.json','verification.json','binding-review.md'),'affects':['run:context.md#C12','run:context.md#G7','run:context.md#G8'],'next_action':'원자료와지정변경을검수하고F1runtime수리의영향경계를재판정한다. 최종판본관문과나머지실연쇄/문서책임을유지한다.'},
 {'id':'F4','kind':'issue','detail':'최종양쪽unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported는기존Windows1314권한으로각1skip이다. 실제탈출반려는미검사이며통과로세지않는다. P04/P05직접반환/원자료필수검사에는skip이없다.','evidence':refs('c/report.json','m/report.json','c.stderr','m.stderr','verification.json'),'affects':['run:context.md#G4','run:plan.md'],'next_action':'G4최종기본전체에서원문상권한조건의정당성과남은미검사를별도로판정하고skip을passed로세지않는다.'}],
'checks':checks}
(E.parent/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('REPORT',report['status'],'changes',len(changes))
