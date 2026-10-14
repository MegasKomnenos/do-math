from work import *
base='run:phases/020/tasks/document-tools/evidence/'
def refs(*names):return [base+name for name in names]
verified=json.loads((E/'verification.json').read_text())
assert set(verified['suites']['c']['counts'])=={'passed','skipped'}
assert verified['suites']['c']['counts']==verified['suites']['m']['counts']=={'passed':199,'skipped':1}
assert verified['suites']['c']['selected']==verified['suites']['m']['selected']==200
details={
 'A1':'시작 skills/diff2675파일은019 manager source-inspected와 전건 일치했다. P03의 현재36문서 위치/조건을 실제 _context/record_map/prepare_role_input/install_tools로 연결했다. execution_window 안내와 동적 파일, scholarly 설정과 호출 성공, 같은 formal_verifier.preview 객체와 반환 JSON을 구별했다. B110~B114 actual diff 및 존재7원보고 SHA를 대조해 이 P03 AST slice 교체와 기본 record_map/명시 owner·별칭/이전 실제 결과 유지로 판단했다. PR24 전체 종결이 아니다.',
 'A2':'실제 Sim 엔진의 _context와 실제 build_profiles/prepare_role_input/install_tools를 사용했다. research_plan/maintenance/goal_audit에서 직접·참조 입력 및 readable/supplied_only를 검사했고 catalog 참조는 정확 파일·SHA/bytes를 읽었다. 설치3wrapper/archive 전체member와 현재 source bytes, schema/context/ext files, command/tool_sha256/snapshot/record_index/limits를 대조한다. Scholarly 비구성/구성 표본은 실제 고정 profile과 일치한다. 기존 LeanPreview/FormalInputManifest/role packaging 및 인용 시험을 유지/연결했다. Console sibling 시험은 설치/선택을,010host와012Lean 승인 원자료는 불변 경계의 실실행 성질만 한정 재사용한다.',
 'A3':'수리 전 동일6소유자 subTest가 ValueError not raised로 실패했다. 최종 같은 기본반려 시험과 실제 설치 정상/손상 검사가 passed다. 생산 뒤 사본에서 self_check_directory/command/checkpoint_bytes/max_artifact_bytes 삭제, 다른 지급command/wrapper 차용, 해시 변조·잘못된archive와 일치hash 쌍, 참조파일 손상을 반려한다. 미설치 preview 없음/검사반려를 정상 installed 증거와 구별했다. Console sibling 부재의 명시 FileNotFoundError/무부수효과, pinned override 반려/worker 추가0을 유지한다. 개별defer 오기·담당/호출 누락·다른owner 동시건너뜀 음성검사도 실행했다. 초기 helper 정본 오류와 maintenance map 가정 실패는 보존한 뒤 교정했다.',
 'A4':'최종 양쪽 동일200선택/고유row를 완결했다. 각199passed·기존권한1314 symlink1skipped·실제exit0이고 실패/오류/미실행은 없다. 각875Python SHA와 해당tree 비캐시 전후소스가 불변이다. 생성계획13경로가 writes안이며 공식생성/마지막캐시동기화/check1336/skill-only를 통과했다. Runtime139입력·corpus144경로/150명시SHA/Gitraw-clean·host8자료/도구5·baseline910/Gitblob·T4고정경계를 보존했다. Skip은 통과/실제탈출반려로 세지 않고 G4에 남긴다. 문서 두문장은 향후prompt판본을 바꾸며 역사실호출의 승인성질만 한정재사용한다. 나머지P/N/REVIEW/TRUST/L01/G4~G6/G8은 후속책임이다.'}
ev={
 'A1':refs('start-comparison.json','input-audit.json','current-bindings.json','history-verification.json','B110-p03.diff','binding-review.md'),
 'A2':refs('binding-review.md','c/report.json','m/report.json','verification.json','preservation.json'),
 'A3':refs('red/report.json','red.stderr','focus/report.json','corrected/report.json','augmented/report.json','c/report.json','m/report.json','binding-review.md'),
 'A4':refs('verification.json','c-process.json','m-process.json','c-before.json','c-after.json','m-before.json','m-after.json','mirror-plan.json','mirror-build.stdout','cache-sync.json','mirror-check.stdout','skill-only.stdout','preservation.json')}
changes=[]
for path in verified['changes']:
    if '.timings' in path:detail='공식 관련 실행의 비용 캐시와 마지막 정본→미러 동기화.'
    elif path.endswith('support/doc_code.py'):detail='P03 AST 조립을 실제 입력 경계로 교체; 개별 defer와 실제 객체 필드 순회. 기본 record_map 및 다른owner 유지.'
    elif path.endswith('support/engine_context.py'):detail='실제 fitted source/설치wrapper/archive/schema/limits/권한을 검증하는 P03 공통 검사.'
    elif path.endswith('sim/test_role_input_context.py'):detail='실제 직접·참조·독립 입력과 설정/미설치 조건, 필드/명령/파일/hash/참조손상 검사.'
    elif path.endswith('structure/test_doc_code.py'):detail='소유자 기본반려·개별defer·담당호출/누락 음성과 저장/입력 구별 유지.'
    elif path.endswith(('test_submission_preview_commands.py','test_knowledge_project_identity.py')):detail='기존 실제 preview 설치 결과를 문서/파일 검사에 연결; 이전 console/project 반려 유지.'
    elif path.endswith('공통-실행.md'):detail='preview가 설치 후 formal_verifier.preview에 지급된 객체이며 부재시 명령을 가정하지 않는다고 명시.'
    else:detail='기존 실제 결과 문서순회에서 정확 P03여섯owner만 실제 설치 담당으로 defer; 해당owner의 기존 검사는 유지.'
    if path.startswith('.agents/'):detail='공식 생성 사본. '+detail
    changes.append({'path':path,'detail':detail})
checks=[]
labels=['red','focus','corrected','augmented','c','mirror-plan','mirror-build','m','bindings','temp-check','cache-sync','mirror-check','skill-only','preservation','output-audit']
for label in labels:
    receipt=json.loads((E/(label+'-process.json')).read_text())
    code=receipt['exit_code']
    assert code is not None
    result='pass' if code==0 or label=='red' and code==1 else 'fail'
    detail={'red':'수리 전6소유자 공백의 예상 실패1/exit1 확인.',
            'focus':'초기helper의 잘못된 contracts.extension_schema 정본 참조로1error/exit1; runtime 결함이 아니며 corrected/c에서 교정.',
            'augmented':'maintenance의 inline verifier를 map으로 가정한 초기시험 실패1/exit1; 실제goal_audit map으로 교정하여 c에서 통과.',
            'c':'200선택/199passed·기존권한1skip. 255.0초; 소프트예산 초과는 단언을 약화하지 않고 기록.',
            'm':'정본과동일200선택/199passed·기존권한1skip. 실패/오류/미실행없음.'}.get(label,'실제argv/cwd/env/PID/시각/exit와 전후소스를 원receipt/output에 보존했다.')
    checks.append({'command':subprocess.list2cmdline(receipt['argv']),'cwd':'repo:.','result':result,'exit_code':code,
                   'evidence':refs(label+'-process.json',label+'.stdout',label+'.stderr'),'detail':detail})
report={
 'status':'complete',
 'narrative':'P03 여섯 문서소유자를 실제 설치 후 최종역할입력에 연결하여 A1~A4를 완료했다. 시작2675파일은019검수본과 같고 실제 변경26경로(정본12·미러12·비용캐시2)는 writes안이다. Runtime/공용계약/engine/runner/adapter/Jobfixture/corpus는 고정했다. 같은 formal_verifier.preview를 별도문서owner로 읽고 기본record_map 실제반환과 P01/P02·B130~B134를 보존했다.\n\n수리전6반례 red, 초기helper정본오류와inline/map가정실패, 각각의 교정근거를 원보고로 보존했다. 최종양쪽 같은200선택은199passed·기존symlink권한1skip·실제exit0이며 각875Python/검사tree소스전후가 같다. skip은 통과나 실제탈출반려 증거가 아니다. 실제 생산·설치·포장·archive/참조파일 대조와 반환뒤 손상반려를 시행했으며 외부포트대역과 실실행 재사용범위는 binding-review.md에 명시했다.\n\n공식미러생성·마지막캐시동기화/check/skill-only와 보존검사를 끝냈다. 기존runtime139입력·corpus144경로/150명시SHA·host8원자료/도구5·baseline910/T4고정경계는 불변이다. 문서 두문장은 향후일반역할prompt에 반영되며 과거 고정smoke의 승인된성질만 한정재사용한다. 학술configured/preview지급을 실호출/검증성공으로 세지 않는다. PR24전체·P04~P11/REVIEW/TRUST/나머지P/N/L01 및 최종 G4~G6/G8은 남으며 새실호출이나Git마감은 수행하지 않았다.',
 'acceptance':[{'id':key,'result':'pass','detail':detail,'evidence':ev[key]} for key,detail in details.items()],
 'changes':changes,'seams':[],
 'findings':[
  {'id':'F1','kind':'decision','detail':'B110 P03의 AST반환추정은 실제_context/설치/포장검사로 교체했다. record_map기본실반환 및 B111~B114의 명시owner·별칭·저장/입력구별·다른packet소비는 유지한다. actualdiff/현재소비/존재7원보고 SHA를 확인했고 역사counts를 현재성공에 합산하지 않았다. PR24전체종결이 아니다.','evidence':refs('history-verification.json','B110-p03.diff','binding-review.md'),'affects':['run:context.md#C9','run:context.md#C10'],'next_action':'P03지정slice를 닫고 나머지PR24/REVIEW/TRUST/packet의 후속책임을 유지한다.'},
  {'id':'F2','kind':'fact','detail':'Runtime139입력·corpus144경로/150명시SHA와Gitraw-clean·host8자료/도구5·baseline910/Gitblob·T4고정경계가 시작과같다. 미래prompt의preview문장만 바뀌므로 과거host/Lean/학술/모델의 승인된고정입력성질만 한정재사용한다. 새문서읽기/준수나새실호출성공은 주장하지 않는다.','evidence':refs('preservation.json','binding-review.md','verification.json'),'affects':['run:context.md#C12','run:context.md#G7','run:context.md#G8'],'next_action':'검수후 제품24비캐시경로를 관리마감하고 최종판본관문 및 필요한 prompt재사용판정을 후속으로 유지한다.'},
  {'id':'F3','kind':'issue','detail':'최종양쪽unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported는 기존Windows1314권한으로각1skip이다. 통과나실제탈출반려증거가아니다. P03필수설치/입력성질은 전부실행됐다.','evidence':refs('c/report.json','m/report.json','c.stderr','m.stderr','verification.json'),'affects':['run:context.md#G4','run:plan.md'],'next_action':'최종기본전체에서 환경조건의 원문정당성과 남은미검사를 별도로판정하며 skip을passed로세지않는다.'}],
 'checks':checks}
(E.parent/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('REPORT',report['status'],'changes',len(changes))
