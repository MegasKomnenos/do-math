"""Records for tests of pure domain functions: governance, task contracts, submissions.

Each function returns new plain records (dicts); none opens a repository or
runs an engine. Records carry explicit synthetic approvals and evidence, never
an actual user decision or model judgment.

Governance
----------
- ``domain_governance()``: instance ``I`` whose charter ``CH1`` (goal "Prove P")
  the user adopted in decision ``D`` from source ``S``
  (``research_fixtures.approved_governance``).
- ``governance_import()``: ``(instance, runtime, source, output)``, an
  interpretation of the public input ``IN`` into one unit ``U`` that asks one
  optional question ``Q``; ``source`` is that input's exact source.
- ``checked_import(kind='charter', handlers=None, payload=None)``:
  ``(instance, runtime, bundle, request)``, that interpretation changed to
  propose ``payload`` (default: charter ``CH2``, goal "Prove Q", superseding
  ``CH1``), independently checked, waiting for the user's later exact approval
  ``request``.
- ``audited_governance()``: ``(instance, runtime)`` with an active additional
  goal audit ``AU`` over ``CH1``.
- ``applied_initial_intent(text)``: ``(instance, runtime, bundle ID)``, a newly
  initialized instance whose original input ``text`` was interpreted, checked
  and applied to its adopted charter.

Task contracts
--------------
- ``task_contract()``: the planned contract ``TK-1`` with obligations ``OB-1``
  (evidence ``EV-1``) and ``OB-2``.
- ``approved_task()``: ``(task, instance, runtime)``, ``task_contract`` as a
  nonformal task of ``domain_governance`` with one source ``SO-1``, one work
  profile and grant, and an approved contract review (``approve_task``).
- ``task_disposition(identifier, kind='selected')``: one plan disposition row.
- ``transfer_assessment()``: ``(instance, runtime, assessment)``, ``approved_task``
  returned with ``EV-1``, a user decision ``DC-1`` transferring ``OB-2`` to
  ``TK-2``, and the plan assessment that closes ``TK-1`` by that transfer;
  ``apply_assessment`` applies an assessment as the plan execution ``EX-plan``.
- ``completed_with_knowledge()``: ``(instance, runtime)`` after a completed
  assessment of ``TK-1`` that cites a candidate theorem ``KN-proof``.
- ``specialist_assessment(judge='identity_review')``: ``transfer_assessment``
  whose single obligation is judged by ``judge`` and a verified theorem
  (``knowledge_fixtures.verified_knowledge``) cited as its evidence.
- ``withdrawable_task()``: ``(instance, runtime, input_tasks)``, an approved
  AI-prepared task ``TK-AI`` with a dependent, a queued review and a waiting
  work action; ``withdraw_prepared`` withdraws it as the plan ``EX-plan``.
- ``installation_repair_state()``: ``(runtime, record)``, a failed plan
  execution held for an accepted installation repair diagnosis.
- ``contract_check(title='one', **changes)``: one preparation self-check row;
  ``preparation_issues(entries, candidates=..., context=preparation_context(), workspace=...)``
  is the receiver's issue list for a preparation output carrying those checks.

Submissions and surfaces
------------------------
- ``execution_state(role='formal_check')``: ``(instance, runtime)`` under the
  stored lifecycle gate with default profiles and one execution ``EX-1`` of
  ``role`` in activity ``AT-1``.
- ``two_observation_output()``: a research_work output with two independent
  observations in two integration bundles; ``observation_knowledge(title)`` is
  one such row and ``research_work_context()`` its fixed input context.
- ``surface_state()``: ``(instance, runtime)``, ``IN-1`` with an adopted
  charter, default profiles and one running research_work execution ``EX-1``;
  ``stored_surface_state()`` is the same under the stored lifecycle gate.
"""
from copy import deepcopy

from do_math import governance as gov, planning
from do_math.repository import exact_content_hash
from research_fixtures import approved_governance, charter, current_state, review_items


def domain_governance():
    return approved_governance({"id": "I"}, [charter()])


def governance_import():
    i = domain_governance(); rt = {"tasks": {}, "executions": {}, "queue": [], "status": "ready",
                                   "inputs": [{"id": "IN", "text": "A choice", "origin": "user"}]}
    s = gov.import_input_source(i, rt, "IN")
    unit = {"unit_id": "U", "source_range": {"start": 0, "end": 8}, "interpretation": "Ask a choice",
            "owner_kind": "charter", "owner_ref": "CH1", "payload": {}, "decision_refs": ["D"], "question_refs": ["Q"]}
    output = {"import_units": [unit], "questions": ["Which scope?"],
              "question_details": [{"id": "Q", "question_index": 0, "target_ids": ["I"], "blocks": False,
                                    "reason": "Optional direction", "options": [{"text": "Keep", "effect": "No change"}],
                                    "source_unit_ids": ["U"]}]}
    return i, rt, s, output


def checked_import(kind='charter', handlers=None, payload=None):
    i, rt, source, output = governance_import()
    replacement = charter('CH2', 'Prove Q'); replacement['supersedes'] = ['CH1']
    payload = payload or {'kind': kind, 'record': replacement}
    output.update(questions=[], question_details=[])
    output['import_units'][0].update(owner_kind=kind, owner_ref=payload.get('record', {}).get('id', 'I'),
                                    payload=payload, question_refs=[])
    bundle = gov.prepare_import(i, rt, source, output, execution_id='E1', input_ref="IN", owner_handlers=handlers)
    rt['executions']['E2'] = {'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
    bundle = gov.check_import(i, rt, bundle['id'], {'bundle_sha256': bundle['sha256'], 'decision': 'approved',
        'scope_complete': True, 'unit_ids': ['U'], 'question_ids': [], 'findings': []}, execution_id='E2',
        owner_handlers=handlers)
    request = {'id': 'LATER', 'action': 'decision', 'origin': 'user', 'text': 'Approve this exact checked change',
        'config': {'kind': 'import_approval', 'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
                   'check_sha256': bundle['check']['sha256'], 'unit_hashes': {'U': exact_content_hash(payload)}}}
    rt['waiting_actions'] = {'CHECK': {'kind': 'import_application_authority', 'import_id': bundle['id'],
                                     'action': {'id': 'CHECK', 'role': 'intent_interpretation', 'stage': 'check'}}}
    return i, rt, bundle, request


def audited_governance():
    i = domain_governance(); rt = {'tasks': {}, 'executions': {}, 'queue': [], 'status': 'ready'}
    audit = {'id': 'AU', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [], 'content': {
        'scope': ['P'], 'required_inputs': ['CH1'], 'assessor': 'goal_audit',
        'verdict_mapping': {'pass': 'satisfied', 'partial': 'not_satisfied', 'unknown': 'unresolved'}}}
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'additional_audit', 'record': audit}, source_ref='S')
    return i, rt


def applied_initial_intent(text):
    import tempfile
    from pathlib import Path
    from do_math.initialization import initialize_state
    instance, runtime = initialize_state(instance_id='RI-case', goal=text, workspace=Path(tempfile.gettempdir()),
                                         config={}, source_input=text)
    records = [charter()]
    instance = approved_governance(instance, records, source=('GS-adoption', text), approval_id='DC-adopt')
    input_id = instance['lifecycle']['input_id']
    source = gov.import_input_source(instance, runtime, input_id)
    output = {'summary': 'Preserve exact original', 'used_sources': [], 'questions': [],
              'question_details': [],
              'import_units': [{'unit_id': 'IU-goal', 'source_range': {'start': 0, 'end': len(text)},
                  'interpretation': text, 'owner_kind': 'charter', 'owner_ref': records[0]['id'],
                  'payload': {}, 'decision_refs': [], 'question_refs': []}]}
    runtime['executions']['EX-author'] = {'id': 'EX-author', 'role': 'intent_interpretation'}
    bundle = gov.prepare_import(instance, runtime, source, output, execution_id='EX-author', input_ref=input_id)
    runtime['executions']['EX-check'] = {'id': 'EX-check', 'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
    gov.check_import(instance, runtime, bundle['id'], {'bundle_sha256': bundle['sha256'],
        'decision': 'approved', 'scope_complete': True, 'unit_ids': ['IU-goal'], 'question_ids': [], 'findings': []},
        execution_id='EX-check')
    instance, runtime, receipt = gov.apply_import(instance, runtime, bundle['id'])
    if receipt['status'] != 'applied' or source['id'] == input_id:
        raise AssertionError('The initial interpretation was not applied from its own input source: ' + repr(receipt))
    return instance, runtime, bundle['id']


def task_contract():
    return {
        "id": "TK-1", "revision": 1, "status": "planned", "question": "What follows?",
        "scope": {"included": ["derive result"], "excluded": ["publish"]},
        "expected": {"outputs": ["proof sketch"], "research_change": "narrow the case"},
        "progress_criteria": [{"id": "PG-1", "claim": "a case is eliminated", "evidence_required": ["EV-1"]}],
        "completion_obligations": [
            {"id": "OB-1", "claim": "provide the proof sketch", "judges": ["task_assessor"], "evidence_required": ["EV-1"]},
            {"id": "OB-2", "claim": "preserve the excluded publication boundary", "judges": ["task_assessor"], "evidence_required": []},
        ],
        "inputs": [], "reuse": [], "dependencies": [], "occurrence_condition": {"op": "always"},
        "profile_refs": [{"id":"PF-1", "revision":1, "sha256":"a"*64}], "authority_refs": ["GR-1"], "basis_refs": ["KN-1"],
    }


def approved_task():
    from do_math.configuration import DEFAULT_CONFIG
    config={**deepcopy(DEFAULT_CONFIG), 'tier_models':{tier:'fixture-model' for tier in ('low','medium','high')},
            'session_limits':{'work':{'fixture-model':3}}}
    from do_math.execution_profiles import seal_profile, profile_ref, BOUNDARY
    from do_math.observations import observation_rule_contract
    # A work role's AI profile reserves the model's work slot.
    capacity = 'CP-' + exact_content_hash({'model':'fixture-model','work':3})
    profile = seal_profile({'role':'research_work','actor_kind':'ai',
        'ai':{'model':'fixture-model','tier':'high','effort':'high','capacity_refs':[capacity]},'boundary':BOUNDARY,
        'observation':{'mode':'event_driven','rule_bindings':observation_rule_contract()}})
    value = task_contract()
    value.update(work_class='nonformal', basis_refs=['SO-1'], profile_refs=[profile_ref(profile)],
                 inputs=['SO-1'], results=[], producer_execution='EX-author')
    instance = {**domain_governance(), 'id':'IN-1',
        'sources':[{'id':'SO-1','name':'source','path':'source.txt','sha256':'a'*64}],
        'execution_profiles':{profile['id']:profile}, 'config':config,
        'grants':{'GR-1':{'id':'GR-1','kind':'local','status':'active','actor':'ai','roles':['research_work'],
                        'task_ids':[value['id']],'reuse':'reusable','valid_from':None,'expires_at':None}}}
    runtime = {'status':'active','tasks':{value['id']:value},'queue':[], 'executions':{},'history':[],'question_links':[]}
    approve_task(value,instance,runtime)
    return value,instance,runtime


def approve_task(value, instance, runtime):
    output = review_items(['SO-1'])
    value['reviews'] = [planning.seal_contract_review(value,output,instance,runtime,execution_id='EX-review')]


def task_disposition(identifier, kind='selected'):
    return {'task_id':identifier,'kind':kind,'reason':'bounded next step','uncertainty':'remaining proof work',
        'parallel_task_ids':[],'expected_research_change':'prove the lemma',
        'revisit':{'event_refs':['EV-next'],'at':None},'missing_inputs':['SO-missing'] if kind=='not_assessable' else [],
        'next_owner':'research_work' if kind=='selected' else 'research_plan'}


def transfer_assessment():
    t,i,r=approved_task()
    for obligation in t['completion_obligations']: obligation['judges']=['research_plan']
    t.update(status='waiting',results=[{'id':'EV-1','execution_id':'EX-work'}])
    target=deepcopy(t);target.update(id='TK-2',results=[],status='planned',reviews=[])
    r['tasks']['TK-2']=target
    r['executions']['EX-plan']={'id':'EX-plan','role':'research_plan','status':'ended'}
    i['decisions']={'DC-1':{'id':'DC-1','actor':'user','source_ref':'SO-1','source_sha256':'a'*64,
        'change':{'kind':'task_scope','task_id':'TK-1','disposition':'transfer','revision':1,
            'contract_sha256':planning.contract_hash(t),'obligation_ids':['OB-2'],'target_task_id':'TK-2'}}}
    assessment={'task_id':'TK-1','decision':'closed','reason':'Proof returned; boundary obligation transferred',
        'item_dispositions':[{'obligation_id':'OB-1','kind':'fulfilled','evidence_refs':['EV-1']},
            {'obligation_id':'OB-2','kind':'transferred','evidence_refs':[],'authority_ref':'DC-1',
             'target_task_id':'TK-2','target_obligation_id':'OB-inherited'}], 'unresolved':[]}
    return i,r,assessment


def apply_assessment(i,r,a):
    from do_math.task_scope import apply_task_assessments
    return apply_task_assessments(i,r,[a],execution_id='EX-plan',input_tasks=deepcopy(r['tasks']))


def completed_with_knowledge():
    instance, runtime, assessment = transfer_assessment()
    assessment['decision'] = 'completed'
    assessment['item_dispositions'] = [
        {'obligation_id': row['id'], 'kind': 'fulfilled', 'evidence_refs': ['KN-proof', *row['evidence_required']]}
        for row in runtime['tasks']['TK-1']['completion_obligations']]
    instance['knowledge'] = {'KN-proof': {'id': 'KN-proof', 'revision': 1, 'lifecycle': 'active',
        'kind': 'theorem', 'formal_result_id': 'FR-proof', 'exposition_id': 'XP-proof',
        'dependencies': [], 'source_basis': []}}
    instance['formal_results'] = {'FR-proof': {'id': 'FR-proof', 'lean_code': 'exact source',
        'declaration_names': ['proof'], 'publication_state': 'candidate', 'formal_use': 'suspended'}}
    instance['expositions'] = {'XP-proof': {'id': 'XP-proof', 'items': [{'id': 'summary', 'text': 'exact argument'}]}}
    instance['identity_assessments'] = {}
    instance['assessment_uses'] = {}
    return apply_assessment(instance, runtime, assessment)


def specialist_assessment(judge='identity_review'):
    from knowledge_fixtures import verified_knowledge
    instance, runtime, assessment = transfer_assessment()
    state, _, kid, aid = verified_knowledge()
    instance.update(state)
    instance['knowledge'][kid]['task_id'] = 'TK-1'
    task = runtime['tasks']['TK-1']
    task['completion_obligations'] = [{'id':'OB-certification', 'claim':'The returned proposal is certified',
        'judges':[judge], 'evidence_required':[]}]
    ref = aid if judge == 'identity_review' else instance['knowledge'][kid]['formal_result_id']
    assessment.update(decision='completed', item_dispositions=[{'obligation_id':'OB-certification',
        'kind':'fulfilled', 'evidence_refs':[ref]}], unresolved=[])
    return instance, runtime, assessment, kid, aid


def withdrawable_task():
    task = {**task_contract(),"id": "TK-AI", "title": "AI proposal", "revision": 3, "status": "planned",
            "producer_execution": "EX-prep",
            "results": [], "reviews": [{"decision": "approved"}], "dependencies": []}
    runtime = {"tasks": {task["id"]: deepcopy(task), "TK-dependent": {
        "id": "TK-dependent", "status": "waiting", "dependencies": [task["id"]]}},
        "executions": {"EX-prep": {"id": "EX-prep", "role": "research_preparation", "status": "ended",
                                       "action": {"role": "research_preparation"}}},
        "queue": [{"id": "AC-review", "role": "task_contract_review", "target": task["id"]},
                  {"id": "AC-other", "role": "research_plan"}],
        "waiting_actions": {"AC-work": {"action": {"id": "AC-work", "role": "research_work", "target": task["id"]}}},
        "history": []}
    return {}, runtime, {task["id"]: deepcopy(task)}


def withdraw_prepared(runtime, snapshot):
    from do_math.task_scope import apply_task_dispositions
    return apply_task_dispositions({}, runtime, [{"task_id": "TK-AI", "disposition": "withdraw",
        "reason": "The prepared task is superseded by a narrower current direction."}],
        execution_id="EX-plan", input_tasks=snapshot)


def installation_repair_state():
    from do_math import activities
    at = '2026-09-22T00:00:00+00:00'
    runtime = {'queue':[], 'executions':{}, 'activities':{}, 'waiting_actions':{}, 'status':'ready'}
    activities.open_activity(runtime, activity_id='AY-work', activity_kind='research_plan',
                             owner_ref='AC-work', input_refs=[], opened_at=at)
    target = {'id':'EX-failed','role':'research_plan','status':'ended','error':'receiver contract conflict',
        'action':{'id':'AC-work','role':'research_plan','owner_activity_id':'AY-work'},
        'owner_activity_id':'AY-work', 'result_ref':'runtime/artifacts/failure/result.json'}
    runtime['executions']['EX-failed'] = target
    runtime['activities']['AY-work'].update(assigned_execution_ids=['EX-failed'],status='waiting',
        waiting={'condition':{'error':'receiver'},'reason':'receiver','next_owner':'operations','at':at})
    runtime['executions']['EX-diagnosis'] = {'id':'EX-diagnosis','role':'operational_review',
        'status':'ended','outcome':'output_accepted','action':{'target':'EX-failed'}}
    record = {'id':'OD-repair','execution_id':'EX-diagnosis','target_execution_id':'EX-failed',
        'status':'installation_repair_pending','disposition':{'kind':'repair',
            'repair_target':'installation:scripts/do_math/task_scope.py','meaning_preserving':True,
            'verification':'Reproduce the receiver conflict and verify completion without weakening evidence',
            'basis_refs':['EX-failed'],'reason':'Receiver contradicts the granted contract','next_owner':'installation_recovery'},
        'result':{'installation_repair':{'installation_sha256':'a'*64,
            'evidence_refs':['runtime/artifacts/failure/result.json']}}}
    runtime['operational_dispositions'] = {record['id']:record}
    runtime['waiting_actions']['AC-work'] = {'action':{**target['action'],'repair_attempt':2,
        'repair':{'execution_id':'EX-failed','issues':[{'message':'actual error'}]}},
        'execution_id':'EX-failed','kind':'output_validation','reason':'failed again'}
    return runtime, record


def contract_check(title="one", **changes):
    return {"task_title": title, "symbols": [], "sibling_boundaries": [],
            "outcome_branches": [{"outcome": "The identity holds on the given inputs", "completion": "Report the check"},
                                 {"outcome": "A given input contradicts the identity", "completion": "Report the contradicting input"}],
            **changes}


def preparation_context():
    """The fixed input of a preparation that assesses models (``budget_unit`` concurrent_sessions)."""
    return {"action": {"id": "AC-this", "role": "research_preparation"}, "budget_unit": "concurrent_sessions",
            "tasks": [], "knowledge_catalog": [], "kind_definitions": {}, "sources": []}


def preparation_issues(entries, *, candidates, context, workspace, conditions=None):
    """The receiver's issues, as JSON text, for a preparation output proposing ``candidates``.

    The extensions carry one model assessment per candidate, the self-checks
    ``entries``, the task ``conditions`` and the fixture's observation rules
    (``research_fixtures.supply_observation_rules``, read at call time, which
    adds its rows to ``conditions`` itself); one integration bundle holds them all.
    """
    import json
    from do_math.contracts import schema_for
    from do_math.submission import payload_issues
    from research_fixtures import supply_observation_rules
    from runner_fixtures import common, rating
    output = {**common("research_preparation"), "candidates": candidates}
    extensions = {"model_assessments": [rating(task_title=c['title']) for c in output['candidates']], "contract_checks": list(entries)}
    if conditions:
        extensions["task_conditions"] = conditions
    supply_observation_rules(output['candidates'], extensions)
    output["integration_bundles"] = [{"integration_id": "IN-check", "members": ["output", *[
        f"activity-extensions.json/{family}/{i}" for family, rows in extensions.items() for i, _ in enumerate(rows)]],
        "impact_set": [], "authority_refs": []}]
    return json.dumps(payload_issues(output, schema_for("research_preparation"), context, extensions, workspace),
                      ensure_ascii=False)


def execution_state(role="formal_check"):
    """``(instance, runtime)`` under the lifecycle gate: default profiles and one execution ``EX-1`` of ``role`` in activity ``AT-1``."""
    from do_math.configuration import DEFAULT_CONFIG
    from do_math.execution_profiles import build_profiles, profile_ref
    from do_math.activities import open_activity, assign_execution
    from do_math.execution_lifecycle import create_execution
    instance, runtime = current_state({"config": deepcopy(DEFAULT_CONFIG), **build_profiles(DEFAULT_CONFIG)},
                                      {"executions": {}})
    profile = next(p for p in instance["execution_profiles"].values() if p["role"] == role)
    open_activity(runtime, activity_id="AT-1", activity_kind="formal_check", owner_ref="engine", input_refs=[], opened_at="2026-09-20T00:00:00Z")
    execution = create_execution(execution_id="EX-1", owner_activity_id="AT-1", actor_kind=profile["actor_kind"], input_manifest={}, profile_ref=profile_ref(profile), created_at="2026-09-20T00:00:00Z")
    execution["role"] = role
    assign_execution(runtime, "AT-1", execution)
    return instance, runtime


def two_observation_output():
    return dict(summary="two observations", used_sources=[], questions=[], outcome="submitted",
                report="independent observations", knowledge=[observation_knowledge("A"), observation_knowledge("B")],
                relations=[], remaining_work=[], checkpoint="", integration_bundles=[
                    dict(integration_id="IN-A", members=["output", "output/knowledge/0"], impact_set=[], authority_refs=[]),
                    dict(integration_id="IN-B", members=["output/knowledge/1"], impact_set=[], authority_refs=[])])


def observation_knowledge(title):
    return dict(kind="observation", title=title, statement=title, explanation=title,
                summary=title, lean_code="", declaration_names=[], dependencies=[])


def research_work_context():
    return dict(action=dict(role="research_work", target="TK-1"), snapshot="fixed",
                kind_definitions={"knowledge": [{"token": "observation"}], "relations": []},
                knowledge_catalog=[], tasks=[], sources=[], grants=[])


def surface_state():
    from do_math import execution_profiles, activities, execution_lifecycle
    from do_math.configuration import DEFAULT_CONFIG
    instance = approved_governance({'id': 'IN-1'}, [charter('CH-1', evidence_boundary='Proof')],
                                   source=('GS-1', 'User approves P'), approval_id='DC-1')
    instance.update(config=deepcopy(DEFAULT_CONFIG), knowledge={}, formal_results={}, expositions={},
                    identity_assessments={}, assessment_uses={}, sources=[], trust_environments={})
    instance.update(execution_profiles.build_profiles(instance['config']))
    runtime = {'status': 'active', 'tasks': {}, 'activities': {}, 'executions': {},
               'queue': [], 'history': [], 'question_links': [], 'reservations': {}, 'waiting_actions': {}}
    activities.open_activity(runtime, activity_id='AC-1', activity_kind='research', owner_ref='IN-1',
                             input_refs=[], opened_at='2026-09-20T00:00:00Z')
    profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
    execution = execution_lifecycle.create_execution(execution_id='EX-1', owner_activity_id='AC-1', actor_kind='ai',
        input_manifest=[], profile_ref=execution_profiles.profile_ref(profile), created_at='2026-09-20T00:00:00Z')
    execution['role'] = 'research_work'
    activities.assign_execution(runtime, 'AC-1', execution)
    return instance, runtime


def stored_surface_state():
    """surface_state under the current lifecycle gate, as every stored state is."""
    instance, runtime = surface_state()
    del runtime['status']
    return current_state(instance, runtime)
