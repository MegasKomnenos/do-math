"""Engine doubles and the engine start states tests share.

Two kinds of engine appear here. Both are the product ``ResearchEngine``:

- In-memory engines hold supplied state and publish nothing to Git.
  ``FakeEngine(root, config=None)`` is an initialized instance ``RI-test`` over
  the ``StateStore`` double whose ``_save`` records copies in ``saves``; it
  grants, registers synthetic trust environments, activates through the
  adoption decision (``activate``), creates knowledge and approved tasks, and
  processes one queued machine action (``machine``). ``approve_contract`` and
  ``formal_verification`` are its contract review and compiler double for
  records outside it; ``formal_check_engine(test)`` is one with a candidate and
  its queued formal check. ``routing_engine()`` is a bare engine with an empty
  active-looking instance for response routing; ``intent_import`` and
  ``intent_verdict`` author and check one interpretation on it.
  ``context_engine(instance=None, runtime=None)`` keeps the real role-context
  producer over ``record_fixtures.surface_state``; ``package`` prepares one
  role input with it. ``initial_failure_engine`` holds a failed initial
  interpretation waiting for maintenance. ``reassessment_engine`` holds a task
  waiting for a missing input. ``governance_host`` and ``goal_audit_host`` hold
  checked governance changes. ``evidence_engine`` is an active instance whose
  store is ``input_snapshot_store``; ``reviewed_task``, ``apply_plan``,
  ``accept_knowledge`` and ``audit_goal`` drive it.
- Git-backed start states give a ``unittest.TestCase`` its attributes.
  ``start_submission_history(test)`` puts a running maintenance execution with
  a sealed input on a copy of the validated active state
  (``state_fixtures.start_active_copy``); ``submit_history`` delivers its
  submission intent and ``start_native_final`` adds its decision basis.
  ``start_query_repository(test)`` publishes knowledge records and a relation
  through the public ``initialize``. ``start_repair_host(test)`` gives a bare
  engine over a real repository that holds one pending operational retry.
  ``initialized`` and the template build ``initialized_instance`` run the
  public ``initialize`` alone; ``PublicInitializationRunner`` answers its
  interpretation roles.

``native_result`` is a provider's native final output for a registered
execution, as the runner reports it; it creates no process.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import create_autospec

from do_math import contracts, execution_lifecycle, execution_profiles as profiles, knowledge_io, knowledge_records as kr
from do_math import planning, submission
from do_math.configuration import DEFAULT_CONFIG
from do_math.context_store import prepare_role_input
from do_math.engine import ResearchEngine
from do_math.governance import OPERATING_ROLES, TASK_WORK_ROLES
from do_math.initialization import governance_working_view, initialize_state
from do_math.repository import ResearchRepository, canonical_json, exact_content_hash
from do_math.trust_validation import AXIOMS
from research_fixtures import (FixtureAdapter, StateStore, approved_governance, bare_engine, charter, governance_start,
                               review_items)
from record_fixtures import surface_state

SCRIPTS = Path(__file__).resolve().parents[1]


def approve_contract(instance, runtime, task, decision='approved'):
    """Seal one contract review of ``task`` against the governing view of ``instance``, as ``FakeEngine.approve`` does."""
    output=review_items(['context:goal'],decision=decision)
    task['reviews']=[planning.seal_contract_review(task,output,governance_working_view(instance),runtime,execution_id='EX-review')]


def formal_verification(source, declarations, chain):
    """``FakeEngine``'s compiler double: every declaration verified as ``Eq Nat 1 1`` with no dependencies."""
    from knowledge_fixtures import formal_result
    return formal_result(source, declarations, chain, closure=(), dependency_evidence=(),
                         declaration_evidence=('Eq Nat 1 1', None), allowed_axioms=sorted(AXIOMS))


class FakeEngine(ResearchEngine):
    """The product engine over in-memory state; a save records a copy.

    Its store is the in-memory ``StateStore`` double: a rejected extended
    control preserves the rejected request on the current head through it.
    """
    def __init__(self,root,config=None):
        self._init_process_state()
        self.store=StateStore(self); self.runner=None
        self.root=Path(root); self.current_time=datetime.now(timezone.utc)
        self.lifecycle_clock=lambda:self.current_time.isoformat()
        self.lifecycle_monotonic=lambda:0.
        config={**deepcopy(DEFAULT_CONFIG), 'tool_review_window_seconds':60,
                'self_check_response_window_seconds':5, **(config or {})}
        config.update(research_reconsider_seconds=60)
        self.instance,self.runtime=initialize_state(instance_id='RI-test',goal='Prove the target',
            workspace=root,config=config,source_input='Original user request',
            created_at=self.current_time.isoformat())
        self.instance.update(profiles.build_profiles(config))
        self.runtime.update(cycles=0,waiting_actions={})
        self.head='fixture-head'; self.saves=[]; self.formal_calls=[]; self.formal_behavior=None
        self.formal_verifier=self.verify
    def _execution_profile(self,action):
        # Like the product selection, the chosen profile's reference is recorded on the action.
        refs=self.runtime['tasks'].get(action.get('target'),{}).get('profile_refs')
        if refs and not action.get('profile_ref'):
            profile=profiles.resolve_profile(self.instance['execution_profiles'],refs[0])
        else:
            profile=profiles.resolve_profile(self.instance['execution_profiles'],
                action.get('profile_ref') or self.instance['role_profile_refs'][action['role']][0])
        action.update(profile_ref=profiles.profile_ref(profile),actor_kind=profile['actor_kind'])
        return profile
    def _controls(self): pass
    def _save(self,artifacts=None):
        self.saves.append({'instance':deepcopy(self.instance),'runtime':deepcopy(self.runtime),'artifacts':deepcopy(artifacts or {})})
    def _ensure_model_assessments(self): return set()
    def control(self,action,config,request_id=None):
        return self._apply_extended_control({'id':request_id or 'UI-'+str(len(self.runtime['extended_controls'])),
                                            'action':action,'config':config})
    def grant(self,identifier,initial=False,http=None):
        grant=http or {'kind':'local','roles':['intent_interpretation'] if initial else sorted(TASK_WORK_ROLES|OPERATING_ROLES),
            'reuse':'reusable','expires_at':(self.current_time+timedelta(days=1)).isoformat()}
        self.control('decision',{'change':{'kind':'grant','grant':{'id':identifier,**grant}}})
    def environment(self,name,active=False):
        from research_fixtures import trust_fixture
        request=trust_fixture(self.root/name,['synthetic-lean',name])
        chain=request['toolchain']
        self._trust_control(request,'UI-env-'+name)
        eid=next(eid for eid,e in self.instance['trust_environments'].items() if e['toolchain']==chain)
        # Explicit synthetic profile edition for this synthetic toolchain.
        configured = profiles.build_profiles({**self.instance['config'], 'lean_command':chain['configured_command']})
        for profile in configured['execution_profiles'].values():
            if profile['role'] == 'trust_check':
                self.instance['execution_profiles'][profile['id']] = profile
                self.instance['role_profile_refs']['trust_check'] = [profiles.profile_ref(profile)]
        if active:
            self._trust_control({'operation':'transition','env_id':eid},'UI-transition-'+name)
            from do_math.trust_validation import check_environment
            self._finish_trust_transition(next(reversed(self.runtime['trust_transitions'])),
                check_environment(self.instance['trust_environments'][eid], self.runtime['trust_bindings'][eid]))
        return eid
    def activate(self, *, external_policy='explicit_grants', review_policy=None):
        """Activate through the adoption decision; ``review_policy`` None adopts the default policy."""
        self.grant('GR-init',True); self.grant('GR-research')
        record=charter('CH-test','Prove the target',rationale='Research the stated target',
            success_criteria=['Target proved'],included_scope=['Target'],priorities=['Proof'],
            evidence_boundary='Proof evidence')
        self.control('decision',{'change':{'kind':'initialization','operation':'governance','records':[record]}})
        for p in self.instance['execution_profiles'].values():
            if p['actor_kind']=='ai':
                row=profiles.capability_evidence(p,FixtureAdapter().describe(),observed_at=self.current_time.isoformat())
                self.instance.setdefault('capability_evidence',{})[row['id']]=row
        self.control('decision',{'change':{'kind':'initialization',
            'config_sha256':exact_content_hash(self.instance['config']),
            'adopt_current_governance':True,'conversation_loss_policy':'continue_authorized',
            'external_policy':external_policy,
            **({'review_policy':review_policy} if review_policy is not None else {'adopt_default_review_policy':True}),
            'initial_grant_ids':['GR-init'],'research_grant_ids':['GR-research']}})
        self.environment('base',True)
        iid=self.instance['lifecycle']['input_id']
        from do_math import governance
        from research_fixtures import intent_response
        source = governance.import_input_source(self.instance, self.runtime, iid)
        author_action = {'id':'AC-interpret', 'role':'intent_interpretation', 'target':iid, 'stage':'interpret'}
        author = self._register_execution(author_action, {'id':'EX-interpret','role':'intent_interpretation','status':'running'})
        output = intent_response({'action':author_action,'user_request':source,
                                  'governance':governance.governance_view(self.instance)})
        bundle = governance.prepare_import(self.instance, self.runtime, source, output,
                                           execution_id=author['id'], input_ref=iid)
        checker_action = {'id':'AC-check','role':'intent_interpretation','target':iid,'stage':'check','import_id':bundle['id']}
        checker = self._register_execution(checker_action, {'id':'EX-check','role':'intent_interpretation','status':'running',
                                                          'intent_import_sha256':bundle['sha256']})
        verdict = intent_response({'action':checker_action,'interpretation_to_check':bundle,
                                   'governance':governance.governance_view(self.instance)})
        governance.check_import(self.instance, self.runtime, bundle['id'], verdict, execution_id=checker['id'])
        self.instance, self.runtime, _ = governance.apply_import(self.instance, self.runtime, bundle['id'])
        for eid in (author['id'], checker['id']):
            self._end_machine_execution(self.runtime['executions'][eid], outcome='execution_incomplete', disposition={'kind':'test_fixture'})
        self._complete_initial_intent(iid)
        result=self._activate_initialization()
        if not result['activated']: raise AssertionError(result)
        self.runtime['queue'].clear(); self.runtime['pending_events'].clear()
    verification=staticmethod(formal_verification)
    def verify(self,**args):
        self.formal_calls.append(args)
        if self.formal_behavior: return self.formal_behavior(args)
        return self.verification(args['source'],args['declarations'],args['expected_toolchain'])
    def knowledge(self,kid,env_id=None,dependencies=None):
        env_id=env_id or self.instance['active_trust_environment']; source='theorem '+kid.lower()+' : 1 = 1 := rfl'
        self.instance,_=kr.create_candidate(self.instance,{'id':kid,'kind':'lemma','statement':'One equals one',
            'summary':'Reflexivity','lean_code':source,'declaration_names':[kid.lower()],'dependencies':dependencies or []},
            source_ref='UI-source',actor_ref='EX-author')
        result=self.verification(source,[kid.lower()],self.instance['trust_environments'][env_id]['toolchain'])
        self.instance=kr.record_formal_result(self.instance,kid,result,env_id,runtime=self.runtime)
        self.instance,_=kr.record_identity_assessment(self.instance,kid,
            {'decision':'match','basis':kr.identity_basis(self.instance,kid)},'review-policy',runtime=self.runtime)
        return self.instance['knowledge'][kid]
    def task(self,task_id='T1',approved=True,condition=None,inputs=None):
        t={'id':task_id,'revision':1,'status':'planned','question':'Derive result',
           'scope':{'included':['derive'],'excluded':['publish']},
           'expected':{'outputs':['proof'],'research_change':'resolve target'},
           'progress_criteria':[{'id':'PG-'+task_id,'claim':'advance','evidence_required':[]}],
           'completion_obligations':[{'id':'OB-'+task_id,'claim':'derive','judges':['task_assessor'],'evidence_required':[]}],
           'work_class':'nonformal','inputs':inputs or [],'reuse':[],'dependencies':[],
           'occurrence_condition':condition or {'op':'always'},'results':[],'producer_execution':'EX-author',
           'profile_refs':[profiles.profile_ref(next(p for p in self.instance['execution_profiles'].values() if p['role']=='research_work' and p['ai']['tier']=='high'))],
           'authority_refs':['GR-research'],'basis_refs':['context:goal'],'reviews':[]}
        self.runtime['tasks'][task_id]=t
        if approved: self.approve(t)
        return t
    def approve(self,t,decision='approved'):
        approve_contract(self.instance,self.runtime,t,decision)
    def machine(self,role):
        a=next(a for a in self.runtime['queue'] if a['role']==role)
        self._process_machine_action(a); return a


def formal_check_engine(test):
    """A ``FakeEngine`` holding candidate ``K1`` and its queued ``formal_check``: ``(engine, action)``.

    The formal check profile uses the active trust environment's configured
    command. The adapter patch and the temporary root end with ``test``.
    """
    from unittest.mock import patch
    adapter = patch('do_math.initialization.adapter_for', return_value=FixtureAdapter())
    adapter.start()
    test.addCleanup(adapter.stop)
    directory = tempfile.TemporaryDirectory()
    test.addCleanup(directory.cleanup)
    engine = FakeEngine(Path(directory.name))
    engine.activate()
    engine.instance, _ = kr.create_candidate(engine.instance,
        {'id': 'K1', 'kind': 'lemma', 'statement': 'One equals one', 'summary': 'Reflexivity',
         'lean_code': 'theorem k1 : 1 = 1 := rfl', 'declaration_names': ['k1'], 'dependencies': []},
        source_ref='UI-source', actor_ref='EX-author')
    environment = engine._formal_environment()
    editions = profiles.build_profiles({**engine.instance['config'],
        'lean_command': environment['toolchain']['configured_command']})
    engine.instance['execution_profiles'].update(editions['execution_profiles'])
    engine.instance['role_profile_refs']['formal_check'] = editions['role_profile_refs']['formal_check']
    action = {'id': 'AC-formal', 'role': 'formal_check', 'target': 'K1'}
    engine.runtime['queue'] = [action]
    return engine, action


def initialized(repository, *, goal, **options):
    """A new Git repository at ``repository`` with one instance from the public ``initialize``; returns its ID.

    The workspace defaults to ``repository / 'work'``; ``options`` pass to ``initialize``.
    """
    from do_math.engine import initialize
    from research_fixtures import git_init
    options.setdefault('workspace', Path(repository) / 'work')
    return initialize(git_init(repository), goal=goal, **options)['instance_id']


def initialized_instance(root, shared, *, goal, config):
    """``restore_template`` build: the public ``initialize`` alone; returns the instance ID.

    The repository is ``root / 'repository'`` and the workspace ``root / 'work-0'``.
    """
    return initialized(root / 'repository', goal=goal, workspace=root / 'work-0', config=config)


class PublicInitializationRunner:
    """Synthetic independent author/checker outputs; real producer/receiver paths."""
    def run(self, *, workspace, on_started, should_stop, control_binding, **kwargs):
        import json
        from do_math import submission
        from do_math.repository import canonical_json
        from research_fixtures import intent_response, seal_response
        context = json.loads((workspace/'input/submission/context.json').read_bytes())
        if context['action']['role'] != 'intent_interpretation':
            raise AssertionError('No research is authorized by the initialization fixture')
        on_started({'job_name':kwargs['launch_ticket']['job_name']})
        output = seal_response(intent_response(context), context, workspace)
        (workspace/'draft.json').write_bytes(canonical_json(output))
        delivery = submission.request_control(workspace, 'draft.json', kind='submit_intent', wait_seconds=0, binding=control_binding)
        # The owner loop receives the request on its next pass. submit_intent closes
        # further research authority; the flag it sets is the expected barrier.
        from do_math.control_transport import ControlTransport
        ControlTransport.wait_receipt(control_binding, delivery['request_id'], 60)
        return {'status':'completed','output':output,'usage':{},'error':None}

def context_engine(instance=None, runtime=None):
    """Keep the real context producer; replace unrelated host observations."""
    base, running = surface_state()
    base.update(relations=[], goal_status='unresolved', lifecycle={'state': 'active'})
    running.update(inputs=[], questions=[])
    running['executions'] = {}
    if instance:
        profiles = {**base['execution_profiles'], **instance.get('execution_profiles', {})}
        base.update(instance)
        base['execution_profiles'] = profiles
    if runtime:
        running.update(runtime)
    engine = bare_engine(base, running, head='a' * 40, store=create_autospec(ResearchRepository, instance=True))
    engine.store.read_many.side_effect = lambda paths, snapshot: {p: engine.store.read(p, snapshot) for p in paths}
    engine._documents = {role: contracts.prompt_documents(role) for role in ('research_preparation', 'research_plan', 'research_work')}
    engine._preparation_checkpoint = create_autospec(engine._preparation_checkpoint, side_effect=lambda: None)
    engine._session_slots = create_autospec(engine._session_slots)
    engine._academic_status = create_autospec(engine._academic_status, side_effect=lambda: {})
    engine._planning_history = create_autospec(engine._planning_history, side_effect=lambda *args: [])
    engine._execution_profile = create_autospec(engine._execution_profile,
                                                side_effect=ValueError('no compiler launched in input test'))
    engine._ensure_academic_followup = create_autospec(engine._ensure_academic_followup, side_effect=lambda: None)
    engine._record_academic_assessment = create_autospec(engine._record_academic_assessment, side_effect=lambda *args: None)
    return engine


def package(engine, root, role='research_plan', target=None):
    action = {'id': 'AC-plan', 'role': role}
    if target:
        action['target'] = target
    context = engine._context(action, root, execution_id='EX-plan')
    profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == role)
    result = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime, role=role,
        profile=profile, snapshot=engine.head, workspace=root, activity_id='AC-1',
        install_submission_tools=True, artifact_prefix='runtime/artifacts/BA-plan')
    fixed = submission.load_json((root / 'input/submission/context.json').read_bytes())
    return result, fixed


def initial_failure_engine(root, kind='execution_failure', stage='interpret'):
    AT = '2026-09-22T00:00:00+00:00'
    from do_math import activities, execution_lifecycle, execution_profiles
    seed = FakeEngine(root)
    seed.grant('GR-init', True)
    seed.instance['grants']['GR-init']['roles'].append('maintenance')
    lifecycle = seed.instance['lifecycle']
    from do_math.model_policy import selection
    selected = selection(seed.instance['config'], {'role': 'intent_interpretation'}, {}, {},
                         instance=seed.instance)['profile_ref']
    profile = execution_profiles.resolve_profile(seed.instance['execution_profiles'], selected)
    lifecycle.update(input_id='UI-original', adoption={'initial_grant_ids': ['GR-init'],
        'initial_profile_ref': execution_profiles.profile_ref(profile)})
    seed.runtime['inputs'] = [{'id': 'UI-original', 'config': {}, **lifecycle['immutable_input']}]
    engine = bare_engine(seed.instance, seed.runtime, head='a' * 40, store=create_autospec(ResearchRepository, instance=True))
    engine.lifecycle_clock = seed.lifecycle_clock
    engine.lifecycle_monotonic = seed.lifecycle_monotonic
    action = {'id': 'AC-original', 'role': 'intent_interpretation', 'target': 'UI-original',
              'stage': stage, 'owner_activity_id': 'AY-original'}
    activities.open_activity(engine.runtime, activity_id='AY-original', activity_kind='intent_interpretation',
        owner_ref='engine', input_refs=['UI-original'], opened_at=AT)
    failed = execution_lifecycle.create_execution(execution_id='EX-bad', owner_activity_id='AY-original',
        actor_kind='ai', input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=AT)
    from research_fixtures import dispatched_launch
    failed['launch_ticket'] = {**dispatched_launch(failed['id'], profile), 'phase':'finished'}
    failed.update(role=action['role'], action=deepcopy(action), capacity={'local_termination': 'confirmed'})
    activities.assign_execution(engine.runtime, 'AY-original', failed)
    execution_lifecycle.transition_execution(failed, 'starting', at=AT)
    execution_lifecycle.transition_execution(failed, 'stopping', at=AT)
    execution_lifecycle.transition_execution(failed, 'ended', at=AT, outcome='execution_incomplete')
    activities.wait_for(engine.runtime, 'AY-original', reason=kind, condition={'action_ids': [action['id']]},
                        next_owner='maintenance', at=AT)
    wait = {'kind': kind, 'action': action, 'execution_id': 'EX-bad', 'reason': 'synthetic failure'}
    if kind == 'output_validation':
        action.update(repair_attempt=2, repair={'execution_id': 'EX-bad', 'issues': [], 'retry_bundle_ids': ['IN-pending']})
    engine.runtime.update(queue=[], waiting_actions={action['id']: wait})
    return engine, action, wait

class NoRepository:
    """The store of an in-memory engine: no Git directory, and nothing to read."""
    git_dir = None

    def read(self, path, snapshot=None):
        # The engine passes this reader to consumers; reading through it is a test defect.
        raise AssertionError("an in-memory engine has no stored artifact: " + path)

    def published_state(self, head):
        return None  # Nothing was published, so the engine's state is never unchanged.


def routing_engine():
    # Every loaded engine has a store and a configured artifact limit; consumers
    # read store.git_dir and config['max_artifact_bytes'] without a fallback.
    engine = bare_engine(store=NoRepository())
    engine.instance = governance_start({"id": "RI-test", "knowledge": {}, "relations": [],
                       "goal_status": "unresolved",
                       "config": {"goal_auditors": 2, "max_artifact_bytes": DEFAULT_CONFIG["max_artifact_bytes"]}})
    engine.runtime = {"tasks": {}, "activities": {}, "executions": {}, "queue": [],
                      "questions": [], "question_links": [], "history": [], "inputs": [],
                      "interpretations": {}, "status": "ready"}
    engine._bind_revision_action = create_autospec(engine._bind_revision_action)
    engine._cancel_selected_revision_targets = create_autospec(engine._cancel_selected_revision_targets)
    engine._record_output_questions = create_autospec(engine._record_output_questions)
    return engine

def intent_import(engine, *, clarification=False, payload=None):
    """Author one interpretation of the input ``UC-input`` on a ``routing_engine``; returns ``(bundle, check action)``.

    With ``clarification`` the interpretation asks one blocking question ``Q-one``;
    ``payload`` is the proposed change of its single unit ``IU-one``.
    """
    text = "Keep the original purpose."
    engine.runtime["inputs"] = [{"id": "UC-input", "text": text, "config": {}, "origin": "user"}]
    questions = ["Which scope?"] if clarification else []
    output = {"summary": "interpretation", "used_sources": [], "questions": questions,
        "import_units": [{"unit_id": "IU-one",
            "source_range": {"start": 0, "end": len(text)}, "interpretation": text,
            "owner_kind": "charter", "owner_ref": "CH-one", "payload": payload or {},
            "decision_refs": [], "question_refs": ["Q-one"] if clarification else []}],
        "question_details": [{"id": "Q-one", "question_index": 0, "blocks": True,
            "target_ids": ["RI-test"], "reason": "scope choice changes the work", "source_unit_ids": ["IU-one"],
            "options": []}] if clarification else []}
    author_action = {"id": "AC-author", "role": "intent_interpretation", "target": "UC-input", "lineage_id": "AC-root"}
    engine.runtime["executions"]["EX-author"] = {"id": "EX-author", "status": "running",
        "role": "intent_interpretation", "action": deepcopy(author_action)}
    engine._apply(author_action, output, "EX-author")
    engine.runtime["executions"]["EX-author"]["status"] = "ended"
    bundle = next(iter(engine.runtime["intent_imports"].values()))
    engine.runtime["executions"]["EX-check"] = {"id": "EX-check", "role": "intent_interpretation",
                                                "status": "ended", "intent_import_sha256": bundle["sha256"]}
    action = deepcopy(engine.runtime["queue"][0])
    engine.runtime["queue"] = []
    return bundle, action


def intent_verdict(bundle, decision="approved", complete=True):
    """The independent check's output for ``bundle``; any decision but approved names one finding."""
    return {"decision": decision, "scope_complete": complete, "bundle_sha256": bundle["sha256"],
            "unit_ids": ["IU-one"], "question_ids": [q["id"] for q in bundle["output"]["question_details"]],
            "findings": [] if decision == "approved" else ["Missing second clause"],
            "summary": "check", "used_sources": [], "questions": []}


def reassessment_engine(directory):
    """A ``FakeEngine`` whose task ``TK-1`` waits for the missing input ``SO-new`` after an incomplete assessment."""
    from record_fixtures import apply_assessment, transfer_assessment
    instance, runtime, assessment = transfer_assessment()
    assessment.update(decision='incomplete', item_dispositions=assessment['item_dispositions'][1:],
        unresolved=[{'obligation_id': 'OB-1', 'missing_inputs': ['SO-new'], 'next_owner': 'research_work'}])
    instance, runtime = apply_assessment(instance, runtime, assessment)
    engine = FakeEngine(directory)
    engine.instance['lifecycle']['state'] = 'active'
    engine.instance.update({key: value for key, value in instance.items() if key not in {'lifecycle', 'config'}})
    engine.runtime.update(runtime)
    engine.runtime['queue'] = [{'id': 'AC-other', 'role': 'research_preparation'}]
    return engine


def governance_host():
    """``(engine, bundle, request)``: a bare engine holding ``record_fixtures.checked_import``'s state.

    ``request`` is the user's later exact approval in the public decision shape;
    completing the initial intent and activation are recorded, not performed.
    """
    from unittest.mock import create_autospec
    from record_fixtures import checked_import
    i, rt, bundle, request = checked_import()
    request = {**request, 'config': {'change': request['config']}}  # the public decision shape
    h = bare_engine(i, rt)
    h._complete_initial_intent = create_autospec(h._complete_initial_intent,
        side_effect=lambda target: setattr(h, 'completed_input', target))
    h._activate_initialization = create_autospec(h._activate_initialization,
        side_effect=lambda: setattr(h, 'activation_attempted', True))
    rt.setdefault('events', [])
    rt.setdefault('pending_events', [])
    for execution in rt['executions'].values(): execution.setdefault('status', 'queued')
    i['config'] = {**deepcopy(DEFAULT_CONFIG),  'scholarly_enabled': False}
    # Config addition is not a premise of this charter import.
    return h, bundle, request


def goal_audit_host():
    """``(engine, action, output)``: ``governance_host`` over ``record_fixtures.audited_governance``.

    ``output`` is a satisfied goal verdict whose additional audit ``AU`` is only partial.
    """
    from unittest.mock import create_autospec
    from record_fixtures import audited_governance
    h, _, _ = governance_host()
    h.instance, h.runtime = audited_governance()
    h.instance.update(knowledge={}, goal_judgments=[])
    h.runtime.update(events=[], pending_events=[], last_observed_utc='2020-01-01T00:00:00Z')
    h._goal_basis_key = create_autospec(h._goal_basis_key, return_value='B')
    action = {'role': 'goal_audit', 'basis': 'B', 'slot': 0, 'required': 1}
    execution = {'id': 'AUDITOR', 'role': 'goal_audit', 'action': deepcopy(action), 'status': 'ended'}
    h._bind_governance_input(action, execution, h._governance_context(action, {}))
    h.runtime['executions']['AUDITOR'] = execution
    output = {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [],
        'summary': 'Ordinary goal verdict cannot override audit', 'questions': [], 'findings': [],
        'additional_audits': [{'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': 'partial',
            'reason': 'Only part of the approved scope has evidence',
            'input_hashes': execution['additional_audit_input'][0]['input_hashes']}]}
    return h, action, output


def start_submission_history(test):
    """Give ``test`` a running maintenance execution on a copy of the validated active state.

    ``state_fixtures.start_active_copy`` first; then the execution ``EX-history``
    holds the sealed input bundle ``BA-history-input`` and installed submission
    tools in ``test.workspace``. Sets ``engine``, ``workspace``, ``context``,
    ``schema``, ``transport``, ``binding`` and a valid ``output``.
    No model or Lean call is made.
    """
    from do_math import contracts, submission
    from do_math.control_transport import ControlTransport
    from do_math.engine import ResearchEngine
    from do_math.planning import governance_revisions
    from do_math.repository import canonical_json
    from research_fixtures import seal_response
    from state_fixtures import start_active_copy
    start_active_copy(test)
    test.engine = ResearchEngine(test.repo, test.identifier)
    action = {'id': 'AC-history', 'role': 'maintenance'}
    test.engine._action_lifecycle_gate(action)
    execution = test.engine._register_execution(action,
        {'id': 'EX-history', 'role': 'maintenance', 'status': 'running'})
    # A sealed role input names its prompt in the input manifest; the prompt is archived below.
    prompt = b'Synthetic history prompt'
    prefix = 'runtime/artifacts/BA-history-input/'
    execution.update(grant_id=action['grant_id'], input_bundle='BA-history-input', input_snapshot=test.engine.head,
                     input_manifest={'prompt': {'artifact_ref': prefix + 'input.txt',
                                                'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}})
    execution.update(governance_revisions(test.engine.instance))
    test.workspace = Path(test.engine.instance['workspace']) / 'runs/EX-history/workspace'
    test.workspace.mkdir(parents=True)
    test.context = {'action': action, 'execution_id': execution['id'], 'snapshot': test.engine.head,
        'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {},
        'grants': [deepcopy(test.engine.instance['grants'][action['grant_id']])]}
    test.schema = contracts.schema_for('maintenance')
    submission.install_tools(test.workspace, test.context, test.schema, 1024*1024)
    test.engine._save({prefix + 'input.txt': prompt,
                       prefix + 'input/submission/context.json': canonical_json(test.context),
                       prefix + 'schema.json': canonical_json(test.schema)})
    test.transport = ControlTransport(test.root/'delivery')
    test.binding = test.transport.issue('EX-history', action['grant_id'], workspace=test.workspace)
    test.output = {'summary': 'Exact é diagnostic', 'used_sources': [], 'questions': [],
                   'report': 'Actual central receipt test; no mathematical approval.', 'remaining_work': []}
    seal_response(test.output, test.context, test.workspace)


def submit_history(test, request_id, raw):
    """Deliver ``raw`` as ``EX-history``'s submission intent ``request_id``; returns ``(request, receipt)``."""
    (test.workspace/'draft.json').write_bytes(raw)
    request = {**test.binding, 'request_id': request_id, 'kind': 'submit_intent',
               'payload': {'draft_path': 'draft.json'}}
    return request, test.transport.receive(request, publish=test.engine._publish_control_request)


def start_native_final(test):
    """``start_submission_history`` whose execution also records its decision basis, as a native final needs."""
    from do_math.input_basis import capture_decision_basis
    start_submission_history(test)
    test.engine.runtime['executions']['EX-history']['decision_basis'] = capture_decision_basis(
        test.engine.instance, test.engine.runtime, [])


def start_repair_host(test):
    """Give ``test`` a bare engine over a real repository holding one pending operational retry.

    ``EX-target`` (research_work) and ``EX-review`` (operational_review) ended;
    the review's disposition ``OD-repair`` retries the target's unfinished
    activity in a fresh workspace. The target's sealed input ``source`` holds
    ``raw`` (sha256 ``digest``) at ``relative`` under bundle ``BA-target``,
    while the workspace copy at ``destination`` is damaged. Sets ``host``,
    ``raw``, ``digest``, ``relative``, ``source``, ``destination`` and ``record``.
    """
    from do_math import activities
    from research_fixtures import current_state, git_init
    at = "2026-09-20T00:00:00Z"
    root = Path(test.enterContext(tempfile.TemporaryDirectory()))
    repo = git_init(root / "repo")
    test.host = host = bare_engine(store=ResearchRepository(repo, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV"))
    configured = profiles.build_profiles(DEFAULT_CONFIG)
    built = configured["execution_profiles"]
    host.instance, host.runtime = current_state({"workspace": str(root / "private"),
        "capacity_constraints": configured["capacity_constraints"],
        "execution_profiles": {key: p for key, p in built.items()
                               if p["role"] in {"research_work", "operational_review"}}},
        {"tasks": {}, "executions": {}, "queue": [], "operational_dispositions": {}})
    for eid, role, aid in [("EX-target", "research_work", "AY-target"),
                            ("EX-review", "operational_review", "AY-review")]:
        profile = next(p for p in host.instance["execution_profiles"].values() if p["role"] == role)
        activities.open_activity(host.runtime, activity_id=aid, activity_kind=role,
            owner_ref="engine", input_refs=[], opened_at=at)
        execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
            actor_kind="ai", input_manifest={}, profile_ref=profiles.profile_ref(profile), created_at=at)
        execution.update(role=role, action={"id": "AC-" + eid, "role": role, "owner_activity_id": aid})
        activities.assign_execution(host.runtime, aid, execution)
        execution_lifecycle.transition_execution(execution, "ended", at=at, outcome="cancelled")
    test.raw = b"sealed mathematical input\n"
    test.digest = hashlib.sha256(test.raw).hexdigest()
    test.relative = "input/catalog/tasks.json"
    target = host.runtime["executions"]["EX-target"]
    target["input_bundle"] = "BA-target"
    target["input_manifest"] = {"catalog": [{"path": test.relative, "sha256": test.digest, "bytes": len(test.raw)}],
                                "execution_profile_ref": target["execution_profile_ref"]}
    test.source = "runtime/artifacts/BA-target/" + test.relative
    test.destination = root / "private/runs/EX-target/workspace" / test.relative
    test.destination.parent.mkdir(parents=True)
    test.destination.write_bytes(b"damaged")
    test.record = {"id": "OD-repair", "execution_id": "EX-review", "target_execution_id": "EX-target",
        "created_at": at, "status": "pending", "disposition": {
            "kind": "retry", "basis_refs": ["EX-target"], "next_owner": "engine",
            "reason": "Use a fresh workspace for the unfinished activity",
            "scope": "Same unfinished activity", "replay_safety": "No external effects"}}
    host.runtime["operational_dispositions"][test.record["id"]] = deepcopy(test.record)
    host.runtime["executions"]["EX-review"]["action"]["target"] = "EX-target"
    host.head = host.store.initialize(host.instance, host.runtime)
    host._save({test.source: test.raw,
                "runtime/artifacts/BA-target/manifest.json": canonical_json(target["input_manifest"])})


QUERY_INSTANCE_ID = "RI-00000000000000000000000000"


def start_query_repository(test):
    """Give ``test`` a published instance ``QUERY_INSTANCE_ID`` with two knowledge records and a relation.

    Sets ``root``, ``git`` (the repository), ``workspace``, ``repository``,
    ``initial_head``, ``kids`` (definition "One", theorem "Two"), ``relation_id``
    (One supports Two, through an activated kind definition), ``old_head`` (that
    state) and ``file_head`` (two more query-fixture artifacts).
    """
    import tempfile
    from do_math.engine import initialize
    from do_math.knowledge_io import (import_candidate, import_relation, register_kind_definition,
        check_kind_definition, activate_kind_definition, relation_templates)
    from do_math.repository import ResearchRepository, canonical_json
    from research_fixtures import git_init
    test.root = Path(test.enterContext(tempfile.TemporaryDirectory()))
    test.git = git_init(test.root / "git")
    test.workspace = test.root / "workspace"
    initialized = initialize(test.git, goal="A goal", workspace=test.workspace, instance_id=QUERY_INSTANCE_ID,
                             config={"operator_enabled": False, "scholarly_enabled": False})
    test.repository = ResearchRepository(test.git, QUERY_INSTANCE_ID)
    test.initial_head = initialized["snapshot"]
    head, instance, runtime = test.repository.load(test.initial_head)
    if head != test.initial_head:
        raise AssertionError('The initialized head did not load as itself')
    test.kids = []
    for title, kind, summary in (("One", "definition", "alpha"), ("Two", "theorem", "beta")):
        instance, runtime, kid = import_candidate(instance, runtime,
            {"kind": kind, "title": title, "statement": summary, "summary": summary,
             "explanation": "Explicit query fixture: " + summary, "lean_code": "",
             "declaration_names": [], "dependencies": []}, source_ref=QUERY_INSTANCE_ID, actor_ref=QUERY_INSTANCE_ID)
        test.kids.append(kid)
    definition = next(row for row in relation_templates() if row['token'] == 'supports')
    instance, _ = register_kind_definition(instance, definition, source_ref=QUERY_INSTANCE_ID, actor_ref=QUERY_INSTANCE_ID)
    check_ref = 'runtime/artifacts/query-kind/check.json'
    approval_ref = 'runtime/artifacts/query-kind/approval.json'
    instance = check_kind_definition(instance, 'relation', 'supports', check_ref=check_ref, actor_ref=QUERY_INSTANCE_ID)
    instance = activate_kind_definition(instance, 'relation', 'supports', approval_ref=approval_ref, actor_ref=QUERY_INSTANCE_ID)
    instance, test.relation_id = import_relation(instance,
        {"kind": "supports", "source": test.kids[0], "target": test.kids[1], "evidence": "alpha"},
        source_ref=QUERY_INSTANCE_ID, actor_ref=QUERY_INSTANCE_ID)
    test.old_head = test.repository.save_with_state(test.initial_head, instance, runtime, artifacts={
        check_ref: canonical_json({'definition': definition, 'verdict': 'checked',
            'scope': 'Explicit CORE_TESTS kind-check fixture'}),
        approval_ref: canonical_json({'definition': definition, 'decision': 'activate',
            'scope': 'Explicit CORE_TESTS fixture; not actual user approval'}),
    })[0]
    test.file_head = test.repository.save_with_state(test.old_head, instance, runtime, artifacts={
        "runtime/artifacts/query-fixture/a.txt": b"needle alpha",
        "runtime/artifacts/query-fixture/b.txt": b"needle beta",
    })[0]

def native_result(execution, context, raw, workspace):
    """Pure protocol fixture; actual Job coverage is a separate connected test."""
    from do_math.codex_adapter import _artifact
    from do_math.launch import ticket
    execution['launch_ticket'] = {**ticket(execution['id'], {'sha256':execution['execution_profile_ref']['sha256'],
        'actor_kind':'ai','role':execution.get('role','maintenance')}), 'phase':'finished'}
    prompt = b'exact sealed prompt'
    request = {'execution_id': execution['id'], 'profile_ref': execution['execution_profile_ref'],
        'cwd': str(workspace), 'codex_path': 'fixture-cli',
        'control_binding': {'execution_id': execution['id'], 'grant_id': execution['grant_id']}}
    request_raw = json.dumps(request).encode()
    identity = {'request_sha256': hashlib.sha256(request_raw).hexdigest(),
        'pid': 123, 'creation_filetime': 134345064658094591, 'job_name': execution['launch_ticket']['job_name'], 'execution_id': execution['id'],
        'profile_ref': execution['execution_profile_ref']}
    # The role input manifest carries the sealed prompt digest the provider received.
    manifest = execution.get('input_manifest')
    if not isinstance(manifest, dict):
        manifest = execution['input_manifest'] = {}
    manifest['prompt'] = {**manifest.get('prompt', {}),
                          'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}
    execution['capacity'] = {'local_termination': 'confirmed',
        'process': {**identity, 'creation_filetime': str(identity['creation_filetime'])}}
    stream = b''.join(json.dumps(row, ensure_ascii=False).encode() + b'\n' for row in [
        {'type': 'thread.started', 'thread_id': 'thread'}, {'type': 'turn.started'},
        {'type': 'item.completed', 'item': {'id': 'message', 'type': 'agent_message', 'text': raw.decode()}},
        {'type': 'turn.completed', 'usage': {}}])
    collect = {'result': 'output_collected', 'reasons': [], 'source_request': _artifact(request_raw),
        'source_prompt': _artifact(prompt), 'stdout': _artifact(stream), 'stderr': _artifact(b''),
        'final': _artifact(raw), 'execution_id': execution['id'], 'profile_ref': execution['execution_profile_ref'],
        'worker_status': {'state': 'exited', 'cli_exit_code': 0, 'request_sha256': identity['request_sha256'],
            'stdin_sha256': execution['input_manifest']['prompt']['sha256'], 'schema_sha256': None,
            'execution_id': execution['id'], 'profile_ref': execution['execution_profile_ref']},
        'termination_barrier': {'confirmed': True, 'root_signaled': True, 'active_processes': 0, 'process_ids': []},
        'stop_receipts': [], 'process_identity': {'pid': 123, 'creation_filetime': identity['creation_filetime']}}
    return {'status': 'completed', 'output': None, 'collection': 'provider_evidence_only',
        'execution_id': execution['id'], 'profile_ref': execution['execution_profile_ref'],
        'execution': {'started': identity, 'collect': collect}}

EVIDENCE_TIME = '2026-09-20T00:00:00+00:00'


def input_snapshot_store(instance, runtime):
    """A ``ResearchRepository`` double (autospec) that holds one fixed input snapshot, ``'input-snapshot'``.

    ``load`` and ``view`` return a copy of ``(instance, runtime)`` at that
    snapshot only; ``read`` serves only that snapshot's archived role context
    (its tasks and ready task IDs). It has no Git directory, so no process
    cache records its reads. It is a storage boundary, never a domain transition.
    """
    from unittest.mock import create_autospec
    from do_math.repository import ResearchRepository
    held = deepcopy((instance, runtime))
    store = create_autospec(ResearchRepository, instance=True)
    store.git_dir = None
    def load(snapshot=None):
        if snapshot != 'input-snapshot': raise ValueError('unexpected snapshot')
        return snapshot, *deepcopy(held)
    def read(path, snapshot=None):
        if path.endswith('/input/submission/context.json'):
            instance, runtime = held
            return json.dumps({'snapshot': snapshot, 'tasks': list(runtime['tasks'].values()),
                'ready_task_ids': planning.ready_task_ids(runtime, instance)}).encode()
        raise ValueError('fixture has no archived artifact: ' + path)
    store.load.side_effect = store.view.side_effect = load
    store.read.side_effect = read
    return store


def evidence_engine(goal='Establish P', *, academic_requirements=None):
    e = bare_engine()
    e.instance = governance_start({'id': 'RI-evidence', 'lifecycle': {'state': 'active'},
        'goal_status': 'unresolved', 'goal_judgments': [],
        'sources': [], 'knowledge': {}, 'relations': [], 'decisions': {}, 'config': deepcopy(DEFAULT_CONFIG),
        'workspace': str(SCRIPTS),
        'grants': {'GR-evidence': {'id': 'GR-evidence', 'kind': 'local', 'status': 'active',
            'roles': ['research_work', 'supplemental_research'], 'task_ids': [],
            'expires_at': None, 'reuse': 'reusable'}}})
    e.instance = approved_governance(e.instance, [charter('CH-fixture', goal, rationale='Research the stated goal',
        desired_result=goal, success_criteria=[goal], evidence_boundary='Proof not preference',
        academic_requirements=academic_requirements or [])],
        source=('US-fixture', 'User approves: ' + goal), approval_id='DC-fixture')
    # ENGINE currently consumes this read projection. It is never persisted.
    from do_math.initialization import governance_working_view
    e.instance = governance_working_view(e.instance)
    e.instance['goal_status'] = 'unresolved'
    e.instance.update(profiles.build_profiles(e.instance['config']))
    e.runtime = {'last_observed_utc': EVIDENCE_TIME, 'tasks': {}, 'activities': {}, 'executions': {}, 'queue': [],
        'waiting_actions': {}, 'history': [], 'inputs': [], 'questions': [], 'question_links': [],
        'interpretations': {}, 'events': [], 'pending_events': [], 'status': 'ready'}
    e.head = 'input-snapshot'
    e.lifecycle_clock = lambda: EVIDENCE_TIME
    e.lifecycle_monotonic = lambda: 0
    e._documents = contracts.all_prompt_documents()
    e.store = input_snapshot_store(e.instance, e.runtime)
    return e


def evidence_task(identifier='TK-1'):
    return {'id': identifier, 'revision': 1, 'status': 'planned', 'title': 'Bounded result',
        'question': 'Does P hold?', 'scope': {'included': ['P'], 'excluded': ['publication']},
        'expected': {'outputs': ['report'], 'research_change': 'resolve one case'},
        'progress_criteria': [{'id': 'PC-1', 'claim': 'inspect a case', 'evidence_required': []}],
        'completion_obligations': [
            {'id': 'OB-proof', 'claim': 'provide result', 'judges': ['research_plan'], 'evidence_required': ['EV-proof']},
            {'id': 'OB-scope', 'claim': 'account for scope', 'judges': ['research_plan'], 'evidence_required': ['EV-scope']}],
        'inputs': [], 'reuse': [], 'dependencies': [], 'profile_refs': [], 'authority_refs': ['GR-evidence'],
        'basis_refs': [], 'occurrence_condition': {'op': 'always'}, 'producer_execution': 'EX-preparation',
        'reviews': [], 'results': []}


def reviewed_task(e, identifier='TK-1', **changes):
    task = evidence_task(identifier); task.update(changes)
    task['profile_refs'] = [profiles.profile_ref(p) for p in e.instance['execution_profiles'].values()
                            if p['role'] in {'research_work', 'supplemental_research'}]
    e.runtime['tasks'][identifier] = task
    output = review_items([identifier])
    task['reviews'] = [planning.seal_contract_review(task, output, e.instance, e.runtime, execution_id='EX-review-' + identifier)]
    return task


def plan_output(**changes):
    return dict({'dispositions': [], 'task_assessments': [], 'goal_audit': False, 'preparation_requests': []}, **changes)


def apply_plan(e, plan, execution_id='EX-plan'):
    e.store = input_snapshot_store(e.instance, e.runtime)
    e.runtime['executions'][execution_id] = {'id': execution_id, 'role': 'research_plan', 'status': 'ended',
                                          'input_snapshot': 'input-snapshot', 'input_bundle': 'BA-plan', 'extensions': {}}
    e._apply({'id': 'AC-' + execution_id, 'role': 'research_plan'}, plan, execution_id)


def truth_candidate(statement='True', source='theorem truth : True := True.intro', **changes):
    """``knowledge_candidate`` stating ``statement`` in every exposition field, proved by ``source``."""
    from knowledge_fixtures import knowledge_candidate
    return knowledge_candidate(title=statement, statement=statement, explanation=statement, summary=statement,
                               lean_code=source, **changes)


def accept_knowledge(e, proposed=None):
    """Only Lean/identity responses are fixtures; import/binding/use gates run."""
    proposed = proposed or truth_candidate()
    e.instance, e.runtime, kid = knowledge_io.import_candidate(e.instance, e.runtime, proposed,
        source_ref='fixture:source', actor_ref='EX-producer')
    from research_fixtures import trust_environment, trust_fixture
    if not hasattr(e, '_trust_fixture_directory'):
        e._trust_fixture_directory = tempfile.TemporaryDirectory()
    trust, binding = trust_environment(trust_fixture(Path(e._trust_fixture_directory.name), ['synthetic-lean']))
    e.instance.update(active_trust_environment='TE-fixture', trust_environments={'TE-fixture': trust})
    e.runtime['trust_bindings'] = {'TE-fixture': binding}
    from knowledge_fixtures import formal_result
    response = formal_result(proposed['lean_code'], ['truth'], trust['toolchain'],
                             dependency_evidence=('fixture-type', 'fixture-constructor'),
                             declaration_evidence=(proposed['statement'], 'fixture-proof'),
                             allowed_axioms=deepcopy(trust['allowed_axioms']))
    e.instance = kr.record_formal_result(e.instance, kid, response, 'TE-fixture', runtime=e.runtime)
    e.instance, aid = kr.record_identity_assessment(e.instance, kid, {'decision': 'match',
        'basis': kr.identity_basis(e.instance, kid)}, 'policy:fixture', runtime=e.runtime)
    return kid, aid


def audit_goal(e, kid, decision='satisfied'):
    basis = e._goal_basis_key()
    for slot in range(2):
        eid = 'EX-goal-' + str(slot) + '-' + str(len(e.instance['goal_judgments']))
        e.runtime['executions'][eid] = {'id': eid, 'role': 'goal_audit', 'status': 'ended'}
        e._bind_governance_input({'role': 'goal_audit'}, e.runtime['executions'][eid],
                                e._governance_context({'role': 'goal_audit'}, {}))
        e._apply({'role': 'goal_audit', 'slot': slot, 'basis': basis, 'required': 2},
            {'decision': decision, 'scope_complete': True, 'used_sources': [kid],
             'summary': 'Fixture auditor response for the stated charter', 'questions': []}, eid)
