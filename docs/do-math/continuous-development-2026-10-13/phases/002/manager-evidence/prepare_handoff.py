"""Write the concrete manager submission and next assignment; no product edits."""
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[6]
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).parent

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

for relative in ['phases/003/tasks/provider-smoke/evidence', 'phases/003/logs']:
    (RUN / relative).mkdir(parents=True, exist_ok=True)

inputs = [
    'run:sources/user-decisions.md',
    'run:phases/001/tasks/gate-readiness/report.json',
    'run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json',
    'run:phases/001/tasks/gate-readiness/evidence/population-and-corpus.json',
    'run:phases/001/tasks/gate-readiness/evidence/environment.json',
    'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
    'repo:docs/do-math/시험-재편-2026-09-29/설계.md',
    'repo:docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json',
    'repo:.claude/skills/do-math/AGENTS.md',
    'repo:.claude/skills/do-math/scripts/이음새-정본.md',
    'repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
    'repo:.claude/skills/do-math/scripts/run_tests.py',
    'repo:.claude/skills/do-math/scripts/probe_cli.py',
    'repo:.claude/skills/do-math/scripts/do_math/contracts.py',
    'repo:.claude/skills/do-math/scripts/do_math/core_engine.py',
    'repo:.claude/skills/do-math/scripts/do_math/model_runner.py',
    'repo:.claude/skills/do-math/scripts/do_math/wiring.py',
    'repo:.claude/skills/do-math/scripts/tests/corpus/manifest.json',
    'repo:.claude/skills/do-math/scripts/tests/structure/test_corpus.py',
    'repo:.claude/skills/do-math/scripts/tests/unit/test_corpus_replay.py',
    'repo:.claude/skills/do-math/scripts/tests/contracts/test_doubles_follow_corpus.py',
    'repo:.claude/skills/do-math/scripts/tests/sim/test_operator_probe_contract.py',
    'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md',
]
relative_writes = [
    'scripts/tests/smoke/',
    'scripts/tests/support/provider_live.py',
    'scripts/tests/unit/test_provider_live.py',
    'scripts/tests/corpus/manifest.json',
    'scripts/tests/corpus/codex/',
    'scripts/tests/corpus/claude/',
    'scripts/tests/corpus/capabilities/',
    'scripts/tests/structure/test_corpus.py',
    'scripts/tests/unit/test_corpus_replay.py',
    'scripts/tests/contracts/test_doubles_follow_corpus.py',
    'scripts/tests/시험-지침.md',
    'scripts/tests/.timings.json',
]
phase = {
    'kind': 'work',
    'purpose': '공식 T5의 빈 공급자 경계를 현 maintenance 역할 schema의 Codex/Claude 최소 실호출과 '
               '파일·checkpoint·종료 회수, 현재판 raw 녹화·재생으로 연결한다. 외부 실행 조건을 문서 작업 전에 '
               '확인하고 실패/미실행은 그대로 보고한다. Job/pythonw 전용 연쇄·Lean·예약·학술·L01은 후속에 남긴다.',
    'tasks': [{'id': 'provider-smoke', 'inputs': inputs,
               'writes': [root + path for root in ('.claude/skills/do-math/', '.agents/skills/do-math/')
                          for path in relative_writes], 'provides': [], 'uses': []}],
}
dump(RUN / 'phases/003/phase.json', phase)

verify = 'run:phases/002/manager-evidence/verification.json'
review = 'run:phases/002/manager-evidence/review.md'
report = 'run:phases/002/tasks/mutation-baseline/report.json'
raw = 'run:phases/002/tasks/mutation-baseline/evidence/related-final/report.json'
next_objective = 'run:phases/003/tasks/provider-smoke/objective.md'
publics = ['context.md', 'plan.md', 'seams.md']
paths = [str((RUN / name).relative_to(REPO)).replace('\\', '/') for name in publics]
diff = subprocess.check_output(['git', 'diff', '--', *paths], cwd=REPO)
(OUT / 'public-docs.diff').write_bytes(diff)
edition = {}
for name, path in zip(publics, paths):
    previous = subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=REPO)
    current = (RUN / name).read_bytes()
    edition[name] = {'before_sha256': hashlib.sha256(previous).hexdigest(),
                     'after_sha256': hashlib.sha256(current).hexdigest()}
dump(OUT / 'public-docs.json', edition)

decision = {
    'next': '003',
    'decision': 'phase 002 mutation-baseline의 complete를 A1~A5 범위에서 승인한다. 공용 문서 갱신 전에 report '
                '검사를 통과했고 현재 2206파일 해시와 related-final의 Python 862개 해시, 58선택/58 passed·exit 0·'
                '실행 중 소스 불변, 실제 fixture 19개의 raw 보고와 시도 연결을 대조했다. 수리 전 정상 결과 파일 부재가 '
                'killed/True로 처리된 반례와 수정 후 execution_error/비통과가 실제 CLI/T3 소비에 연결된다. 최초 fixture '
                '준비 오류와 중간 단언 실패는 별도 실패 기록으로 보존한다. D9·모듈 비용 순서·failfast·정상 실패 제외·'
                '시간 종료 금지를 유지했다. F1/F2는 해당 정상 기준 결함과 PR01 mutation slice의 해결로 처분하며 '
                '전체 함수 변이·PR01 나머지와 G1~G8 미완료 조건을 보존한다.\n\n'
                '다음은 단일 work task provider-smoke다. 현재 비어 있는 T5와 Codex 녹화/설치판 차이를 해소할 '
                '최소 공급자 경계를 먼저 수행해 실제 모델 접근 및 역할 schema 수락 조건을 확인한다. 현재 maintenance '
                'action schema를 그대로 보내는 실제 두 공급자 호출, 파일/checkpoint/종료 회수, raw 녹화와 parser 재생, '
                'Claude background의 현 계약 재판정만 묶었다. PR15/B86/B87의 관련 slice를 결합하며, 제품 parser/worker '
                '수리는 쓰기 범위 밖이다. 실패하면 유효한 구현과 원자료를 partial/blocked로 반환해 다음 수리 또는 외부 '
                '결정을 특정한다. 전체 T5·G7이나 최종 review 완료는 아니다.\n\n'
                '공유 corpus·미러·캐시·실모델 호출 때문에 같은 phase에 다른 task를 두지 않는다. 모델/effort는 기존 '
                'Codex 기본 설정을 상속하고 실호출 모델은 task가 현재 근거로 명시한다. manager는 제품을 편집하거나 '
                '이미 통과한 관련 시험을 반복하지 않았다. 공용 문서 차이를 검토한 뒤 handoff 검사와 manager.json 게시, '
                '정확한 파일·기억 결합 커밋으로 마감한다. push/graphify 갱신은 하지 않는다.',
    'reports': [{'task': 'mutation-baseline', 'state': 'read',
                 'detail': '보고 전문과 A1~A5를 읽고 report 검사 통과. 결과 부재 red2, 58개 최종 관련 시험, 실제 child '
                           '17개 최종 fixture 및 2개 수리 전 fixture, 소스 해시·허용 쓰기·생성 미러를 원자료와 대조했다. '
                           '해당 task 완료를 승인한다. 전체 G의 실행/최종 review는 미완료다.',
                 'evidence': [report, verify, review, raw,
                              'run:phases/002/manager-evidence/report-check.stdout.txt']}],
    'dispositions': [
        {'item': '002/mutation-baseline/F1', 'action': 'resolve',
         'destination': ['run:context.md#C11', 'run:plan.md'],
         'reason': '001/gate-readiness/F4의 정상 근거 부재 거짓 포착을 실제 red/green과 CLI/T3 소비로 해결했다. '
                   '현재 결과·baseline·attempt 구조를 최종 G6에 사용하도록 명시했다. 전체 함수 모집단/fresh T3/전체 '
                   '변이는 기존 최종 관문에 남아 있으며 이번 해결로 G3/G6 전체를 충족했다고 판정하지 않는다.',
         'evidence': [verify, raw, review,
                      'run:phases/002/tasks/mutation-baseline/evidence/boundary-observations.json']},
        {'item': '002/mutation-baseline/F2', 'action': 'resolve',
         'destination': ['run:context.md#C9', 'run:plan.md'],
         'reason': 'B56 원보고 네 경로 부재를 재확인하고 실제 commit diff·현재 소비·새 관련 결과로 mutation '
                   'slice의 유지/교정을 승인했다. 원본을 복원하거나 과거 counts를 합산하지 않는다. PR01의 T3 store·'
                   '전체 runner·provenance는 해당 작업에서 필요한 근거를 확인할 남김으로 보존한다.',
         'evidence': [verify, review,
                      'run:phases/002/tasks/mutation-baseline/evidence/prior-review.json',
                      'run:phases/002/tasks/mutation-baseline/evidence/review-notes.md']},
    ],
    'context_updates': [
        {'item': 'C2', 'action': 'amend', 'destination': ['run:context.md#C2'],
         'reason': '역사 기준선과 B129/B130~B134 한계를 보존하고 phase 002 검수·58개 부분 성공·현재 해시와 범위 한계를 추가했다.',
         'evidence': [verify, report, 'run:phases/002/manager-evidence/public-docs.diff']},
        {'item': 'C5', 'action': 'amend', 'destination': ['run:context.md#C5'],
         'reason': '종료된 002를 과거로 바꾸고 003 단일 task의 공유 corpus/캐시/실호출 충돌 조건을 반영했다. worker와 소스 고정 규칙은 유지했다.',
         'evidence': [report, next_objective, 'run:phases/003/phase.json']},
        {'item': 'C8', 'action': 'amend', 'destination': ['run:context.md#C8'],
         'reason': '현재 서비스 수행 상태에 phase 002 보고 검수를 반영했다. 지원 모델 목록 미확인과 제품 G7 실호출 경계의 구별은 유지했다.',
         'evidence': [report, verify]},
        {'item': 'C9', 'action': 'amend', 'destination': ['run:context.md#C9'],
         'reason': 'phase 001 검토 모집단과 완료 slice를 보존하고 PR01/B56 mutation slice의 새 유지/교정 판정 및 네 원보고 부재를 추가했다.',
         'evidence': [review, verify, 'run:phases/002/tasks/mutation-baseline/evidence/review-notes.md']},
        {'item': 'C11', 'action': 'amend', 'destination': ['run:context.md#C11'],
         'reason': '미수리 fails_unmutated 설명을 검수한 현재 단일 결과/정상 기준/시도 연결로 교체했다. 전체 G6 모집단과 '
                   'T4/T5·환경 한계는 유지하고 phase 003의 대표 maintenance 공급자 경계 및 후속 G7 범위를 명시했다.',
         'evidence': [verify, review, report, next_objective,
                      'run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json']},
    ],
    'plan_update': 'phase 002 정상 기준 수리와 PR01 mutation slice 검수를 완료로 기록하고 바로 다음 단위를 003 '
                   'provider-smoke로 바꿨다. 외부 모델/역할 schema 조건을 장기 문서 수리보다 먼저 확인한다. P01/N03·'
                   '나머지 문서/의미 질문·T4 측정·Job/Lean/예약/학술/L01·전체 일반→fresh T3→전체 함수 변이→'
                   '수정 없는 최종 review 순서와 완료 조건은 유지한다. 외부 실패를 정확히 보고한 뒤 독립 수리는 계속 '
                   '배정하며 모든 행동이 외부 조건에 막힐 때의 상신 절차도 유지한다. public-docs.diff로 전후 의미를 대조했다.',
    'seam_updates': [],
    'completion': None,
}
dump(RUN / 'phases/002/manager.pending.json', decision)
print('Prepared phase 003 and manager.pending.json; no handoff has been published.')
