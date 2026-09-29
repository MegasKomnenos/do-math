"""Retention and cleanup of execution runs (``retention``, layer 2): what may be deleted, checked against the pinned archive.

The runs are real folders. The archive is a reader over pinned bytes, or the
real ``ResearchRepository`` on the in-process Git fake. What the legacy tests
imitated by replacing ``os.walk`` or ``Path.lstat`` is made real here with
``support.storage_files``: a subdirectory held open with no sharing cannot be
listed, and ``runs`` is an actual junction.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import Mock

from do_math.retention import _run_path, cleanup, cleanup_candidates, retention_inputs
from research_fixtures import current_state
from support.storage_files import age, audit_events, junction, remove_link, unlistable
from support.storage_records import record_store

REPARSE = 'physical path crosses a reparse point or symlink: '


def archived_run(root):
    """``(run, state, archive, read)``: an ended run ``EX-1`` whose one file and termination receipt are archived at ``'a'*40``.

    The state is eligible for cleanup as it is; ``read`` refuses any other snapshot.
    """
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


class CleanupEligibilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_cleanup_uses_current_recovery_completion_and_obligations(self):
        from do_math.record_schemas import RECORDS
        from jsonschema import Draft202012Validator
        _, state, _, reader = archived_run(self.root)
        recovery = {'id': 'RY-1', 'started_at': '2026-09-25T00:00:00Z',
                    'execution_ids': ['EX-1'], 'dispositions': []}
        state['runtime']['recoveries'] = {'RY-1': recovery}
        Draft202012Validator(RECORDS['recoveries']).validate(recovery)
        pending = cleanup_candidates(self.root, **state, read_artifact=reader)[0]
        self.assertIn('recovery_pending', pending['reasons'])
        recovery['finished_at'] = '2026-09-25T00:01:00Z'
        Draft202012Validator(RECORDS['recoveries']).validate(recovery)
        self.assertTrue(cleanup_candidates(self.root, **state, read_artifact=reader)[0]['eligible'])
        state['runtime']['waiting_actions'] = {'AC-1': {'execution_id': 'EX-1'}}
        waiting = cleanup_candidates(self.root, **state, read_artifact=reader)[0]
        self.assertIn('recovery_pending', waiting['reasons'])
        state['runtime']['waiting_actions'] = {}
        state['runtime']['reservations'] = {'RS-1': {'owner_id': 'EX-1', 'state': 'held'}}
        reserved = cleanup_candidates(self.root, **state, read_artifact=reader)[0]
        self.assertIn('unsettled_reservation', reserved['reasons'])
        self.assertFalse(reserved['eligible'])
        # The activity obligation of the name: an unfinished activity that holds the run.
        state['runtime']['reservations'] = {}
        state['runtime']['activities'] = {'AT-1': {'assigned_execution_ids': ['EX-1'], 'status': 'open'}}
        obliged = cleanup_candidates(self.root, **state, read_artifact=reader)[0]
        self.assertEqual(obliged['reasons'], ['activity_obligation_pending'])

    def test_retention_preserves_unpinned_receipt_and_unreadable_inventory(self):
        run, state, archive, read = archived_run(self.root)
        state['executions']['EX-1']['termination']['snapshot'] = 'HEAD'
        permissive_reader = lambda path, snapshot: archive[path]
        result = cleanup_candidates(self.root, read_artifact=permissive_reader, **state)
        self.assertFalse(result[0]['eligible'])
        self.assertEqual(result[0]['reasons'],
                         ['termination_unverified: OID must be a lowercase 40/64-character hexadecimal string'])
        state['executions']['EX-1']['termination']['snapshot'] = 'a' * 40
        # A run folder that cannot be listed, with an empty archive manifest: if the
        # listing error were dropped, no listed file would equal no archived row and
        # the run would be eligible. The listing error is the only reason.
        state['executions']['EX-1']['collection']['retention_manifest'] = []
        with unlistable(run):
            result = cleanup_candidates(self.root, read_artifact=read, **state)
        self.assertFalse(result[0]['eligible'])
        self.assertEqual(len(result[0]['reasons']), 1, result[0]['reasons'])
        self.assertTrue(result[0]['reasons'][0].startswith('[WinError 32] ')
                        and result[0]['reasons'][0].endswith(repr(str(run))), result[0]['reasons'])
        self.assertTrue(run.exists())

    def test_cleanup_archive_failure_is_local_degradation(self):
        run, state, archive, read = archived_run(self.root)
        candidates = cleanup_candidates(self.root, read_artifact=read, **state)
        original = deepcopy(state)

        def failed_reader(path, snapshot):
            raise RuntimeError('archive store unavailable')
        result = cleanup(self.root, candidates, current_state=lambda: state, read_artifact=failed_reader)
        self.assertEqual(result['status'], 'degraded')
        self.assertEqual([row['error'] for row in result['failures']],
                         ['cleanup prerequisites changed: archive_does_not_cover_current_files, archive_unverified: '
                          'archive store unavailable, termination_unverified: archive store unavailable'])
        self.assertEqual(state, original)
        self.assertTrue(run.exists())

    def test_descendant_reference_blocks_cleanup(self):
        result = cleanup_candidates(self.root, {'EX-1': {'id': 'EX-1', 'status': 'ended', 'artifact_bundle': 'bundle'}},
                                    protected_references={'runs/EX-1/needed.txt'})
        self.assertFalse(result[0]['eligible'])
        self.assertIn('protected_reference', result[0]['reasons'])

    def test_bundle_name_alone_never_proves_preservation(self):
        result = cleanup_candidates(self.root, {'EX-1': {'id': 'EX-1', 'status': 'ended', 'artifact_bundle': 'bundle'}},
                                    protected_references=set())
        self.assertFalse(result[0]['eligible'])
        # Nothing but the bundle name: no run folder, receipt, manifest, current state or approval.
        self.assertEqual(result[0]['reasons'], ['artifacts_not_verified', 'current_recovery_and_reservations_unexamined',
                                                'execution directory missing', 'outside_approved_scope',
                                                'termination_unconfirmed'])

    def test_cleanup_hashes_local_files_and_archive_rows_once(self):
        run, state, archive, read = archived_run(self.root)
        reader, git_dir, marks = Mock(side_effect=read), 'git-' + uuid.uuid4().hex, {}
        # Only a settled fingerprint may stand in for the bytes; a fresh file's times are set back.
        age(run / 'output.txt', 60)

        def run_file_opens():
            """Files of the run opened so far (each ``read_stable`` opens its file once)."""
            return len([event for event in opened if str(event[1][0]).startswith(str(run) + os.sep)])
        with audit_events('open') as opened:
            candidates = cleanup_candidates(self.root, **state, read_artifact=reader, git_dir=git_dir, marks=marks)
            self.assertTrue(candidates[0]['eligible'], candidates)
            self.assertEqual((run_file_opens(), reader.call_count), (1, 2))
            result = cleanup(self.root, candidates, current_state=lambda: state, read_artifact=reader,
                             git_dir=git_dir, marks=marks)
        self.assertEqual(result['deleted'], ['runs/EX-1'])
        # The pre-deletion recheck used fingerprints and matched archive rows.
        self.assertEqual(run_file_opens(), 1)
        self.assertEqual(reader.call_count, 3)  # only the termination receipt is parsed again

    def test_retention_requires_ended_closed_preserved_unrecovered_execution(self):
        run, state, archive, reader = archived_run(self.root)
        candidates = cleanup_candidates(self.root, **state, read_artifact=reader)
        self.assertEqual(candidates[0]['eligible'], True)
        result = cleanup(self.root, candidates, current_state=lambda: state, read_artifact=reader)
        self.assertEqual(result['deleted'], ['runs/EX-1'])
        self.assertFalse(run.exists())
        run.mkdir(parents=True)
        recovery = {'id': 'RY-1', 'started_at': '2026-09-25T00:00:00Z', 'execution_ids': ['EX-1'], 'dispositions': []}
        blocked = cleanup_candidates(self.root, {'EX-1': {'id': 'EX-1', 'status': 'ended',
                                                          'artifact_bundle': 'runtime/artifacts/EX-1'}},
                                     protected_references=set(), runtime={'recoveries': {'RY-1': recovery}})
        self.assertFalse(blocked[0]['eligible'])
        self.assertIn('recovery_pending', blocked[0]['reasons'])

    def test_cleanup_rechecks_reference_files_and_archive_before_deletion(self):
        for mutation in ('reference', 'local', 'archive', 'termination', 'reservation', 'recovery'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                run, state, archive, reader = archived_run(root)
                candidates = cleanup_candidates(root, **state, read_artifact=reader)
                self.assertTrue(candidates[0]['eligible'])
                if mutation == 'reference':
                    state['protected_references'].add('runs/EX-1/output.txt')
                elif mutation == 'local':
                    (run / 'new.txt').write_bytes(b'not archived')
                elif mutation == 'archive':
                    archive['runtime/artifacts/EX-1/output.txt'] = b'corrupt'
                elif mutation == 'termination':
                    archive['runtime/artifacts/EX-1/termination.json'] = b'{}'
                elif mutation == 'reservation':
                    state['runtime']['reservations'] = {'RS': {'owner_id': 'EX-1', 'state': 'held'}}
                else:
                    state['runtime']['recoveries'] = {'RY-1': {'id': 'RY-1', 'started_at': '2026-09-25T00:00:00Z',
                                                               'execution_ids': ['EX-1'], 'dispositions': []}}
                original = deepcopy(state)
                result = cleanup(root, candidates, current_state=lambda: state, read_artifact=reader)
                self.assertEqual(result['status'], 'degraded')
                self.assertEqual(len(result['failures']), 1)
                self.assertTrue(result['failures'][0]['error'].startswith('cleanup prerequisites changed: '),
                                result['failures'])
                self.assertTrue(run.exists())
                self.assertEqual(state, original)

    def test_retention_resolves_real_git_archive_bytes_at_pinned_commit(self):
        """About 0.2-0.3 s, over the 0.2 s unit budget: two publications through the storage contract on the in-process Git fake."""
        repository = record_store(self.root / 'repository')
        instance, runtime = current_state({'id': 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'}, {'executions': {}, 'activities': {}})
        head = repository.initialize(instance, runtime)
        run, state, archive, _ = archived_run(self.root / 'work')
        archived = repository.save_with_state(head, instance, runtime, artifacts=archive)[0]
        execution = state['executions']['EX-1']
        execution['termination']['snapshot'] = archived
        for row in execution['collection']['retention_manifest']:
            row['snapshot'] = archived
        reader = lambda path, snapshot: repository.read(path, snapshot)
        candidate = cleanup_candidates(self.root / 'work', **state, read_artifact=reader)
        self.assertTrue(candidate[0]['eligible'], candidate)
        result = cleanup(self.root / 'work', candidate, current_state=lambda: state, read_artifact=reader)
        self.assertEqual(result['deleted'], ['runs/EX-1'])
        self.assertEqual(repository.read('runtime/artifacts/EX-1/output.txt', archived), b'preserved result')


class PhysicalPathTests(unittest.TestCase):
    """Windows path aliases: a reparse point or a name Windows stores as another run."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_reparse_root_is_rejected_before_resolution(self):
        with tempfile.TemporaryDirectory() as outside:
            run, state, archive, reader = archived_run(Path(outside))
            junction(Path(outside) / 'runs', self.root / 'runs')
            try:
                candidates = cleanup_candidates(self.root, **state, read_artifact=reader)
            finally:
                remove_link(self.root / 'runs')
            self.assertFalse(candidates[0]['eligible'])
            self.assertIn(REPARSE + str(self.root / 'runs'), candidates[0]['reasons'])
            self.assertTrue(run.exists())

    def test_run_path_refuses_an_execution_id_that_windows_stores_as_another_run(self):
        # Windows drops a trailing dot, so the folder of "EX-1." would be that of "EX-1".
        with self.assertRaisesRegex(ValueError, '^path contains an invalid segment$'):
            _run_path(self.root, 'EX-1.')

    @unittest.skipUnless(os.name == 'nt', 'Windows junction probe')
    def test_real_windows_runs_junction_is_not_a_new_trusted_root(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside)
            (target / 'EX-1').mkdir()
            (target / 'EX-1/important').write_bytes(b'keep')
            link = junction(target, self.root / 'runs')
            try:
                result = cleanup_candidates(self.root, {'EX-1': {'id': 'EX-1', 'status': 'ended'}},
                                            protected_references=set())
                self.assertFalse(result[0]['eligible'])
                self.assertIn(REPARSE + str(link), result[0]['reasons'])
                self.assertEqual((target / 'EX-1/important').read_bytes(), b'keep')
            finally:
                remove_link(link)  # Only the exact temporary junction, not its target.
        run, state, archive, reader = archived_run(self.root)
        alias = junction(run, self.root / 'protected-alias')
        try:
            state['protected_references'] = {str(alias / 'output.txt')}
            result = cleanup_candidates(self.root, **state, read_artifact=reader)
            self.assertFalse(result[0]['eligible'])
            # The alias is refused, not followed, so no run is trusted through it.
            self.assertIn(REPARSE + str(alias), result[0]['reasons'])
            self.assertTrue(run.exists())
        finally:
            remove_link(alias)


class ReferenceClosureTests(unittest.TestCase):
    def test_reference_closure_follows_records_and_preserves_unknown_origins(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            run, state, archive, reader = archived_run(root)
            state['protected_references'] = {'KN'}
            # retention_inputs lists the references each persisted record holds.
            rows = [{'id': 'KN', 'root': 'research', 'family': 'knowledge',
                     'record': {'id': 'KN', 'dependencies': ['CP']}},
                    {'id': 'CP', 'root': 'research', 'family': 'formal_results',
                     'record': {'id': 'CP', 'path': 'runs/EX-1/output.txt', 'references': ['KN']}}]
            records, _ = retention_inputs({}, {}, rows)
            result = cleanup_candidates(root, **state, read_artifact=reader, reference_records=records)
            self.assertIn('protected_reference', result[0]['reasons'])
            result = cleanup_candidates(root, **state, read_artifact=reader)
            self.assertIn('unresolved_reference: KN', result[0]['reasons'])


if __name__ == '__main__':
    unittest.main()
