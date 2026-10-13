"""Write the phase 003 manager's reviewed common documents and next assignment."""
import difflib
import hashlib
import json
import re
from pathlib import Path

REPO = Path(r'C:\math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).parent


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def save(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def replace_once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new, 1)


before = {name: (OUT / (name + '.before')).read_text(encoding='utf-8-sig')
          for name in ('context.md', 'plan.md', 'seams.md')}
for name, content in before.items():
    assert (RUN / name).read_text(encoding='utf-8-sig') == content, name + ' changed while reviewing'

context = before['context.md']
context = replace_once(context, '## C3 현재 정본과 이력의 역할', '''phase 003 provider-smoke는 partial이다. A1/A3/A4의 지정 범위와 A2/A5의 실패를 manager가 승인했다. report 검사 뒤 종료 파일 2254개, 정본/미러 공식 보고의 Python 864개 해시와 선택/실제 row/exit, 세 실제 호출의 schema·prompt·worker·파일·종료 원자료를 대조했다. 변경 62개가 모두 writes 안이고 현재 종료 해시 불일치는 0개다. Claude 최종 1개 실호출과 정본 오프라인 23개는 통과했으나 Codex schema HTTP 400 및 미러 4선택 중 2실패는 미해결이다. 관리 검수 당시 HEAD는 ea4b4f0fc04dbc0f2b384ff4d60d7de5a817611d이다. 근거는 run:phases/003/manager-evidence/verification.json 및 run:phases/003/tasks/provider-smoke/report.json이며 구체적 현재 조건은 C12에 둔다.

## C3 현재 정본과 이력의 역할''')
context = replace_once(context, 'phase 001의 독립 분석 세 task와 phase 002의 변이 정상 기준 수리 단일 task는 종료됐다. phase 003은 공급자 최소 스모크·녹화를 단일 task로 운영한다.', 'phase 001의 독립 분석 세 task, phase 002 변이 정상 기준 수리, phase 003 공급자 최소 스모크 task는 종료됐다. phase 003의 두 실패는 C12에 유지하며 phase 004는 미러 녹화 원바이트 수리를 단일 task로 운영한다.')
context = replace_once(context, '현재는 phase 001 세 task와 phase 002 한 task의 report를 각각 새 manager가 검사했다.', '현재는 phase 001 세 task, phase 002 한 task와 phase 003 한 task의 report를 각각 새 manager가 검사했다. phase 003은 실제 공급자 경계를 실행했으나 A2/A5가 실패한 partial이다.')
context = replace_once(context, '저장소 원보고 100개의 해시와 그중 39개의 선택·결과를 읽었다는 것은 closure-map의 관찰이다.', '''phase 003에서 PR15/B86/B87의 공급자 녹화·native background completion slice를 검토했다. 46a67a7f/87fd1c1b 도입 diff·현재 소비자·존재하는 네 원보고를 대조했고 Codex error/turn.failed 분류, Claude task_id/tool_use_id 및 시작/완료/선택 result 순서의 현 계약을 유지한다. 기존 background 원보고는 actual_wait_tool=false와 passed=false 그대로다. 현재 계약의 nonce 파일·native completion·로컬 종료 성질만 재사용하며 maintenance schema 수락이나 연구 저장 증거로 넓히지 않는다. PR15의 다른 slice는 미검토다. 근거는 run:phases/003/tasks/provider-smoke/evidence/review-notes.md와 run:phases/003/manager-evidence/verification.json이다.

저장소 원보고 100개의 해시와 그중 39개의 선택·결과를 읽었다는 것은 closure-map의 관찰이다.''')
context = replace_once(context, 'T5의 smoke 폴더에는 현재 test_*.py가 없고 runner는 빈 선택을 거부한다.', 'phase 001 당시 T5의 smoke 폴더에는 test_*.py가 없었고 runner는 빈 선택을 거부했다. phase 003이 현재 두 공급자 시험을 연결했으며 실제 결과와 남김은 C12를 따른다.')
context = replace_once(context, 'G7 work에서 공식 T5 진입점에 실제 smoke를 연결하고 필요한 실호출·말뭉치를 최종 소스 고정 전에 취득한다.', 'G7 work에서 필요한 실제 연쇄와 녹화를 최종 소스 고정 전에 완결한다. 공급자 최소 smoke의 구현과 부분 실호출만으로 다른 연쇄를 대신하지 않는다.')
start = context.index('phase 003 provider-smoke는 이 중 공식 T5의 공급자 최소 경계만 구현·실행한다.')
end = context.index('\ngate-readiness가 관찰한 설치 Codex는', start)
context = context[:start] + '''phase 003은 현행 maintenance action schema 전체로 공급자 최소 smoke를 구현·실행했다. Claude 역할 응답·파일·checkpoint·종료 회수는 최종 호출에서 성공했고 Codex는 동일 schema를 거부했다. 실제 원출력과 현재 parser 재생은 보존됐지만 미러 생성의 녹화 원바이트 변형도 확인됐다. 수리 책임과 재사용 조건은 C12에 둔다. Job/pythonw 전용 경계·Lean/Mathlib·예약·학술·L01과 G7 전체는 후속 책임이며 PR15 전체 검토로 확대하지 않는다.
''' + context[end:]
context = replace_once(context, 'gate-readiness가 관찰한 설치 Codex는 0.162.1, 녹화 manifest는 0.160.0이며 Claude는 양쪽 2.1.289다.', 'phase 001 gate-readiness 당시 설치 Codex는 0.162.1, 녹화 manifest는 0.160.0이며 Claude는 양쪽 2.1.289였다. phase 003은 현재 command-surface와 새 역할 호출을 녹화했고 이전 항목도 보존했다.')
context = replace_once(context, 'Claude background는 실제 event 순서와 현 background_completed_before_result 조건을 재판정해야 한다.', 'Claude background의 해당 native completion·파일·종료 조건 재판정은 phase 003과 C9/C12에서 완료했다.')
context = context.rstrip() + '''

## C12 공급자 부분 성공과 두 후속 수리

phase 003의 현재 T5 선택은 Codex/Claude maintenance 각 한 건이다. 실 ModelRunner·real_ports·worker·adapter·parser를 사용하며 세 worker schema가 현재 action_schema 전체와 같다. 새 호출은 Codex 1회·Claude 2회다. live-01은 2선택/2실패이며 Claude는 읽기 도구 출력에 checkpoint가 섞여 정확 비교가 실패했다. prompt를 명확히 한 live-02의 Claude 1선택은 모든 9개 판정과 공식 row가 통과했다. 마지막 live 뒤 호출 경로는 불변이고 오프라인 corpus 검사 세 파일만 바뀌었다. 최종 정본 23개 및 미러 4개의 Python 864개 해시가 현재와 일치한다. 근거는 run:phases/003/manager-evidence/verification.json 및 task의 live-01/live-02/offline-01/mirror-replay 원보고다.

F1은 확인된 제품 전달 경계 실패다. Codex 0.162.1/gpt-6-astra/low는 보통 maintenance schema의 선택 필드 integration_bundles가 required에 없다는 HTTP 400 invalid_json_schema를 반환했다. worker exit 1, parse_complete=true, turn_failed=true, final/파일/checkpoint 부재와 로컬 종료 barrier를 보존한다. 인증 부재나 timeout으로 추정하지 않으며 연구 control_binding 경로의 실패도 입증하지 않는다. 첫 오류 뒤 다른 제약은 미확인이다. 후속 schema/공급자 전달·수신 work는 현재 호출자 범위와 선택 필드의 부재/null/값 의미를 보존하는 해결책을 검증하고 Codex 대표 실호출을 새로 수행한다. 선택 필드를 삭제하거나 제품에서 강제로 필수화해 통과시키지 않는다.

F2는 현재 미러 규칙의 확인된 원바이트 보존 위반이다. 정본 corpus는 17항목·44파일·200872바이트이고 기존 raw는 불변이다. 미러는 두 Claude help 파일만 다르며 CLAUDE.md→AGENTS.md 치환 때문에 원 SHA a58ca228…가 1804fa77…로 바뀐다. 이전 help도 phase 003 시작 전에 이미 달랐다. 공식 --check exit 0은 생성 규칙 일치이며 실제 원자료 무결성을 대신하지 않는다. 미러 구조/재생은 4선택/2통과/2실패다. phase 004 mirror-corpus는 기존 _rules.json의 verbatim으로 corpus 데이터 경계를 보호하고 공식 생성 뒤 양쪽 전건 해시와 재생을 확인한다. 원 manifest의 SHA/verdict를 변형된 바이트에 맞추지 않는다. manager는 현재 Git clean이 정본 manifest·Lean 입력·scheduler 녹화 세 파일의 CRLF 바이트를 변환함도 확인했다. 이 관찰은 아직 커밋/checkout을 수행한 결과가 아니며, 같은 원바이트 인도 작업에서 corpus 한정 .gitattributes와 실제 clean 경로의 전건 보존을 확인하도록 배정한다. 근거는 run:phases/003/manager-evidence/git-clean-observation.json이다.

F3의 한정 재사용을 승인했다. 보존된 Claude background 원자료 9파일의 해시, 같은 task/tool ID와 시작<완료<result 순서, nonce 파일과 종료 barrier 및 현재 직접 코드 판본을 manager가 대조했다. 과거 passed=false를 유지하며 native completion·파일·로컬 종료 성질만 사용한다. 관련 B86/B87 판정은 C9에 있다. 별도 background 유료 호출은 필요하지 않다. 새 Claude 두 호출의 reported list cost 합계 약 USD 0.4631016은 실제 청구액이 아니며 Codex 거부 비용은 미보고다.

다음 순서는 작은 미러 수리 뒤 Codex 전달 경계 수리다. 둘은 제품 의존 자체는 다르지만 공식 미러 생성기·말뭉치·시험 캐시를 공유하므로 같은 phase로 병렬 배정하지 않는다. 외부 사용자 결정이 있어야만 진행할 문제로 판정하지 않았다. phase 003의 검수 기록과 새 배정은 관리 커밋으로 보존한다. 관련 실패의 교정·검증 전인 제품/시험 변경은 작업트리에 유지하고 제품 커밋은 별도 검수 후 판단한다. 보고·원자료와 제품 변경의 보관 범위는 run:phases/003/manager-evidence/review.md를 따른다. G1~G8의 원래 완료 조건과 다른 문서/의미/전체 관문 남김은 그대로다.
'''

plan = before['plan.md']
plan = replace_once(plan, '## phase 001~002의 결과와 현재 상태', '## phase 001~003의 결과와 현재 상태')
plan = replace_once(plan, '최종 전체 관문은 아직 실행하지 않았다. 현재 상태의 근거는 context C9~C11과 다음 자료다.', 'phase 003은 공급자 smoke를 구현했으나 Codex schema 거부와 미러 원바이트 변형 때문에 partial이다. Claude 최종 실호출과 정본 오프라인 23개 성공은 그 범위에서 승인했다. 최종 전체 관문은 아직 실행하지 않았다. 현재 상태의 근거는 context C9~C12와 다음 자료다.')
plan = replace_once(plan, '분류는 완료율이 아니다.', '- 공급자 실호출의 부분 결과: run:phases/003/tasks/provider-smoke/report.json 및 run:phases/003/manager-evidence/verification.json. task 종료 2254파일과 원보고/실호출 원자료를 대조했다. F1/F2는 미해결이며 F3 background의 한정 재사용과 PR15/B86/B87 지정 slice만 승인했다.\n\n분류는 완료율이 아니다.')
start = plan.index('## 다음 phase: 003')
end = plan.index('## 가까운 후속 배정과 선행 관계', start)
plan = plan[:start] + '''## 다음 phase: 004

work task `mirror-corpus` 하나를 배정한다. phase 003 F2의 두 Claude help 원자료 변형을 기존 `_rules.json`의 verbatim 규칙으로 수리한다. 현재 생성기는 이 규칙을 먼저 적용해 원바이트를 반환하므로 별도 생성기나 공급자 예외를 도입할 이유가 없다. corpus 전체 데이터 경계를 보호하고 일반 지시문의 런타임 치환을 유지하는 작은 회귀 검증, 공식 생성, 양쪽 해시/재생으로 끝낸다.

이 작업을 먼저 하는 이유는 모든 후속 corpus 인도에 이미 확인된 미러 실패가 반복되며, 모델 재호출 없이 좁은 규칙 수정과 현재 근거로 종료할 수 있기 때문이다. Codex schema 수리는 별도 다음 단위다. 동일 생성기·말뭉치·시험 캐시를 쓰는 두 수리를 병렬화하지 않는다. 상세 쓰기 범위와 A1~A4는 run:phases/004/tasks/mirror-corpus/objective.md다. manager는 제품을 직접 수정하지 않는다.

''' + plan[end:]
plan = replace_once(plan, '003 결과를 검수한 뒤 아래 구체적 남김에서 다음 단위를 선택한다.', '004 결과를 검수한 뒤 우선 Codex schema 전달·수신 경계의 확인된 실패를 한정 work로 배정한다. 그 밖의 구체적 남김은 아래와 같다.')
plan = replace_once(plan, '| G7 실제 공급자 조건·말뭉치 | phase 003에 배정했다. 현재 모델·인증을 비밀 비노출로 확인하고 두 공급자의 실제 역할 schema 호출 및 녹화/재생을 연결한다. Claude background는 현 사건/파일 조건으로 재판정한다. | 결과의 충족 범위를 G7에 연결한다. 버전 확인만으로 호출 성공을 선언하지 않는다. 외부 조건 부재는 정확한 상신으로 남긴다. |', '''| G7/G8 녹화 원바이트와 미러 | phase 004 mirror-corpus에 F2 수리를 배정했다. 기존/신규 raw·manifest를 보존하고 양쪽 전건 해시 및 실제 재생을 통과한다. | 현재 제품 생성의 실제 --check와 원자료 무결성을 함께 확인한다. 모델 호출·역할 schema 변경은 없다. |
| G7 Codex schema 수락·말뭉치 | phase 003 F1: 보통 maintenance의 선택 integration_bundles가 required에 없다는 실제 HTTP 400이다. 후속 task가 역할 schema와 공급자 전달/수신 경계의 현재 호출자를 확인하고 선택 필드 의미를 보존하는 수리·관련 검사·Codex 새 실호출과 녹화를 수행한다. | 004 뒤 단일 work로 배정한다. 부재/null/값과 다른 schema 제약을 확인하며 단순 필드 삭제·필수화를 하지 않는다. 기존 Codex 실패는 보존하고 Claude 성공/background는 경로 불변이면 재사용한다. |''')

seams = before['seams.md']
start = seams.index('phase 001의 독립 분석과')
end = seams.index('\n\n제품의 기존 공유 정의는', start)
seams = seams[:start] + '''phase 001의 독립 분석, phase 002 변이 정상 기준 수리와 phase 003 공급자 smoke 작업은 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring, 공급자 호출은 기존 contracts.action_schema·ModelRunner.run·real_ports·adapter/parser가 정본이다. phase 003의 부분 성공과 두 실패는 context C12에 있다.

phase 004의 단일 task는 `.agents/diff/_rules.json`과 `writing-skills/scripts/build_skill_mirrors.py`의 기존 transform/build_target을 사용해 corpus 원자료의 축자 생성을 수리한다. 입력은 정본 파일 바이트와 기존 규칙, 결과는 생성 미러이며 의미는 `writing-skills/references/멀티런타임_동기화.md`와 실제 코드로 확인한다. 한 task가 규칙과 생성 결과·양쪽 소비를 검증하므로 새 독립 인터페이스나 분리된 제공자/소비자를 만들지 않는다. provides/uses는 빈 목록이고 새 S 항목은 없다. report의 형식은 서비스 protocol.md가 직접 규정한다.''' + seams[end:]

after = {'context.md': context, 'plan.md': plan, 'seams.md': seams}
diff = []
for name, content in after.items():
    write(RUN / name, content)
    diff.extend(difflib.unified_diff(before[name].splitlines(keepends=True), content.splitlines(keepends=True),
                                    fromfile=name + ' before 003 manager', tofile=name + ' after 003 manager'))
write(OUT / 'common-docs.diff', ''.join(diff))
save(OUT / 'common-docs-review.json', {
    'changed_context_ids': ['C2', 'C5', 'C8', 'C9', 'C11', 'C12'],
    'unchanged_goal_ids': ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8'],
    'unchanged_context_ids': ['C1', 'C3', 'C4', 'C6', 'C7', 'C10'],
    'semantic_review': '기존 G 조건과 문서/의미/전체 관문 남김을 유지했다. C11의 당시 미실행 설명은 역사 관찰로 표시하고 현재 한정 성공/실패와 다음 책임은 C12에 분리했다. S 계약은 바꾸지 않았다.',
    'before_sha256': {n: hashlib.sha256((OUT / (n + '.before')).read_bytes()).hexdigest() for n in before},
    'after_sha256': {n: hashlib.sha256((RUN / n).read_bytes()).hexdigest() for n in after},
})

phase = {'kind': 'work', 'purpose': 'phase 003 F2의 녹화 원바이트 변형을 기존 미러 verbatim 규칙으로 수리하고 실제 양쪽 corpus 해시·재생·공식 생성 일치를 확인한다. Codex 역할 schema 거부는 별도 후속 work로 유지한다.',
         'tasks': [{'id': 'mirror-corpus', 'inputs': [
             'run:sources/user-decisions.md', 'run:phases/003/tasks/provider-smoke/report.json',
             'run:phases/003/tasks/provider-smoke/evidence/review-notes.md',
             'run:phases/003/tasks/provider-smoke/evidence/mirror-plan.json',
             'run:phases/003/tasks/provider-smoke/evidence/mirror-replay/report.json',
             'run:phases/003/tasks/provider-smoke/evidence/mirror-replay-command/stderr.txt',
             'run:phases/003/manager-evidence/verification.json', 'run:phases/003/manager-evidence/git-clean-observation.json',
             'repo:.agents/diff/_rules.json', 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md',
             'repo:.claude/skills/writing-skills/scripts/build_skill_mirrors.py',
             'repo:.claude/skills/writing-skills/scripts/test_build_skill_mirrors.py',
             'repo:.claude/skills/do-math/AGENTS.md', 'repo:.claude/skills/do-math/.gitattributes', 'repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
             'repo:.claude/skills/do-math/scripts/tests/corpus/manifest.json',
             'repo:.agents/skills/do-math/scripts/tests/corpus/manifest.json',
             'repo:.claude/skills/do-math/scripts/tests/structure/test_corpus.py',
             'repo:.claude/skills/do-math/scripts/tests/unit/test_corpus_replay.py',
             'repo:.claude/skills/do-math/scripts/tests/contracts/test_doubles_follow_corpus.py'],
         'writes': ['.agents/diff/_rules.json', '.claude/skills/do-math/.gitattributes', '.agents/skills/do-math/.gitattributes',
             '.claude/skills/writing-skills/scripts/test_build_skill_mirrors.py',
             '.agents/skills/writing-skills/scripts/test_build_skill_mirrors.py',
             '.claude/skills/writing-skills/references/멀티런타임_동기화.md',
             '.agents/skills/writing-skills/references/멀티런타임_동기화.md',
             '.agents/skills/do-math/scripts/tests/corpus/',
             '.claude/skills/do-math/scripts/tests/.timings.json', '.agents/skills/do-math/scripts/tests/.timings.json'],
         'provides': [], 'uses': []}]}
save(RUN / 'phases/004/phase.json', phase)
for path in [RUN / 'phases/004/logs/.gitkeep', RUN / 'phases/004/tasks/mirror-corpus/evidence/.gitkeep']:
    write(path, '')
print('Updated common documents; prepared phase 004 and diff.')
