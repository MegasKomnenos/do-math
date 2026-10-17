"""The scheduled operator's value rules: task names and the read-only wake reasons (layer 2).

``supervision.task_names`` names the three scheduled tasks of one instance, and
``planning.research_wake_reasons`` is the wake decision the engine's status
reports to the operator. Both are pure over their inputs.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import planning, revisions
from do_math.supervision import task_names


AT = '2026-09-22T00:00:00+00:00'


class TaskNameTests(unittest.TestCase):
    def test_task_names_are_repository_scoped_and_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, instance = root / 'repository', 'RI-00000000000000000000000000'
            repository.mkdir()
            first = task_names(repository, instance)
            second = task_names(repository, instance)
            other = task_names(root / 'other-repository', instance)
        self.assertEqual(first, second)
        self.assertNotEqual(first['operator'], other['operator'])
        self.assertIn('Operator', first['operator'])
        self.assertIn('Engine', first['engine'])


class InstallationEvidenceTests(unittest.TestCase):
    def test_repair_reports_require_both_version_and_source_commit_even_when_git_is_unavailable(self):
        from jsonschema import validate, ValidationError
        from do_math.supervision import repair_report_schema
        report = {'summary': 'repair', 'observed_status': 'repaired', 'actions': [],
                  'evidence_paths': [], 'user_questions': [], 'next_step': 'verify',
                  'installation_version': 'a' * 64, 'source_commit': None}
        for diagnosed in (False, True):
            value = {**report, **({'repair_outcome': 'repaired', 'verification_evidence': ['log.txt']}
                                  if diagnosed else {})}
            schema = repair_report_schema(diagnosed=diagnosed)
            for field in ('installation_version', 'source_commit'):
                with self.subTest(diagnosed=diagnosed, missing=field):
                    # All other current report fields remain present.
                    self.assertIn(field, schema['required'])
                    with self.assertRaises(ValidationError) as caught:
                        validate({key: item for key, item in value.items() if key != field}, schema)
                    self.assertEqual(caught.exception.validator, 'required')
                    self.assertEqual(list(caught.exception.absolute_path), [])
                    self.assertEqual(caught.exception.message, f"'{field}' is a required property")
            validate(value, schema)

    def test_source_head_and_uncommitted_evidence_do_not_replace_installed_bytes(self):
        import hashlib
        from do_math.repair_execution import installation_evidence
        from do_math.canonical import exact_content_hash
        from support.operator_finish_ports import SourceGit
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory).resolve()
            skill = repository / 'skill'
            skill.mkdir()
            skill.joinpath('SKILL.md').write_bytes(b'dirty installed document\n')
            skill.joinpath('new.txt').write_bytes(b'untracked file\n')
            diff = b'diff --git a/skill/SKILL.md b/skill/SKILL.md\nactual dirty diff\n'
            backend = SourceGit(repository, diff=diff, tracked_paths=['skill/SKILL.md'])
            observed = installation_evidence(skill, backend=backend)
            self.assertEqual(observed['installation_version'], exact_content_hash({
                'SKILL.md': hashlib.sha256(b'dirty installed document\n').hexdigest(),
                'new.txt': hashlib.sha256(b'untracked file\n').hexdigest()}))
            self.assertEqual(observed['source_commit'], 'a' * 40)
            self.assertEqual(observed['source_tree'], 'b' * 40)
            self.assertEqual(observed['source_status'], 'observed')
            self.assertEqual(observed['tracked_diff']['sha256'], hashlib.sha256(diff).hexdigest())
            self.assertEqual(observed['untracked_installation_paths'], ['skill/new.txt'])
            self.assertEqual(backend.objects, {}, 'read-only evidence must not write a Git object')
            untracked = installation_evidence(skill, backend=SourceGit(repository, tree=None))
            self.assertIsNone(untracked['source_commit'])
            self.assertEqual(untracked['source_status'], 'unavailable')
            self.assertEqual(untracked['source_reason'], 'installation has no subtree in source HEAD')


class WakeReasonTests(unittest.TestCase):
    def test_due_research_reconsideration_is_a_wake_reason_without_mutating_state(self):
        instance = {'lifecycle': {'state': 'active'}, 'goal_status': 'unresolved'}
        runtime = {'status': 'waiting', 'tasks': {}, 'executions': {},
                   'queue': [{'role': 'research_preparation'}], 'next_research_reconsider_at': AT}
        before = deepcopy(runtime)
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now='2026-09-21T00:00:00Z'), [])
        reasons = planning.research_wake_reasons(instance, runtime, now=AT)
        self.assertEqual(reasons[0]['kind'], 'research_reconsider_due')
        self.assertEqual(runtime, before)

    def test_regeneration_and_task_timers_are_read_only_and_not_duplicated(self):
        instance = {'lifecycle': {'state': 'active'}, 'goal_status': 'unresolved'}
        revisit = {'kind': 'not_selected', 'execution_id': 'EX-plan', 'revisit': {'at': AT, 'event_refs': []}}
        runtime = {'status': 'waiting', 'tasks': {'TK-wait': {'id': 'TK-wait', 'selection_disposition': revisit}},
                   'queue': [{'role': 'research_work'}], 'executions': {}}
        due = planning.collect_due_events(instance, runtime, AT)
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT)[0]['kind'], 'task_revisit_due')
        runtime['events'] = due
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT), [])
        runtime.update(tasks={}, queue=[], history=[{'kind': 'task_repetition', 'lineage': 'exhaustion_empty',
            'lineage_id': 'empty', 'outcome': 'empty', 'regenerate_after': AT}])
        # The legacy test forced "no repetition hold" by patching; this history records none, so the product agrees.
        self.assertIsNone(revisions.repetition_hold(runtime, 'exhaustion_empty', 'empty'))
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now='2026-09-21T00:00:00Z'), [])
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT), [{'kind': 'research_regeneration_due'}])
        instance['id'] = 'RI-wait'
        runtime['question_links'] = [{'id': 'QU-user', 'status': 'open', 'owner': 'user',
                                     'blocks': True, 'target_ids': ['RI-wait'], 'unresolved_target_ids': ['RI-wait']}]
        self.assertIsNone(revisions.repetition_hold(runtime, 'exhaustion_empty', 'empty'))
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT), [])


if __name__ == '__main__':
    unittest.main()
