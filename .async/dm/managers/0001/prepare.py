"""Prepare shared context and independent read tasks before publishing the queue."""
import json
from pathlib import Path

REPO = Path('C:/math')
RECORDS = REPO / '.async/dm'
LEGACY = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')

context_path = RECORDS / 'context.md'
context = context_path.read_text(encoding='utf-8')
begin = context.index('## 중단 지점과 첫 manager 책임')
end = context.index('## 모델·권한·자원', begin)
context = context[:begin] + '''## 이관 검수 완료와 현재 시작판

async manager 0001은 중단된 029/doc-names의 A1~A5와 F1의 지정 여덟 발견을 이관된 시작판의 성과로 수용했다. 현재 2675개 스킬 소스는 029 manager source-inspected 및 task 종료판과 전건 일치한다. 이관 snapshot 2681파일도 원래 해시와 같고, 추가 6파일은 루트 지침·설정이다. 원task 129파일은 불변이다. 현재 diff에서 정본10·미러10·비용캐시2의 범위, setup/probe의 실제 parser 공유, 문서 helper의 실제 정의 소비와 새 단언을 확인했다. 최종 c2/m2는 각각 183선택·183고유 passed·exit0이고 각875Python SHA가 현재와 같다. 기존38문서ID와 여덟 finding의 정확 시험ID도 그 결과에 포함된다. 새 제품 시험과 외부 호출은 실행하지 않았다.

판정의 정본은 `managers/0001/inheritance-review.json`과 `review.md`다. 과거 `phases/029/manager.pending.json`, 공용 문서와 M-0579는 중단 당시 초안으로 그대로 보존하며, 거기에 적힌 게시·압축·커밋 예정 표현을 완료 사실로 사용하지 않는다. 원task·제품 원바이트·중단로그·초안은 `managers/0001/legacy-029-raw.zip`과 `preservation.json`에 보존한다. 검수한20비캐시 제품경로의 관리 마감은 이번 manager의 commit 기록으로 연결한다. 기존 dirty/untracked·비용캐시·과거 관리초안은 이 작업의 제품 변경에 섞지 않는다.

029는 새 workspace task가 아니므로 integrate하거나 queue.accepted에 추가하지 않는다. 새 async 결과부터 실제 workspaces.py integrate와 accepted 절차를 따른다. 029 F2는 유지한다. parser·문구 변경은 설치/prompt hash를 바꾸므로 과거 전체 설치·실호출 판본 동등성이나 모델 독해를 재인증하지 않는다. 불변 하위경계 성질과 실제 관련 회귀만 재사용한다. L01 Q1/Q2와 원문 UTF-8 byte 미충족, Windows1314 symlink 실반려 미검사, G4~G8 및 다른 의미 질문은 열려 있다.

현재 새 배정은 r02(요청 생산·수신), r07(반환 소유권 모집단), r18(실제 외부 경계 호출)의 세 독립 work다. 기존030은 실행되지 않은 후보 원문이며 새 objective가 workspace/보고/경로 규약을 대체한다. 모두 제품 writes와 depends_on이 비어 있다. 같은 읽기 질문을 전수 감사나 문서 작업으로 확대하지 않으며, 각 완료 사건에서 확인된 공백만 후속 구현·관련 검증에 연결한다.

''' + context[end:]
write(context_path, context)

plan_path = RECORDS / 'plan.md'
plan = plan_path.read_text(encoding='utf-8')
begin = plan.index('## 첫 manager의 유한한 작업')
end = plan.index('## 이후의 진행 방식', begin)
plan = plan[:begin] + '''## 현재 배정과 수용한 결과

0001은 029의 지정 문서/검사 수리를 현재 소스와 원자료에 대조해 이관 성과로 수용했다. 여덟028 finding과029 F1은 종결했다. 판본 한계인 F2와 G4~G8, L01, symlink 미검사는 유지한다. 이관 성과는 새 queue의 accepted task가 아니다. 근거는 managers/0001/inheritance-review.json·review.md이며 새 제품 시험은0이다.

| task | 종료할 질문과 산출물 | 선행·수정 범위 |
|---|---|---|
| r02 | R02/1-A 중 작업자 요청 가족의 실제 ModelRunner 생산과 Codex/Claude 수신, 필수+선택 역방향을 branch-field-map.json으로 판정. PR18/B49 관련 slice와 직접 K/P2만 연결. | 독립 work, depends_on=[], writes=[] |
| r07 | R07/1-E의 현재 owned builder·transformer·borrowed lookup과 실제 반환 경로/검사 등록을 ownership-map.json으로 대조. PR06/B22 및 기존 G4/G5 반환소유권 검토의 남은 모집단만 판정. | 독립 work, depends_on=[], writes=[] |
| r18 | R18/9-A의 현재 프로세스·파일 경계 호출과 구조 검사 등록을 boundary-map.json으로 대조. PR02/B13/B14/B62/B85 관련 slice,029 parser 이동의 경계 영향만 판정. | 독립 work, depends_on=[], writes=[] |

모델은 세 task 모두 gpt-6.1-sol/high이며 실행기 max_workers=3이다. 시작 inputs/base/workspace가 각자 고정되므로 다른 task 결과를 기다리거나 중간 변경을 소비하지 않는다. 순수 정적 파싱·해시·기존 원자료 대조로 종료 질문에 답한다. 새 공식 검사·실호출·공유 캐시 변경은 이번 배정에 필요하지 않다. 자료와 결론은 자기 task/evidence와 async report.json에 남긴다.

한 결과가 도착하면 manager가 실제 파일/단언/원보고를 검수하고 무변경 조사도 integrate한 뒤 accepted에 넣는다. 충분한 기존 증거, 최종 실행 대기, 확인된 수리, 정확 미결을 구별한다. 구현이 필요하면 정확 반례·파일·검증을 한 task에 묶고, 공유 helper 수정은 한 담당자로 모은다. 독립 후속은 다른 조사 종료를 기다리지 않고 준비하며 실행 중 배정은 바꾸지 않는다.

''' + plan[end:]
plan = plan.replace('029는 이관 검수 대상이다.', '029의 지정 여덟 발견은0001에서 이관 검수를 마쳤다.')
write(plan_path, plan)

seams_path = RECORDS / 'seams.md'
seams = seams_path.read_text(encoding='utf-8')
seams += '''
## 이번 세 읽기의 실제 연결과 보고 경계

- r02: `do_math/model_runner.py:ModelRunner` 및 현재 adapter의 요청 조립, `worker_request.py`의 `check_codex_request`/`check_claude_request`, `codex_worker.py`/`claude_worker.py`의 load 경계가 대상이다. `tests/contracts/pairs.py:_worker_request_samples`와 `test_pairs.py`의 required/optional 역방향 단언이 실제 저장·수신까지 무엇을 입증하는지 구별한다. 이 문서는 새 요청 schema를 정의하지 않는다.
- r07: `tests/structure/test_schema_builders.py`의 `_calls`, `_composition_calls`, `_constant_object_calls`, `TRANSFORMERS`, `DELEGATED_SCHEMA_METHODS`가 현 등록이다. 실제 contracts/control/record schema와 engine·review_cycle·knowledge_io·planning 반환의 소유 계약에 대응한다. caller 입력을 빌리는 transformer나 read-only borrowed row를 임의 copy 의무로 바꾸지 않는다.
- r18: `tests/structure/test_boundary_invariants.py`의 `PROCESS_STARTS`, `INJECTED_STARTS`, `JOB_RUN_STARTS`, `INTERPRETER_USES`, `EXECUTABLE_IDENTITY` 및 발견 함수와 `file_io.py`의 소유 규칙을 실제 windows_job/git_process/cli_worker/formal/scheduler 및 최상위 도구 호출에 연결한다. 현재 누락과 장래 가상 우회 가능성을 구별한다.
- 세 task의 제품 경로는 자기 workspace 상대 경로다. `C:/math/docs/...`와 `C:/math/.async/dm/...` 입력은 읽기 전용 원자료다. 과거 문서 안 `run:`은 legacy 실행 루트, 과거 `repo:docs/...`는 공용소스의 원자료를 뜻한다. workspace에 없는 대형 기록을 제품 누락으로 판정하지 않는다.
- source 판본 비교는 task의 `baseline.json`과 자기 workspace를 기준으로 하고, 이관 기준은 `managers/0001/source-inspected.json`의 스킬2675파일과 교집합에서 대조한다. 실제 차이가 있으면 명시한다. 이후 manager가 공용소스에 다른 결과를 반영해도 이미 실행 중인 task는 자기 고정판으로 완료한다.
- 보고는 async protocol의 `status`, `summary`, 문자열 목록 `changes`/`findings`, `verification`을 사용한다. 제품 무변경 조사는 changes=[]이다. 각 finding 문자열에는 해당 요구·증거 파일/심볼·영향과 다음 행동을 함께 적고 자세한 표는 자기 evidence를 참조한다.
'''
write(seams_path, seams)

old_phase = json.loads((LEGACY / 'phases/030/phase.json').read_text(encoding='utf-8'))
mapping = [('r02', 'request-producers'), ('r07', 'schema-ownership'), ('r18', 'boundary-census')]
tasks = []
for task_id, old_id in mapping:
    old = (LEGACY / 'phases/030/tasks' / old_id / 'objective.md').read_text(encoding='utf-8')
    purpose = old.split('## 완료 조건')[0].replace('고정된029 검수판', '자기 workspace의 이관 검수판').replace('같은030의 다른 task', '다른 async task')
    middle = old[old.index('### A2'):old.index('### A4')]
    objective = purpose + '''## 입력과 실행 위치

SESSION_JSON의 workspace에서 현재 코드와 시험을 읽는다. inputs/context.md·plan.md·seams.md, objective.md·task.json이 이번 배정의 정본이다. C:/math 공용소스와 다른 task 기록은 읽기 전용이다. inputs의 스킬 상대 경로는 workspace 기준이며 절대 경로는 원자료다. 과거 문서 안 `run:`은 C:/math/docs/do-math/continuous-development-2026-10-13, `repo:docs/`는 C:/math/docs/를 뜻한다. 과거 `repo:.claude/` 코드는 현재 workspace에서 확인한다. 기존030 objective는 질문의 출처이며 그 phase/cwd/report/공용쓰기 절차는 사용하지 않는다.

## 완료 조건

### A1 현재판과 필요한 원문만 고정

baseline.json과 inputs를 사용해 자기 시작판을 고정한다. managers/0001/source-inspected.json의2675 스킬 파일과 자기 baseline의 해당 경로를 대조하고 실제 차이를 기록한다. root 지침6파일과 과거 docs의 snapshot 부재는 제품 결함이 아니다. 해당 requirement-state/tracking-state ID와 원문·설계, 직접 연결 K/P2만 읽는다. 103행 전체 재분류나 기존 충분한 후보의 전수 재감사를 반복하지 않는다. 사용한 정의·단언·원보고 판본과 소스 해시를 evidence에 남긴다.

''' + middle + f'''### A4 무변경과 인계

writes=[]이므로 제품·시험·미러·공용 문서·다른 task·engine·graphify·Git index를 수정하지 않는다. 자기 task/evidence와 report.json만 쓴다. 끝날 때 baseline 대비 소스 변경이 없음을 확인한다. 새 공식 run_tests/pytest/unittest, 실제 모델/Job/Lean/예약/네트워크 호출은 하지 않는다. 정적 파싱·해시·기존 원자료 대조가 기본이며, 추가 순수 계산은 질문 해결에 꼭 필요하고 제품 부수효과나 공유 캐시가 없을 때만 사용한다. 관찰을 새 통합 실행으로 보고하지 않는다.

런타임·검사 수리가 필요하면 최소 입력, 계약상 기대/현재 결과, 정확 파일·심볼·단언과 다음 담당을 보고한다. manager가 구현·미러·관련 검증을 한 task로 배정한다. 다른 독립 task의 결과를 기다리거나 읽지 않는다. L01 Q1/Q2·UTF-8 byte 미충족, Windows1314 symlink 실반려 미검사, G4~G8과 다른 미결 질문을 유지한다. 이번 complete는 이 종료 질문의 판단 완료이며 전체 제품 합격이 아니다.

## 결과 제출

C:/math/.async/dm/tasks/{task_id}/report.json에 async protocol 형식으로 status, summary, changes=[], verification, findings(문자열 목록)를 작성한다. summary에는 닫힌 질문과 남은 수리/최종 실행을 구별하고 verification에는 실제 읽은 정의·단언·원자료와 새 실행 유무·한계를 적는다. 각 finding 문자열은 근거·영향 G/원문 ID·다음 행동을 포함하며 상세 표와 conclusion.md를 자기 evidence에서 가리킨다. 과거 acceptance/checks 구조를 새 보고 필드로 복사하지 않는다.

마지막에 `python C:/math/services/async-development/check.py report C:/math/.async/dm {task_id}`를 실행해 PASS를 확인한다. Git 과거 조회는 `git -C C:/math`로 읽기만 하며 workspace를 Git repo로 가정하지 않는다. commit은 manager 책임이다.
'''
    write(RECORDS / 'tasks' / task_id / 'objective.md', objective)
    spec = next(t for t in old_phase['tasks'] if t['id'] == old_id)
    inputs = []
    for reference in spec['inputs']:
        if reference.startswith('run:'):
            reference = (LEGACY / reference[4:]).as_posix()
        elif reference.startswith('repo:docs/'):
            reference = (REPO / reference[5:]).as_posix()
        elif reference.startswith('repo:'):
            reference = reference[5:]
        inputs.append(reference)
    inputs += [(OUT / 'inheritance-review.json').as_posix(), (OUT / 'source-inspected.json').as_posix()]
    tasks.append({'id': task_id, 'kind': 'work', 'depends_on': [], 'writes': [], 'inputs': inputs,
                  'model': 'gpt-6.1-sol', 'effort': 'high'})
write(OUT / 'queue.pending.json', json.dumps({'status': 'active', 'tasks': tasks, 'accepted': []}, ensure_ascii=False, indent=2) + '\n')
print('Prepared shared documents and independent tasks: r02, r07, r18; queue not published.')
