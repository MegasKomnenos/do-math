"""Actual worker/QU scenes for the intent evidence consumer and storage corpus."""
from do_math.canonical import canonical_json
from support.default_responder import DefaultResponder, common
from support.engine_lifecycle import applied, clear_work
from support.model import ModelDouble
from support.sim import Sim, built


def evidence_waits(sim):
    return [w for w in sim.runtime.get('waiting_actions', {}).values() if w.get('kind') == 'import_check_evidence']


def evidence_bundle(sim):
    wait, = evidence_waits(sim)
    return sim.runtime['intent_imports'][wait['import_id']]


def _build_initial_waiting(root, shared):
    sim = Sim(root, shared=shared)
    sim.model = ModelDouble(sim.clock, EvidenceResponder())
    try:
        sim.activate()
    except AssertionError as error:
        if (not str(error).startswith('public activation did not reach active: ')
                or sim.instance['lifecycle']['state'] != 'initializing' or not evidence_waits(sim)):
            raise
    else:
        raise AssertionError('the missing evidence must leave initialization waiting')
    return sim


def initial_waiting_sim(root=None):
    sim = (_build_initial_waiting(root, root) if root is not None
           else built('intent-initial-evidence', _build_initial_waiting))
    sim.model = ModelDouble(sim.clock, EvidenceResponder())
    return sim


def authorize_initial_evidence(sim):
    from datetime import timedelta
    applied(sim, 'decision', text='Authorize the initial evidence inspection', config={'change': {'kind': 'grant',
        'grant': {'id': 'GR-evidence-initial', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable',
                  'expires_at': (sim.clock.wall() + timedelta(days=1)).isoformat()}}})
    applied(sim, 'decision', text='Adopt the initial inspection grant', config={'change': {'kind': 'initialization',
        'initial_grant_ids': ['GR-initial-sim', 'GR-evidence-initial']}})


class EvidenceResponder(DefaultResponder):
    def __init__(self, *, repeat=False, evidence_ref=None):
        super().__init__()
        self.repeat = repeat
        self.evidence_ref = evidence_ref

    def respond(self, role, context, workspace):
        action = context['action']
        output = super().respond(role, context, workspace)
        if role == 'intent_interpretation' and action.get('stage') == 'check':
            if not action.get('import_check_release') or self.repeat:
                output.update(decision='unresolved', findings=['Required source evidence is unavailable'],
                              questions=['Recover the required interpretation evidence'])
                if self.evidence_ref:
                    output['used_sources'] = ['context:goal', self.evidence_ref]
                existing = next((q for q in context['question_links'] if q.get('obligation', {}).get('requirement_ref') == 'intent-evidence'), None)
                route = {'question_index': 0, 'owner': 'operations', 'target_ids': [context['instance_id']],
                    'reason': 'Recover evidence for this preserved input', 'blocks': False,
                    'obligation': {'kind': 'input_retrieval', 'subject_ref': context['instance_id'],
                                   'requirement_ref': 'intent-evidence'}}
                if existing:
                    route['existing_question_id'] = existing['id']
                (workspace / 'activity-extensions.json').write_bytes(canonical_json({'question_routes': [route]}))
        elif role == 'maintenance' and action.get('question_ids'):
            question, = context['operations_questions']
            (workspace / 'source-check.txt').write_bytes(b'Inspected the original and the required source.\n')
            output = {**common(role), 'report': 'The required interpretation evidence was recovered', 'remaining_work': []}
            (workspace / 'activity-extensions.json').write_bytes(canonical_json({'question_resolutions': [{
                'question_id': question['id'], 'generation': question['assigned_generation'],
                'affected_ids': question['assigned_target_ids'], 'disposition': 'resolved',
                'evidence_refs': ['workspace:source-check.txt'], 'reason': 'The actual source was inspected'}]}))
        return output


def waiting_sim(*, repeat=False, evidence_ref=None):
    sim = Sim.activated()
    clear_work(sim)
    if evidence_ref:
        path = sim.root / evidence_ref.removeprefix('source:')
        path.write_bytes(b'Initial interpretation evidence.\n')
        applied(sim, 'source', config={'path': str(path)})
    sim.model = ModelDouble(sim.clock, EvidenceResponder(repeat=repeat, evidence_ref=evidence_ref))
    applied(sim, 'input', text='Preserve the exact purpose and original.', request_id='intent-evidence-input')
    sim.run_until(lambda s: bool(evidence_waits(s)) and all(e['status'] == 'ended'
        for e in s.runtime['executions'].values()), max_steps=4)
    return sim
