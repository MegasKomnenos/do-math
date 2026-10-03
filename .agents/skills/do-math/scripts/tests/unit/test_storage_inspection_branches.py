"""중앙 CHECK_AREAS 전건과 영역 지정·실제 저장 lifecycle 거부."""
from copy import deepcopy
from pathlib import Path
import re
import tempfile
import unittest

from do_math.record_schemas import validate_lifecycle
from do_math.state_checks import CHECK_AREAS, inspect_state, inspection_exit_code
from support.state_builders import current_state
from support.storage_records import record_store


class InspectionBranches(unittest.TestCase):
    def test_all_declared_areas_are_inspected_on_repository_loaded_state(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = record_store(Path(directory))
            head = repo.initialize(*current_state())
            _, instance, runtime = repo.load(head)
            result = inspect_state(instance, runtime, snapshot=head,
                read_artifact=lambda path: repo.read(path, head),
                read_artifacts=lambda paths: repo.read_many(paths, head, missing='omit'))
            self.assertEqual(result['requested_areas'], list(CHECK_AREAS))
            self.assertEqual([row['name'] for row in result['areas']], list(CHECK_AREAS))
            self.assertEqual(result['snapshot'], head)
            self.assertEqual(result['status'], 'healthy')
            self.assertEqual(result['findings'], [])
            self.assertEqual(result['not_checked'], [])
            self.assertEqual(inspection_exit_code(result), 0)

    def test_area_selection_rejects_bad_types_and_deduplicates_unknown_names(self):
        for value in ('record_storage', [None]):
            with self.assertRaisesRegex(ValueError, '^requested_areas must be a list of area names$'):
                inspect_state({}, {}, requested_areas=value)
        result = inspect_state({}, {}, requested_areas=['unknown', 'unknown'])
        self.assertEqual(result['requested_areas'], ['unknown'])
        self.assertEqual(result['not_checked'], ['unknown'])
        self.assertEqual(result['areas'], [{'name': 'unknown', 'status': 'incomplete', 'checked': False, 'findings': 1}])
        self.assertEqual(result['findings'], [{'area': 'unknown', 'status': 'incomplete',
            'message': 'unknown inspection area', 'blocked_scope': [], 'evidence': [], 'next_owner': 'operator'}])
        self.assertEqual(inspection_exit_code(result), 1)

    def test_lifecycle_rejects_missing_closed_projection_and_non_utc_highwater(self):
        for which, reason in (
                ('absent', 'current lifecycle contract: the lifecycle and the runtime status are required'),
                ('closed', 'current lifecycle contract: a permanently closed instance cannot have a live projection'),
                ('offset', 'current lifecycle contract: the persisted UTC high-water is absent or invalid')):
            instance, runtime = current_state()
            if which == 'absent':
                del instance['lifecycle']
            elif which == 'closed':
                instance['lifecycle']['permanently_closed'] = True
            else:
                runtime['last_observed_utc'] = '2026-01-01T09:00:00+09:00'
            with self.subTest(which=which), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                validate_lifecycle(instance, runtime)
        instance, runtime = current_state()
        self.assertIsNone(validate_lifecycle(instance, runtime))


    def test_loaded_machine_attempt_reports_absent_source_manifest_without_changing_state(self):
        from do_math.canonical import canonical_json
        from support.record_builders import execution_state

        with tempfile.TemporaryDirectory() as directory:
            repo = record_store(Path(directory))
            head = repo.initialize(*execution_state())
            _, instance, runtime = repo.load(head)
            before = canonical_json([instance, runtime])
            result = inspect_state(instance, runtime, snapshot=head, requested_areas=['start_import_input'])
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(result['snapshot'], head)
            self.assertEqual(result['not_checked'], [])
            self.assertEqual(result['areas'], [{'name': 'start_import_input', 'status': 'blocked',
                'checked': True, 'checked_invariants': ['load-time state contract validation',
                    'machine input manifest presence', 'execution manifest availability'],
                'not_checked': [], 'findings': 1}])
            self.assertEqual(result['findings'], [{'area': 'start_import_input', 'status': 'blocked',
                'message': 'machine execution has no source manifest', 'blocked_scope': ['EX-1'],
                'evidence': ['EX-1'], 'next_owner': 'maintenance'}])
            self.assertIs(type(result['areas'][0]['checked']), bool)
            self.assertEqual(inspection_exit_code(result), 1)
            self.assertEqual(canonical_json([instance, runtime]), before)
            self.assertEqual(repo.load(), (head, instance, runtime))


if __name__ == '__main__':
    unittest.main()
