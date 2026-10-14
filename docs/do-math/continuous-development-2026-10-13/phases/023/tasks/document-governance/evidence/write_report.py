from work import *
verification=json.loads((E/'verification.json').read_text(encoding='utf-8-sig'))
assert verification['suites']['c2']['exit_code']==verification['suites']['m']['exit_code']==0
prefix='run:phases/023/tasks/document-governance/evidence/'
def refs(*names): return [prefix+n for n in names]
suite=verification['suites']['c2']
mirrored=verification['suites']['m']
details={
 'doc_code.py':'P06/P10 네 owner의 소비/반환 AST 결속을 실제 값 필수 경계로 교체했다. 정확 owner·line-local 별칭·payload={} 조건을 유지하고 일반 순회의 명시 위임만 허용한다. 다른 생산자의 AST helper는 유지한다.',
 'engine_context.py':'실제 payload/check/view/status 문서 검사와 원문·승인·seal·execution·모집단·판본 및 독립 status/reason 기대를 결속하는 한정 도우미를 추가했다. 기존 도우미 함수는 시작과 같다.',
 'test_doc_code.py':'네 owner의 실제 값 없는 통과 반례, 소유 혼동·빈 payload 조건, 정확 담당/owner/method 누락·오기 반려를 추가했다. 다른 owner·callable·배열·부재 단언을 유지했다.',
 'test_governance_imports.py':'실제 prepare_import/check_import의 네 decision/scope 사례와 반환 사본 hash/실행/bundle/check 차용 반려를 추가하고, 기존 payload target 사례에 kind 필수/owner 일치 및 실제 문서 검사를 결속했다.',
 'test_governance_records.py':'실제 현재 governance 반환을 원 source/별도 승인·active charter·goal/policy 판본과 연결했다. 모든 반환 키 삭제·다른 판본/상태 객체 및 헌장 부재/비유일성 반례를 확인한다.',
 'test_academic_requirements.py':'실제 academic_status의 미해결·해결 근거 부재·학술 요구 없음·pending/active/외부 거부 분기를 명시 기대에 연결하고 반환 삭제/다른 상태를 반려한다.',
 'test_governance_interpretation.py':'실제 엔진 수신 경로의 실패 findings와 검사 승인 후 사용자 결정 대기에서 payload 및 bundle.check의 문서 결속을 확인한다.',
 'test_governance_context.py':'실제 intent_interpretation 최종 포장에서 현재 승인 governance와 정확 original_source를 확인한다.',
 'test_academic_consumers.py':'실제 독립 TASKS/academic assessment가 만든 completed, 연구 계획/목표 감사의 최종 포장과 fixed checker context, 수행 근거 변경 후 active를 문서/독립 기대에 결속했다.',
 'test_knowledge_impact_review.py':'실제 impact-request 소비에 각 mutation target의 previous_hashes 누락/변조 반려와 상태 무변경을 추가했다.',
 'test_planning_revision_transitions.py':'기존 실제 revision_requests followup에서 과제를 즉시 바꾸지 않는 전후 불변 단언을 추가했다.',
 '.timings.json':'공식 관련 실행의 비용 캐시와 정본→미러 마지막 동기화 결과다.'}
changes=[]
for path in verification['changes']:
    name=Path(path).name
    detail=details.get(name,'기존 해당 owner 문서 순회에서 P06/P10 네 owner를 실제 담당으로 명시 위임했다. 이 모듈 자신의 기존 소유자/오류/값 단언은 유지한다.')
    if path.startswith('.agents/'):
        detail='공식 생성기의 대응 미러. '+detail
    changes.append({'path':path,'detail':detail})
checks=[]
for name in ('temp-check','red','focus','corrected','history','sections','preservation','mirror-build',
             'c','c2','cache-before-m','m','cache-sync','diff','mirror-check','skill-only','audit','sources-final'):
    process=json.loads((E/(name+'-process.json')).read_text(encoding='utf-8-sig'))
    result='pass' if process['exit_code']==0 or name=='red' else 'fail'
    detail='실제 argv/cwd/명시 환경/PID/UTC 시작·종료/exit, stdout/stderr 및 skills/diff 전후 SHA를 보존했다. 업무 판정은 binding-review.md와 해당 원자료에 설명한다.'
    if name=='red': detail='수리 전 한 method의 네 owner가 실제 값 없이 통과하는 공백을 네 ValueError 미발생 subTest/failed row/exit1로 의도대로 관측했다.'
    elif name=='focus': detail='새 도우미의 별도 승인 원문 혼동, kind 누락의 정확 오류 기대 및 담당 호출 표기 문제로 3 failed row/exit1이었다. 원실패를 유지했고 직접 소유/현재 계약과 명시 호출로 교정한 corrected 및 최종 같은 ID의 통과에 연결했다.'
    elif name=='c': detail='첫 460선택은456passed·권한1skip·observer KeyError3/exit1이다. action.role이 항상 있다는 자기 evidence 도우미의 가정이 기존 유효 포장 입력을 방해했다. 원 도우미/원실패를 보존하고 실제 execution_profile.role을 읽도록 도우미만 교정했다. 최종 c2와 제품/시험875개 SHA는 같다.'
    elif name in ('c2','m'):
        row=verification['suites'][name]
        detail=f"최종 동일{row['selected']}선택/고유row, {row['counts']['passed']}passed·Windows1314 권한1skip·실제exit0. {row['source_sha256_count']} Python과 비캐시 전후/현재 SHA가 같고 실제 최종 반환{row['final_returns']}·check{row['checked_returns']}·academic query{row['academic_queries']}를 보존했다. 제안 전문{row['single_proposal_returns']}반환은 전부 독립 기대1이다. skip은 passed나 실제 탈출 반려 근거가 아니다. 전체 일반/T3/변이/T4/T5 최종 관문을 대신하지 않는다."
    checks.append({'command':subprocess.list2cmdline(process['argv']),'cwd':'repo:.','result':result,
        'exit_code':process['exit_code'],'evidence':refs(name+'-process.json',name+'.stdout',name+'.stderr'),
        'detail':detail})
report={
 'status':'complete',
 'narrative':f"P06 수입 입력/독립 검사 결과와 P10 현재 헌장/학술 상태를 실제 소비·반환·최종 역할 입력에 연결했다. 시작 skills/diff2675파일은022 manager 판본과 전건 같고 기존 dirty를 보존했다. 변경{len(changes)}경로는 모두 writes 안이다. 제품 runtime·문서·스키마·포트·runner/adapter·Job fixture·corpus는 불변이며 실제 저장/적용/포장을 대역으로 가리지 않았다. 네 owner의 값 없는 통과 반례를 먼저 남긴 뒤 읽기/반환/추가 AST 결속을 실제 값 필수 경계와 한정 문서/계약 단언으로 교체했다. 상세 현재 구간·입출력·실제 담당과 정상/반례는 binding-review.md, packets/bindings 및 section-name-decisions에 있다.\n\n수입 bundle과 bundle.check, check.sha256와 submission_check.passed, 독립 검사 승인과 사용자 권한/실제 적용을 구별한다. 현재 헌장의 원 입력과 별도 승인 원문·ID/판본을 유지하며, 학술 조회의 조건별 기대와 실제 completed/최종 포장·근거 변경을 확인한다. N02-014 네 이름은 현재 consumer와 기존 의미 검사에 연결했고 previous_hashes 누락/변조와 개정 요청의 과제 무변경만 보완했다. B111/B113의 관련 hunk를 교체하고 B110~B114 존재7원보고 및 B119~B122 닫힌 PURE 원보고/모집단을 유지한다. 다른 hunk/PR24·전체 N 의미 완료나 역사 counts 합산은 주장하지 않는다.\n\n최종 정본/미러는 같은{suite['selected']}선택·고유row의 각{suite['counts']['passed']}passed/권한1skip/exit0이며 각875 Python과 전후 판본이 일치한다. 실제 반환/check/학술 조회를 원자료로 남겼고 현재 제안 전문{suite['single_proposal_returns']}개 최종반환의 기대1도 유지했다. 변경을 소비하지 않는 이전 review8모듈은 source/import 근거로 제외해022의 유효한 성질만 재사용했다. 초기 focus3실패와 첫 통합 c의 observer3오류는 원실패로 보존했으며, 자기 도우미의 가정을 교정한 뒤 새 c2/m으로 완결했다. 제품/시험을 바꾸거나 실패를 성공으로 덮지 않았다.\n\n공식 미러 생성·비용 캐시 동기화·--check·skill-only와 실제 범위/원바이트 인도를 완료했다. 022의 새review_cycle을 기준으로 runtime/실호출139입력·고정경계258·corpus144/명시SHA150/Git raw-clean·host8/도구5·baseline910/Gitblob 및022 원task{verification['previous_task_files_unchanged']}파일을 보존했다. 승인된 불변 하위 실호출 성질만 재사용하며 새 유료/예약/학술 호출·연구 재개/삭제·graphify 갱신·Git stage/commit/reset/checkout/push는 없다. Windows1314 symlink의 실제 반려, P08/P09/P11·다른 N/L01, 전체 일반/freshT3/전수변이·G7 최종판 연결·최종 review는 후속 책임이다. complete는 배정 A1~A5의 완료다.",
 'acceptance':[
  {'id':'A1','result':'pass','detail':'시작2675파일의 현재 SHA/기존dirty와 역사 P06/P10→현재 문장/정확 owner를 대조했다. 네 owner의 실제 값 없는 통과를 수리 전 네 red subTest로 확인했고 독립 입력/계약 기대에 연결했다.',
   'evidence':refs('start-comparison.json','git-status.stdout','input-audit.json','packets.json','bindings.json','current-sections.json','red/report.json','red.stderr','task-changes.diff')},
  {'id':'A2','result':'pass','detail':'실제 payload 소비/owner 대상·{} 무변경, prepare_import/check_import의 source·seal·unit/question·독립 execution·check SHA와 실제 엔진 수신에 연결했다. 네 verdict/scope, 반환 삭제/변조/다른 bundle·check 및 passed 차용을 반려하며 기존 승인/현재성/재적용 성질을 유지했다.',
   'evidence':refs('c2/report.json','m/report.json','c2-observations.json','m-observations.json','binding-review.md','verification.json')},
  {'id':'A3','result':'pass','detail':'현재 유일한 승인 헌장/정확 두 원문·승인 ID/goal·policy 판본 및 반환 삭제/다른 상태를 검사했다. academic의 조건별 실제 반환과 실제 독립 TASKS 소비의 completed, 연구 계획/목표 감사의 최종 지급·근거 변경을 확인했다. 기존 P01~P05/P07·PURE 및 단일 전문/정확 복원을 유지한다.',
   'evidence':refs('c2/report.json','m/report.json','c2-observations.json','m-observations.json','history-verification.json','change-coordinates.json','binding-review.md','verification.json')},
  {'id':'A4','result':'pass','detail':'현재 제목으로 여섯 고정 구간과 N02-014 네 정확 문장을 현재 consumer/기존 단언에 연결했다. 실제 이전 hunk/원보고의 한정 유지·교체를 판정하고 빠진 두 좁은 축만 보완했다. 문서 본문 교정은 필요하지 않았으며 다른 packet/전체 N 의미를 인증하지 않는다.',
   'evidence':refs('current-sections.json','previous-revision-names.json','section-name-decisions.json','revision-tests.json','history-verification.json','binding-review.md','verification.json')},
  {'id':'A5','result':'pass','detail':f"같은 최종{suite['selected']}선택/고유row의 양쪽 각{suite['counts']['passed']}passed·권한1skip·exit0, 875 Python/전후 SHA 및 실제 원반환/전문1을 확인했다. 허용 범위의 공식 미러/캐시/--check/skill-only,022 판본의 보존/한정 재사용을 완료했다. skip과 전체 관문은 명시 남김이다.",
   'evidence':refs('related-selection.json','selection-decisions.json','verification.json','preservation.json','final-preservation-check.json','mirror-plan.json','mirror-build.stdout','cache-sync.json','mirror-check.stdout','skill-only.stdout','change-coordinates.json')}],
 'changes':changes,'seams':[],
 'findings':[
  {'id':'F1','kind':'fact','detail':'P06/P10 네 owner의 AST 모양 추정을 실제 값 필수 문서 검사와 입력/반환/최종 지급의 독립 단언으로 교체했다. 검사 승인/사용자 권한/적용, 현재 헌장 두 원문, 수학 해결/학술 후속/외부 효과의 의미는 개정하지 않았다. 제품 runtime/문서는 불변이다.',
   'evidence':refs('binding-review.md','verification.json','task-changes.diff'),
   'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G3'],
   'next_action':'P06/P10의 이 지정 남김을 새 실제 근거로 처분하되 다른 packet/전체 N 및 최종 G 완료로 확대하지 않는다.'},
  {'id':'F2','kind':'fact','detail':'B111의 P10 두 반환 AST와 B113의 P06 읽기/반환/추가 AST hunk만 교체했다. B110~B114 존재7원보고와 B119~B122 PURE 네 원보고/실제 diff 및 현재 다른 owner 단언을 유지했다. PR24 전체는 미종결이다.',
   'evidence':refs('history-verification.json','change-coordinates.json','binding-review.md'),
   'affects':['run:context.md#C9','run:context.md#G2','run:context.md#G3'],
   'next_action':'이 한정 slice의 교체/유지만 반영하고 역사 counts·다른 hunk/PR24 남김을 유지한다.'},
  {'id':'F3','kind':'decision','detail':'N02-014의 impact_set/previous_hashes/revision_requests/revision_resolutions는 현재 실제 소비와 기존 의미 검사를 유지했다. mutation별 hash 누락/변조 반려와 요청의 과제 무변경을 보완했다. 정확 네 이름/문장에 대한 판정이며 전체 네 N 절/모집단, input_overflow/question_links나 운영 scope/replay_safety/repair_target의 인증은 아니다.',
   'evidence':refs('section-name-decisions.json','c2/report.json','m/report.json','binding-review.md'),
   'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G3','run:plan.md'],
   'next_action':'022 F5의 개정 네 이름은 이 정확 범위의 유지/보완 근거로 처리하고 P09/P11·운영 처분·P08/TRUST 및 다른 N/L01의 구체적 후속 질문을 유지한다.'},
  {'id':'F4','kind':'issue','detail':'최종 양쪽 ContextStoreTests.test_outside_symlink_is_reported_when_supported는 Windows1314로 각1skipped다. 실제 symlink 탈출 반려는 미검사이며459passed에 포함하지 않았다.',
   'evidence':refs('verification.json','c2/report.json','m/report.json','c2.stderr','m.stderr'),
   'affects':['run:context.md#G4','run:plan.md'],
   'next_action':'G4 최종 기본전체에서 원문상 환경조건의 정당성과 실제 미검사를 별도로 판정하고 skip을 통과로 세지 않는다.'},
  {'id':'F5','kind':'fact','detail':'022 판본 기준 runtime/실호출139입력·고정runtime/T4 258경로·corpus144/명시SHA150/Git raw-clean·host8자료/도구5·baseline910 원바이트/Gitblob과022 원task 자료는 불변이다. 과거전체 설치/T4 및 모델 독해의 한계는 유지하며 불변 하위 실호출의 승인 성질만 재사용한다.',
   'evidence':refs('preservation.json','verification.json','binding-review.md'),
   'affects':['run:context.md#C12','run:context.md#G4','run:context.md#G5','run:context.md#G6','run:context.md#G7','run:context.md#G8'],
   'next_action':'검수한 정확 제품/시험/미러 경로의 관리 마감과 최종 전체 일반/freshT3/전수변이·G7 최종판 연결·제품 수정 없는 review를 이어간다. 기존 성공을 새 전체 관문으로 합산하지 않는다.'}],
 'checks':checks}
save('../report.json',report)
print('Report complete; changes',len(changes),'acceptance',len(report['acceptance']),'findings',len(report['findings']),'checks',len(checks))
