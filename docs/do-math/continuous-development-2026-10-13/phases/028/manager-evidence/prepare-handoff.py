"""Write this manager's common-state edits and next assignment, never product code."""
import difflib
import json
from pathlib import Path

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
TASKS = ('operator-names', 'cli-control-names', 'role-glossary-names')

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def append_section(text, id, addition):
    start = text.index('## ' + id + ' ')
    end = text.find('\n## C', start + 4)
    if end < 0: end = len(text)
    return text[:end].rstrip() + '\n\n' + addition + '\n\n' + text[end:].lstrip('\n')

def main():
    assert not (RUN / 'phases/028/manager.json').exists()
    next_dir = RUN / 'phases/029'
    (next_dir / 'logs').mkdir(exist_ok=True)
    (next_dir / 'tasks/doc-names/evidence').mkdir(exist_ok=True)
    inputs = [
        'run:sources/user-decisions.md', 'run:sources/model-policy-2026-10-14.md',
        'run:sources/document-batching-2026-10-14.md',
        'run:phases/028/manager-evidence/source-inspected.json',
        'run:phases/028/manager-evidence/verification.json', 'run:phases/028/manager-evidence/review.md',
        'run:phases/027/tasks/doc-policy/evidence/c3/report.json',
    ]
    for t in TASKS:
        inputs.append(f'run:phases/028/tasks/{t}/report.json')
    for t, names in {
        'operator-names': ['minimal-counterexamples.json', 'json-example-bindings.json', 'identity-module-mismatch.json', 'test-bindings.json'],
        'cli-control-names': ['findings.json', 'pure-observations.json', 'check-bindings.json'],
        'role-glossary-names': ['repair-candidates.json', 'schema-observations.json', 'test-bindings.json'],
    }.items():
        inputs.extend(f'run:phases/028/tasks/{t}/evidence/{n}' for n in names)
    inputs += ['repo:' + p for p in [
        '.claude/skills/do-math/AGENTS.md', '.claude/skills/do-math/scripts/tests/시험-지침.md',
        '.claude/skills/do-math/scripts/이음새-정본.md',
        '.claude/skills/writing-skills/references/멀티런타임_동기화.md',
        '.claude/skills/do-math/README.md', '.claude/skills/do-math/references/초기화-운전.md',
        '.claude/skills/do-math/references/CLI-실행-계약.md',
        '.claude/skills/do-math/scripts/tests/support/doc_code.py',
        '.claude/skills/do-math/scripts/tests/structure/test_doc_code.py',
        '.claude/skills/do-math/scripts/setup_lean.py', '.claude/skills/do-math/scripts/probe_cli.py',
    ]]
    writable = [
        'README.md', 'references/초기화-운전.md', 'references/CLI-실행-계약.md',
        'scripts/setup_lean.py', 'scripts/probe_cli.py',
        'scripts/tests/support/doc_code.py', 'scripts/tests/structure/test_doc_code.py',
        'scripts/tests/unit/test_engine_cli_contract.py',
        'scripts/tests/sim/test_toolchain_tools.py', 'scripts/tests/sim/test_operator_probe_contract.py',
        'scripts/tests/시험-지침.md', 'scripts/tests/.timings.json', 'scripts/tests/.timings-t3.json',
    ]
    phase = dict(kind='work', purpose='028의 여덟 문구/검사 공백을 실제 parser·schema·소비 단언에 연결해 한 번의 공유 수리·미러·관련 회귀로 닫는다.',
                 tasks=[dict(id='doc-names', model='gpt-6.1-sol', effort='high', inputs=inputs,
                             writes=[root + '/' + p for root in ('.claude/skills/do-math', '.agents/skills/do-math') for p in writable],
                             provides=[], uses=[])])
    save(next_dir / 'phase.json', phase)
    # Recreate from the recorded pre-edit bytes to make retries deterministic.
    context = (O / 'context.md.before').read_text(encoding='utf-8-sig')
    result = ('phase 028 세 고정판 task의 A1~A4 complete를 검수했다. report 형식 검사 뒤027·각 시작/끝·현재2675소스의 전건 SHA와 파일 집합 일치, 원task92파일 불변을 확인했다. '
              '288절의 정확 합집합과 현재 이름 좌표655/1223/634개·정의/시험118파일을 대조했다. 가운데1223은 inline849와 fence374의 합이므로 같은 모집단으로 합산하지 않는다. '
              '027 c3의134선택/고유row 중38문서passed 및 현재875Python SHA를 재사용했고 새 제품 실행은0이다. 유지241·재사용29·문구수정4·검사보강14절이며 후속 issue는8개다. '
              '조사 완료와 제품 합격을 구분하고 여덟 수리를029에 통합한다. 근거는 run:phases/028/manager-evidence/verification.json·decisive-sources.json·review.md와 세 원report다. 전체G 완료가 아니다.')
    context = append_section(context, 'C2', result)
    old = ('phase 001~027 task 세션은 종료됐고027 통합 수리를 검수했다.028은 고정판 N01의 이름 판정을 operator-names(66절), cli-control-names(27절), role-glossary-names(195절)의 세 독립 읽기 task로 배정한다. 정확288절 합집합은028 assignments.json에 있고 작은 용어집 절162개를 개별 작업으로 나누지 않는다. 제품 쓰기·공식 시험·미러/캐시 갱신·같은 phase 결과 소비가 없어 병렬 가능하다. 결과가 요구하는 공유 helper/문서/미러 수리는 후속 통합 work가 맡는다. 공식 검사에는 jobs1·전체worker3 이하·한 묶음씩·소스 고정을 유지한다.')
    new = ('phase 028의 세 독립 읽기 task는 모두 종료됐고288절의 정확 합집합을 검수했다.029 doc-names는 여덟 issue의 문구·doc_code/test_doc_code·두 도구 parser 연결·공식 미러/관련 회귀를 한 담당자에게 배정한다. '
           '공유 helper와 미러/캐시가 겹치므로 병렬 구현은 하지 않는다. 이미 끝난 이름 조사를 반복하지 않고 정확 문장·14최소 helper 반례·모듈 집합과 부재 검사를 통합한다. '
           '실제 parser 정의가 main과 문서 검사에 함께 쓰이게 하는 작은 추출만 제품 코드 쓰기 범위에 포함한다. 공식 검사는 jobs1·전체worker3 이하·한 묶음씩·소스 고정을 유지한다.')
    assert context.count(old) == 1
    context = context.replace(old, new)
    context = append_section(context, 'C8', '028 세 task의 gpt-6.1-sol/high 수행을 검수했고029 doc-names에도 같은 model/effort를 명시한다. manager와 제품 공급자 모델 설정은 바꾸지 않는다.')
    context = append_section(context, 'C9', '028의 기존 근거 재사용은 같은 현재 문장/정의/단언과 원report SHA가 확인된 성질로 제한한다. 과거38문서passed를 새 실행으로 세지 않고, knowledge/external/종류 제안의 기존 직접 소비 단언은 원문과 대조한 정적 근거다.029가 그 단언을 포함한 최종 관련 실행을 맡는다. 이번 조사로 PR 전체나 G2의 나머지를 종결하지 않는다. 근거는028 manager review.md·reused-report.json 및 세 task의 결속표다.')
    context = append_section(context, 'C10', '028에서 N01 288절의 이름/조합 판정을 마쳤다. 유지241·재사용29절을 승인하고 문구수정4·검사보강14절은 여덟 issue로029에 넘긴다. operator F1은 setup/probe의 실제 parser 옵션 소유, F2는 README 설정/초기화grant 예제, F3는 능력 식별모듈 누락7개다. cli F1은 knowledge의 기존ID import 금지·새 replacement/조건부formal 재사용·여섯연산/withdrawn예외, F2는 전송원장과 실행running·HTTP409 failed/unknown 구별, F3는 상태표/설정기본값/query/knowledgeJSON의 다섯 검사 반례다. role F1은 knowledge.kind의 TEXT와 활성/같은묶음 제안 검사 설명, F2는 CLI네단계/checkpoint의 다섯 반례다. role F3의 보존/한정재사용 사실은 종결한다. 029가 문구와 실제 정의 소비·미러/관련 검사를 통합한다.027/P/PURE/N02/N03의 승인 성질과 L01 Q1/Q2·원문UTF-8 byte 미충족은 유지한다. 근거는 run:phases/028/manager-evidence/review.md 및 run:phases/029/tasks/doc-names/objective.md다.')
    context = append_section(context, 'C12', '028은 제품·시험·문서·미러 변경이 없어027 판본의 승인된 성질과 제한을 유지한다. 이번 관리 커밋은 원task92파일을 직접 추적하고 공용 인계·검수 근거·029 배정·기억을 포함한다. 새 중복 archive는 만들지 않는다. 진행 로그·stage/commit 행정 수신은 로컬 보관으로 정리 시 사라질 수 있다. 기존 dirty/untracked 제품·운영자 변경은 stage하지 않는다. 정확 추적 범위와 원자료 SHA는 run:phases/028/manager-evidence/preservation.json에 둔다.')
    (RUN / 'context.md').write_text(context, encoding='utf-8')
    plan = (O / 'plan.md.before').read_text(encoding='utf-8-sig')
    plan = plan.replace('## phase 001~027의 결과와 현재 상태', '## phase 001~028의 결과와 현재 상태', 1)
    start = plan.index('## 다음 phase: 028')
    end = plan.index('## 가까운 후속 배정과 선행 관계', start)
    next_plan = ('## 다음 phase: 029\n\n'
                 '028의 세 고정판 task를 검수했고 N01 288절의 유지/재사용 부분을 승인했다. 여덟 issue를 doc-names 한 작업(gpt-6.1-sol/high)으로 통합한다. '
                 '정확 책임은 문구 네 묶음(모듈목록·knowledge·external·kind), setup/probe 실제 parser 공유, 초기화 JSON, CLI 표/JSON·네 검토단계/checkpoint의 검사 결속이다. '
                 '14최소 helper 반례와 모듈집합·부재 반례를 실제 정의에 연결하고 기존38문서시험과 직접 소비 단언을 유지한다.\n\n'
                 'doc_code/test_doc_code·문서·공식미러/캐시와 최종 관련 선택이 겹쳐 단일 소유가 필요하다. parser 추출을 포함한 정확26쓰기 경로만 허용하며 제품 schema·권한·도메인 의미는 바꾸지 않는다. '
                 '현재 결과만으로 충분한 이름 조사는 다시 배정하지 않는다.029가 최종판의 양쪽 같은 관련 실행과 미러/skill-only를 완결한 뒤 manager가 여덟 발견의 해소를 판단한다. '
                 '그 뒤 requirement-state의 구체적 남김과 최종판 연결로 진행하며, L01 외부결정과 전체 관문은 별도로 유지한다.\n\n')
    plan = plan[:start] + result + '\n\n' + next_plan + plan[end:]
    old_group = '**027 manager의 묶음 결정:** 027의 공유 수리·미러·관련 회귀를 검수했다.028에서는 나머지 N01을 기존288절 목록과 실제 소비 경계로 세 읽기 묶음에 나눈다. 제품 수정/실행이 없어 동일판본으로 병렬화하며, 새 공백이 나오면 공유 helper와 미러/회귀를 후속 한 작업에 모은다. L01 외부 결정·최종 관문과 이미 닫힌 N02/N03는 별도로 보존한다.'
    new_group = '**028 manager의 묶음 결정:** 세 독립 조사가 끝났으므로029는 공통 helper·parser 소비·문구·미러와 관련 회귀를 한 번에 통합한다. 여덟 발견을 문서 번호별 phase로 나누지 않는다. 각 수리의 정상/반례와 기존 단언이 구체적으로 있어 새 장기 조사 없이 한 세션의 구현·검증·보고로 닫을 수 있다. 별도 독립 조사는 현재 가까운 수리의 선행 조건이 아니므로 추가하지 않는다. L01·최종관문과 기존 승인 성질은 유지한다.'
    assert old_group in plan
    plan = plan.replace(old_group, new_group)
    lines = plan.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('| G1/G3 나머지 문서·정책 |'):
            lines[i] = '| G1/G3 나머지 문서·정책 | P01~P11과026~027 정책/N02/N03의 승인 성질을 유지한다.028에서 N01 판정을 마쳤으며 여덟 문구/검사 issue는029의 한 통합 작업이 맡는다. 명시 소비 없는 instance의 제거 가능성 판단은 기존 남김으로 유지한다. | 실제 schema/parser/생산·소비에 결속하고 양쪽 관련 검사를 고정판에서 완료한다.025의 마지막 AST 소비자/네 helper 제거는 유지하며 제거 수나14보강절을 전체 의미 완료율/독립14작업으로 읽지 않는다. L01과 최종 관문은 별도다. |'
    (RUN / 'plan.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    seams = (O / 'seams.md.before').read_text(encoding='utf-8-sig').rstrip() + '\n\n'
    seams += ('028의 고정판 판정을 검수했다.029는 기존 setup/probe parser의 인자·기본값·오류 의미를 보존하며 main과 문서 검사가 같은 실제 정의를 소비하게 한다. '
              'configuration/control·knowledge/external·stage/checkpoint·identity_modules의 정본은 기존 코드이며 문서용 별도 제품 schema를 만들지 않는다. '
              '문구/helper/필요한 parser 추출·미러·관련 실제 소비를 한 task가 함께 맡으므로 S항목과 provides/uses를 추가하지 않는다. '
              '구현/권한의 새 의미가 필요하면 정확 반례로 반환한다.\n')
    (RUN / 'seams.md').write_text(seams, encoding='utf-8')
    diff = ''
    for n in ('context.md', 'plan.md', 'seams.md'):
        before = (O / (n + '.before')).read_text(encoding='utf-8-sig')
        after = (RUN / n).read_text(encoding='utf-8-sig')
        diff += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=n + '.before', tofile=n))
    (O / 'common-docs.diff').write_text(diff, encoding='utf-8')
    objective = 'run:phases/029/tasks/doc-names/objective.md'
    evidence = ['run:phases/028/manager-evidence/verification.json', 'run:phases/028/manager-evidence/review.md']
    mapping = {
        ('operator-names', 'F1'): ('A3', '실제 두 parser 선언과 타도구 flag 반례를 확인했다. main과 helper의 공유 정의·정상/반려 연결을029에 배정한다.'),
        ('operator-names', 'F2'): ('A3', '실제 config/GRANT 반려와 문서helper 빈 진단을 확인했다. 지정 예제와 부재 검사를 실제 정의에 결속한다.'),
        ('operator-names', 'F3'): ('A2', '문장7/10과 실제14/17·생산자 전건 해시의 차이를 확인했다. 문구와 실제 집합 비교를 수리한다.'),
        ('cli-control-names', 'F1'): ('A2', '기존ID import 반려·새replacement·현재formal 재사용·withdrawn 예외를 실제 코드/소비 단언에서 확인했다. 문구와 최종 관련 실행에 반영한다.'),
        ('cli-control-names', 'F2'): ('A2', 'prepared 전송표지와 HTTP결과 세 분기 및 기존 직접 단언을 확인했다. execution.running과 구별한 문구 수리를 맡긴다.'),
        ('cli-control-names', 'F3'): ('A4', '다섯 최소 변형의 helper 거짓통과와 실제 정의 반려를 확인했다. 상태표·설정·query·완전knowledge예제만 결속한다.'),
        ('role-glossary-names', 'F1'): ('A2', '실제 action_schema의TEXT와 활성/같은묶음 제안 수신 검사를 확인했다. 동적enum 설명을 교정하고 runtime 의미는 유지한다.'),
        ('role-glossary-names', 'F2'): ('A4', 'CLI 네단계/checkpoint의 다섯 반례와 실제 owner를 확인했다.027 검사와 현재CLI 좌표의 차이를 보존하며 좁은 결속/부재검사를 추가한다.'),
    }
    reports = []; dispositions = []
    for t in TASKS:
        rp = read(RUN / 'phases/028/tasks' / t / 'report.json')
        reports.append(dict(task=t, state='read', detail=f'{t} report 전문과 A1~A4를 검수했고 report 형식 검사를 통과했다. 배정된 조사 complete를 승인하며 issue의 제품 수리는029로 넘긴다. 새 제품 실행은 없다.',
                            evidence=[f'run:phases/028/tasks/{t}/report.json', f'run:phases/028/manager-evidence/check-{t}.txt', *evidence]))
        for f in rp['findings']:
            if (t, f['id']) in mapping:
                a, reason = mapping[(t, f['id'])]
                dispositions.append(dict(item=f'028/{t}/{f["id"]}', action='carry',
                                         destination=[objective + '#' + a, 'run:context.md#C10'], reason=reason,
                                         evidence=[*f['evidence'], 'run:phases/028/manager-evidence/decisive-sources.json', *evidence]))
            else:
                assert t == 'role-glossary-names' and f['id'] == 'F3'
                dispositions.append(dict(item=f'028/{t}/{f["id"]}', action='resolve', destination=['run:context.md#C10', 'run:context.md#C12'],
                                         reason='195절/2675소스/원task 보존과 기존38문서row의 한정 재사용을 검산했다. 용어집 보편 개념과 구현 이름을 동의어로 강제하지 않으며 새 runtime 결함이나 전체G 성공으로 올리지 않는다.', evidence=[*f['evidence'], *evidence]))
    reasons = {
        'C2': '028 세 조사 완료와 실제 검수 수치·한계·여덟 후속issue를 추가했다. 기존 이력은 보존했다.',
        'C5': '028 독립 조사 예정 문단을 완료 상태와029 단일소유로 교체했다. 공유 helper/미러/캐시 중첩과 실제 parser의 좁은 추출 책임을 명시하고 자원 규칙은 유지했다.',
        'C8': '029 task의 사용자 지정 gpt-6.1-sol/high 승계를 추가했다. manager/제품 모델은 변경하지 않았다.',
        'C9': '028 정적 재사용의 실제판본·범위를 기록하고 기존 직접소비 단언의 새실행을029 책임으로 구분했다. PR 전체 종결로 확대하지 않았다.',
        'C10': 'N01 유지/재사용 판정과 여덟 수리 책임을 현재로 갱신했다. 이전 승인 문장과 L01/byte 미충족을 보존했다.',
        'C12': '제품 불변과 원task92파일의 직접추적·로컬 행정수신 구분을 추가했다. 기존 dirty/untracked를 포함하지 않는다.',
    }
    updates = [dict(item=c, action='amend', destination=['run:context.md#' + c], reason=reason,
                    evidence=[*evidence, 'run:phases/028/manager-evidence/common-docs.diff', objective]) for c, reason in reasons.items()]
    manager = dict(next='029', decision=('세 report의 A1~A4 complete를 승인한다. 현재2675소스·원task92파일 불변, 정확288절과현재좌표/정의118파일·기존38문서row/875Python을 검산했다. '
                   '문구4묶음과 검사 공백의 issue8개가 실제 코드/원관찰에 근거하므로 개발 완료를 선언하지 않는다. role F3의 한정재사용 사실만 종결한다. '
                   '029 doc-names가 실제 parser·schema·소비 단언을 이용해 문구·공유helper·미러·최종 관련 회귀를 통합한다. '
                   '동일 doc_code/test_doc_code와 미러/캐시가 겹쳐 구현을 병렬화하지 않으며 완료된288절 조사를 반복하지 않는다. '
                   '두 도구의 parser 추출 외 runtime/권한/도메인 의미는 바꾸지 않는다. '
                   'G1~G8·역사실패·L01 외부결정/byte미충족·symlink미검사·기본전체/freshT3/전수변이/G7최종판/G8review를 유지한다. '
                   '공용 diff의 의미 변경은 context_updates와review에 기록했다. 이번에는 제품 변경 없이 원task자료와관리인계·기억만 직접추적하며 handoff 통과/게시 후 정확파일을 커밋하고 push하지 않는다.'),
                   reports=reports, dispositions=dispositions, context_updates=updates,
                   plan_update='028의 조사 결과를 추가하고 다음 phase를029 단일 통합수리로 변경했다. 여덟issue의 문구·공유helper·두parser·미러/관련실행 책임과 종료조건을 지정했다. 완료된 이름 조사는 재배정하지 않으며 기존의 의미/PR 질문·외부결정·최종관문 선행관계를 유지했다.',
                   seam_updates=[], completion=None)
    save(RUN / 'phases/028/manager.pending.json', manager)
    print('Prepared 029/doc-names; 9 dispositions; 6 context updates; product writes 0 by manager.')

if __name__ == '__main__':
    main()
