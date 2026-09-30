"""The worker-side scenes of the submission region: tools, transport and a publisher without an engine, and producer checks.

The legacy ``test_submission_tools.LocalControlProtocolTests`` set this up in its
``setUp`` over a real Git repository and the system clock. ``ProtocolScene(root)``
builds the same scene on the Git port's in-process fake (the real
``GitStateStore``) and a fake clock:

- ``workspace`` (``root/worker``) with the submission tools installed for a
  maintenance context whose ``control_binding`` is the transport's binding for
  ``EX-worker`` and ``GR-worker``; ``draft`` (``.scratch/draft.json``) holds the
  sealed valid ``output``.
- ``store`` (a ``GitStateStore`` at ``root/repo``), ``head`` (``None`` until a
  publication), ``transport`` (``root/delivery``), ``binding``, ``context``,
  ``schema`` and ``clock``.
- ``publish_intent(request)``: the central publisher double of the legacy test.
  It seals the request's draft with the product's ``seal_submission``, publishes
  the sealed artifacts and the check under ``runtime/artifacts/<request ID>/``
  (the first publication also carries ``research/transport-fixture.json``) and
  answers ``rejected`` (with the check) when the seal did not pass, otherwise
  ``accepted`` with the new head. A rejected draft's artifacts are published too.
- ``mcp(case, name, arguments)``: one ``tools/call`` request to the product's MCP
  control server, run as its own child process with ``mcp_server_config(binding)``;
  ``case`` asserts that it exits 0 without a JSON-RPC error, and the tool's JSON
  result is returned.

The producer's side of the legacy ``ProducerToolTests`` (its ``prepare`` and ``check_output``):

- ``producer_workspace(root, role='research_preparation', context_values=None,
  max_artifact_bytes=None)``: a new workspace ``root/<role>-producer-<n>`` with the
  tools installed for a fixed producer context of ``role`` (action ``AC-producer``,
  execution ``EX-producer``, the ontology's kind definitions), updated with
  ``context_values``; returns ``(workspace, context)``. The installed context must
  carry the executable check (``submission_contract`` with its command).
- ``check_output(case, workspace, context, output, extension=None, process=False)``:
  one run of the installed check on a copy of ``output`` (sealed unless it
  declares its bundles) written to ``.scratch/submission.json``, with
  ``extension`` as ``activity-extensions.json`` when given. It runs the launcher's
  ``submission_tool.main(["--output", draft])`` in this process with the workspace
  as the working directory, or with ``process`` the installed command in a child
  interpreter, as the producer does. ``case`` asserts that the exit code is 0 or 1
  and says whether the check passed, and that the draft still holds the author's
  output; returns the check record the tool printed.
"""
from __future__ import annotations

import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess

from do_math import contracts, submission
from do_math.canonical import canonical_json
from do_math.control_server import mcp_server_config
from do_math.control_transport import ControlTransport
from do_math.git_store import GitStateStore
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake, make_repository

INSTANCE_ID = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'


class ProtocolScene:
    def __init__(self, root, *, clock=None):
        from research_fixtures import seal_response
        self.root = Path(root)
        self.clock = clock or FakeClock()
        self.workspace = self.root / 'worker'
        self.workspace.mkdir()
        self.store = GitStateStore(make_repository(self.root / 'repo'), INSTANCE_ID, backend=make_fake(),
                                   clock=self.clock)
        self.head = None
        self.transport = ControlTransport(self.root / 'delivery', clock=self.clock)
        self.binding = self.transport.issue('EX-worker', 'GR-worker', workspace=self.workspace)
        self.context = {'action': {'role': 'maintenance', 'id': 'AC-worker'}, 'execution_id': 'EX-worker',
                        'control_binding': self.binding, 'snapshot': 'fixed', 'tasks': [], 'knowledge_catalog': [],
                        'sources': [], 'kind_definitions': {}}
        self.schema = contracts.schema_for('maintenance')
        submission.install_tools(self.workspace, self.context, self.schema, None, clock=self.clock)
        self.output = {'summary': 'Inspect only', 'used_sources': [], 'questions': [], 'report': 'Inspected',
                       'remaining_work': []}
        seal_response(self.output, self.context, self.workspace)
        self.draft = self.workspace / '.scratch/draft.json'
        self.draft.parent.mkdir()
        self.draft.write_bytes(canonical_json(self.output))

    def publish_intent(self, request):
        sealed = submission.seal_submission(self.workspace, request['payload']['draft_path'], execution_id='EX-worker',
                                            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024,
                                            clock=self.clock)
        changes = {'runtime/artifacts/' + request['request_id'] + '/' + name: data
                   for name, data in sealed['artifacts'].items()}
        if self.head is None:
            changes['research/transport-fixture.json'] = canonical_json({'scope': 'transport evidence only'})
        changes['runtime/artifacts/' + request['request_id'] + '/receipt-check.json'] = canonical_json(sealed['check'])
        self.head = self.store.publish(self.head, changes).head
        if not sealed['passed']:
            return {'state': 'rejected', 'reason': 'Draft validation failed', 'result': sealed['check']}
        return {'state': 'accepted', 'published': True, 'snapshot': self.head}

    def mcp(self, case, name, arguments):
        server = mcp_server_config(self.binding)
        request = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': name, 'arguments': arguments}}
        process = subprocess.run([server['command'], *server['args']], input=json.dumps(request) + '\n', text=True,
                                 capture_output=True, timeout=30)
        case.assertEqual(0, process.returncode, process.stderr)
        envelope = json.loads(process.stdout)
        case.assertNotIn('error', envelope)
        return json.loads(envelope['result']['content'][0]['text'])


def producer_workspace(root, role='research_preparation', *, context_values=None, max_artifact_bytes=None):
    from do_math import knowledge_io
    root = Path(root)
    workspace = root / (role + '-producer-' + str(len(list(root.glob(role + '-producer-*')))))
    workspace.mkdir(exist_ok=True)
    context = {'action': {'id': 'AC-producer', 'role': role}, 'execution_id': 'EX-producer',
               'snapshot': 'fixed-producer-input', 'observed_at': '2026-09-23T00:00:00Z',
               'budget_unit': 'concurrent_sessions', 'tasks': [], 'ready_task_ids': [], 'knowledge_catalog': [],
               'sources': [], 'kind_definitions': knowledge_io.catalog_definitions(knowledge_io.ensure_ontology({}))}
    context.update(context_values or {})
    submission.install_tools(workspace, context, contracts.action_schema(context['action']), max_artifact_bytes,
                             clock=FakeClock())
    if 'submission_contract' not in context or not context['submission_contract']['command']:
        raise AssertionError('the producer needs an executable check, fixed inputs and limits')
    return workspace, context


def check_output(case, workspace, context, output, extension=None, *, process=False):
    from do_math import submission_tool
    from research_fixtures import seal_response
    output = deepcopy(output)
    draft = workspace / '.scratch/submission.json'
    draft.parent.mkdir(exist_ok=True)
    if extension is not None:
        (workspace / 'activity-extensions.json').write_bytes(canonical_json(extension))
    if 'integration_bundles' not in output:
        seal_response(output, context, workspace)
    draft.write_bytes(canonical_json(output))
    if process:
        command = [*context['submission_contract']['command'], '--output', str(draft)]
        run = subprocess.run(command, cwd=workspace, capture_output=True, timeout=30)
        code, printed, errors = run.returncode, run.stdout, run.stderr.decode('utf-8', 'replace')
    else:
        stdout = io.StringIO()
        with contextlib.chdir(workspace), contextlib.redirect_stdout(stdout):
            code = submission_tool.main(['--output', str(draft)])
        printed, errors = stdout.getvalue(), ''
    case.assertIn(code, (0, 1), errors)
    result = json.loads(printed)
    case.assertEqual(code == 0, result['passed'])
    case.assertEqual(json.loads(draft.read_bytes()), output, "a validator cannot rewrite the author's meaning")
    return result
