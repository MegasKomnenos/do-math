"""Read existing sources; write closure-map evidence only. No product imports or tests."""
from __future__ import annotations

import collections
import ast
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/001/tasks/closure-map/evidence'
OLD = REPO / 'docs/do-math/시험-재편-2026-09-29'
BOARD = OLD / '단계-전환표-2026-10-03.json'
SCRIPTS = REPO / '.claude/skills/do-math/scripts'
PATH_CORRECTIONS = {
    '.claude/skills/do-math/scripts/tests/flows/test_provider_close_native_storage.py':
    '.claude/skills/do-math/scripts/tests/flows/test_provider_native_storage.py',
}
TEST_CORRECTIONS = {
    'flows.test_provider_close_native_storage.NativeStorageTests.test_native_numbers_and_public_blocks_survive_actual_runner_and_repository':
    'flows.test_provider_native_storage.NativeStorageTests.test_native_numbers_and_public_blocks_survive_actual_runner_and_repository',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    path = Path(path).resolve()
    try:
        return 'run:' + path.relative_to(RUN).as_posix()
    except ValueError:
        return 'repo:' + path.relative_to(REPO).as_posix()


def resolve(value):
    value = str(value).replace('\\', '/')
    if value.startswith('repo:'):
        return REPO / value[5:]
    if value.startswith('run:'):
        return RUN / value[4:]
    p = Path(value)
    if p.is_absolute():
        return p
    if value.startswith(('tests/', 'do_math/')):
        return SCRIPTS / value
    if '/' not in value and value.endswith('.py') and (SCRIPTS / value).is_file():
        return SCRIPTS / value
    if value.endswith('.json') and '/' not in value:
        return OLD / value
    return REPO / value


def binding(value, selector=None, recorded_sha=None):
    p = resolve(value)
    result = {'reference': ref(p), 'exists': p.is_file()}
    if selector:
        result['selector'] = selector
    if p.is_file():
        result['sha256'] = sha(p)
    if recorded_sha:
        result['recorded_sha256'] = recorded_sha
        result['matches_recorded_sha256'] = result.get('sha256') == recorded_sha
    return result


def walk(value, pointer=''):
    if isinstance(value, dict):
        yield pointer, value
        for key, child in value.items():
            yield from walk(child, pointer + '/' + str(key))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, pointer + '/' + str(i))


board = read(BOARD)
index = read(RUN / 'sources/requirements-index.json')
baseline = read(RUN / 'sources/baseline.json')
cw = board['current_work']
ie = cw['independent_execution']
tasks = ie['plan']['tasks']
p2_path = OLD / board['stage2']['p2_bindings']
p2 = read(p2_path)
task_by_id = {t['id']: t for t in tasks}
originals = {
    'stage1': {r['id']: r for r in board['obligations']},
    'stage2': {r['id']: r for r in board['stage2']['eleven_obligations']},
    'preservation': {r['id']: r for r in board['preservation']},
    'p2': {r['id']: r for r in p2['rows']},
}
current_rows = {r['id']: r for group in ['stage1', 'stage2'] for r in cw[group]}

# This measures edition equality, not semantic correctness.
snapshot = []
for group in ['source_files', 'engine_files', 'product_files']:
    for r in baseline[group]:
        snapshot.append({'group': group, **binding(r['path'], recorded_sha=r['sha256'])})
git_head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
write('source-comparison.json', {
    'observed_at': datetime.now(timezone.utc).isoformat(),
    'baseline_head': baseline['head'], 'current_head': git_head,
    'interpretation': 'HEAD 변화와 제품 판본 변화를 구별한다. 파일 바이트의 일치만 확인하며 의미 검증을 뜻하지 않는다.',
    'files': snapshot,
    'changed_or_missing': [x for x in snapshot if not x['matches_recorded_sha256']],
    'index_authority': binding(BOARD, recorded_sha=index['authority_sha256']),
    'index_p2': binding(p2_path, recorded_sha=index['p2_source_sha256']),
})

# A compact catalog of the original integration claims, with actual report bytes.
# No raw execution is repeated. Reading an outcome does not certify assertion strength.
catalog = {}
report_catalog = {}
raw_inspect_ids = {'B21', 'B36', 'B37', 'B44', 'B55', 'B72', 'B73', 'B107', 'B108', 'B109',
                   'B115', 'B116', 'B117', 'B118', 'B119', 'B120', 'B121', 'B122',
                   'B129', 'B130', 'B131', 'B132', 'B133', 'B134'}
hash_cache = {resolve(x['reference']): x.get('sha256') for x in snapshot}


def current_hash(path):
    path = path.resolve()
    if path not in hash_cache:
        hash_cache[path] = sha(path) if path.is_file() else None
    return hash_cache[path]


def report_record(r, raw=False):
    if not any(k in r for k in ('complete', 'successful', 'counts')):
        return None
    p = resolve(r['path'])
    if not p.is_file() or p.suffix != '.json':
        return None
    try:
        key = ref(p)
    except ValueError:
        return None
    if key not in report_catalog:
        report_catalog[key] = binding(p, recorded_sha=r.get('sha256'))
    record = report_catalog[key]
    if raw and 'raw_summary' not in record:
        data = read(p)
        if isinstance(data, dict):
            summary = {k: data[k] for k in ['complete', 'successful', 'counts', 'total_seconds', 'changed_during_run'] if k in data}
            if isinstance(data.get('selected'), list):
                summary['selected_count'] = len(data['selected'])
            files = data.get('source_sha256', {})
            comparison = []
            if isinstance(files, dict):
                for name, recorded in files.items():
                    if isinstance(recorded, str):
                        path = resolve(name)
                        try:
                            comparison.append({'reference': ref(path), 'recorded_sha256': recorded,
                                               'current_sha256': current_hash(path),
                                               'matches': current_hash(path) == recorded})
                        except ValueError:
                            pass
            summary['current_source_comparison'] = {
                'compared_count': len(comparison),
                'changed_or_missing': [x for x in comparison if not x['matches']],
            }
            # Retain exact outcomes for the candidate IDs used by this analysis.
            candidate_ids = {x for t in tasks for x in t.get('candidate_test_ids', [])}
            candidate_ids.update(TEST_CORRECTIONS.values())
            outcomes = []
            for _, node in walk(data):
                if node.get('id') in candidate_ids and 'outcome' in node:
                    outcomes.append({k: node[k] for k in ['id', 'outcome', 'seconds'] if k in node})
            summary['mapped_outcomes'] = outcomes
            record['raw_summary'] = summary
    return key


for key, value in cw.items():
    if not isinstance(value, dict) or not re.fullmatch(r'B\d+', str(value.get('id', ''))):
        continue
    entry = {'id': value['id'], 'selector': 'current_work.' + key,
             'scope': value.get('scope', ''), 'state': value.get('state', ''),
             'reports': [], 'historical_report_locations': [],
             'limits': value.get('limits', value.get('remaining', '')),
             'semantic_review_here': False}
    scan = value
    if key == 'independent_execution':
        scan = value['reports']
    for pointer, node in walk(scan):
        if 'path' in node and ('sha256' in node or 'counts' in node):
            report = report_record(node, raw=value['id'] in raw_inspect_ids)
            if report and report not in entry['reports']:
                entry['reports'].append(report)
            if not report and any(k in node for k in ('complete', 'successful', 'counts')):
                entry['historical_report_locations'].append({
                    'board_selector': entry['selector'] + pointer.replace('/', '.'),
                    'historical_locator': node['path'], 'currently_exists': resolve(node['path']).is_file(),
                    'recorded_sha256': node.get('sha256'), 'recorded_counts': node.get('counts'),
                    'raw_read_here': False,
                    'limit': '원보고를 재사용 판정한 것이 아니라 보드가 기록한 위치/주장이다. 보고서 evidence 참조로 사용하지 않는다.',
                })
    catalog[entry['selector']] = entry

for c in ie['prior_review']['completed_review']['commits']:
    for r in c['original_evidence']:
        report_record(r, raw=True)

write('evidence-catalog.json', {
    'board': binding(BOARD), 'integrations': catalog, 'reports': report_catalog,
    'limit': 'integration의 scope/state는 과거 주장이다. raw_summary는 실제 원보고를 읽은 결과이며 현재 의미 검토나 전체 성공을 뜻하지 않는다. 변경 파일은 부분 원보고를 최종 판본 근거로 확대하지 못함을 나타낸다.',
})

print(json.dumps({'snapshot_files': len(snapshot), 'baseline_changes': sum(not x['matches_recorded_sha256'] for x in snapshot),
                  'head': git_head, 'integration_records': len(catalog), 'report_files': len(report_catalog),
                  'raw_reports_read': sum('raw_summary' in x for x in report_catalog.values())}, ensure_ascii=False))

# Analyst decisions. These are deliberately separate from mechanically extracted claims.
FINAL = '최종 판본 연결만 필요'
REPAIR = '확정된 수리 필요'
QUESTION = '판정 질문 필요'
INSUFFICIENT = '현재 근거 부족'
CAT_REF = ref(OUT / 'evidence-catalog.json')
BOARD_REF = ref(BOARD)
POLICY = ref(RUN / 'sources/user-decisions.md')

# Extra current records prevent old top-level gaps from overriding later repairs.
extra_ids = {
 '1-A': ['B85'], '1-D': ['B44', 'B129'], '1-E': ['B22', 'B116', 'B117'],
 '9-A': ['B85', 'B117', 'B118'], '9-B': ['B86', 'B89'], '11-A': ['B21', 'B109', 'B129'],
 '11-B': [f'B{i}' for i in range(90,110)], '13-C': ['B115'] + [f'B{i}' for i in range(119,123)] + [f'B{i}' for i in range(130,135)],
 'K-27': ['B36'], 'K-38': ['B37'], 'K-72': ['B37'], 'K-75': ['B36','B37','B80'],
 'K-71': ['B129'], 'A-31': ['B21','B107','B109'], 'B-32': ['B72','B73'],
 'A-27': ['B81','B82','B84'], 'B-14': ['B76'], 'B-15': ['B76'], 'B-09': ['B74','B75'],
 'C-03': ['B16','B35'], 'C-19': ['B17','B18','B71'], 'C-20': ['B33'],
}
id_to_key = {v['id']: k for k,v in catalog.items()}

meaning_overrides = {
 '1-A': '원문 인용은 필수 필드를 말하지만 설계 3.3/A20은 역방향을 수신 검사가 아는 필수+선택 필드 전체로 넓혔다. 원문을 바꾸지 않고 이 현행 계약을 추가 적용한다. A22의 저장 필드 이름 검사는 실제 생산/쓰기 도달을 대신하지 않는다.',
 '1-B': '역사 저장 대역의 이름을 복원하지 않는다. 현재는 실제 ResearchRepository와 Git 외부 포트 대역으로 저장 검증을 보존한다(설계 4.3). 남은 판정은 실제 쓰기 분기의 검증 도달이다.',
 '2-D': '7-A의 지정 사건 열에 붙는 공통 성질이다. 별도 전이 기계를 중복 구현하지 않는다.',
 '7-A': '역사 메모리 저장 대역은 현재 실제 저장 계약 경로로 대체되었다. 폐기한 run timeout을 사건 알파벳 이름 때문에 부활시키지 않는다.',
 '6-A': '폐기된 run 기한과 시험/변이 강제 종료는 재도입하지 않는다. 현행 호출 창·관찰 국면·사건 시각·대화 임대의 의미는 유지한다. 2026-10-04 정정 우선.',
 '9-A': '초기 하위 프로세스 14곳은 역사 수치다. R17의 네 명령 생산자 완료와 R18의 공통 경계 전건 재사용 판단을 구별한다.',
 '13-C': 'B130~B134 뒤에도 상위 remaining은 B122에서 멈춰 있다. 최신 세부 task/생산자 기록을 우선 연결한다. 정책 이름 존재는 D-06 조건 의미 검증이 아니며 stdin 역할 문서 바이트를 도구 출력 한도로 오독하지 않는다.',
 'K-01': 'SHARDS 자체가 아니라 수집 누락·유령 거부를 보존한다. 현행 폴더 기반 분류로 이행했다.',
 'K-02': '뒤 조각으로 조용히 배정되는 역사 구멍을 보존할 요구가 아니다. 수동 중복 등록 제거/거부가 옳은 방향이다.',
 'K-06': 'T3 측정 자료 증분 재사용과 시험 결과 캐시를 구별한다. 최종 T3는 --full이며 현재 실행 결과를 재사용하지 않는다.',
 'K-10': 'Job 소유/진행/임시 경로/종료 보고는 보존하되 timeout과 시간에 따른 Job 강제 종료는 최신 사용자 정정으로 폐기됐다.',
 'K-11': '시험 격리 timeout도 폐기됐다. 실제 Lean의 무제한 계산 및 실제 종료/취소 계약과 구별한다.',
 'K-24': '실제 프로세스가 대상인 경계만 실프로세스로 확인한다. 1·2층 흐름 통과를 그 대체로 쓰지 않는다.',
 'K-28': '시작 정확히 1회·소유 자식 정리는 보존한다. 옛 10초 제한을 실행기 강제종료로 복원하지 않는다.',
 'K-36': '폐기된 StateStore/NoRepository를 복원하지 않는다. 실제 저장 읽기·검증을 외부 Git 포트만 대역으로 둔 경로로 보존한다.',
 'K-37': '옛 published_state=None 구현 대신 실제 게시 head/정확 JSON 동등성으로 무게시를 구별한다. bool과 int를 동등하게 취급하지 않는다.',
 'K-38': '역사 strength-gap 뒤 B37의 명시 Lean 사실/전체 reload 수리가 있다. 과거 signature_hash 오류를 되살리지 않고 현행 선언 계약을 대조한다.',
 'K-46': '정확한 해시/수송/동시 실행 성질과 옛 120초 운영 상한을 구별한다. 시간만으로 기능 실패 판정하지 않는다.',
 'K-65': '고정 sleep 회피·시계 주입은 유지한다. 조건/단계 상한과 경과 시간 강제 종료를 혼동하지 않는다.',
 'K-66': '실경계 분류와 실제 소유를 보존한다. historical_next_action의 phase timeout 표현은 폐기된 수단이다.',
 'K-68': '현재 폴더 기반 수집을 쓰므로 SHARDS 재도입은 필요 없다. 모듈의 성질 중심 명명은 별도 판단한다.',
 'A-27': '역사 timeout/event_driven 기대를 그대로 되살리지 않는다. 현재 관찰 규칙의 선언 도구 국면과 밀린 종료 사건의 의미로 반례를 대응한다.',
 'A-31': 'P2 파일의 plan1/Stage2필수 표시는 B21 및 B107~B109 이후 현재 결함 증거가 아니다. 빈 준비 호출0 수리는 재구현하지 않는다.',
 'B-32': 'P2 원문의 필수 분류 공백을 최신 B72/B73이 다뤘다. 의도적으로 필수인 goal의 overflow를 실패 기대값으로 바꾸지 않는다.',
}

k_questions = {
 'K-01':'폴더 누락·유령·누락 수집 모듈을 넣으면 유효 ID와 함께 요청해도 실행 전 거부되는가?',
 'K-02':'현재 폴더 분류에는 중복 귀속 경로가 없는가; 수동 등록이 남아 있다면 중복을 거부하는가?',
 'K-03':'한 모듈 import 오류가 유효한 다른 모듈과 함께 수집될 때 종료 2와 고유 사유를 유지하는가?',
 'K-04':'유효 ID+미등록 ID를 함께 요청한 반례가 전체 선택을 거부하는가?',
 'K-05':'빈 match/selection에서 과거 측정 재사용 건을 신규 pass로 집계하지 않는가?',
 'K-06':'비어 있지 않은 출력 폴더를 거부하고 --full의 실제 실행 전건과 증분 측정 재사용을 구분하는가?',
 'K-07':'setUpClass와 setUpModule 각각의 실패가 요청된 모든 시험을 not_run으로 남기고 successful=false인가?',
 'K-08':'뒤 시험 시작 전에 최초 실패의 complete=false 파일이 실제 게시되는 관찰이 있는가?',
 'K-09':'실행 중 제품 또는 시험 .py 변경을 source_sha256으로 거부하는 음성 검증이 있고 해시 대상이 현행 문서와 일치하는가?',
 'K-10':'실제 Job 격리에서 시작/완료 보고, TMP/TEMP, 자식 회수, 원 종료 코드를 잃지 않는가?',
 'K-11':'실제 Lean의 완료를 기다리는 경로에서 옛 격리 timeout이 남지 않았는가?',
 'K-12':'실패·skip subTest의 부모 집계가 pass가 되지 않고 하위 이유가 보존되는가?',
 'K-15':'연속 요청한 두 템플릿 사본이 같은 절대 경로이고 이전 엔진을 동시 재사용하는 caller가 없는가?',
 'K-16':'shared 신뢰 파일의 전체 stat 지문이 restore 전후 동일함을 직접 단언하는가?',
 'K-17':'기본값을 포함한 JSON key와 실제 builder 인자가 같고 configure로 늦게 바꾸는 소비자가 없는가?',
 'K-18':'한 key의 빌드 실패 뒤 같은 프로세스에서 재시도 없이 key를 포함한 AssertionError가 나는가?',
 'K-19':'디스크 캐시를 재사용하지 않고 만료/clock high-water 시험이 공개 입력·시계를 쓰는가?',
 'K-20':'restart/restore 때 readiness·lifecycle·solution basis 등 현재 메모리 cache가 모두 재설정되는가?',
 'K-21':'템플릿 복사 직전 미종료 실행·예약이 없는지 실제 guard가 확인하는가?',
 'K-23':'활성화 연결과 solved_instance의 실제 공개 경로가 현재 대응 시험에서 도달되는가?',
 'K-24':'셸 종료·인코딩·pythonw·Job·소유자 식별·백그라운드·기동을 검사하는 현행 boundary가 실제 자식을 쓰고 단순 잠금 경합은 불필요한 자식을 없앴는가?',
 'K-25':'비용을 줄인 각 해당 hunk에서 마지막 관찰 뒤 호출 수가 증가하거나 대역 검사에만 도달하는 경로를 놓치지 않았는가?',
 'K-27':'B36의 정상 bound 응답은 binding/accepted를 강제하고 의도한 unbound·rejected 표본만 명시 기대를 쓰는가?',
 'K-28':'실제 Job 시작 정확히 1회·잔여 활성 프로세스 0·외부 래퍼 중첩 방지의 보고/단언이 있는가?',
 'K-29':'source_ref의 부재·잘림·해시/경로 손상을 실제 read_fixture_context caller와 role receiver가 고유 사유로 거부하는가?',
 'K-30':'고정 입력에 없는 개정 target을 seal_response의 실제 caller로 넣어 거부하는가?',
 'K-31':'계약 구조/비어 있는 보고/미제공 모델평가/원문 불일치/두 관점 밖 scope의 다섯 음성이 각 실제 caller를 지나는가?',
 'K-32':'repair·형식증거 전 감사·효력 없는 최종 평가·예상 밖 역할·non-live 운영점검을 대역이 즉시 거부하는가?',
 'K-33':'paused/closed/waiting 및 단계 상한에 걸리는 공개 drive가 상태 요약과 함께 실패하는가?',
 'K-34':'공개 활성화 중 금지된 formal 호출이 guard에 실제 도달하면 준비 실패로 드러나는가?',
 'K-35':'send_control rejected 및 initialize rejected/active 미도달이 준비 caller에 전파되는가?',
 'K-36':'actual repository/reader/snapshot 경로가 생산 결과 저장과 소비를 검사하고 옛 저장 대체가 남아 가리지 않는가?',
 'K-37':'게시 head·정규화된 전체 views·Unicode·bool/int 차이가 정확한 no-op 판정과 연결되는가?',
 'K-38':'B37의 두 기본 소스 선언 type/value·비어 있지 않은 dependency facts·전체 결과가 실제 receiver reload와 같은가?',
 'K-39':'현재 fixture/manifest/제어 본문이 synthetic 경계를 실제 소비 결과까지 유지하는가?',
 'K-41':'합성 toolchain checker identity가 현재 formal 코드와 일치하며 설치 변경은 실제 경계에서 거부되는가?',
 'K-42':'설정 unapproved-config-command와 승인된 명령의 차이가 실제 compile 소비에서 유지되는가?',
 'K-45':'소유 스레드 밖 저장 거부·head 전진·게시 후 stop 순서를 현재 _save caller에서 각각 관찰하는가?',
 'K-46':'동시 호출·조사 source hash/실행계약 불상속·reject/quota 수송의 현재 대응자가 실제 같은 성질을 유지하는가?',
 'K-48':'실제 자식 읽기에서 held가 비어 있지 않고 reached/held 두 값으로 비밀 비도달을 판단하는가?',
 'K-49':'후보 결속→봉인→issued schema 검증→제출의 실제 경로와 발행 schema bytes/hash가 receiver input_hashes에 같은가?',
 'K-51':'review_items/OPERATORS/PROFILE_CONFIG가 현행 제품 정의를 import하며 검사하려는 계산 결과는 독립 기대값인가?',
 'K-52':'admitted/cycle 결정/봉인통과/유예의 기대 결말을 실제 각 helper caller가 확인하고 수송이 필요한 곳은 Sim으로 연결하는가?',
 'K-54':'최종 검사 시작~종료 manifest가 같고 실행 중 제품·시험 편집이나 checkout이 없었는가?',
 'K-61':'현재 실제 Lean 실행의 command/toolchain fingerprint와 DO_MATH_KNOWLEDGE_TEST_LEAN 환경이 어떤 판본인가?',
 'K-62':'직접 unittest 종료값 대신 공식 runner의 선택 전건 outcome과 종료가 실제 인도 근거인가?',
 'K-64':'겹치는 변경의 시험 이름과 실제 입력·관찰 시점·기대값이 동일한 한 성질을 말하는가?',
 'K-65':'제품/시험의 시간 equality 대상이 같은 주입 clock을 쓰며 고정 sleep에 기대지 않는가?',
 'K-66':'실제 Lean/프로세스 대상이 현행 boundary에 배치되어 실제 launch/정리 보고로 검증되는가?',
 'K-67':'제품에서 가져온 이름/정의와 독립적으로 적어야 할 기대 계산값을 해당 변경의 단언에서 구별했는가?',
 'K-68':'새 모듈이 성질/제품 이름으로 분류되며 현행 폴더 수집 누락을 실패로 드러내는가?',
 'K-69':'시험 간 import 대신 실제 공유 support를 쓰며 inherited method를 가짜 standalone testID로 보고하지 않는가?',
 'K-70':'재검토할 해당 B hunk의 실제 red 원보고/source와 green이 같은 반례를 대응시키는가?',
 'K-71':'해당 음성의 정확 오류/사유와 정상 대조가 고정됐는가; B129 Git 거부 2개 수리도 현 판본에 남았는가?',
 'K-72':'B37의 기본 Lean 사실이 실제 컴파일 자료에서 왔고 변경된 선언에 암묵 성공을 부여하지 않는가?',
 'K-73':'해당 수리의 정확 reversal 또는 현재 대상 변이/정상 baseline이 실제 실패로 검출됨을 보여 주는가?',
 'K-74':'현재 계약 변경의 모든 관련 fake caller가 원 입력/값/receiver/시점을 보존하고 단언을 느슨하게 하지 않았는가?',
 'K-75':'B36/B37 및 B80 비용 변경의 앞뒤 실제 준비 경로·시작 상태·수신 전체값이 동일 성질을 유지하는가?',
 'K-76':'각 결과가 실호출/대역 상태/실프로세스·파일/문서 읽기 중 무엇을 입증했는지 구별돼 있는가?',
 'K-77':'최초 실패 원보고가 남아 있고 후속 green의 고정 소스/환경 및 보조 코드 실패 처분이 연결돼 있는가?',
 'K-78':'모든 현재 저장 생산 분기의 양방향 필드 대응과 실제 검증 켜진 receiver 값/도달이 연결되는가?',
}
p2_questions = {
 'A-23':'INIT/RESULT 복수 구간, task-notification, 후속 실패/절단의 현재 parser 기대가 원문과 같고 최신 실제 CLI 말뭉치까지 연결되는가?',
 'A-27':'B81의 국면 행렬이 선언 도구 20분·선언 없음·밀린 종료 사건의 원래 세 반례를 현행 규칙으로 보존하는가?',
 'A-31':'B21과 현재 EmptyPreparationDefectTests의 plan0 및 dispatch 대상 없는 reason-only 거부를 원래 두 잘못된 양성 ID에 각각 연결했는가?',
 'A-42':'현재 시험이 capacity=0뿐 아니라 work_calls 누적 budget 소진에서도 독립 운영풀 계획/진단을 허용하는가?',
 'B-02':'현재 setup 실제 생산값이 build_kind=clean 합성 보충 없이 등록되고 실패 compile/unknown field가 거부되는가; 실 Lean 끝단은 어느 G7 자료인가?',
 'B-09':'B74/B75의 관리 정보 불변·내용 stale·후속1회가 정상 terminal producer에서 성립하고 synthetic closed 이행 사례도 교정됐는가?',
 'B-14':'B76의 current inventory/manifest가 실제 채택 root 전건을 쓰며 파일 1개 누락·목록 밖 추가·검색 경로를 각각 거부하는가?',
 'B-15':'verified 표지와 무관하게 bytes/exit/부재 경로/command/toolchain의 원문 축 모두를 실제 validation 소비자가 확인하는가?',
 'B-32':'B72/B73이 실제 prepare_role_input→fit_context의 governance/action 필수와 goal/policies 선택 입력(각800,예산1200)을 원래 P2 ID에 연결했는가?',
 'C-03':'실제 tracker open→boundary→rule proposal→close→저장/restart가 현행 닫힌 schema를 통과하고 control_call_ids 사본이 없는가?',
 'C-19':'문서 grant 그대로 trust roles 없이 check 두 번→activate 및 중간 revoke가 실제 owner/Job과 같은 권한 판정을 사용하는가?',
 'C-20':'같은 repair identity에서 미판정 refused/HOLD는 기회를 안 쓰고 판정 완료 HOLD/failed는 1회를 쓰는 양·음성이 실제 collector에 연결되는가?',
}

def task_inputs(t):
    result=[]
    for x in t.get('inputs', []):
        path=PATH_CORRECTIONS.get(x['path'],x['path'])
        if resolve(path).is_file():
            entry=binding(path,x.get('section'))
            if path!=x['path']: entry['historical_locator_corrected']=x['path']
            result.append(entry)
    return result


def test_bindings(ids):
    out = []
    for test_id in dict.fromkeys(ids):
        historical_id=test_id
        test_id=TEST_CORRECTIONS.get(test_id,test_id)
        parts = test_id.split('.')
        p = SCRIPTS / 'tests' / ('/'.join(parts[:-2]) + '.py')
        row = {'test_id': test_id, 'meaning_checked_here': False}
        if test_id!=historical_id: row['historical_test_id']=historical_id
        if p.is_file():
            row.update(binding(p))
        else:
            row['unresolved_module_locator'] = str(p.relative_to(REPO)).replace('\\', '/')
        out.append(row)
    return out


rows = []
for indexed in index['rows']:
    group, rid = indexed['group'], indexed['id']
    old = originals[group][rid]
    linked = [t for t in tasks if rid in t['requirement_ids']]
    keys = list(dict.fromkeys(k for t in linked for k in t.get('existing_evidence_keys', [])))
    keys += [id_to_key[x] for x in extra_ids.get(rid, []) if x in id_to_key and id_to_key[x] not in keys]
    props = []
    for key in keys:
        if key in catalog:
            props.append({'property': catalog[key]['scope'], 'evidence_catalog_selector': key,
                          'review_level': '기존 통합 기록의 한정 성질; 이 task에서 의미 검토를 새로 완료한 것은 아님'})
    if group in ['stage1','stage2']:
        remaining = current_rows[rid]['remaining']
        question = ' / '.join(t.get('unresolved_decision_question', t['exit_condition']) for t in linked)
        if rid=='1-A':
            question += ' / 설계 A20에 따라 수신 검사가 아는 선택 필드까지 생산 분기와 역방향 대응하는가?'
        original = indexed['original']
        historical = {k: old[k] for k in ['historical_credit','historical_gap','historical_gap_type','current_update'] if k in old}
        classification = FINAL if rid in ['1-D','11-A','11-B'] else REPAIR if rid=='13-C' else INSUFFICIENT if rid=='9-B' else QUESTION
        if rid=='9-A':
            remaining = 'R17/B85/B117/B118의 한정 성질은 유지. R18 외부 호출 전건의 현행 추가/누락 유무를 대조한 뒤 G4~G7에 연결한다. 상위 implementation_reviewed만으로 R18 전건을 닫지 않는다.'
        if rid=='13-C':
            remaining = 'DOC-RETURN-PURE/CLI 및 ROLE의 manifest/복원/profile_selection은 완료 기록 재사용. 남은 _context·REVIEW·TRUST 반환 결속 교체, 단독/조합 이름·D-06 정책 의미·실제 읽기 출력 한도 판정.'
        tests_for_row = [x['id'] for x in old.get('test_bindings', [])]
        tests_for_row += [x for t in linked for x in t.get('candidate_test_ids', [])]
    elif group=='preservation':
        original = indexed['original']
        historical = {k: old[k] for k in ['historical_status','historical_next_action','current_update','disposition'] if k in old}
        props.insert(0, {'property': original, 'historical_claim': old['historical_status'],
                         'review_level': '역사 처분/강도 분류; 현재 의미 증명으로 승격하지 않음'})
        question = k_questions[rid]
        remaining = '이 항목의 현행 소비자와 정확 단언/원보고를 위 질문으로 판정. 기존 처분의 유지/이동/은퇴와 동작 증명을 구별한다.'
        classification = INSUFFICIENT if rid in ['K-61','K-64','K-70','K-73'] else QUESTION
        tests_for_row = old.get('actual_test_ids', [])
    else:
        original = indexed['historical_expectation']
        historical = {k: old[k] for k in ['normal_expected_from_historical_prep','counterexample_from_historical_prep','historical_classification'] if k in old}
        props.insert(0, {'property': original, 'historical_claim': old['historical_classification'],
                         'review_level': '역사 정상 기대값과 testID 대응; 현재 반례의 의미 검증은 미완료'})
        question = p2_questions[rid]
        remaining = '원래 P2 반례의 현재 생산자·수신자·기대값 연결 및 실제 판본 증거. 추가 KD 사례와 원래 12 ID를 섞지 않는다.'
        classification = INSUFFICIENT if rid=='A-42' else QUESTION
        tests_for_row = [x['id'] for x in old['tests']]
    if not props:
        props = [{'property': old.get('historical_credit', original),
                  'review_level': '원문/역사 binding만 확인. 이 항목 전건의 현재 의미를 검토 완료로 표시하지 않음'}]
    sources = [binding(BOARD, indexed['baseline_selector']), binding(RUN/'sources/requirements-index.json', f"rows[group={group},id={rid}]")]
    source = indexed['source']
    if isinstance(source, dict):
        if resolve(source['path']).is_file():
            sources.append(binding(source['path'], str(source.get('line_start',source.get('line','')))))
    elif isinstance(source, str):
        sources.append(binding(source))
    elif group=='preservation':
        sources.append(binding(OLD/'조사/대역-사각지대.md', '3부 '+rid))
        ledger = old.get('disposition',{}).get('ledger')
        if ledger and resolve(ledger).is_file(): sources.append(binding(ledger, 'id='+rid))
    if group=='p2': sources.append(binding(p2_path, 'rows[id='+rid+']'))
    b129 = next((x for key,x in report_catalog.items() if key.endswith('/2026-10-06-일반통합-B129/report.json')), {})
    observed = [x for x in b129.get('raw_summary',{}).get('mapped_outcomes',[]) if x['id'] in {TEST_CORRECTIONS.get(t,t) for t in tests_for_row}]
    row = {'group':group, 'id':rid, 'original':original, 'classification':classification,
           'classification_reason': '원문 전건의 현재 의미 결론이 없으므로 아래 종료 질문만 배정한다.',
           'sources':sources, 'historical_claims':historical, 'reviewed_properties':props,
           'evidence_catalog': CAT_REF, 'evidence_keys':keys, 'current_test_bindings':test_bindings(tests_for_row),
           'observed_b129_outcomes':observed,
           'edition_limit':'source-comparison의 baseline 일치는 시작 이후 변경 부재만 뜻한다. 과거 raw report의 판본 비교는 evidence-catalog에 있으며 해당 일부 통과를 최종 전체 성공으로 합산하지 않는다.',
           'meaning_resolution':meaning_overrides.get(rid,'원문 의미를 유지한다. 역사 위치/수치는 현재 모집단 또는 성공 증명으로 자동 승격하지 않는다.'),
           'remaining':remaining, 'question':question,
           'next_action': ('재구현 없이 현재 성질을 G4 일반 전체·G5 fresh T3·G6 변이 결과에 연결하고, 새 반례나 계약 변경이 있을 때만 다시 연다.' if classification==FINAL else
                           'document-closeout 결과를 manager가 검수하여 실제 반환/공유 계약 교체의 한정 packet을 배정한다. 이름·정책·읽기 한도는 별도 종료 질문으로 유지한다.' if classification==REPAIR else
                           '지정한 source/test/기존 원보고로 질문을 답한다. 충분하면 최종 판본 대기로 옮기고, 빠진 입력/단언이 확인될 때만 그 한정 수리를 배정한다.'),
           'tracking_task_ids':[t['id'] for t in linked], 'product_completion_claim':False}
    row['unavailable_historical_raw_report_selectors']=[
        x['board_selector'] for key in keys if key in catalog
        for x in catalog[key]['historical_report_locations'] if not x['currently_exists']]
    if classification==FINAL:
        row['classification_reason']='현재 작업판의 implementation_reviewed 판단을 한정 재사용한다. 1-D/11-A는 현재 시험·생산 경로도 직접 대조했다. 11-B는 기존 B90~B109와 PR23 검토를 재사용하며 이번 task가 전부 재감사한 것은 아니다.'
    elif classification==REPAIR:
        row['classification_reason']='B115 J3/J4의 실제 삭제/재대입 거짓 통과와 구문 의존이 교체 근거다. 현재 반환값 자체의 제품 결함을 뜻하지 않는다. B130~B134 완료 범위를 빼고 배정한다.'
    elif classification==INSUFFICIENT:
        row['classification_reason']='정확한 실제 환경/모집단/원 반례 또는 원보고 연결이 부족하다. 파일 존재나 유사 시험의 통과로 대체하지 않는다.'
    rows.append(row)

write('requirement-state.json', {
    'kind':'phase 001 closure-map classification, not G1/G2 acceptance',
    'source_edition':ref(OUT/'source-comparison.json'),
    'classifications':[FINAL,REPAIR,QUESTION,INSUFFICIENT],
    'counts_by_population':dict(collections.Counter(r['group'] for r in rows)),
    'classification_counts_by_population':{g:dict(collections.Counter(r['classification'] for r in rows if r['group']==g)) for g in originals},
    'no_aggregate_completion_rate':True,
    'precedence':[POLICY,ref(RUN/'context.md'),ref(OLD/'설계.md'),BOARD_REF],
    'scope':'30의무·61보존·원래P2 12의 전건 연결. 미검토 의미는 질문/근거부족으로 남긴다. 109개 코드 재감사·제품시험 실행은 하지 않았다.',
    'rows':rows,
})

aux_goals = {
 'DESIGN-0':['G2'], 'DESIGN-1a':['G2','G3'], 'DESIGN-1b':['G2','G3'], 'DESIGN-1c':['G2','G3'],
 'DESIGN-1d':['G2','G3'], 'DESIGN-1f-migration':['G2','G3'], 'DESIGN-2-classes':['G1','G3'],
 'DESIGN-2-ledger':['G1','G2'], 'FINAL-instructions':['G3','G8'], '9-C':['G7'],
 'FINAL-T4':['G7'], 'FINAL-T5':['G7'], 'FINAL-corpus':['G7'], 'FINAL-ordinary':['G4'],
 'FINAL-T3':['G5'], 'FINAL-mutation':['G6'], 'FINAL-mirrors':['G8'], 'FINAL-main':['G8'],
}
row_by_id={r['id']:r for r in rows}
tracking=[]
for t in tasks:
    ids=t['requirement_ids']; targets=[]
    for rid in ids:
        targets.append({'id':rid, 'kind':'original_requirement' if rid in row_by_id else 'auxiliary_design_or_gate',
                        'goals': ['G2'] if rid.startswith('K-') or rid in originals['p2'] else ['G1'] if rid in row_by_id else aux_goals.get(rid,[])})
    state = QUESTION
    if t['id'] in ['DOC-RETURN-PURE','DOC-RETURN-CLI','DOC-OPTIONAL-FLAG','INTEGRATION-CURRENT','R17'] or t['id'].startswith('LINK-'):
        state=FINAL
    elif t['id'].startswith('DOC-RETURN-'):
        state=REPAIR
    elif t['id'].startswith(('FINAL-','MUTATION-')) or t['id'] in ['R19','R20']:
        state=INSUFFICIENT
    unresolved_inputs = [x for x in t.get('inputs',[]) if not resolve(PATH_CORRECTIONS.get(x['path'],x['path'])).is_file()]
    tracking.append({'id':t['id'], 'historical_status':t['status'], 'purpose':t['purpose'],
                     'classification':state, 'requirement_links':targets,
                     'population':t.get('population'), 'finite_question':t.get('unresolved_decision_question',t['exit_condition']),
                     'completed_scope':t.get('completed_scope',[]), 'remaining_scope':t.get('remaining_scope',[]),
                     'dependencies':t.get('dependencies',[]), 'evidence_keys':t.get('existing_evidence_keys',[]),
                     'evidence_pointer':t.get('evidence_pointer',t.get('review_pointer')),
                     'inputs':task_inputs(t), 'unresolved_historical_input_locators':unresolved_inputs,
                     'dispatch_caution':'큰 기존 제목을 그대로 재파견하지 않는다. 원문/생산자/소비자/입력축/정확 단언을 한정한다.',
                     'special_disposition': ('B129 실행/실패 판정 작업은 완료지만 3988 pass·1 fail·1 skip이다. FINAL-ORDINARY 성공과 중복 계수하지 않는다.' if t['id']=='INTEGRATION-CURRENT' else
                                             '최종 gate의 실제 실행 증거가 필요하며 선행 의미 판정/수리가 끝나기 전 실행할 수 있다는 뜻이 아니다.' if t['id'].startswith(('FINAL-','MUTATION-')) else
                                             '현재 기록의 완료 범위 재사용; 전체 원문 충족과 구별.')})
overlaps=[]
for rid in sorted({x for t in tasks for x in t['requirement_ids']}):
    owners=[t['id'] for t in tasks if rid in t['requirement_ids']]
    if len(owners)>1:
        relation = '같은 의무의 서로 다른 모집단 분할; 중복 완료율로 세지 않음'
        if rid=='13-C': relation='R27/R28의 이름·읽기 질문과 DOC-* 반환 교체 범위가 일부 겹침; 동일 생산자/문서의 읽기와 교정은 함께 배정'
        if rid=='FINAL-ordinary': relation='INTEGRATION-CURRENT는 과거 실패를 확정한 진단, FINAL-ORDINARY는 최종 성공 관문; 서로 다른 완료 조건'
        if rid=='FINAL-mutation': relation='계획·17파일 묶음·결합 검사가 같은 G6에 연결됨; 현재 함수 분모는 fresh T3 후 확정'
        overlaps.append({'requirement_id':rid,'task_ids':owners,'relation':relation})
write('tracking-state.json',{'board':binding(BOARD,'current_work.independent_execution.plan.tasks'),
      'tasks':tracking, 'overlap_groups':overlaps, 'auxiliary_requirement_goals':aux_goals,
      'orphan_definition':'원래103 ID 또는 명시한 설계/관문 G에 연결되지 않는 추적항목',
      'duplicate_task_ids':[k for k,v in collections.Counter(t['id'] for t in tasks).items() if v>1],
      'orphan_tasks':[t['id'] for t in tracking if any(not x['goals'] for x in t['requirement_links'])]})

review_joins = {
 'PR00':['HISTORY-LINK','INTEGRATION-CURRENT','FINAL-ORDINARY'],
 'PR01':['KEEP-RUNNER-DISCOVERY','KEEP-RUNNER-REPORT','FINAL-T3','MUTATION-PLAN'],
 'PR02':['R17','R18','KEEP-ISOLATION','FINAL-T4'],
 'PR03':['HISTORY-LINK','CLASSES-LINK'],
 'PR04':['KEEP-TEMPLATES','KEEP-PUBLIC-PATH','KEEP-MODEL-SUBMIT','R14','R15'],
 'PR05':[t['id'] for t in tasks if t['id'].startswith(('KEEP-','P2-GROUP-'))]+['HISTORY-LINK'],
 'PR06':['R01','R05','R06','R07','LINK-1-D','KEEP-STORAGE'],
 'PR07':['R08','R09','R10','KEEP-MODEL-SUBMIT'],
 'PR08':['R03','R45','KEEP-FAKE-EVIDENCE','P2-GROUP-04-1'],
 'PR09':['R34','R35','P2-GROUP-07-1'],
 'PR10':['R37','R38','R39','R40','R41','R42','R43'],
 'PR11':['R11','R15','R16','R29','R30'],
 'PR12':['R31','R42','R43','LINK-11-A','P2-GROUP-03-1','P2-GROUP-08-1'],
 'PR13':['R44','R45','R46','DOC-RETURN-REVIEW','P2-GROUP-05-1'],
 'PR14':['R32','R35','R45'],
 'PR15':['R10','R19','R20','FINAL-T4','FINAL-T5'],
 'PR16':['R12','R13','R25','R26'],
 'PR17':['R31','R32','R33','R21','KEEP-ROLE-INPUT'],
 'PR18':['R02','R03','R04','R34','R35','R36','P2-GROUP-06-1'],
 'PR19':['R47','R48','R49','LINK-11-B','P2-GROUP-02-1'],
 'PR20':['LINK-11-B','R16','R45'],
 'PR21':['LINK-11-B','R31','R32'],
 'PR22':['LINK-11-B','R41'],
 'PR23':['LINK-11-B','LINK-11-A','P2-GROUP-03-1'],
 'PR24':['R25','R26','R27','R28','DOC-RETURN-ROLE','DOC-RETURN-REVIEW','DOC-RETURN-TRUST'],
}
history=ie['prior_review']['history_to_unit']
review_rows=[]
for unit in ie['prior_review']['review_units']:
    uid=unit['id']; slices=[]
    for h in history:
        if h['review_unit']!=uid: continue
        paths=[]; unresolved=[]
        for value in h.get('source_files_from_record',[]):
            value=value.get('path') if isinstance(value,dict) else value
            if not isinstance(value,str): continue
            p=resolve(value)
            if p.is_file(): paths.append(binding(p))
            else: unresolved.append(value)
        slices.append({'history_id':h['id'],'board_selector':h['board_pointer'],'commit':h.get('commit'),
                       'current_files':paths,'unresolved_historical_file_locators':unresolved,
                       'original_report_selectors':[x['pointer'] for x in h.get('original_report_paths',[])],
                       'diff_to_read': ('git show '+h['commit']+' -- .claude/skills/do-math' if h.get('commit') else
                                        '해당 board_selector의 도입 commit을 git log -S로 찾고 실제 제품/시험 hunk를 확인'),
                       'required_comparison':'위 실제 hunk의 변경 함수 → 현재 직접 caller/수신자 → 원보고의 그 testID/판본을 함께 읽는다. 매핑만으로 유지 판정하지 않는다.'})
    disposition='아직 재검토하지 않은 영역. 원래 end_question을 같은 파일을 다루는 요구 작업의 입력에 합친다.'
    if uid=='PR23': disposition='기존 B107~B109의 accept_bounded_repair 판정을 재사용. 현재 핵심 경로를 제한적으로 다시 대조했고 확정 수리 없음. 11-B/G4~G7 전체 성공은 별도.'
    if uid=='PR06': disposition='B116의 B22 유지 판정과 B117의 빌더 등록/입력축 보강을 재사용. B03/B11/B44/B58 저장/JSON/증거 hunk의 의미 검토까지 완료한 것으로 확대하지 않는다.'
    seeds=[]
    for value in unit['source_seeds']:
        p=resolve(value)
        seeds.append(binding(p) if p.is_file() else {'search_directory_or_unresolved_locator':value, 'exists':p.exists(), 'is_directory':p.is_dir()})
    review_rows.append({'id':uid,'title':unit['title'],'historical_status':unit['status'],
                       'history_ids':unit['history_ids'],'actual_reviewed_history_ids':unit.get('reviewed_history_ids', unit['history_ids'] if uid=='PR23' else []),
                       'disposition':disposition,'finite_question':unit['end_question'],
                       'coassign_with_tracking_tasks':review_joins[uid], 'source_seeds':seeds,'review_slices':slices,
                       'foundation_or_migration_sources':{'board':BOARD_REF, 'selectors':[
                           'current_work.independent_execution.prior_review.foundation_to_unit',
                           'current_work.independent_execution.prior_review.non_b_history_to_unit',
                           'current_work.independent_execution.prior_review.migration_artifact_to_unit',
                           'current_work.independent_execution.prior_review.legacy_population_mapping',
                           'current_work.independent_execution.prior_review.preservation_mapping']},
                       'stop':'한 slice의 성질 유지/교정/제거/추가 판정과 근거가 있으면 종료. 다른 영역의 완료를 선행 장벽으로 삼지 않는다.'})

pr23=[]
diff_outputs=[]
for c in ie['prior_review']['completed_review']['commits']:
    comparison=[]
    for name in c['actual_changed_files']:
        p=REPO/name
        result=subprocess.run(['git','show',c['commit']+':'+name],cwd=REPO,capture_output=True,check=False)
        same=result.returncode==0 and p.is_file() and result.stdout.replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n')
        comparison.append({'file':binding(p),'commit':c['commit'],'git_show_exit':result.returncode,
                           'same_after_crlf_normalization':same})
        if not same:
            cmd=['git','diff','--no-ext-diff',c['commit'],'--',name]
            diff=subprocess.run(cmd,cwd=REPO,capture_output=True,check=False)
            diff_outputs.append('$ '+' '.join(cmd)+'\nexit='+str(diff.returncode)+'\n'+diff.stdout.decode('utf-8',errors='replace')+diff.stderr.decode('utf-8',errors='replace'))
    pr23.append({'id':c['id'],'commit':c['commit'],'verdict_reused':c['verdict'],
                 'preserved_properties':c['preserved_properties'],'code_evidence':c['code_evidence'],
                 'needed_fix':c['needed_fix'],'verification_needed_now':c['verification_needed_now'],
                 'current_edition_comparison':comparison,
                 'report_references':[ref(resolve(x['path'])) for x in c['original_evidence'] if resolve(x['path']).is_file()],
                 'limits':c.get('matrix_limit',c.get('regression_boundary',c.get('not_masking'))),
                 'interpretation':'기존 독립 판정의 재사용. 그 뒤 달라진 파일 전체를 검토 완료로 승격하지 않으며 diff 파일로 영향 범위를 한정한다.'})
(OUT/'pr23-current-diff.txt').write_text('\n\n'.join(diff_outputs) or 'All compared files equal after CRLF normalization.\n',encoding='utf-8')
doc=ie['document_review']
schema=cw['independent_schema_boundary_followup']['schema_review']
write('prior-review-state.json',{
 'board':binding(BOARD,'current_work.independent_execution.prior_review'),
 'mapping_is_not_review':True, 'review_units':review_rows,'reused_pr23':pr23,
 'pr23_current_diff':ref(OUT/'pr23-current-diff.txt'),
 'reused_b115_document_review':{'selector':'current_work.independent_execution.document_review',
      'review_status':doc['review_status'],'reviewed_head':doc['reviewed_head'],'summary':doc['summary'],
      'judgments':[{k:j[k] for k in ['id','feature','decision','actual_benefit','error_examples','preserve','recommended_scope','exit_condition'] if k in j} for j in doc['judgments']],
      'later_disposition':'선택 인자는 B115, PURE/CLI는 B119~B131, ROLE 일부는 B132~B134에서 수리. 남은 반환 결속을 다른 task가 검토하므로 여기서 같은 코드를 재감사하지 않는다.'},
 'reused_b116_b117_schema_review':{'selector':'current_work.independent_schema_boundary_followup.schema_review',
      'decision':schema['decision'],'what_is_already_proved':schema['what_is_already_proved'],
      'latest_disposition':'B116 유한 입력축과 B117 클래스4/상수6의 추가 검증을 재사용. R07의 remaining은 새 후보 발굴이 아니라 현행 선언과 원문 모집단 최종 대응이다.'},
 'remaining_non_b_review':'PR03/PR05의 foundation_to_unit·migration_artifact_to_unit 항목도 같은 구조/처분 파일 소비자에서 다룬다. B01~B109 매핑으로 기반 전체 리뷰를 대신하지 않는다.',
})

# Exact excerpts support only the bounded code readings stated in this report.
readback_specs=[
 ('tests/unit/test_storage_codec_properties.py',1,None),
 ('tests/support/storage_obligations.py',1,None),
 ('tests/support/storage_records.py',54,60),
 ('tests/support/cross_contracts.py',57,63),
 ('tests/flows/test_cross_role_calls.py',74,94),
 ('tests/flows/test_cross_role_calls.py',190,282),
 ('tests/flows/test_cross_role_calls.py',285,311),
 ('do_math/payloads.py',83,182),
 ('do_math/repository.py',370,381),
 ('do_math/planning.py',806,858),
 ('do_math/dispatch_engine.py',84,102),
 ('do_math/lifecycle_engine.py',636,727),
 ('do_math/core_engine.py',2608,2620),
]
excerpts=[]
for name,start,end in readback_specs:
    p=SCRIPTS/name; lines=p.read_text(encoding='utf-8-sig').splitlines(); end=end or len(lines)
    excerpts.append({**binding(p), 'line_start':start,'line_end':end,'text':'\n'.join(lines[start-1:end])})
write('code-readback.json',{
 'method':'원문 파일 읽기와 필요한 현재 함수/시험 본문 대조. AST는 위치 선택에만 사용했고 실행 반환을 추정하는 증거로 쓰지 않음.',
 'observations':[
  {'requirement':'1-D','finding':'실제 encode/decode·ResearchRepository.save_with_state와 새 contract load를 사용한다. payload_records는 큰 값 둘과 키순서를 생성하고 title_sequences는 재등장 열을 만든다. exact canonical bytes·validate·sha1/sha256 및 payload 내용까지 단언한다. 저장 경로를 대역으로 가리지 않는다.', 'limit':'새 실행 아님. 현재 대응 시험의 B129 passed는 부분 증거이며 G4~G6는 미완료.'},
  {'requirement':'11-A','finding':'초기 준비/검토/계획 각1, 정상 research 점유 중 추가0, 빈 준비 plan0 및 계획 재방문 경계가 실제 Sim step/worker와 model 기록 대조에 연결된다.', 'limit':'공급자 CLI 실호출 아님. 조건부 주기 재방문을 무조건 호출0으로 오독하지 않는다.'},
  {'requirement':'11-B / PR23','finding':'schedule_reconsideration은 waiting next_owner를 호출 근거로 쓰지 않는다. readiness는 재계산하고 errors+contract+records의 같은 원인만 억제한다. 새 source는 미시작 준비에만 결속하고 수락한 action.event_refs만 소비한다.', 'limit':'B90~B106 전건을 이번 task에서 다시 검토한 것은 아님. 기존 기록과 PR23 판정을 한정 재사용.'},
 ],'excerpts':excerpts})

final_state=read(OUT/'requirement-state.json')
for row in final_state['rows']:
    if row['id'] in ['1-D','11-A','11-B']:
        row['bounded_code_readback']=binding(OUT/'code-readback.json','observations[requirement='+row['id']+']')
        row['reviewed_properties'].append({
            'property':next(o['finding'] for o in read(OUT/'code-readback.json')['observations'] if o['requirement'].startswith(row['id'])),
            'review_level':'이번 task의 명시된 현재 본문 대조; 새 시험 실행 없음',
        })
write('requirement-state.json',final_state)

print(json.dumps({'requirements':len(rows),'tracking_tasks':len(tracking),'prior_review_units':len(review_rows),
      'classification_counts_by_population':{g:dict(collections.Counter(r['classification'] for r in rows if r['group']==g)) for g in originals},
      'task_orphans':[t['id'] for t in tracking if any(not x['goals'] for x in t['requirement_links'])]},ensure_ascii=False))
