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
import json
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
from support.wait_reporting import assert_status_report

setUpModule = warm_template


def engine_with(instance, runtime, files=None):
    """A restored Sim's engine holding ``instance`` and ``runtime`` at a head that also holds artifact ``files``."""
    engine = Sim.activated().engine
    if files:
        publish(engine, files)
    engine.instance, engine.runtime = instance, runtime
    return engine


def source_question(identifier, execution_id, field, *, source_ref=None, targets=()):
    """Exact source-view fixture produced by the current question linker."""
    from support.fakes.clock import FakeClock
    row = questions.link({}, execution_id=execution_id, field=field, owner='user', targets=list(targets),
                         source_ref=source_ref, blocks=True if targets else False, clock=FakeClock())
    row['id'] = identifier
    return row


class QuestionTextTests(unittest.TestCase):
    def test_overflow_question_text_follows_its_artifact_pointer(self):
        source = 'runtime/artifacts/BA-overflow/input-overflow.json'
        reader = engine_with({"decisions": {}}, {"question_links": [source_question('QU-overflow', 'EX-overflow',
            'resolution_question/question', source_ref=source, targets=['AC-held'])]},
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
                source_question('QU-current', 'EX-current', 'output/disposition/question'),
                source_question('QU-wrong', 'EX-current', 'disposition/question'),
                source_question('QU-missing', 'EX-missing', 'output/disposition/question'),
                source_question('QU-sealed', 'EX-current', 'disposition/question', source_ref=sealed)]},
            files={sealed: canonical_json({'disposition': {'question': 'Question from the sealed response'}})})
        view = {row['id']: row for row in engine._question_view()}
        self.assertEqual(view['QU-current']['text'], 'Choose the next action')
        self.assertEqual(view['QU-sealed']['text'], 'Question from the sealed response')
        for identifier in ('QU-wrong', 'QU-missing'):
            self.assertIsNone(view[identifier]['text'])
            self.assertEqual(view[identifier]['source_status'], 'unavailable')
        self.assertEqual(engine._user_questions(), ['Choose the next action', 'Question from the sealed response'])


class RecordedQuestionTests(unittest.TestCase):
    def test_sealed_questions_resolve_by_owner_with_partial_user_answer_and_restart(self):
        """About 5.5 s: two worker submissions, scoped public answers and cold owner replay."""
        from pathlib import Path
        from support.engine_lifecycle import applied, clear_work
        from support.model import ModelDouble
        from support.default_responder import DefaultResponder

        sim = Sim.activated()
        clear_work(sim)
        charter = next(row['id'] for row in sim.instance['governance'].values() if row['kind'] == 'charter')

        class QuestionResponder(DefaultResponder):
            def respond(self, role, context, workspace):
                output = super().respond(role, context, workspace) if role == 'intent_interpretation' else role_output(role)
                if context['action'].get('reason') == 'Publish scoped questions':
                    output['questions'] = ['Choose the scope', 'Check the lemma', 'Inspect the operation']
                    extensions = {'question_routes': [
                        {'question_index': 0, 'owner': 'user', 'target_ids': [sim.instance_id, charter],
                         'blocks': True, 'reason': 'These two scopes need a user choice'},
                        {'question_index': 1, 'owner': 'research', 'target_ids': [],
                         'reason': 'Research owns the lemma'},
                        {'question_index': 2, 'owner': 'operations', 'target_ids': [sim.instance_id],
                         'reason': 'Inspect the instance support', 'obligation': {'kind': 'other',
                             'subject_ref': sim.instance_id, 'requirement_ref': 'support'}}]}
                else:
                    assigned = set(context['action'].get('question_ids', []))
                    extensions = {'question_resolutions': [
                        {'question_id': row['id'], 'disposition': 'resolved',
                         'reason': 'The preserved first receipt supplies the answer',
                         'evidence_refs': [row['origin_execution_id']],
                         **({'generation': context['action']['question_generation'],
                             'affected_ids': context['action']['question_target_ids']} if row['owner'] == 'operations' else {})}
                        for row in context['question_links'] if row['status'] == 'open'
                        and (row['id'] in assigned or row['owner'] == 'research' and role == 'research_plan')]}
                (Path(workspace) / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                return output

        sim.model = ModelDouble(sim.clock, QuestionResponder())
        applied(sim, 'request', text='Publish scoped questions', config={'role': 'maintenance'})
        sim.run_until(lambda s: len(s.runtime['question_links']) == 3 and
                      all(e['status'] == 'ended' for e in s.runtime['executions'].values()), max_steps=1)
        original = deepcopy(sim.runtime['question_links'])
        self.assertEqual({row['owner'] for row in original}, questions.QUESTION_OWNERS)
        self.assertTrue(all(row['status'] == 'open' for row in original))
        user = next(row for row in original if row['owner'] == 'user')
        self.assertEqual(next(row for row in original if row['owner'] == 'operations')['target_ids'], [sim.instance_id])
        def reported_questions():
            report, human = assert_status_report(self, sim.engine)
            rows = {row['id']: row for row in report['question_links']}
            for stored in sim.runtime['question_links']:
                row = rows[stored['id']]
                self.assertEqual({key: row[key] for key in stored}, stored)
                header = 'question ' + row['id'] + ':'
                if row['status'] != 'open':
                    self.assertNotIn(header, human)
                    continue
                self.assertIn(header + ' status=open next=' + row['owner'], human)
                self.assertIn('reason=' + str(row.get('routing_reason')), human)
                self.assertIn('  text: ' + json.dumps(row['text'], ensure_ascii=False), human)
                for field in ('origin_execution_id', 'origin_field', 'source_ref'):
                    self.assertIn(json.dumps(row[field], ensure_ascii=False), human)
                self.assertIn('  targets: ' + json.dumps({key: row[key] for key in
                    ('target_ids', 'unresolved_target_ids')}, ensure_ascii=False, sort_keys=True), human)
            return report, rows, human

        report, rows, human = reported_questions()
        self.assertEqual(report['tasks'], [])
        self.assertEqual(report['questions'], ['Choose the scope'])
        self.assertEqual({row['owner']: row['text'] for row in report['question_links']},
                         {'user': 'Choose the scope', 'research': 'Check the lemma', 'operations': 'Inspect the operation'})
        self.assertIn('Check the lemma', human)
        self.assertIn('Inspect the operation', human)
        # Returned mutable fields belong to the observer, not the stored question links.
        rows[user['id']]['unresolved_target_ids'].clear()
        self.assertEqual(sim.runtime['question_links'], original)
        self.assertEqual(sim.engine.store.load()[2]['question_links'], original)
        waiting = lambda target: questions.user_waits({'id': target, 'role': 'research_plan'}, sim.instance, sim.runtime)
        self.assertEqual([row['question_id'] for row in waiting(sim.instance_id)], [user['id']])
        calls = len(sim.model.calls)
        applied(sim, 'input', text='Unrelated information does not answer a question')
        self.assertEqual(sim.runtime['question_links'], original)
        request = applied(sim, 'decision', request_id='UI-partial-question', config={'change': {
            'kind': 'question_answer', 'text': 'Resolve the instance scope only',
            'target_ids': [sim.instance_id], 'resolves_questions': [user['id']]}})
        partial = deepcopy(sim.runtime['question_links'])
        answered = next(row for row in partial if row['id'] == user['id'])
        self.assertEqual((answered['status'], answered['unresolved_target_ids']), ('open', [charter]))
        self.assertEqual(len(answered['resolution_history']), 1)
        self.assertEqual(waiting(sim.instance_id), [])
        self.assertEqual([row['question_id'] for row in waiting(charter)], [user['id']])
        sim.restart()
        sim.control('decision', request_id=request['request_id'], config={'change': {
            'kind': 'question_answer', 'text': 'Resolve the instance scope only',
            'target_ids': [sim.instance_id], 'resolves_questions': [user['id']]}},
            text='lifecycle test control: decision')
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['question_links'], partial)
        self.assertEqual(len(sim.model.calls), calls)
        report, rows, human = reported_questions()
        self.assertEqual(rows[user['id']]['target_ids'], [sim.instance_id, charter])
        self.assertEqual(rows[user['id']]['unresolved_target_ids'], [charter])
        sim.model.responder = QuestionResponder()
        sim.run_until(lambda s: all(row['status'] != 'open' for row in s.runtime['question_links']
                                   if row['owner'] == 'operations'), max_steps=4)
        applied(sim, 'request', text='Answer the preserved research question', config={'role': 'research_plan'})
        sim.run_until(lambda s: all(row['status'] != 'open' for row in s.runtime['question_links']
                                   if row['owner'] == 'research'), max_steps=4)
        resolved = deepcopy(sim.runtime['question_links'])
        for row in resolved:
            if row['owner'] == 'user':
                self.assertEqual(row, answered)
            else:
                self.assertEqual(row['status'], 'resolved')
                self.assertEqual(len(row['resolution_history']), 1)
                execution = sim.runtime['executions'][row['resolution_ref']]
                self.assertEqual(execution['submission_receipt']['state'], 'accepted')
                self.assertEqual(execution['role'], 'maintenance' if row['owner'] == 'operations' else 'research_plan')
        report, rows, human = reported_questions()
        self.assertEqual({row['owner']: row['status'] for row in rows.values()},
                         {'user': 'open', 'research': 'resolved', 'operations': 'resolved'})
        calls_after_resolution = len(sim.model.calls)
        applied(sim, 'decision', config={'change': {'kind': 'question_answer', 'text': 'Resolve the remaining scope',
            'target_ids': [charter], 'resolves_questions': [user['id']]}})
        self.assertEqual(waiting(charter), [])
        final = deepcopy(sim.runtime['question_links'])
        self.assertEqual(len(next(row for row in final if row['id'] == user['id'])['resolution_history']), 2)
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['question_links'], final)
        # Unrelated queued input may have run its normal interpretation and
        # preparation. The final answer/restart itself starts no model call.
        self.assertEqual(len(sim.model.calls), calls_after_resolution)
        report, rows, human = reported_questions()
        self.assertEqual(report['questions'], [])
        self.assertNotIn('question ', human)

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
            'action': {'role': 'research_plan'},
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
        self.assertEqual(calls.calls['read'], [])
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
            'action': action, 'submission_intent': {'output_ref': ref}, 'extensions': {'question_routes': [
                {'question_index': 0, 'owner': 'research', 'target_ids': [], 'reason': 'Research decides the result'}]}}
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
        extensions = {'question_routes': [{'question_index': 0, 'owner': 'research', 'target_ids': [],
                                          'reason': 'The scope needs research judgment'}]}
        artifacts = {ref: canonical_json(output)}
        before = canonical_json(engine.runtime)
        with ObservedCalls(validate=code_of(ResearchRepository.validate_candidate)) as calls:
            preview = integration.preview_bundles(engine.instance, engine.runtime, output, extensions, context,
                execution_id=execution_id,
                apply_bundle=lambda instance, runtime, bundle: engine._apply_bundle_candidate(
                    instance, runtime, bundle, action=action, execution_id=execution_id,
                    extensions=extensions, question_source_ref=ref),
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


class OperationsHandlingTests(unittest.TestCase):
    def setUp(self):
        from support.engine_lifecycle import clear_work, task
        self.sim = Sim.activated()
        clear_work(self.sim)
        task(self.sim.engine, 'TK-support')
        task(self.sim.engine, 'TK-later')
        self.sim.engine._save()

    def report(self, execution_id, targets, *, existing=None, observation_ref=None):
        from support.engine_lifecycle import _ended_execution
        engine = self.sim.engine
        _ended_execution(engine, execution_id, 'research_work')
        route = {'question_index': 0, 'owner': 'operations', 'target_ids': targets, 'blocks': True,
            'reason': 'These targets depend on the same support obligation',
            'obligation': {'kind': 'execution_support', 'subject_ref': 'TK-support', 'requirement_ref': 'tool:scholarly'}}
        if existing:
            route['existing_question_id'] = existing
        if observation_ref:
            route.update(reopen_basis_refs=[observation_ref], reopen_reason='A newly preserved observation reports a real recurrence')
        engine.runtime['executions'][execution_id]['extensions'] = {'question_routes': [route]}
        output = {'questions': ['Inspect the supplied support and report the observed scope.']}
        source = 'runtime/artifacts/BA-' + execution_id + '/output.json'
        engine._record_output_questions({'role': 'research_work', 'target': 'TK-support'}, output, execution_id, source_ref=source)
        engine._reconcile_question_actions()
        engine._save({source: canonical_json(output)})
        return next(q for q in engine.runtime['question_links'] if q['obligation']['subject_ref'] == 'TK-support')

    def test_live_resolution_preserves_a_new_observation_on_the_same_target(self):
        row = self.report('EX-original-observation', ['TK-support'])
        engine = self.sim.engine
        action = next(a for a in engine.runtime['queue'] if a.get('question_ids') == [row['id']])
        prepared = engine._prepare_call(action)
        self.assertIsInstance(prepared, dict)
        eid = prepared['execution_id']
        context, _ = engine._issued_input(engine.runtime['executions'][eid])
        ref = 'runtime/artifacts/BA-new-support/failure.txt'
        engine._save({ref: b'A new support attempt failed after the handler fixed its input.\n'})
        self.report('EX-new-observation', ['TK-support'], existing=row['id'], observation_ref=ref)
        extension = {'question_resolutions': [{'question_id': row['id'], 'generation': 1,
            'affected_ids': ['TK-support'], 'disposition': 'resolved', 'evidence_refs': ['TK-support'],
            'reason': 'Only the original fixed observation was inspected'}]}
        output = {**role_output('maintenance'), 'report': 'The fixed original observation was checked'}
        preview = integration.preview_bundles(engine.instance, engine.runtime, output, extension, context,
            execution_id=eid,
            apply_bundle=lambda i, r, b: engine._apply_bundle_candidate(i, r, b, action=prepared['action'],
                execution_id=eid, extensions=extension),
            validate_current=lambda i, r, b: engine._validate_bundle_current(i, r, b, action=prepared['action'],
                execution_id=eid, context=context), validate_candidate=engine._validate_bundle_candidate)
        self.assertEqual(preview['status'], 'accepted', preview['issues'])
        remaining = next(q for q in preview['runtime']['question_links'] if q['id'] == row['id'])
        self.assertEqual((remaining['status'], remaining['unresolved_target_ids']), ('open', ['TK-support']))
        self.assertEqual(remaining['handling']['generation'], 2)
        self.assertFalse(any(a.get('question_ids') == [row['id']] and a.get('question_generation') == 2
                             for a in preview['runtime']['queue']))
        self.assertEqual(engine.runtime['executions'][eid]['action']['question_generation'], 1)

    def test_reports_restart_and_live_addition_preserve_one_fixed_handler_scope(self):
        from pathlib import Path
        import tempfile
        from do_math.execution_lifecycle import transition_execution
        row = self.report('EX-first-report', ['TK-support'])
        qid = row['id']
        self.report('EX-second-report', ['TK-support'], existing=qid)
        self.sim.restart()
        engine = self.sim.engine
        engine._reconcile_question_actions()
        handlers = [a for a in engine.runtime['queue'] if a.get('question_ids') == [qid]]
        self.assertEqual(len(handlers), 1)
        action = handlers[0]
        execution = engine._register_execution(action, {'id': 'EX-support-handler', 'role': 'maintenance', 'status': 'running'})
        fixed = deepcopy(execution['action'])
        row = self.report('EX-later-report', ['TK-later'], existing=qid)
        self.assertEqual(execution['action'], fixed)
        self.assertEqual(row['handling']['execution_ids'], ['EX-support-handler'])
        self.assertEqual(row['unresolved_target_ids'], ['TK-support', 'TK-later'])
        self.assertEqual(row['handling']['generation'], 1)
        self.assertEqual(len([a for a in engine.runtime['queue'] if a.get('question_ids') == [qid]]), 1)
        with tempfile.TemporaryDirectory() as directory:
            context = engine._context(action, Path(directory), execution_id=execution['id'])
        assigned, = context['operations_questions']
        self.assertEqual(assigned['assigned_target_ids'], ['TK-support'])
        self.assertEqual(len(assigned['reports']), 3)
        resolution = {'question_id': qid, 'disposition': 'resolved', 'generation': 1,
            'affected_ids': ['TK-support'], 'evidence_refs': ['TK-support'], 'reason': 'Only the fixed target was inspected'}
        self.assertEqual(questions.validate_extensions({}, {'question_resolutions': [resolution]}, context), [])
        resolution['affected_ids'].append('TK-later')
        self.assertTrue(questions.validate_extensions({}, {'question_resolutions': [resolution]}, context))
        resolution['affected_ids'] = ['TK-support']
        resolution['generation'] = 2
        self.assertTrue(questions.validate_extensions({}, {'question_resolutions': [resolution]}, context))
        at = engine.ports.clock.now()
        transition_execution(execution, 'stopping', at=at)
        transition_execution(execution, 'ended', at=at, outcome='execution_incomplete')
        engine._save()
        self.sim.restart()
        self.assertEqual(next(q for q in self.sim.runtime['question_links'] if q['id'] == qid)['handling']['execution_ids'],
                         ['EX-support-handler'])

    def test_paused_owner_preserves_reports_without_starting_triage_or_releasing_pause(self):
        from support.engine_lifecycle import applied
        applied(self.sim, 'pause')
        pause = deepcopy(self.sim.runtime['user_pause'])
        row = self.report('EX-preserved-report', ['TK-support'])
        self.assertEqual(row['handling']['state'], 'pending')
        self.assertFalse(any(a.get('question_ids') == [row['id']] for a in self.sim.runtime['queue']))
        calls = len(self.sim.model.calls)
        self.sim.engine.run(max_steps=1)
        self.assertEqual(len(self.sim.model.calls), calls)
        self.assertEqual(self.sim.runtime['user_pause'], pause)
        self.assertEqual(self.sim.engine.status()['status'], 'paused')


if __name__ == '__main__':
    unittest.main()
