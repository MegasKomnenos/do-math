"""Prepare the next bounded assignments and current shared knowledge."""
from collections import Counter
import difflib
import json
from pathlib import Path
from verify import R, RUN, O, read, save

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8')

def append_section(text, section, paragraph):
    start = text.index('## ' + section + ' ')
    end = text.find('\n## ', start + 1)
    if end == -1: end = len(text)
    return text[:end].rstrip() + '\n\n' + paragraph + '\n\n' + text[end:].lstrip()

def main():
    next_dir = RUN / 'phases/028'
    assert not (RUN / 'phases/027/manager.json').exists()
    assert not next_dir.exists(), 'Do not overwrite an already prepared phase'
    next_dir.mkdir()
    (next_dir / 'logs').mkdir()
    packet = next(p for p in read(RUN / 'phases/001/tasks/document-closeout/evidence/followup-packets.json')['packets'] if p['id'] == 'N01')
    groups = [
        ('operator-names', [(1, 46), (269, 288)], '운전·초기화 문서의 이름', 'SKILL/README와 초기화 두 문서', '역할 읽기 표·명령/경로·초기화 채택과 효율/정비 이름을 판정한다. Win32_Process·PT0S·FileRenameInfoEx는 외부 이름/표현의 현 소유와 기존 OS 근거를 연결하고 Python 이름 부재를 제품 결함으로 만들지 않는다.026 정책 다섯 의미와027 기본 방침/연결 정책·probe 교정은 지정 문장을 재사용하며 새 의미 감사를 반복하지 않는다.'),
        ('cli-control-names', [(209, 235)], 'CLI 제어·조회 이름', 'CLI-실행-계약 도입부터 export까지', '반환/종료 코드·상태 enum·설정·명령·구조화 decision/source/knowledge/trust/external/conversation과 조회의 이름/조합을 실제 해당 parser·schema·생산자·소비자에 연결한다. needs_revision은 과제 상태가 아니라는 명시 음성 예시를 보존한다. P03/P06/P08/P10 및 정책/연결의 이미 검수한 정확 문장은 근거를 재사용하고 한 절 전체로 확대하지 않는다.'),
        ('role-glossary-names', [(47, 208), (236, 268)], '역할 입력·산출과 용어 이름', 'GLOSSARY와 CLI의 AI 실행 입력부터 끝까지', '용어집의 개념 표기(F/U 등)와 실제 코드 이름을 구별한다. CLI 역할별 주 JSON·동적 단계·보조 파일·제출/복구·판정/대기 설명의 이름/조합을 정확 역할과 현재 schema/소비자에 연결한다. N01-237/260의 지정 재시도·운영처분 문장은024 근거를 재사용하고 남은 문장만 판정한다. P01~P11/PURE의 실제 반환 교체를 재구현하지 않는다.027의 단계/부분 예제 검사 범위가 다른 문서까지 자동 확장됐다고 보지 않는다.')
    ]
    assignments = []
    all_ids = []
    tasks = []
    common_inputs = [
        'run:sources/user-decisions.md', 'run:sources/model-policy-2026-10-14.md', 'run:sources/document-batching-2026-10-14.md',
        'run:phases/028/assignments.json', 'run:phases/027/manager-evidence/source-inspected.json', 'run:phases/027/manager-evidence/verification.json', 'run:phases/027/manager-evidence/review.md',
        'run:phases/027/tasks/doc-policy/report.json', 'run:phases/027/tasks/doc-policy/evidence/c3/report.json',
        'run:phases/001/tasks/document-closeout/evidence/followup-packets.json', 'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json', 'run:phases/001/tasks/document-closeout/evidence/source-census.json',
        'run:phases/026/manager-evidence/review.md',
        'repo:.claude/skills/do-math/AGENTS.md', 'repo:.claude/skills/do-math/scripts/tests/시험-지침.md', 'repo:.claude/skills/do-math/scripts/이음새-정본.md',
        'repo:.claude/skills/do-math/scripts/tests/support/doc_code.py', 'repo:.claude/skills/do-math/scripts/tests/structure/test_doc_code.py',
        'repo:docs/do-math/시험-재편-2026-09-29/설계.md', 'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md'
    ]
    for task_id, ranges, title, scope, special in groups:
        slices = [s for s in packet['required_slices'] if any(lo <= int(s['id'].split('-')[1]) <= hi for lo,hi in ranges)]
        docs = sorted({s['document'] for s in slices})
        all_ids += [s['id'] for s in slices]
        assignments.append(dict(task=task_id, title=title, ranges=ranges, slice_count=len(slices), historical_inline_occurrences=sum(s['candidate_occurrences'] for s in slices), documents=docs, slices=[{k:s[k] for k in ('id','document','start_line','end_line','heading')} for s in slices]))
        inputs = common_inputs + docs
        if task_id == 'operator-names':
            inputs += ['run:phases/026/tasks/policy-semantics/evidence/policy-decisions.json', 'run:phases/026/tasks/policy-semantics/evidence/test-bindings.json', 'run:phases/027/tasks/doc-policy/evidence/changes-final.diff']
        elif task_id == 'cli-control-names':
            inputs += ['run:phases/023/manager-evidence/review.md', 'run:phases/025/manager-evidence/review.md', 'run:phases/026/tasks/policy-semantics/evidence/policy-decisions.json']
        else:
            inputs += ['run:phases/022/tasks/review-delivery/evidence/section-name-decisions.json', 'run:phases/024/manager-evidence/section-check.json', 'run:phases/026/tasks/role-contract-names/evidence/review.md']
        tasks.append(dict(id=task_id, model='gpt-6.1-sol', effort='high', inputs=inputs, writes=[], provides=[], uses=[]))
        d = next_dir / 'tasks' / task_id
        (d / 'evidence').mkdir(parents=True)
        range_text = ', '.join(f'N01-{lo:03d}~N01-{hi:03d}' for lo,hi in ranges)
        objective = f'''## 목적과 역할

027의 공유 문서 검사 수리 뒤 고정된 현재판에서 N01의 남은 이름 판정을 마친다. 담당은 {scope}, 원 packet 좌표는 {range_text}의 {len(slices)}절이다. 정확 목록은 run:phases/028/assignments.json의 자기 task 행이다. 같은 phase의 다른 두 task와 읽기만 공유하고 자기 report/evidence에만 쓴다. 전체 의미 재감사나 제품 수정 없는 최종 review가 아니라, G1/G3의 한정된 미판정 이름·조합을 끝내고 실제 수리 필요분을 통합자에게 주는 work다.

## 완료 조건

### A1 배정 모집단과 현재 좌표

027 manager source-inspected와 시작 소스를 대조하고 차이를 기록한다. 자기 원 slice 전부를 현재 문서의 제목·행·SHA와 연결해 누락/중복을 확인한다. 과거 행번호를 현재 위치로 가정하지 않는다. inline 이름뿐 아니라 표와 명령/JSON 코드펜스, 산문의 실제 이름 주장을 읽고 모집단을 확정한다. 이름 없는 절도 이유를 적는다. 조사표는 자기 evidence이며 새 제품 정본이 아니다. 입력 전부를 stdout에 쏟지 않고 자기 절과 필요한 정의를 나눠 읽는다.

### A2 소유와 조합의 판정

현재 각 이름/조합에 실제 소유자·역할·입출력·정의/소비 위치 또는 구체적인 비코드·외부·파일명·명시 음성 예시 사유를 붙인다. 단어가 전체 코드 어딘가에 있다는 이유로 승인하지 않는다. 같은 정의를 쓰는 반복은 근거를 공유해도 원 출현 좌표를 빠뜨리지 않는다. {special}

P01~P11, B132~B134,026~027의 이미 닫힌 정확 성질은 현재 문장/정의/시험 SHA와 기존 manager 근거를 대조해 재사용한다. 동일 owner의 다른 문장까지 인증하지 않는다. 문서와 구현의 불일치는 원문·기대·실제 정의/최소 반례로 issue에 남기고, 정의만 확인돼 실행 의미가 미정인 부분은 질문을 구체화한다. 알 수 없는 항목을 유지로 일괄 처리하지 않는다.

### A3 기존 검사 범위와 필요한 보강

담당 문장에 적용되는 현재 doc_code 및 실제 schema/parser/소비 시험의 단언을 확인한다. 잘못된 역할/단계의 동명 필드, 오타·허용되지 않는 조합이 무엇에 의해 반려되는지 원문 수준으로 대조한다. 모든 사례에 새 시험을 만들지 않는다.027 c3의 정확38문서 row와875Python SHA를 확인해 그 검사가 맡은 성질만 재사용하며 새 실행으로 기록하지 않는다. 코드펜스는 완전 응답·부분 객체·명령 synopsis를 구별한다. 검사 밖의 실제 위험은 가장 작은 정상/반례와 영향 helper·소비 시험·문서 좌표를 제시한다. 새 반례를 실행하지 않았다면 정적 판단이라고 명시한다.

### A4 유한한 인도와 보존

배정 절 전부에 유지/기존 근거 재사용/문구 수정/검사 보강/정확 미결 중 하나의 근거 있는 결론을 남긴다. source profiles와 결정표·검사 결속표·간결한 review를 자기 evidence에 쓰되 같은 정보를 여러 표로 중복하지 않는다. 후속이 있으면 같은 helper/미러/실제 소비 단위로 묶을 수 있게 정확 파일·성질·완료 조건을 제시한다. 없으면 근거로 닫는다. 범위 밖 새 우려를 끝없는 전수 조사로 확장하지 않는다. 시작/끝 소스 불변과 사용한 원보고 SHA를 기록하고 report 검사에 통과한다.

## 판단과 경계

제품 writes는 비어 있다. 제품·시험·공용 문서·이전 report/evidence·미러·캐시·index·graphify를 고치지 않는다. 다른028 task의 작업 중 evidence를 읽거나 기다리지 않는다. 고정 원자료의 공유 읽기와 자기 evidence만 사용하는 표준 라이브러리 분석은 허용한다. 제품 import가 필요한 순수 schema/문서 검사 관찰은 -B를 쓰고 어떤 함수를 호출했는지 기록하며 OS/네트워크/저장/모델 호출이나 테스트 runner를 실행하지 않는다. 공식 회귀·공유 캐시·미러 생성은 후속 통합 work가 맡는다. 관찰용 wrapper가 제품 정의를 복제하거나 현재 결과를 기대값으로 삼지 않게 한다.

상위 protocol·G1~G8과 원래 의무를 유지한다. L01 Q1/Q2, UTF-8 byte 요구와 미충족, symlink1314 실제 반려 미검사, 기본 전체/freshT3/전수변이/최종 review는 이 이름 판정의 완료와 별개다. 임의로 운전 host·출력 단위·권한을 정하거나 새 유료·예약·Lean·학술 실행을 배정하지 않는다. 기존 명시 제외와 실패 기록은 보존한다. Git commit/reset/checkout/push는 manager만 맡는다.

## 검증 방법

cwd C:/math, Python C:/Users/wogud/AppData/Local/Programs/Python/Python312/python.exe. 원 packet은 자기 ranges만 선택하고 current 문서·정의·검사 본문으로 확인한다. 분석 스크립트는 자기 evidence에서만 실행하고 자기 산출에만 쓴다. 027 source-inspected와 시작/종료 SHA, slice 집합의 정확 일치·정의/근거 경로의 존재·현재 인용·재사용한 공식 row/판본을 검산한다. 구체 수정 후보의 정상/반례는 현재 정의·해당 단언과 대조한다. 기존 문제의 해결이나 실제 연결 성공을 새로 주장하려면 그 원자료를 확인한다. 자료가 없으면 원위치와 영향을 기록한다.

새 제품 시험을 실행하지 않으므로 새 통과 수는 없다. 후속 manager가 세 결과의288절 합집합과 차이·수리 후보를 검수하고 공유 수정/미러/공식 회귀를 한 work로 묶는다. 자기 검증 뒤 `python services/continuous-development/check.py report C:/math C:/math/docs/do-math/continuous-development-2026-10-13 028 {task_id}`를 지정 Python으로 실행한다.
'''
        write(d / 'objective.md', objective)
    assert len(all_ids) == len(set(all_ids)) == 288
    assert set(all_ids) == {s['id'] for s in packet['required_slices']}
    write(next_dir / 'assignments.json', json.dumps(dict(note='Historical N01 coordinates for bounded allocation, not a product schema or current semantic approval. Current source/heading verification belongs to each task.', tasks=assignments), ensure_ascii=False, indent=2))
    write(next_dir / 'phase.json', json.dumps(dict(kind='work', purpose='027 수리판을 고정하고 N01의 남은 이름·조합을 운전/초기화, CLI 제어/조회, 역할/용어의 독립 읽기 범위로 판정해 필요한 공유 수리만 반환한다.', tasks=tasks), ensure_ascii=False, indent=2))

    context = (O / 'context.md.before').read_text(encoding='utf-8-sig')
    summary = 'phase 027 doc-policy의 A1~A5 complete를 검수했다. 시작2675소스는026 검수본과 같고 종료/현재 전건 SHA 일치 및 허용18변경(비캐시16·캐시2)을 확인했다. 최종 정본/미러 같은134선택·고유row가 전부passed·exit0이며 각875Python과 전후판본을 대조했다. 실제 저장/CLI 반환각84개에서 기본방침3/2/17·명시우선·해시와 연결4세대의 양쪽 정책/정확ref, probe 정상/HOLD/조회오류를 검산했다. 기존33문서시험과 나머지 helper/단언을 보존했다. 원task196파일은 불변이고 초기3집중실패·TEMP표기1실패·보조검산2오류는 역사 기록으로 유지한다. 근거는 run:phases/027/manager-evidence/verification.json·return-check.json·review.md다. 지정 범위 완료이며 전체G 완료가 아니다.'
    context = append_section(context, 'C2', summary)
    old = 'phase 001~026의 task 세션은 종료됐다.026의 고정판 세 조사를 검수했고027은 doc-policy 단일 통합 work다. 문구 두 곳·초기화/연결 정책 직접 단언·역할 단계/부분 JSON/operator mode 검사와 공식 미러/관련 회귀를 한 담당자가 소유한다. 같은 doc_code/structure·미러·캐시 및 최종 판본을 공유하므로 수리를 병렬 task로 쪼개지 않는다. N01 나머지 이름 조사는 그 입력/소비가 바뀌는 동안 병행하지 않고 수리 검수 뒤 한정한다. 공식 검사는 jobs1·전체worker3 이하·한 묶음씩·소스 고정을 유지한다.'
    new = 'phase 001~027 task 세션은 종료됐고027 통합 수리를 검수했다.028은 고정판 N01의 이름 판정을 operator-names(66절), cli-control-names(27절), role-glossary-names(195절)의 세 독립 읽기 task로 배정한다. 정확288절 합집합은028 assignments.json에 있고 작은 용어집 절162개를 개별 작업으로 나누지 않는다. 제품 쓰기·공식 시험·미러/캐시 갱신·같은 phase 결과 소비가 없어 병렬 가능하다. 결과가 요구하는 공유 helper/문서/미러 수리는 후속 통합 work가 맡는다. 공식 검사에는 jobs1·전체worker3 이하·한 묶음씩·소스 고정을 유지한다.'
    assert old in context
    context = context.replace(old, new)
    context = append_section(context, 'C5', '027의 첫 관련실행은 C:/temp와 실제 C:/Temp의 문자열 차이로 정확 reconcile 단언이 실패했다. 같은 제품과 단언에서 전용 TEMP를 Path.resolve의 실제 표기로 지정한 새 실행은 통과했다. 후속에도 저장소 밖 짧은 전용 TEMP의 정규 표기와 상위 Git 부재를 확인한다. 원실패를 숨기거나 경로 단언을 약화하지 않는다. 근거는027 원 final-c.stderr와 manager 검수다.')
    context = append_section(context, 'C8', '027의 gpt-6.1-sol/high 작업을 검수했다.028의 세 독립 조사에도 같은 model/effort를 명시하며 manager와 제품 공급자 모델 설정은 바꾸지 않는다.')
    context = append_section(context, 'C10', '027에서026 policy F2/F3와 role F1/F2의 지정 남김을 닫았다. 기본방침 생성/명시우선 문구와 probe 정상/조기 반환 문구를 교정했고, 공개 저장/restart의 독립 기대·4세대 양쪽 정책과 정확 ref를 검수했다. initial/organize의 지정 출력 문장, 두 부분 JSON과 operator mode는 실제 stage_schema/extension_schema/parser에 연결돼 오타·타단계 차용·누락 반례를 반려한다. 기존33문서시험과 P/PURE/소유 helper는 보존했다. 문서 전반의 자연어 소유 추론으로 확대하지 않는다.028은 N01의288절에서 이미 닫힌 정확 문장을 재사용하고 나머지 이름/조합만 판정한다. N02/N03의 승인된 부분을 다시 조사하지 않으며 L01 Q1/Q2·원문byte 미충족은 유지한다. 근거는027 manager verification.json·return-check.json·review.md와028 assignments/objectives다.')
    context = append_section(context, 'C11', '027의 양쪽134passed는 지정 관련 회귀다. symlink 시험은 선택에 없고 기존1314 실제 반려 미검사는 그대로다. 기본 전체 G4·freshT3 G5·전수변이 G6·G7 최종판 연결·G8 최종review는 남는다.028의 고정판 이름 판정은 이 실행 관문을 대신하지 않는다.')
    context = append_section(context, 'C12', '027의18변경 밖 소스는026 시작판과 같아 runtime/schema/choices/corpus 및 기존 승인 하위 성질을 유지한다. 문구 두 곳이 바꾸는 향후 prompt/설치 문서 hash를 과거 모델 독해·전판본 성공으로 인증하지 않는다. 이번 검수한16비캐시 문서/시험/지침/미러 경로를 관리 커밋으로 마감한다. 원task196파일과16제품 원바이트는 manager-evidence/raw-evidence.zip에 보존하고 선별 원경로 및 전건 SHA는 preservation.json에 둔다. 압축으로만 추적하는 중복 소스 snapshot의 원경로와 진행 로그·stage/commit 행정 수신은 로컬 보관으로 정리 시 사라질 수 있다. 압축은 복원 지시가 아니다.028 배정·관리/기억 추가는 검수한 제품판본을 바꾸지 않는다.')
    write(RUN / 'context.md', context)
    plan = (O / 'plan.md.before').read_text(encoding='utf-8-sig')
    plan = plan.replace('## phase 001~026의 결과와 현재 상태', '## phase 001~027의 결과와 현재 상태')
    i, j = plan.index('## 다음 phase: 027'), plan.index('## 가까운 후속 배정과 선행 관계')
    plan = plan[:i] + summary + '\n\n## 다음 phase: 028\n\n027의 문구·저장 단언·단계/부분 JSON/operator mode 수리를 승인하고 N01의 남은 이름 판정을 고정판에서 수행한다. 세 task는 gpt-6.1-sol/high이며 writes/provides/uses는 모두 비어 있다. operator-names는 SKILL/README·초기화 두 문서의66절, cli-control-names는 CLI 제어/조회27절, role-glossary-names는 용어집162절과 CLI 입력/산출33절을 맡는다.288절의 정확 목록은028 assignments.json에 있으며 역사 행번호는 현재 원문에 다시 연결한다.\n\n이미 검수한 P01~P11/PURE·026 정책·027 문장/검사 성질은 같은 문장/정의/시험 판본에서 재사용한다. 각 task는 자기 evidence만 쓰고 새 공식 시험·미러·공유 캐시를 사용하지 않으므로 독립 병렬 진행한다. 이름의 소유·조합/예시 판정과 필요한 최소 수리 목록으로 끝내며, 구현 배정용 장기 조사나 전체 의미 재감사로 넓히지 않는다. 결과를 검수한 manager가 공통 helper·문서·미러·관련 시험의 수정 후보를 한 work로 통합한다. 수리가 없으면 requirement-state의 구체적 남김과 최종판 연결로 이어 간다.\n\n' + plan[j:]
    old_batch = '**026 manager의 묶음 결정:** 독립 조사는 끝났고 수정 후보가 문구 두 곳·정책 단언 두 경계·문서 검사 세 축으로 한정됐다. 이를027 단일 work에 묶어 공유 helper·미러와 관련 최종 회귀를 통합한다. 각 문서마다 별도 phase를 만들지 않고 N01의 다른 의미 질문/L01 외부 결정/최종 관문은 보존한다.'
    new_batch = '**027 manager의 묶음 결정:** 027의 공유 수리·미러·관련 회귀를 검수했다.028에서는 나머지 N01을 기존288절 목록과 실제 소비 경계로 세 읽기 묶음에 나눈다. 제품 수정/실행이 없어 동일판본으로 병렬화하며, 새 공백이 나오면 공유 helper와 미러/회귀를 후속 한 작업에 모은다. L01 외부 결정·최종 관문과 이미 닫힌 N02/N03는 별도로 보존한다.'
    assert old_batch in plan
    plan = plan.replace(old_batch, new_batch)
    plan = plan.replace('026의 N03 이름 유지 판정을 재사용하며 문구/검사 공백은027에 남긴다.', '026 유지 판정과027 문구/검사 수리를 재사용한다.')
    plan = plan.replace('027에서 문구 두 곳·정책 저장 단언·역할 단계/JSON/operator mode 검사만 통합 수리하며 N01의 다른 이름은 유지한다.', '027의 문구 두 곳·정책 저장·역할 단계/JSON/operator mode 수리를 검수했다.028에서 N01 나머지 이름/조합을 고정판으로 판정한다.')
    write(RUN / 'plan.md', plan)
    seams = (O / 'seams.md.before').read_text(encoding='utf-8-sig')
    write(RUN / 'seams.md', seams.rstrip() + '\n\n027의 기존 정책 저장·probe 분기와 stage/extension/parser 경계 소비를 검수했다.028은 같은 고정판의 이름·조합·기존 검사 범위를 읽는 세 독립 task다. 새 제품 인터페이스를 제공/소비하거나 제품을 수정하지 않으며 S항목 개정과 provides/uses는 없다. 코드/공유 schema가 계속 정본이고 조사표는 제품 정의가 아니다. 발견된 수리의 실제 연결 검증은 다음 통합 work가 맡는다.')
    changes = []
    for name in ('context.md', 'plan.md', 'seams.md'):
        a = (O / (name + '.before')).read_text(encoding='utf-8-sig').splitlines(True)
        b = (RUN / name).read_text(encoding='utf-8-sig').splitlines(True)
        changes.extend(difflib.unified_diff(a,b,fromfile='before/'+name,tofile='after/'+name))
    write(O / 'common-docs.diff', ''.join(changes))
    save('assignment-check.json', dict(total_slices=len(all_ids), unique_slices=len(set(all_ids)), historical_occurrences=sum(x['historical_inline_occurrences'] for x in assignments), partitions=[{k:v for k,v in x.items() if k != 'slices'} for x in assignments], no_product_writes=True, no_same_phase_result_dependencies=True, no_shared_test_processes=True))
    print(json.dumps({'next':'028', 'tasks':[{k:v for k,v in a.items() if k in ('task','ranges','slice_count','historical_inline_occurrences')} for a in assignments]}, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
