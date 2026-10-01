"""Fixed planning populations and deferred review inputs with actual snapshots."""
from copy import deepcopy
import json
import unittest

from do_math import knowledge_records, submission
from do_math.canonical import canonical_json
from support.record_builders import task_disposition
from support.role_answers import seal_response
from support.default_responder import common
from support.engine_lifecycle import task, approve, clear_work, grant, _ended_execution
from support.engine_purpose import drive
from support.live_finish_inputs import artifact_scene, issued_plan
from support.provider_probes import ObservedCalls
from support.review_research import InvestigationResponder, research_sim
from support.review_sim import produced_sim, reviewed_theorem
from support.sim import warm_template
from support.storage_probes import Returns


def setUpModule():
    warm_template()
    produced_sim()
    research_sim()


class InputConnections(unittest.TestCase):
    def test_fixed_question_is_packaged_and_answer_returns_to_its_seat(self):
        from do_math.context_store import prepare_role_input
        sim = research_sim()
        responder = sim.model.responder = InvestigationResponder()
        captured = []
        original = responder.runner.answer

        def answer(role, context, workspace):
            if role == 'supplemental_research':
                captured.append(deepcopy(context))
                self.assertNotIn('role_review', context)
                request = context['review_research']
                cycle = sim.runtime['review_cycles'][context['action']['review_cycle_id']]
                self.assertEqual(request['id'], context['action']['research_request_id'])
                self.assertEqual(cycle['research'][request['id']]['status'], 'pending')
            output = original(role, context, workspace)
            if role == 'identity_review' and context['action']['stage'] == 'initial' and context['action']['slot'] == 'initial-0' \
                    and not context['role_review']['supplemental_results']:
                # Keep the original defer_review_for_research question and exact
                # source population, while the real worker performs the request.
                extension_path = workspace / 'activity-extensions.json'
                extensions = json.loads(extension_path.read_bytes())
                extensions['research_requests'] = [{'id': 'domain',
                    'question': 'Which axioms does this exact declaration use?',
                    'source_refs': ['proposal:formal.axioms', 'proposal:lean_code']}]
                extension_path.write_bytes(canonical_json(extensions))
            if role == 'supplemental_research':
                reference = context['review_research']['sources'][0]['ref']
                output.update(summary='Fixed source comparison', used_sources=[reference],
                              answer='The map is complete.', evidence_refs=[reference])
            if role == 'identity_review' and context['action']['stage'] == 'initial' and context['action']['slot'] == 'initial-1':
                output['summary'] = 'PRIVATE-INITIAL-PEER'
            return output

        responder.runner.answer = answer
        with ObservedCalls(package=prepare_role_input) as observed, Returns(prepare_role_input) as returned:
            drive(self, sim, lambda s: bool(responder.resumed_contexts) and
                  any(c['decision'] == 'match' for c in s.runtime['review_cycles'].values()))
        self.assertEqual(len(captured), 1)
        research = captured[0]['review_research']
        self.assertEqual(research['question'], 'Which axioms does this exact declaration use?')
        self.assertEqual([row['ref'] for row in research['sources']], ['proposal:formal.axioms', 'proposal:lean_code'])
        resumed = responder.resumed_contexts[0]
        self.assertTrue(resumed['supplemental_results'])
        self.assertNotIn('PRIVATE-INITIAL-PEER', json.dumps(resumed))
        cycle = sim.runtime['review_cycles'][captured[0]['action']['review_cycle_id']]
        assessment = sim.instance['identity_assessments'][cycle['assessment_id']]
        self.assertEqual(assessment['review_cycle_id'], cycle['id'])
        call = next(r for r in observed.captured('package') if r['role'] == 'supplemental_research')
        execution = next(e for e in sim.runtime['executions'].values() if e['role'] == 'supplemental_research')
        manifest = execution['input_manifest']
        self.assertIsNone(manifest['private_scope'])
        self.assertIn('review_research', manifest['required_direct_keys'])
        self.assertNotIn('task', manifest['required_direct_keys'])
        self.assertEqual(call['context']['review_research']['id'], research['id'])
        packaged = next(r for r in returned.values if r['context']['action']['role'] == 'supplemental_research')
        self.assertIsNone(packaged['overflow'])
        self.assertEqual(execution['outcome'], 'output_accepted')
        self.assertIn(execution['id'], cycle['execution_accounting']['admissions'])


class RoleInputBoundaryTests(unittest.TestCase):
    def test_artifact_candidate_survives_packaging_and_population_stays_fixed(self):
        sim, selected = artifact_scene()
        root, fitted, fixed = issued_plan(sim)
        self.assertEqual(fixed['ready_task_ids'], [selected['id']])
        self.assertEqual(fixed['observed_at'], fixed['submission_contract']['basis_time'])
        self.assertEqual(fitted['manifest']['candidate_order']['ids'], [selected['id']])
        output = {**common('research_plan'), 'dispositions': [task_disposition(selected['id'])]}
        (root / 'activity-extensions.json').write_bytes(canonical_json({'model_assessments': [{
            'task_id': selected['id'], 'difficulty': 'low', 'importance': 'low',
            'reason': 'The selected fixture task has bounded evidence and scope.'}]}))
        seal_response(output, fixed, root)
        draft = root / 'draft.json'
        draft.write_bytes(canonical_json(output))
        check = submission.producer_check(root, draft, clock=sim.ports.clock)
        self.assertTrue(check['passed'], check['issues'])
        later = task(sim.engine, 'TK-later', condition=deepcopy(selected['occurrence_condition']))
        grant(sim.engine, 'GR-later', spec={'kind': 'local', 'roles': ['research_work'],
            'task_ids': [later['id']], 'reuse': 'reusable',
            'expires_at': sim.instance['grants'][selected['authority_refs'][0]]['expires_at']})
        later = sim.runtime['tasks']['TK-later']
        later['authority_refs'] = ['GR-later']
        approve(sim.engine, later)
        sim.runtime['queue'].clear()
        sim.runtime['pending_events'].clear()
        sim.engine._save()
        sim.engine._apply_plan(output, 'EX-plan')
        self.assertEqual([a['target'] for a in sim.runtime['queue']], [selected['id']])
        sim.engine._save()

    def test_selected_candidate_still_requires_current_authority(self):
        sim, selected = artifact_scene()
        _, _, fixed = issued_plan(sim)
        output = {**common('research_plan'), 'dispositions': [task_disposition(selected['id'])]}
        sim.instance['grants'][selected['authority_refs'][0]]['status'] = 'revoked'
        sim.engine._save()
        with self.assertRaisesRegex(ValueError, 'changed|current'):
            sim.engine._validate_decision_acceptance(fixed['action'], output, sim.runtime['executions']['EX-plan'],
                fixed, evaluation_context=sim.engine._evaluation_context())

    def test_delivered_identity_receipt_can_complete_only_its_current_task(self):
        for mutation in (None, 'foreign', 'withdrawn'):
            with self.subTest(mutation=mutation):
                sim = produced_sim()
                clear_work(sim)
                kid, assessment = reviewed_theorem(sim)
                # The old specialist fixture linked the receipt only by task_id;
                # its returned work was not the knowledge producer. Preserve that
                # distinction so changing task_id really makes the receipt foreign.
                selected = task(sim.engine, 'TK-specialist')
                _ended_execution(sim.engine, 'EX-specialist-return', 'research_work')
                selected['results'] = [{'id': 'EV-1', 'execution_id': 'EX-specialist-return'}]
                sim.instance['knowledge'][kid]['task_id'] = selected['id']
                selected['completion_obligations'] = [{'id': 'OB-certification', 'claim': 'The returned proposal is certified',
                    'judges': ['identity_review'], 'evidence_required': []}]
                selected['status'] = 'waiting'
                selected.pop('assessment', None)
                approve(sim.engine, selected)
                sim.engine._save()
                root, _, fixed = issued_plan(sim)
                output = {**common('research_plan'), 'task_assessments': [{'task_id': selected['id'], 'decision': 'completed',
                    'reason': 'Proof returned; the independent receipt certifies this obligation',
                    'item_dispositions': [{'obligation_id': 'OB-certification', 'kind': 'fulfilled',
                                          'evidence_refs': [assessment['id']]}], 'unresolved': []}]}
                seal_response(output, fixed, root)
                draft = root / 'draft.json'
                draft.write_bytes(canonical_json(output))
                check = submission.producer_check(root, draft, clock=sim.ports.clock)
                self.assertTrue(check['passed'], check['issues'])
                if mutation == 'foreign':
                    other = task(sim.engine, 'TK-other')
                    sim.instance['knowledge'][kid]['task_id'] = other['id']
                elif mutation == 'withdrawn':
                    sim.engine.instance = knowledge_records.set_assessment_use(sim.instance, assessment['id'], 'withdrawn', 'recheck', 'reviewer')
                sim.engine._save()
                if mutation:
                    with self.assertRaisesRegex(ValueError, 'evidence|receipt|obligation|current'):
                        sim.engine._apply_plan(output, 'EX-plan')
                else:
                    sim.engine._apply_plan(output, 'EX-plan')
                    self.assertEqual(sim.runtime['tasks'][selected['id']]['status'], 'completed')
                    sim.engine._save()
