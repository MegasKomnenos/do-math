"""The producer's sealed evidence (``submission``, layer 2): the central seal keeps the snapshot read log, and a check reuses the prepared tool digest."""
import tempfile
from copy import deepcopy
import unittest

from do_math import submission
from do_math.canonical import canonical_json
from support.purpose_answers import common
from support.role_answers import seal_response
from support.provider_probes import ObservedCalls
from support.submission_protocol import ProtocolScene, producer_workspace


class FixtureMutationSealTests(unittest.TestCase):
    """K-30: a producer may revise only a hashed record in its fixed input."""
    def test_candidate_revision_cannot_target_an_absent_or_unhashed_input_record(self):
        from support.fakes.clock import FakeClock
        from support.model import Answer, ModelDouble
        for records in ([], [{'id': 'TK-fixed'}]):
            with self.subTest(records=records), tempfile.TemporaryDirectory() as directory:
                workspace, context = producer_workspace(directory, context_values={
                    'tasks': records, 'execution_profiles': [], 'grants': []})
                before = deepcopy(context)
                output = {**common('Revise only the supplied record.'),
                          'candidates': [{'revises_task_id': 'TK-fixed'}]}
                with self.assertRaisesRegex(AssertionError,
                        '^The fixture cannot revise a record absent from its fixed input: TK-fixed$'):
                    seal_response(output, context, workspace)
                model = ModelDouble(FakeClock())
                with self.assertRaisesRegex(AssertionError,
                        '^The fixture cannot revise a record absent from its fixed input: TK-fixed$'):
                    model.render(Answer(lambda out, ctx: output), 'research_preparation', context, workspace)
                self.assertNotIn('integration_bundles', output)
                self.assertEqual(context, before)

    def test_each_extension_mutation_requires_the_target_in_fixed_input(self):
        for family, key in (('knowledge_changes', 'id'), ('task_dispositions', 'task_id'),
                            ('revision_resolutions', 'record_id')):
            with self.subTest(family=family), tempfile.TemporaryDirectory() as directory:
                workspace, context = producer_workspace(directory)
                path = workspace / 'activity-extensions.json'
                raw = canonical_json({family: [{key: 'outside-fixed-input'}]})
                path.write_bytes(raw)
                before = deepcopy(context)
                output = {**common('No foreign revision.'), 'candidates': []}
                with self.assertRaisesRegex(AssertionError,
                        '^The fixture cannot revise a record absent from its fixed input: outside-fixed-input$'):
                    seal_response(output, context, workspace)
                self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(context, before)
                self.assertNotIn('integration_bundles', output)

    def test_revision_seal_keeps_exact_fixed_hashes_from_both_input_catalogs(self):
        from pathlib import Path
        from do_math import contracts, execution_profiles, initialization, knowledge, knowledge_io
        from do_math.configuration import DEFAULT_CONFIG
        from support.entry import entry
        from support.record_builders import observation_knowledge
        from support.role_answers import candidate
        from support.storage_records import INSTANCE_ID, engine_on, record_store

        ports = entry().ports
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instance, runtime = initialization.initialize_state(
                instance_id=INSTANCE_ID, goal='Inspect fixed revisions', workspace=root / 'work',
                config=DEFAULT_CONFIG, source_input='Inspect fixed revisions',
                clock=ports.clock, host=ports.host)
            instance.update(execution_profiles.build_profiles(instance['config'], host=ports.host))
            task = contracts.task_candidate_record(candidate('Fixed task'), task_id=ports.clock.new_id('TK'))
            task.pop('revises_task_id')
            task.update(status='planned', results=[])
            runtime['tasks'][task['id']] = task
            instance, runtime, kid = knowledge_io.import_candidate(
                instance, runtime, observation_knowledge('Fixed observation'),
                source_ref=instance['lifecycle']['input_id'], actor_ref='user', clock=ports.clock)
            store = record_store(root / 'repository', backend=ports.git_backend, clock=ports.clock)
            engine, _ = engine_on(store, instance, runtime, workspace=root / 'work', ports=ports)
            workspace = root / 'producer'
            context = engine._context({'id': 'AC-producer', 'role': 'research_preparation'},
                                      workspace, execution_id='EX-producer')
            submission.install_tools(workspace, context, contracts.action_schema(context['action']), None,
                                     clock=ports.clock)
            task_row, = context['tasks']
            knowledge_row, = context['knowledge_catalog']
            expected_hashes = {
                task['id']: knowledge.content_hash(engine.runtime['tasks'][task['id']]),
                kid: knowledge.content_hash(engine.instance['knowledge'][kid])}
            self.assertEqual({row['id']: row['content_sha256'] for row in (task_row, knowledge_row)},
                             expected_hashes)
            path = workspace / 'activity-extensions.json'
            raw = canonical_json({'knowledge_changes': [{'id': kid}]})
            path.write_bytes(raw)
            before = deepcopy(context)
            output = {**common('Use the exact visible revisions.'),
                      'candidates': [{'revises_task_id': task['id']}]}
            result = seal_response(output, context, workspace)
            self.assertIs(result, output)
            bundle, = result['integration_bundles']
            self.assertEqual(bundle['previous_hashes'], expected_hashes)
            self.assertEqual(bundle['members'], ['output', 'activity-extensions.json/knowledge_changes/0'])
            self.assertEqual((bundle['impact_set'], bundle['authority_refs']), ([], []))
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(context, before)


class SealedReadLogTests(unittest.TestCase):
    def test_sealed_submission_preserves_the_snapshot_read_log(self):
        with tempfile.TemporaryDirectory() as directory:
            scene = ProtocolScene(directory)
            log = scene.workspace / 'checks/reads.jsonl'
            log.parent.mkdir(exist_ok=True)
            log.write_bytes(b'{"request": "DC-1", "status": "ok"}\n')
            sealed = submission.seal_submission(scene.workspace, '.scratch/draft.json', execution_id='EX-worker',
                                                context=scene.context, schema=scene.schema,
                                                max_artifact_bytes=1024 * 1024, clock=scene.clock)
            self.assertEqual(sealed['artifacts']['reads.jsonl'], log.read_bytes())


class ToolDigestTests(unittest.TestCase):
    def test_producer_check_reuses_the_prepared_tool_digest(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace, context = producer_workspace(directory)
            output = {**common("No proposal."), "candidates": []}
            seal_response(output, context, workspace)
            draft = workspace / ".scratch/submission.json"
            draft.parent.mkdir(exist_ok=True)
            draft.write_bytes(canonical_json(output))
            # The legacy test wrapped read_stable with a patch; the unchanged function's calls are observed.
            with ObservedCalls(read=submission.read_stable) as read:
                result = submission._producer_check(workspace, ".scratch/submission.json", [], clock=_entry.ports.clock)
            self.assertEqual(result["tool_sha256"], context["submission_contract"]["tool_sha256"])
            paths = [str(arguments["path"]) for arguments in read.captured("read")]
            self.assertTrue(paths, 'the check read no file')
            # Preparation fixed the archive digest; a tool call never rereads the archive.
            self.assertFalse(any(path.endswith("submission-support.zip") for path in paths), paths)


if __name__ == "__main__":
    unittest.main()
