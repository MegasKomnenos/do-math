"""The engine's receiver of interpretation results (``governance_engine._apply_governance_intent`` through ``_apply``).

The legacy ``engine_fixtures.routing_engine`` refused every store write and
replaced ``_record_output_questions``, ``_bind_revision_action`` and
``_cancel_selected_revision_targets``. Here the engine is a restored public
activation's: the input arrives by the public ``input`` control, the author and
checker executions are registered by the engine itself, and each stage's output
goes to the engine's ``_apply`` as the owner hands a received result. Calls to
``_record_output_questions`` are observed, not replaced.
"""
from copy import deepcopy
import unittest

from do_math.engine import ResearchEngine
from do_math.execution_lifecycle import transition_execution
from support.engine_lifecycle import ObservedCalls, code_of
from support.governance_sim import returned
from support.engine_context import assert_governance_documents
from support.sim import Sim, warm_template

setUpModule = warm_template

TEXT = 'Keep the original purpose.'


def authored(test, *, clarification=False, payload=None):
    """``(sim, bundle, check action, record calls, links before)``: the author stage of ``TEXT`` applied by the engine.

    With ``clarification`` the interpretation asks one blocking question
    ``Q-one``; ``payload`` is the proposed change of its unit ``IU-one``. The
    author ``EX-author`` has ended; the checker ``EX-check`` is registered for
    the queued check action, which is taken off the queue as the owner does.
    """
    sim = Sim.activated()
    engine = sim.engine
    request = sim.control('input', text=TEXT)
    engine.process_controls()
    target = request['request_id']
    output = {'summary': 'interpretation', 'used_sources': [], 'questions': ['Which scope?'] if clarification else [],
        'import_units': [{'unit_id': 'IU-one', 'source_range': {'start': 0, 'end': len(TEXT)}, 'interpretation': TEXT,
            'owner_kind': 'charter', 'owner_ref': 'CH-one', 'payload': payload or {},
            'decision_refs': [], 'question_refs': ['Q-one'] if clarification else []}],
        'question_details': [{'id': 'Q-one', 'question_index': 0, 'blocks': True, 'target_ids': [engine.instance['id']],
            'reason': 'scope choice changes the work', 'source_unit_ids': ['IU-one'], 'options': []}]
        if clarification else []}
    author = {'id': 'AC-author', 'role': 'intent_interpretation', 'target': target, 'lineage_id': 'AC-root'}
    execution = engine._register_execution(author, {'id': 'EX-author', 'role': 'intent_interpretation', 'status': 'running'})
    links = deepcopy(engine.runtime['question_links'])
    with ObservedCalls(record=code_of(ResearchEngine._record_output_questions)) as calls:
        engine._apply(author, output, 'EX-author')
    at = engine._lifecycle_now().isoformat()
    transition_execution(execution, 'stopping', at=at)
    transition_execution(execution, 'ended', at=at, outcome='execution_incomplete')
    (bundle,) = [row for row in engine.runtime['intent_imports'].values() if row['input_ref'] == target]
    (check,) = [row for row in engine.runtime['queue'] if row.get('import_id') == bundle['id']]
    engine.runtime['queue'].remove(check)
    returned(engine, check, 'EX-check')
    return sim, bundle, check, calls, links


def verdict(bundle, decision='approved', complete=True):
    """The independent check's output for ``bundle``; any decision but approved names one finding."""
    return {'decision': decision, 'scope_complete': complete, 'bundle_sha256': bundle['sha256'],
            'unit_ids': ['IU-one'], 'question_ids': [q['id'] for q in bundle['output']['question_details']],
            'findings': [] if decision == 'approved' else ['Missing second clause'],
            'summary': 'check', 'used_sources': [], 'questions': []}


class IntentConnections(unittest.TestCase):
    def test_clarification_still_receives_independent_check(self):
        sim, bundle, action, calls, links = authored(self, clarification=True)
        self.assertEqual(action['stage'], 'check')
        self.assertEqual(action['import_id'], bundle['id'])
        self.assertEqual(sim.runtime['question_links'], links)
        self.assertEqual(calls.calls['record'], [])

    def test_failed_check_returns_to_authoring_with_findings(self):
        sim, bundle, action, _, _ = authored(self)
        engine = sim.engine
        before = deepcopy(engine.runtime['queue'])
        questions = deepcopy(engine.runtime['questions'])
        output = verdict(bundle, 'revision_required', False)
        engine._apply(action, output, 'EX-check')
        assert_governance_documents(self, bundle['check'], owner='import_check', bundle=bundle,
            runtime=engine.runtime, output=output, execution_id='EX-check', source=bundle['source'])
        self.assertEqual(engine.runtime['queue'][:len(before)], before)
        (retry,) = engine.runtime['queue'][len(before):]
        self.assertEqual(retry['stage'], 'interpret')
        self.assertEqual(retry['lineage_id'], 'AC-root')
        self.assertEqual(retry['previous_import_id'], bundle['id'])
        self.assertEqual(retry['intent_repair']['findings'], ['Missing second clause'])
        self.assertEqual(engine.runtime['questions'], questions)

    def test_check_cannot_apply_unresolved_proposed_changes(self):
        sim, bundle, action, _, links = authored(self, clarification=True,
                                                payload={'kind': 'charter', 'record': {'id': 'CH-one'}})
        engine = sim.engine
        queue = deepcopy(engine.runtime['queue'])
        engine._apply(action, verdict(bundle), 'EX-check')
        assert_governance_documents(self, bundle['check'], owner='import_check', bundle=bundle,
            runtime=engine.runtime, output=verdict(bundle), execution_id='EX-check', source=bundle['source'])
        assert_governance_documents(self, bundle['output']['import_units'][0]['payload'],
            owner='import_payload', unit=bundle['output']['import_units'][0])
        self.assertNotIn('CH-one', engine.instance['governance'])
        self.assertEqual(engine.runtime['intent_imports'][bundle['id']]['application']['status'], 'awaiting_decision')
        self.assertEqual(engine.runtime['question_links'][:len(links)], links)
        (added,) = engine.runtime['question_links'][len(links):]
        self.assertEqual((added['source_kind'], added['source_id']), ('intent_import', bundle['id']))
        self.assertEqual(engine.runtime['queue'], queue)


if __name__ == '__main__':
    unittest.main()
