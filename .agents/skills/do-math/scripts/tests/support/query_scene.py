"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from pathlib import Path
import tempfile
from do_math.repository import ResearchRepository


QUERY_INSTANCE_ID = "RI-00000000000000000000000000"


def start_query_repository(test):
    """Give ``test`` a published instance ``QUERY_INSTANCE_ID`` with two knowledge records and a relation.

    Sets ``root``, ``git`` (the repository), ``workspace``, ``repository``,
    ``initial_head``, ``kids`` (definition "One", theorem "Two"), ``relation_id``
    (One supports Two, through the installed kind definition), ``old_head`` (that
    state) and ``file_head`` (two more query-fixture artifacts).
    """
    from support.entry import entry
    _entry = entry()
    from do_math.wiring import real_ports
    _entry.ports = real_ports(environment=_entry.environment)
    import tempfile
    from do_math.engine import initialize
    from do_math.knowledge_io import import_candidate, import_relation
    from do_math.repository import ResearchRepository
    from support.fakes.git_backend import make_repository
    test.root = Path(test.enterContext(tempfile.TemporaryDirectory()))
    test.git = make_repository(test.root / "git")
    test.workspace = test.root / "workspace"
    initialized = initialize(test.git, goal="A goal", workspace=test.workspace, instance_id=QUERY_INSTANCE_ID,
                             config={"operator_enabled": False, "scholarly_enabled": False}, codex_home=_entry.codex_home, host_id=_entry.host_id, ports=_entry.ports)
    test.repository = ResearchRepository(test.git, QUERY_INSTANCE_ID, backend=_entry.ports.git_backend, clock=_entry.ports.clock)
    test.initial_head = initialized["snapshot"]
    head, instance, runtime = test.repository.load(test.initial_head)
    if head != test.initial_head:
        raise AssertionError('The initialized head did not load as itself')
    test.kids = []
    for title, kind, summary in (("One", "definition", "alpha"), ("Two", "theorem", "beta")):
        instance, runtime, kid = import_candidate(instance, runtime,
            {"kind": kind, "title": title, "statement": summary, "summary": summary,
             "explanation": "Explicit query fixture: " + summary, "lean_code": "",
             "declaration_names": [], "dependencies": []}, source_ref=QUERY_INSTANCE_ID, actor_ref=QUERY_INSTANCE_ID, clock=_entry.ports.clock)
        test.kids.append(kid)
    instance, test.relation_id = import_relation(instance,
        {"kind": "supports", "source": test.kids[0], "target": test.kids[1], "evidence": "alpha"},
        source_ref=QUERY_INSTANCE_ID, actor_ref=QUERY_INSTANCE_ID, clock=_entry.ports.clock)
    test.old_head = test.repository.save_with_state(test.initial_head, instance, runtime)[0]
    test.file_head = test.repository.save_with_state(test.old_head, instance, runtime, artifacts={
        "runtime/artifacts/query-fixture/a.txt": b"needle alpha",
        "runtime/artifacts/query-fixture/b.txt": b"needle beta",
    })[0]
