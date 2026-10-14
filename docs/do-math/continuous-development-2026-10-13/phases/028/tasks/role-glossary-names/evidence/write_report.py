from analyze import RUN, OUT, read, save

E='run:phases/028/tasks/role-glossary-names/evidence/'
PY='C:/Users/wogud/AppData/Local/Programs/Python/Python312/python.exe'
BASE='docs/do-math/continuous-development-2026-10-13/phases/028/tasks/role-glossary-names/evidence/'
def check(script,result,code,files,detail):
    return {'command':PY+' -B '+BASE+script,'cwd':'repo:.','result':result,'exit_code':code,'evidence':[E+f for f in files],'detail':detail}

report={
 'status':'complete',
 'narrative':'028 role-glossary-names의 A1~A4를 완료했다. 고정판의 용어집162절과 CLI33절, 총195절을 현재 제목·행·SHA에 연결했고 634회 원 인라인 출현과 코드펜스/산문/명령 synopsis의 비인라인 주장을 분리 판정했다. 절별 결론은 유지187·기존 근거 재사용2·문구 수정1·검사 보강5다. 보편 개념 K/F/U·상태와 실제 저장/역할 입력, 주 JSON·단계별 출력·보조 파일·제출/복구·대기/판정의 소유를 구별했다. 조사표는 새 제품 정본이 아니다.\n\n실제 action_schema는 knowledge.kind를 TEXT로 만들고 수신 검사는 활성 또는 같은 묶음의 제안을 대조하므로, CLI748의 active enum 설명을 문구 수정 F1로 반환했다. F2는 CLI 네 검토 단계와 checkpoint 예제의 좁은 검출 보강이다. 메모리 변형 다섯 개에서 적용 가능한 doc_code 진단이 정상과 같이 빈 결과인 반면 실제 schema 경로/enum 또는 checkpoint_value는 잘못된 이름·값을 허용하지 않음을 관찰했다. 새 공식 suite/실제 소비 시험을 실행한 주장은 아니다. test-bindings.json은 현재8그룹의 구체 단언·SHA·유효 exact row를 연결한다.\n\n027 c3의 정확38문서 passed row와875Python SHA가 현재에 일치한다. N01-237/260의024 지정6이름행/3문단은 현재 원문을 대조해 그 성질만 재사용했다. 027의 역할 계약 helper가 다른 CLI 문장까지 검사한 것으로 확대하지 않는다. 초기사용의 checkpoint str/bytes 오류와 변경된024 structure SHA를 현재에 재사용하려던 보조 검산 실패를 보존하고 관찰/검산 도구만 교정했다.\n\n시작·끝의 소스2675개와 실제 파일 집합은027 검수판과 같고 제품 변경0이다. 자기 evidence/report만 썼으며 이전 보고·공용 문서·미러·캐시·engine·graphify를 바꾸지 않았다. 두 수리 후보는 같은 helper/structure 시험·공식 미러/관련 회귀를 쓰는 다음 통합 work에 넘긴다. L01 Q1/Q2와원문UTF-8 byte미충족·symlink1314실제반려미검사·G4기본전체/G5freshT3/G6전수변이/G7최종판연결/G8최종review는 남는다. 상세 판정과 한계는 review.md와 원 관찰 JSON에 있다.',
 'acceptance':[
   {'id':'A1','result':'pass','detail':'배정195절의 ID집합/현재 제목·행·문서 SHA를 전건 대조했다. 용어집162/CLI33, 누락0·중복0이며 원634회 인라인 좌표를 원문과 재검산했다. JSON fence의 키와 timeline synopsis, 산문 입력/출력 경로도 별도로 읽었다. 시작2675소스는027 source-inspected와 전건 같다.','evidence':[E+'slice-map.json',E+'source-comparison.json',E+'non-inline-claims.json',E+'verification.json']},
   {'id':'A2','result':'pass','detail':'각 출현을 역할/단계/생산·소비의 소유 프로필 또는 구체적 개념·파일·음성 예시 이유에 연결했다. 실제 schema82경로를 관찰했고 동일성 root/item decision, 일반/고정질문 조사, disposition, checkpoint 문자열/파일을 분리했다.024 지정 문장은 정확 현재 원문만 재사용했다. CLI kind의 실제 불일치는 F1로 구체적 기대/실제와 후속을 반환했다. 알 수 없는 이름을 전역 존재로 승인하지 않았다.','evidence':[E+'section-decisions.json',E+'owner-profiles.json',E+'source-profiles.json',E+'schema-observations.json',E+'exact-reuse.json',E+'repair-candidates.json']},
   {'id':'A3','result':'pass','detail':'현재 doc_code와 실제 schema/parser/소비 시험의8그룹 단언을 본문/SHA로 확인했다.027 정확38문서 rows/875Python 현재 일치를 재사용했다. CLI 네 단계 오타/타단계차용 및 checkpoint 오타 다섯 반례를 순수 helper로 관찰하고 실제 정의와 대조했다. 이는 적용 가능한 helper 범위의 검출 공백이며 공식 suite의 새 실행/전체 green 주장과 다르다. 기존 runtime 단언의 범위와 새 문서 보강의 최소 완료조건을 명시했다.','evidence':[E+'test-bindings.json',E+'reused-rows.json',E+'schema-observations.json',E+'observe.stdout',E+'repair-candidates.json']},
   {'id':'A4','result':'pass','detail':'195절 모두에 유지/재사용/문구수정/검사보강의 근거 있는 결론을 남겼다. 정확 미결/무주체 항목은 없고 F1/F2의 파일·성질·완료조건을 같은 통합 work로 인도한다. 시작·끝2675소스의 내용과 실제 파일 집합, 정의/입력 원보고 SHA·출현 집합의 불변을 검산했다. 제품 writes는0이며 자기 report의 형식 검사를 별도로 수행한다.','evidence':[E+'decision-table.md',E+'repair-candidates.json',E+'source-start.json',E+'source-end.json',E+'input-profiles.json',E+'verification.json',E+'review.md']}
 ],
 'changes':[], 'seams':[],
 'findings':[
   {'id':'F1','kind':'issue','detail':'N01-243/CLI748은 knowledge.kind enum을 active 정의에서 동적으로 만든다고 설명하지만 현재 contracts.action_schema는 연구 생산자 kind를 TEXT로 바꾸고 submission._payload_issues는 활성 또는 같은 묶음의 제안인지 검사한다. CoreEngineMixin._response_schema/_governance_schema도 kind enum을 추가하지 않는다. 실제 정의/순수 관찰 및 기존 same-bundle 제안 소비 단언과 문구가 다르다.','evidence':[E+'schema-observations.json',E+'repair-candidates.json',E+'test-bindings.json'],
    'affects':['repo:.claude/skills/do-math/references/CLI-실행-계약.md','run:context.md#C10','run:context.md#G1','run:context.md#G3','run:plan.md'],
    'next_action':'repair-candidates F1의 한 문장을 실제 schema와 수신 의미 검사 역할에 맞춰 고친다. 신규 제안의 독립 의미/활성화 경계와 미등록 반려는 유지하며 runtime을 enum으로 제한하지 않는다. F2와 같은 후속 통합 work에서 좁은 문서 단언·미러·공식 관련 회귀를 수행한다.'},
   {'id':'F2','kind':'issue','detail':'N01-250~253의 명시 단계 산출과 N01-256 checkpoint 예제는 현재 올바르지만 다섯 최소 변형이 기존 적용 가능한 doc_code helper를 빠져나간다. findings/findingz, organize root decision 차용, answers/answerz, judge item enum에 match 차용, checkpoint current_claim/current_cliam이 그 사례다. 현재 schema의 정확 owner와 checkpoint_value는 잘못된 이름/값을 허용하지 않는다.027 helper는 다른 역할 계약 좌표만 읽으며 이 CLI 예제를 자동으로 보장하지 않는다.','evidence':[E+'schema-observations.json',E+'test-bindings.json',E+'repair-candidates.json'],
    'affects':['repo:.claude/skills/do-math/scripts/tests/support/doc_code.py','repo:.claude/skills/do-math/scripts/tests/structure/test_doc_code.py','run:context.md#C10','run:context.md#G1','run:context.md#G3','run:plan.md'],
    'next_action':'정확 CLI 절·문장·원소를 실제 stage_schema에, checkpoint JSON fence를 CHECKPOINT_SCHEMA/checkpoint_value에 한정 결속한다. 정상 및 다섯 반례와 절/선언/fence 부재를 검사하고 기존027/P/PURE를 보존한다. F1과 같은 통합 work로 미러/공식 관련 회귀를 확인하며 전역 단어·자연어 소유 추론기로 넓히지 않는다.'},
   {'id':'F3','kind':'fact','detail':'195절의 유한 판정과 소스2675파일 불변을 확인했다.027 c3의38문서 passed rows/875Python SHA와024 지정6이름행·3문단만 근거 범위에 맞춰 재사용했다. 새 공식 시험·실제 소비/모델/OS/Lean/학술 실행은 없다. 용어집의 보편 historical과 현 formal_use.withdrawn은 도입의 비동의어 경계로 구분하며 새 runtime 불일치 수리를 요구하지 않는다.','evidence':[E+'verification.json',E+'reused-rows.json',E+'exact-reuse.json',E+'review.md'],
    'affects':['run:context.md#C10','run:context.md#G4','run:context.md#G5','run:context.md#G6','run:context.md#G7','run:context.md#G8','run:plan.md'],
    'next_action':'manager가 배정절의 유지/재사용 부분과 F1/F2를 분리해 검수한다. 이 task 완료를 제품 합격으로 확대하지 않고 L01 외부결정/byte미충족·symlink1314·최종관문을 보존한다.'}
 ],
 'checks':[
   check('analyze.py','pass',0,['source-comparison.json','input-profiles.json','slice-map.json','reused-rows.json'],'2675 시작SHA/195절 좌표·634출현,027 exact38row와875Python 현재 SHA를 확인했다. 현재 제품 import/실행 없는 표준라이브러리 분석이다.'),
   check('observe.py','fail',1,['observe-initial.stderr','observe-initial.stdout'],'첫 순수 관찰에서 checkpoint_value에 str을 전달해 AttributeError였다. 실제 API를 읽어 bytes와 ValidationError 처리를 교정했다. 제품 오류나 정상/반례의 성공으로 세지 않는다.'),
   check('observe.py','pass',0,['observe.stdout','observe.stderr','schema-observations.json'],'-B로 실제 schema/doc helper만 호출했다.82개 실제 owner경로,5변형의 helper 동등 빈진단·실제 schema 금지, checkpoint 정상/오타 반려와 kind TEXT를 관찰했다. OS/네트워크/저장/모델/runner는 호출하지 않았다.'),
   check('decide.py','pass',0,['decide.stdout','section-decisions.json','source-profiles.json','exact-reuse.json'],'195절의 소유/개념/음성/파일 판단과54정의파일 SHA·현재 선언을 정리했다. 초기 작업 스크립트의 없는 파일명 추정은 경로 assertion에서 교정됐으며 최종 근거 경로는 전건 실재한다.'),
   check('finish.py','fail',1,['finish-initial.py','finish-initial.stderr'],'024 c2의 structure 시험 SHA도 현재와 같다고 가정한 보조 검산 오류였다.027 수리로 바뀐 시험을 재사용하지 않고 실제 같은 SHA의 exact row만 연결하도록 교정했다.'),
   check('finish.py','pass',0,['finish.stdout','finish.stderr','verification.json','test-bindings.json'],'195ID집합·좌표/634출현/원보고SHA·소유경로/실제2675파일집합과 전후내용을 전건 대조했다. 같은SHA의 과거 exact rows만 재사용했고 소스변경/추가/삭제0이다.'),
   {'command':'공식 제품 시험/미러 생성/기본전체/fresh T3/전수변이/실호출','cwd':'repo:.','result':'not_run','exit_code':None,'evidence':[E+'review.md'],'detail':'writes 없는 고정판 조사 배정이다. 공식 제품 실행과 공유캐시·미러 생성은 수행하지 않았으며 수리/연결/관련 회귀는 후속 통합 work 책임이다.'}
 ]}
(OUT.parent/'report.json').write_text(__import__('json').dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('report.json written')
