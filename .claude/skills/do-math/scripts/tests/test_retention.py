"""Retention and cleanup of execution runs: what may be deleted, archived or kept, checked against the pinned Git archive."""
from __future__ import annotations

import json
import hashlib
import os
from copy import deepcopy
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from do_math.system_clock import new_id
from do_math.repository import ResearchRepository
from do_math.retention import cleanup, cleanup_candidates
from research_fixtures import current_state, git_init


def archived_run(root):
    run = root / 'runs/EX-1'
    run.mkdir(parents=True)
    (run / 'output.txt').write_bytes(b'preserved result')
    receipt = json.dumps({'execution_id': 'EX-1', 'local_terminated': True}).encode()
    snapshot = 'a' * 40
    archive = {'runtime/artifacts/EX-1/output.txt': b'preserved result',
               'runtime/artifacts/EX-1/termination.json': receipt}
    execution = {'id': 'EX-1', 'status': 'ended', 'termination': {
        'local_terminated': True, 'evidence_ref': 'runtime/artifacts/EX-1/termination.json',
        'snapshot': snapshot, 'sha256': hashlib.sha256(receipt).hexdigest(), 'bytes': len(receipt)},
        'collection': {'retention_manifest': [{'path': 'output.txt', 'artifact_ref': 'runtime/artifacts/EX-1/output.txt',
            'snapshot': snapshot, 'sha256': hashlib.sha256(b'preserved result').hexdigest(), 'bytes': 16}]}}
    state = {'executions': {'EX-1': execution}, 'protected_references': set(),
             'approved_execution_ids': {'EX-1'}, 'runtime': {}}
    def read(path, commit):
        if commit != snapshot:
            raise ValueError('not an archived snapshot')
        return archive[path]
    return run, state, archive, read


class RetentionTests(unittest.TestCase):
    def test_cleanup_uses_current_recovery_completion_and_obligations(self):
        from do_math.record_schemas import RECORDS
        from jsonschema import Draft202012Validator
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, state, _, reader = archived_run(root)
            recovery = {'id': 'RY-1', 'started_at': '2026-09-25T00:00:00Z',
                        'execution_ids': ['EX-1'], 'dispositions': []}
            state['runtime']['recoveries'] = {'RY-1': recovery}
            Draft202012Validator(RECORDS['recoveries']).validate(recovery)
            pending = cleanup_candidates(root, **state, read_artifact=reader)[0]
            self.assertIn('recovery_pending', pending['reasons'])
            recovery['finished_at'] = '2026-09-25T00:01:00Z'
            Draft202012Validator(RECORDS['recoveries']).validate(recovery)
            self.assertTrue(cleanup_candidates(root, **state, read_artifact=reader)[0]['eligible'])
            state['runtime']['waiting_actions'] = {'AC-1': {'execution_id': 'EX-1'}}
            waiting = cleanup_candidates(root, **state, read_artifact=reader)[0]
            self.assertIn('recovery_pending', waiting['reasons'])
            state['runtime']['waiting_actions'] = {}
            state['runtime']['reservations'] = {'RS-1': {'owner_id': 'EX-1', 'state': 'held'}}
            reserved = cleanup_candidates(root, **state, read_artifact=reader)[0]
            self.assertIn('unsettled_reservation', reserved['reasons'])
            self.assertFalse(reserved['eligible'])

    def test_retention_preserves_unpinned_receipt_and_unreadable_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run, state, archive, read = archived_run(root)
            state['executions']['EX-1']['termination']['snapshot'] = 'HEAD'
            permissive_reader = lambda path, snapshot: archive[path]
            result = cleanup_candidates(root, read_artifact=permissive_reader, **state)
            self.assertFalse(result[0]['eligible'])
            state['executions']['EX-1']['termination']['snapshot'] = 'a' * 40
            def inaccessible(*args, **kwargs):
                if kwargs.get('onerror'):
                    kwargs['onerror'](PermissionError('cannot list execution directory'))
                return iter(())
            state['executions']['EX-1']['collection']['retention_manifest'] = []
            with patch('do_math.retention.os.walk', side_effect=inaccessible):
                result = cleanup_candidates(root, read_artifact=read, **state)
            self.assertFalse(result[0]['eligible'])
            self.assertTrue(run.exists())

    def test_cleanup_archive_failure_is_local_degradation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run, state, archive, read = archived_run(root)
            candidates = cleanup_candidates(root, read_artifact=read, **state)
            original = deepcopy(state)
            def failed_reader(path, snapshot):
                raise RuntimeError('archive store unavailable')
            result = cleanup(root, candidates, current_state=lambda: state, read_artifact=failed_reader)
            self.assertEqual(result['status'], 'degraded')
            self.assertEqual(state, original)
            self.assertTrue(run.exists())

    def test_descendant_reference_blocks_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            result = cleanup_candidates(Path(d), {'EX-1': {'id': 'EX-1', 'status': 'ended', 'artifact_bundle': 'bundle'}}, protected_references={'runs/EX-1/needed.txt'})
            self.assertFalse(result[0]['eligible'])
            self.assertIn('protected_reference', result[0]['reasons'])

    def test_bundle_name_alone_never_proves_preservation(self):
        with tempfile.TemporaryDirectory() as d:
            result = cleanup_candidates(Path(d), {'EX-1': {'id': 'EX-1', 'status': 'ended', 'artifact_bundle': 'bundle'}}, protected_references=set())
            self.assertFalse(result[0]['eligible'])

    def test_cleanup_hashes_local_files_and_archive_rows_once(self):
        import uuid
        from unittest.mock import Mock, patch
        from do_math import file_io, retention
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run, state, archive, read = archived_run(root)
            reader, git_dir, marks = Mock(side_effect=read), 'git-' + uuid.uuid4().hex, {}
            # A fresh file's birth time cannot be aged; treat any past fingerprint as settled.
            with patch.object(file_io, 'RACY_NS', 0), \
                    patch.object(retention, 'read_stable', wraps=retention.read_stable) as local:
                candidates = cleanup_candidates(root, **state, read_artifact=reader, git_dir=git_dir, marks=marks)
                self.assertTrue(candidates[0]['eligible'], candidates)
                self.assertEqual((local.call_count, reader.call_count), (1, 2))
                result = cleanup(root, candidates, current_state=lambda: state, read_artifact=reader,
                                 git_dir=git_dir, marks=marks)
            self.assertEqual(result['deleted'], ['runs/EX-1'])
            # The pre-deletion recheck used fingerprints and matched archive rows.
            self.assertEqual(local.call_count, 1)
            self.assertEqual(reader.call_count, 3)  # only the termination receipt is parsed again

    def test_retention_requires_ended_closed_preserved_unrecovered_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run, state, archive, reader = archived_run(root)
            candidates = cleanup_candidates(root, **state, read_artifact=reader)
            self.assertEqual(candidates[0]["eligible"], True)
            result = cleanup(root, candidates, current_state=lambda: state, read_artifact=reader)
            self.assertEqual(result["deleted"], ["runs/EX-1"])
            self.assertFalse(run.exists())
            run.mkdir(parents=True)
            recovery = {"id": "RY-1", "started_at": "2026-09-25T00:00:00Z", "execution_ids": ["EX-1"], "dispositions": []}
            blocked = cleanup_candidates(root, {"EX-1": {"id": "EX-1", "status": "ended", "artifact_bundle": "runtime/artifacts/EX-1"}}, protected_references=set(), runtime={"recoveries": {"RY-1": recovery}})
            self.assertFalse(blocked[0]["eligible"])
            self.assertIn("recovery_pending", blocked[0]["reasons"])

    def test_cleanup_rechecks_reference_files_and_archive_before_deletion(self):
        for mutation in ('reference', 'local', 'archive', 'termination', 'reservation', 'recovery'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as d:
                root = Path(d); run, state, archive, reader = archived_run(root)
                candidates = cleanup_candidates(root, **state, read_artifact=reader)
                self.assertTrue(candidates[0]['eligible'])
                if mutation == 'reference': state['protected_references'].add('runs/EX-1/output.txt')
                elif mutation == 'local': (run / 'new.txt').write_bytes(b'not archived')
                elif mutation == 'archive': archive['runtime/artifacts/EX-1/output.txt'] = b'corrupt'
                elif mutation == 'termination': archive['runtime/artifacts/EX-1/termination.json'] = b'{}'
                elif mutation == 'reservation': state['runtime']['reservations'] = {'RS': {'owner_id': 'EX-1', 'state': 'held'}}
                else: state['runtime']['recoveries'] = {'RY-1': {'id': 'RY-1',
                    'started_at': '2026-09-25T00:00:00Z', 'execution_ids': ['EX-1'], 'dispositions': []}}
                original = deepcopy(state)
                result = cleanup(root, candidates, current_state=lambda: state, read_artifact=reader)
                self.assertEqual(result['status'], 'degraded')
                self.assertTrue(run.exists())
                self.assertEqual(state, original)

    def test_retention_resolves_real_git_archive_bytes_at_pinned_commit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git_init(root)
            identifier = new_id('RI'); repository = ResearchRepository(root, identifier)
            instance, runtime = current_state({'id': identifier}, {'executions': {}, 'activities': {}})
            head = repository.initialize(instance, runtime)
            run, state, archive, _ = archived_run(root / 'work')
            archived = repository.save_with_state(head, instance, runtime, artifacts=archive)[0]
            execution = state['executions']['EX-1']
            execution['termination']['snapshot'] = archived
            for row in execution['collection']['retention_manifest']: row['snapshot'] = archived
            reader = lambda path, snapshot: repository.read(path, snapshot)
            candidate = cleanup_candidates(root / 'work', **state, read_artifact=reader)
            self.assertTrue(candidate[0]['eligible'], candidate)
            result = cleanup(root / 'work', candidate, current_state=lambda: state, read_artifact=reader)
            self.assertEqual(result['deleted'], ['runs/EX-1'])
            self.assertEqual(repository.read('runtime/artifacts/EX-1/output.txt', archived), b'preserved result')

    def test_reparse_root_is_rejected_before_resolution(self):
        from do_math import retention
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); run, state, archive, reader = archived_run(root)
            real_stat = Path.lstat
            def lstat(path):
                if path == root / 'runs':
                    class Reparse:
                        st_mode = 0
                        st_file_attributes = 0x400
                    return Reparse()
                return real_stat(path)
            with patch.object(Path, 'lstat', lstat):
                candidates = retention.cleanup_candidates(root, **state, read_artifact=reader)
            self.assertFalse(candidates[0]['eligible'])
            self.assertTrue(any('reparse' in r for r in candidates[0]['reasons']))

    def test_run_path_refuses_an_execution_id_that_windows_stores_as_another_run(self):
        # Windows drops a trailing dot, so the folder of "EX-1." would be that of "EX-1".
        from do_math.retention import _run_path
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                _run_path(Path(d), 'EX-1.')

    @unittest.skipUnless(os.name == 'nt', 'Windows junction probe')
    def test_real_windows_runs_junction_is_not_a_new_trusted_root(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            root = Path(d); target = Path(outside)
            (target / 'EX-1').mkdir(); (target / 'EX-1/important').write_bytes(b'keep')
            junction = root / 'runs'
            script = "New-Item -ItemType Junction -Path '" + str(junction).replace("'", "''") + "' -Target '" + str(target).replace("'", "''") + "' | Out-Null"
            made = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True)
            self.assertEqual(made.returncode, 0, made.stderr)
            try:
                result = cleanup_candidates(root, {'EX-1': {'id': 'EX-1', 'status': 'ended'}}, protected_references=set())
                self.assertFalse(result[0]['eligible'])
                self.assertTrue(any('reparse' in reason for reason in result[0]['reasons']))
                self.assertEqual((target / 'EX-1/important').read_bytes(), b'keep')
            finally:
                os.rmdir(junction)  # Only the exact temporary junction, not its target.
            run, state, archive, reader = archived_run(root)
            alias = root / 'protected-alias'
            script = "New-Item -ItemType Junction -Path '" + str(alias).replace("'", "''") + "' -Target '" + str(run).replace("'", "''") + "' | Out-Null"
            self.assertEqual(subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True).returncode, 0)
            try:
                state['protected_references'] = {str(alias / 'output.txt')}
                result = cleanup_candidates(root, **state, read_artifact=reader)
                self.assertFalse(result[0]['eligible'])
                self.assertTrue(run.exists())
            finally:
                os.rmdir(alias)

    def test_reference_closure_follows_records_and_preserves_unknown_origins(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); run, state, archive, reader = archived_run(root)
            state['protected_references'] = {'KN'}
            # retention_inputs lists the references each persisted record holds.
            from do_math.retention import retention_inputs
            rows = [{'id': 'KN', 'root': 'research', 'family': 'knowledge',
                     'record': {'id': 'KN', 'dependencies': ['CP']}},
                    {'id': 'CP', 'root': 'research', 'family': 'formal_results',
                     'record': {'id': 'CP', 'path': 'runs/EX-1/output.txt', 'references': ['KN']}}]
            records, _ = retention_inputs({}, {}, rows)
            result = cleanup_candidates(root, **state, read_artifact=reader, reference_records=records)
            self.assertIn('protected_reference', result[0]['reasons'])
            result = cleanup_candidates(root, **state, read_artifact=reader)
            self.assertIn('unresolved_reference: KN', result[0]['reasons'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
