"""Write the bounded manager handoff, without modifying product files."""
import difflib
import hashlib
import json
import re
from pathlib import Path

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
BASE = 'run:phases/026/manager-evidence/'
NEXT = 'run:phases/027/tasks/doc-policy/objective.md'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s.rstrip()+'\n',encoding='utf-8')
def save(p,x): write(p,json.dumps(x,ensure_ascii=False,indent=2))

assert not (RUN/'phases/026/manager.json').exists()
before={n:(O/(n+'.before')).read_text(encoding='utf-8-sig') for n in ('context.md','plan.md','seams.md')}
assert all((RUN/n).read_text(encoding='utf-8-sig') == s for n,s in before.items())

write(O/'review.md', '''# phase 026 manager 검수

세 task의 A1~A4 조사 완료를 승인한다. 각각 report 형식 검사에 통과했다. 다음 work는 027/doc-policy 한 개다. 제품을 고치지 않은 조사 phase이므로 최종 review나 개발 완료로 처리하지 않는다.

## 근거 대조

025 검수본과 세 task의 시작/끝, 현재 정본·미러·diff 2,675파일이 전건 같다. 원 task 84파일의 SHA를 검수 전후 대조했다. policy의 63 원문 구간 및 reference/role 정의의 235개 출처 레코드, N02의 현재 occurrence와 N03의 이름별 행을 현재 원문에 대조했다. 원 packet과 현재 판정의 N02 58절/N03 144절 ID가 같다. 이 기계적 대응을 의미 검토로 대체하지 않았다.

기존 정책 실행 31행과 이름 task가 재사용한 정확 행들을 실제 report.reports[].rows·selected·SHA에서 회수했다. 025 문서 검사 33passed와 현재 Python 875개 SHA가 일치한다. B129 unsuccessful와 이후 코드 변화, 현재 HOLD 시험의 과거판 차이를 유지한다. 이번에 제품 시험을 새로 실행한 것은 아니다. manager 검산의 첫 두 exit1은 코드펜스를 한 행으로 대조한 오류와 공식 row를 최상위 tests에서 찾은 오류였다. 검산기를 실제 다중행 범위와 reports[].rows에 맞춘 뒤 통과했다. 원 task 자료와 제품에는 변경이 없었다.

## 발견의 판단

정책 F1의 세 이름은 해당 원문 문장의 한정 의미를 종결한다. conversation_loss_policy의 연결 의존 해제와 사용자 정지/HOLD/허가는 별도이며 model_policy의 기본값 모듈과 잠금 실패 분류도 구별한다. external_policy는 실제 효과별 허가를 대체하지 않는다. 후속 최종 실행과 전체 정책 검증을 완료로 올리지 않는다.

정책 F2는 초기화-운전182의 '이미 채택한' 표현과 initialization_engine100~106의 실제 생성·저장 분기가 다르다. 현재 설정의 reviewers/review_rounds로 기본 방침을 생성·채택하고 실제 내용 해시를 결박한다는 문구로 고친다. 명시 review_policy 우선은 유지한다. InitialAdoptionTests 본문은 기본값 생성의 독립 기대를 직접 확인하지 않으므로 reviewers3/rounds2의 3/2/17 및 저장해시를 보강한다. 정책 F3도 lifecycle_engine481~495의 양쪽 저장을 현재 단언이 각각 독립 확인하지 않는 범위만 보강한다. 실행 제품 결함으로 선언하지 않는다.

역할 F1은 독립-운영15의 model_called=false를 정상 관찰에 한정한다. scheduled_operator.check235~245는 HOLD에서 outcome=held만, 상태 조회 오류에서는 오류 객체를 반환한다. 정상 observed와 설치 진단 관찰은 false marker가 있다. 모든 분기에 marker를 추가하는 runtime 수리는 필요 없다.

역할 F2의 세 검출 공백은 doc_code의 FIELD.fullmatch, code_examples/command_issues 및 실제 cli_contract의 mode choices와 대조했다. 단독 주 산출 이름은 단계별 schema, 두 JSON 예시는 실제 extension_schema의 부분 객체, operator mode는 parser choices에 한정해 연결한다. 현재 문서의 허용 예시는 유지한다. 문서 전체 자연어 해석기나 조사 판정표의 제품 복제는 허용하지 않는다. 후속은 먼저 최소 변형의 실제 기존 거짓 통과를 기록하고 기존 검사를 확장한다.

N02 7문서의 이름·조합 유지 판정과 N03의 위 두 finding 외 유지 부분을 승인한다. 동명 check/payload/decision, 저장/역할 입력과 역할·단계를 구별한 조사다. scholarly의 describe_source/not_implemented/restricted는 현재 서버 정본의 이름으로 종결하되 list_sources 실측을 search/fetch/이미지 판독 성공으로 확대하지 않는다. 이 비확대 원칙은 새 G7 의무를 추가한다는 뜻이 아니며 기존 원문 완료 기준을 따른다. PR24/B57/B110~B114는 조사한 owner·문법·현 소비 부분만 유지한다. B57/B64의 부재 Temp 원보고와 역사 counts의 한계는 그대로다.

## 배정과 보존

027은 문구 두 곳, 초기화/연결 정책의 직접 단언, 역할 단계·부분 JSON·operator mode 문서 검사만 통합한다. 공유 doc_code/structure 시험·미러·캐시와 같은 최종 관련 실행을 한 담당자가 소유한다. N01의 나머지 이름 조사는 같은 helper/문서 판본을 바꾸는 이 work와 병행하지 않는다. 026 결과를 다시 전수 조사하지 않으며 통합 수리 후 N01 남김을 현재 판본에서 한정한다.

이번 관리 마감은 공용 인계·027 배정·026의 원 task 84파일과 검수 근거·기억 노드만 포함한다. 제품 변경은 0이며 기존 dirty/untracked 제품·운영자 변경을 stage하지 않는다. 원 task 자료는 직접 Git 추적하며 새 중복 archive는 만들지 않는다. 진행 로그와 stage/commit 행정 수신은 로컬 보관으로 정리 시 사라질 수 있다. N01 나머지·L01 Q1/Q2 및 원문 byte 미충족·symlink1314·G4~G8은 유지한다.
''')

objective='''## 목적과 역할

026의 고정판 조사에서 확인된 네 finding(policy F2/F3, role F1/F2)을 한 변경으로 통합한다. 문구 두 곳과 정책의 직접 저장 단언, 현재 문서에 있는 역할 단계·부분 JSON·operator mode의 검사 공백을 닫는다. 공유 doc_code/structure 검사·미러·관련 회귀를 한 번의 최종 판본에서 검증한다. N02 유지 판정과 P01~P11/PURE를 다시 구현하지 않는다.

## 완료 조건

### A1 정확한 문구 두 곳

026 source-inspected와 시작 SHA를 먼저 대조한다. 초기화-운전.md182의 adopt_default_review_policy는 현재 config.reviewers/review_rounds로 기본 방침을 생성·채택하고 실제 내용 해시를 저장한다는 설명으로 교정한다. 명시 review_policy를 함께 주면 그 객체를 사용하는 예외와 stale config/probe 절차는 유지한다. 독립-운영.md15의 operator probe는 정상 관찰의 model_called=false와 HOLD·상태 조회 실패 등 조기 반환을 구별한다. 모델 호출이 없다는 성질을 모든 반환의 필수 marker로 바꾸지 않는다. runtime과 권한은 바꾸지 않고 공식 미러에 반영한다.

### A2 기본 방침의 실제 채택과 저장

sim/test_initialization_controls.py의 기존 InitialAdoptionTests 경로를 이용한다. 현재 설정 reviewers=3/review_rounds=2, 기존 review_policy 부재 및 다른 유효 객체의 두 경우에서 default 채택이 minimum_initial_slots=3, round_limit=2, activity_execution_limit=17, judge_slots=[judge-0, judge-1, judge-2], required_perspectives=[], overflow_disposition=unresolved를 생성하는지 독립 기대값으로 검사한다. 같은 builder를 다시 호출해 기대를 만들지 않는다. 명시 policy 동시 제공의 우선도 실제 경로로 확인한다. 실제 채택/저장과 재시작의 객체·adoption.review_policy_sha256를 대조하고 기존 stale config 반려·정책 hash 불일치 활성화 missing을 유지한다. 직접 내부 helper 호출로 충분한 필드 검사와 공개 control/저장/복원을 구별해 적절한 기존 fixture를 쓴다.

### A3 연결 정책의 양쪽 저장

sim/test_lifecycle_engine_public.py의 실제 공개 conversation 경로에서 instance continue_authorized, 명시 pause attach, 새 generation의 정책 생략, 반대 명시 continue_authorized와 다시 생략을 확인한다. 매 단계 instance.conversation_loss_policy와 runtime.conversations[id].disconnect_policy를 각각 독립 기대와 비교한다. generation/source_ref, 저장 및 restart 후 양쪽 값도 직접 확인한다. 현재 instance 소비가 잘못된 연결행 정책을 가리지 않게 한다. 기존 lease의 전달 시각/정확 만료, 동세대 반려, resume 필요·원문 재전달 원자성을 유지한다. runtime 수리가 필요한 실행 반례가 생기면 범위 밖 변경 대신 finding으로 반환한다.

### A4 문맥을 구별하는 문서 검사

role-contract-names의 repair-candidates.R2에 지정된 세 축만 기존 doc_code.py와 structure/test_doc_code.py에서 보강한다. 현재 실제 문서의 정상 예시와 다음 최소 변형을 수리 전/후에 대조한다.

- 동일성 검토 initial의 decision/findings/scope_complete와 organize의 issues 및 issues[].finding_refs/answer_role_slot_id를 실제 stage_schema에 연결한다. organize 주 산출에 initial/judge의 decision을 차용하는 문장을 반려한다. 정확한 절·역할·단계의 소유를 명시하며 모든 산문 backtick을 필드로 추측하지 않는다.
- 후보-준비156~158의 contract_checks[].sibling_boundaries 원소,220~229의 assessment_targets 보충 평가/보류 예시를 현재 extension_schema의 정확 부분 객체와 연결한다. independent_of_next_revision 오타와 보충 task_id를 일반 task_title로 바꾸는 차용을 각각 반려한다. 전체 주 응답 schema로 부분 예시를 오검사하지 않는다. 문서 삭제/절·펜스 누락이 빈 성공이 되지 않도록 이 한정 대상의 존재도 확인한다.
- operator install/probe 및 do_math.py/$dmCli를 포함한 표기를 실제 parser mode choices로 검사하고 operator invent를 반려한다. 기존 top command·flag 검사를 유지한다.

허용 예시·오타·다른 역할 차용의 정확 실패 사유를 확인한다. 모든 출력에 공통인 전역 어휘 합집합, 자연어 소유자 추론기, 복제 제품 schema나026 조사표 전체를 새 제품 정본으로 만들지 않는다. 기존 source owner/별칭/배열·실제 반환/P01~P11·PURE 검사와 음성 단언은 유지한다.

### A5 최종 관련 검증·미러·근거

변경을 고정하고 정본·공식 생성 미러의 같은 관련 선택을 완결한다. 선택/고유 실제 row/exit와 소스 전후 SHA를 보존하고 fail/error/not_run을 숨기지 않는다. 아래 필수 선택과 변경 영향의 직접 소비를 합쳐 관련 묶음을 정하며, 새 반례/변경 없이 같은 검사를 반복하지 않는다. 현재 HOLD 경계는 새 실행 근거를 얻고 B129의 옛 통과로 대신하지 않는다. 이전 정확33 doc rows 및 기존 P 성질의 단언을 유지한다. 공식 미러 --check 및 skill-only 구조를 확인한다. 원 실패/보조 관찰 오류는 보존하고 새로운 통과와 분리한다. 새 증거의 의미·미검사·L01/최종관문 남김을 report로 인도한다.

## 판단과 경계

하나의 task가 공유 helper/직접 시험·문구·미러·비용 캐시를 소유한다. writes의 문서와 시험 파일만 수정한다. 현재 runtime, 제출/기록 schema, parser choices, 정책·권한 의미, runner, engine 및 graphify는 변경하지 않는다. tests/시험-지침.md는 이번 검사 책임을 실제로 달리 설명해야 할 때만 좁게 갱신한다. 다른 문서의 문구 교정이나 N01 전수 조사는 추가하지 않는다. 제안된 새 단언은 기존 계약의 기대를 검사하며 조사에서 실행 결함이 이미 관측됐다고 쓰지 않는다.

제품 검사는 총 worker3 이하·동시에 한 묶음·기본 jobs1이다. 검사 중 정본과 미러를 고정한다. 새 유료 모델/OS 예약/설치 변경/Lean/학술 호출·기존 연구 조작은 수행하지 않는다. 기존 공개 sim 및 임시 저장 fixture의 정상 부수 효과는 허용한다. 외부 TEMP/TMP/TMPDIR는 저장소 밖의 짧은 자기 전용 경로를 쓰며 상위 C:/math Git을 찾지 않는지 확인한다. resource output도 짧은 evidence/c와 m 등을 쓴다. 공유 캐시·미러 생성·Git index를 다른 작업과 동시에 쓰지 않는다. task는 commit/reset/checkout/push를 하지 않는다.

이전 원 report/evidence·공용 문서를 고치지 않는다.027은 G1/G2/G3 지정 공백의 수리이며 G4 전체 일반/G5 fresh T3/G6 전수 변이/G7 최종판 연결/G8 review를 대신하지 않는다. L01 Q1/Q2·원문 UTF-8 byte 요구/미충족 및 symlink1314를 유지한다. 026이 종결한 이름·정책 문장과 PR의 한정 slice는 새 반례가 없으면 재사용한다.

## 검증 방법

cwd C:/math, Python C:/Users/wogud/AppData/Local/Programs/Python/Python312/python.exe. 시작/끝 전체 SHA와 실제 변경 목록을026 manager source-inspected에 대조한다. 먼저 A4 최소 문서 변형의 현재 거짓 통과와 정상 대조를 자기 evidence에 보존한다. 정책의 새 단언이 처음부터 통과하면 그 사실을 그대로 기록하며 인위적 red를 만들지 않는다. 현 원문·소비·기존 시험 및026의 판정 근거로 수리하고, 최종 공식 선택은 다음을 포함한다.

`python -u -B .claude/skills/do-math/scripts/run_tests.py structure.test_doc_code sim.test_initialization_controls sim.test_lifecycle_engine_public sim.test_operator_finish_cli unit.test_review_cycle_stages unit.test_submission_contract_checks unit.test_submission_contracts --jobs 1 --output <자기 evidence/c>`

미러는 같은 선택을 .agents/skills/do-math/scripts/run_tests.py로 evidence/m에 실행한다. test_operator_finish_cli의 정상 probe/공개 HOLD 단언을 포함하고 필요한 실제 경계가 빠졌으면 같은 파일 안에 최소 검사를 추가한다. syntax/CLI 오타로 미수집이 생기면 성공으로 처리하지 않는다. 실제 저장·재시작 결과를 원파일 또는 반환 JSON으로 남기며 bytes가 있으면 JSON과 원시 파일을 분리한다. 관찰자를 고치려고 원 성공 report를 다시 쓰지 않는다.

공식 생성기의 정본은 .claude/skills/writing-skills/references/멀티런타임_동기화.md다. 생성 전 영향 경로를 확인하고 writes 밖이나 다른 작업의 변경을 덮지 않는다. 기존 mirror drift가 범위 밖이면 정확 차이와 영향만 반환한다. --check와 skill-only의 실제 출력/exit를 보존한다. 최종 report는 A1~A5 전부와 모든 findings를 연결하고 지정 Python으로 services/continuous-development/check.py report C:/math C:/math/docs/do-math/continuous-development-2026-10-13 027 doc-policy 를 통과한다.
'''
write(RUN/'phases/027/tasks/doc-policy/objective.md',objective)
(RUN/'phases/027/tasks/doc-policy/evidence').mkdir(parents=True,exist_ok=True)
(RUN/'phases/027/logs').mkdir(exist_ok=True)

inputs=[
'run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:sources/document-batching-2026-10-14.md',
BASE+'source-inspected.json',BASE+'verification.json',BASE+'review.md',
'run:phases/026/tasks/policy-semantics/report.json','run:phases/026/tasks/policy-semantics/evidence/policy-decisions.json',
'run:phases/026/tasks/policy-semantics/evidence/test-bindings.json','run:phases/026/tasks/policy-semantics/evidence/review.md',
'run:phases/026/tasks/role-contract-names/report.json','run:phases/026/tasks/role-contract-names/evidence/repair-candidates.json',
'run:phases/026/tasks/role-contract-names/evidence/fence-decisions.json','run:phases/026/tasks/role-contract-names/evidence/source-profiles.json',
'run:phases/026/tasks/reference-names/evidence/review.md',
'repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
'repo:.claude/skills/do-math/scripts/이음새-정본.md','repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md',
'repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md']
rels=['references/초기화-운전.md','계약/독립-운영.md','scripts/tests/support/doc_code.py',
      'scripts/tests/structure/test_doc_code.py','scripts/tests/sim/test_initialization_controls.py',
      'scripts/tests/sim/test_lifecycle_engine_public.py','scripts/tests/sim/test_operator_finish_cli.py',
      'scripts/tests/시험-지침.md','scripts/tests/.timings.json','scripts/tests/.timings-t3.json']
inputs += ['repo:.claude/skills/do-math/'+p for p in rels if not p.endswith('.json') and '시험-지침' not in p]
inputs += ['repo:.claude/skills/do-math/'+p for p in ['계약/동일성-검토.md','계약/후보-준비.md',
    'scripts/do_math/initialization_engine.py','scripts/do_math/lifecycle_engine.py','scripts/do_math/review_policy.py',
    'scripts/do_math/scheduled_operator.py','scripts/do_math/cli_contract.py','scripts/do_math/review_cycle.py',
    'scripts/do_math/submission.py']]
for x in inputs:
    prefix,path=x.split(':',1)
    assert ((R if prefix=='repo' else RUN)/path).is_file(),x
save(RUN/'phases/027/phase.json',dict(kind='work',purpose='026의 정책/역할 문구 두 곳과 직접 저장·단계/예제/명령 검사 공백을 한 변경으로 수리하고 관련 회귀·미러를 통합 검증한다.',tasks=[dict(
    id='doc-policy',model='gpt-6.1-sol',effort='high',inputs=inputs,
    writes=[prefix+p for prefix in ('.claude/skills/do-math/','.agents/skills/do-math/') for p in rels],provides=[],uses=[])]))

summary='phase 026 세 고정판 task의 A1~A4 complete를 검수했다. 025·시작·끝·현재 2675소스가 같고 원task84파일이 불변이다. 현재 원문63구간·235출처 레코드, N02 58절/N03 144절 좌표와 과거 정책31row·025 문서33passed/현재875Python SHA를 독립 대조했다. 새 제품 실행은 없다. N02 이름과 N03 유지 부분, 정책 세 이름의 지정 문장을 종결하고 문구 두 곳·정책 저장 단언·역할 단계/JSON/operator mode 검사 공백을027로 넘긴다. 조사 complete는 제품 합격이나 최종G 충족이 아니다. 근거는 run:phases/026/manager-evidence/verification.json·review.md다.'
additions={
'C2':summary,
'C8':'026 세 task의 gpt-6.1-sol/high 수행을 검수했고027 doc-policy에도 같은 model/effort를 명시한다. manager와 제품 공급자 모델 설정은 변경하지 않는다.',
'C9':'026 정책 F4와 이름 task의 역사 재사용을 한정 승인한다. B57의 실제 policy helper 세 함수와 B110~B114의 owner/line-local/배열/실제 반환 위임 부분은 유지한다. B64는 이번 다섯 의미를 변경한 hunk가 없으며 부재 Temp 보고의 counts를 새 성공으로 쓰지 않는다. B129 unsuccessful와 current HOLD/지원 코드 변화는 유지하고 필요한 현재 실행을027에 배정한다. PR24 전체나 G2 전부의 종결은 아니다. 근거는026 manager review.md와 각 task 역사 근거다.',
'C10':'026에서 N02 참조7문서/58절의 이름·조합 유지 판정을 종결하고, N03 역할11문서/144절은 유지 부분을 승인하되 독립-운영15의 분기 문구와 역할 단계·부분 JSON·operator mode 검사 공백은027에 남긴다. 024 F2 중 conversation_loss_policy/model_policy/external_policy의 지정 의미 질문은 닫는다. disconnect_policy 문장은 유지하지만 명시/생략·양쪽 저장/restart 단언, adopt_default_review_policy는 현 설정의 기본 방침 생성·채택 설명과 독립 기대 단언이 필요하다. scholarly describe_source/not_implemented/restricted의 이름 정의는 확인됐고 실제 search/fetch/독해 성공으로 확대하지 않는다. 이러한 미주장은 새 실행 의무를 추가하지 않으며 원래 G7 범위를 따른다.027은 공유 helper·직접 시험·문구/미러를 한 담당자에게 통합한다. N01의 나머지 이름·L01 Q1/Q2·원문byte 미충족과 최종 관문은 유지한다. 근거는026 manager review.md 및027 objective다.',
'C12':'026은 제품·시험·문서·미러 변경이 없어025 판본의 기존 승인 성질과 제한을 유지한다. 이번 관리 커밋은 원task84파일을 직접 추적하고 공용 인계·검수 근거·027 배정·기억을 포함한다. 새 중복 archive는 만들지 않는다. 진행 로그와 stage/commit 행정 수신은 로컬 보관으로 정리 시 사라질 수 있다. 기존 dirty/untracked 제품·운영자 변경은 stage하지 않는다. 정확 추적 범위와 원자료 SHA는 run:phases/026/manager-evidence/preservation.json에 둔다.'}
context=before['context.md']
for cid,paragraph in additions.items():
    pattern=r'(## '+cid+r' [^\n]*\n)(.*?)(?=\n## C\d+ |\Z)'
    context,n=re.subn(pattern,lambda m:m.group(1)+m.group(2).rstrip()+'\n\n'+paragraph+'\n\n',context,flags=re.S)
    assert n==1,cid
old=next(p for p in context.split('\n\n') if p.startswith('phase 001~025의 task 세션은 종료됐다.026은'))
new='phase 001~026의 task 세션은 종료됐다.026의 고정판 세 조사를 검수했고027은 doc-policy 단일 통합 work다. 문구 두 곳·초기화/연결 정책 직접 단언·역할 단계/부분 JSON/operator mode 검사와 공식 미러/관련 회귀를 한 담당자가 소유한다. 같은 doc_code/structure·미러·캐시 및 최종 판본을 공유하므로 수리를 병렬 task로 쪼개지 않는다. N01 나머지 이름 조사는 그 입력/소비가 바뀌는 동안 병행하지 않고 수리 검수 뒤 한정한다. 공식 검사는 jobs1·전체worker3 이하·한 묶음씩·소스 고정을 유지한다.'
context=context.replace(old,new)
write(RUN/'context.md',context)
plan=before['plan.md'].replace('## phase 001~025의 결과와 현재 상태','## phase 001~026의 결과와 현재 상태')
start=plan.index('## 다음 phase: 026')
end=plan.index('## 가까운 후속 배정과 선행 관계',start)
plan=plan[:start]+summary+'\n\n'+'''## 다음 phase: 027

gpt-6.1-sol/high의 doc-policy 한 task가026 정책 F2/F3와 역할 F1/F2를 통합한다. 초기화-운전의 기본 방침 생성·채택 설명과 독립-운영의 probe 분기 문구 두 곳을 고친다. 기존 초기화/공개 lifecycle 시험에 독립 기대·양쪽 저장/restart를 보강하고, 기존 doc_code/structure에 역할 단계·두 부분 JSON·operator mode의 정상/차용/오타 반례를 연결한다. runtime·정책·권한은 바꾸지 않는다. 새 runtime 반례는 후속 판단으로 반환한다.

공유 helper/structure·미러·비용 캐시와 같은 최종 관련 선택을 한 담당자가 소유해 문서별 반복 실행을 줄인다. 같은 판본을 읽는 N01 나머지 조사를 구현과 병행하면 종료 SHA와 소비가 바뀌므로 이번 phase에는 넣지 않는다.027의 정확 수리·관련 양쪽 회귀/미러 검수 뒤 N01 나머지 이름 질문을 현재판에서 한정하고 기존 requirement-state의 구체적 남김으로 이어 간다. N02 유지 부분이나 N03 이미 확인한 이름은 새 반례 없이 다시 조사하지 않는다.

'''+plan[end:]
old=next(p for p in plan.split('\n\n') if p.startswith('**025 manager의 묶음 결정:**'))
plan=plan.replace(old,'**026 manager의 묶음 결정:** 독립 조사는 끝났고 수정 후보가 문구 두 곳·정책 단언 두 경계·문서 검사 세 축으로 한정됐다. 이를027 단일 work에 묶어 공유 helper·미러와 관련 최종 회귀를 통합한다. 각 문서마다 별도 phase를 만들지 않고 N01의 다른 의미 질문/L01 외부 결정/최종 관문은 보존한다.')
plan=plan.replace('옛 전역은 복원하지 않는다. N03 다른 절은 계속 미검토.','옛 전역은 복원하지 않는다.026의 N03 이름 유지 판정을 재사용하며 문구/검사 공백은027에 남긴다.')
plan=plan.replace('026은024 F2다섯정책과N02/N03이름을독립판정하고N01의다른이름은유지한다.','026의 N02 유지 및 N03/정책 지정 판정을 검수했다.027에서 문구 두 곳·정책 저장 단언·역할 단계/JSON/operator mode 검사만 통합 수리하며 N01의 다른 이름은 유지한다.')
write(RUN/'plan.md',plan)
write(RUN/'seams.md',before['seams.md'].rstrip()+'\n\n026의 고정판 판정 결과를 검수했다.027은 기존 초기화 채택/대화 연결 저장, scheduled_operator의 probe 분기, stage_schema/extension_schema 및 cli_contract의 mode choices를 소비한다. 실제 코드 정의가 정본이고 반환·권한·오류 의미를 바꾸지 않는다. 문서/기존 시험/helper·공식 미러를 한 task가 소유하므로 새 S항목이나 provides/uses는 추가하지 않는다. 조사표를 별도 제품 schema로 복제하지 않으며 runtime 수리가 필요하면 정확 반례를 반환한다.')
after={n:(RUN/n).read_text(encoding='utf-8-sig') for n in before}
write(O/'common-docs.diff',''.join(''.join(difflib.unified_diff(before[n].splitlines(True),after[n].splitlines(True),fromfile=n+'.before',tofile=n)) for n in before))
save(O/'common-comparison.json',dict(before={n:sha(O/(n+'.before')) for n in before},after={n:sha(RUN/n) for n in before},criteria_unchanged=re.findall(r'### G\d+.*?(?=\n### G|\n## C|\Z)',before['context.md'],re.S)==re.findall(r'### G\d+.*?(?=\n### G|\n## C|\Z)',after['context.md'],re.S),meaning='C2/C8/C9/C10/C12에 검수 사실·한정 처분 추가, C5의 완료된026 배정을027로 교체. plan 다음 배정/관련 남김 갱신. 기존 G·L01·역사 실패/예외와 S의 의미는 불변.'))

dispositions=[]
def disp(task,fid,action,dest,reason,files):
    dispositions.append(dict(item=f'026/{task}/{fid}',action=action,destination=dest,reason=reason,evidence=[BASE+'review.md',BASE+'verification.json']+[f'run:phases/026/tasks/{task}/evidence/{f}' for f in files]))
disp('policy-semantics','F1','resolve',['run:context.md#C10'],'세 이름의 지정 문장·실제 승인/소비와 조건을 대조해 한정 의미 질문을 종결한다. 전체 정책/새 실행 인증은 아니다.',['policy-decisions.json'])
disp('policy-semantics','F2','carry',[NEXT+'#A1',NEXT+'#A2','run:context.md#C10'],'기본 방침을 기존 객체 재사용처럼 읽히게 하는 문구와 생성값/저장해시 직접 단언을 통합 교정한다.',['policy-decisions.json'])
disp('policy-semantics','F3','carry',[NEXT+'#A3','run:context.md#C10'],'명시/생략 정책의 연결행·instance 저장과 restart를 각각 독립 기대로 검사한다. runtime 결함으로 확대하지 않는다.',['test-bindings.json'])
disp('policy-semantics','F4','carry',[NEXT+'#A5','run:context.md#C9'],'원보고 부재와 역사판 한계는 유지하고 현재 HOLD·필요 관련 선택의 실행 근거를027에서 교체한다. PR 전체 종결은 아니다.',['history-review.json','historical-execution.json'])
disp('policy-semantics','F5','resolve',['run:context.md#C12'],'2675 전건/84 원task 불변을 manager가 확인했다. 기존 승인 성질만 재사용하며 제품 관문은 그대로 남긴다.',['source-end.json'])
disp('reference-names','F1','resolve',['run:context.md#C10'],'N02의58절 이름/조합은 현 소유와 직접 소비로 유지하며 새 수리 후보가 없다. 전체 기능의 재인증은 아니다.',['decisions.json','static-checks.json'])
disp('reference-names','F2','resolve',['run:context.md#C10'],'학술 이름 정의의 pending만 종결한다. 실제 응답/독해의 미주장을 새로운 확대 의무로 바꾸지 않고 원래G7/L01 책임을 유지한다.',['review.md'])
disp('role-contract-names','F1','carry',[NEXT+'#A1',NEXT+'#A5','run:context.md#C10'],'probe 정상 관찰과 HOLD/오류 반환을 문구에서 구별하고 현재 공개 경계 실행을 확인한다.',['repair-candidates.json'])
disp('role-contract-names','F2','carry',[NEXT+'#A4','run:context.md#C10'],'단계별 주 산출·두 부분JSON·operator mode의 정확 검사 공백을 기존helper/structure에 한정해 보강한다.',['repair-candidates.json','fence-decisions.json'])
disp('role-contract-names','F3','resolve',['run:context.md#C10','run:context.md#C12'],'N03 유지 부분과 기존P/설치경로 성과는 재사용하고 F1/F2만 별도 수리로 남긴다. 조사수/과거green을 전체합격으로 바꾸지 않는다.',['review.md','history-reuse.json'])
reasons={
'C2':'026 조사 완료와 manager 원자료 대조·미실행 한계를 추가했다.',
'C5':'종료된026 독립 조사 설명을027의 공유 파일/실행 자원 단독 소유로 교체했다.',
'C8':'사용자 지정 모델 그대로027 배정을 추가했다.',
'C9':'026의 역사보고 재사용·부재와 정확 PR slice 처분을 추가했다.',
'C10':'N02와N03/정책 유지 부분을 종결하고 네 수리 finding 및 기존 N01/L01 남김을 구별했다.',
'C12':'제품 불변과 원task 직접 추적·기존 변경 비포함 관리 마감을 추가했다.'}
save(RUN/'phases/026/manager.pending.json',dict(next='027',decision='세 report를 전문으로 읽고 형식/원자료를 검수해 A1~A4 조사 완료를 승인한다. N02 이름·N03 유지 부분과 정책 세 이름의 지정 문장을 종결한다. 정책 F2/F3 및 역할 F1/F2의 구체적 공백은027/doc-policy에 통합한다. 공유 helper/structure·미러·캐시 및 같은 최종 관련 선택을 한 담당자가 소유해 반복 실행과 마감을 줄인다. N01 나머지 조사는 입력판본 변화와 겹치므로 병행하지 않는다. 현재 제품 실행을 새로 수행한 것으로 주장하지 않으며 과거 실패·원보고 부재/판본 한계를 보존한다. 코드/권한 계약을 바꾸지 않는 work이고 최종 review가 아니므로 개발 종료는 불가하다. 공용 문서 차이를 검수해 G1~G8·L01 원문byte·symlink 미검사와 기존 예외를 보존했다. 관리 커밋은 보고/근거·배정·기억만 포함하고 제품/다른 dirty 변경이나 push는 없다.',
    reports=[dict(task=t,state='read',detail='A1~A4 complete 조사 결과를 승인한다. 검수와 한정 처분은 review.md, 발견별 후속은 dispositions에 있다. 제품 전체 합격 또는 새 시험 실행은 아니다.',evidence=[f'run:phases/026/tasks/{t}/report.json',BASE+'report-check.json',BASE+'verification.json',BASE+'review.md']) for t in ('policy-semantics','reference-names','role-contract-names')],
    dispositions=dispositions,context_updates=[dict(item=k,action='amend',destination=['run:context.md#'+k],reason=v,evidence=[BASE+'review.md',BASE+'verification.json',BASE+'common-docs.diff']) for k,v in reasons.items()],
    plan_update='026의 유지/종결과 네 수리 finding을 반영해027 단일 통합 work를 배정했다. 공유helper·직접단언·문구/미러·관련회귀를 묶고 N01 나머지/L01/최종관문 선행관계를 유지했다. common-docs.diff에 실제 변경과 기존 의미 보존을 기록했다.',seam_updates=[],completion=None))

print('Prepared 027/doc-policy and 026/manager.pending.json')
