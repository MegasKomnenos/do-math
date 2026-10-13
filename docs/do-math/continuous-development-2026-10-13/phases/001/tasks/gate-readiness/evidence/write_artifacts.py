"""Serialize the gate-readiness analysis from this task's observed evidence."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = Path('C:/math')
TASK_REF = 'run:phases/001/tasks/gate-readiness/'
SCRIPT = '.claude/skills/do-math/scripts/'
PYTHON = 'C:/Users/wogud/AppData/Local/Programs/Python/Python312/python.exe'


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def evidence(name):
    return TASK_REF + 'evidence/' + name


def source(name):
    return 'repo:' + SCRIPT + name


def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


population = read('population-and-corpus.json')
environment = read('environment.json')
contracts = read('source-contracts.json')
history = read('historical-reports.json')
before = read('source-before.json')

commands = [
    ('ordinary', SCRIPT + 'run_tests.py', ['--jobs', '3', '--output', '{new_output_dir}']),
    ('fresh-t3', SCRIPT + 'run_tests.py', ['--tier', 'T3', '--full', '--jobs', '3', '--output', '{new_output_dir}', '--t3-store', '{new_t3_store_dir}']),
    ('mutation-every', SCRIPT + 'tests/support/mutation.py', ['--base', '{frozen_head}', '--every', '--output', '{new_output_dir}']),
    ('t4', SCRIPT + 'run_tests.py', ['--tier', 'T4', '--jobs', '3', '--output', '{new_output_dir}']),
    ('t5', SCRIPT + 'run_tests.py', ['--tier', 'T5', '--jobs', '1', '--output', '{new_output_dir}']),
    ('corpus-replay', SCRIPT + 'run_tests.py', ['structure.test_corpus', 'unit.test_corpus_replay', 'contracts.test_doubles_follow_corpus', '--jobs', '1', '--output', '{new_output_dir}']),
    ('provider-codex', SCRIPT + 'probe_cli.py', ['--provider', 'codex', '--model', '{verified_codex_model}', '--cases', 'files', '--scholarly', '--output-dir', '{new_output_dir}']),
    ('provider-claude', SCRIPT + 'probe_cli.py', ['--provider', 'claude', '--model', '{verified_claude_model}', '--cases', 'files', 'background', '--only-assigned-model', '--output-dir', '{new_output_dir}']),
    ('delivery-mirror-check', '.claude/skills/writing-skills/scripts/build_skill_mirrors.py', ['--check', '--target', '.agents']),
]
command_rows = [{'id': identifier, 'executable': PYTHON, 'interpreter_arguments': ['-u', '-B'], 'script': script, 'arguments': args, 'cwd': 'repo:.', 'execution': 'not_run'} for identifier, script, args in commands]

normal_criteria = [
    '실제 프로세스 종료 코드 0과 최종 report.json을 함께 확인한다. 현재 runner는 오류/빈 선택을 exit 2로 거부하며 발견/선택 단계 실패에는 최종 report가 없을 수 있다.',
    'complete=true, successful=true, changed_during_run=[]를 확인한다. complete는 실행 완결, successful은 기능 판정이다.',
    'selected와 reports[].rows 중 fixture가 아닌 id의 집합·중복·개수를 전건 대조한다. 실패/error/not_run/running/unexpected_success가 없어야 한다. fixture_counts와 worker_error, returncode도 확인한다.',
    'skipped와 expected_failure는 runner successful=true에 들어갈 수 있다. G4의 통과 수로 세지 않고 원문상 허용 여부와 미검증 성질을 개별 처분한다.',
    'source_sha256은 scripts/**/*.py의 시작 해시이고 changed_during_run은 전후 차이 목록이다. JSON·문서·말뭉치·미러까지 고정되었다는 증거는 별도 전후 manifest가 필요하다.',
]

gate = {
    'schema': 'gate-readiness/1',
    'status': 'preparation_complete; gates_not_executed',
    'phase': '001', 'task': 'gate-readiness',
    'scope': 'writes=[]; 자기 report/evidence만 작성. 제품/시험 import·discovery·run_tests --list/실행·변이·실공급자·다운로드·컴파일·예약 변경·graphify 갱신 없음. 표준 라이브러리 AST/JSON/해시/파일 조회 및 명시 버전 명령만 사용했다.',
    'edition': {'head': before['head'], 'baseline_head': before['baseline_head'], 'canonical_files': before['current_product_count'], 'differences_from_baseline': before['baseline_differences'], 'evidence': evidence('source-before.json'), 'note': 'HEAD는 준비 이후 변경되었지만 baseline에 기록된 정본 969개 및 source/engine 파일 해시는 모두 일치한다. dirty/untracked는 준비 상태로 보존한다.'},
    'command_bindings': {
        'new_output_dir': '후속 배정 task의 evidence 아래 실행별 새 절대 경로. 프로세스 stdout/stderr/execution.json은 runner 출력 디렉터리의 형제 경로에 둬 --output의 empty 조건을 보존한다.',
        'new_t3_store_dir': '후속 task evidence 아래 새 T3 저장소 경로. --full 자체가 재사용을 막고 이 경로 지정은 증거 소유와 격리를 명확히 한다.',
        'frozen_head': '최종 실행 시작 시 기록한 실제 Git commit ID. --every에서도 --base는 필수이며 실제 commit이어야 한다. 이 준비의 HEAD를 미래 실행에 고정하지 않는다.',
        'verified_codex_model': '후속 실호출 담당자가 현재 계정·설정·지원으로 확인할 Codex 모델 ID. 이번에는 인증/설정 비밀을 읽지 않아 미확정이다.',
        'verified_claude_model': '후속 실호출 담당자가 확인할 claude-로 시작하는 전체 모델 ID. 역사 말뭉치의 모델 ID를 현재 사용 가능하다고 가정하지 않는다.',
        'warning': '중괄호 값은 아직 배정되지 않은 출력/환경 입력이다. 실행 전 구체 값으로 결속한다. 존재하지 않는 제품 CLI 옵션을 추가한 것이 아니다.',
    },
    'commands': command_rows,
    'official_selection': {
        'source': source('run_tests.py'), 'symbols': ['FOLDERS', 'TIERS', 'DEFAULT_FOLDERS', 'test_modules', 'discover', 'main'],
        'tiers': contracts['tiers'],
        'default': 'TIERS[T3]와 같은 structure/unit/contracts/sim/flows를 고르지만 --tier T3를 주지 않으면 측정하지 않는다. G4는 위치 인자·--match·--tier 없이 공식 기본 전체 선택을 실행한다.',
        'rules': '반복 --tier는 합집합, 위치 인자/--match와는 교집합이다. 모르는 위치 ID 하나라도 전체 exit 2. 모든 폴더의 필수 __init__, 디스크 test_*.py/수집 모듈 일치, 중복 test ID를 검사한 후 선택한다. 폴더 없는 시험·빈 선택도 거부한다.',
        'current_disk_test_modules': population['test_module_counts'],
        'population_limit': '위 수는 파일 수이며 실제 unittest 수집 시험 수가 아니다. 상속·동적 수집이 있어 AST test_ 개수나 B129 3990을 현재 선택 분모로 쓰지 않는다. 이번 --list는 하지 않았다.',
        'side_effects': ['일반 실행의 tests/.timings.json', '측정 실행의 tests/.timings-t3.json', '온전한 T3의 tests/.selection-index.json 및 Git blob 저장', 'T3 저장소 records.json/coverage.data', '새 출력 디렉터리의 report/worker/scratch 파일'],
    },
    'gates': [
        {
            'id': 'G4', 'command': 'ordinary', 'readiness': '명령 계약 확인; 최종 제품 수리/판본 고정 뒤 실행',
            'prerequisites': ['Windows/Python/Git 및 제품·시험 의존', '동시 검사 묶음 없음, 총 workers<=3', '후속 task의 runner 부수 파일 쓰기 소유와 source manifest', 'G1~G3 수리와 필요한 실제 경계 수리가 끝난 최종 후보'],
            'outputs': ['{new_output_dir}/report.json', '{new_output_dir}/parallel-N/{requested.json,result.json,worker-report.json,stdout.txt,stderr.txt,progress-*.json,scratch/}', '{new_output_dir}/<folder>-isolated-N/의 같은 worker 자료'],
            'important_fields': ['selected', 'discovered', 'folders', 'tiers', 'tests', 'counts', 'fixture_counts', 'reports[].rows', 'reports[].complete', 'reports[].successful', 'reports[].returncode', 'reports[].worker_error', 'source_sha256', 'changed_during_run', 'group_seconds', 'total_seconds', 'budget'],
            'acceptance': normal_criteria,
            'source': [source('run_tests.py'), evidence('historical-reports.json')],
        },
        {
            'id': 'G5', 'command': 'fresh-t3', 'readiness': 'fresh 명령 계약 확인; 최종 판본 측정은 미실행',
            'prerequisites': ['같은 최종 판본 G4 완결', 'Python 3.12 sys.monitoring 및 coverage 7.16.2', '충분한 디스크·메모리·독점 검사 슬롯; 고정 여유 RAM 중단 문턱은 만들지 않음'],
            'selection': 'TIERS[T3] 전체, 위치 인자와 --match 없음. --full 명시. coverage는 시험 모듈별 분기 합집합, sys.monitoring은 시험/fixture별 함수 진입, audit hook은 열린 비코드 입력을 기록한다.',
            'measurement_scope': 'LAYERS 1/2/3의 현재 123개 모듈을 gate가 판정한다. adapter 5개는 제외. tests/support는 선택을 위해 측정되지만 제품 gate 대상은 아니다. 일반 parallel worker는 각각 측정·병합한다. lean/resource 격리 클래스와 제품의 임의 자식 프로세스는 자동 측정되지 않으며, 격리 시험 ID는 선택 색인의 in-process 시험 집합에서 제외된다.',
            'outputs': ['report.json의 branch_gate/selection_index/measurement_missing/closing_eligible/t3_store/passed', 'coverage.json', 'entered.json', 'opened.json', '각 측정 worker의 coverage.data/entered.json/opened.json', 'tests/.selection-index.json 생성본을 evidence에 보존', '{new_t3_store_dir}/records.json 및 coverage.data'],
            'acceptance': normal_criteria + ['passed=true AND branch_gate.passed=true AND measurement_missing=[] AND closing_eligible=true AND t3_store.mode=full AND reused_modules=[]가 모두 필요하다.', 'branch_gate.judged_modules를 실행 시 LAYERS 모집단과 대조하고 unmeasured_modules/modules_with_gaps/missing_branches/missing_lines를 확인한다. 제외는 coverage.json의 excluded_lines와 원문상 사유를 개별 검토한다.', 'selection_index는 요약 필드이므로 실제 색인 tests/files/functions/blob과 entered/opened 원자료를 함께 보존한다. index가 쓰였다는 사실이나 closing_eligible=true는 시험 성공을 보장하지 않는다.', 'T3 complete/changed만으로 index 작성이 가능한 현재 구현상 시험 실패 또는 measurement_missing 상황에서도 index 존재를 성공 근거로 쓰지 않는다. 실패한 측정의 index를 최종 변이에 공급하지 않는다.'],
            'reuse': '현재 색인은 2026-10-01, 2163 tests/696 files이며 commit은 HEAD의 조상이다. 이것은 현재 판본 완비성이 아니다. 저장소는 /1 형식 304 modules이고 현 코드 요구는 /2다. 어느 경우든 G5는 --full로 새로 측정한다.',
            'source': [source('tests/support/branch_gate.py'), source('tests/support/selection.py'), source('tests/support/t3_store.py'), evidence('source-contracts.json')],
        },
        {
            'id': 'G6', 'command': 'mutation-every', 'readiness': '파일 범위 확인; 정상 기준 오류 처리와 7개 범위외 파일 처분을 먼저 확정',
            'prerequisites': ['G5의 통과한 동일 판본 fresh 색인/entered 자료', '정상 기준 missing/load/실행 결과를 성공과 구분하는 수리', '최종 현재 함수+rule+선택 시험 목록과 분할 합집합 확정', 'tests/pseudo_tested.json 쓰기를 후속 task에 배정; 분할끼리 같은 목록을 병렬 수정하지 않음'],
            'selection': '--every와 --base를 같이 쓰면 LAYERS 1/2/3 각 모듈의 현재 모든 함수·메서드·중첩함수 본문을 대상으로 한다. --only는 scripts-relative 모듈 glob, 반복은 합집합. --mutation-base만 붙인 T3는 변경 함수 검사이므로 전체 G6 대체가 아니다. mutation CLI에 --jobs/--timeout/--full/--list 옵션은 없다.',
            'outputs': ['{new_output_dir}/mutation.json', 'mutant-N/{mutant.py,spec.json,result.json,output.txt}', 'unmutated-N/{spec.json,result.json,output.txt}', 'tests/pseudo_tested.json (살아남은 함수 사유 목록; 생성/갱신 가능)'],
            'important_fields': ['base', 'every', 'functions', 'counts', 'baseline_failing', 'unreasoned_entries', 'list', 'seconds', 'survived', 'outcomes[].module/function/rule/line/status/tests/folders/estimated_seconds/seconds/killed_by/detail'],
            'acceptance': ['함수별 outcomes와 현재 대상 함수 manifest를 일대일 대조한다. counts 합계와 functions, trivial/비trivial 구분, 선택 시험과 실제 child 증거가 모두 맞아야 한다.', 'passed(report)는 unreasoned_entries=0, baseline_failing=[], execution_error/mutation_error/not_executed=0을 요구한다. 하지만 현 정상 기준 분기 결함과 empty 대상 검증 부재 때문에 exit 0만으로 G6를 승인하지 않는다.', 'survived를 숨기지 않는다. None/빈 본문과 본질적으로 같은 변이만 계약 근거로 사유 처리하고, 일반 생존은 실제 결과 단언을 보강한다.', '원본 실패는 kill이 아니다. 환경/loader 실패와 미완결은 별도 실패이며 비용·시간 초과는 kill이 아니다. 정상 결과 없는 후보를 통과 처리하지 않는다.'],
            'source': [source('tests/support/mutation.py'), source('tests/unit/test_mutation.py'), source('tests/boundary/test_mutation_baseline.py')],
        },
        {
            'id': 'G7-T4', 'command': 't4', 'readiness': '현재 boundary 69개 시험 파일; 실제 실행/권한은 미확인',
            'prerequisites': ['Windows Job/console와 pythonw sibling', '실제 Git 프로세스, loopback 서버 포트, 파일 교체 권한', 'PowerShell ScheduledTasks 조회, 실제 Lean portable 경로', '후속 실행 때 모든 skip 조건 및 도구 판본 기록'],
            'port_mapping': {'clock': 'SystemClock', 'calls': 'ThreadCalls', 'git_backend': 'GitProcess', 'jobs': 'WindowsJobs', 'http': 'UrllibHttp + loopback server', 'scheduler': 'PowerShellScheduler.status (고유한 부재 task명)', 'host': 'LocalHost discover_lean/cli_identity/cli_describe'},
            'contract_location': 'support/port_contracts/*.py를 contracts의 대역 구현과 boundary의 실제 구현 하위 클래스가 공유한다. 실제 조립은 do_math/wiring.py:real_ports다.',
            'outputs': ['공통 report/worker evidence', '도구 판본 및 실제 환경 skip 사유', '필요한 어댑터 분기 측정은 별도 미완료'],
            'acceptance': normal_criteria,
            'limits': ['T4의 예약 계약은 status뿐이다. test_operator_schedule_adapter는 등록 cmdlet을 대역으로 바꾸고 실제 설정 XML을 내보내므로 실제 OS 등록/발화/해제를 증명하지 않는다.', 'test_provider_cli_surface는 fixture batch CLI로 어댑터를 검사한다. T4 통과는 실공급자 모델 호출 성공이 아니다.', 'run_tests는 T3 요청 시에만 Measurement를 만든다. --tier T4만으로 설계 5.5의 adapter 분기 보고를 만들지 않는다. 기존 전체 T3와 T4를 혼합해 fresh T3 선택을 흐리지 말고 경계 담당자가 이 측정 경로를 별도 완결해야 한다.'],
            'source': [source('do_math/wiring.py'), source('tests/support/port_contracts/scheduler.py'), source('tests/support/port_contracts/host.py'), source('tests/boundary/test_operator_schedule_adapter.py'), source('tests/boundary/test_provider_cli_surface.py')],
        },
        {
            'id': 'G7-T5', 'command': 't5', 'readiness': '구현 공백: smoke/test_*.py=0, 현재 선택은 empty로 exit 2가 되는 정적 경로',
            'prerequisites': ['기존 run_tests T5 경로에 실제 smoke 시험 구현', '공급자별 모델/인증/계정 한도/로컬 도구 권한 확인', '새 시험 전용 설치/인스턴스와 예약 고유 이름·정리 증거', '실제 Lean/Mathlib 대표 컴파일과 학술 MCP list_sources 접근', '필요한 말뭉치와 미러 쓰기 범위 배정'],
            'available_partial_commands': ['provider-codex', 'provider-claude'],
            'partial_scope': 'probe_cli의 files는 실제 ModelRunner/WindowsJob/worker/수신 parser/파일/checkpoint 연쇄를 실행한다. codex files --scholarly는 실제 mcp__scholarly__list_sources 관측을 요구한다. Claude files/background 두 사례는 회수 조건과 모델 고정을 확인한다. 기본 cases 세 개를 그대로 쓰지 않아 공급자당 files 1개, Claude background 추가 1개로 최소화할 수 있다. 이 도구의 작은 protocol_probe schema는 실제 제품 역할 schema 전부, Lean/Mathlib, 예약 연쇄를 대신하지 않는다.',
            'probe_outputs': ['출력 루트 report.json: at/provider/model/passed/cases/sources/scope', '<case>/report.json: checks/result/actual_tool_names', '<case>/evidence의 실제 worker/stdout/final 자료', '<case>/workspace의 nonce 파일/checkpoint 등'],
            'probe_acceptance': ['프로세스 exit와 root/case passed, 실제 local_termination, structured_result, preserved_file, checkpoint를 함께 확인한다.', '--scholarly는 native 실제 도구명과 결과를 확인한다. 설정 파일 존재만으로 접근 성공을 세지 않는다.', 'background는 같은 task_id/tool_use_id로 시작→완료→최종 결과 순서를 current background_completed_before_result 계약과 대조한다.', 'provider 모델/effort 지원·schema 반려·인증/환경 실패는 그 상태대로 보존한다. raw bytes를 합성하거나 --version을 모델 호출로 세지 않는다.'],
            'remaining_required_chain': ['실제 역할 schema의 최소 실호출', 'Job 자식 종료·pythonw 출력 회수', 'Lean/Mathlib 대표 검증', '시험 전용 예약 등록·발화·해제·정리', '학술 MCP 실제 list_sources', '현재 도구판 녹화+현 파서/대역 재생'],
            'source': [source('run_tests.py'), source('probe_cli.py'), evidence('population-and-corpus.json')],
        },
        {
            'id': 'G8', 'command': 'delivery-mirror-check', 'readiness': '최종 review와 인도는 후속 manager/review 책임',
            'prerequisites': ['G1~G7 근거 완비', '후속 task가 필요한 정본/미러/지침 변경을 마친 뒤 판본 고정', '제품 수정 없는 review kind phase'],
            'acceptance': ['--check --target .agents는 실제 있는 읽기 옵션이다. 전체 skills target를 검사하므로 다른 스킬의 기존 drift와 do-math 결과를 구분한다.', 'main에 인도되는 제품/시험/문서/미러가 검증 판본과 일치해야 한다. manager가 모든 finding을 처분한 뒤에만 개발 완료를 정한다.', 'review 이후 제품·결과 설정·seam이 바뀌면 해당 work/review를 다시 배정한다. task는 commit/reset/checkout/push를 하지 않는다.'],
            'source': ['repo:.claude/skills/writing-skills/scripts/build_skill_mirrors.py', 'run:context.md#G8'],
        },
    ],
    'mutation_preparation': {
        'existing_file_partitions': {'source': 'repo:docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json', 'json_pointer': '/current_work/independent_execution/plan/tasks', 'count': population['shard_count'], 'unique_files': population['shard_unique_files'], 'current_eligible_modules': len(population['eligible_modules']), 'missing_eligible': population['eligible_not_in_shards'], 'duplicates': population['shard_duplicate_files'], 'not_selected_by_mutator': population['shard_ineligible_files'], 'detail': '기존 17개는 8파일씩 16묶음+2파일이다. 현재 123개 layer1/2/3 모듈은 전부 한 번 포함되며 5 adapter와 runner/isolation 두 파일은 변이 선택에서 제외된다. --only로 이 일곱 파일을 줘도 mutator의 layer filter를 확장하지 않는다. manager는 설계의 대상 밖 처분과 별도 검증 책임을 명시해야 한다.'},
        'rules': {'return_first': '함수 자신의 scope에 yield/yield from이 있는 generator: 첫 실행문 전에 return 삽입', 'return_none': '함수 자신의 scope에 None 외 값을 반환하는 return이 있으면 본문을 return None으로 치환', 'pass': '그 외 상태변경형 본문을 pass로 치환', 'trivial': 'docstring을 뺀 본문이 없거나 pass/...뿐이면 변이와 같아 별도 trivial 상태'},
        'final_population_method': ['최종 LAYERS에서 1/2/3 파일 집합을 다시 읽어 현 디스크와 대응시킨다.', '현 mutation.functions/changed_functions/mutate 규칙으로 qualified name(중복 #n 포함), 위치, rule, trivial 여부와 소스 SHA/blob을 확정한다. 과거 1586은 분모가 아니다.', 'fresh selection-index/2의 files[repo-relative module].functions에서 함수 이름(#n 제외)을 tests ordinal에 대응시키고 entered.json의 시험/fixture 진입과 대조한다.', '동일 blob에 진입 시험이 없는 비trivial은 not_executed로 별도 남긴다. 바뀐/없는 색인의 folder fallback을 fresh 선택 근거로 오인하지 않는다. 현재 선택 fallback은 1/2층 unit+contracts, 3층 sim이다.', '123 모듈이라는 파일 수와 최종 함수 수·진입 시험 수·trivial 수·실제 변이 outcome 수를 구분하고 파일 묶음 합집합에 누락/중복이 없는지 검산한다. 결과가 없는 파일을 묶음 exit 0으로 덮지 않는다.'],
        'baseline_behavior': '현재는 선택 시험 전체를 원본으로 먼저 실행하지 않는다. 변이체에서 실패한 시험만 lazy하게 한 번 정상 실행해 기억하며, 원본에서도 같은 ID가 실패하면 제외 후 mutant를 다시 돌린다. 정상 spec/result는 unmutated-N에 있지만 mutation.json에는 baseline 성공 전건 목록·실제 testsRun·skip 수가 없다. G4/T3의 정상 결과 및 개별 원본 결과를 연결해야 한다.',
        'confirmed_static_issue': {'location': source('tests/support/mutation.py'), 'symbols': ['run.fails_unmutated', '_child_run', '_child', 'passed'], 'counterexample_input': 'mutant 결과 failing={unit.probe.Case.test_value}; 그 시험의 unmutated child가 결과 파일을 남기지 않아 failing={CHILD_NO_RESULT}', 'source_derived_result': 'fails_unmutated는 test in failing만 저장하므로 False; broken는 빈 집합; killers에 원래 test가 남아 killed; baseline_failing=[]가 된다. 다른 문제가 없으면 passed=True가 가능하다. 실제 실행 반례를 수행한 결과가 아니라 현 소스 분기를 따라 얻은 반례다.', 'expected': '정상 기준 결과 부재/loader·환경 실패는 정상 통과로 인정하지 않고 evidence failure로 보고해 G6를 막아야 한다.', 'related_limit': 'mutant의 load_error/loader.errors도 문자열 kill로 다뤄 정상 loader 기준을 확인하지 않는다. 정상 child의 skip/0-test 또는 비정상 exit도 현재 결과 형식만으로 명확히 판정하기 어렵다. 후속 수리에서 원본 실패/부재/수집 오류와 실제 mutant 포착을 구분하고 기존 실제 경로를 검증한다.', 'next_owner': 'manager가 mutation evidence 처리의 한정 work task를 배정; 재현 후 수정·관련 unit/boundary 검증. 이번 writes=[]에서는 수정하지 않는다.'},
        'pseudo_list_observation': population['pseudo_tested'],
        'pseudo_list_limit': '파일 부재는 read_list가 빈 목록으로 읽는 상태일 뿐, 변이 0생존/전체 실행의 증거가 아니다.',
        'execution_cost': '단일 mutation 프로세스가 각 child를 순서대로 기다린다. estimated_seconds는 기존 .timings 기반 추정이며 deadline이 아니다. 17묶음 병렬은 공유 pseudo 목록 충돌과 합계 worker 제한 때문에 허용하지 않는다.',
    },
    'environment_readiness': {
        'observed': evidence('environment.json'),
        'facts': ['Python 3.12.10과 sys.monitoring, coverage 7.16.2, Hypothesis 6.168.3가 설치되어 있다.', 'Git 2.50.0.windows.2, Codex 0.162.1, Claude Code 2.1.289, PowerShell 5.1.22621.6133 버전 명령 exit 0.', 'portable Lean 4.32.0과 Lake 5.0.0-src+8c9756b의 직접 실행 파일 --version exit 0. PATH의 lean/lake/elan은 없다.', 'Mathlib lean-toolchain/lake-manifest/lakefile/.do-math-ready와 Mathlib.lean/Mathlib.olean이 존재한다. 현재 컴파일 성공/의존 무결성은 검증하지 않았다.', 'pythonw sibling와 corpus에 기록된 scholarly 서버/venv 실행 파일이 존재한다. 현재 설정·인증·실서비스 응답은 확인하지 않았다.'],
        'explicit_lean_path': 'C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe',
        'lean_followup': '필요하면 후속 실행 환경의 DO_MATH_KNOWLEDGE_TEST_LEAN에 위 직접 경로를 지정한다. 실제 코드 support/provider_inputs.py:actual_command 및 portable_bin fallback과 대조한다. PATH 부재를 Lean 미설치로 오판하거나 elan 다운로드를 시작하지 않는다.',
        'unconfirmed_conditions': ['현재 두 공급자의 로그인·계정 한도·선정 모델/effort 접근·역할 schema 수락·sandbox 파일 쓰기', '실제 Windows Job 생성/자식 종료 및 pythonw 출력 회수', '예약 서비스 조회/등록/발화/해제 권한과 cleanup', '현재 Lean/Mathlib 대표 컴파일·kernel evidence/설치 trust identity', '실효 scholarly 설정 해석 및 MCP 초기화/list_sources 접근', '심볼릭 링크 생성 권한: B129의 WinError1314는 역사 관측이며 현재 권한을 시험하지 않음', '최종 T3/변이의 실제 시간·피크 메모리·출력 디스크 사용량'],
        'not_observed': '버전/파일 존재를 실사용·모델 호출·컴파일·예약 성공으로 세지 않는다. 인증 비밀은 읽지 않았다.',
    },
    'corpus_reuse': {
        'manifest': source('tests/corpus/manifest.json'), 'inventory': evidence('population-and-corpus.json'),
        'counts': {k: population['corpus'][k] for k in ['entry_count', 'kinds', 'file_count', 'bytes_without_manifest', 'undeclared_files', 'missing_files']},
        'current_version_gap': 'manifest.supported_stream_versions.codex=codex-cli 0.160.0, 실제 --version=0.162.1. 새 실호출/command-surface 녹화와 현재 parser replay가 필요하다. 과거 성공을 현재 Codex 성공으로 세지 않는다.',
        'claude_caveat': '설치와 녹화 버전 2.1.289는 같다. background 녹화의 historical live_checks.actual_wait_tool=false와 미통과 scope는 보존한다. 현재 probe는 TaskOutput을 필수로 삼지 않고 background_completed_before_result의 identity/순서를 검사한다. 따라서 과거 실패를 현 계약 실패로 단정하지도, 새 판정 없이 성공으로 바꾸지도 않는다. 재사용 담당자가 raw event 순서·실제 파일/종료 증거와 B87 변경 근거를 대조해야 한다.',
        'scope_caveats': ['schemarejected Codex 녹화는 오류 해석 증거이지 성공 호출이 아니다.', 'scholarly_config 녹화는 구성 해석이며 실제 list_sources 성공이 아니다.', 'scheduler_json 녹화는 세 예약 부재 조회이며 등록/발화/해제 성공이 아니다.', '두 provider legacy entry의 tool_version은 not recorded by the run으로 현재판 증거에 쓰지 않는다.', 'Lean corpus는 preview signature/axiom parse가 주요 범위이며 Mathlib 전체 설치 연쇄 성공을 대신하지 않는다.'],
        'reuse_conditions': ['원바이트 SHA256·tool_version·recorded_at·command·role·source·verdict를 유지한다.', '새 최종 판본의 실제 producer/worker/parser/schema/환경과 어떤 성질이 같은지 확인한다. 버전이 같아도 코드·권한·요구 변화가 있으면 자동 승계하지 않는다.', '현재 버전의 최소 실호출과 녹화 재생을 함께 확보한다. 모든 회귀를 다시 유료 호출로 바꾸지 않는다.', 'corpus-replay 명령은 실제 파서·대역을 대조하지만 네트워크/공급자 성공을 만들어주지 않는다. 실패 녹화를 정상 기대값으로 고치지 않는다.'],
        'consumer_sources': [source('tests/structure/test_corpus.py'), source('tests/unit/test_corpus_replay.py'), source('tests/contracts/test_doubles_follow_corpus.py')],
    },
    'historical_ordinary': {
        'evidence': evidence('historical-reports.json'),
        'b129': {'complete': True, 'successful': False, 'selected': 3990, 'counts': {'passed': 3988, 'failed': 1, 'skipped': 1}, 'seconds': 10724.0, 'process_exit': 1, 'missing_duplicate_unexpected_ids': 0, 'current_python_source_differences': 8, 'execution_source': 'repo:docs/do-math/시험-재편-2026-09-29/검증/2026-10-06-일반통합-B129/execution.json'},
        'repair': '같은 B129 디렉터리 repair.json은 2 passed/9.7초이고 원보고 실패 1개와 직접 회귀를 한정 확인한다. 전체 성공으로 합산하지 않는다.',
        'later': '원보고 해시를 전환표와 대조했다. B130=22 passed, B131=25, B132 최종 문서검사=26, B133=28, B134=28. B134 green은 현재 scripts Python 862개와 해시가 일치하고 다른 green에는 후속 7개 시험/지원 파일 차이가 남는다. B134의 28개가 현재판의 부분 증거이지 전체 3990개 성공은 아니다.',
        'historical_failure': 'structure.test_test_smells의 contracts/test_port_git_backend.py 거부 세부 단언 누락. B129 repair에서 보강됨.',
        'historical_skip': 'unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported: WinError 1314. 현재 조건에서 재판정하며 허용된 환경 제외라도 passed 수에 넣지 않는다.',
        'cost_policy': '검증한 B129의 10724초는 그 판본/환경의 실측이다. T3_full 3300초 등 budgets는 소프트 기준이다. 현 최종판 T3/변이/T4/T5 비용은 미측정이므로 완료 시각을 약속하지 않는다. 전환표의 과거 1586 함수/537 분기 등은 현재 분모/결과가 아니다.',
    },
    'execution_procedure': [
        {'step': 1, 'action': 'manager는 T5 구현·현재 공급자 녹화·변이 정상 기준 수리와 범위외 7파일 처분을 유한 task로 배정한다. 필요한 실제 경계 수리가 최종 소스 고정보다 앞서야 한다. 외부 모델/권한 결정을 해결하지 못하면 정확한 G7 미충족으로 상신한다.'},
        {'step': 2, 'action': '배정된 실행자가 실제 입력·도구판·Git HEAD/dirty·정본 전체 파일 SHA256와 증거 출력 경로를 기록한다. 기존 untracked/연구자료는 그대로 둔다. --list가 필요하면 이 후속 실행 배정에서 수행하고 import 부수효과를 고려한다.'},
        {'step': 3, 'action': '동시에 검사 묶음 하나만 시작한다. run_tests --jobs 3이면 기계의 3슬롯 전부를 사용한다. mutation은 한 프로세스씩 순차 진행한다. runner의 .timings/.selection-index/pseudo list 소유를 확보한다.'},
        {'step': 4, 'action': '한 번 시작한 실행의 PID/session ID·실제 argv/cwd·start 시각·source-before·stdout/stderr 위치를 execution.json에 기록한다. Windows background helper가 필요하면 창을 숨긴다. 제품/시험·문서·자료를 실행 중 편집하거나 git 상태를 바꾸지 않는다.'},
        {'step': 5, 'action': '관찰 도구의 yield/대기 만료는 실행 실패가 아니다. 같은 process/session을 재개해 실제 종료까지 기다리고 필요할 때 진행 상태를 한 번 읽는다. 실행 중 result.json은 do_math.file_io.read_bytes_shared로 읽어 Windows atomic rename을 막지 않는다. 이번 분석은 실행 중 report를 읽지 않았다.'},
        {'step': 6, 'action': '실제 종료·exit·end 시각과 source-after를 기록한다. report가 없으면 PID/worker/log의 실제 상태를 조사하고 종료 원인을 추측하지 않는다. G4→fresh G5→G6를 같은 최종 판본으로 완결한다. G7의 실제 경계/녹화 결과도 해당 판본과 연결한다.'},
        {'step': 7, 'action': '공통 결과/선택/worker/skip 규칙 및 gate별 조건을 확인한다. 원보고 bytes는 수정하지 않고 해시와 파생 판정을 별도 보존한다. 실패하면 먼저 원로그/코드를 읽고 필요한 관련 시험으로 수리한다.'},
        {'step': 8, 'action': '후속 제품/시험/문서/schema/corpus 변경은 영향받는 증거를 무효화한다고 명시한다. 최종 동일판 전체 관문은 새 판본에서 다시 완결해야 하며 과거 부분 통과를 합산하지 않는다. 관리용 report/기억만 추가된 경우와 제품 변경은 구분한다.'},
        {'step': 9, 'action': '모든 필요한 수리/미러/지침 반영 뒤 G1~G7 증거로 제품 수정 없는 review를 배정한다. G8 인도 일치와 finding 처분은 manager가 판단한다. 이번 task complete는 개발 완료가 아니다.'},
    ],
    'source_evidence': [evidence('source-contracts.json'), evidence('source-before.json'), evidence('population-and-corpus.json'), evidence('environment.json'), evidence('historical-reports.json'), 'run:sources/user-decisions.md', 'run:context.md', 'run:plan.md'],
}

write('gate-readiness.json', gate)
print('Wrote gate-readiness.json: preparation only; no gate command executed.')

after = read('source-after.json')
assert after['changed_since_task_start'] == []

findings = [
    {
        'id': 'F1', 'kind': 'issue',
        'detail': 'T5의 현재 실행 경로가 비어 있다. TIERS[T5]는 smoke만 선택하지만 그 폴더에는 __init__.py뿐이고 test_*.py는 0개다. main의 빈 선택 분기로 exit 2가 되어 최종 T5 report를 만들 수 없는 상태다(소스/디스크 대조이며 이번에 실행한 결과 아님). 기존 probe_cli의 files/background는 실제 공급자·Job·worker 일부를 실행할 수 있지만 작은 protocol_probe schema이고 실제 역할 schema·Lean/Mathlib·예약 등록/발화/해제까지 묶은 T5를 대신하지 않는다.',
        'evidence': [evidence('population-and-corpus.json'), evidence('source-contracts.json'), source('probe_cli.py')],
        'affects': ['run:context.md#G7', 'run:plan.md', source('tests/smoke/__init__.py')],
        'next_action': 'manager는 기존 run_tests T5 경로에 실제 smoke를 구현하는 한정 work를 배정한다. 필요한 정본/말뭉치/미러 쓰기를 포함하고 실제 역할 schema 최소 호출, Job·pythonw, Lean/Mathlib, 시험 전용 예약과 학술 list_sources의 구현·검증 책임을 명시한다. 환경 선행 조건을 해결한 뒤 최종 소스 고정 전에 실행한다.'
    },
    {
        'id': 'F2', 'kind': 'fact',
        'detail': '현재 Codex --version은 0.162.1이고 manifest의 지원 녹화는 0.160.0이다. Claude는 둘 다 2.1.289이나, historical background entry의 미통과 scope/actual_wait_tool=false와 현 background_completed_before_result 계약은 같지 않으므로 원시 event·파일·종료 근거 재판정이 필요하다. corpus 12 entries/20 files/89899 bytes의 파일 선언과 기재 해시는 맞지만 이것은 현재 공급자 접근 성공이 아니다. portable Lean/Lake/Mathlib 자료, Pythonw, scholarly 서버/venv는 존재한다. 인증·모델·계정 한도, 실제 컴파일/예약 권한·MCP 응답은 확인하지 않았다.',
        'evidence': [evidence('environment.json'), evidence('population-and-corpus.json'), source('tests/corpus/manifest.json'), source('probe_cli.py')],
        'affects': ['run:context.md#G7', 'run:plan.md'],
        'next_action': '경계 담당자는 현재 모델·인증·권한을 비밀 비노출 방식으로 확인하고 Codex 현 버전 최소 실호출/command surface를 녹화한다. Claude 재사용은 버전뿐 아니라 현 코드·event 순서·성질을 대조한다. scholarly 구성/예약 부재 조회와 실제 호출/발화 증거를 분리한다. 필요한 외부 조건이 없으면 G7 미충족을 정확히 상신한다.'
    },
    {
        'id': 'F3', 'kind': 'fact',
        'detail': '기존 MUTATION-001~017은 현재 존재하는 130개 파일을 중복 없이 포함한다. 현 LAYERS 1/2/3의 123개 모듈은 전부 포함되지만 adapter 5개와 run_tests.py/test_categories.py는 mutation.run의 module filter에서 제외된다. --only를 붙여도 이 7파일은 선택되지 않는다. 기존 선택 색인은 2026-10-01의 2163 tests/696 files로 조상 검사는 통과하지만 현재 함수·시험 완비성은 보장하지 않는다. 과거 1586 함수는 현 분모가 아니며 pseudo_tested.json도 현재 존재하지 않는다.',
        'evidence': [evidence('population-and-corpus.json'), evidence('source-contracts.json'), source('do_math/layers.py')],
        'affects': ['run:context.md#G6', 'run:plan.md', 'repo:docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json'],
        'next_action': 'manager는 설계 6.3의 layer1/2/3 대상 계약에 따라 7파일의 제외/별도 검증 처분을 명시한다. MUTATION-PLAN 성격의 후속 task가 통과한 fresh T3 뒤 현 함수·rule·trivial·선택 시험 manifest를 확정하고 17 파일 묶음에 대응시킨다. 공유 pseudo 목록 때문에 묶음은 순차 실행한다.'
    },
    {
        'id': 'F4', 'kind': 'issue',
        'detail': '정상 기준 부재가 kill로 통과할 수 있는 정적 반례를 확인했다. mutation.run.fails_unmutated는 _child_run이 돌려준 집합에 시험 ID가 있는지만 저장한다. mutant에서 시험 t가 실패하고 unmutated child 결과가 없어서 {CHILD_NO_RESULT}를 돌려주면 t in failing=False가 되어 broken에서 t가 빠지고, mutant는 killed, baseline_failing=[]가 된다. 다른 문제가 없으면 passed=True다. mutant 자체의 결과 부재는 execution_error로 막지만 원본 경로에는 같은 검사가 없다. loader 오류 문자열도 정상 비교 없이 kill 후보가 되고 child 결과는 실제 testsRun/skip/exit 정상성의 명시 증거가 부족하다. 이번에는 mutation 실행이나 동적 재현을 하지 않았으며 소스 분기와 기존 시험 범위로 판정했다.',
        'evidence': [evidence('source-contracts.json'), source('tests/support/mutation.py'), source('tests/unit/test_mutation.py'), source('tests/boundary/test_mutation_baseline.py')],
        'affects': ['run:context.md#G6', source('tests/support/mutation.py'), source('tests/unit/test_mutation.py'), source('tests/boundary/test_mutation_baseline.py')],
        'next_action': '최종 변이 전에 한정 work task에서 정상 child 결과 부재·수집/환경 오류를 재현하고 증거 실패로 보존하도록 수정한다. 실제 원본 시험 통과만 kill의 정상 기준으로 인정하고 정상/변이 spec·result·exit·실행/skip을 연결한다. 전체 변이를 재현 도구로 쓰지 말고 관련 작은 시험과 실제 child 경계로 검증한다.'
    },
    {
        'id': 'F5', 'kind': 'fact',
        'detail': 'B129 원보고 SHA256과 selected↔rows를 직접 대조했다. 3990건이 누락/중복 없이 완결됐고 3988 passed/1 failed/1 skipped, successful=false, process exit 1, 10724초다. repair 2건 성공과 B130~134의 22/25/26/28/28건 성공은 별도 부분 증거다. B134 green의 862개 Python 소스 해시는 현재와 모두 일치하지만 28건 선택이다. B129와 현재의 Python 파일 차이는 8개다. baseline의 정본 969개 및 지정 source/engine 해시는 현재와 일치하고 작업 전후에도 변하지 않았다.',
        'evidence': [evidence('historical-reports.json'), evidence('source-before.json'), evidence('source-after.json'), 'repo:docs/do-math/시험-재편-2026-09-29/검증/2026-10-06-일반통합-B129/execution.json'],
        'affects': ['run:context.md#C2', 'run:context.md#G4', 'run:context.md#G5', 'run:plan.md'],
        'next_action': 'B129 실패와 WinError1314 skip를 원래대로 유지한다. 필요한 제품/경계 수리 뒤 최종 동일 판본에서 공식 기본 전체 G4와 fresh G5를 완결한다. B134 부분 성공은 해당 28건의 현재판 증거로 재사용하되 전체 성공으로 합산하지 않는다. 비용은 소프트 기준과 실측을 분리한다.'
    },
    {
        'id': 'F6', 'kind': 'issue',
        'detail': 'T4 실행과 adapter 분기 보고의 연결이 아직 준비되지 않았다. run_tests.main은 T3가 tiers에 있을 때만 Measurement를 만들므로 --tier T4 단독은 boundary 시험 결과를 남기지만 설계 5.5가 요구하는 경계 adapter 분기 측정 보고는 만들지 않는다. 실제 포트 계약은 7개 공유 정의/실제 wiring에 연결되어 있으나 예약 계약은 status뿐이고 provider surface 일부는 batch fixture다. T4가 모두 통과해도 T5 실제 등록·공급자 성공으로 확장할 수 없다.',
        'evidence': [evidence('source-contracts.json'), source('tests/support/port_contracts/scheduler.py'), source('tests/boundary/test_operator_schedule_adapter.py'), source('tests/boundary/test_provider_cli_surface.py'), 'repo:docs/do-math/시험-재편-2026-09-29/설계.md'],
        'affects': ['run:context.md#G7', 'run:plan.md', source('run_tests.py')],
        'next_action': 'T4 담당 작업에 실제 경계 전체 선택과 별도 adapter 분기 보고 책임을 함께 명시하고 현재 측정 경로를 구현/검증하거나 원문상 처분을 근거로 결정한다. T3에 T4를 섞어 최종 T3 선택을 바꾸거나 새 옵션이 이미 있는 것처럼 실행하지 않는다.'
    },
]

helper = 'docs/do-math/continuous-development-2026-10-13/phases/001/tasks/gate-readiness/evidence/inspect_sources.py'
actual_checks = [
    ('snapshot before', 'source-before.json', '969개 정본과 baseline source/engine 해시 일치 및 실제 HEAD/dirty 상태를 기록했다.'),
    ('contracts', 'source-contracts.json', '공식 parser 옵션·분기 관문·변이·probe 함수 원문을 AST로 읽어 보존했다. 제품 함수를 실행하지 않았다.'),
    ('population', 'population-and-corpus.json', '17분할/현 layer 모집단/디스크 시험/말뭉치 선언·해시를 조회했다. 초기 도우미는 pseudo_tested.json 존재를 가정해 FileNotFoundError로 끝났으며, 파일 부재를 명시 기록하도록 자기 evidence 도우미만 고친 뒤 재실행했다.'),
    ('environment', 'environment.json', '7개 안전 버전 명령 모두 exit 0. 각 executable/argv/cwd/exit/stdout/stderr/경과를 보존했다. 인증·비용 실호출·설치·컴파일·예약 변경은 하지 않았다.'),
    ('reports', 'historical-reports.json', 'B129/repair와 B130~B134 원보고를 해시·실제 선택/결과 집합·현재 Python 해시로 대조했다. 원본 보고는 수정하지 않았다.'),
    ('snapshot after', 'source-after.json', '작업 전후 정본 해시 차이 0. 원자료/engine도 baseline과 일치한다.'),
]
checks = [{'command': f'& "{PYTHON}" -B "{helper}" {mode}', 'cwd': 'repo:.', 'result': 'pass', 'exit_code': 0, 'evidence': [evidence(filename)], 'detail': detail} for mode, filename, detail in actual_checks]
checks.append({'command': f'& "{PYTHON}" -B "docs/do-math/continuous-development-2026-10-13/phases/001/tasks/gate-readiness/evidence/verify_preparation.py"', 'cwd': 'repo:.', 'result': 'pass', 'exit_code': 0, 'evidence': [evidence('proposal-validation.json')], 'detail': '9개 제안 명령의 실제 script/옵션, 전체 기본 선택과 fresh T3 조건, corpus ID 파일, 분할 집합·해시·원보고 대응을 정적으로 확인했다. 실행 인수의 중괄호는 후속 배정 때 결속할 값이며 실모델/출력 경로가 이미 확정되었다는 뜻이 아니다.'})
for row in command_rows:
    if row['id'] not in ['ordinary', 'fresh-t3', 'mutation-every', 't4', 't5', 'provider-codex', 'provider-claude']:
        continue
    argv = [PYTHON, *row['interpreter_arguments'], row['script'], *row['arguments']]
    command = '& ' + ' '.join("'" + part.replace("'", "''") + "'" for part in argv)
    checks.append({'command': command, 'cwd': 'repo:.', 'result': 'not_run', 'exit_code': None, 'evidence': [evidence('gate-readiness.json')], 'detail': '이번 objective는 준비 분석이며 무거운 검사·변이·공급자/예약/네트워크 비용 스모크를 실행하지 않도록 지정했다. 출력·최종판·모델 값은 후속 task에서 결속한다. 실제 성공/실패/시간을 주장하지 않는다.'})

report = {
    'status': 'complete',
    'narrative': 'A1~A4의 실행 준비 분석을 마쳤다. 공용 context/plan/phase/seams와 자기 objective, 사용자 결정·baseline·시험 지침·설계의 실행/변이/경계 계약, 단계표의 관문/17분할/후속 부분 보고, B129 원보고를 현재 소스까지 따라 대조했다. gate-readiness.json에 공식 기본 전체·fresh T3·전체 함수 변이·T4/T5 명령, 필수 입력, 출력/판정 필드, 판본·재사용·대기 절차를 기록했다.\n\n실제 준비를 막는 것은 빈 T5 선택, 현재 Codex와 녹화판 차이, 변이 정상 기준의 결과 부재 처리, 분할의 7개 도구 대상 밖 파일 처분, T4 adapter 측정 연결이다. 이것들을 이미 성공한 것으로 처리하지 않고 근거와 다음 책임으로 남겼다. 현재 공급자 인증·모델·권한과 Mathlib/예약/학술 실제 연쇄는 미확인이다. 설치/버전 확인과 실호출 성공을 분리했다.\n\nB129 실패 보고와 뒤의 부분 수리를 합산하지 않았다. B134의 28개 성공은 현재 Python 판본과 일치하지만 전체 관문 성공은 아니다. 현재 정본 969개는 baseline과 일치하고 작업 전후 변경이 없다. 쓰기는 자기 report/evidence로 한정했으며 제품·시험/runner import, --list, 전체 검사, T3, 변이, 실공급자 호출, 설치/다운로드/컴파일, 예약 변경, Git 변경, graphify 갱신은 하지 않았다. 보고의 complete는 이 준비 task의 완료이며 G4~G8의 실행 완료나 프로젝트 종료를 뜻하지 않는다.',
    'acceptance': [
        {'id': 'A1', 'result': 'pass', 'detail': 'run_tests/branch_gate/t3_store/selection/mutation 및 실제 포트·corpus 소비 코드를 읽어 9개 실제 인터페이스 명령을 정리했다. default 전체를 수동 폴더 목록으로 축소하지 않았고 --full, outputs/selection/report 필드와 empty/불완결/기능 실패를 구분했다. T5 현 구현 공백과 T4 측정 공백도 실행 준비 상태에 포함했다.', 'evidence': [evidence('gate-readiness.json'), evidence('source-contracts.json'), evidence('proposal-validation.json')]},
        {'id': 'A2', 'result': 'pass', 'detail': '17분할 130파일↔현 변이 대상 123모듈의 집합을 대조했다. 함수/rule/trivial/진입 시험 분모는 통과한 fresh T3 뒤 확정하도록 했고 과거 함수 수를 채택하지 않았다. normal-baseline 실패·부재·loader, not_executed, survived, execution_error를 실제 필드에 연결하고 정상 기준의 정적 반례를 후속 수리로 명시했다.', 'evidence': [evidence('gate-readiness.json'), evidence('population-and-corpus.json'), evidence('source-contracts.json')]},
        {'id': 'A3', 'result': 'pass', 'detail': '실행 파일 절대 경로와 argv/exit/stdout을 기록한 7개 버전 명령, 설치 의존 metadata, Lean/Mathlib/학술 지원 파일 존재, 말뭉치 12항목의 버전/해시/소비자를 확인했다. Codex 버전 차이와 아직 미확인 모델·인증·권한·컴파일·MCP 조건을 구체적으로 분리했다. 인증 비밀은 읽지 않았고 금지한 실호출/환경 변경을 수행하지 않았다.', 'evidence': [evidence('environment.json'), evidence('population-and-corpus.json'), evidence('gate-readiness.json')]},
        {'id': 'A4', 'result': 'pass', 'detail': 'B129 원보고/실제 종료기록/repair와 B130~134 원보고를 대조했다. 마지막 부분 성공의 현 판본 일치와 전체 재실행 필요를 구분했다. source-before/after, workers<=3·단일 검사 묶음, 실제 session 종료와 관찰 만료 구분, 공유 읽기, skip 처분, 변경 시 무효화·녹화 재사용 및 실측/소프트 비용 기준을 9단계 절차로 제시했다.', 'evidence': [evidence('historical-reports.json'), evidence('source-before.json'), evidence('source-after.json'), evidence('gate-readiness.json')]},
    ],
    'changes': [], 'seams': [], 'findings': findings, 'checks': checks,
}
(OUT.parent / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Wrote report.json: complete (preparation task only).')
