"""Actual Git restoration of fixed review sources preserves fault coordinates."""
from copy import deepcopy
from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math import review_cycle as rc
from do_math.execution_lifecycle import transition_execution
from do_math.git_process import GitProcess
from do_math.git_store import GitStateStoreError
from support.review_scene import ReviewScene
from support.storage_records import record_store, engine_on


class FixedSourceRestorationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.scene = ReviewScene(self.root)
        self.engine = self.scene.engine
        author = self.engine._register_execution(
            {'id': 'AC-review-author', 'role': 'research_work'},
            {'id': 'author', 'role': 'research_work', 'status': 'running'})
        self.assertIsNotNone(author)
        transition_execution(author, 'stopping', at=self.engine.ports.clock.now())
        transition_execution(author, 'ended', at=self.engine.ports.clock.now(), outcome='execution_incomplete')
        ports = replace(self.engine.ports, git_backend=GitProcess(environment=self.engine.environment))
        store = record_store(self.root / 'actual-git', backend=ports.git_backend, clock=ports.clock)
        self.engine, _ = engine_on(store, self.engine.instance, self.engine.runtime,
            workspace=self.root / 'actual-workspace', ports=ports)
        self.scene.engine = self.engine
        raw = b'preserved fixed evidence'
        path = 'runtime/artifacts/review-fixed/source.txt'
        self.engine._save({path: raw})
        cid = self.scene.start('K1')
        action = deepcopy(self.scene.pending())
        supplied = {'id': 'S-fixed', 'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        self.engine._prepare_review_context(action, self.root / 'prepared-source', sources=[supplied])
        self.row = self.engine._research_source_spec(self.engine.runtime['review_cycles'][cid], action, 'S-fixed')
        self.action = action
        self.assertEqual(self.engine.store.read(self.row['artifact_ref'], self.row['snapshot']), raw)
        visible = self.engine._materialize_research_sources([self.row], self.root / 'normal-source', slot=action['slot'])
        self.assertEqual((self.root / 'normal-source' / visible[0]['local_path']).read_bytes(), raw)
        from support.engine_context import assert_review_documents
        assert_review_documents(self, visible, owner='review_sources', sources=[self.row],
                                engine=self.engine, workspace=self.root / 'normal-source')

    def test_missing_fixed_artifact_returns_a_coordinate_restoration_fault(self):
        row, action = deepcopy(self.row), self.action
        row['artifact_ref'] = 'runtime/artifacts/review-missing/source.txt'
        before = deepcopy((self.engine.instance, self.engine.runtime))
        head = self.engine.head
        with self.assertRaises(rc.ReviewRestorationError) as caught:
            self.engine._materialize_research_sources([row], self.root / 'missing-source', slot=action['slot'])
        self.assertIs(type(caught.exception.__cause__), GitStateStoreError)
        self.assertEqual(str(caught.exception), str(caught.exception.__cause__))
        self.assertEqual(caught.exception.diagnostics, {
            'cause_kind': 'fixed_source_io_unavailable',
            'coordinate': {'slot': action['slot'], 'source_index': 0, 'source_ref': row['ref'],
                           'artifact_ref': row['artifact_ref'], 'snapshot': row['snapshot'],
                           'errno': None, 'path': None},
            'expected_sha256': row['sha256'], 'observed_sha256': None,
            'preserved_range': {'slot': action['slot'], 'verified_indices': []},
            'retryable': False, 'continuity_broken': False})
        self.assertEqual(list((self.root / 'missing-source' / 'input' / 'review-research').iterdir()), [])
        self.assertEqual((self.engine.instance, self.engine.runtime), before)
        self.assertEqual(self.engine.head, head)

    def test_damaged_materialization_preserves_the_fixed_source_coordinate(self):
        workspace = self.root / 'normal-source'
        path = workspace / 'input' / 'review-research' / ('0000-' + self.row['sha256'] + '.txt')
        path.write_bytes(b'changed local source')
        before = deepcopy((self.engine.instance, self.engine.runtime))
        with self.assertRaises(rc.ReviewRestorationError) as caught:
            self.engine._materialize_research_sources([self.row], workspace, slot=self.action['slot'])
        diagnostic = caught.exception.diagnostics
        self.assertEqual(diagnostic['cause_kind'], 'materialized_content_mismatch')
        self.assertEqual(diagnostic['coordinate']['slot'], self.action['slot'])
        self.assertEqual(diagnostic['coordinate']['source_ref'], self.row['ref'])
        self.assertEqual(diagnostic['coordinate']['snapshot'], self.row['snapshot'])
        self.assertEqual(diagnostic['coordinate']['path'], str(path.resolve()))
        self.assertEqual(diagnostic['expected_sha256'], self.row['sha256'])
        self.assertEqual(diagnostic['observed_sha256'], hashlib.sha256(b'changed local source').hexdigest())
        self.assertEqual((self.engine.instance, self.engine.runtime), before)
