from work import *
v=json.loads((E/'verification.json').read_text())
start=json.loads((E/'start.json').read_text())
final=json.loads((E/'final.json').read_text())
preserve=json.loads((E/'preservation.json').read_text())
assert all(final[p]['sha256']==sha for p,sha in preserve['runtime_sha256'].items())
assert all(final[p]['sha256']==sha for p,sha in preserve['fixed_runtime_and_t4_sha256'].items())
assert all(start[r['path']]==final[r['path']] for r in preserve['corpus'])
original=json.loads((E/'prior-task-preservation.json').read_text())
assert all(digest(REPO/p)['sha256']==sha for p,sha in original['files'].items())
save('delivery-preservation.json',{'runtime139':True,'fixed_boundaries258':True,'corpus144':True,
    'explicit_SHA150_checked_in_preservation':True,'host8_tools5_checked_in_preservation':True,
    'baseline910_checked_in_preservation':True,'prior_task352_unchanged':True,
    'final_source_count':len(final),'changes':v['changes']})
root='run:phases/025/tasks/document-trust/evidence/'
def refs(*names):return [root+n for n in names]
descriptions={
    '초기화-운전.md':'등록 문단에 non-Lake toolchain.project=null을 명시했다. 등록·활성화 권한은 유지했다.',
    '초기화-효율과-정비.md':'지문 불일치의 50개 목록/전체 개수와 성공·재결박·초기 오류의 필드 부재, compact 프로젝트 소스 식별을 해당 문장에 명시했다.',
    'doc_code.py':'P08 세 owner를 실제 반환 경계로 교체했다. 정확 owner별 위임과 분기별 부재를 검사하며, 마지막 제품 소비자가 사라진 producer_nodes/produced/written/consumed AST 추론을 제거했다.',
    'engine_context.py':'현재 문서 순회와 독립 장면 사실을 사용하는 assert_trust_documents를 추가했다. 기존 함수 본문은 불변이다.',
    'test_doc_code.py':'세 owner의 실제 경계 요구·오기/차용/중첩 누락·정확 담당 메서드/owner 위임을 검사한다. 폐기된 AST 장치만의 단언을 제거하고 함께 있던 다른 소유자·현재 입력 단언은 유지했다.',
    'test_trust_environment.py':'실제 기록/판정 파일 소비의 모든 기존 check에 문서 검사를 연결했다. 성공/재결박 부재, 추가55·목록50·전체55, 변경/삭제, 기록 파손/부재 및 비기록 성질과 음성 단언을 보완했다.',
    'test_toolchain_tools.py':'실제 identity 함수가 기록된 DLL 바이트 변경도 정확 경로 오류로 반려하는 축을 보완했다.',
    'test_knowledge_lean_verifier.py':'실 Lean/Job의 non-Lake와 Lake 반환을 현재 문서에 연결했다. 독립 파일 SHA/입력 지문/검색 경로·적재 검사기·실행파일을 비교하고 소유자 중첩 삭제·변조를 반려한다.',
    '.timings.json':'공식 관련 실행에서 갱신한 비용 캐시이며 정본과 미러를 동기화했다.'}
changes=[]
for p in v['changes']:
    detail=descriptions.get(Path(p).name,'기존 실제 문서 순회에 세 trust owner의 명시 위임을 추가했다. 해당 원래 경계/음성 단언은 유지했다.')
    if p.startswith('.agents/') and Path(p).name!='.timings.json':detail='공식 생성기의 대응 미러. '+detail
    changes.append({'path':p,'detail':detail})
acceptance=[
    {'id':'A1','result':'pass','detail':'시작 skills/diff 2675파일이 024 manager source-inspected와 전건 동일했다. HEAD/index와 기존 dirty 원바이트를 보존했다. P08 세 원문과 N01-274/279/281의 현재 제목/문장을 연결했고 실제 반환 없이 세 토큰이 승인되는 red 공식 한 시험의 3 subTest 실패를 보존했다. 원문·독립 파일/명령 입력으로 기대값을 정했다.',
     'evidence':refs('start-comparison.json','git-preservation.json','change-coordinates.json','red/report.json','doc_code-start.py','inputs-read.json')},
    {'id':'A2','result':'pass','detail':'실제 inspect_toolchain/_project_identity를 교체하지 않고 real_ports·portable Lean/Lake·Windows Job으로 non-Lake project=None과 Lake의 manifest/source/search_paths를 확인했다. 동일 입력의 검색 경로 재사용과 manifest 변경 재관측을 기존 독립 호출 계수로 유지했다. 파일 SHA와 독립 input-map digest, Lake 설치 경로 구성으로 기대값을 얻었다. 현재 추적 Git subtree/diff는 실제 producer와 별도 native Git 조회로 대조했고, 미추적 변경/.lake 제외/포트 세계·오류는 기존 current project 장면으로 확인했다. 합성 host/Lean 장면과 설치된 실제 5 Job을 구별한다. 실행파일·DLL·기록된/적재한 검사기·프로젝트 판본 반려와 owner/중첩 삭제·변조를 확인했다. 공유 설치/기록을 수정하지 않았다.',
     'evidence':refs('c2/report.json','m/report.json','c2-actual-returns.json','m-actual-returns.json','actual-git-project.json','lake-search-path-contract.json','reuse-verification.json')},
    {'id':'A3','result':'pass','detail':'check_environment가 실제 trust_inventory 생산 기록과 파일을 읽는 현재 경로를 문서에 연결했다. 성공/재결박에는 changed_files/count가 없고, 지문 불일치는 추가/삭제/변경과55개 변화의 앞50/전체55를 보존한다. 기록 ID/identity 불일치, 파손/부재, usable baseline 오류, 현재 host identity 오류 및 judgment unavailable의 실제 서로 다른 오류를 기존 정확/원인별 단언과 반환 원자료로 유지했다. 재결박 previous/current/recorded_at와 새 결박을 확인하고 검사 자체의 기준 비기록을 확인했다. 등록과 활성화, compile-before-admission 실패, 이전 환경 보존·실제 한 번 rebound 사건·정확 대기 해소는 현재 trust flow/consumer를 사용했다. trust fixture는 실제 기록 생산자이고 host/compiler만 명시 대역이다.',
     'evidence':refs('c2-actual-returns.json','m-actual-returns.json','c2/report.json','m/report.json','changes.diff')},
    {'id':'A4','result':'pass','detail':'지정 N 세 절의 등록/검색 경로·환경 오류/재결박·프로젝트 판본 문장을 해당 실제 소비에 연결했다. 두 문서의 세 문단만 조건을 명확히 했으며 등록/활성화/컴파일/사람의 재기록 권한은 개정하지 않았다. B113 도입 및 B114 후속 hunk, B110~B114 존재 원보고7개 SHA와 PR24 한정 slice를 대조했다. 012/B38·016·018·024의 관련 runtime 다섯 파일은 네 검수 좌표와 바이트가 같다. AST 네 helper는 마지막 제품 소비가 사라진 뒤 제거하고 그 장치만의 시험을 정리했다. 나머지 doc_code 및 engine_context 기존 함수와 P01~P07/P09~P11/PURE의 owner·오류·단일 지급·복원 단언을 유지했다. 정책 다섯 이름 전체·다른 N/L01은 닫지 않았다.',
     'evidence':refs('history-verification.json','helper-preservation.json','change-coordinates.json','reuse-verification.json','changes.diff','binding-review.md')},
    {'id':'A5','result':'pass','detail':'실제 문서 순회6모듈·P08 담당·직접 신뢰 흐름·제안/고정 원자료 보호에서19모듈/클래스를 선정했다. 이전254/460을 누적하지 않고 비소비/판본·설치 소비의 재사용 근거를 적었다. 정본 c2와 미러 m은 동일185선택/고유row가 전부passed·exit0이고 각875 Python 및 문서/비캐시 전후 SHA가 같다. 실제 trust 반환은 각122개(project40/toolchain2/environment80), 설치 Job은 각5개가 보존됐다. cache 동기화·공식 mirror 계획14/생성14/--check1336·skill-only를 완료했고 28변경 전부 writes 안이다. runtime139/고정258/corpus144·SHA150·raw-clean/host8·도구5/baseline910/완료task352를 보존했다. 부가 전체 packaging 반환 JSON 캡처는 bytes로 각24오류이며 성공으로 세지 않는다. P08 반환은 온전하고 현재 기존 review-stage test가 최종 입력 전문1을 직접 단언한다. 전체 설치·모델 문서 독해·symlink1314·L01·최종 전체 관문은 미검사/기존 남김으로 유지한다.',
     'evidence':refs('verification.json','selection-decisions.json','c2-actual-returns.json','m-actual-returns.json','c2-resource-cwd.json','m-resource-cwd.json','mirror-plan.json','mirror-build-process.json','mirror-check-process.json','skill-only-process.json','cache-sync.json','preservation.json','delivery-preservation.json','prior-task-preservation.json')}
]
checks=[]
for name in ('red','focus','c','c2','m','mirror-build','mirror-check','skill-only'):
    process=json.loads((E/(name+'-process.json')).read_text())
    expected_failure=name=='red'
    checks.append({'command':subprocess.list2cmdline(process['argv']),'cwd':'repo:.',
        'result':'pass' if process['exit_code']==0 or expected_failure else 'fail',
        'exit_code':process['exit_code'],'evidence':refs(name+'-process.json',name+'.stdout',name+'.stderr'),
        'detail':('수리 전 세 owner의 실제 값 없는 승인 반례를 실패로 확인했다. 기대 exit1/failed1이며 제품 통과가 아니다.' if expected_failure else
                  '초기 구조 단언의 이전 AST 성공 기대가 남아 error1이다. 실제 경계 요구 단언으로 교정했고 최종 같은 ID가 passed다.' if name=='focus' else
                  'Lake 검색 경로의 독립 기대가 설치 표준 두 경로를 누락해 failed1이었다. 설치 Lake 원문으로 교정했고 원실패는 보존한다.' if name=='c' else
                  '공식 선택/실제 row·exit 및 실행 전후 판본을 대조했다. 부분 실행이며 전체 관문으로 합산하지 않는다.' if name in ('c2','m') else
                  '공식 생성/드리프트/구조 검사 실제 exit0과 원출력을 보존했다. skill-only의 verified는 구조이며 문서 전체 의미나 runtime 실실행 판정은 아니다.')})
checks.extend([
    {'command':f'"{PY}" -B "{E / "audit.py"}"','cwd':'repo:.','result':'pass','exit_code':0,
     'evidence':refs('verification.json','c2-actual-returns.json','m-actual-returns.json'),
     'detail':'동일185선택/고유row/실제 exit, 각875Python, 전후 비캐시 불변, 모든 trust 분기 반환과 실제 설치 Job5개를 검산했다. 부가 packaging 캡처 오류24개씩은 별도 한계로 분리했다. 초기 보조 audit의 과도한 전체-packaging 무오류/합성 Job exit0 가정은 검산 범위를 정확히 구분해 고쳤고 제품/원관찰은 바꾸지 않았다.'},
    {'command':f'"{PY}" -B "{E / "git_identity.py"}"','cwd':'repo:.','result':'pass','exit_code':0,
     'evidence':refs('actual-git-project.json','git-identity-0.stdout','git-identity-1.stdout','git-identity-2.stdout'),
     'detail':'실제 source identity의 현재 tracked tree와 raw diff, untracked count/digest를 독립 native Git/파일 조회로 확인했다. 최초 보조 기대는 canonical_json의 끝 개행을 잘못 포함했으며 json_digest의 개행 없는 정규 JSON 의미로 교정했다. stage/commit은 없다.'},
    {'command':f'"{PY}" -B "{E / "preserve.py"}"','cwd':'repo:.','result':'pass','exit_code':0,
     'evidence':refs('preservation.json','prior-task-preservation.json','delivery-preservation.json'),
     'detail':'실제 바이트·Git raw/clean·명시 SHA와 도구/원자료/910 baseline 및 완료 원task352를 대조했다. 마지막 delivery 검산에서도 고정 입력은 같다.'},
    {'command':f'"{PY}" -B "{E / "diff.py"}"','cwd':'repo:.','result':'pass','exit_code':0,
     'evidence':refs('changes.diff','diff-sources.json','git-preservation.json'),
     'detail':'024 archive 또는 Git raw/CRLF 후보가 정확 start SHA와 일치할 때만 시작 원바이트로 사용해26비캐시 파일의 실제 diff를 얻었다. HEAD/index는 시작과 동일하다.'}
])
findings=[
    {'id':'F1','kind':'fact','detail':'P08/DOC-RETURN-TRUST의 세 실제 반환 및 N01-274/279/281의 지정 문장은 현재 소비·독립 기대·정본/미러185passed로 연결됐다. non-Lake null과 성공/재결박/초기 오류의 changed_files 부재는 정상 조건이며 양성 Lake/지문 불일치 표본도 별도 검사했다. 나머지 N 절이나 13-C 전체의 의미 완료는 아니다.',
     'evidence':refs('change-coordinates.json','verification.json','c2-actual-returns.json','m-actual-returns.json','binding-review.md'),
     'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G3','run:plan.md'],
     'next_action':'manager가 지정 P08/TRUST와 이 세 N 문장만 닫고 정책 다섯 이름/다른 N/L01 및 최종 관문을 유지한다.'},
    {'id':'F2','kind':'decision','detail':'B113의 P08 AST 조립과 B114 후속 사용은 실제 경계로 교체한다. 실제 제품 소비가 전부 사라진 producer_nodes/produced_object_schema/written_object_schema/consumed_object_schema 및 그 장치만의 단언을 제거했다. 다른 소유자·현재 입력·callable/명령/별칭 검사와 모든 기존 engine_context 함수는 유지했다. 존재 원보고7개와 PURE 역사 근거는 과거 counts를 새 성공으로 합산하지 않고 유지한다.',
     'evidence':refs('history-verification.json','helper-preservation.json','changes.diff','verification.json'),
     'affects':['run:context.md#C9','run:context.md#C10','repo:.claude/skills/do-math/scripts/tests/support/doc_code.py'],
     'next_action':'manager가 이 한정 PR24/TRUST 교체·제거 처분을 검수한다. 다른 PR24 slice의 전체 종료로 확대하지 않는다.'},
    {'id':'F3','kind':'fact','detail':'작업 시작은024의2675파일과 같고28변경 모두 writes 안이다. runtime/실호출139·고정258·corpus144/SHA150/Gitraw-clean·host8/tools5·baseline910·원task352·HEAD/index는 보존됐다. 두 문서의 세 문단은 미래 prompt/설치 문서 해시를 바꾼다. 과거 실호출은 불변 하위 경계 성질만 재사용하며 현재 문서 독해/전체 설치 동등성으로 확대하지 않는다. 이번 선택에 symlink 검사가 없어 Windows1314 실제 반려 미검사는 여전히 남고 전체 일반/freshT3/전수변이/G7 최종판/최종review는 수행하지 않았다.',
     'evidence':refs('preservation.json','delivery-preservation.json','prior-task-preservation.json','reuse-verification.json','git-preservation.json','selection-decisions.json'),
     'affects':['run:context.md#C11','run:context.md#C12','run:context.md#G4','run:context.md#G5','run:context.md#G6','run:context.md#G7','run:context.md#G8'],
     'next_action':'manager가 기존 불변 하위 성질의 한정 재사용·문서 영향·미검사를 유지하고 후속 최종 판본 관문/남은 의미 질문을 배정한다.'},
    {'id':'F4','kind':'fact','detail':'증거 전용 sys.monitoring은 각 최종 suite의 실제 trust 반환122개와 실제 설치 Job5개를 보존했다. 추가로 시도한 전체 prepare_role_input 반환은 원시 archive bytes 때문에 각24 JSON 직렬화 오류가 나서 캡처하지 못했다. 오류를 숨기거나 전체 packaging 반환 보존으로 주장하지 않는다. 이 부가 관찰은 P08 담당이 아니며 모든 P08 관찰은 성공했다. 현재 unchanged review-stage test는 모든 자리의 전문1을 직접 단언해185passed에 포함됐고,024의 이전 실제 전문1 raw와 producer/helper 바이트는 보존됐다. 원 observer 오류와 초기 보조 audit 실패는 제품 실패/변경과 구별한다.',
     'evidence':refs('c2-actual-returns.json','m-actual-returns.json','verification.json','helper-preservation.json','prior-task-preservation.json'),
     'affects':['run:context.md#C10','run:context.md#G3','run:context.md#G8'],
     'next_action':'manager가 현재 P08 원자료와 추가 packaging 관찰 한계를 구별해 검수한다. 후속 작업에서 전체 packaging raw가 필요하면 context/manifest와 원시 byte 파일을 따로 보존하며, 이 실패를 현재 전체 packaging 캡처 성공으로 세지 않는다.'}
]
narrative='''P08/DOC-RETURN-TRUST와 N01-274/279/281의 지정 문장을 한 변경으로 완료했다. 시작 skills/diff2675파일은024검수본과 같았다. 실제 입력 없는 AST 승인 반례(red의3subTest)를 먼저 공식 실패로 보존하고, 세 owner를 실제 inspect/project/environment 반환에 연결했다. 제품 runtime·공유 schema·포트·설치/기록·연구는 바꾸지 않았다.

실 Lean/Lake·Windows Job으로 non-Lake null과 전용 Lake 프로젝트를 확인했다. 기대는 자기 프로젝트 파일·독립 입력 digest·현재 설치의 경로 구성에서 얻었고 실제 producer를 대역으로 가리지 않았다. 초기 Lake 기대가 표준 library/source 경로 두 개를 누락한 c의184passed/1failed는 보존하고 설치 원문으로 교정했다. 실제 Git producer도 별도 native 읽기와 대조했다. 합성 host/compiler 시험은 실제 기록 생산자·파일 소비를 유지하며 외부 host 대역이라는 한계를 명시한다. 성공/재결박의 changed_files 부재와 지문 불일치·파일55개/목록50개·기록/identity/판정 오류를 구별했다. 등록·활성화·컴파일·사람의 재기록 권한과 이전 환경 보존·한 번 rebound/정확 대기는 현재 기존 소비 시험으로 확인했다.

B113/B114 실제 P08 hunk·B110~B114 존재 원보고7개·PR24의 한정 질문을 대조했다. 마지막 제품 소비가 사라진 AST 추론 네 helper만 제거하고 다른 helper 함수와 P01~P07/P09~P11/PURE의 보호성질은 유지했다. 문서는 두 파일의 세 문단에서 null/분기별 부재/목록 제한/compact source identity만 명확히 했다. 정책 다섯 이름의 전체 의미, 다른 N/L01과 최종 관문은 닫지 않는다.

최종 정본 c2와 미러 m은 같은185선택/고유row가 전부passed·exit0이며 각875Python 및 문서/비캐시 전후SHA가 같다. 현재 문서 순회와 직접 소비·보호성질로 선택했으며 이전254/460을 누적하지 않았다. 각 실제 trust 반환122개와 설치 Job5개·실제cwd/argv/출력/exit를 보존했다. 부가 전체 packaging 반환 JSON 캡처는 원시 bytes 때문에 각24오류였으며 해당 추가 캡처 성공을 주장하지 않는다. P08 원자료는 모두 보존됐고 전문1은 unchanged 현재 review-stage 직접 단언과024의 보존된 raw로 확인한다. 초기 구조 error1·Lake 기대 failed1·보조 script/audit 오류는 수정 전 사실로 남기며 최종 정확ID의 passed와 구별한다.

공식 미러14변경 계획/생성·비용캐시 동기화·--check1336·skill-only를 완료했고 실제28변경은 허용 범위 안이다. 고정 runtime/입력·말뭉치/원자료/도구·baseline910·완료task352 및HEAD/index를 보존했다. 문서 수정이 미래 prompt/설치 해시에 주는 영향과 과거 실호출의 불변 하위 성질 재사용을 구별한다. 새 유료/예약/학술 호출·기존 연구 재개/삭제·graphify 갱신·Git stage/commit/reset/checkout/push는 수행하지 않았다. symlink1314, L01 Q1/Q2·원문byte와 최종 전체 일반/freshT3/전수변이/G7최종판연결/제품수정없는review는 남는다. 이 complete는 A1~A5의 한정 task 완료다.'''
report={'status':'complete','narrative':narrative,'acceptance':acceptance,'changes':changes,
        'seams':[],'findings':findings,'checks':checks}
(E.parent/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(E/'binding-review.md').write_text('# 025 document-trust의 한정 판단\n\n'+narrative+'\n\n'+
    '\n\n'.join('## '+a['id']+'\n\n'+a['detail'] for a in acceptance)+'\n',encoding='utf-8')
print('Written report complete; A1-A5 pass;',len(changes),'actual changes; final185/185 each')
