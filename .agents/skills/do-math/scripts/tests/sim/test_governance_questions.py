"""Question links the engine records and reads (``question_engine.QuestionEngineMixin``) over the real store.

The legacy tests ran these mixin methods on engines built without ``__init__``
(``research_fixtures.bare_engine``, ``engine_fixtures.context_engine``) whose store
was a hand-written reader or an autospec. Here each engine is a restored Sim's:
the same records are its in-memory state (``engine_with``, as
``support.engine_context.context_engine`` gives the legacy context state), and a
question's source artifact is published to the Sim's repository and read back
by the product's ``ResearchRepository`` at the engine's head.
"""
from copy import deepcopy
import unittest

from jsonschema import Draft202012Validator

from do_math import integration, questions
from do_math.canonical import canonical_json
from do_math.repository import ResearchRepository
from do_math.submission import extension_schema
from support.default_responder import common as role_output
from support.engine_context import context_engine, publish
from support.engine_lifecycle import ObservedCalls, code_of
from support.governance_sim import returned
from support.sim import Sim, warm_template

setUpModule = warm_template


def engine_with(instance, runtime, files=None):
    """A restored Sim's engine holding ``instance`` and ``runtime`` at a head that also holds artifact ``files``."""
    engine = Sim.activated().engine
    if files:
        publish(engine, files)
    engine.instance, engine.runtime = instance, runtime
    return engine


class QuestionTextTests(unittest.TestCase):
    def test_overflow_question_text_follows_its_artifact_pointer(self):
        source = 'runtime/artifacts/BA-overflow/input-overflow.json'
        reader = engine_with({"decisions": {}}, {"question_links": [{
            "id": "QU-overflow", "origin_execution_id": "EX-overflow",
            "origin_field": "resolution_question/question", "source_ref": source,
            "owner": "user", "target_ids": ["AC-held"], "unresolved_target_ids": ["AC-held"],
            "blocks": True, "status": "open", "resolution_ref": None}]},
            files={source: b'{"resolution_question":{"question":"Choose an authorized larger profile."}}'})
        row = reader._question_view()[0]
        self.assertEqual(row["text"], "Choose an authorized larger profile.")
        self.assertNotIn("source_status", row)

    def test_operational_question_uses_exact_execution_or_sealed_source_coordinate(self):
        sealed = 'runtime/artifacts/BA-sealed/sealed-output.json'
        engine = engine_with({'decisions': {}}, {'executions': {
            'EX-current': {'id': 'EX-current', 'role': 'operational_review',
                           'output': {'disposition': {'question': 'Choose the next action'}}},
            'EX-missing': {'id': 'EX-missing', 'role': 'operational_review', 'output': {}}},
            'question_links': [
                {'id': 'QU-current', 'origin_execution_id': 'EX-current',
                 'origin_field': 'output/disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-wrong', 'origin_execution_id': 'EX-current',
                 'origin_field': 'disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-missing', 'origin_execution_id': 'EX-missing',
                 'origin_field': 'output/disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-sealed', 'origin_execution_id': 'EX-current', 'source_ref': sealed,
                 'origin_field': 'disposition/question', 'owner': 'user', 'status': 'open'}]},
            files={sealed: canonical_json({'disposition': {'question': 'Question from the sealed response'}})})
        view = {row['id']: row for row in engine._question_view()}
        self.assertEqual(view['QU-current']['text'], 'Choose the next action')
        self.assertEqual(view['QU-sealed']['text'], 'Question from the sealed response')
        for identifier in ('QU-wrong', 'QU-missing'):
            self.assertIsNone(view[identifier]['text'])
            self.assertEqual(view[identifier]['source_status'], 'unavailable')
        self.assertEqual(engine._user_questions(), ['Choose the next action', 'Question from the sealed response'])


class RecordedQuestionTests(unittest.TestCase):
    def test_review_questions_include_pending_research_without_a_result(self):
        # A limit closure can publish while another slot's fixed question is still pending.
        owner = Sim.activated().engine
        owner.runtime = {"question_links": []}
        cycle = {"id": "RC-closed", "knowledge_id": "KN-reviewed", "followup": [], "research": {
            "EX-a:first": {"status": "pending", "question": "Is the binder fixed?", "result": None},
            "EX-b:second": {"status": "unresolved", "question": "Which domain?",
                            "result": {"output": {"questions": ["The domain remains open"]}}}}}
        owner._record_review_questions(cycle, "EX-closing")
        self.assertEqual([row["origin_field"] for row in owner.runtime["question_links"]], [
            "research/EX-a:first/question", "research/EX-b:second/question",
            "research/EX-b:second/result/output/questions/0"])
        self.assertTrue(all(row["source_id"] == "RC-closed" for row in owner.runtime["question_links"]))

    def test_submission_route_controls_only_its_affected_user_wait(self):
        validator = Draft202012Validator(extension_schema({'role': 'research_work'}))
        owner = Sim.activated().engine
        for blocking in (None, False, True):
            with self.subTest(blocking=blocking):
                route = {'question_index': 0, 'owner': 'user', 'target_ids': ['A'],
                         'reason': 'The answer determines the next action on A.'}
                if blocking is not None:
                    route['blocks'] = blocking
                extensions = {'question_routes': [route]}
                self.assertIsNone(validator.validate(extensions))
                owner.instance = {'id': 'I', 'decisions': {}}
                owner.runtime = {'tasks': {'A': {'id': 'A'}, 'B': {'id': 'B'}},
                    'question_links': [], 'executions': {'EX-route': {
                        'artifact_bundle': 'BA-route', 'extensions': extensions}}}
                output = {'questions': ['Which action on A is authorized?']}
                context = {'instance_id': 'I', 'action': {'role': 'research_work'},
                           'tasks': list(owner.runtime['tasks'].values())}
                self.assertEqual(questions.validate_extensions(output, extensions, context), [])
                owner._record_output_questions({'role': 'research_work', 'target': 'A'}, output, 'EX-route')
                (linked,) = owner.runtime['question_links']
                self.assertEqual(linked['blocks'], blocking is True)
                waits = lambda target: questions.user_waits(
                    {'role': 'research_work', 'target': target}, owner.instance, owner.runtime)
                self.assertEqual([row['question_id'] for row in waits('A')], [linked['id']] if blocking else [])
                self.assertEqual(waits('B'), [])
                questions.resolve_user(owner.runtime, [linked['id']], resolution_ref='DC-answer', affected_ids=['A'])
                self.assertEqual(waits('A'), [])
        route['blocks'] = 'true'
        self.assertEqual([(list(error.absolute_path), error.validator) for error in
                          validator.iter_errors({'question_routes': [route]})], [([ 'question_routes', 0, 'blocks'], 'type')])

    def test_question_mixin_publishes_advice_without_global_wait_and_resolves_atomically(self):
        from support.entry import entry
        _entry = entry()
        evidence = "runtime/artifacts/BA-answer/answer.md"
        h = engine_with({"id": "I"}, {"executions": {"E": {"id": "E", "role": "research_plan", "artifact_bundle": "B",
            "extensions": {"question_routes": [{"question_index": 0, "owner": "user", "target_ids": ["I"],
                                                "blocks": False, "reason": "optional"}]}}}},
            files={evidence: b"evidence"})
        h._record_output_questions({"role": "research_plan"}, {"questions": ["Optional priority?"]}, "E")
        self.assertEqual(questions.user_waits({"role": "research_plan"}, h.instance, h.runtime), [])
        one = questions.link(h.runtime, execution_id="A", field="questions/0", owner="research", targets=["I"], clock=_entry.ports.clock)
        h.runtime["executions"]["E"]["extensions"] = {"question_resolutions": [
            {"question_id": one["id"], "disposition": "resolved", "evidence_refs": [evidence], "reason": "answered"},
            {"question_id": "missing", "disposition": "resolved", "evidence_refs": [evidence], "reason": "bad"}]}
        # Artifact evidence resolves through the engine's store read, not a runtime family.
        with ObservedCalls(read=code_of(ResearchRepository.read_many)) as calls:
            with self.assertRaisesRegex(ValueError, "^only distinct open research or operations questions"):
                h._apply_question_resolutions("E")
        self.assertIn([evidence], [list(call['paths']) for call in calls.calls['read']])
        self.assertEqual(one["status"], "open")
        self.assertEqual([row["status"] for row in h.runtime["question_links"]], ["open", "open"])


class QuestionSourceTests(unittest.TestCase):
    def test_accepted_maintenance_question_reads_its_single_sealed_source(self):
        ref = 'runtime/artifacts/BA-sealed/submission/output.json'
        output = {**role_output('maintenance'), 'questions': ['Which result should be used?']}
        engine = context_engine(files={ref: canonical_json(output)})
        action = {'id': 'AC-sealed-question', 'role': 'maintenance'}
        engine.runtime['executions']['EX-sealed-question'] = {
            'id': 'EX-sealed-question', 'role': 'maintenance', 'status': 'ended',
            'action': action, 'submission_intent': {'output_ref': ref}}
        before = deepcopy(engine.runtime['question_links'])
        engine._record_output_questions(action, output, 'EX-sealed-question')
        engine._record_output_questions(action, output, 'EX-sealed-question')
        self.assertEqual(engine.runtime['question_links'][:len(before)], before)
        (linked,) = engine.runtime['question_links'][len(before):]
        self.assertEqual(linked['source_ref'], ref)
        view = {row['id']: row for row in engine._question_view()}
        self.assertEqual(view[linked['id']]['text'], 'Which result should be used?')

    def test_running_maintenance_question_preview_uses_captured_candidate_only(self):
        engine = Sim.activated().engine
        action = {'id': 'AC-preview-question', 'role': 'maintenance'}
        execution_id = 'EX-preview-question'
        engine._register_execution(action, {'id': execution_id, 'role': 'maintenance', 'status': 'running'})
        output = {**role_output('maintenance'), 'questions': ['Which condition needs a decision?']}
        context = {'action': action, 'snapshot': engine.head, 'execution_id': execution_id}
        ref = 'runtime/artifacts/preview/' + execution_id + '/output.json'
        artifacts = {ref: canonical_json(output)}
        before = canonical_json(engine.runtime)
        with ObservedCalls(validate=code_of(ResearchRepository.validate_candidate)) as calls:
            preview = integration.preview_bundles(engine.instance, engine.runtime, output, {}, context,
                execution_id=execution_id,
                apply_bundle=lambda instance, runtime, bundle: engine._apply_bundle_candidate(
                    instance, runtime, bundle, action=action, execution_id=execution_id,
                    extensions={}, question_source_ref=ref),
                validate_current=lambda *_: None,
                validate_candidate=lambda instance, runtime, bundle: engine._validate_bundle_candidate(
                    instance, runtime, bundle, artifacts=artifacts))
        self.assertEqual(preview['status'], 'accepted', preview['issues'])
        self.assertEqual(canonical_json(engine.runtime), before)
        self.assertEqual(len(calls.calls['validate']), 1)
        added = [row for row in preview['runtime']['question_links']
                 if row not in engine.runtime.get('question_links', [])]
        self.assertEqual([row['source_ref'] for row in added], [ref])
        self.assertNotIn('artifact_bundle', engine.runtime['executions'][execution_id])


if __name__ == '__main__':
    unittest.main()
