"""Prepare only manager-owned shared state and the next assignment."""
from pathlib import Path
import difflib
import hashlib
import json

REPO = Path(__file__).resolve().parents[6]
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


before = {name: (RUN / name).read_text('utf-8') for name in ('context.md', 'plan.md', 'seams.md')}
context = before['context.md']


def replace_once(source, old, new):
    assert source.count(old) == 1, old[:100]
    return source.replace(old, new)


paragraph = '''phase 006 codex-schema는 partial로 검수했다. report 형식 검사 후 시작 2624파일이 phase 005 종료와 같고, 종료 2640파일과 현재 파일의 차이가 0개임을 확인했다. 실제 50변경은 report changes 및 쓰기 범위와 일치한다. 공식 9묶음의 선택/고유 row/exit와 각 판본을 대조했으며 Codex 실호출 1passed와 11개 판정, 원/전송 schema·worker·파일·checkpoint·종료를 원파일에서 확인했다. 정본 corpus 18passed와 미러 14passed는 최종 Python 각 865개와 일치한다. 양쪽 각 18항목·51파일·223685바이트·50개 명시 SHA, 총102경로 raw/clean 동등성을 확인했다. 직접 소비 45건 중 11실패와 저장 pair의 성공 표본 공백 때문에 A3/A5는 미충족이다. A1/A2/A4의 지정 성과만 승인한다. 검수 당시 HEAD는 9c917b644360ebdb0d6fd0e0cc8ef3191f4956b8이며 근거는 run:phases/006/manager-evidence/verification.json과 review.md다. 전체 관문의 성공은 아니다.

'''
context = replace_once(context, '## C3 현재 정본과 이력의 역할', paragraph + '## C3 현재 정본과 이력의 역할')
old = context[context.index('phase 001의 독립 분석 세 task와 phase 002~005의 단일 work task는 종료됐다.'):context.index('\ndo-math 시험 프로세스는')]
new = '''phase 001의 독립 분석 세 task와 phase 002~006의 단일 work task는 종료됐다. phase 006에서 Codex 대표 전달 실패는 해소됐고 직접 소비 fixture·성공 표본 공백이 남았다. phase 007 provider-consumers는 이 도우미와 소비 회귀·미러 인도를 한 task가 맡는다. 제품 runtime은 고정한다. 공유 support helper, 시험 템플릿·비용 캐시, 공식 생성기가 얽혀 있으므로 파일별 병렬 배정으로 나누지 않는다. 이후 제품/시험을 수정하고 검사하는 phase도 같은 독립성 기준으로 판단하며, 고정판의 독립적인 읽기 검토에는 병렬성을 사용한다.
'''
context = replace_once(context, old, new)
context = replace_once(context, '현재는 phase 001 세 task와 phase 002~005 각 한 task의 report를 각각 새 manager가 검사했다.', '현재는 phase 001 세 task와 phase 002~006 각 한 task의 report를 각각 새 manager가 검사했다.')
context = replace_once(context, '이전 partial report 자체는 수정하지 않는다.', 'phase 006은 A1/A2/A4의 한정 성과를 승인한 partial이며 A3/A5를 007에 넘긴다. 이전 partial report 자체는 수정하지 않는다.')
review_history = '''phase 006은 B49/065a323a의 전달·반려·수치·종료 slice를 실제 도입 diff와 현재 소비자에 대조했다. 두 Temp 원보고가 없다는 관찰을 유지하고 역사 161/6 counts를 새 성공으로 합산하지 않는다. 새 related-01의 5실패는 수정한 4개 fixture의 related-02와 오류 단언을 보강한 semantic-final에서 해소됐음을 원 row로 확인했다. pinned 입력·worker 반려·canonical 값 거부·종료 보호를 유지한 이 slice의 판단을 승인한다. 직접 소비 11실패와 pair 공백은 별도 미해결이며 B49의 다른 관찰 가족이나 PR15 전체를 완료로 바꾸지 않는다. 근거는 run:phases/006/tasks/codex-schema/evidence/history-b49.diff, history-review.json, review-notes.md와 run:phases/006/manager-evidence/verification.json이다.

'''
context = replace_once(context, '저장소 원보고 100개의 해시와 그중 39개의 선택·결과를 읽었다는 것은 closure-map의 관찰이다.', review_history + '저장소 원보고 100개의 해시와 그중 39개의 선택·결과를 읽었다는 것은 closure-map의 관찰이다.')
context = replace_once(context, 'Codex 역할 schema 거부는 phase 006의 후속 수리다. 수리 책임과 재사용 조건은 C12에 둔다.', 'Codex 역할 schema 거부는 phase 006의 원 의미를 보존하는 전송/수신 수리와 새 실호출로 해소됐다. 직접 소비 fixture·pair 공백의 007 수리 책임과 실호출 재사용 조건은 C12에 둔다.')
context = replace_once(context, 'phase 003의 현재 T5 선택은', 'phase 003이 추가한 T5 선택은')
context = replace_once(context, '최종 정본 23개 및 미러 4개의 Python 864개 해시가 현재와 일치한다.', '003 검수 시 최종 정본 23개 및 미러 4개의 Python 864개 해시는 당시 종료 판본과 일치했다. 006 이후 판본은 아래의 새 근거를 따른다.')
start = context.index('F1은 확인된 제품 전달 경계 실패다.')
end = context.index('\n\nphase 003 F2', start)
context = context[:start] + '''phase 003 F1은 실제 제품 전달 실패였다. Codex 0.162.1/gpt-6-astra/low는 보통 maintenance schema의 선택 필드 integration_bundles가 required에 없다는 HTTP 400 invalid_json_schema를 반환했다. worker exit 1, parse_complete=true, turn_failed=true, final/파일/checkpoint 부재와 로컬 종료 barrier는 역사 실패 그대로 보존한다. 인증 부재나 timeout 또는 연구 control_binding 실패로 해석하지 않는다. phase 006의 새 전달 표현과 대표 실호출은 아래의 범위에서 이 거부를 해소했다. 원 schema의 선택 필드 부재/null/값과 제약은 그대로다.''' + context[end:]
start = context.index('다음 phase 006 codex-schema는')
context = context[:start] + '''phase 006은 provider_final.output_contract/semantic_output에 Codex 문자열 봉투를 정의했다. ModelRunner는 원 prompt와 output.schema.json을 보존하고 transport.schema.json을 CLI에 전달한다. collector의 source_request·worker hash·native final 일치·종료 검사 뒤 classify_run이 봉투를 엄격히 해석해 canonical 값과 원 schema를 검증한다. 선택 필드 삭제/필수화, null/default 보충, 구형 fallback은 없다. Claude의 직접 JSON 및 control_binding의 중앙 제출 분기는 유지한다. 실제 코드와 의미 회귀를 검수했으며 이 제품 정의를 중복 schema로 다시 만들지 않는다.

006의 Codex 0.162.1/gpt-6-astra/low 새 호출은 1선택/1passed/exit0이며 11개 판정이 전부 참이다. 원/전송 schema·prompt·worker snapshot/hash·native final·파일·checkpoint와 종료의 대응을 확인했다. live 이후 runtime124파일과 smoke helper는 불변이며 이후 Python 변경은 corpus 검사3모듈뿐이다. 실제 모델명·비용·내부 요청 수는 미보고다. 새 성공 녹화는 codex-maintenance-transport-20261014이며 기존17항목과 실패 verdict는 유지한다. 현재 각 corpus는18항목·51파일·223685바이트·50명시SHA이고 manager도 전102경로 raw/clean을 검산했다. 정본18개·미러14개 corpus 회귀와 --check1305파일/skill-only 성공은 이 범위에서 승인한다. 근거는 run:phases/006/manager-evidence/verification.json 및 git-clean-observation.json이다.

006 F2/F3와 A3/A5는 phase007 provider-consumers로 넘긴다. consumers45건 중11실패는9개 probe,1개 repair,1개 native storage fixture에 남았다. 통과한 contracts.pairs도 source_request 없는 합성 표본 때문에 Codex/Claude 비결박 성공 둘을 output_validation 실패로만 검사한다. 단일 chunk의 구 final과 cross_installation의 전송 schema 최상위 가정은 정적 확인이며 추가 실제 실패 수로 세지 않는다. 후속 task는 외부 CLI fixture의 원/전송 구분, 실제 성공/결박/실패/정지 표본과 상태 단언, malformed raw의 구체적 collector 반려를 검증한다. 제품 runtime은 고정하고 이 도우미의 직접 소비·미러를 함께 확인한다. 구 fixture를 제품 fallback으로 살리지 않는다. 정확한 범위는 run:phases/007/phase.json과 tasks/provider-consumers/objective.md다.

006 F4의 Claude 재사용은 한정 승인한다. 원 smoke를 현 parser/collector/분류기로 재수신한 completed·정확 output, 같은 prompt/schema·worker/tool12모듈 및 경로·버전/help 근거를 확인했다. 당시 CLI 바이너리 SHA는 미기록이므로 실행 파일 바이트 동등성을 주장하지 않는다. 새 Claude/background 호출은 없다. 기존 background의 승인된 성질과 역사 passed=false도 그대로다. 이후 입력/실행 경로/도구 조건이 바뀌면 영향을 받는 실호출을 별도로 판단한다. 이번 Codex 성공은 유지된 실행 경로에 한해 후속 시험 수정 뒤에도 재사용할 수 있다. 근거는 run:phases/006/tasks/codex-schema/evidence/claude-reuse.json과 manager 검수다.

직접 소비 회귀가 남아 공급자 제품 후보는 작업트리에 유지한다. 이번 관리 기록·원보고/필요 원자료·007 배정과 기억은 관리 커밋으로 보존하고, 이번50변경의 원바이트는 run:phases/006/manager-evidence/pending-products.zip 및 product-snapshot.json에 보관한다. 이전004의68파일·005의두속성 archive도 유효한 당시 증거다. archive는 승인된 제품 판본이나 자동 복원 지시가 아니다. 007의 관련 회귀·검수 후 공급자 단위 제품 커밋을 판단하고 corpus staged blob을 원바이트와 대조한다. 다른 G1~G8 의무, 문서/의미 질문, Job/pythonw·Lean/Mathlib·예약·학술·L01 및 최종 관문은 유지한다.
'''

plan = before['plan.md']
plan = replace_once(plan, '## phase 001~005의 결과와 현재 상태', '## phase 001~006의 결과와 현재 상태')
plan = replace_once(plan, 'Codex schema 실패는 계속 남으며 phase 006으로 배정한다.', 'phase 006은 원 의미를 보존하는 Codex 전송/수신 수리와 대표 실호출에 성공했다. 직접 소비11실패와 pair의 성공 표본 공백 때문에 partial이며 phase007에서 fixture와 분기 단언을 수리한다.')
plan = replace_once(plan, 'F1 Codex 거부는 미해결이고 F2의 후속 현재 상태는 다음 항목에 있다.', 'F1 Codex 거부의 새 해소는006 결과에 있고 F2의 미러 후속 상태는 다음 항목에 있다.')
summary = '''- Codex 전달 수리와 소비 시험 남김: run:phases/006/tasks/codex-schema/report.json 및 run:phases/006/manager-evidence/verification.json. 종료2640소스·허용50변경·9묶음의 실제 선택/row/exit·새 Codex1호출과11개판정을 대조했다. 최종 corpus 정본18개/미러14개와 전102경로 Git 바이트는 통과했다. 직접 소비45개 중11실패와 pair의 두 성공 표본 공백은007 책임이다. 정적 추가 관찰인 chunk·cross_installation도 정확한 직접 소비 범위에 넣는다.

'''
plan = replace_once(plan, '분류는 완료율이 아니다.', summary + '분류는 완료율이 아니다.')
start = plan.index('## 다음 phase: 006')
end = plan.index('## 가까운 후속 배정과 선행 관계', start)
plan = plan[:start] + '''## 다음 phase: 007

단일 work task `provider-consumers`가006 F2/F3와 A3/A5의 관련 회귀 남김을 닫는다. 제품 runtime을 고정하고 operator/probe/cross_installation의 외부 CLI fixture, native storage/chunk/raw ingress의 명시 입력, contracts.pairs의 실제 성공·결박·실패·정지 표본과 상태 단언을 수리한다. 원 schema 의미·관찰 바이트·정확한 오류·저장·정산·종료 성질을 유지하며 구 fixture 때문에 제품 계약을 완화하지 않는다. 지정된 직접 소비·제품 경계·미러 검사를 수행하고 원실패와 새 성공을 연결한다. 상세 A1~A5와 쓰기 범위는 run:phases/007/tasks/provider-consumers/objective.md 및 phase.json이다.

Codex 대표 실호출과 corpus 수리는 검수됐으므로 동일 조건의 유료 호출을 반복 배정하지 않는다. runtime·smoke 입력·corpus 불변을 확인해006 Codex와003 Claude의 승인된 성질을 한정 재사용한다. 공유 helper·시험 템플릿/캐시·생성기와 그 직접 소비 때문에 이번 단위는 한 task로 묶고 manager는 제품을 직접 수정하지 않는다. 관련 회귀를 검수한 뒤 공급자 단위의 제품 커밋을 판단한다. 고정판 독립 읽기 review의 병렬성은 유지한다.

''' + plan[end:]
plan = replace_once(plan, '006의 수리·실호출 결과에 따라 Codex 실패의 해소 또는 정확한 후속 조건을 판단한다.', '007의 직접 소비·분기 회귀 결과를 검수해 공급자 단위의 관련 회귀 종료와 제품 커밋을 판단한다.')
old = '| G7 Codex schema 수락·말뭉치 | phase 006이 원 계약 의미를 유지하는 제품 전달/수신 수리·관련 반례 회귀·Codex 새 실호출·녹화를 수행한다. | phase 005의 Git 수리는 검수됐다. 첫 HTTP 400 뒤 추가 제약을 실제 근거로 확인하고 기존 Codex 실패·Claude 성공/background의 한정 재사용을 보존한다. |'
new = '| G1/G2/G3 공급자 직접 소비 회귀 | phase007이11실패와 성공 표본 공백을 현 외부 fixture·실제 분기 단언으로 해소하고 직접 소비/미러 검사를 완료한다. | 006의Codex 대표실호출·녹화와005의Git 수리는 검수됐다. runtime이 고정된 동안 그 성질을 재사용하고 역사 실패·Claude/background의 한정 재사용을 보존한다. |'
plan = replace_once(plan, old, new)

seams = '''# 현재 경계 계약의 사용

phase001의 독립 분석과 phase002~006의 work는 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring이 정본이다. 공급자 호출의 의미는 contracts.action_schema·ModelRunner.run·model_call.classify_run·real_ports·adapter/parser가 정의한다. 현재 결과와 남김은 context C11/C12에 있다.

phase006이 구현한 Codex 비결박 전송의 정본은 do_math/provider_final.py의 output_contract·semantic_output이다. ModelRunner가 원 schema를 output.schema.json에 보존하고 전송 schema를 transport.schema.json으로 넘긴다. source_request·worker snapshot/hash·native final과 종료는 기존 수집 경계를 거쳐야 한다. classify_run은 전송을 해석한 의미 값을 canonical 검사와 원 schema로 검증한다. 선택 필드 부재/null/값과 원 제약은 유지한다. Claude는 직접 JSON을, control_binding은 별도 중앙 제출 계약을 유지한다. 코드 정의를 자연어의 별도 schema로 복제하지 않는다.

phase007은 제품 runtime을 고정하고 같은 경계를 소비하는 시험 fixture와 실제 분기 검증을 한 task가 수리한다. 원 schema와 CLI 전송 schema를 구별하고, pair가 저장 가능한 실패만 검사하면서 성공 표본을 잃는 문제를 닫는다. 외부 CLI/Job 대역은 현 계약을 따르며 실제 runner·collector·수신/저장기를 가리지 않는다. provides/uses는 빈 목록이고 독립 task 간 새 인터페이스를 배정하지 않으므로 S 항목을 추가하지 않는다. 이번 공통 설명 갱신은 이미 구현된 정본과 후속 검증 책임의 반영이며 제품 계약 개정이 아니다.

corpus 생성의 정본은 `.agents/diff/_rules.json`, `writing-skills/scripts/build_skill_mirrors.py`의 transform/build_target과 `writing-skills/references/멀티런타임_동기화.md`다. phase004의 verbatim과005의 하위 manifest -text를 유지한다.007은 새 녹화를 만들지 않고 기존 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 및 미러 생성 일치를 확인한다.

제품 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. report 형식은 서비스 protocol.md가 직접 규정한다. 후속 phase에서 외부 제공자/소비자를 분리 배정하려면 manager가 먼저 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 공유 검사와 실제 연결 책임을 해당 S 항목에 정한다. 같은 인터페이스는 같은 S ID를 유지하며 제품 내부 선택을 불필요한 seam으로 승격하지 않는다.
'''

after = {'context.md': context, 'plan.md': plan, 'seams.md': seams}
diffs = []
for name, content in after.items():
    diffs.extend(difflib.unified_diff(before[name].splitlines(keepends=True), content.splitlines(keepends=True),
                                    fromfile='before/' + name, tofile='after/' + name))
    (RUN / name).write_text(content, encoding='utf-8')
(OUT / 'common-docs.diff').write_text(''.join(diffs), encoding='utf-8')
unchanged = ['C1', 'C3', 'C4', 'C6', 'C7', 'C10']
def section(text, item):
    marker = '\n## ' + item + ' '
    begin = text.index(marker)
    end = text.find('\n## ', begin + len(marker))
    return text[begin:end if end >= 0 else len(text)]
assert all(section(before['context.md'], c) == section(context, c) for c in unchanged)
save(OUT / 'common-docs-review.json', {
    'before_sha256': {n: hashlib.sha256(v.encode()).hexdigest() for n, v in before.items()},
    'after_sha256': {n: hashlib.sha256(v.encode()).hexdigest() for n, v in after.items()},
    'unchanged_context_sections': unchanged, 'unchanged_goals': list(range(1, 9)),
    'amended': {'C2': '006의부분성과·실제원자료대조 추가', 'C5': '007의공유fixture/검사환경을단일task로배정',
                'C8': '006 partial검수와007책임 반영', 'C9': 'B49지정slice의검토범위와원보고부재 보존',
                'C11': 'Codex거부해소와남은직접소비책임 구별',
                'C12': '새전송/실호출/말뭉치·F2/F3미해결·재사용과관리보존 조건'},
    'plan': '완료된Codex대표호출을결과로옮기고007회귀수리를배정; 다른문서/의미/실경계/최종관문 유지',
    'seams': 'S항목의추가/개정없음; 구현된제품정본과007의시험소비책임을공통설명에반영'})

tests = [
    'support/operator_finish_scene.py', 'support/operator_probe_inputs.py', 'support/cross_installation.py',
    'support/provider_runs.py', 'support/model.py', 'support/provider_inputs.py',
    'contracts/pairs.py', 'contracts/test_pairs.py', 'sim/test_operator_probe_contract.py',
    'sim/test_operator_finish_recovery.py', 'sim/test_operator_finish_provider.py',
    'sim/test_operator_finish_cli.py', 'sim/test_operator_finish_children.py',
    'sim/test_operator_finish_supervision.py', 'sim/test_operator_supervision_contract.py',
    'sim/test_observation_delivery.py', 'sim/test_provider_schema.py',
    'flows/test_provider_native_storage.py', 'flows/test_provider_raw_ingress.py',
    'flows/test_operator_recovery_contract.py', 'flows/test_scheduling_close_repair_exit.py',
    'flows/test_scheduling_close_remaining_exits.py', 'flows/test_cross_required_events.py', '.timings.json']
writes = [f'{tree}/skills/do-math/scripts/tests/{p}' for tree in ('.claude', '.agents') for p in tests]
inputs = [
    'run:sources/user-decisions.md', 'run:phases/006/tasks/codex-schema/report.json',
    'run:phases/006/tasks/codex-schema/evidence/review-notes.md',
    'run:phases/006/tasks/codex-schema/evidence/source-final.json',
    'run:phases/006/tasks/codex-schema/evidence/consumers/report.json',
    'run:phases/006/tasks/codex-schema/evidence/pair-observation.json',
    'run:phases/006/tasks/codex-schema/evidence/claude-reuse.json',
    'run:phases/006/manager-evidence/verification.json', 'run:phases/006/manager-evidence/review.md',
    'repo:.claude/skills/do-math/AGENTS.md', 'repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
    'repo:.claude/skills/do-math/scripts/이음새-정본.md',
    'repo:.claude/skills/do-math/references/CLI-실행-계약.md']
inputs += ['repo:.claude/skills/do-math/scripts/do_math/' + p for p in
           ('provider_final.py', 'model_runner.py', 'model_call.py', 'codex_adapter.py', 'claude_adapter.py')]
inputs += ['repo:.claude/skills/do-math/scripts/tests/' + p for p in
           ('support/operator_finish_scene.py', 'support/operator_probe_inputs.py', 'support/cross_installation.py',
            'support/cross_research_machine.py', 'support/provider_runs.py', 'contracts/pairs.py', 'contracts/test_pairs.py',
            'sim/test_observation_delivery.py', 'flows/test_provider_native_storage.py',
            'flows/test_provider_raw_ingress.py', 'flows/test_cross_required_events.py')]
save(RUN / 'phases/007/phase.json', {'kind': 'work',
     'purpose': '006의직접소비11실패와성공pair공백을현재외부fixture·실제분기단언으로수리하고제품불변조건의관련회귀/미러인도를완료한다.',
     'tasks': [{'id': 'provider-consumers', 'inputs': inputs, 'writes': writes, 'provides': [], 'uses': []}]})
for sub in ('phases/007/logs', 'phases/007/tasks/provider-consumers/evidence'):
    d = RUN / sub
    d.mkdir(parents=True, exist_ok=True)
    (d / '.gitkeep').touch()
print('Prepared phase 007 and shared documents; C1/G1-G8 preserved.')
