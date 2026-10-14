import json
import subprocess
from work import REPO, RUN, HERE, PYTHON, save

PREFIX = 'run:phases/027/tasks/doc-policy/evidence/'
def ev(*names):
    return [PREFIX + name for name in names]

verification = json.loads((HERE / 'verification-final.json').read_text(encoding='utf-8'))
descriptions = {
    'references/초기화-운전.md': '기본 검토 방침을 현 config.reviewers/review_rounds로 생성·채택하고 실제 해시를 저장한다고 교정했다. 명시 review_policy 우선과 stale config/probe 절차를 유지했다.',
    '계약/독립-운영.md': 'probe의 model_called=false를 정상 관찰에 한정하고 HOLD/상태 조회 실패의 별도 반환을 설명했다.',
    'scripts/tests/support/doc_code.py': 'initial/organize 지정 출력 문장, 두 부분 JSON 예시와 operator mode를 실제 stage_schema/extension_schema/parser choices에 연결했다. 기존 field/owner/반환/policy helper는 보존했다.',
    'scripts/tests/structure/test_doc_code.py': '단계별 정상/오타/다른 단계 차용, 부분 JSON 오타/일반 평가 필드 차용, 절·펜스 누락, operator mode/선택지 표기 반례의 5개 시험을 추가했다. 기존 33개 시험 본문은 불변이다.',
    'scripts/tests/sim/test_initialization_controls.py': '공개 configure/adopt, 저장, restart에서 독립 기대3/2/17의 기본 정책(부재/다른 객체)과 명시 정책 동시 제공 우선·채택 해시를 확인하는 두 시험/공통 단언을 추가했다.',
    'scripts/tests/sim/test_lifecycle_engine_public.py': '기존 reconnect/resume 시험에 pause 명시→생략→continue_authorized 명시→생략의 4세대 양쪽 정책/source_ref/generation 저장·restart를 추가했다. 기존 단언과 소실/동세대 반려/resume 경계를 유지하고 약2.3초 비용 사유를 docstring에 적었다.',
    'scripts/tests/sim/test_operator_finish_cli.py': '정상 공개 CLI probe와 실제 status 읽기 실패의 무모델/무연구 시작·정확 반환/저장 단언을 추가했다. 기존 공개 HOLD 단언은 불변이다.',
    'scripts/tests/시험-지침.md': '이번 한정 단계/부분 JSON/operator mode 문서 검사의 소유와 누락 반려 책임, 그 밖의 산문·읽기/준수 인증 한계를 명시했다.',
    'scripts/tests/.timings.json': '공식 관련 실행의 비용 캐시. 최종 미러 생성에서 정본 캐시와 동기화했다. 실행 성공 증거가 아닌 부산물이다.'}
changes = []
for path in verification['changes']:
    rel = path.split('/skills/do-math/', 1)[1]
    changes.append({'path': path, 'detail': ('공식 생성기의 대응 미러. ' if path.startswith('.agents/') else '') + descriptions[rel]})

checks = []
labels = [
    ('red-doc', 'pass', '수리 전 실제 문서 정상3/변형7의 기존 command/scoped/unowned 검사 결과가 모두 빈 목록임을 보존했다. 실행 결함이 아니라 문서 검사 공백의 재현이다.'),
    ('green-doc', 'pass', '당시 수리판에서 정상3은 승인하고 변형7을 단계/부분 객체/mode별 사유로 반려했다. 최종 같은 성질의 정확 단언은 c3/m2 공식 row에 있다.'),
    ('focus', 'fail', '43선택 중40passed/3failed. 선택지 synopsis 미처리, JSON 오류 순서 단언, 동일 채택 요청의 영수증 재사용을 기록했다. runtime 결함으로 보지 않는다.'),
    ('corrected', 'pass', '집중 실행의 정확3실패 ID를 수정 후 재실행해3passed로 해소했다. 다른 검사 전체를 반복하지 않았다.'),
    ('final-c', 'fail', '첫 관련134선택은133passed/1failed. reconcile 문자열의 C:/Temp 정규 경로와 TEMP의 C:/temp 표기가 다른1row/3subTest였다. 원trace를 보존했다.'),
    ('final-c2', 'pass', 'TEMP를 Path.resolve의 실제 표기로 지정한 동일제품 재실행134passed. 원실패의 단언은 약화하지 않았다.'),
    ('final-m', 'pass', '같은 중간판본의 미러134passed. 이후 lifecycle 비용 docstring 추가로 최종판본 증거는 m2로 교체했다.'),
    ('final-c3', 'pass', '마지막 비용 docstring까지 포함한 최종 정본134선택/고유row134passed·실제exit0·875Python SHA 및 실행 중 변경0. 저장/CLI 반환84개를 교체 없는 monitoring으로 관측했다.'),
    ('final-m2', 'pass', '최종 미러의 같은134선택/고유row134passed·실제exit0·875Python SHA 및 실행 중 변경0. 저장/CLI 반환84개를 별도 관측했다.'),
    ('mirror-build', 'pass', '공식 생성 전에9예상변경 전부 writes 안·stale0을 확인했다. 실제9변경은 예상과 같다.'),
    ('mirror-costs', 'pass', '중간 관련 실행 후 허용된 .timings.json1경로만 공식 재생성했다. 제품/시험 내용 변경은 없다.'),
    ('mirror-check', 'pass', '중간 미러1336파일 드리프트0. 최종 검사와 구별한다.'),
    ('skill-c', 'pass', '정본 installed_skill_structure=verified. 검사 후의 유일한 비캐시 변경은 설치파일 집합에서 제외하는 tests의 비용 docstring이므로 문서/schema 구조 근거는 유효하다.'),
    ('skill-m', 'pass', '미러 installed_skill_structure=verified. 실제 runtime_execution/document_semantics/Lean/연구 효력까지 인증했다고 쓰지 않는다.'),
    ('verify', 'fail', '보조 검산의 첫 실패는 Git text blob과 작업트리 개행 바이트를 그대로 같다고 가정한 오류다. 원stderr/exit1을 보존했다.'),
    ('verify2', 'fail', '개행 변환 후보만으로 doc_code의 혼합 개행 원바이트를 재구성할 수 없었다. 원stderr/exit1을 보존했다.'),
    ('verify3', 'pass', '025 manager archive의 doc_code 원바이트를 완전 start SHA와 대조하고 나머지 Git 원바이트/개행 후보도 SHA 검증해 중간판본 보존·정확 row/저장/분기를 검산했다.'),
    ('mirror-docstring', 'pass', '소프트 비용 지침에 따른 lifecycle docstring 한 경로만 공식 미러로 생성했다. 그 뒤 c3/m2를 고정 실행했다.'),
    ('mirror-cost-final', 'pass', '최종 c3/m2 후 비용캐시1경로만 공식 생성기로 동기화했다. final source_sha256의875Python은 불변이다.'),
    ('mirror-check-final', 'pass', '최종1336파일 드리프트0·실제exit0·소스변경0.'),
    ('verify-final', 'pass', '최종134전건 대응/875SHA/이전33row/기존 함수·단언 보존과 실제 반환 각84개의 정책/해시/4세대/3probe분기를 검산했다. 범위 밖 변경0.')]
for label, result, detail in labels:
    process = json.loads((HERE / (label + '-process.json')).read_text())
    names = [label + '-process.json', label + '.stdout', label + '.stderr']
    if label.startswith('final-'):
        names.append({'final-c':'c','final-c2':'c2','final-c3':'c3','final-m':'m','final-m2':'m2'}[label] + '/report.json')
    if label == 'focus': names.append('f/report.json')
    if label == 'corrected': names.append('f2/report.json')
    checks.append({'command': subprocess.list2cmdline(process['command']), 'cwd': 'repo:.', 'result': result,
                   'exit_code': process['exit_code'], 'evidence': ev(*names), 'detail': detail})
checks.insert(0, {'command': PYTHON + ' -B docs/do-math/continuous-development-2026-10-13/phases/027/tasks/doc-policy/evidence/work.py start',
                 'cwd': 'repo:.', 'result': 'pass', 'exit_code': 0,
                 'evidence': ev('source-start.json', 'start-verification.json'),
                 'detail': '026 manager와 동일한2675소스 전건SHA 차이0, 저장소 밖 전용TEMP의 Git조회 exit128(상위 저장소 부재)을 확인했다.'})
checks.append({'command': '최종 기본 전체 / fresh T3 / 전수 변이 / 새 유료·OS 예약·설치·Lean·학술 호출',
               'cwd': 'repo:.', 'result': 'not_run', 'exit_code': None,
               'evidence': ev('review.md'), 'detail': '027의 배정 범위 밖이거나 금지된 실행이다. 현재 G4~G8/L01/symlink 미검사 상태를 유지한다.'})

report = {
 'status': 'complete',
 'narrative': '027/doc-policy의 A1~A5를 완료했다. 026 검수판과 시작2675소스가 같음을 확인하고 정책 F2/F3·역할 F1/F2의 정확 범위만 통합했다. 문구 두 곳을 실제 생성·채택/분기 반환에 맞추고, 공개 초기화와 대화 연결의 실제 저장·재시작을 독립 기대로 검사했다. 역할 단계와 두 부분 JSON의 문서 이름은 실제 stage_schema/extension_schema, operator mode는 parser choices를 소비한다. 별도 제품 schema나 전역 어휘/자연어 소유자 추론기를 만들지 않았다.\n\n수리 전 실제 문서 정상3/변형7의 거짓 통과, 집중43건의3실패, 첫 관련134건의1실패와 보조검산의2오류를 그대로 보존했다. 선택지 표기·오류 순서·같은 요청 영수증 재사용을 fixture/검사에서 고쳤고 TEMP 표기를 실제 정규 경로로 지정했다. runtime이나 권한·제출 schema/choices를 바꾸지 않았다. 마지막 비용 docstring을 포함한 최종 정본 c3/미러 m2는 동일134선택·고유row가 전부passed·exit0, 각875Python SHA가 현재와 같고 실행중 변경0이다. 저장/CLI 반환각84개를 기존 monitoring으로 관측해 기본정책3/2/17·해시, 명시우선, 연결4세대의양쪽정책/정확ref와 probe 정상/HOLD/조회오류를 별도 대조했다.\n\n기존33문서시험과 다른P/PURE helper본문은 불변이며 lifecycle의 이전 단언도 전부 보존됐다. 실제 변경18경로는 허용16비캐시 정본/미러와 비용캐시2뿐이다. 공식 --check는1336파일 드리프트0이고 양쪽skill-only가verified다. tests의 마지막 docstring은 설치파일집합에서 제외돼 이전skill-only 문서/schema근거를 무효화하지 않는다. 과거Git원바이트와혼합개행문제는 시작SHA에맞는025archive로 검산했고 원보고를 수정하지 않았다.\n\ncomplete는 이번 지정수리/관련검사의완료다. N01나머지·L01 Q1/Q2와UTF-8 byte요구/미충족·symlink1314 실제반려 미검사·G4전체일반/G5freshT3/G6전수변이/G7최종판연결/G8review는 그대로다. 새 유료/OS예약/설치/Lean/학술 호출이나 연구조작, Gitindex/commit/reset/checkout/push, graphify갱신은 없다. 기존실호출은 runtime불변의 승인된하위성질만 재사용하며 교정된문서의 실제모델독해/준수를 주장하지 않는다.',
 'acceptance': [
  {'id':'A1','result':'pass','detail':'026 시작SHA전건을 먼저 대조했다. 초기화182는현config의기본방침생성·채택/실제해시와명시policy우선을 설명하고 stale/probe는 유지한다. 독립15는정상false marker와HOLD/조회실패별도반환을 구별한다. 공식미러반영 및 실제CLI/probe경계단언이통과했다.', 'evidence':ev('start-verification.json','changes-final.diff','mirror-check-final.stdout','c3/report.json','m2/report.json')},
  {'id':'A2','result':'pass','detail':'InitialAdoptionTests의공개configure/adopt/save/restart에서정책부재와다른유효객체후기본채택의3/2/17·judge3·empty perspectives·unresolved 및 해시를 독립기대로 확인했다. 명시policy+default flag는명시객체우선이다. 재요청은서로다른원문으로분리해같은영수증재사용을새채택처럼세지않았다. 기존stale/hash불일치활성화missing시험은불변이며최종통과했다.', 'evidence':ev('c3/report.json','m2/report.json','c3-returns.jsonl','m2-returns.jsonl','verification-final.json')},
  {'id':'A3','result':'pass','detail':'초기continue_authorized에서generation1명시pause→2생략pause→3명시continue_authorized→4생략continue_authorized를공개conversation경로로검사했다. 매번instance와runtime행정책·generation·request source_ref를각각기대값과save/restart에비교했다. 기존lease시각/동세대반려/명시resume·원문재전달원자성은해당모듈의기존단언보존및최종통과로유지한다.', 'evidence':ev('c3/report.json','m2/report.json','c3-returns.jsonl','m2-returns.jsonl','assertion-preservation-final.json','verification-final.json')},
  {'id':'A4','result':'pass','detail':'동일성initial/organize의명시출력문장과issues원소를정확stage에결속했다. organize decision차용과initial findingz를반려한다. 후보의형제경계원소·assessment_targets확장예시는각부분schema로승인하고independent_of_revision 및task_title차용을required/additionalProperties와정확경로로반려한다. 절/선언/펜스/문서부재는빈성공이아니다. bare/do_math.py/$dmCli operator와선택지표기를실제choices로검사해invent를반려한다. 다른산문의모든backtick을필드로읽지않는다.', 'evidence':ev('document-before.json','document-after.json','c3/report.json','m2/report.json','assertion-preservation-final.json')},
  {'id':'A5','result':'pass','detail':'최종c3/m2동일134선택/고유row134passed·exit0,875Python/전후SHA·이전33row를검산했다. 현재공개HOLD와정상/조회실패probe의새실행을포함한다. 원실패/보조오류와새통과는분리했다. 공식미러1336드리프트0·양쪽skill-onlyverified이며끝2675중허용18변경/범위밖0이다. 최종관문과L01/권한미검사남김은유지한다.', 'evidence':ev('verification-final.json','source-end.json','end-verification.json','mirror-check-final.stdout','skill-c.stdout','skill-m.stdout','c3/report.json','m2/report.json')}
 ],
 'changes': changes, 'seams': [],
 'findings': [
  {'id':'F1','kind':'decision','detail':'026 policy F2/F3와role F1/F2의문구/직접저장/문서검사공백을이번한정수리로종결후보에올린다. runtime실행결함반례는없었고정책/권한개정도없다. 실제정책저장·4세대양쪽정책과문서반례/최종관련통과가근거다. 조사표전체나문서전체의의미인증으로넓히지않는다.', 'evidence':ev('verification-final.json','c3/report.json','m2/report.json','document-before.json','document-after.json'), 'affects':['run:context.md#C10','run:context.md#G1','run:context.md#G2','run:context.md#G3','run:plan.md'], 'next_action':'manager가026의네carryfinding과027A1~A5를정확근거로처분하고N01의나머지이름질문을현재고정판에서한정한다. 현재stage/extension/parser정본을유지한다.'},
  {'id':'F2','kind':'fact','detail':'초기집중3실패는선택지synopsis/단언순서/내용주소요청재사용이었고corrected3 및최종정확ID통과로해소됐다. 첫관련실패의C:/temp와C:/Temp문자열차이는외부TEMP를정규표기로지정한동일제품실행으로해소했다. Git/작업트리원바이트혼동의보조오류2건은start SHA와맞는archive로교정했다. 실패를삭제하거나약한단언·runtimefallback을추가하지않았다.', 'evidence':ev('f/report.json','f2/report.json','c/report.json','final-c.stderr','c3/report.json','verify.stderr','verify2.stderr','assertion-preservation-final.json'), 'affects':['run:context.md#C5','run:context.md#G3','run:plan.md'], 'next_action':'후속실행도전용TEMP의정규실제경로와상위Git부재를확인한다. 원실패는역사자료로보존하고새제품issue나현재실패로전파하지않는다.'},
  {'id':'F3','kind':'fact','detail':'2675소스중18허용변경외에는불변이다. 기존33문서시험과P/PURE helper·runtime·schema/choices·corpus는유지됐다. 교정문서가향후prompt/설치문서hash를바꾸므로기존실호출을새문서독해/준수나전판본성공으로확대하지않는다. L01 Q1/Q2/원문byte미충족·symlink1314미검사·N01나머지·G4~G8최종관문은이번134passed와별도로남는다.', 'evidence':ev('source-start.json','source-end.json','end-verification.json','assertion-preservation-final.json','verification-final.json','review.md'), 'affects':['run:context.md#C9','run:context.md#C10','run:context.md#C12','run:context.md#G4','run:context.md#G5','run:context.md#G6','run:context.md#G7','run:context.md#G8','run:plan.md'], 'next_action':'manager가불변하위경계의한정재사용과남김을보존한다. 최종관문/제품수정없는review및L01외부결정은해당후속책임에서판정한다.'}
 ],
 'checks': checks
}
(HERE.parent / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status':report['status'],'acceptance':len(report['acceptance']), 'changes':len(changes), 'checks':len(checks)},ensure_ascii=False))
