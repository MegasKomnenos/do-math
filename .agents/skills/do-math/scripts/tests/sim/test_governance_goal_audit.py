"""The goal audit's additional audits (``governance_engine._apply_governance_goal_audit``, ``governance.evaluate_goal_audits``).

The user adopts an additional audit ``AU`` by public decision; one goal auditor
is registered by the engine as a returned execution and bound to the audit
input it read (``support.governance_sim.goal_auditor``), and its answer goes to
the engine's goal audit consumer. The instance is a restored public activation,
or one whose theorem ``k1`` the Lean double verified (``theorem_sim``): its
knowledge is usable, so only the audit's mapping decides the goal. Nothing
replaces an engine method, the store, or the product's knowledge checks.
"""
from copy import deepcopy
import unittest

import jsonschema

from do_math import governance as gov
from do_math.academic import apply_goal_assurance
from do_math.engine import ResearchEngine
from do_math.record_schemas.schemas import RECORDS
from support.engine_lifecycle import ObservedCalls, code_of
from support.governance_sim import adopt_audit, goal_auditor, theorem_sim
from support.sim import Sim


def setUpModule():
    Sim.activated()
    theorem_sim()


class AuditInputTests(unittest.TestCase):
    def test_audit_context_schema_binding_and_rejected_missing_results(self):
        sim = Sim.activated()
        adopt_audit(sim)
        engine = sim.engine
        action = {'role': 'goal_audit'}
        from do_math.context_store import prepare_role_input
        from do_math.execution_profiles import resolve_profile
        from support.role_input_requirements import assert_judgment_inputs
        workspace = sim.root / 'additional-audit-input'
        context = engine._context(action, workspace)
        profile = resolve_profile(sim.instance['execution_profiles'], sim.instance['role_profile_refs']['goal_audit'][0])
        fitted = prepare_role_input(context, instance=sim.instance, runtime=sim.runtime,
            role='goal_audit', profile=profile, snapshot=engine.head, workspace=workspace,
            activity_id='AY-additional-audit-input', install_submission_tools=True, clock=sim.clock)
        assert_judgment_inputs(self, 'goal_audit', fitted, workspace, producer_context=context)
        self.assertEqual(context['additional_audit_input'][0]['audit']['id'], 'AU')
        schema = engine._governance_schema(action, {'type': 'object', 'properties': {}, 'required': []})
        self.assertIn('additional_audits', schema['required'])
        execution = {'id': 'AUDITOR', 'role': 'goal_audit'}
        engine._bind_governance_input(action, execution, context)
        self.assertEqual(execution['additional_audit_input'], context['additional_audit_input'])
        engine.runtime['executions']['AUDITOR'] = execution
        with self.assertRaisesRegex(ValueError, '^all additional audits require actual verdicts$'):
            gov.evaluate_goal_audits(engine.instance, engine.runtime, 'AUDITOR', [])


class GoalConsumerTests(unittest.TestCase):
    def test_review_scheduling_preserves_goal_acceptance_and_stored_currentness(self):
        """~4.8s: acceptance, stored goal/restart and content/use demotion share one valid scene."""
        from do_math import knowledge_io, knowledge_records as kr
        from support.knowledge_builders import knowledge_candidate
        sim = theorem_sim()
        adopt_audit(sim)
        engine = sim.engine
        kid = next(iter(engine.instance['knowledge']))
        # An imported exposition reuses the checked formal result and has not
        # started identity review yet. The existing theorem remains usable.
        engine.instance, engine.runtime, pending = knowledge_io.import_candidate(engine.instance, engine.runtime,
            knowledge_candidate(title='Another exposition', lean_code='', declaration_names=[],
                formal_result_ref=engine.instance['knowledge'][kid]['formal_result_id']),
            source_ref='user:exposition', actor_ref='user', clock=sim.clock)
        action, output = goal_auditor(engine, verdict='pass')
        # This helper also supplies identity-review findings. Goal auditors use
        # the issued goal response contract, whose explanation is reason.
        output.pop('findings')
        jsonschema.Draft202012Validator(engine._response_schema(action)).validate(output)
        record = engine.instance['knowledge'][pending]
        self.assertNotIn('review_cycle_id', record)
        cycle = engine._start_identity_review(pending)
        self.assertEqual(record['review_cycle_id'], cycle)
        self.assertTrue(kr.usable_links(engine.instance, kid))
        self.assertEqual(engine._goal_basis_key(), action['basis'])
        judgment = engine._apply_governance_goal_audit(action, output, 'AUDITOR')
        self.assertIs(judgment['current'], True)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        engine._save()
        sim.restart()
        engine = sim.engine
        engine._invalidate_goal_currentness()
        self.assertIs(engine.instance['goal_judgments'][-1]['current'], True)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        self.assertFalse(any(e['kind'] == 'goal_basis_invalidated' for e in engine.runtime['events']))
        with self.assertRaisesRegex(ValueError, '^goal audit slot already sealed$'):
            engine._apply_governance_goal_audit(action, output, 'AUDITOR')
        # The same dependency's actual content still invalidates the stored
        # judgment, reopens the goal and queues the existing reassessment owner.
        stored = deepcopy((engine.instance, engine.runtime))
        current_key = engine._goal_basis_key()
        for change in ('content', 'use'):
            with self.subTest(change=change):
                engine.instance, engine.runtime = deepcopy(stored)
                if change == 'content':
                    engine.instance['knowledge'][kid]['title'] = 'Corrected mathematical evidence'
                else:
                    aid = kr.usable_links(engine.instance, kid)[0]['assessment_id']
                    engine.instance = kr.set_assessment_use(engine.instance, aid, 'suspended', 'Concrete defect', 'user')
                self.assertNotEqual(engine._goal_basis_key(), current_key)
                engine._invalidate_goal_currentness()
                self.assertIs(engine.instance['goal_judgments'][-1]['current'], False)
                self.assertEqual(engine.instance['goal_status'], 'unsolved')
                self.assertEqual(len([e for e in engine.runtime['events'] if e['kind'] == 'goal_basis_invalidated']), 1)
                self.assertTrue(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))

    def test_negative_goal_verdicts_emit_one_exact_followup_and_survive_restart(self):
        from support.engine_lifecycle import clear_work
        from support.wait_reporting import assert_status_report
        for decision in ('not_satisfied', 'unresolved'):
            with self.subTest(decision=decision):
                sim = theorem_sim()
                adopt_audit(sim)
                clear_work(sim)
                engine = sim.engine
                action, output = goal_auditor(engine)
                output.pop('findings')
                output.update(decision=decision, reason='현재 증거로 목표 보증을 확정할 수 없다.')
                judgment = engine._apply_governance_goal_audit(action, output, 'AUDITOR')
                self.assertEqual(judgment['decision'], decision)
                events = [e for e in sim.runtime['events'] if e['kind'] == 'goal_audit_completed']
                self.assertEqual(len(events), 1)
                event = events[0]
                self.assertEqual((event['basis_sha256'], event['judgment_ids'], event['next_owner']),
                    (action['basis'], [judgment['id']], 'research_plan'))
                self.assertNotEqual(sim.runtime['status'], 'completed')
                engine._save()
                sim.restart()
                engine = sim.engine
                events = deepcopy([e for e in sim.runtime['events'] if e['kind'] == 'goal_audit_completed'])
                before = deepcopy((sim.instance, sim.runtime))
                with self.assertRaisesRegex(ValueError, '^goal audit slot already sealed$'):
                    engine._apply_governance_goal_audit(action, output, 'AUDITOR')
                self.assertEqual((sim.instance, sim.runtime), before)
                engine._refresh_readiness()
                plans = [a for a in sim.runtime['queue'] if a['role'] == 'research_plan' and event['id'] in a.get('event_refs', [])]
                self.assertEqual(len(plans), 1)
                for queued in sim.runtime['queue']:
                    engine._bind_revision_action(queued)
                queue = deepcopy(sim.runtime['queue'])
                engine._refresh_readiness()
                self.assertEqual(sim.runtime['queue'], queue)
                self.assertEqual(engine._record_goal_audit_followup(action['basis'], [judgment]), event['id'])
                self.assertEqual([e for e in sim.runtime['events'] if e['kind'] == 'goal_audit_completed'], events)
                engine._save()
                report, human = assert_status_report(self, engine)
                self.assertIn('goal_status:', human)
                self.assertEqual(report['pending_actions'], len(queue))

    def test_actual_goal_consumer_stores_mapping_not_generic_satisfied(self):
        sim = theorem_sim()
        adopt_audit(sim)
        engine = sim.engine
        self.assertEqual(engine.instance['goal_judgments'], [])
        action, output = goal_auditor(engine)
        judgment = engine._apply_governance_goal_audit(action, output, 'AUDITOR')
        self.assertEqual(judgment['decision'], 'satisfied')
        self.assertEqual(judgment['additional_audits'][0]['decision'], 'not_satisfied')
        self.assertNotEqual(engine.runtime['status'], 'completed')
        self.assertEqual(engine.instance['goal_judgments'], [judgment])
        with self.assertRaisesRegex(ValueError, '^additional audit does not establish goal satisfaction$'):
            apply_goal_assurance(engine.instance, decision='mathematically_solved', basis=action['basis'],
                                 judgments=[judgment], runtime=engine.runtime)

    def test_actual_goal_consumer_rejects_missing_wrong_and_stale_audit_before_append(self):
        cases = [('missing', '^all additional audits require actual verdicts$'),
                 ('wrong_hash', '^audit required input is absent or stale$'),
                 ('wrong_assessor', '^audit assessor or verdict differs from approval$'),
                 ('stale', '^goal audit inputs changed before acceptance$'),
                 ('stale_audit_input', '^goal auditor did not receive these current additional-audit inputs$')]
        sim = Sim.activated()
        adopt_audit(sim)
        engine = sim.engine
        action, answer = goal_auditor(engine)
        charter = gov.governance_view(engine.instance)['charter']['id']
        for mutation, reason in cases:  # the stale cases change the charter, so they run last
            with self.subTest(mutation=mutation):
                output, request = deepcopy(answer), action
                if mutation == 'missing': output.pop('additional_audits')
                elif mutation == 'wrong_hash': output['additional_audits'][0]['input_hashes'] = {
                    ref: '0' * 64 for ref in output['additional_audits'][0]['input_hashes']}
                elif mutation == 'wrong_assessor': output['additional_audits'][0]['assessor'] = 'producer-claim'
                elif mutation == 'stale': engine.instance['governance'][charter]['content']['goal'] += ' changed'
                else:
                    # The request names the current goal basis, so the audit input the auditor read is what is stale.
                    request = {**action, 'basis': engine._goal_basis_key()}
                with self.assertRaisesRegex(ValueError, reason):
                    engine._apply_governance_goal_audit(request, output, 'AUDITOR')
                self.assertEqual(engine.instance['goal_judgments'], [])

    def test_goal_consumer_and_final_assurance_with_actual_verified_knowledge(self):
        for verdict, expected in [('partial', False), ('pass', True)]:
            with self.subTest(verdict=verdict):
                sim = theorem_sim()
                adopt_audit(sim)
                engine = sim.engine
                old_judgment = {'id': 'GJ-old', 'basis': 'old', 'slot': 0, 'required': 1,
                                'execution_id': 'EX-old', 'decision': 'not_satisfied', 'current': False}
                engine.instance['goal_judgments'].append(deepcopy(old_judgment))
                action, output = goal_auditor(engine, verdict=verdict)
                with ObservedCalls(followup=code_of(ResearchEngine._ensure_academic_followup)) as calls:
                    engine._apply_governance_goal_audit(action, output, 'AUDITOR')
                basis_schema = RECORDS['goal_judgments']['properties']['record_basis']
                record_basis = engine.instance['goal_judgments'][-1]['record_basis']
                self.assertTrue(record_basis)
                jsonschema.validate(record_basis, basis_schema)
                self.assertEqual(engine.instance.get('goal_status') == 'mathematically_solved', expected)
                self.assertEqual(len(calls.calls['followup']), 1 if expected else 0)
                self.assertEqual(engine.instance['goal_judgments'][0], old_judgment)
                self.assertEqual(len(engine.instance['goal_judgments']), 2)


class AuditRecoveryTests(unittest.TestCase):
    def test_public_audit_contract_and_actual_goal_judgment_survive_git_reload(self):
        import hashlib
        from pathlib import Path
        import tempfile
        from do_math import contracts, execution_lifecycle, integration, submission
        from do_math.canonical import canonical_json
        from support.state_builders import charter
        from support.execution_inputs import dispatched_launch
        from support.engine_lifecycle import applied
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(directory)
            engine = sim.engine
            applied(sim, 'decision', config={'change': {'kind': 'initialization', 'operation': 'governance',
                'records': [charter()]}}, text='Adopt charter')
            adopt_audit(sim, {'pass': 'satisfied', 'partial': 'not_satisfied'})
            action = {'id': 'AC-AUDITOR', 'role': 'goal_audit', 'target': None,
                      'basis': engine._goal_basis_key(), 'slot': 0, 'required': 1}
            ex = engine._register_execution(action, {'id': 'AUDITOR', 'role': 'goal_audit'})
            context = engine._context(action, Path(engine.instance['workspace']), execution_id='AUDITOR')
            self.assertEqual(context['additional_audit_input'][0]['audit']['id'], 'AU')
            self.assertIn('additional_audits', engine._response_schema(action)['required'])
            engine._bind_governance_input(action, ex, context)
            output = {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [],
                'summary': 'Audit has only partial evidence', 'questions': [],
                'reason': 'Preserve the actual goal judgment explanation',
                'additional_audits': [{'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': 'partial',
                    'reason': 'Only part of the scope has evidence',
                    'input_hashes': context['additional_audit_input'][0]['input_hashes']}]}
            for invalid, reason in (([], '^all additional audits require actual verdicts$'), ([{**output['additional_audits'][0], 'verdict': 'invented'}], '^audit assessor or verdict differs from approval$')):
                with self.assertRaisesRegex(ValueError, reason):
                    engine._apply(action, {**output, 'additional_audits': invalid}, 'AUDITOR')
                self.assertEqual(engine.instance['goal_judgments'], [])
            engine._apply(action, output, 'AUDITOR')
            # Preserve a crash immediately after the judgment/receipt publication,
            # before the original execution's final output_accepted bookkeeping.
            output['integration_bundles'] = [{'integration_id': 'IN-audit', 'members': ['output'],
                'impact_set': [], 'authority_refs': []}]
            fixed = {**deepcopy(context), 'action': action, 'snapshot': engine.head}
            schema = engine._response_schema(action)
            bundle = next(integration.split_bundles(output, {}, fixed))
            engine.runtime.setdefault('integrations', {})['IN-audit'] = {'id': 'IN-audit', 'execution_id': 'AUDITOR',
                'payload_sha256': bundle['payload_sha256'], 'members': ['output'], 'input_snapshot': engine.head}
            ex = engine.runtime['executions']['AUDITOR']
            execution_lifecycle.transition_execution(ex, 'ended', at=engine.instance['created_at'],
                outcome='start_failed', reason='crash fixture before finalization')
            profile = engine.instance['execution_profiles'][ex['execution_profile_ref']['id']]
            ex['launch_ticket'] = {**dispatched_launch(ex['id'], profile, jobs=sim.jobs, clock=sim.clock), 'phase': 'finished'}
            ex['capacity'] = {'local_termination': 'confirmed', 'reservation_ids': [], 'provider': None, 'process': None}
            ex['input_bundle'] = 'BA-audit-input'
            ex['input_snapshot'] = engine.head
            ex['result_ref'] = 'runtime/artifacts/BA-audit/result.json'
            artifacts = {ex['result_ref']: b'{"status":"completed"}',
                'runtime/artifacts/BA-audit-input/input/submission/context.json': canonical_json(fixed),
                'runtime/artifacts/BA-audit-input/schema.json': canonical_json(schema)}
            check = submission.check_submission(output, schema, fixed, {}, Path(engine.instance['workspace']),
                mode='receiver', execution_id='AUDITOR', tool_sha256='a' * 64, clock=sim.ports.clock)
            self.assertTrue(check['passed'], check['issues'])
            ex['submission_intent'] = {'schema_ref': contracts.schema_reference(schema)}
            refs = []
            for name, value in (('output', output), ('extensions', {}), ('check', check)):
                ref = 'runtime/artifacts/BA-audit/' + name + '.json'
                raw = canonical_json(value)
                artifacts[ref] = raw
                digest = hashlib.sha256(raw).hexdigest()
                ex['submission_intent'][name + '_ref'] = ref
                ex['submission_intent'][name + '_sha256'] = digest
                refs.append({'path': ref, 'sha256': digest, 'bytes': len(raw)})
            ex['submission_receipt'] = {'state': 'accepted', 'execution_id': 'AUDITOR',
                                        'payload': {'submission_check': {'artifacts': refs}}}
            submission.read_sealed_submission(ex, engine.head, lambda path, snapshot: artifacts[path])
            engine._save(artifacts)
            sim.restart()
            restarted = sim.engine
            self.assertEqual(restarted.instance['goal_judgments'][0]['additional_audits'][0]['decision'], 'not_satisfied')
            self.assertNotEqual(restarted.runtime['status'], 'completed')
            self.assertEqual(restarted.runtime['executions']['AUDITOR']['additional_audit_input'],
                             context['additional_audit_input'])
            judgments, events = deepcopy(restarted.instance['goal_judgments']), deepcopy(restarted.runtime['events'])
            result_ref = restarted.runtime['executions']['AUDITOR']['result_ref']
            activity = restarted.runtime['executions']['AUDITOR']['owner_activity_id']
            with restarted.store.writer_lock():
                restarted._recover_disappeared()
                self.assertEqual(restarted.runtime['waiting_actions'][action['id']]['kind'], 'submission_publication',
                                 restarted.runtime['waiting_actions'][action['id']])
                restarted._retry_submission_publications()
            sim.restart()
            final = sim.engine
            self.assertEqual(final.runtime['executions']['AUDITOR']['outcome'], 'output_accepted')
            self.assertEqual(final.runtime['activities'][activity]['status'], 'finished')
            self.assertEqual(final.runtime['executions']['AUDITOR']['result_ref'], result_ref)
            self.assertEqual(final.instance['goal_judgments'], judgments)
            self.assertEqual(final.runtime['events'], events)
            self.assertNotIn(action['id'], final.runtime['waiting_actions'])


if __name__ == '__main__':
    unittest.main()
