"""A checked import waits for the user's exact later approval (``governance_engine._governance_control``).

The start states are reached by events and restored from templates
(``support.governance_sim``): a user's input interpreted by the model double as
proposing charter ``CH2`` (goal ``Prove Q``), checked independently and waiting
for the user (``checked_sim``); or the same during public activation for the
initial input (``initial_checked_sim``). A test then approves as the user does:
through ``_governance_control``, the engine's handler of the approval request,
or through the public ``decision`` control the owner processes. Nothing replaces
an engine method or the store.
"""
from copy import deepcopy
import json
import unittest

from do_math import governance as gov
from do_math.engine import ResearchEngine
from support.engine_lifecycle import ObservedCalls, applied, code_of
from support.governance_sim import (CONFIGURATION, INPUT, approval, checked_bundle, checked_sim, initial_checked_sim)


def request(bundle, identifier='LATER', **changes):
    """The user's later approval request as the owner hands it to ``_governance_control``."""
    return {'id': identifier, 'action': 'decision', 'origin': 'user', 'text': 'Approve this exact checked change',
            'config': {'change': approval(bundle, **changes)}}


def reauthors(runtime, bundle):
    return [row for row in runtime['queue'] if row['role'] == 'intent_interpretation'
            and row.get('previous_import_id') == bundle['id']]


class LaterApprovalTests(unittest.TestCase):
    def test_exact_later_control_applies_once_and_queues_followup(self):
        sim = checked_sim()
        engine, bundle = sim.engine, checked_bundle(sim)
        self.assertTrue(engine._governance_control(request(bundle)))
        self.assertEqual(engine.instance['governance']['CH2']['content']['goal'], 'Prove Q')
        queue = deepcopy(engine.runtime['queue'])
        self.assertTrue(engine._governance_control(request(bundle)))
        self.assertEqual(engine.runtime['queue'], queue)
        # The product queue merges this follow-up into the same pending preparation request.
        self.assertTrue(any(a['role'] == 'research_preparation' and 'checked user information' in a['reason']
                            for a in queue))

    def test_stale_approval_rejects_and_routes_to_reauthor(self):
        sim = checked_sim()
        engine, bundle = sim.engine, checked_bundle(sim)
        charter = gov.governance_view(engine.instance)['charter']
        engine.instance['decisions'][charter['approval_ref']]['source_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, '^import authority or affected targets changed$'):
            engine._governance_control(request(bundle))
        self.assertNotIn('CH2', engine.instance['governance'])
        self.assertEqual(len(reauthors(engine.runtime, bundle)), 1)

    def test_corrected_exact_approval_cancels_unstarted_recheck_of_same_seal(self):
        """About 2.2 s under a full run, over the 2 s Sim budget: a restore and two public controls the owner processes."""
        sim = checked_sim()
        engine, bundle = sim.engine, checked_bundle(sim)
        wrong = sim.control('decision', text='Wrong sealed reference',
                            config={'change': approval(bundle, check_sha256='0' * 64)})
        engine.process_controls()
        wrong_result = engine.control_result(wrong['request_id'])
        self.assertEqual((wrong_result['effect'], wrong_result['reason']),
                         ('rejected', 'approval does not name the exact sealed interpretation and check'))
        self.assertEqual(len(reauthors(engine.runtime, bundle)), 1)
        exact = sim.control('decision', text='Approve this exact checked change', config={'change': approval(bundle)})
        engine.process_controls()
        self.assertEqual(engine.control_result(exact['request_id'])['effect'], 'applied')
        self.assertEqual(reauthors(engine.runtime, bundle), [])

    def test_original_changed_before_later_approval_is_not_applied(self):
        # Approval rechecks the public input the import interpreted (input_ref).
        sim = checked_sim()
        engine, bundle = sim.engine, checked_bundle(sim)
        (row,) = [row for row in engine.runtime['inputs'] if row['id'] == bundle['input_ref']]
        row['text'] = 'A different user original'
        with self.assertRaisesRegex(ValueError, '^original public input changed$'):
            engine._governance_control(request(bundle))
        self.assertNotIn('CH2', engine.instance['governance'])

    def test_import_source_and_public_input_have_distinct_global_identity(self):
        sim = checked_sim()
        engine, bundle = sim.engine, checked_bundle(sim)
        source = bundle['source']
        self.assertEqual((source['text'], bundle['input_ref']), (INPUT, 'input-Q'))
        self.assertNotEqual(source['id'], bundle['input_ref'])
        # A later public input that reuses the preserved source's ID gets a source of its own.
        sim.control('input', text=source['text'], request_id=source['id'])
        engine.process_controls()
        created = engine._apply_governance_intent({'id': 'AC-NEW', 'role': 'intent_interpretation',
            'target': source['id']}, bundle['output'], bundle['execution_id'])
        self.assertEqual(created['input_ref'], source['id'])
        self.assertNotEqual(created['source']['id'], source['id'])
        self.assertEqual(created['source']['sha256'], source['sha256'])


class InitialApprovalTests(unittest.TestCase):
    def test_initial_later_control_completes_initialization_without_new_check(self):
        sim = initial_checked_sim()
        engine = sim.engine
        bundle = checked_bundle(sim)
        self.assertEqual(bundle['input_ref'], engine.instance['lifecycle']['input_id'])
        self.assertEqual(engine.instance['lifecycle']['state'], 'initializing')
        self.assertNotIn('intent_check', engine.instance['lifecycle'])
        self.assertEqual(engine.instance['lifecycle']['activation']['missing'], ['independent_intent'])
        with ObservedCalls(activate=code_of(ResearchEngine._activate_initialization)) as calls:
            self.assertTrue(engine._governance_control(request(bundle)))
        self.assertEqual(engine.instance['lifecycle']['intent_check']['interpretation_execution_id'],
                         bundle['execution_id'])
        self.assertEqual(len(calls.calls['activate']), 1)
        # The attempt ran: the independent intent is now met, and the approved charter change left the
        # governance the adoption bound, so activation waits for the user to adopt it.
        self.assertEqual(engine.instance['lifecycle']['activation']['missing'], ['governance'])
        self.assertEqual(engine.instance['lifecycle']['state'], 'initializing')
        self.assertFalse(any(a['role'] == 'intent_interpretation' for a in engine.runtime['queue']))

    def test_failed_initial_followup_does_not_publish_partial_control_effect(self):
        sim = initial_checked_sim()
        engine = sim.engine
        bundle = checked_bundle(sim)
        # The author's execution record is the initial intent evidence the completion resolves.
        del engine.runtime['executions'][bundle['execution_id']]
        with self.assertRaisesRegex(ValueError, '^initial interpretation execution evidence does not resolve$'):
            engine._governance_control(request(bundle))
        self.assertNotIn('CH2', engine.instance['governance'])
        self.assertNotIn('application', engine.runtime['intent_imports'][bundle['id']])


class PublicApprovalTests(unittest.TestCase):
    def test_control_applies_actual_checked_import_and_records_one_public_result(self):
        sim = checked_sim()
        engine, bundle = sim.engine, checked_bundle(sim)
        before = [row for row in engine.runtime['history'] if row.get('kind') == 'user_control']
        sim.control('decision', text='Approve this exact checked change', config={'change': approval(bundle)})
        # One pass of the owner's control loop over its actual inbox, as process_controls runs it.
        with engine.store.writer_lock():
            engine._reload()
            with ObservedCalls(save=code_of(ResearchEngine._save),
                               extended=code_of(ResearchEngine._apply_extended_control)) as calls:
                engine._controls()
        self.assertEqual(engine.instance['governance']['CH2']['content']['goal'], 'Prove Q')
        self.assertEqual(engine.runtime['intent_imports'][bundle['id']]['application']['status'], 'applied')
        after = [row for row in engine.runtime['history'] if row.get('kind') == 'user_control']
        self.assertEqual(after[:len(before)], before)
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual(len(calls.calls['save']), 1)
        self.assertEqual(calls.calls['extended'], [])

    def test_git_changed_premise_rejects_later_approval_and_preserves_seal(self):
        sim = checked_sim()
        engine, bundle = sim.engine, checked_bundle(sim)
        sealed = deepcopy(bundle['check'])
        charter = gov.governance_view(engine.instance)['charter']
        audit = {'id': 'AU-LATER', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [], 'content': {
            'scope': ['P'], 'required_inputs': [charter['id']], 'assessor': 'goal_audit',
            'verdict_mapping': {'pass': 'satisfied', 'unknown': 'unresolved'}}}
        applied(sim, 'decision', text='Adopt a new premise before application',
                config={'change': {'kind': 'additional_audit', 'record': audit}})
        stale = sim.control('decision', text='Approval of the old checked premise', config={'change': approval(bundle)},
                            request_id='stale-premise-approval')
        engine.process_controls()
        stale_result = engine.control_result(stale['request_id'])
        self.assertEqual((stale_result['effect'], stale_result['reason']),
                         ('rejected', 'import authority or affected targets changed'))
        sim.restart()
        restarted = sim.engine
        self.assertNotIn('CH2', restarted.instance['governance'])
        self.assertEqual(restarted.runtime['intent_imports'][bundle['id']]['check'], sealed)
        self.assertTrue(any(a.get('previous_import_id') == bundle['id'] for a in restarted.runtime['queue']))



class SealedApprovalTests(unittest.TestCase):
    """The sealed import's approval after a rejected one, applied and replayed across a restart.

    The approval arrives as the CLI's ``decision --file`` sends it: the file's
    exact text (a CRLF JSON document) as the control text and its parsed object
    as the change (``cli.execute``; ``boundary.test_governance_cli_decision``
    covers the CLI reading the file).
    """

    def sealed_approval(self, sim):
        """The restarted engine after the wrong approval, its replay, and the exact CRLF approval."""
        engine, bundle = sim.engine, checked_bundle(sim)
        sealed = deepcopy(bundle['check'])
        spec = approval(bundle)
        wrong = approval(bundle, check_sha256='0' * 64)
        sim.control('decision', text='Wrong sealed reference', config={'change': wrong}, request_id='wrong-approval')
        engine.process_controls()
        rejected = engine.control_result('wrong-approval')
        self.assertEqual((rejected['effect'], rejected['reason']),
                         ('rejected', 'approval does not name the exact sealed interpretation and check'))
        replayed = sim.control('decision', text='Wrong sealed reference', config={'change': wrong},
                               request_id='wrong-approval')
        self.assertEqual(replayed['snapshot'], rejected['snapshot'])
        approval_text = json.dumps(spec, ensure_ascii=False, indent=2).replace('\n', '\r\n') + '\r\n'
        sim.control('decision', text=approval_text, config={'change': json.loads(approval_text)},
                    request_id='approve-Q')
        engine.process_controls()
        result = engine.control_result('approve-Q')
        self.assertEqual(result['effect'], 'applied')
        sim.restart()
        restarted = sim.engine
        self.assertTrue(any(row['text'] == approval_text for row in restarted.instance['governance_sources'].values()))
        self.assertEqual(restarted.runtime['intent_imports'][bundle['id']]['check'], sealed)
        self.assertFalse(any(a.get('previous_import_id') == bundle['id'] for a in restarted.runtime['queue']))
        replay = sim.control('decision', text=approval_text, config={'change': spec}, request_id='approve-Q')
        self.assertEqual(replay['snapshot'], result['snapshot'])
        return restarted

    def test_git_sealed_import_later_control_and_restart(self):
        """About 2.4 s under a full run, over the 2 s Sim budget: a restore, three public controls, a restart and a replay."""
        restarted = self.sealed_approval(checked_sim())
        self.assertEqual(gov.governance_view(restarted.instance)['goal'], 'Prove Q')

    def test_git_configuration_import_uses_public_transition_and_profiles(self):
        """About 3 s under a full run, over the 2 s Sim budget: a restore, three public controls (one rebuilding the profiles), a restart and a replay."""
        sim = checked_sim('configuration')
        engine = sim.engine
        expected, _ = engine._configure_candidate(engine.instance, engine.runtime,
                                                  {'action': 'configure', 'origin': 'user', 'config': CONFIGURATION})
        restarted = self.sealed_approval(sim)
        for field in ('config', 'role_profile_refs', 'execution_profiles', 'capacity_constraints'):
            self.assertEqual(restarted.instance[field], expected[field])


if __name__ == '__main__':
    unittest.main()
