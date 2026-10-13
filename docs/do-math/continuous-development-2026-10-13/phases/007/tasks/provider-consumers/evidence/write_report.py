"""Build the protocol submission from completed, checked evidence."""
import subprocess
from audit_delivery import read
from run_command import EVIDENCE, write_json

prefix = 'run:phases/007/tasks/provider-consumers/evidence/'
def refs(*names):
    return [prefix + name for name in names]

verification = read(EVIDENCE / 'verification-final.json')
changes = {
    'support/provider_runs.py': '실제 CLI argv의 원 schema/전송 schema를 cli_schemas에서 구분하고 제품 output_contract와 대조한다. cli_final도 이 helper를 사용하며 명시 native stdout/final의 자동 재작성은 하지 않는다.',
    'support/operator_finish_scene.py': 'worker가 전달한 schema를 call.schema로, 의미 계약을 call.output_schema로 기록하고 의미 계약으로 외부 CLI 응답을 구성한다.',
    'support/operator_probe_inputs.py': '원 schema에서 nonce를 읽고 기존 파일/checkpoint/도구/정지 사건을 유지하며 explicit stream과 final에 같은 현재 전송 바이트를 쓴다.',
    'support/cross_installation.py': '실 설치 복구 호출의 repair_outcome 필드를 원 의미 schema에서 확인한다.',
    'contracts/pairs.py': '합성 collection을 실제 runner/worker/collector 호출로 교체한다. 공급자별 성공·실제 결박·CLI exit에 의한 불완전 수집·소유자 정지 8표본과 Claude 소수 비용을 보존한다.',
    'contracts/test_pairs.py': '표본별 실제 status/output/collection/error_kind/error, collector 결과·원자료 해시·결박·종료를 검사한다. 기존 수신·필수/선택 필드 역방향 모집단 검사도 유지한다.',
    'sim/test_operator_probe_contract.py': 'probe의 원 schema와 CLI 전송 schema를 각각 검사하고 기존 nonce·checkpoint·학술 도구·정지 단언을 유지한다.',
    'sim/test_operator_finish_recovery.py': 'OPERATOR_SCHEMA와 전송 schema를 구분해 검사하면서 잘못된 next_step의 정확 output_validation 오류와 실패 출력 보존 단언을 유지한다.',
    'sim/test_provider_schema.py': '실 probe 입력을 만드는 CLI 대역의 schema 해석을 공유 helper로 통일한다. 독립적인 원 schema/출력/오류 단언은 유지한다.',
    'sim/test_observation_delivery.py': '현재 Codex native final을 명시하고 기존 20관찰/한 callback에 원행 바이트와 의미 output 단언을 더한다.',
    'flows/test_provider_native_storage.py': 'Codex native final을 현재 봉투로 구성하며 수치·공개 블록·source 바이트·저장/재읽기와 별도 의미 output 검사를 유지한다.',
    'flows/test_provider_raw_ingress.py': 'normal turn.start/final/terminal 순서를 갖춘 공통 stream에 malformed 행만 주입한다. 두 공급자 정상 대조와 42사례의 정확 collector 오류·원바이트·후속/저장/중복 방지를 검사한다.',
    '.timings.json': '공식 시험 실행이 갱신한 비용 캐시다. 미러 실행 후 정본 값을 공식 생성기로 다시 동기화했다.',
}
file_changes = []
for path in verification['changes']:
    relative = path.split('/scripts/tests/', 1)[1]
    detail = changes[relative]
    if path.startswith('.agents/'):
        detail = '공식 build_skill_mirrors.py 생성 사본. ' + detail
    file_changes.append({'path': path, 'detail': detail})

check_details = {
    'pair-red': ('pass', '수리 전 새 분기 단언의 기대된 실패: 공식 1선택/1failed, 비결박 Codex/Claude 두 subTest가 failed/output_validation을 포착했다. 제품 통과가 아니다.'),
    'pair-green': ('pass', '실제 collection 표본으로 교체한 뒤 같은 정확한 ID가 1passed다. 이후 raw fixture만 바뀌었고 최종 consumers에서도 pair 전체를 재검사했다.'),
    'consumers': ('fail', '첫 직접 소비 98선택/97passed/1failed. 기존 11실패는 전부 해소됐으나 raw ingress의 보강 단언이 기존 final/terminal 순서와 parser 중단 조건을 드러냈다. 당시 시험/원출력을 보존했다.'),
    'raw-green': ('pass', '정상 framing 대조와 공급자별 정확 오류로 교정한 raw ingress 1passed. 2개 정상 대조 및 42개 malformed 입력을 실제 worker/runner/저장 경로에서 검사했다.'),
    'consumers-final': ('pass', '최종 직접 소비 및 설치 복구의 두 정확한 ID. 선택/고유 row/종료와 최종 Python 해시가 일치하며 과거 11실패를 모두 passed에 연결했다.'),
    'boundaries': ('pass', '지정 제품 경계 보존 묶음. 원 schema 제약, native final mismatch, worker hash, 종료 barrier, Claude/control_binding, 냄새/층 검사를 최종 Python 판본에서 완료했다.'),
    'corpus': ('pass', '정본 corpus 구조·전건 재생·실 녹화와 대역 계약 묶음을 최종 Python 판본에서 완료했다.'),
    'reuse': ('pass', 'runtime124와 smoke 입력3, 현재 두 CLI 경로/실행 파일 SHA/version/help를 phase006과 대조했다. 새 모델 호출0이며 phase003 Claude의 역사 binary SHA 미기록 한계는 유지한다.'),
    'mirror-plan': ('pass', '공식 생성 함수의 계획과 기존 dirty, overlay manifest 바이트를 대조했다. 변경 후보가 이번 허용 대응 파일에만 속한다.'),
    'mirror-build': ('pass', '공식 생성기로 계획한 미러 파일만 갱신했다. 원/생성 파일별 변화는 command의 source-before/after에 보존했다.'),
    'mirror': ('pass', '지정 미러 직접 소비·pair·corpus 묶음을 완료했다. 선택/고유 row/종료가 대응하고 최종 미러 Python 판본과 일치한다.'),
    'cache-plan': ('pass', '미러 실행 뒤 공식 생성 차이가 허용된 미러 .timings 한 파일뿐임을 확인했다.'),
    'cache-sync': ('pass', '공식 생성기로 미러 .timings 한 파일을 정본 값에 맞췄다.'),
    'mirror-check': ('pass', '공식 --check에서 전체 생성 파일 drift가 없음을 확인했다.'),
    'skill-check': ('pass', 'probe_cli --skill-only에서 installed_skill_structure verified를 확인했다.'),
    'final-audit': ('pass', '전체 소스와 쓰기 범위, 각 공식 selected/row/exit/최종 해시, 이전11실패 해소, runtime/smoke 불변, 양쪽 corpus18/51/50명시SHA와 전102경로 Git raw/clean 동등성을 검산했다.'),
}
checks = []
for label, (result, detail) in check_details.items():
    record = read(EVIDENCE / (label + '-command') / 'command.json')
    assert record['state'] == 'exited'
    assert record['exit_code'] == (1 if label in ('pair-red', 'consumers') else 0)
    if label in verification['checks']:
        observed = verification['checks'][label]
        detail += f" 실제 선택 {observed['selected']}개, 결과 {observed['counts']}, exit {record['exit_code']}."
    checks.append({'command': subprocess.list2cmdline(record['argv']), 'cwd': 'repo:.', 'result': result,
                   'exit_code': record['exit_code'],
                   'evidence': refs(label + '-command/command.json', label + '-command/stdout.txt', label + '-command/stderr.txt'),
                   'detail': detail})

report = {
    'status': 'complete',
    'narrative': 'phase 006의 제품 전송 계약을 고정하고 그 직접 소비 시험을 수리했다. 시작 2640소스는 phase006 종료와 전부 같았고 기존 dirty를 보존했다. 실제 worker가 전달한 Codex schema 안의 원 의미 schema를 기존 provider_runs helper에서 읽고 제품의 한 전송 정의와 대조한다. operator/probe/cross_installation은 원 schema로 응답을 구성하고 CLI 전송 schema는 별도 확인한다. 명시 native final만 현재 봉투로 갱신했으며 nonce·파일·checkpoint·학술 도구·정지·정확한 오류·수치·공개 블록·저장/재읽기·단일 chunk의 기존 단언을 유지했다. 제품 decoder를 기대값 생성기로 쓰거나 제품 fallback을 추가하지 않았다.\n\n'
        '성공 표본 공백은 새 분기 단언의 red에서 Codex/Claude 두 비결박 표본을 실제 failed/output_validation으로 포착했다. 이후 실제 runner/worker/collector가 만든 요청·원바이트·결박 결과로 8분기를 구성했고 상태/출력/collection/error_kind/정확 오류/원자료 해시/종료를 검사한다. 기존 artifact/operator file 수신 및 Pair.fields의 필수·선택 필드 역방향 검사는 유지했다.\n\n'
        '첫 직접 소비98건은97passed/1failed였고 phase006의11실패는 이미 해소됐다. 새로 보강한 raw ingress가 final과 terminal 사이에 놓인 기존 정상 후속 행의 별도 오류를 드러냈다. 정상 turn.start/final/terminal 순서를 갖춘 동일 생성기에서 malformed 행만 더하는 방식으로 교정했다. 두 공급자 정상 completed 대조와42malformed 사례의 공급자별 정확 collector 오류·원바이트·후속/저장/재전달 무효과가 통과했다. parser 중단으로 생기는 terminal/final 부재와 무관한 출력 형식 오류를 구별하며 원실패와 당시 fixture를 보존했다.\n\n'
        '최종 consumers-final·boundaries·corpus 및 공식 생성 뒤 mirror의 지정 묶음을 완결했다. verification-final은 선택 ID/고유 row/실제 exit와 최종 Python 해시, 검사 중 불변을 대응시킨다. 실행 중 변경은 허용된 비용 캐시뿐이며 묶음은jobs1로 순차 실행했다. 마지막 미러 비용 캐시를 공식 생성기로 다시 맞추고 --check/skill-only를 통과했다. 양쪽 corpus는 각각18항목·51파일·223685바이트·50명시SHA를 유지하고 전102경로 Git raw/clean이 같다. 원자료·기존 manifest·역사 실패 verdict는 불변이다.\n\n'
        'runtime124개와 smoke 입력3개, 두 CLI의 경로/실행 파일 SHA/버전/help가 phase006과 같아 Codex 대표 실호출 및 phase003 Claude의 승인된 한정 재사용 조건을 유지했다. 새 모델 호출은0이다. phase003의 바이너리SHA 미기록 및 background passed=false 한계는 보존한다. 전체 일반/T3/극단 변이, 나머지 G7 연쇄, 상태기계 전체 공간과 최종review는 배정 범위 밖이며 이 부분 통과를 G4~G8 충족으로 확대하지 않는다. Git stage/commit/push와 graphify 갱신도 수행하지 않았다. 다음 검수와 제품 커밋 판단은 manager 책임이다.',
    'acceptance': [
        {'id': 'A1', 'result': 'pass', 'detail': '시작2640소스/기존dirty, 원11실패의 정확ID/traceback, pair의 실제 source_request 공백을 확인했다. 지정 helper와 직접 소비·보존 기대값 표를 review-notes에 남겼고 chunk/raw/설치복구 두 사례 및 상태기계 호출부까지 읽었다.',
         'evidence': refs('source-start.json', 'start-state.json', 'input-sources.json', 'previous-failures.json', 'review-notes.md')},
        {'id': 'A2', 'result': 'pass', 'detail': '원/전송 schema 구분을 기존 support.provider_runs 한 곳에서 공유한다. probe/repair의 원 의미와 정확 오류, 명시 raw와 수치/공개블록/저장/한 chunk 단언을 유지했다. raw malformed는 정상 final 대조와 정확 collector 이유로 검사하며 제품 runtime은 불변이다.',
         'evidence': refs('consumers-final/report.json', 'boundaries/report.json', 'raw-green/report.json', 'review-notes.md', 'verification-final.json')},
        {'id': 'A3', 'result': 'pass', 'detail': '수리 전 한시험/두subTest 실패를 보존했다. 실제 runner/collector로 두 공급자 각각 성공·결박·불완전·정지8표본을 만들며 실제 결과 분기를 확인했다. 실제 생산 결과의 두 저장 수신 검사와 필수/선택 필드 written 합집합 검사를 유지했다.',
         'evidence': refs('pair-red/report.json', 'pair-red-command/stderr.txt', 'pair-green/report.json', 'consumers-final/report.json', 'review-notes.md')},
        {'id': 'A4', 'result': 'pass', 'detail': '지정 최종 직접 소비·제품 경계·corpus 묶음을 완결했고 phase006의11실패 모두 현재passed다. chunk/설치복구 두사례/오형태반려와 기존 Claude/control_binding/native mismatch/worker hash/종료/원schema 제약도 확인했다. 전체 일반 성공은 주장하지 않는다.',
         'evidence': refs('consumers-final/report.json', 'boundaries/report.json', 'corpus/report.json', 'verification-final.json')},
        {'id': 'A5', 'result': 'pass', 'detail': '정확한runtime124와smoke입력·도구 조건의 불변으로 기존 실호출 근거를 한정 재사용했다. 허용된 미러 생성·지정 미러 회귀·비용캐시 재동기화·최종--check/skill-only를 완료했다. 각corpus18/51/50SHA와102경로raw=clean을 실제 바이트로 확인했다.',
         'evidence': refs('live-reuse.json', 'mirror-plan.json', 'mirror/report.json', 'cache-plan.json',
                          'mirror-check-command/stdout.txt', 'skill-check-command/stdout.txt', 'corpus-final.json', 'source-final.json', 'verification-final.json')},
    ],
    'changes': file_changes,
    'seams': [],
    'findings': [
        {'id': 'F1', 'kind': 'fact', 'detail': 'phase006의11개 직접소비 실패와 성공pair 두분기 공백은 최종 동일판본 검사로 해소됐다. source-request를 허용 없이 보충한 합성결과가 아니라 실제 수집 결과를 사용하며 새 분기 단언의 red/green을 보존했다.',
         'evidence': refs('pair-red/report.json', 'pair-green/report.json', 'consumers-final/report.json', 'verification-final.json'),
         'affects': ['run:context.md#C12', 'run:context.md#G3', 'run:plan.md'],
         'next_action': 'manager가 phase006 F2/F3 및 A3/A5의 이 직접소비 남김을 새 근거로 처분하고 공급자 단위 제품 커밋을 판단한다. 다른G 의무를 완료로 바꾸지 않는다.'},
        {'id': 'F2', 'kind': 'fact', 'detail': '기존 raw ingress의 Codex 정상 후속 행 위치는 자체 final mismatch를 만들었다. 정상 stream 대조로 이를 제거했으며 malformed 자체의 parser 중단에 따른 terminal/final 부재는 코드 계약에 맞는 정확한 목록으로 검사한다. 첫97pass/1fail과 수정한raw/최종전체지정묶음의 성공을 구별한다.',
         'evidence': refs('consumers/report.json', 'raw-ingress-first.py', 'raw-green/report.json', 'consumers-final/report.json', 'review-notes.md'),
         'affects': ['run:context.md#G3', 'repo:.claude/skills/do-math/scripts/tests/flows/test_provider_raw_ingress.py'],
         'next_action': 'manager는 이 수리된 fixture 오류와 정확한 반려 성질을 검수한다. 추가 제품 parser 수리나 실패 기대값 완화의 근거로 해석하지 않는다.'},
        {'id': 'F3', 'kind': 'fact', 'detail': '제품runtime124·smoke입력3·두CLI경로/실행파일SHA/version/help와 기존corpus가 불변이다. 새 유료호출0으로006Codex 및003Claude의 승인된 한정 근거를 유지한다.003역사binarySHA 미기록과background passed=false는 그대로다.',
         'evidence': refs('live-reuse.json', 'corpus-final.json', 'verification-final.json'),
         'affects': ['run:context.md#C12', 'run:context.md#G7', 'run:plan.md'],
         'next_action': 'manager는 기존 대표 실호출의 재사용 범위를 보존하고 남은 G7 실연쇄 및 최종 관문을 별도 배정한다. stage/제품 커밋과 staged corpus 바이트 대조는 관리 마감에서 수행한다.'},
    ],
    'checks': checks,
}
write_json(EVIDENCE.parent / 'report.json', report)
print('Wrote complete report with', len(file_changes), 'changed files and', len(checks), 'checks.')
