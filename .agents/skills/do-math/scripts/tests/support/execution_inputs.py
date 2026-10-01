"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from pathlib import Path
from do_math.canonical import canonical_json
from support.role_answers import seal_response


IDENTITY = {"host": "CORE_TESTS synthetic host", "implementation": "CORE_TESTS synthetic adapter"}


def dispatched_launch(execution_id, profile, *, jobs, clock):
    """The current explicit runner contract used by native boundary fixtures."""
    from do_math.launch import ticket
    value = ticket(execution_id, profile, clock=clock, jobs=jobs)
    value['phase'] = 'dispatched'
    return value


def sealed_maintenance_submission(workspace, execution_id):
    """Create real central seal bytes for lifecycle/storage fixture assertions."""
    from support.entry import entry
    _entry = entry()
    from do_math import contracts, submission
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    context = {'action': {'id': 'AC-fixture', 'role': 'maintenance'},
               'execution_id': execution_id, 'snapshot': 'fixture-input',
               'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {}}
    schema = contracts.schema_for('maintenance')
    submission.install_tools(workspace, context, schema, None, clock=_entry.ports.clock)
    output = {'summary': 'Inspect fixture', 'used_sources': [], 'questions': [],
              'report': 'Explicit synthetic maintenance output.', 'remaining_work': []}
    seal_response(output, context, workspace)
    (workspace / 'draft.json').write_bytes(canonical_json(output))
    sealed = submission.seal_submission(workspace, 'draft.json', execution_id=execution_id,
        context=context, schema=schema, max_artifact_bytes=1024*1024, clock=_entry.ports.clock)
    if not sealed['passed']:
        raise AssertionError(sealed['check']['issues'])
    prefix = 'runtime/artifacts/BA-fixture-submission/'
    return ({**sealed['intent'], 'output_ref': prefix + 'output.json'},
            {prefix + path: raw for path, raw in sealed['artifacts'].items()})
