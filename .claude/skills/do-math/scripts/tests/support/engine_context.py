"""Role-input scenes of the engine region: the product's context producer on a Sim's engine and store.

The legacy ``engine_fixtures.context_engine`` kept the context producer but gave
it an autospec store and replaced seven engine methods (the preparation
checkpoint, session slots, academic status, planning history, execution profile,
academic follow-up and assessment recording). ``context_engine`` here keeps the
same synthetic records as the input (``context_state``) and replaces nothing: it
is the engine of a restored Sim, every method runs, and the store is the Sim's
``ResearchRepository`` over the Git port. Artifact bytes a test reads are
published with ``publish``; an issued input an execution received is archived
with ``issue``, as the engine archives one below its input bundle.

- ``context_state(instance=None, runtime=None)``: ``record_fixtures.surface_state``
  with the legacy ``context_engine`` additions, merged with ``instance`` and
  ``runtime`` as that fixture merged them. Pure records for unit tests.
- ``context_engine(instance=None, runtime=None, files=None)``: a Sim engine whose
  in-memory state is ``context_state(...)`` (keeping the Sim's workspace) at a
  head that holds ``files``.
- ``publish(engine, files)``: a commit of the engine's current head plus ``files``
  (artifact paths only, so the stored state records are unchanged); the engine
  moves to it. ``issue(engine, execution, context, bundle)`` archives ``context``
  as ``execution``'s issued input.
- ``package(engine, root, role='research_plan', target=None)``: the legacy
  ``engine_fixtures.package``: the engine's context for one action, packaged as
  the engine packages it, and the fixed checker context written to ``root``.
- ``central_check_knowledge()``: one K record whose central check stored the
  compiler's raw output and evidence (moved from ``test_role_input``).
- ``prepare(action, direct=None, ...)``: one role input packaged from a context
  holding every key of ``SCOPED_KEYS`` (moved from ``test_role_input``'s
  ``RoleInputClassTests.prepare``); ``is_map_entry`` and the direct input shapes
  come with it.
"""
from __future__ import annotations

from pathlib import Path
import tempfile

from do_math import submission
from do_math.canonical import canonical_json
from do_math.context_store import prepare_role_input

# Fields of a stored central check beyond knowledge_fixtures.formal_result: the compiler's
# raw output and invocation, signatures and the check reference.
CENTRAL_CHECK = {'stdout': 'raw Lean output', 'stderr': 'raw Lean warnings', 'command': ['lake', 'env', 'lean', 'Check.lean'],
                 'exit_code': 0, 'declaration_signatures': {'truth': 'True'},
                 'signature_hash': 's' * 64, 'execution_id': 'EX-formal', 'artifact_ref': 'runtime/artifacts/BA-formal/formal.json'}
# What identity review and goal audit compare (계약/동일성-검토.md, 계약/목표-감사.md).
JUDGED = {'status', 'source_sha256', 'declarations', 'axioms', 'declaration_signatures', 'signature_hash',
          'toolchain', 'execution_id', 'artifact_ref'}


# Context keys the engine builds for many roles; each reaches only the roles whose contract
# or checks read it. The expectations below are those roles, from the role contracts.
SCOPED_KEYS = ('model_policy', 'resources', 'budget_unit', 'academic_requirements', 'academic_phase',
               'academic_validation', 'repetition_holds', 'goal', 'policies', 'goal_revision', 'policy_revision',
               'events', 'external_operations', 'external_rejections', 'user_inputs', 'open_questions',
               'recent_history', 'relations', 'formal_verifier', 'execution_profiles', 'role_profile_refs',
               'decisions', 'pending_revisions', 'blocked_actions')
# Derived machine files the input builds only for the scopes that inline them; elsewhere the
# records they are derived from stay readable through the record map.
DERIVED_KEYS = {'configuration_source', 'relation_validation_source'}
PLANNING_DIRECT = {'tasks': [], 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': [], 'blocked_actions': []}
INTENT_DIRECT = {'user_request': {'id': 'UI-1'}, 'interpretation_to_check': None}
OPERATIONAL_DIRECT = {'execution_to_review': {'id': 'EX-work'}, 'observation': {}, 'operational_evidence': {},
                      'admissible_basis_refs': []}


def assert_operational_documents(case, context, workspace, engine, *, owner, snapshot=None):
    """Bind document fields to one real _context/packaging result and sealed bytes."""
    import hashlib
    from support.doc_code import documents, operational_field_issues
    value = context[owner]
    snapshot = engine.head if snapshot is None else snapshot
    for document in documents(Path(__file__).resolve().parents[3]):
        case.assertEqual(operational_field_issues(document.read_text(encoding='utf-8'), owner, value), [],
                         str(document))
    target = context['execution_to_review']
    case.assertEqual(value['source_snapshot'], snapshot)
    if owner == 'operational_evidence':
        case.assertEqual(value['execution_status'], target['status'])
        sources = [value['checkpoint_source'], *value['checkpoint_files']]
        if value['checkpoint_status'] == 'preserved':
            case.assertEqual(value['checkpoint_source']['artifact_ref'], value['checkpoint']['artifact_ref'])
            case.assertEqual(value['checkpoint_source']['sha256'], value['checkpoint']['sha256'])
        else:
            case.assertIsNone(value['checkpoint_source'])
        case.assertIn('activity_continuations', value)
    elif owner == 'recovery_materials':
        case.assertFalse(context['live_review'])
        case.assertEqual(value['execution_id'], target['id'])
        bundle = 'runtime/artifacts/' + target['artifact_bundle'] + '/'
        case.assertEqual(value['result_source']['artifact_ref'], target.get('result_ref') or bundle + 'result.json')
        if value['checkpoint_source'] is not None:
            case.assertEqual(value['checkpoint_source']['artifact_ref'], bundle + 'checkpoint-recovery.json')
        sources = [value['result_source'], value['checkpoint_source'], *value['output_files']]
    else:
        raise ValueError('Unknown operational input owner: ' + owner)
    for source in sources:
        if source is None:
            continue
        case.assertEqual(source['snapshot'], snapshot)
        if 'restoration_error' in source:
            case.assertNotIn('local_path', source)
            case.assertEqual(set(source['restoration_error']),
                             {'error_type', 'reason', 'observed_sha256', 'observed_bytes'})
            case.assertTrue(source['restoration_error']['reason'])
            continue
        case.assertIn('local_path', source)
        case.assertTrue(source['local_path'].startswith('input/operational-review/' + target['id'] + '/'))
        local = (Path(workspace) / source['local_path']).resolve()
        case.assertTrue(local.is_relative_to(Path(workspace).resolve() / 'input'))
        raw = local.read_bytes()
        case.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
        case.assertEqual(len(raw), source['bytes'])
        case.assertEqual(engine.store.read(source['artifact_ref'], source['snapshot']), raw)


def assert_operational_damage_rejected(case, context, workspace, engine, *, owner):
    """Perturb copies after production; these failures are document/file checks."""
    from copy import deepcopy
    value = context[owner]
    slots = (['checkpoint_source'] if owner == 'operational_evidence' else
             ['result_source', 'checkpoint_source'])
    file_key = 'checkpoint_files' if owner == 'operational_evidence' else 'output_files'
    slots += [(file_key, index) for index in range(len(value[file_key]))]
    for slot in slots:
        source = value[slot[0]][slot[1]] if isinstance(slot, tuple) else value[slot]
        if source is None or 'restoration_error' in source:
            continue
        for fault in ('local_path', 'sha256', 'bytes'):
            damaged = deepcopy(context)
            row = damaged[owner][slot[0]][slot[1]] if isinstance(slot, tuple) else damaged[owner][slot]
            if fault == 'local_path':
                del row[fault]
            elif fault == 'sha256':
                row[fault] = '0' * 64
            else:
                row[fault] += 1
            with case.subTest(owner=owner, slot=slot, fault=fault), case.assertRaises(AssertionError):
                assert_operational_documents(case, damaged, workspace, engine, owner=owner)
    other = 'recovery_materials' if owner == 'operational_evidence' else 'operational_evidence'
    if other in context:
        swapped = deepcopy(context)
        swapped[owner] = swapped[other]
        with case.subTest(owner=owner, fault='other_owner'), case.assertRaises(AssertionError):
            assert_operational_documents(case, swapped, workspace, engine, owner=owner)


def is_map_entry(value):
    """A context key given as a map entry: its exact catalog source and item count, not its content."""
    return isinstance(value, dict) and set(value) == {'source_ref', 'total'}


def prepare(action, direct=None, *, instance=None, runtime=None, extra=None, root=None, snapshot='a' * 40,
            install=False):
    """One role input whose engine context held every scoped key.

    Returns the packaged context, or with ``root`` the whole prepared input in that workspace.
    ``install`` also installs the submission and read tools, as the engine does.
    """
    from support.entry import entry
    _entry = entry()
    if instance is None:
        from support.record_builders import surface_state
        instance, runtime = surface_state()
    profile = next(p for p in instance['execution_profiles'].values() if p['role'] == action['role'])
    context = {key: [] for key in SCOPED_KEYS}
    context.update(action={'id': 'AC-scope', **action}, **(direct or {}), **(extra or {}))

    def run(workspace):
        return prepare_role_input(context, instance=instance, runtime=runtime, role=action['role'],
            profile=profile, snapshot=snapshot, workspace=workspace, activity_id='AC-1',
            install_submission_tools=install, max_artifact_bytes=100000 if install else None, clock=_entry.ports.clock)
    if root is not None:
        return run(root)
    with tempfile.TemporaryDirectory() as directory:
        return run(Path(directory))['context']


def context_state(instance=None, runtime=None):
    """``(instance, runtime)``: the legacy ``context_engine`` state, as plain records."""
    from support.record_builders import surface_state
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
    return base, running


def publish(engine, files):
    """Publish artifact ``files`` on top of the engine's head and move the engine there.

    Only new ``runtime/artifacts/`` paths are accepted (the store's immutable
    artifact rule is real), so the stored state records stay as they were.
    """
    if not all(path.startswith('runtime/artifacts/') for path in files):
        raise ValueError('publish takes artifact paths only')
    engine.head = engine.store._store.publish(engine.head, dict(files)).head
    return engine.head


def issue(engine, execution, context, bundle, schema=None):
    """Archive ``context`` (and ``schema``) as the issued input of ``execution`` below ``bundle``."""
    prefix = 'runtime/artifacts/' + bundle + '/'
    files = {prefix + 'input/submission/context.json': canonical_json(context)}
    if schema is not None:
        files[prefix + 'schema.json'] = canonical_json(schema)
    publish(engine, files)
    execution['input_bundle'] = bundle
    return execution


def context_engine(instance=None, runtime=None, files=None):
    """The engine of a restored Sim over ``context_state(instance, runtime)``, at a head holding ``files``."""
    from support.sim import Sim
    engine = Sim.activated().engine
    if files:
        publish(engine, files)
    workspace = engine.instance['workspace']
    engine.instance, engine.runtime = context_state(instance, runtime)
    engine.instance.setdefault('workspace', workspace)
    return engine


def package(engine, root, role='research_plan', target=None):
    """``(prepared input, fixed checker context)`` of one ``role`` action, packaged into ``root``."""
    action = {'id': 'AC-plan', 'role': role}
    if target:
        action['target'] = target
    context = engine._context(action, root, execution_id='EX-plan')
    profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == role)
    result = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime, role=role,
        profile=profile, snapshot=engine.head, workspace=root, activity_id='AC-1',
        install_submission_tools=True, artifact_prefix='runtime/artifacts/BA-plan', clock=engine.ports.clock)
    fixed = submission.load_json((root / 'input/submission/context.json').read_bytes())
    return result, fixed


def damage(store, path, raw):
    """Point the instance ref at a copy of its head whose ``path`` holds ``raw``, as damage from outside do-math.

    ``store`` is a ``ResearchRepository``. The commit is written by the state
    store's own tree and commit writers through the Git port and the ref moves
    by the port's compare-and-swap; only the publication rules (the immutable
    artifact bundles) are not applied, since no do-math writer made this change.
    Returns the damaged head.
    """
    state = store._store
    head = state.read_snapshot().head
    tree, _ = state._write_tree(state._tree(head).directories, {path: raw})
    commit = state._write_commit(tree, head)
    if not state._backend.update_ref(state.repository, state.ref, commit, head):
        raise AssertionError('the instance ref moved while the damage was written')
    return commit


def record_contexts(sim, responder=None):
    """Give ``sim`` a model double that also keeps ``(role, context)`` of every call in ``contexts``.

    The context is what the worker's model read from its actual prompt
    (``runner_fixtures.context_from``); ``prompts`` holds ``(role, context,
    prompt)`` with the raw prompt text the provider CLI received on its input.
    ``responder`` replaces the default responder (``support.default_responder.DefaultResponder()``),
    for example a formal one.
    """
    from copy import deepcopy
    from pathlib import Path
    from support.model import FakeCLI, ModelDouble

    class PromptRecordingCLI(FakeCLI):
        def communicate(self, input=None, timeout=None):
            self.model.received = input.decode('utf-8')
            try:
                return super().communicate(input, timeout)
            finally:
                self.model.received = None

    class ContextRecordingModel(ModelDouble):
        def __init__(self, clock, responder=None):
            super().__init__(clock, responder)
            self.contexts, self.prompts, self.received = [], [], None

        def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
                  creationflags=0):
            return PromptRecordingCLI(self, list(command), stdout, stderr, Path(cwd))

        def output(self, role, ctx, workspace):
            self.contexts.append((role, deepcopy(ctx)))
            self.prompts.append((role, deepcopy(ctx), self.received))
            return super().output(role, ctx, workspace)
    sim.model = ContextRecordingModel(sim.clock, responder)
    return sim.model


class GitBatches:
    """Count the Git port's batch reads (``object_info``, ``read_objects``) while the context is open.

    The real backend (``git_process.GitProcess``) runs one ``git cat-file``
    process per call with specs, so ``count`` is the number of those processes
    the same code would start. The fake's methods are restored on exit.
    """

    def __init__(self, backend):
        self.backend, self.calls = backend, []

    def __enter__(self):
        for name in ('object_info', 'read_objects'):
            original = getattr(self.backend, name)

            def counted(repository, specs, name=name, original=original):
                if specs:
                    self.calls.append((name, list(specs)))
                return original(repository, specs)
            setattr(self.backend, name, counted)
        return self

    def __exit__(self, *exc):
        for name in ('object_info', 'read_objects'):
            delattr(self.backend, name)
        return False

    @property
    def count(self):
        return len(self.calls)


def central_check_knowledge():
    """``(instance, runtime, kid, stored verification)``: one K record whose check stored raw output and evidence."""
    from support.knowledge_builders import verified_knowledge
    from support.record_builders import surface_state
    instance, runtime = surface_state()
    evidence, _, kid, _ = verified_knowledge(check=CENTRAL_CHECK)
    instance.update(evidence)
    verification = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]['verification']
    return instance, runtime, kid, verification
