"""13-A 산문 단계와 현재 CLI 분기의 대응표 및 실제 CLI 호출 도우미.

상태가 pending인 행은 구현 완료로 세지 않는다. 공개 요청 JSON은 사용자가
내는 입력이며 저장 JSON·승인 해시를 손으로 쓰는 이음매가 아니다.
"""
from contextlib import redirect_stdout
from io import StringIO
import json
from datetime import datetime, timezone
from pathlib import Path

from do_math import cli
from do_math.engine import ResearchEngine
from support.fakes.clock import FakeClock
from support.sim import Sim, CONFIG, WALL_YEAR


# (단계, 문서 좌표, CLI/공개 도구, 전제, 기대 상태/정지점, 구현 상태)
JOURNEY_STEPS = (
    ('create', 'README.md#start-guide', 'init', '원 요청과 목표 파일', 'initializing; 정확 원문', 'implemented'),
    ('status', '초기화-운전.md §1', 'status', '생성된 ID', '현재 설정 해시', 'implemented'),
    ('research_files', '초기화-운전.md §1', 'query', '현재 ID', '연구 경로 전건', 'implemented'),
    ('runtime_files', '초기화-운전.md §1', 'query', '현재 ID', '실행 경로 전건', 'implemented'),
    ('read_original', '초기화-운전.md §1', 'read', 'query의 snapshot/path', 'UTF-8 원문과 해시', 'implemented'),
    ('configure', '초기화-운전.md §1', 'configure', '위임된 관찰 초 선택', 'operator 출처', 'implemented'),
    ('governance', '초기화-운전.md §2', 'decision', '공개 헌장 요청', 'applied; 원 승인 전문', 'implemented'),
    ('initial_grant', '초기화-운전.md §3', 'decision', '사용자 초기 권한', '연구 실행 없음', 'implemented'),
    ('research_grant', '초기화-운전.md §3', 'decision', '별도 연구 권한', '별도 ID 보존', 'implemented'),
    ('grant_query', '초기화-운전.md §3', 'query', '두 권한 적용', '두 grant', 'implemented'),
    ('probe', '초기화-운전.md §4', 'decision', 'status 설정 해시', 'applied', 'implemented'),
    ('capability_query', '초기화-운전.md §4', 'query', 'probe 적용', '현재 AI 프로필 전건', 'implemented'),
    ('adopt', '초기화-운전.md §4', 'decision', '같은 설정 해시와 grant ID', 'applied', 'implemented'),
    ('select', '초기화-운전.md §4', 'select-profile', 'adopt 적용', 'high; 모델 실행 없음', 'implemented'),
    ('prepare_trust', '초기화-운전.md §5', 'setup_lean.main', '실제 worker/spawn', 'recorded; trust 파일', 'implemented'),
    ('register_trust', '초기화-운전.md §5', 'trust', '공개 도구 생성 파일', 'recorded', 'implemented'),
    ('transition', '초기화-운전.md §5', 'trust', 'query로 얻은 환경 ID', 'checking', 'implemented'),
    ('activate', '초기화-운전.md §5', 'run --until-active', '관문 전건', 'active 직후 연구 배정 0', 'implemented'),
    ('import_approval', '초기화-운전.md §6', 'prepare-import-approval', 'snapshot/import ID', 'draft_only→decision', 'conditional_implemented'),
    ('answer', '초기화-운전.md §6', 'input', '공개 질문 ID', '해석/검사/승인 뒤 해소', 'conditional_implemented'),
    ('retry', '초기화-운전.md §6', 'request', '실패 활동과 승인', '정확히 한 후속과 실패 이력 보존', 'conditional_implemented'),
    ('first_research', '초기화-운전.md §6', 'run', 'K 있음/없음', 'plan/preparation 배정 전 정지', 'conditional_implemented'),
    ('handoff', 'README.md#handoff-judgment', 'operator', '활성화와 예약', '공개 start→실제 예약 진입/연구 CLI/worker→수락 게시→사용자 정지; OS 예약 발화는 T5 미검사', 'partial'),
    ('pause', 'README.md#existing-control', 'pause', '사용자 정지', 'paused', 'implemented'),
    ('resume', 'README.md#existing-control', 'resume', '정지 해제', 'applied', 'implemented'),
    ('close', 'README.md#existing-control', 'close', '사용자 종결', 'closed', 'implemented'),
)


class CliSim(Sim):
    """상태 생성은 공개 CLI init, 외부 포트·worker 배선은 공통 Sim을 그대로 쓴다."""
    def __init__(self, root, *, goal, original):
        self.root = self.shared = Path(root).resolve()
        self.root.mkdir(parents=True)
        self._wire(FakeClock(wall=datetime(WALL_YEAR, 1, 1, tzinfo=timezone.utc)), None)
        self.repository = self.root / 'repository'
        goal_path, request_path, config_path = (self.root / name for name in
                                              ('goal.txt', 'request.txt', 'config.json'))
        goal_path.write_bytes(goal.encode('utf-8'))
        request_path.write_bytes(original.encode('utf-8'))
        config_path.write_text(json.dumps({**CONFIG, 'lean_command': [str(self.trust_lean)]}), encoding='utf-8')
        output = StringIO()
        with redirect_stdout(output):
            code = cli.main(['init', '--create-repository', '--repository', str(self.repository),
                '--workspace', str(self.root / 'work'), '--goal-file', str(goal_path),
                '--request-text-file', str(request_path), '--config-file', str(config_path)],
                ports=self.ports, environment=self.environment, host_id=self.host_id, codex_home=self.codex_home)
        if code != 0:
            raise AssertionError('공개 init 실패: ' + output.getvalue())
        self.created = json.loads(output.getvalue())['result']
        self.instance_id = self.created['instance_id']
        self.engine = ResearchEngine(self.repository, self.instance_id, ports=self.ports,
            environment=self.environment, host_id=self.host_id, codex_home=self.codex_home)


class Journey:
    """Sim 포트만 주입하며 매 호출의 실제 Repository 상태는 새로 읽는다."""
    def __init__(self, sim, directory):
        self.sim, self.directory = sim, directory
        self.calls = []
        self.steps = []

    def call(self, command, *arguments, step=None):
        output = StringIO()
        with redirect_stdout(output):
            code = cli.main([command, '--repository', str(self.sim.repository), '--instance', self.sim.instance_id,
                             *map(str, arguments)], ports=self.sim.ports, environment=self.sim.environment,
                            host_id=self.sim.host_id, codex_home=self.sim.codex_home)
        wire = output.getvalue()
        response = json.loads(wire)
        self.calls.append((command, tuple(arguments), code, response))
        if code != 0 or 'result' not in response:
            raise AssertionError('공개 CLI 단계 실패: ' + wire)
        if step is not None:
            self.steps.append(step)
        return response['result']

    def document(self, name, value):
        path = self.directory / (name + '.json')
        raw = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
        path.write_bytes(raw.encode('utf-8'))
        return path, raw

    def decision(self, name, change, *, step=None):
        path, raw = self.document(name, change)
        result = self.call('decision', '--file', path, step=step)
        if result['effect'] != 'applied':
            raise AssertionError('공개 승인 적용 실패: ' + repr(result))
        return result, raw

    def state(self):
        return self.sim.engine.store.load()

    def files(self, prefix):
        result = self.call('query', '--files', '--prefix', prefix, '--limit', '1',
                           step='research_files' if prefix == 'research/' else 'runtime_files')
        snapshot, total = result['snapshot'], result['total']
        rows, cursors = [], set()
        # 조회 모집단 자체가 유한 상한이다. 같은 커서 반복과 과잉 페이지를 거부한다.
        for _ in range(total + 1):
            rows.extend(result['items'])
            cursor = result['next_cursor']
            if cursor is None:
                break
            if cursor in cursors:
                raise AssertionError('공개 조회 커서가 반복됨')
            cursors.add(cursor)
            result = self.call('query', '--files', '--prefix', prefix, '--limit', '1',
                               '--snapshot', snapshot, '--cursor', cursor)
        if len(rows) != total or result['next_cursor'] is not None:
            raise AssertionError('공개 경로 조회의 전체 모집단이 보존되지 않음')
        return snapshot, rows
