"""Write manager-owned current context and the next bounded work assignment."""
import difflib
import json
from pathlib import Path

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)

def main():
    original = {n: (RUN / n).read_text(encoding='utf-8') for n in ('context.md', 'plan.md', 'seams.md')}
    ctx = original['context.md']
    outcome = ('phase 008 document-recovery는 A1~A4 pass·A5 fail의 partial로 검수했다. '
               '현재2640파일과 task 종료 해시는 전건 같고30변경은 report/writes에 일치한다. '
               '8개 공식 실행의 선택/고유row/exit·소스 전후를 대조했으며 최종 정본110건은106passed·4failed, '
               '미러89건은85passed·4failed다. 두 최종 Python865파일은 현재와 같고 skip/error/미실행은 없다. '
               'P01 red2단언과 운영/복구·설치 지정 검사는 통과했으나 기존 CLI 함수 표기가 unowned field로 분류돼 '
               '전건 문서 검사4건이 실패한다. 현재/HEAD 원문과 당시 helper에서 같은 분류를 재현했고 '
               '현 함수 검사 표기로 해결 가능한 것을 확인했다. runtime124·smoke입력3·corpus102경로는 불변이며 '
               'Git raw/clean을 재확인했다. 검수 HEAD는12a751550dc06ac75cdc56058b622d8b621b21cd이고 '
               '근거는 run:phases/008/manager-evidence/verification.json 및 review.md다. '
               '부분 성공을 최종 전체 관문이나 제품 합격으로 확대하지 않는다.')
    ctx = replace_once(ctx, '## C3 현재 정본과 이력의 역할', outcome + '\n\n## C3 현재 정본과 이력의 역할')
    start = ctx.index('phase 001의 독립 분석 세 task와 phase 002~007의 단일 work task는 종료됐다.')
    end = ctx.index('\n\n', start)
    ctx = ctx[:start] + ('phase 001의 독립 분석 세 task와 phase 002~008의 단일 work task는 종료됐다. '
         '008의 P01 운영/복구와 N03-003 지정 문장 성과는 검수했으나 기존 CLI 함수 표기의4실패로 partial이다. '
         '009 document-callable 한 task가 해당 표기를 기존 함수 검사 경로로 바꾸고008 최종 관련 회귀·미러를 확인한다. '
         '공유 전건 문서 순회·비용 캐시·공식 미러 생성은 같은 판본을 요구하므로 나누어 실행하지 않는다. '
         '다른 G7 실연쇄도 설치 문서·shared cache/corpus를 사용하므로 이 짧은 수리 뒤 배정한다. '
         '후속 작업도 파일과 시험/캐시 독립성을 확인하며 고정판의 독립 읽기 검토는 병렬화할 수 있다.') + ctx[end:]
    ctx = replace_once(ctx, '현재는 phase 001 세 task와 phase 002~007 각 한 task의 report를 각각 새 manager가 검사했다.',
                       '현재는 phase 001 세 task와 phase 002~008 각 한 task의 report를 각각 새 manager가 검사했다.')
    ctx = replace_once(ctx, 'phase 007은 A1~A5 complete로 검수했다. 이전 partial report 자체는 수정하지 않는다.',
                       'phase 007은 A1~A5 complete로 검수했다. phase 008은 A1~A4를 승인하고 A5의 기존 문서4실패를009로 넘긴 partial이다. 이전 partial report 자체는 수정하지 않는다.')
    start = ctx.index('document-closeout은 실제 24문서')
    end = ctx.index('followup-packets.json의 P01~P11', start)
    ctx = ctx[:start] + ('''document-closeout의 원목록은 실제24문서(계약11 포함), inline 필드189회·lexical owner79개·노출 owner84개와 당시 AST34지점이다. 이 수는 역사 목록의 크기이며 현 의미 검증 완료율이 아니다.008에서 P01의 운영/복구6 AST지점을 실제 _context/포장 객체와 저장·물질화 파일 검사로 교체했다. operational_evidence와 recovery_materials의 동명 source를 구별하고 정상·restoration_error·checkpoint_source=null·live 부재·activity_continuations와 반환 사본/제품 입력 반례를 확인했다. 일반 재개의 result_source와 B130~B134 기존 성질을 유지하며, 마지막 소비가 없어진 checkpoint_source/recovery_source/checkpoint_files/recovered_output_files 단독 입력은 제거했다. defer 두 입력의 실제 문서 검사 담당과 오기/누락 반례도 확인했다. 근거는 run:phases/008/tasks/document-recovery/evidence/binding-review.md 및 run:phases/008/manager-evidence/review.md다.

독립-운영.md의 LIVE_INSTALLATION_ROOT 문장은008에서 현 bootstrap.main의 manifest.installation_root 또는 snapshot_root를 scheduled_operator.main의 installation_root 인자로 전달하는 경계로 교정했다. 기존 bootstrap-info2개는 양쪽 최종 보고에서 통과했다. 옛 전역 이름은 제품에 복원하지 않았으며 N03의 다른 절은 미검토다.

008 F1과 A5는 미해결이다. CLI-실행-계약의 공급자 절에 있는 bare dotted 함수명 provider_final.output_contract가 현/HEAD 문서 검사에서 unowned field로 분류돼 양쪽 각4검사가 실패했다.008의 P01 문장 범위 밖이었으므로 partial 보고를 승인한다.009는 이 표기를 기존 function_reference_issues가 실제 callable로 검사하는 명시 호출 표기로 교정하고 동일 관련 묶음을 새 판본으로 확인한다. unknown owner/defer 완화·상태 schema 추가·runtime 수리는 필요하지 않다. 근거는 run:phases/008/manager-evidence/verification.json의 callable_issue와 suites, run:phases/009/tasks/document-callable/objective.md다. P01/N03-003의 지정 성과를 보존하되 전건 관련 회귀 종료는009 뒤 판단한다.

''') + ctx[end:]
    ctx = replace_once(ctx, 'P01 운영/복구, P02 원자료/과제 결과, P03 실행 안내/설치를 구별하고',
                       'P01의 검수된 지정 성과와009의 회귀 남김, P02 원자료/과제 결과, P03 실행 안내/설치를 구별하고')
    ctx += ('\n008 F2의 보존 사실은 manager가 확인해 종결했다.008의 문서·시험 변경은 공급자 runtime124·smoke입력3·'
            'corpus102경로를 바꾸지 않았으므로 기존 실호출의 승인된 성질은 유지한다.007의 제품124파일 마감은 '
            '로컬 commit.json의 exit0 및 HEAD78d9c6d에서 확인했다.008 제품30경로(비용 캐시2 포함)는 '
            '문서4실패가 남아009 검증 뒤 커밋하며 현재 raw 바이트는008 manager-evidence의 archive로 보존한다. '
            '이번 커밋은 관리 기록·선별 원근거·009 배정·기억만 포함한다. 원바이트/추적 범위는 '
            'run:phases/008/manager-evidence/preservation.json에 둔다. G4~G6/G8의 새 최종 판본 검증과 '
            '나머지 G7 책임은 유지한다.\n')
    plan = original['plan.md']
    plan = replace_once(plan, '## phase 001~007의 결과와 현재 상태', '## phase 001~008의 결과와 현재 상태')
    plan = replace_once(plan, '최종 전체 관문은 아직 실행하지 않았다.',
                       '008은 운영/복구와 설치 지정 성과 A1~A4를 검수했지만 기존 CLI 함수 표기 때문에 A5가 실패한 partial이다. 최종 전체 관문은 아직 실행하지 않았다.')
    plan = replace_once(plan, '제품124파일은 관리 마감의 정확 stage·바이트 검증 뒤 커밋한다.',
                       '제품124파일은007 관리 마감의 정확 stage·바이트 검증 뒤 HEAD78d9c6d에 커밋됐다.')
    insertion = ('- 운영/복구 문서의 지정 성과와 관련 회귀 남김: run:phases/008/tasks/document-recovery/report.json 및 '
                 'manager-evidence/verification.json·review.md. 현재2640파일·허용30변경과8개 공식 실행을 대조했다. '
                 '정본110개106passed/4failed·미러89개85passed/4failed이며4실패는 기존 CLI 함수 표기다. '
                 'P01 정상/오류/null/부재 및 N03-003 지정 문장 성과는 보존하고 전건 회귀와 제품 커밋은009 뒤 판단한다.\n\n')
    plan = replace_once(plan, '분류는 완료율이 아니다.', insertion + '분류는 완료율이 아니다.')
    start = plan.index('## 다음 phase: 008')
    end = plan.index('## 가까운 후속 배정과 선행 관계', start)
    plan = plan[:start] + '''## 다음 phase: 009

단일 work task `document-callable`이 CLI-실행-계약의 provider_final.output_contract 표기를 기존 함수 검사 경로로 교정하고008의 A5 남김을 닫는다. 실제 callable과 명시 module.function(...) 검사는 이미 존재하므로 unknown/defer/schema/helper를 고치지 않는다. 정본110개·미러89개의008 최종 관련 선택을 새 문서 판본으로 확인하며 정확한4실패 ID의 passed 연결을 남긴다. 부분 성공인008 report는 그대로 보존한다.

task는 gpt-6.1-sol/high다. 쓰기는 해당 문서·공식 미러·비용 캐시로 닫는다. 실제 회귀와 생성이 같은 문서·캐시 판본에 의존해 한 task가 소유한다. 다른 G7 실연쇄도 설치 문서와 shared cache/corpus를 사용하므로 이 짧은 수리 뒤 배정한다. 정확한 A1~A3와 writes는 run:phases/009/tasks/document-callable/objective.md 및 phase.json에 있다.

''' + plan[end:]
    plan = replace_once(plan, '007의 지정 관련 회귀를 검수했고 공급자 변경 단위를 커밋한다. 다음은008의 문서·실제 반환 연결을 검수하고 G7의 개별 실제 연쇄 배정을 정한다.',
                       '007 공급자 변경 단위는 커밋됐고008 지정 성과를 검수했다.009가 전건 문서4실패를 해소하면008~009의 문서·시험 변경을 함께 마감하고 G7의 개별 실제 연쇄 배정을 정한다.')
    plan = replace_once(plan, '| G1/G3 문서 P01 | phase 008이 operational_evidence와 recovery_materials의 동명 result/checkpoint를 실제 생산자별로 결속하고 정상·restoration_error·null/부재 조건의 문서 지시와 반례를 확인한다. | B133 일반 재개 경계는 유지. doc_code/역할 입력 공유 파일을 단일 task가 수정한다. |',
                       '| G1/G3 문서 P01 및 전건 회귀 | 008의 운영/복구 실제 반환·파일·반례 성과는 검수했다.009가 기존 CLI 함수 표기를 교정하고 전건 관련 회귀4실패를 새 판본에서 닫는다. | B133/B132~B134 및008 단언 유지. 제품 커밋은009 검수 뒤. |')
    plan = replace_once(plan, '| G1/G8 문서 N03 확정 불일치 | phase 008이 독립-운영.md의 LIVE_INSTALLATION_ROOT 설명을 실제 installation_root 전달로 교정하고 기존 bootstrap-info 근거와 미러를 연결한다. | 해당 문서 절만 배정 가능하며 옛 전역 변수를 제품에 복원하지 않는다. |',
                       '| G1/G8 문서 N03 지정 문장 | 008에서 installation_root 전달 설명과 양쪽 bootstrap-info2건을 검수했다.009 뒤 같은 문서 변경 단위의 인도 근거에 연결한다. | 옛 전역은 복원하지 않는다. N03 다른 절은 계속 미검토. |')
    seams = original['seams.md'].replace('phase 002~007의 work는 종료됐다.', 'phase 002~008의 work는 종료됐다.', 1)
    seams += ('\n008의 운영/복구 및 설치 설명 지정 성과를 검수했으나 전건 문서 검사는 기존 CLI 함수 표기로4건 실패했다. '
              '009는 해당 표기를 function_reference_issues의 현 함수 표기 계약에 맞추는 문서 수리이며 '
              '제품 경계·오류·입력 의미를 바꾸지 않는다. provides/uses는 계속 빈 목록이고 새 S 항목은 없다. '
              '검수 근거는 run:phases/008/manager-evidence/review.md, 후속 책임은009 objective다.\n')
    for name, updated in (('context.md', ctx), ('plan.md', plan), ('seams.md', seams)):
        (RUN / name).write_text(updated, encoding='utf-8')
    (OUT / 'common-documents.diff').write_text(''.join(''.join(difflib.unified_diff(
        original[n].splitlines(keepends=True), (RUN / n).read_text(encoding='utf-8').splitlines(keepends=True),
        fromfile=n + ':before', tofile=n + ':after')) for n in original), encoding='utf-8')
    new = RUN / 'phases/009'
    (new / 'tasks/document-callable/evidence').mkdir(parents=True, exist_ok=True)
    (new / 'logs').mkdir(exist_ok=True)
    inputs = ['run:sources/user-decisions.md', 'run:sources/model-policy-2026-10-14.md',
              'run:phases/008/tasks/document-recovery/report.json',
              'run:phases/008/tasks/document-recovery/evidence/source-final.json',
              'run:phases/008/tasks/document-recovery/evidence/binding-review.md',
              'run:phases/008/manager-evidence/verification.json', 'run:phases/008/manager-evidence/review.md',
              'run:phases/008/manager-evidence/preservation.json',
              'repo:.claude/skills/do-math/AGENTS.md',
              'repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
              'repo:.claude/skills/do-math/references/CLI-실행-계약.md',
              'repo:.claude/skills/do-math/scripts/tests/support/doc_code.py',
              'repo:.claude/skills/do-math/scripts/tests/structure/test_doc_code.py',
              'repo:.claude/skills/do-math/scripts/do_math/provider_final.py']
    writes = [tree + '/skills/do-math/' + suffix for tree in ('.claude', '.agents')
              for suffix in ('references/CLI-실행-계약.md', 'scripts/tests/.timings.json')]
    write_json(new / 'phase.json', {'kind': 'work', 'purpose': 'CLI 함수 표기를 기존 callable 검사와 맞추고008의 최종 관련 회귀4실패를 해소한다.',
                'tasks': [{'id': 'document-callable', 'model': 'gpt-6.1-sol', 'effort': 'high',
                           'inputs': inputs, 'writes': writes, 'provides': [], 'uses': []}]})
    ev = ['run:phases/008/manager-evidence/verification.json', 'run:phases/008/manager-evidence/review.md']
    updates = [
        ('C2', '008의 실제 판본·8실행·A1~A4 성과와A5 실패를 추가한다. 기존 역사 결과와 전체 G 미충족은 보존한다.'),
        ('C5', '008 종료와009 단일 수리의 공유 문서/캐시/미러 독립성 판단으로 현재 배정을 교체한다. 슬롯·순차 검사 규칙은 유지한다.'),
        ('C8', '새 manager가008 partial을 검수했다는 수행 상태만 추가하며 사용자 모델 정책은 그대로 유지한다.'),
        ('C10', 'P01/N03-003의 예정 수리를 검수된 지정 성과로 갱신하고F1의 원인·009 처분을 추가한다. 역사 모집단·다른 패킷·L01·N03 나머지는 보존한다.'),
        ('C12', 'F2의runtime/corpus 불변·호출 재사용 조건과007 실제 커밋 확인을 추가한다.008 제품 마감 대기와 원바이트 보존, 최종 관문 책임을 유지한다.')]
    manager = {
        'next': '009',
        'decision': ('008 report를 전문으로 읽고 report 검사 후 현재 파일·원결과를 검수했다. A1~A4의 P01 실제 반환/파일 '
                     '결속과 N03-003 지정 문장 수리를 승인한다. A5는 정본106/110·미러85/89 통과이며 동일한4문서 '
                     '실패가 남아 partial이다. 실제 callable이 bare dotted 표기여서 상태 필드로 분류되며 HEAD 원문에서도 '
                     '같은 분류를 재현했다.008의 명시 범위를 넘지 않고 issue로 반환한 판단은 적절하다.009는 현 함수 '
                     '검사 표기를 사용하는 문서 수리와 최종 관련 회귀만 맡는다. 공유 문서·비용 캐시·미러에 의존해 '
                     '한 task로 소유하며 다른 G7 실연쇄는 이 짧은 수리 뒤 배정한다. 제품 runtime/corpus는 불변이다. '
                     '관리 기록과 원근거를 커밋하고 제품30변경은 archive로 보존해009 통과 뒤 함께 마감한다. '
                     '공용 문서 전후 차이를 common-documents.diff로 확인하며 C/G 의미와 나머지 미결을 보존한다. '
                     '직전은work이고 G1~G8 전체 충족 근거가 없으므로 종료하지 않는다.'),
        'reports': [{'task': 'document-recovery', 'state': 'read',
                     'detail': 'report 형식 검사exit0. A1~A4 pass·A5 fail의partial을 실제2640파일/30변경·8묶음과 대조했다. 같은4실패는009 A1~A3에서 수리·재검증한다.',
                     'evidence': ['run:phases/008/tasks/document-recovery/report.json', 'run:phases/008/manager-evidence/report-check.json', *ev]}],
        'dispositions': [
            {'item': '008/document-recovery/F1', 'action': 'carry',
             'destination': ['run:context.md#C10', 'run:plan.md', 'run:phases/009/tasks/document-callable/objective.md'],
             'reason': '현/HEAD 표기와 helper에서 재현한 유효한 문서 분류 실패다.008의P01 문장 경계 밖이었으며009가 기존 명시 callable 표기로 교정하고4실패를 최종 관련 묶음에서 확인한다.', 'evidence': ev},
            {'item': '008/document-recovery/F2', 'action': 'resolve',
             'destination': ['run:context.md#C12', 'run:plan.md'],
             'reason': 'runtime124·smoke입력3·corpus102경로의 현재/시작 동등과 실제Git raw/clean을 확인했다. 이전 공급자 호출의 한정 성질은 유지하되 바뀐 문서/시험의 최종G4~G6/G8과 나머지G7 책임은 남는다.',
             'evidence': [*ev, 'run:phases/008/manager-evidence/git-clean-observation.json']}],
        'context_updates': [{'item': ident, 'action': 'amend', 'destination': ['run:context.md#' + ident],
                             'reason': reason, 'evidence': [*ev, 'run:phases/008/manager-evidence/common-documents.diff']} for ident, reason in updates],
        'plan_update': '008의지정 성과·partial과007 실제 커밋을 반영하고 다음을009 document-callable로 변경했다. P01/N03-003의확인된 의미 검증을 보존하며 관련 회귀4실패 및제품 마감만009로 넘긴다. 다른 문서/의미 질문·G7 개별실연쇄·T4 보고·최종 일반/fresh T3/변이/review의순서와 책임은 유지한다.',
        'seam_updates': [], 'completion': None}
    write_json(RUN / 'phases/008/manager.pending.json', manager)

if __name__ == '__main__':
    main()
