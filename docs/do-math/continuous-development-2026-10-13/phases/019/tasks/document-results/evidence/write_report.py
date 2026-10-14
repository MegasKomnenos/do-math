from work import *

def read(name): return json.loads((E/name).read_text(encoding='utf-8-sig'))
v=read('verification.json')
assert set(v['suites'])=={'red','focus','corrected','c','m'}
assert v['suites']['c']['counts']==v['suites']['m']['counts']=={'passed':186,'skipped':1}
prefix='run:phases/019/tasks/document-results/evidence/'
def refs(*names):return [prefix+name for name in names]

review='''# P02 문서 결속 검토와 인계

시작 HEAD는 a29f3c6a7889a74bc35af7360e36de9492ad814a다. 시작 skills/diff 2,675개 SHA256은 phase 018 manager source-inspected와 전건 일치한다. Git dirty의 canonical.py/repository.py·migration fixture, 두 미추적 시험의 양쪽 사본과 운영자 작문 도구·서비스 설정은 시작부터 존재하며 이 task에 귀속하지 않는다. 시작 Git diff·index·상태와 해시를 따로 보존했다. 제품 파일의 현재 변경은 지정 writes 안에서만 발생했다.

| P02 소유자 | 실제 생산·소비와 담당 | 확인한 성질 |
|---|---|---|
| source_ref | write_source_catalog / ContextStoreTests.test_new_catalog_is_hashed_from_the_bytes_it_wrote; fit_context와 prepare_role_input의 실제 참조 파일도 읽음 | canonical JSON 원바이트, path/SHA256/bytes/format, catalog total 및 축소 항목 total. 큰 목록의 catalog 참조와 과제 행의 input/details 참조·snapshot을 구별 |
| research_sources | _context의 sources → prepare_role_input / PackagedInputTests.test_planning_keeps_completed_report_and_active_work_as_readable_context | 문서 sources 별칭, 이번 workspace의 정확 input/sources 경로, 원 source record·artifact SHA·snapshot 원바이트, 완료 과제 읽기와 선택 모집단 분리 |
| materialized_output_files | _preserve_outputs와 _context / PackagedInputTests.test_task_result_paths_survive_packaging_without_entering_validation_hashes; 기존 600k 실제 흐름 | stored artifact_ref/path/hash/size와 새 input/task-results/<task>/<execution>/<path>를 대조. 동일 바이트라도 다른 과제·실행 경로 차용 반려 |
| results | _apply의 실제 저장 결과 / sim 수신 시험 및 AcceptanceTests.test_large_accepted_report_survives_revision_review_and_resumed_work | report 전바이트, 저장 output_files·복원 파일, 독립 knowledge/relations/integration_bundles의 결과 비중복, 개정·계약 검토·재개에서 600k 보고와 증거 파일 보존 |

수제 task.results fixture는 물질화 검사에만 사용한다. _apply 생산과 knowledge의 별도 권위 기록은 기존 KnowledgeConnections·ReceiptPreservationTests에서 직접 관측한다. 실제 제출의 bundle 분할/수신·재시도와 owns_response=False의 보고 비중복은 기존 수신 시험을 유지했다. integration.member_values는 manifest를 연구 응답 본문에서 분리하며 _apply도 같은 필드를 보존 결과에서 제외한다. 정상 bundle manifest를 task.results에 다시 저장하는 새 계약을 만들지 않았다. 파일 보존은 실제 600k 보고/부분 evidence의 저장과 재개 입력으로 연결한다. 엔진, 저장소, _context, _apply, _preserve_outputs, prepare_role_input을 대역으로 가리지 않았다. 기존 모델·Git·Lean의 외부 포트 대역 경계는 유지했다.

일반 scoped_field_issues는 네 소유자가 실제 입력 없이 검사될 때 기본 거부한다. 실제 경계를 가진 여섯 소비 모듈의 문서 순회만 명시 defer하며, structure의 로컬 담당 대응 검사가 네 owner와 담당 method의 실제 assert_result_documents 호출을 확인한다. 오기·담당 누락·없는 method·문서 검사가 없는 method로 교환하면 실패한다. 네 owner의 defer가 P01 operational_evidence, 일반 재개 result_source 또는 status까지 건너뛰지 않는 음성 단언을 유지했다. 새로운 전역 담당 등록부나 제품 AST 추론기를 만들지 않았다. 기존 AST helper는 다른 P03/REVIEW/TRUST 소비가 남아 있으므로 유지하고 P02의 source_ref/stored_file/restored_file/retained/result 조립만 제거했다.

반환 후 사본 교란은 실제 제품의 입력 반려와 구별한다. 실제 catalog 참조의 경로 차용·hash/size 변조, 복원 결과의 report 삭제·각 output file의 local_path 삭제·hash/size 변조·다른 실행의 동일 바이트 경로 차용, 원자료의 경로/hash/size 교란, 저장 execution에 local_path를 붙이는 대체 증거를 검사한다. 실제 값으로 문서 필드 오기와 다른 owner의 동명 필드를 반려한다. 두 output file을 각각 교란하므로 한 항목의 정상 필드로 다른 항목의 누락을 가리지 않는다. 정상 빈 sources/results와 명시 index의 부재도 검사하지만 빈 배열을 원소 필드의 정상 증거로 쓰지 않는다. 실제 _context의 source/task artifact hash 손상은 정확 ValueError와 미물질화를, 실제 read_source의 hash/size 손상은 정확 error_type/reason·빈 bytes·range=None을 확인한다.

수리 전 red는 한 test method의 8개 owner/별칭 subTest가 ValueError not raised로 실패했다. focus의 13error/22passed는 _context 관련 다른 소비가 쓰는 context_store import를 잘못 제거한 NameError와, 준비 역할의 좁은 tasks에서 다른 과제를 찾은 StopIteration이었다. import를 복구하고 조회 권한의 전건 task_catalog에서 다른 과제 원문을 찾게 교정했다. corrected 23passed를 연결했다. 첫 문서 편집 스크립트의 CRLF 가정 실패는 공통-실행의 첫 문장만 반영됐고 지식 문서 바이트는 쓰기 전이었다. 개행과 무관한 정확 문장 교체로 끝냈다. 초기 mirror-plan의 iter_files 반환형 가정과 출력 감사의 selected/진행 중 report 가정 오류는 자기 evidence 스크립트만 교정했다. 실패 출력과 원 스크립트를 제품 실패/정상 결과로 바꾸지 않았다.

B110~B114의 실제 도입 Git diff·현재 P02 소비·phase 001 분석을 대조했다. 해당 7개 저장소 원보고의 SHA256도 현재 파일과 같지만 역사 counts를 이번 성공에 합산하지 않는다. B113의 source_ref AST 결속과 B114의 stored/restored/results 문자열 조립은 실제 writer/_context/_apply 결과로 교체했다. B110~B112의 명시 owner·line-local 별칭·저장/역할 입력 구별은 유지한다. B114의 review_sources는 다른 REVIEW 경계이므로 그대로 둔다. PR24 전체나 다른 hunk의 재검토 완료를 주장하지 않는다. P01 및 B130~B134의 default-reject/defer/실제 반환·manifest/continuation/profile_selection 단언은 최종 관련 선택에서 유지됐다.

문서 수정은 공통-실행의 source_ref.sha256/bytes 명시와 지식-저작과-재사용의 sources[].local_path 및 해당 research_sources 별칭이다. 결과 읽기 권한과 선택 모집단의 차이, 과거 artifact와 이번 local_path 구별, 읽기 실패를 빈 목록으로 바꾸지 않는 설명은 보존했다. 입력 계약·입출력 스키마·runtime을 바꾸지 않았다.

정본과 미러는 동일 187 ID를 전부 실행해 각각 186passed·1skipped·exit0다. 실패·오류·미실행은 없고 공식 Python 875개 및 검사 tree의 비캐시 파일 전후 해시가 전건 일치한다. skip은 기존 ContextStoreTests의 실제 심볼릭 링크 생성이 Windows 1314로 반려된 권한 조건이며 해당 파일의 원래 skip 처리다. 권한을 바꾸거나 정상으로 세지 않는다. P02 필드/파일 결속 성질에는 이 skip이 없지만 G4의 조건부 환경 남김은 manager가 별도로 판정해야 한다. 소프트 예산 초과는 공식 보고에 보존하며 단언을 약화하지 않았다.

공식 생성 계획의 15개 변경은 모두 writes 안이었다. 생성 후 동일 선택의 미러 실행, 마지막 비용 캐시 동기화와 --check/skill-only를 확인한다. runtime/실호출 입력139·corpus144경로/150명시SHA·host8원자료·도구5SHA·과거baseline910/Git blob·기존 T4 runner/adapter/Job fixture를 보존했다. 이전 실호출의 승인된 성질만 같은 입력/도구 바이트에서 한정 재사용한다. 두 문장 변경은 향후 일반 역할 prompt 판본을 바꾸므로 역사 고정 smoke prompt의 성공을 새 문서 읽기/준수의 증거로 확대하지 않는다.

이 작업은 P02의 지정 문서 결속을 닫는다. P03, REVIEW/TRUST·다른 P/N, L01 운전 프로필·출력 단위, G4 기본전체·G5 fresh T3·G6 전수변이 및 G8 최종 review는 남는다. 전체 T4 재실행·새 T5/유료/예약/학술 호출·설치 신뢰 변경·기존 연구 재개/삭제·graphify 갱신·Git stage/commit/reset/checkout/push를 수행하지 않았다.
'''
(E/'binding-review.md').write_text(review,encoding='utf-8')

checks=[]
for label in ('red','focus','corrected','c','m','doc-edit','mirror-plan','mirror-build','history-review','preservation','output-audit-interim','output-audit-c','cache-sync','mirror-check','skill-only','output-audit-final'):
    path=E/(label+'-process.json')
    if not path.exists():continue
    obj=read(path.name)
    assert obj['exit_code'] is not None
    result='pass' if obj['exit_code']==0 or label=='red' else 'fail'
    detail={'red':'수리 전 기대한 owner/별칭 8subTest 실패를 보존했다. 제품 성공이 아니다.',
        'focus':'초기 수리 코드의 NameError와 fixture의 좁은 tasks 조회 오류를 보존했다. corrected와 최종 실행에서 해소했다.',
        'c':'187선택/고유row,186passed·1기존 권한조건 skip,exit0. skip을 통과로 세지 않는다.',
        'm':'정본과 같은187ID/고유row,186passed·1기존 권한조건 skip,exit0. 새로운 실호출은 없다.',
        'output-audit-interim':'진행 중인 미러 report를 최종 형식으로 가정한 자체 감사 오류다. 종료 상태를 먼저 확인하도록 고쳐 최종 감사에서 통과했다.'}.get(label,'실제 argv/cwd/환경·PID·시각·exit와 stdout/stderr·전후 소스를 보존했다.')
    evidence=refs(label+'-process.json',label+'.stdout',label+'.stderr')
    if label in v['suites']:evidence+=refs(label+'/report.json')
    checks.append({'command':subprocess.list2cmdline(obj['argv']),'cwd':'repo:.','result':result,
                   'exit_code':obj['exit_code'],'evidence':evidence,'detail':detail})
details={
 'support/doc_code.py':'P02의4owner를 실제입력경계로 전환하고 AST/문자열조립을 제거했다. 소유자별default거부/defer와 실제객체·별칭 필드순회를 추가했다.',
 'support/engine_context.py':'실제catalog/원자료/과제결과와 workspace·task·execution·artifact·snapshot·SHA256·크기를 대조하는 공통검사와 반환사본교란검사를 추가했다.',
 'structure/test_doc_code.py':'네owner의default거부/잘못된defer/담당method·실제문서검사호출의누락반례를 추가했다. P02의구문표본단언은실제writer/복원시험으로 이관하고나머지owner단언을 유지했다.',
 'sim/test_role_input_context.py':'기존물질화/과제전건읽기시험에 실제결과·두파일·동일바이트다른실행차용·저장execution대체반례를 결속했다. 빈입력과 실제_context hash손상반려를 추가했다.',
 'unit/test_context_catalog.py':'기존writer/축소시험의 실제canonical JSON·path/hash/bytes/format/total과참조교란을 검사하고 실제read_source hash/size의정확오류사유를 보강했다.',
 'sim/test_submission_receiver.py':'기존실제_apply의저장report·독립knowledge권위·비중복필터와결과문서검사를 보강했다.',
 'flows/test_submission_acceptance.py':'기존600k보고·파일의개정/계약검토/재개모델입력에서 실제저장/복원결과와문서·사본교란을 검사한다. 새엔진시나리오는 만들지 않았다.',
 'references/공통-실행.md':'기존catalog읽기지시에 실제source_ref.sha256과source_ref.bytes필드명을 명시했다.',
 'references/지식-저작과-재사용.md':'원자료읽기경로를 sources[].local_path로 명시하고 research_sources의line-local별칭에 결속했다.'
}
def change_detail(p):
    if Path(p).name in ('.timings.json','.timings-t3.json'):
        return '공식실행의비용캐시및미러동기화. 성공의근거로사용하지 않는다.'
    rel=p.split('/skills/do-math/',1)[1]
    key=rel.removeprefix('scripts/tests/')
    detail=details.get(key,'기존자기owner의실제문서검사를 유지하고P02네owner만명시defer하여각담당검사에 위임했다.')
    return detail+(' 정본에서공식생성한미러다.' if p.startswith('.agents/') else '')
for label in ('mirror-check','skill-only','output-audit-final'):
    assert read(label+'-process.json')['exit_code']==0
report={
 'status':'complete',
 'narrative':'P02의 네 문서 소유자를 실제 catalog·저장 결과·복원 파일·최종 역할 입력에 연결해 A1~A4를 완료했다. 시작 skills/diff2675파일은018 manager 판본과 같고, 기존 dirty 및 운영자 설정은 보존했다. source_ref와 stored/restored/results의 AST·문자열 조립을 제거하고 실제 writer/_context/_apply/포장 결과와 해당 workspace·artifact·snapshot·SHA256·bytes를 검사한다. 수제 results의 물질화와 실제 생산을 구별하며, 기존 수신/600k보고·증거파일의 개정·재개 흐름을 보강했다.\n\n수리 전 owner/별칭8반례의 red, 초기 수리/fixture13error, corrected23passed 및 최종 정본/미러 동일187선택을 원자료로 보존했다. 최종 양쪽은186passed·권한1314에 따른 기존 symlink1skip·실제exit0이며 실패/오류/미실행은 없다. 각875Python과 실행 tree의 비캐시 전후 해시를 대조했다. skip은 통과가 아니고 G4조건 판정은 별도로 남긴다.\n\n공식 미러 생성/마지막 캐시 동기화·--check·skill-only와 보존 검사를 완료했다. runtime139입력·144corpus경로/150명시SHA·host8원자료/도구·baseline910·T4경계는 불변이다. 두 문장 변경은 향후 역할 prompt판본에 반영되며 역사 smoke의 승인된 성질만 한정 재사용한다. 상세 소비/반례·B110~B114의 P02한정 처분과 초기 감사 오류는 binding-review.md에 적었다. 전체 G완료, 다른 문서 packet/PR24전체, 새 실호출/최종 관문 실행은 주장하지 않는다.',
 'acceptance':[
  {'id':'A1','result':'pass','detail':'시작2675개SHA의018 manager 전건 일치와 기존Git dirty/HEAD를 확인했다. 세 문서의 네owner·별칭·읽기 조건을 현재 write_source_catalog/_preserve_outputs/_apply/_context/prepare_role_input과 직접 시험에 연결했다. actual B110~B114 diff와 존재하는7원보고 SHA를 대조해 P02 slice만 교체/유지 판정했다. 저장artifact와 복원local_path, 수제fixture와 실제생산을 구별했다.','evidence':refs('start-comparison.json','start.json','git-status.stdout','git-diff.stdout','history-verification.json','binding-review.md')},
  {'id':'A2','result':'pass','detail':'네owner를 실제 writer/파일·_context/포장·_apply 저장 결과로 검사한다. canonical JSON의path/hash/bytes/total, input/details snapshot, 원자료와 각결과파일의 정확workspace/task/execution/artifact를 대조했다. 실제수신의별도지식권위/독립bundle 비중복 및600k보고·파일의개정/재개는 기존시험에 연결했다. runtime/스키마를 바꾸거나 최종반환을 손으로 베껴정상표본으로 쓰지 않았다. 문서의읽기권한/선택모집단·artifact/local_path·읽기실패 의미를 유지했다.','evidence':refs('c/report.json','m/report.json','verification.json','binding-review.md')},
  {'id':'A3','result':'pass','detail':'수리전한method의8owner/별칭반례가 기대AssertionError로red였다. 정상반환후 report/각두파일local_path누락·다른실행의동일바이트경로차용·SHA/size교란·원자료차용·저장execution local_path대체·문서오기/동명다른owner를 반려했다. 실제_context hash반려와read_source hash/size 정확사유를 따로확인했다. 정상빈배열/조건부경계와 populated원소검사를 구별하며 owner별담당method/검사호출·defer오기/누락/다른경계 건너뜀 반려와 P01/B130~B134 기존단언을 유지했다.','evidence':refs('red/report.json','red.stderr','corrected/report.json','c/report.json','m/report.json','binding-review.md')},
  {'id':'A4','result':'pass','detail':'지정직접·공유관련14선택범위를 최종판본에서 양쪽동일187ID로 완결했다. 각186passed·기존권한조건1skip·exit0이고 전후/현재875Python 및 비캐시판본 일치다. skip은통과로세지않고G4외부조건책임에남긴다. 공식생성15변경계획/허용범위·마지막캐시동기화·--check/skill-only와runtime139/corpus144·150SHA/host8·도구5/baseline910/T4고정경계 보존을 확인했다. 향후prompt판본영향과나머지P/N·L01·G4~G6/G8책임을 명시했다.','evidence':refs('verification.json','mirror-plan.json','mirror-check.stdout','skill-only.stdout','preservation.json','binding-review.md')}
 ],
 'changes':[{'path':p,'detail':change_detail(p)} for p in v['changes']],
 'seams':[],
 'findings':[
  {'id':'F1','kind':'fact','detail':'P02 네owner의 AST/문자열 조립은 실제writer/생산·저장·복원·포장 경계로 교체됐다. 일반defer가각담당의문서검사에연결되고그누락/오기·다른owner동시건너뜀을거부한다. B110~114중이P02 slice만교체/유지판정했으며review_sources/P03/TRUST/PR24전체는남는다.','evidence':refs('binding-review.md','verification.json','history-verification.json'),'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G3','run:plan.md'],'next_action':'manager가원결과/소스/반례를검수해P02의지정남김만종결하고다른packet·최종판본관문을유지한다.'},
  {'id':'F2','kind':'fact','detail':'정본/미러동일187ID중각186passed·1skipped·exit0다. skip은기존symlink생성의Windows1314권한조건이며P02지정성질의시험은전부실행됐다. symlink의실제탈출반려를이환경에서새로증명한것은아니고G4전체성공/skip통과로확대할수없다.','evidence':refs('c/report.json','m/report.json','verification.json'),'affects':['run:context.md#G4','run:context.md#G8','run:plan.md'],'next_action':'manager는지정회귀완료와조건부미검사범위를구별하고G4최종전체에서원문계약상권한조건건너뜀의정당성을별도로판정한다. 권한을자의변경하지않는다.'},
  {'id':'F3','kind':'fact','detail':'runtime/실호출139입력·144corpus경로/150명시SHA·host8원자료/5도구SHA·과거910파일/Gitblob·T4고정경계가보존됐다. 문서두문장은향후일반역할prompt판본을바꾸며현재고정smoke입력/녹화는불변이다. 이전승인된실호출성질만한정재사용하며새문서읽기/AI준수의실측으로해석하지않는다.','evidence':refs('preservation.json','verification.json','binding-review.md'),'affects':['run:context.md#C12','run:context.md#G4','run:context.md#G5','run:context.md#G6','run:context.md#G8','run:plan.md'],'next_action':'manager는동일입력/도구의기존승인성질을유지하고문서변경을새최종전체관문·review판본에연결한다. 새유료호출이나T4전체재실행의근거로과장하지않는다.'}
 ],
 'checks':checks
}
(E.parent/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('report status complete;',len(report['changes']),'changes;',len(checks),'recorded checks')
