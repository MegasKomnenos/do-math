"""Waits a received submission leaves or ends, through whole role calls on a Sim (``core_engine._receive_submission``).

These scenes run the product's role calls end to end: the owner dispatches
the role, the worker's model double answers from the actual role input and
submits with the workspace tool, the owner seals the draft and later receives
it. What the legacy tests set up with a replaced ``_apply`` or an autospec
store is reached here by an actual response: a user's input whose checked
interpretation needs the user, and an identity review whose publication gate
finds the approved toolchain changed (the host port fake answers the
identity check). Each scenario is longer than one Sim test's budget.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import trust_inventory as records
from do_math.engine import ResearchEngine
from support.trust_inputs import validation_fixture
from support.engine_lifecycle import applied
from support.fakes.host import FakeHost
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template
from support.wait_reporting import assert_wait_report

setUpModule = warm_template

CHANGED = 'approved toolchain file changed'


def interpreted(kind, instance_id):
    """An interpretation answer whose checked import leaves ``kind`` for the user.

    ``import_application_authority``: the unit proposes a charter change, so the
    checked import waits for the user's exact approval (as the legacy
    ``PurposeAnswers`` answers a new goal). ``import_user_decision``: the unit asks
    one blocking question, so the applied import waits for the user's answer.
    The independent check keeps the default approving answer.
    """
    from support.model import Answer

    def make(output, context):
        if context['action'].get('stage', 'interpret') != 'interpret':
            return output
        unit = output['import_units'][0]
        if kind == 'import_application_authority':
            current = context['governance']['charter']
            record = {'id': 'CH-proposed-scope', 'kind': 'charter', 'revision': current['revision'] + 1,
                      'supersedes': [current['id']], 'content': {**deepcopy(current['content']),
                                                                 'goal': context['user_request']['text']}}
            unit.update(owner_ref=record['id'], payload={'kind': 'charter', 'record': record})
        else:
            output['questions'] = ['Which scope?']
            output['question_details'] = [{'id': 'Q-one', 'question_index': 0, 'blocks': True,
                'target_ids': [instance_id], 'reason': 'scope choice changes the work',
                'source_unit_ids': [unit['unit_id']], 'options': []}]
            unit['question_refs'] = ['Q-one']
        return output
    return Answer(make)


class WaitOwnershipTests(unittest.TestCase):
    def test_new_user_wait_survives_successful_response(self):
        """About 6 s per kind: the input's interpretation and its independent check are two role calls.

        The check's accepted response applies the import, which leaves a user wait
        for that same action; the receipt keeps it.
        """
        for kind in ('import_application_authority', 'import_user_decision'):
            with self.subTest(kind=kind):
                sim = Sim.activated()
                sim.model.on('intent_interpretation').reply(interpreted(kind, sim.instance_id))
                sim.control('input', text='Restrict the work to natural numbers below ten.')
                sim.run_until(lambda s: any(row.get('kind') == kind
                                            for row in s.runtime.get('waiting_actions', {}).values()), max_steps=12)
                (action_id, wait), = [(key, row) for key, row in sim.runtime['waiting_actions'].items()
                                      if row.get('kind') == kind]
                self.assertEqual(wait['kind'], kind)
                check, = [row for row in sim.runtime['executions'].values()
                          if row.get('role') == 'intent_interpretation' and row['action'].get('id') == action_id]
                self.assertEqual(check['action'].get('stage'), 'check')
                self.assertEqual(check['outcome'], 'output_accepted')
                receipt, = [row for row in sim.runtime['control_receipts'].values()
                            if row['execution_id'] == check['id'] and row['kind'] == 'submit_intent']
                self.assertEqual(receipt['state'], 'accepted')


def rerecord(environment, clock):
    """What ``setup_lean.rerecord`` records for the unchanged synthetic toolchain: one more baseline.

    Its host observation and representative compile are the toolchain tools' own
    (``sim.test_toolchain_tools`` covers them); the record file changes as theirs does.
    """
    path = Path(environment['toolchain_record']['path'])
    with records.writer_lock(path.parent):
        record = records.read_record(path)
        fingerprint = records.observe_fingerprint(environment['toolchain'])
        content = records.content_hashes(environment['toolchain'], fingerprint['files'])
        record['baselines'].append(records.new_baseline(fingerprint, content, validation_fixture(
            environment['toolchain'], path.parent / 'smoke.lean'), clock=clock))
        records.write_record(path, record)


class SubmissionPublicationWaitTests(unittest.TestCase):
    def test_sealed_response_waits_for_a_record_change_after_a_failed_identity_check(self):
        """About 15 s: a public activation of its own (its toolchain record changes), then a theorem's formal check
        and identity review.

        The review's accepted response is published only after the active
        environment's current identity passes; the host reports the approved
        toolchain changed, so the sealed response waits for the engine. The host
        answering again is not a record change and retries nothing; a re-record is,
        and the retried receipt publishes the sealed bytes.
        """
        with tempfile.TemporaryDirectory() as directory:
            host = FakeHost()
            sim = Sim.activated(Path(directory), host=host)
            sim.lean.allow('theorem k : 1 = 1 := rfl', ['k'], signatures={'k': 'k : 1 = 1'},
                declaration_evidence={'k': {'type': '1 = 1', 'value': None}}, axioms={'k': []}, dependencies={'k': {}})
            engine = sim.engine
            environment = engine.instance['trust_environments'][engine.instance['active_trust_environment']]
            applied(sim, 'knowledge', config={'operation': 'import', 'candidate': {
                'kind': 'theorem', 'title': 'k', 'statement': 'One equals one', 'summary': 'Reflexivity',
                'explanation': 'By reflexivity.', 'lean_code': 'theorem k : 1 = 1 := rfl',
                'declaration_names': ['k'], 'dependencies': []}})
            host.toolchain_errors = [CHANGED]

            def waiting(s):
                return [row for row in s.runtime.get('waiting_actions', {}).values()
                        if row.get('kind') == 'submission_publication']
            sim.run_until(waiting, max_steps=12)
            (wait,) = waiting(sim)
            self.assertEqual((wait['kind'], wait['next_owner']), ('submission_publication', 'engine'))
            self.assertEqual(wait['detail']['environment_id'], environment['id'])
            assert_wait_report(self, engine, wait['action']['id'])
            execution = engine.runtime['executions'][wait['execution_id']]
            self.assertEqual(execution['role'], 'identity_review')
            sealed_ref = execution['submission_intent']['output_ref']
            submitted = (Path(engine.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
                         / 'output.json').read_bytes()
            # The host answers the identity check again; the record did not change, so nothing is retried.
            host.toolchain_errors = []
            with ObservedCalls(receive=ResearchEngine._receive_submission) as calls:
                engine._retry_submission_publications()
            self.assertEqual(0, calls.count('receive'))
            self.assertIn(wait['action']['id'], engine.runtime['waiting_actions'])
            # A user re-records after restoring the files; the record change releases the wait.
            rerecord(environment, sim.clock)
            engine._retry_submission_publications()
            self.assertNotIn(wait['action']['id'], engine.runtime['waiting_actions'])
            self.assertEqual(engine.runtime['executions'][execution['id']]['outcome'], 'output_accepted')
            self.assertEqual(engine.store.read(sealed_ref), submitted)
            released = deepcopy(engine.store.load())
            engine._retry_submission_publications()
            self.assertEqual(engine.store.load(), released)
            with ObservedCalls(identity=FakeHost.toolchain_identity_errors,
                               scan=records.observe_fingerprint) as calls:
                engine.status()
            self.assertEqual((0, 0), (calls.count('identity'), calls.count('scan')))


if __name__ == "__main__":
    unittest.main()
