"""실제 Git의 고정 원천 누락과 좌표 복원 계약. 모델·Lean은 호출하지 않는다."""
from copy import deepcopy
import hashlib
import errno
import shutil

from do_math import review_cycle as rc
from support.review_owner_inputs import ReviewOwnerCase
from support.gap_inputs import ExecutedLines, ReadObjectLaunchFault, observation


class GitReadLaunchRestorationTests(ReviewOwnerCase):
    def setUp(self):
        super().setUp()
        from dataclasses import replace
        from do_math.git_process import GitProcess
        from support.storage_records import record_store, engine_on
        # 실제 Git 경계: 새 저장소를 정상 상태로 초기화한 뒤 같은 엔진을 사용한다.
        invalid_executable = self.root / 'invalid-git.exe'
        invalid_executable.write_bytes(b'This test-owned file is not an executable.\n')
        self.launch = ReadObjectLaunchFault(invalid_executable)
        ports = replace(self.engine.ports, git_backend=GitProcess(environment=self.engine.environment, run=self.launch))
        store = record_store(self.root / 'actual-git', backend=ports.git_backend, clock=ports.clock)
        self.engine, _ = engine_on(store, self.engine.instance, self.engine.runtime,
            workspace=self.root / 'actual-workspace', ports=ports)
        self.scene.engine = self.engine
        raw = b'preserved fixed evidence'
        path = 'runtime/artifacts/review-fixed/source.txt'
        self.engine._save({path: raw})
        cid, action = self.opened()
        supplied = {'id': 'S-fixed', 'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        self.engine._prepare_review_context(action, self.root / 'prepared-source', sources=[supplied])
        self.row = self.engine._research_source_spec(self.engine.runtime['review_cycles'][cid], action, 'S-fixed')
        self.action = action
        self.assertEqual(self.engine.store.read(self.row['artifact_ref'], self.row['snapshot']), raw)
        visible = self.engine._materialize_research_sources([self.row], self.root / 'normal-source', slot=action['slot'])
        self.assertEqual((self.root / 'normal-source' / visible[0]['local_path']).read_bytes(), raw)
        self.raw = raw
        self.engine._save()
        # A new physical repository identity, as a fresh reader of a preserved
        # repository: never clear/patch Repository's process-wide artifact cache.
        from do_math.engine import ResearchEngine
        from support.storage_records import INSTANCE_ID
        cold = self.root / 'cold-reader'
        shutil.copytree(self.engine.store.repository, cold)
        self.engine = ResearchEngine(cold, INSTANCE_ID, ports=ports,
            codex_home=self.engine.codex_home, environment=self.engine.environment,
            host_id=self.engine.host_id)
        self.assertEqual(self.engine.runtime['review_cycles'][cid],
                         self.scene.engine.runtime['review_cycles'][cid])
        self.assertEqual(self.engine.runtime['review_inputs'], self.scene.engine.runtime['review_inputs'])

    def test_git_read_launch_oserror_preserves_source_and_recovers_after_fault(self):
        """Real CreateProcess rejects our own invalid executable at the Git read effect."""
        row, action = self.row, self.action
        before = deepcopy((row, self.engine.instance, self.engine.runtime))
        head = self.engine.head
        raw = self.raw
        workspace = self.root / 'launch-fault'
        self.launch.spec = row['snapshot'] + ':' + row['artifact_ref']
        try:
            with ExecutedLines(self.engine._materialize_research_sources) as reached:
                with self.assertRaisesRegex(rc.ReviewRestorationError, '.') as caught:
                    self.engine._materialize_research_sources([row], workspace, slot=action['slot'])
        finally:
            self.launch.spec = None
        self.assertEqual(len(self.launch.errors), 1)
        cause = self.launch.errors[0]
        self.assertIs(caught.exception.__cause__, cause)
        self.assertEqual(str(caught.exception), str(cause))
        self.assertEqual(caught.exception.diagnostics, {
            'cause_kind': 'fixed_source_io_unavailable',
            'coordinate': {'slot': action['slot'], 'source_index': 0, 'source_ref': row['ref'],
                'artifact_ref': row['artifact_ref'], 'snapshot': row['snapshot'],
                'errno': cause.errno, 'path': cause.filename},
            'expected_sha256': row['sha256'], 'observed_sha256': None,
            'preserved_range': {'slot': action['slot'], 'verified_indices': []},
            'retryable': cause.errno in {errno.EAGAIN, errno.EINTR, errno.EBUSY, errno.ETIMEDOUT},
            'continuity_broken': False})
        self.assertFalse(caught.exception.diagnostics['retryable'])
        import ast
        import inspect
        import textwrap
        source_lines, first_line = inspect.getsourcelines(self.engine._materialize_research_sources)
        tree = ast.parse(textwrap.dedent(''.join(source_lines)))
        handler = next(node for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler)
            and any(isinstance(value, ast.Constant) and value.value == 'fixed_source_io_unavailable'
                    for value in ast.walk(node)))
        expected_lines = {first_line + node.lineno - 1 for node in [handler, *handler.body]}
        self.assertEqual(len(expected_lines), 3)
        self.assertTrue(expected_lines.issubset(reached.lines), reached.lines)
        self.assertEqual(list((workspace / 'input' / 'review-research').iterdir()), [])
        self.assertEqual((row, self.engine.instance, self.engine.runtime), before)
        self.assertEqual(self.engine.head, head)
        self.assertEqual(self.engine.store.read(row['artifact_ref'], row['snapshot']), raw)
        restored = self.engine._materialize_research_sources([row], workspace, slot=action['slot'])
        self.assertEqual((workspace / restored[0]['local_path']).read_bytes(), raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
        self.assertEqual(len(raw), row['bytes'])
        self.assertEqual((row, self.engine.instance, self.engine.runtime), before)
        self.assertEqual(self.engine.head, head)
        observation('R6-OS', errno=cause.errno, winerror=getattr(cause, 'winerror', None),
                    error=str(cause), diagnostics=caught.exception.diagnostics, lines=reached.lines,
                    read_spec=self.launch.calls[-1].decode().strip(), recovered=True)
