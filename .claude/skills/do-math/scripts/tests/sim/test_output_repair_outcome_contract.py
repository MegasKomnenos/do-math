"""4-C: actual bundle receivers decide which returns consume output repair."""
from copy import deepcopy
import re
import unittest

from do_math import integration, submission
from do_math.input_basis import capture_decision_basis
from support.review_sim import held_impact, impact_sim
from support.submission_receiver import history, research
from support.submission_scenes import withhold_publication, release_publication
from support.sim import warm_template

setUpModule = warm_template


def returned_case(kind):
    if kind == 'impact_review':
        sim = impact_sim()
        _, producer, _, _ = held_impact(sim)
        return sim.engine, producer['action'], producer['id'], deepcopy(producer['integration_result']), {}
    scene = research() if kind in {'partial_rejection', 'premises_changed'} else history()
    engine = scene.engine
    if kind == 'partial_rejection':
        scene.output['integration_bundles'][0]['members'].remove('output')
        scene.output['integration_bundles'][1]['members'].append('output')
        scene.output['knowledge'][1]['dependencies'] = ['KN-not-supplied']
    if kind == 'premises_changed':
        execution = engine.runtime['executions'][scene.execution_id]
        execution['decision_basis'] = capture_decision_basis(engine.instance, engine.runtime, [scene.task['id']])
        engine.runtime['tasks'][scene.task['id']]['question'] += ' Changed after the issued input.'
        engine._save()
    if kind == 'output_rejected':
        scene.output['summary'] = []
    issues = submission.payload_issues(scene.output, scene.schema, scene.context, {}, scene.workspace,
        clock=engine.ports.clock)
    if kind == 'publication_wait':
        withhold_publication(scene.sim, scene.execution_id)
    try:
        received = engine._apply_submission_bundles(scene.action, scene.output, {}, scene.execution_id,
                                                  scene.context, issues)
    finally:
        if kind == 'publication_wait':
            release_publication(scene.sim)
    return engine, scene.action, scene.execution_id, received, scene.output


class OutputRepairOutcomeContractTests(unittest.TestCase):
    def test_every_submission_disposition_counts_only_declared_producer_repairs(self):
        exercised = set()
        for kind in (*integration.SUBMISSION_OUTCOMES, 'partial_rejection'):
            with self.subTest(kind=kind):
                engine, action, identifier, received, output = returned_case(kind)
                expected = 'output_rejected' if kind == 'partial_rejection' else kind
                self.assertEqual(integration.submission_outcome(received), expected)
                exercised.add(expected)
                if kind == 'partial_rejection':
                    self.assertEqual(received['status'], 'partial')
                    self.assertEqual([row['status'] for row in received['bundles']], ['accepted', 'returned'])
                before = deepcopy((engine.instance, engine.runtime))
                engine.route_submission_return(action, received, identifier, output)
                if integration.SUBMISSION_OUTCOMES[expected]['output_repair']:
                    retry = engine.runtime['queue'][-1]
                    self.assertEqual(retry['repair_attempt'], action.get('repair_attempt', 0) + 1)
                    self.assertEqual(retry['repair']['retry_bundle_ids'], received['retry_bundle_ids'])
                    self.assertEqual(retry['repair']['issues'], received['issues'])
                else:
                    self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(exercised, set(integration.SUBMISSION_OUTCOMES))

    def test_unregistered_receipt_status_cannot_consume_a_repair(self):
        scene = history()
        for status in ('unknown-status', None, [], True):
            received = {'status': status, 'bundles': [], 'issues': [], 'retry_bundle_ids': []}
            before = deepcopy((scene.engine.instance, scene.engine.runtime))
            with self.subTest(status=status), self.assertRaisesRegex(ValueError,
                    '^' + re.escape('unknown integration receipt status: ' + repr(status)) + '$'):
                scene.engine.route_submission_return(scene.action, received, scene.execution_id, scene.output)
            self.assertEqual((scene.engine.instance, scene.engine.runtime), before)
