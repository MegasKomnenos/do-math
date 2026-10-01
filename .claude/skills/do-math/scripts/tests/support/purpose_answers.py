"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from copy import deepcopy
from do_math.canonical import canonical_json
from support.role_answers import assessment, contract_review, disposition, intent_response, read_fixture_context, scope_response, candidate as v5_candidate


SOURCE = 'theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n'


STATEMENT = 'For every natural number n, n + 0 = n.'


EXPLANATION = 'The variable n ranges over Nat. The proof applies Nat.add_zero to that n.'


GOAL = 'Establish that adding zero to any natural number leaves it unchanged.'


NEW_GOAL = 'Establish the same zero-addition identity with the natural-number domain explicit.'


def parse_context(prompt, workspace):
    return read_fixture_context(prompt, workspace)


def common(summary):
    return {'summary': summary, 'used_sources': [], 'questions': []}


def candidate(title, *, formal=True, revises=None, refs=None):
    return v5_candidate(title, formal=formal, revises=revises, refs=refs)


def theorem():
    return {'kind': 'theorem', 'title': 'Natural zero identity', 'statement': STATEMENT,
            'explanation': EXPLANATION, 'summary': 'Addition of zero preserves each natural number.',
            'lean_code': SOURCE, 'declaration_names': ['add_zero_fixture'], 'dependencies': []}


class PurposeAnswers:
    def __init__(self, scenario='direct', *, observation=None, pause_sender=None):
        self.scenario, self.observation, self.pause_sender = scenario, observation, pause_sender
        self.calls = []
        self.work_order = []
        self.preparations = 0
        self.currentness_prepared = False
        self.observed_workers = 0
        self.returned = []

    def answer(self, role, context, workspace):
        action = context['action']
        if role == 'research_preparation':
            if 'assessment_targets' in action or 'observation_rule_targets' in action:
                return {**common('Assess only the supplied contracts'), 'candidates': []}
            self.preparations += 1
            tasks = context.get('tasks', [])
            if self.scenario == 'dependency' and not tasks and not any(
                    k['title'] == 'Natural zero identity' for k in context.get('knowledge_catalog', [])):
                (workspace / 'activity-extensions.json').write_bytes(canonical_json({'task_conditions': [{
                    'task_title': 'A', 'occurrence_condition': {'op': 'task_disposition_is', 'task_id': 'B', 'value': 'completed'},
                    'dependencies': ['B']}]}))
                return {**common('Prepare B before A; the extension fixes the dependency'), 'candidates': [candidate('A'), candidate('B', formal=False)]}
            revision_targets = set(action.get('revision_targets', {}))
            if revision_targets:
                revisable = next((t for t in tasks if t['id'] in revision_targets), None)
                if revisable is None:
                    raise AssertionError('The preparation fixture did not receive its declared revision target')
                return {**common('Revise only the contract declared before this execution'),
                        'candidates': [candidate('A', revises=revisable['id'])]}
            if self.scenario == 'currentness' and any(k['title'] == 'Natural zero identity' and k['usable_as_k']
                                                      for k in context.get('knowledge_catalog', [])):
                source = next(k['id'] for k in context['knowledge_catalog']
                              if k['title'] == 'Natural zero identity' and k['usable_as_k'])
                self.currentness_prepared = True
                return {**common('Prepare a task that explicitly consumes the certified result'),
                        'candidates': [candidate('Dependent', formal=False, refs=[source])]}
            if tasks or any(k['title'] == 'Natural zero identity' for k in context.get('knowledge_catalog', [])):
                return {**common('Preserve existing contracts and supplied results when no revision target was declared'), 'candidates': []}
            return {**common('Prepare the exact natural-number identity'), 'candidates': [candidate('A')]}
        if role == 'task_contract_review':
            return {**common('Inspect the actual scope, obligations and evidence'), **contract_review(context)}
        if role == 'research_plan':
            tasks = context.get('tasks', [])
            ready = context['ready_task_ids']
            from do_math.task_contracts import returned_task_ids
            returned = set(returned_task_ids({t['id']: t for t in tasks}))
            assessments = [assessment(t) for t in tasks if t['id'] in returned]
            finished = all(t['status'] == 'completed' or t['id'] in returned for t in tasks)
            catalog = context.get('knowledge_catalog', [])
            certified = any(k['title'] == 'Natural zero identity' and k['usable_as_k'] for k in catalog)
            preparations = []
            if self.scenario == 'currentness' and not self.currentness_prepared and finished and certified:
                preparations = ['Prepare an explicit downstream task that uses Natural zero identity']
                finished = False
            return {**common('Select only enabled tasks and assess actual returned reports'), 'dispositions': [disposition(tid) for tid in ready],
                    'preparation_requests': preparations, 'goal_audit': finished and certified,
                    'task_assessments': assessments}
        if role == 'research_work':
            task = context['task']
            title = task['title']
            self.work_order.append(title)
            if self.scenario == 'dependency' and title == 'A':
                prerequisite = next(t for t in context['tasks'] if t['title'] == 'B')
                if prerequisite['status'] != 'completed': raise AssertionError('A started before B was assessed complete')
            if title == 'B':
                knowledge = [{'kind': 'observation', 'title': 'Domain note', 'statement': 'The domain is the natural numbers.',
                    'explanation': 'This note fixes the declared domain; it does not claim a formal theorem.',
                    'summary': 'Natural-number domain recorded.', 'lean_code': '', 'declaration_names': [], 'dependencies': []}]
            elif title == 'Dependent':
                knowledge = []
            else:
                knowledge = [theorem()]
            return {**common('The report fixes n : Nat and applies Nat.add_zero'),
                'used_sources': task.get('reuse', []), 'outcome': 'submitted',
                'report': EXPLANATION + ('\nAppendix records the same fixed Nat domain.' * 6000 if self.scenario == 'catalog' else ''),
                'knowledge': knowledge, 'relations': [], 'remaining_work': [], 'checkpoint': 'Argument and domain are explicit'}
        if role == 'identity_review':
            if action['stage'] == 'scope':
                return {**common('Inspect the full supplied proposal and assign independent perspectives'), **scope_response(context)}
            review = context['role_review']
            base = {**common('Compare the exact Nat statement, explanation and proof'), 'proposal_digest': review['proposal_digest'],
                    'used_sources': ['proposal:statement', 'proposal:explanation', 'proposal:lean_code']}
            stage = action['stage']
            if stage == 'initial':
                if self.scenario == 'dispute' and action['slot'] == 'initial-0':
                    return {**base, 'decision': 'mismatch', 'scope_complete': True,
                        'findings': [{'id': 'domain-objection', 'statement': 'The explanation might quantify over real numbers, unlike Nat in Lean.',
                                      'evidence': ['proposal:explanation']} ]}
                return {**base, 'decision': 'match', 'scope_complete': True, 'findings': []}
            if stage == 'organize':
                source = review['pending_findings'][0]['ref']
                return {**base, 'issues': [{'id': 'domain-issue', 'finding_refs': [source], 'answer_role_slot_id': 'initial-0'}]}
            if stage == 'answer':
                return {**base, 'answers': [{'issue_id': 'domain-issue', 'disposition': 'withdraw',
                    'statement': 'I withdraw the objection: the supplied explanation explicitly says that n ranges over Nat.',
                    'evidence': ['proposal:explanation']}], 'new_findings': []}
            return {**base, 'decision': 'match', 'scope_complete': True, 'new_findings': [],
                'issue_verdicts': [{'issue_id': 'domain-issue', 'decision': 'rejected',
                    'reason': 'The explanation explicitly fixes n : Nat, exactly as the Lean declaration does.',
                    'evidence': ['proposal:explanation', 'proposal:lean_code']}]}
        if role == 'goal_audit':
            eligible = context.get('eligible_knowledge', [])
            if not eligible: raise AssertionError('Goal audit was scheduled before effective formal evidence existed')
            if not all(item['links'] and all(a['decision'] == 'match' for a in item['identity_assessments']) for item in eligible):
                raise AssertionError('Goal audit did not receive the effective final identity assessment')
            return {**common('The certified Nat zero-addition theorem meets the exact requested identity'),
                    'used_sources': [k['id'] for k in eligible], 'decision': 'satisfied', 'scope_complete': True,
                    'additional_audits': [],
                    'reason': 'The requested domain and equality coincide with the reviewed theorem.'}
        if role == 'intent_interpretation':
            output = intent_response(context)
            if action.get('stage', 'interpret') == 'interpret' and context['user_request']['text'] == NEW_GOAL:
                current = context['governance']['charter']
                record = {'id': 'CH-proposed-new-goal', 'kind': 'charter', 'revision': current['revision'] + 1,
                    'supersedes': [current['id']], 'content': {**deepcopy(current['content']),
                        'goal': NEW_GOAL, 'success_criteria': [NEW_GOAL], 'included_scope': [NEW_GOAL]}}
                output['import_units'][0].update(owner_ref=record['id'], payload={'kind': 'charter', 'record': record})
            return output
        if role == 'operational_review':
            if not action.get('live'): raise AssertionError('Unexpected execution failure triggered a non-live operational review')
            proposal = {'kind': 'continue', 'basis_refs': [action['target']], 'next_owner': 'research_work',
                'reason': 'The visible checkpoint contains the fixture argument', 'next_review': None}
            if self.observation == 'stop':
                proposal = {'kind': 'retry', 'basis_refs': [action['target']], 'next_owner': 'research_work',
                    'reason': 'Preserve the partial argument before retrying the missing report',
                    'scope': 'Complete the report using the preserved checkpoint and current input',
                    'replay_safety': 'This attempt has published no theorem or external effect'}
            return {**common('A checkpoint and a visible observation are available'), 'disposition': proposal}
        raise AssertionError('Unexpected fixture role: ' + role)


SOLVED_REQUIREMENT_CRITERIA = ["draft account", "cite reviewed equality"]


def requirement(criteria: list[str], *, required_inputs=None, external_effects=None) -> dict:
    return {
        "id": "writeup",
        "scope": "A reader-facing account of the solved natural-number theorem.",
        "criteria": criteria,
        "assessor": "research_plan",
        "required_inputs": required_inputs or [],
        "external_effects": external_effects or [],
    }


class AcademicAnswers(PurposeAnswers):
    def __init__(self, *args, effect_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.effect_request = effect_request

    def answer(self, role, context, workspace):
        action = context["action"]
        if role == "research_plan" and action.get("rejection_id"):
            (workspace / "activity-extensions.json").write_bytes(canonical_json({
                "academic_resolutions": [{
                    "id": action["rejection_id"], "decision": "resolved",
                    "evidence": "The planner compared the preserved objection with the completed reviewed task report.",
                    "evidence_refs": [row['id'] for row in context['knowledge_catalog'] if row.get('usable_as_k')],
                }],
            }))
        if role == "research_work" and context["task"].get("academic_requirement_id"):
            task = context["task"]
            effects = task.get("required_external_effects", [])
            if effects and self.effect_request:
                (workspace / "activity-extensions.json").write_bytes(canonical_json({"external_requests": [{
                    "id": "academic-effect", "academic_effect_id": effects[0]["id"],
                    "grant_id": effects[0].get("grant_id") or self.effect_request["grant_id"],
                    "purpose": effects[0]["scope"], "request": deepcopy(self.effect_request["request"]),
                }]}))
            self.work_order.append(task["title"])
            return {
                "summary": "The academic criterion is addressed by the submitted reader-facing account.",
                "used_sources": task.get("reuse", []), "questions": [], "outcome": "submitted",
                "report": "The report explains the exact natural-number domain and the reviewed equality.",
                "knowledge": [], "relations": [], "remaining_work": [],
                "checkpoint": "The required account and its evidence are ready for independent assessment.",
            }
        return super().answer(role, context, workspace)
