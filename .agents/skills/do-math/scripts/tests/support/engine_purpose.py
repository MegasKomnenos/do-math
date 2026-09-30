"""The purpose scenario on a Sim: a scripted research run that proves one natural-number identity.

- ``PurposeResponder(scenario='direct')`` answers the Sim model double's calls
  (``ModelDouble.responder``) as the legacy ``purpose_fixtures.PurposeRunner``
  answered its runner calls: the same answers (``PurposeRunner.answer``) and
  the same activity extensions its ``run`` wrote beside them (preparation:
  model assessments, contract checks, observation rules and revision
  resolutions; plan: model assessments). The model double then binds and seals
  the answer and the worker submits it with the workspace tool. It keeps every
  call's ``(role, action, context)`` in ``calls`` and the runner's
  ``work_order``. Its input checks stay: an action carrying a repair, and every
  check ``PurposeRunner.answer`` makes of its input, fail the call; the failure
  is kept in ``failures`` so ``drive`` fails the test at once instead of the
  flow absorbing it (preserved rule K-32).
- ``purpose_sim(**config)``: a restored copy of the public activation with the
  purpose configuration (``PURPOSE_CONFIG`` updated by ``config``), one
  template per configuration, built once per process. The configured Lean is
  the Sim's synthetic toolchain, so formal checks run the product's
  ``verify_lean`` with the Lean double.
- ``drive(test, sim, predicate=None, limit=45)``: owner passes until
  ``predicate(sim)`` (default: the goal is mathematically solved). The test
  fails at once when the responder failed, and when the instance pauses,
  closes or waits before the predicate holds, with the state summary; also
  when the limit passes (preserved rule K-33).
"""
from __future__ import annotations

from copy import deepcopy
import json

from do_math.canonical import canonical_json
from support.sim import Sim, built

# purpose_fixtures.PurposeHarness.fixture_config without its Lean command, which the Sim's toolchain supplies.
PURPOSE_CONFIG = {'reviewers': 2, 'goal_auditors': 2, 'review_rounds': 2, 'plan_settle_seconds': 1,
                  'max_input_bytes': 2_000_000, 'tool_review_window_seconds': 60,
                  'self_check_response_window_seconds': 5}


def _extensions(workspace):
    path = workspace / 'activity-extensions.json'
    return path, (json.loads(path.read_bytes()) if path.exists() else {})


class PurposeResponder:
    def __init__(self, scenario='direct'):
        from purpose_fixtures import PurposeRunner
        self.runner = PurposeRunner(scenario)
        self.calls, self.failures = [], []

    @property
    def work_order(self):
        return self.runner.work_order

    def respond(self, role, context, workspace):
        action = context['action']
        self.calls.append({'role': role, 'action': deepcopy(action), 'context': deepcopy(context)})
        try:
            if action.get('repair'):
                raise AssertionError('A purpose fixture must not silently adapt to an engine validation failure: '
                                     + str(action['repair'].get('error') or action['repair'].get('issues')))
            output = self.runner.answer(role, context, workspace)
        except AssertionError as error:
            self.failures.append(str(error))
            raise
        self._write_extensions(role, action, context, workspace, output)
        return output

    def _write_extensions(self, role, action, context, workspace, output):
        """The activity extensions ``PurposeRunner.run`` wrote beside its answer, in its order."""
        from research_fixtures import planning_model_assessments, prepared_rule_conditions, supply_observation_rules
        from runner_fixtures import contract_checks
        if role == 'research_preparation' and action.get('revision_targets'):
            path, extensions = _extensions(workspace)
            revised = {candidate.get('revises_task_id') for candidate in output.get('candidates', [])}
            extensions['revision_resolutions'] = [{'record_id': identifier,
                'disposition': 'revised' if identifier in revised else 'deferred',
                'reason': 'The fixture replaces this contract.' if identifier in revised
                else 'The fixture preserves this remaining obligation.'} for identifier in action['revision_targets']]
            path.write_bytes(canonical_json(extensions))
        if role == 'research_preparation':
            path, extensions = _extensions(workspace)
            targets = action.get('assessment_targets')
            identities = ([{'task_id': tid} for tid in targets] if targets else
                          [{'task_title': row['title']} for row in output['candidates']])
            extensions['model_assessments'] = [{**identity, 'difficulty': 'low', 'importance': 'medium',
                'reason': 'The fixture supplies a bounded natural-number identity'} for identity in identities]
            if output['candidates']:
                extensions['contract_checks'] = contract_checks(output['candidates'])
            path.write_bytes(canonical_json(extensions))
        if role == 'research_plan':
            path, extensions = _extensions(workspace)
            extensions['model_assessments'] = planning_model_assessments(output, context)
            path.write_bytes(canonical_json(extensions))
        if role == 'research_preparation' and output.get('candidates'):
            path, extensions = _extensions(workspace)
            supply_observation_rules(output['candidates'], extensions)
            path.write_bytes(canonical_json(extensions))
        if role == 'research_preparation' and action.get('observation_rule_targets'):
            path, extensions = _extensions(workspace)
            extensions['task_conditions'] = prepared_rule_conditions(action['observation_rule_targets'])
            path.write_bytes(canonical_json(extensions))


def purpose_sim(**config):
    """A restored public activation with the purpose configuration; the model double answers as ``PurposeResponder``."""
    settings = {**PURPOSE_CONFIG, **config}

    def build(root, shared):
        sim = Sim(root, shared=shared, config=settings)
        sim.activate()
        return sim
    return built('engine-purpose-' + canonical_json(settings).decode('ascii'), build)


def drive(test, sim, predicate=None, limit=45):
    predicate = predicate or (lambda s: s.instance['goal_status'] == 'mathematically_solved')
    responder = sim.model.responder
    for _ in range(limit):
        sim.step()
        if getattr(responder, 'failures', None):
            test.fail('The purpose responder refused its input: ' + '; '.join(responder.failures))
        if predicate(sim):
            return
        if sim.runtime['status'] in {'paused', 'closed', 'waiting'}:
            test.fail('Workflow stopped before its fixture outcome: ' + json.dumps({
                'status': sim.runtime['status'], 'questions': sim.runtime['questions'], 'queue': sim.runtime['queue'],
                'executions': [{key: row.get(key) for key in ('role', 'outcome', 'error')}
                               for row in sim.runtime['executions'].values()]}, ensure_ascii=False, default=str))
    test.fail('Fixture did not finish within its bounded scenario: ' + json.dumps(sim.waiting(), default=str))
