"""Receiver scenes of the submission region on a Sim's engine and store.

The legacy flow tests started from ``engine_fixtures.start_submission_history``
(an engine over the synthetic 2-stage active state) or from in-memory engine
doubles with replaced methods. These scenes start from a restored Sim: the
engine is the real ``ResearchEngine``, its store the real ``ResearchRepository``
over the Git port fake, and nothing is replaced. Where the legacy scene put
records on the engine, the scene makes them with the engine's own registration
and saves them, so every later step reads published state.

- ``history()``: the legacy ``start_submission_history``: a running maintenance
  execution ``EX-history`` whose sealed input bundle ``BA-history-input`` is
  published, with the submission tools installed in its workspace and a control
  binding on its own transport. Returns a ``Scene`` (``sim``, ``engine``,
  ``action``, ``workspace``, ``context``, ``schema``, ``transport``, ``binding``
  and a valid sealed ``output``); ``scene.engine`` follows ``sim.engine``.
- ``research()``: the legacy ``PartialCaptureGitTests`` start: a running research
  work execution ``EX-partial`` on the planned task ``TK-partial`` whose contract
  review approved it, with its decision basis, issued input and tools.
- ``submit(scene, request_id, raw)``: ``raw`` as the execution's draft, delivered
  as a submission intent through the transport to the engine's receiver;
  returns ``(request, receipt)`` (legacy ``engine_fixtures.submit_history``).
- ``receive(scene)``: the owner's receipt of the sealed submission, as the call
  collection applies it (``_receive_submission`` with ``preserved=True``).
- ``held_ref(sim)``: while open, the instance ref's ``.lock`` file exists, as
  while another Git writer updates the ref, so a publication's compare-and-swap
  fails and nothing is published.
- ``order(**functions)``: ``ObservedCalls`` whose captures append to ``calls.order``,
  in the order the calls started, each name with the observed calls still running
  around it (so a call nested inside another observed call shows it).
- ``native_result(sim, execution, context, raw, workspace)``: the legacy
  ``engine_fixtures.native_result`` (pure provider protocol evidence of a
  finished native final) with the launch ticket drawn from the Sim's Jobs and
  clock ports instead of the host's Windows Job and system clock.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path

from do_math import contracts, submission
from do_math.canonical import canonical_json
from do_math.control_transport import ControlTransport
from support.provider_probes import ObservedCalls
from support.sim import Sim

PREFIX = 'runtime/artifacts/BA-history-input/'


class Scene:
    def __init__(self, sim, **fields):
        self.sim = sim
        self.__dict__.update(fields)

    @property
    def engine(self):
        return self.sim.engine


def _issue_input(engine, execution, context, schema, bundle, prompt=None):
    """Publish ``context`` and ``schema`` as ``execution``'s sealed input bundle, with the engine's save."""
    prefix = 'runtime/artifacts/' + bundle + '/'
    files = {prefix + 'input/submission/context.json': canonical_json(context),
             prefix + 'schema.json': canonical_json(schema)}
    if prompt is not None:
        files[prefix + 'input.txt'] = prompt
    engine._save(files)


def history(*, bound=False):
    """``bound`` puts the control binding into the issued and installed context, as the engine does for a
    worker, so the installed tool itself can send the draft (the legacy scene sent it for the worker)."""
    from do_math.planning import governance_revisions
    from support.role_answers import seal_response
    sim = Sim.activated()
    engine = sim.engine
    action = {'id': 'AC-history', 'role': 'maintenance'}
    engine._action_lifecycle_gate(action)
    execution = engine._register_execution(action, {'id': 'EX-history', 'role': 'maintenance', 'status': 'running'})
    # A sealed role input names its prompt in the input manifest; the prompt is archived below.
    prompt = b'Synthetic history prompt'
    execution.update(grant_id=action['grant_id'], input_bundle='BA-history-input', input_snapshot=engine.head,
                     input_manifest={'prompt': {'artifact_ref': PREFIX + 'input.txt',
                                                'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}})
    execution.update(governance_revisions(engine.instance))
    workspace = Path(engine.instance['workspace']) / 'runs/EX-history/workspace'
    workspace.mkdir(parents=True)
    context = {'action': action, 'execution_id': execution['id'], 'snapshot': engine.head,
               'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {},
               'grants': [deepcopy(engine.instance['grants'][action['grant_id']])]}
    transport = ControlTransport(sim.root / 'delivery', clock=sim.clock)
    binding = transport.issue('EX-history', action['grant_id'], workspace=workspace)
    if bound:
        context['control_binding'] = binding
    schema = contracts.schema_for('maintenance')
    submission.install_tools(workspace, context, schema, 1024 * 1024, clock=sim.clock)
    _issue_input(engine, execution, context, schema, 'BA-history-input', prompt)
    output = {'summary': 'Exact é diagnostic', 'used_sources': [], 'questions': [],
              'report': 'Actual central receipt test; no mathematical approval.', 'remaining_work': []}
    seal_response(output, context, workspace)
    return Scene(sim, action=action, execution_id='EX-history', workspace=workspace, context=context, schema=schema,
                 transport=transport, binding=binding, output=output)


def research():
    from do_math import knowledge_io, planning
    from do_math.input_basis import capture_decision_basis
    from support.record_builders import approve_contract
    from support.record_builders import two_observation_output
    from support.role_answers import candidate
    sim = Sim.activated()
    engine = sim.engine
    action = {'id': 'AC-partial', 'role': 'research_work'}
    engine._action_lifecycle_gate(action)
    execution = engine._register_execution(action, {'id': 'EX-partial', 'role': 'research_work', 'status': 'running'})
    wire = candidate()
    wire['profile_refs'] = [execution['execution_profile_ref']]
    wire['authority_refs'] = [action['grant_id']]
    task = contracts.task_candidate_record(wire, task_id='TK-partial')
    task.pop('revises_task_id', None)
    task.update(status='planned', results=[], reviews=[], occurrence_condition={'op': 'always'})
    engine.runtime['tasks'][task['id']] = task
    reviewer = {'id': 'AC-review', 'role': 'task_contract_review', 'target': task['id']}
    engine._register_execution(reviewer, {'id': 'EX-review', 'role': 'task_contract_review', 'status': 'running'})
    approve_contract(engine.instance, engine.runtime, task)
    action['target'] = task['id']
    execution['action']['target'] = task['id']
    execution['contract_sha256'] = planning.contract_hash(task)
    engine._save()
    execution = engine.runtime['executions']['EX-partial']
    execution.update(grant_id=action['grant_id'], input_bundle='BA-partial-input', input_snapshot=engine.head,
        decision_basis=capture_decision_basis(engine.instance, engine.runtime, []),
        **planning.governance_revisions(engine.instance))
    workspace = Path(engine.instance['workspace']) / 'runs/EX-partial/workspace'
    workspace.mkdir(parents=True)
    context = {'action': action, 'execution_id': 'EX-partial', 'snapshot': engine.head,
               'tasks': [deepcopy(task)], 'sources': [], 'knowledge_catalog': [],
               'kind_definitions': knowledge_io.catalog_definitions(engine.instance),
               'grants': [deepcopy(engine.instance['grants'][action['grant_id']])]}
    schema = contracts.action_schema(action)
    submission.install_tools(workspace, context, schema, None, clock=sim.clock)
    _issue_input(engine, execution, context, schema, 'BA-partial-input')
    transport = ControlTransport(sim.root / 'delivery', clock=sim.clock)
    binding = transport.issue('EX-partial', action['grant_id'], workspace=workspace)
    output = two_observation_output()
    return Scene(sim, action=action, execution_id='EX-partial', task=task, workspace=workspace, context=context,
                 schema=schema, transport=transport, binding=binding, output=output)


def submit(scene, request_id, raw, draft='draft.json'):
    (scene.workspace / draft).write_bytes(raw)
    request = {**scene.binding, 'request_id': request_id, 'kind': 'submit_intent', 'payload': {'draft_path': draft}}
    return request, scene.transport.receive(request, publish=scene.engine._publish_control_request)


def receive(scene):
    return scene.engine._receive_submission(scene.action, {}, scene.execution_id, scene.context, scene.schema,
                                            scene.workspace, preserved=True)


@contextmanager
def held_ref(sim):
    store = sim.engine.store._store
    lock = Path(store.git_dir) / (store.ref + '.lock')
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_bytes(b'')
    try:
        yield lock
    finally:
        os.unlink(lock)


def order(**functions):
    """``ObservedCalls`` of ``functions``; ``calls.order`` lists ``(name, enclosing)`` in the order the calls started.

    ``enclosing`` is the tuple of the other observed names still running when the
    call started (their frames are on the stack), so a call that starts only after
    another returned has ``()``, and one made from inside it names it.
    """
    import inspect
    import sys
    codes = {inspect.unwrap(getattr(function, '__func__', function)).__code__: name
             for name, function in functions.items()}
    sequence = []

    def recorder(name):
        def record(arguments):
            enclosing, frame = [], sys._getframe(1)
            while frame is not None:
                other = codes.get(frame.f_code)
                if other is not None and other != name:
                    enclosing.append(other)
                frame = frame.f_back
            sequence.append((name, tuple(reversed(enclosing))))
            return dict(arguments)
        return record
    calls = ObservedCalls(capture={name: recorder(name) for name in functions}, **functions)
    calls.order = sequence
    return calls


def native_result(sim, execution, context, raw, workspace):
    from do_math.codex_adapter import _artifact
    from do_math.launch import ticket
    execution['launch_ticket'] = {**ticket(execution['id'], {'sha256': execution['execution_profile_ref']['sha256'],
        'actor_kind': 'ai', 'role': execution.get('role', 'maintenance')}, jobs=sim.ports.jobs, clock=sim.clock),
        'phase': 'finished'}
    prompt = b'exact sealed prompt'
    request = {'execution_id': execution['id'], 'profile_ref': execution['execution_profile_ref'],
        'cwd': str(workspace), 'codex_path': 'fixture-cli',
        'control_binding': {'execution_id': execution['id'], 'grant_id': execution['grant_id']}}
    request_raw = json.dumps(request).encode()
    identity = {'request_sha256': hashlib.sha256(request_raw).hexdigest(),
        'pid': 123, 'creation_filetime': 134345064658094591, 'job_name': execution['launch_ticket']['job_name'],
        'execution_id': execution['id'], 'profile_ref': execution['execution_profile_ref']}
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
