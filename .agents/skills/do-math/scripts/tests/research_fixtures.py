"""Shared test fixtures: synthetic inputs, process helpers and shared starting states.

All authority and persistence still pass through the engine. The adapter and
Lean facts here are synthetic test evidence. They do not establish host
capabilities, a real compiler result, or approval by the actual user.

Fixture modules
===============
A test module takes its fixtures from these modules, never from another test
module. Each module's docstring lists what it holds.

- ``research_fixtures`` (this module): inputs every area uses (task
  candidates, review outputs, charters and their approval, trust environments,
  observation rules, clocks and batches), the in-process ``git_init``,
  ``run_cli`` and ``cli_result``, public activation (``activate``), what a
  prepared role input lets its role reach (``role_reach``) and the shared
  starting states below.
- ``state_fixtures``: the validated synthetic active state (``active_instance``,
  ``active_repository``, ``start_active_copy``) and the owner-loop helpers
  (``owner_calls``, ``start_model_call``).
- ``engine_fixtures``: engine doubles over in-memory state (``FakeEngine``,
  ``routing_engine``, ``context_engine``) and Git-backed engine start states
  (``start_submission_history``, ``start_query_repository``).
- ``runner_fixtures``: ``ScriptedRunner`` and the role outputs it writes.
- ``purpose_fixtures``: the purpose scenario (``PurposeRunner``), its harnesses
  and the builds that drive it.
- ``record_fixtures``: records for pure domain functions (governance, task
  contracts, submissions).
- ``knowledge_fixtures``: knowledge candidates and their synthetic formal evidence.
- ``review_fixtures``: identity review doubles, cycles and harnesses.
- ``provider_fixtures``: provider adapters, host resources and external services.

A fixture that one test module uses stays in that module as a module function.
Before a second module uses it, it moves to the fixture module of its area.

Shared starting states
======================

Building an active instance through the public path (``activate``: several
controls plus two interpretation executions) costs tens of seconds, and a Git
or CLI child process costs a noticeable fraction of a second. A test whose
subject comes after that path starts from a copy of a state built once per
process instead.

What to use
-----------
``restore_template(build, **parameters)`` returns ``(root, value)``. The first
call in a process runs ``build(root, shared, **parameters)`` once. Every call,
the first included, then gives a fresh copy of exactly the bytes that build
left under ``root``: Git objects and refs, the workspace with its ``runs/``
outputs and the control inbox, as the product published them. ``value`` is a
deep copy of what the build returned. Every build puts the repository at
``root / 'repository'`` and the workspace at ``root / 'work-0'``. These builds
are shared (keywords in parentheses):

- ``state_fixtures.active_instance`` (``config``, ``external_policy``,
  ``review_policy``): the validated synthetic active state assembled with
  ``engine_fixtures.FakeEngine``, without interpretation executions;
  returns the instance ID.
- ``activated_instance`` (``goal``, ``config``, ``external_policy``,
  ``review_policy``): public ``initialize`` plus ``activate``, the published
  state before the first research step; returns the instance ID.
- ``engine_fixtures.initialized_instance`` (``goal``, ``config``): the public
  ``initialize`` alone; returns the instance ID.
- ``purpose_fixtures.solved_instance`` (``criteria``): public activation driven
  by the purpose scenario to the mathematical solution, with academic
  requirement ``writeup`` approved first when ``criteria`` is a list; returns
  ``{'instance_id', 'head', 'work_order'}``.
- ``purpose_fixtures.purpose_state`` (``config``, ``until``,
  ``review_policy``, ``external_policy``, ``signed``): the synthetic active
  state driven until task ``A``'s work is queued (``until='prepared'``) or its
  identity review opens (``'review'``); returns the instance ID.
- ``purpose_fixtures.assessment_preparation_instance`` (``config``): two
  academic tasks of requirement ``r`` awaiting model assessment; returns the
  instance ID.

The other builds serve one test module each and stay there, each with its
state in its docstring: ``requirement_change_instance`` (``test_academic_engine``),
``cli_instance`` (``test_cli``), ``created_instance`` (``test_cli_advanced``),
``plan_ready_instance`` (``test_currentness``), ``efficiency_instance``
(``test_engine``), ``overflowed_maintenance`` (``test_input_recovery``),
``rejected_assessment_instance`` (``test_model_assessment_flow``),
``reviewed_task``, ``parked_failed_plan`` and ``paused_limited_recovery``
(``test_research_recovery``), ``ready_work`` (``test_session_scheduler``),
``waiting_action`` (``test_stop_flags``) and ``prepared_tasks``
(``test_submission_boundaries``).

Then ``ResearchEngine(root / 'repository', instance_id, runner=..., formal_verifier=...)``
with a new runner. ``purpose_fixtures.ActivatedPurposeHarness`` wraps the first
two as ``make_active`` and ``make``. ``test_engine.EngineTests.active`` is the
plain form.

Two process helpers replace a child process where the process is not examined:
``git_init(path)`` for ``git init -q <path>`` and ``run_cli(*arguments, cwd=...)``
for ``python do_math.py *arguments`` (a ``CompletedProcess`` with text output).

Rules of a copy
---------------
- ``root`` is the same path for every copy of one template; that keeps the
  absolute paths in the state, and the hashes over them, true. A call replaces
  the previous copy, so a test finishes with one engine before asking for the
  next. A test may add instances to the copied repository itself.
- Parameters are JSON values, and every value that shapes the built state is
  one: goal, config, policies. Set configuration here rather than with a later
  ``configure`` control, which makes new profile editions that need new
  capability evidence. Defaults count, so omitting one names the same template.
- Process-local engine state is not in a copy; set it on the new engine:
  ``_task_readiness`` is empty until ``run`` (call ``_refresh_readiness()`` to
  read it before), and clock or method patches (``lifecycle_clock``,
  ``_solution_basis``) apply to the object they were set on.
- A template lives in one process and is never reused from disk: it carries
  the installed edition, grant expiries (one day after the build) and the
  clock high-water. A test whose rule depends on time elapsed since the build
  uses the public path.
- The build runs inside the first test that asks for it, and a failed build
  fails every later test that asks for the same template.

Writing a build
---------------
``build(root, shared, **parameters)`` creates everything the state names under
``root``, except files whose stat fingerprint the state records, such as
``trust_fixture`` toolchains and records: a copy gets a new creation time, so
those go under ``shared``, which is never copied or cleared and must only be
read afterwards. A deeper state is a build that starts from a ready build on
its own ``root`` (for example ``activated_instance(root, shared, ...)``) and
then drives an engine with a scripted runner; it returns whatever the tests
need (instance IDs, a task's copy before a change, an execution ID). End the
build where no execution is unfinished and nothing is reserved: an executor
started on the copy recovers every unfinished execution. A test that needs a
running call copies the state before it and starts the call itself. Formal
checks on the synthetic state need ``lean_command=list(state_fixtures.ACTIVE_LEAN_COMMAND)``
in its config; public activation registers the configured command itself.

When to keep the public path or the child process
--------------------------------------------------
Keep the public path when the test's subject is that path: initialization,
activation gates, the interpretation check, probes or trust registration
during initialization, or the end-to-end connection the dedicated tests keep
(``test_engine.EngineTests.test_public_initialization_reaches_active_with_distinct_interpretation``,
``test_engine.PublicGitFlow.test_public_activation_work_receipt_assessment_and_next_plan``, and
the ``purpose_fixtures.solved_instance`` build, which ``test_purpose_engine.SolvedPurposeTests``
reads).
Keep it too when the test patches or counts something during activation, or
reads process-local engine state activation leaves behind. The check: if
activation broke while still publishing the same final state, should this
test fail? If yes, it examines the path.

Keep the child process when the process is the subject: exit codes as the
shell sees them, stdout/stderr encoding, ``pythonw``, Windows Jobs, owner
identity of another process, background or detached processes, and the
interpreter's start-up (imports, ``sys.path``, installation freezing). A lock
held by another descriptor in the same process conflicts as across processes
(``file_io.os_lock``), so lock contention alone does not need a child.

When a scenario may stop early
------------------------------
A ``drive``/``run`` loop may stop at the first state in which every asserted
value is final: its predicate is what the assertions read. Before stopping
early, confirm that nothing after that point adds to an asserted count
("exactly N reviews") and that no fixture check that only runs later is lost
(a scripted role that raises on a wrong input is a check). Drive to the goal
when the goal judgment is asserted, is the test's stated claim (its name or
docstring), or feeds such a fixture check.
"""
from __future__ import annotations

from types import SimpleNamespace
import atexit
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
from unittest.mock import patch

from do_math.contracts import CONTRACT_REVIEW_ITEMS, ROLES
from do_math.control_transport import ControlTransport
from do_math.execution_profiles import profile_ref
from do_math.file_io import sha256_file
from do_math.repository import canonical_json

IDENTITY = {"host": "CORE_TESTS synthetic host", "implementation": "CORE_TESTS synthetic adapter"}
from do_math.trust_validation import AXIOMS


def clock_ports(**overrides):
    """A Ports bundle whose clock is the real clock with the named operations replaced.

    Legacy tests that move one clock (usually ``monotonic``) and keep the rest real
    set ``engine.ports = clock_ports(monotonic=...)``.
    """
    from do_math.ports import Ports
    from do_math.system_clock import SystemClock
    real = SystemClock()
    operations = {name: getattr(real, name) for name in ('now', 'wall', 'wall_ns', 'monotonic', 'sleep', 'new_id')}
    operations.update(overrides)
    from do_math.git_process import GitProcess
    return Ports(clock=SimpleNamespace(**operations), git_backend=GitProcess())


def bare_engine(instance=None, runtime=None, *, head="fixture-head", store=None, runner=None,
                formal_verifier=None):
    """A ``ResearchEngine`` over supplied state, without loading a repository.

    The product initializes the process-local owner state, so the engine carries
    every attribute a loaded engine has. ``_save`` compares the state with what
    ``store`` holds for ``head`` (``published_state``); a fixture head the store
    never published holds nothing, so the first ``_save`` publishes to ``store``.
    Without a ``store`` the engine gets the in-memory ``StateStore`` double.
    """
    from do_math.engine import ResearchEngine
    engine = object.__new__(ResearchEngine)
    engine._init_process_state()
    engine.instance, engine.runtime, engine.head = instance, runtime, head
    engine.store = StateStore(engine) if store is None else store
    engine.runner, engine.formal_verifier = runner, formal_verifier
    return engine


def current_state(instance=None, runtime=None):
    """The smallest (instance, runtime) the current state contract accepts, plus the caller's fields.

    Every validated state passes the lifecycle rules (``record_schemas.validate_lifecycle``):
    a lifecycle with its exact original input, a runtime status and a UTC clock
    high-water. Storage tests extend this with the families they examine.
    """
    raw = b"fixture input"
    base_instance = {"lifecycle": {"state": "initializing", "input_id": "UI-fixture", "immutable_input": {
        "text": raw.decode(), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}}}
    base_runtime = {"status": "initializing",
                    "last_observed_utc": "2026-01-01T00:00:00+00:00",
                    "inputs": [{"id": "UI-fixture", "text": raw.decode(), "sha256": hashlib.sha256(raw).hexdigest(),
                                "config": {"goal": "fixture"}, "created_at": "2026-01-01T00:00:00+00:00"}]}
    return {**base_instance, **(instance or {})}, {**base_runtime, **(runtime or {})}


def governance_start(instance=None):
    """``instance`` with the empty governance families ``initialization.initialize_state`` gives every instance.

    A domain test that calls a governance function on a small instance starts here
    instead of relying on the function to create these families.
    """
    return {"governance": {}, "governance_sources": {}, "decisions": {}, "grants": {}, **(instance or {})}


def installed_contract():
    """A new StateContract holding the installed families, for a test that adds to it.

    Repositories share default_state_contract(), which never gains a family,
    so a test registers extra families on a contract of its own.
    """
    from do_math.record_schemas import install
    from do_math.state_contract import StateContract
    contract = StateContract()
    install(contract)
    return contract


def with_validator(contract, root, name, validator):
    """Give one family of a test-owned ``contract`` this record validator in place of its own."""
    from dataclasses import replace
    contract._families[root, name] = replace(contract.family(root, name), validator=validator)
    contract._manifest = None
    return contract


class StateStore:
    """The persisted head of an in-memory engine double.

    It implements the repository calls an in-memory engine reaches: ``load``
    reads the engine's current state as that head's published state,
    ``published_state`` holds no cached state (so ``_save`` always publishes),
    and ``save_with_state`` publishes a candidate as the next head and keeps a
    copy in ``published``. It has no Git directory (``git_dir`` is None), so no
    process cache records its reads. Any other repository use fails as it would
    without a store.
    """
    git_dir = None

    def __init__(self, engine):
        self.engine = engine
        self.published = []

    def published_state(self, head):
        return None

    def load(self, snapshot=None):
        return self.engine.head, deepcopy(self.engine.instance), deepcopy(self.engine.runtime)

    def read(self, path, snapshot=None):
        # The engine passes this reader to consumers; no artifact is stored here.
        raise AssertionError("an in-memory engine double stores no artifact: " + path)

    def save_with_state(self, expected_head, instance, runtime, *, artifacts=None, retain=None):
        self.published.append({"instance": deepcopy(instance), "runtime": deepcopy(runtime),
                               "artifacts": dict(artifacts or {})})
        return f"{expected_head}+{len(self.published)}", deepcopy(instance), deepcopy(runtime)


def new_instance(repository, *, goal, workspace=None, **options):
    """Create a Git repository and initialize one instance in it through the public ``initialize``.

    ``workspace`` defaults to ``repository / 'work'``; ``options`` pass to ``initialize``.
    Returns the new instance ID.
    """
    from do_math.engine import initialize
    repository = Path(repository)
    git_init(repository)
    return initialize(repository, goal=goal, workspace=repository / "work" if workspace is None else workspace,
                      **options)["instance_id"]


def read_fixture_context(prompt, workspace):
    """Read the same exact local sources exposed to the scripted role."""
    from do_math.context_store import read_source
    value = json.loads(prompt.split('--- CANONICAL INPUT CONTEXT ---\n', 1)[1].split('\n--- OUTPUT JSON SCHEMA ---', 1)[0])
    def read(reference):
        result = read_source(workspace, reference, limit=max(1, reference['bytes']))
        if result['status'] != 'ok' or result['truncated']:
            raise AssertionError('Supplied context source could not be read exactly: ' + repr(result))
        contents = json.loads(result['bytes'])
        for token in reference.get('json_pointer', '').strip('/').split('/') if reference.get('json_pointer') else []:
            contents = contents[int(token)] if isinstance(contents, list) else contents[token]
        return contents
    for key, entry in list(value.items()):
        if isinstance(entry, dict) and isinstance(entry.get('source_ref'), dict) and entry['source_ref'].get('path'):
            value[key] = read(entry['source_ref'])
    for index, task in enumerate(value.get('tasks', []) if isinstance(value.get('tasks'), list) else []):
        if isinstance(task.get('source_ref'), dict):
            task = value['tasks'][index] = {**task, **read(task['source_ref'])}
        for field in ('results', 'reviews', 'revision_history', 'assessment_history'):
            if task.get(field + '_source'):
                task[field] = read(task[field + '_source'])
    return value


def role_reach(prompt, workspace, secret):
    """Where ``secret`` reaches the role given ``prompt`` in its prepared ``workspace``.

    A role reads three things: its rendered prompt, the files of its workspace (the fixed
    input), and through its installed read tool the input snapshot that record_map allows.
    The tool is run as the role runs it, on every record_index ID and on every snapshot
    file that holds ``secret``. Returns ``(reached, held)``: the prompt, workspace files and
    tool requests that yield ``secret``, and the snapshot files that hold it. An empty
    ``held`` means the snapshot never held the secret, so ``reached`` proves nothing.
    """
    import subprocess
    from do_math.git_store import GitStateStore
    workspace, needle = Path(workspace), secret.encode("utf-8")
    reached = ["prompt"] if secret in prompt else []
    reached += sorted(path.relative_to(workspace).as_posix() for path in workspace.rglob("*")
                      if path.is_file() and needle in path.read_bytes())
    context = json.loads((workspace / "input/submission/context.json").read_bytes())
    store = GitStateStore(Path(context["record_store"]["repository"]), context["record_store"]["instance_id"])
    paths = sorted(store.tree_paths(context["snapshot"]))
    held = sorted(path for path, raw in store.read_many(context["snapshot"], paths).items() if needle in raw)
    requests = [argument for identifier in sorted({i for ids in context["record_index"].values() for i in ids})
                for argument in ("--id", identifier)] + [argument for path in held for argument in ("--path", path)]
    if requests:
        result = subprocess.run([sys.executable, "-B", "input/tools/read_input.py", *requests], cwd=workspace,
                                capture_output=True, timeout=120)
        output = json.loads(result.stdout)
        reached += ["read_input.py " + row["request"] for row in output["records"]
                    if row["status"] == "ok" and secret in json.dumps(row, ensure_ascii=False)]
    return reached, held


def candidate(title="task", *, formal=False, revises=None, refs=None):
    return {"revises_task_id": revises, "title": title,
        "question": "Can the stated natural-number identity be established?",
        "scope": {"included": ["Natural numbers and addition of zero"], "excluded": ["Other domains"]},
        "expected": {"outputs": ["An argument or an explicit remaining obstacle"],
                     "research_change": "Resolve the stated zero-addition identity"},
        "progress_criteria": [{"id": "PC-argument", "claim": "Identify the argument and domain", "evidence_required": []}],
        "completion_obligations": [{"id": "OB-argument", "claim": "Report the exact argument and its domain",
                                     "judges": ["research_plan"], "evidence_required": []}],
        "inputs": list(refs or []), "reuse": list(refs or []), "dependencies": [],
        "profile_refs": [], "authority_refs": [], "basis_refs": [],
        "work_class": "formal" if formal else "nonformal"}


def bind_candidates(output, context):
    """Select only work profiles and current grants actually supplied to the author."""
    current = context.get("role_profile_refs", {}).get("research_work")
    for row in output.get("candidates", []):
        row["profile_refs"] = [profile_ref(p) for p in context["execution_profiles"]
                               if p["role"] == "research_work"
                               and (current is None or profile_ref(p) in current)]
        row["authority_refs"] = [g["id"] for g in context["grants"]
                                 if g["status"] == "active" and "research_work" in g.get("roles", [])]


def review_items(evidence_refs, *, decision="approved", next_owner="research_plan", findings=()):
    """A contract review output that reviews every product contract item alike."""
    return {"item_reviews": [{"item_id": item, "decision": decision,
        "evidence_refs": list(evidence_refs), "findings": list(findings),
        "missing_inputs": ["Contract clarification"] if decision == "unresolved" else [],
        "next_owner": next_owner} for item in CONTRACT_REVIEW_ITEMS]}


def contract_review(context, *, decision="approved", findings=()):
    task = context["task"]
    if not task.get("completion_obligations") or not task.get("scope"):
        raise AssertionError("The review fixture requires the actual structured contract")
    return review_items([task["id"]], decision=decision, next_owner="research_preparation", findings=findings)


def scope_response(context):
    review = context["role_review"]
    policy = review["review_policy"]
    perspectives = list(policy["required_perspectives"])
    for value in ("Statement and proof", "Explanation and domain"):
        if len(perspectives) < policy["minimum_initial_slots"]:
            perspectives.append(value)
    if len(perspectives) < policy["minimum_initial_slots"]:
        raise AssertionError("The explicit fixture only defines two independent perspectives")
    return {"proposal_digest": review["proposal_digest"], "scope_complete": True,
        "scope_assessment": {"assessment_id": "fixture-full-scope", "policy_id": policy["id"],
            "required_perspectives": list(policy["required_perspectives"]),
            "initial_slots": [{"id": "initial-" + str(i), "perspective": perspective,
                               "required_source_refs": ["proposal"]} for i, perspective in enumerate(perspectives)],
            "selected_profile_ref": profile_ref(context["execution_profile"]),
            "activity_execution_limit": policy["activity_execution_limit"],
            "overflow_disposition": policy["overflow_disposition"]}}


def disposition(task_id, *, kind="selected"):
    return {"task_id": task_id, "kind": kind, "reason": "Select the current independently approved contract",
        "uncertainty": "Completion of the contracted argument remains to be tested.",
        "parallel_task_ids": [], "expected_research_change": "Obtain the contracted argument",
        "revisit": {"event_refs": [], "at": None}, "missing_inputs": [], "next_owner": "research_work"}


def planning_model_assessments(output, context):
    tasks = {task['id']: task for task in context.get('tasks', [])}
    selected = [row['task_id'] for row in output.get('dispositions', []) if row.get('kind') == 'selected']
    assessments = []
    for task_id in selected:
        task = tasks.get(task_id)
        prior = task.get('model_assessment') if task else None
        if not prior:
            raise AssertionError('The planning fixture cannot assess a selected task without its supplied model assessment')
        assessments.append({'task_id': task_id, 'difficulty': prior['difficulty'],
            'importance': prior['importance'],
            'reason': 'The planner explicitly re-assesses the supplied bounded contract'})
    return assessments


class Clock:
    """A settable clock for an ``ObservationTracker``: each call returns ``value``."""
    def __init__(self): self.value = 0
    def __call__(self): return self.value


def observation_rule(operator="counter_gte", subject_kind="counter", subject_id="attempts", threshold=2, **changes):
    """One observation rule ``R-1`` on ``subject_id``; its basis is ``operator``'s own source and unit.

    The default counts ``attempts`` from the worker checkpoint; ``changes``
    replace fields (``id``, ``required_evidence``, ``basis``) or add
    ``repeat_interval``.
    """
    from do_math.observations import OPERATORS
    value = {
        "id": "R-1", "operator": operator, "subject": {"kind": subject_kind, "id": subject_id},
        "basis": {"source": OPERATORS[operator]["source"], "unit": OPERATORS[operator]["unit"]},
        "threshold": threshold, "required_evidence": ["EV-1"],
    }
    value.update(changes)
    return value


def self_check_response(obligation, status="normal", evidence=None):
    """The worker's answer to a delivered self-check ``obligation``: every due rule gets ``status``.

    ``evidence`` replaces each rule's required evidence references; an
    ``indeterminate`` answer names that evidence as missing.
    """
    return {"obligation_id": obligation["id"], "execution_id": obligation["execution_id"],
            "rule_revision": obligation["rule_revision"], "progress": "progress",
            "attempts": ["checked actual artifact"], "next_method": "continue proof",
            "rule_results": [{"rule_id": row["rule_id"], "status": status,
                "evidence_refs": evidence if evidence is not None else row["required_evidence"],
                "missing_evidence_refs": row["required_evidence"] if status == "indeterminate" else [],
                "reason": "artifact comparison"} for row in obligation["due"]]}


def supply_observation_rules(candidates, extensions):
    """Declare an explicit checkpoint-counter policy for the scripted short task."""
    if not candidates:
        return
    conditions = extensions.setdefault('task_conditions', [])
    for candidate in candidates:
        row = next((item for item in conditions if item.get('task_title') == candidate['title']), None)
        if row is None:
            row = {'task_title': candidate['title']}
            conditions.append(row)
        row.setdefault('observation_rules', [observation_rule(
            threshold=10, id='fixture-attempts', required_evidence=['checkpoint.json'])])


def write_checkpoint(workspace, *, counters=None, iteration=None, claim="fixture progress"):
    """Write a valid worker checkpoint; a tracker reads counters and iterations only from here."""
    value = {"current_claim": claim, "evidence_paths": [], "attempts": [], "remaining_work": [],
             "next_step": "continue", "progress_state": "working"}
    if counters is not None:
        value["counters"] = counters
    if iteration is not None:
        value["iteration"] = iteration
    Path(workspace, "checkpoint.json").write_text(json.dumps(value), encoding="utf-8")


def observe(tracker, event, **options):
    """``tracker.observe`` of ``event`` as the next one-byte stream row, received at the tracker's clock.

    A runner delivers every row with its stream coordinate (``ObservationBatch.source``);
    this gives a unit test that same coordinate without a stream file.
    """
    previous = tracker.observation_source
    start = previous["end_offset"] if previous is not None else 0
    source = {"stream": "stdout.jsonl", "start_offset": start, "end_offset": start + 1,
              "received_at": datetime.now(timezone.utc).isoformat(), "received_monotonic": tracker.clock()}
    return tracker.observe(event, source=source, **options)


def acknowledge(tracker, obligation_id):
    """Deliver an open self-check request and observe the worker's successful poll of it.

    After this, a research action the tracker observes violates the open request.
    """
    from do_math.control_transport import CONTROL_SERVER, SELF_CHECK_TOOL
    request = tracker.issue_self_check(obligation_id)
    previous = tracker.observation_source
    tracker.record_delivery(obligation_id, source_offset=previous["end_offset"] if previous is not None else 0)
    poll = {"type": "item.completed", "item": {"id": "poll-" + obligation_id, "type": "mcp_tool_call",
            "server": CONTROL_SERVER, "tool": SELF_CHECK_TOOL, "arguments": {"self_check_id": obligation_id},
            "status": "completed", "result": {"content": [{"type": "text", "text": json.dumps(request)}]}}}
    observe(tracker, poll, evaluate=False)
    assert tracker.obligations[obligation_id].get("acknowledged_call_id") == "poll-" + obligation_id


def observation_batch(events=(), *, received_monotonic, stream_path, start=0, terminated=False):
    """The runner's batch of ``events`` as consecutive JSON rows starting at stream offset ``start``."""
    from do_math.observation_transport import ObservationBatch
    rows = [json.dumps(event).encode("utf-8") + b"\n" for event in events]
    offsets, position = [], start
    for row in rows:
        offsets.append((position, position + len(row)))
        position += len(row)
    return ObservationBatch(list(events), offsets, rows, 0, datetime.now(timezone.utc).isoformat(),
                            received_monotonic, position, Path(stream_path), lambda: terminated)


def prepared_rule_conditions(task_ids):
    """Explicit response fixture for assigned existing-task rule preparation."""
    extensions = {}
    supply_observation_rules([{'title': tid} for tid in task_ids], extensions)
    return [{'task_id': row['task_title'], 'observation_rules': row['observation_rules']}
            for row in extensions.get('task_conditions', [])]


def assessment(task):
    reports = task.get("results", [])
    if not reports or not all(row.get("report") for row in reports):
        raise AssertionError("Completion fixture requires a supplied nonempty report")
    return {"task_id": task["id"], "decision": "completed", "reason": "The supplied report states the argument and domain",
        "item_dispositions": [{"obligation_id": row["id"], "kind": "fulfilled",
                               "evidence_refs": [r["execution_id"] for r in reports]}
                              for row in task["completion_obligations"]], "unresolved": []}


def intent_response(context):
    if context["action"].get("stage", "interpret") == "interpret":
        source = context["user_request"]
        return {"summary": "Preserve the supplied input verbatim for independent inspection",
            "used_sources": [], "questions": [], "question_details": [],
            "import_units": [{"unit_id": "IU-original", "source_range": {"start": 0, "end": len(source["text"])},
                "interpretation": source["text"], "owner_kind": "charter",
                "owner_ref": context["governance"]["charter"]["id"],
                "payload": {}, "decision_refs": [], "question_refs": []}]}
    bundle = context["interpretation_to_check"]
    source = bundle["source"]["text"]
    units = bundle["output"]["import_units"]
    if "".join(u["interpretation"] for u in units) != source:
        raise AssertionError("This fixture only approves verbatim, complete interpretation")
    return {"summary": "Independently compare supplied units with the exact original input",
        "used_sources": [], "questions": [], "decision": "approved", "scope_complete": True,
        "bundle_sha256": bundle["sha256"], "unit_ids": [u["unit_id"] for u in units],
        "question_ids": [q["id"] for q in bundle["output"]["question_details"]], "findings": []}


def seal_response(output, context, workspace):
    """Producer declares its real output/extension coordinates as one coupled unit."""
    from do_math.integration import mutation_members
    members = ["output"]
    role = context["action"]["role"]
    if role == 'research_preparation':
        from do_math.model_policy import preparation_only
        if not preparation_only(context['action']) and context.get('observed_at'):
            from datetime import datetime, timedelta
            output.setdefault('regenerate_after', (datetime.fromisoformat(context['observed_at'].replace('Z', '+00:00'))
                                                  + timedelta(hours=1)).isoformat())
    if role in {"research_work", "supplemental_research"} and not context["action"].get("review_cycle_id"):
        members += [f"output/{key}/{i}" for key in ("knowledge", "relations") for i, _ in enumerate(output.get(key, []))]
    path = workspace / "activity-extensions.json"
    extensions = json.loads(path.read_bytes()) if path.exists() else {}
    members += [f"activity-extensions.json/{family}/{i}" for family, rows in extensions.items() for i, _ in enumerate(rows)]
    identifier = "IN-" + hashlib.sha256(canonical_json({"action": context["action"], "output": output,
                                                       "extensions": extensions})).hexdigest()[:24]
    visible = {row["id"]: row for family in ("tasks", "knowledge_catalog")
               for row in context.get(family, []) if row.get("id")}
    mutation_ids = {target for _, _, target, _ in mutation_members(output, extensions)}
    previous_hashes = {}
    for target in mutation_ids:
        record = visible.get(target)
        if record is None or not record.get("content_sha256"):
            raise AssertionError("The fixture cannot revise a record absent from its fixed input: " + str(target))
        previous_hashes[target] = record["content_sha256"]
    output["integration_bundles"] = [{"integration_id": identifier, "members": members,
                                      "impact_set": [], "authority_refs": [],
                                      "previous_hashes": previous_hashes}]
    return output


def local_job_runner(method):
    """Give scripted model calls a real, bounded local process lifetime."""
    @wraps(method)
    def run(self, **arguments):
        callback = arguments["on_started"]
        if getattr(callback, "fixture_job", False):
            return method(self, **arguments)
        from do_math.windows_job import WindowsJob, process_identity
        job = None

        def started(_reported_identity=None):
            nonlocal job
            if job is not None:
                raise AssertionError("A scripted call must start exactly once")
            job = WindowsJob([sys.executable, "-c", "import time; time.sleep(600)"],
                             cwd=arguments.get("workspace"), name=arguments['launch_ticket']['job_name'])
            callback({**process_identity(job), "job_name": job.name})
            job.resume()

        started.fixture_job = True
        try:
            return method(self, **{**arguments, "on_started": started})
        finally:
            if job is not None:
                try:
                    job.terminate()
                    if not job.wait(10) or job.inspect().active_processes:
                        raise AssertionError("The fixture child did not terminate")
                finally:
                    job.close()
    return run


def dispatched_launch(execution_id, profile):
    """The current explicit runner contract used by native boundary fixtures."""
    from do_math.launch import ticket
    value = ticket(execution_id, profile)
    value['phase'] = 'dispatched'
    return value


def submit_intent(binding, workspace, output):
    if binding is None:
        raise AssertionError("The engine must supply its real control transport")
    from do_math.submission import request_control
    (workspace / "output.json").write_bytes(canonical_json(output))
    delivery = request_control(workspace, "output.json", kind="submit_intent", wait_seconds=0, binding=binding)
    request_id = delivery["request_id"]
    # The owner loop receives transport requests every pass; the worker only waits.
    receipt = ControlTransport.wait_receipt(binding, request_id, 60)
    if not receipt or receipt["state"] != "accepted":
        raise AssertionError("Submission intent did not receive engine acceptance: " + repr(receipt))


def await_control(engine, request, timeout=60):
    """Wait until the running owner loop has applied a queued public control."""
    import time
    until = time.monotonic() + timeout
    while request["request_id"] not in engine.runtime.get("processed_controls", []):
        if time.monotonic() > until:
            raise AssertionError("The owner loop did not apply control " + request["request_id"])
        time.sleep(.01)


def await_stop(should_stop, timeout=60):
    """Wait until the owner's stop judgment has set the calculation's flag."""
    import time
    until = time.monotonic() + timeout
    while not should_stop():
        if time.monotonic() > until:
            return False
        time.sleep(.01)
    return True


def producer_result(result, arguments):
    """Add only producer transport/envelope facts to a scenario's explicit response."""
    if result.get("status") == "completed" and isinstance(result.get("output"), dict):
        context = read_fixture_context(arguments["prompt"], arguments["workspace"])
        bind_candidates(result["output"], context)
        seal_response(result["output"], context, arguments["workspace"])
        submit_intent(arguments.get("control_binding"), arguments["workspace"], result["output"])
    return result


FIXTURE_CAPABILITIES = {"jsonl": True, "model": True, "structured_output": True}


class FixtureAdapter:
    """The synthetic observation double for ``LocalCLIAdapter``'s probe surface."""
    def __init__(self, capabilities=FIXTURE_CAPABILITIES):
        self.capabilities = dict(capabilities)

    def capability_identity(self):
        return deepcopy(IDENTITY)

    def observation_key(self): return ('fixture',)

    def describe(self):
        return {"identity": deepcopy(IDENTITY), "verified": True,
            "scope": "synthetic_test_evidence_not_host_verification",
            "supported": dict(self.capabilities), "unknown": [],
            "version_sha256": "a" * 64, "exec_help_sha256": "b" * 64}


def install_adapter_fixture(test_case):
    """Replace only external observation; retain evidence hashing and capability gates."""
    def adapter(profile):
        return FixtureAdapter()
    mocked = patch("do_math.initialization.adapter_for", side_effect=adapter)
    mocked.start()
    test_case.addCleanup(mocked.stop)


@contextmanager
def fixture_setup_lean(toolchain, smoke, *, validation=True):
    """setup_lean with host observations replaced by a fixture toolchain.

    Fixture files are created moments before, so the racy window is closed for
    them; recording would otherwise wait for their fingerprints to settle.
    """
    import setup_lean
    compiled = validation_fixture(toolchain, smoke)
    result = compiled if validation else {**compiled, 'status': 'failed', 'exit_code': 1}
    with patch.object(setup_lean, 'observe_identity', return_value=deepcopy(toolchain)), \
         patch.object(setup_lean, 'verify_environment', return_value=result), \
         patch('do_math.file_io.RACY_NS', 0):
        yield


def validation_fixture(toolchain, source):
    """Explicit compiler double; never present this record as native validation."""
    from do_math.trust_inventory import validation_program
    text,scope=validation_program(toolchain)
    return {'status':'verified','scope':scope,'source':str(source.resolve()),'source_text':text,
        'source_sha256':hashlib.sha256(text.encode()).hexdigest(),
        'command':[*toolchain['configured_command'],str(source.resolve())],
        'exit_code':0,'stdout':'synthetic external compiler result','stderr':'',
        'started_at':'2026-09-20T00:00:00Z','finished_at':'2026-09-20T00:00:01Z'}


SYNTHETIC_TOOLCHAIN_FILES = ('bin/lean.exe', 'bin/lake.exe', 'bin/libleanshared.dll', 'lib/lean/Init/Prelude.olean')


def trust_fixture(root, command):
    """A synthetic installation, its shared toolchain record and the registration request.

    The checker identity is the real formal.py, so publication gates recompute a
    consistent identity. Each call owns a new directory and record.
    """
    import tempfile
    from do_math import formal, trust_inventory as records
    Path(root).mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix='synthetic-trust-', dir=root)).resolve()
    for relative in SYNTHETIC_TOOLCHAIN_FILES:
        path = directory / 'toolchain' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(("CORE_TESTS synthetic " + relative + " for " + " ".join(command)).encode())
    lean, lake = directory / 'toolchain/bin/lean.exe', directory / 'toolchain/bin/lake.exe'
    checker = Path(formal.__file__).resolve()
    toolchain = {"executable": str(lean), "sha256": sha256_file(lean), "version": "Lean test 4.32.0",
                 "version_exit": 0, "configured_command": list(command),
                 "verifier_sha256": sha256_file(checker), "verifier_path": str(checker),
                 "executables": {str(lean): sha256_file(lean), str(lake): sha256_file(lake)}, "project": None}
    fingerprint = records.observe_fingerprint(toolchain)
    content = records.content_hashes(toolchain, fingerprint['files'])
    record = records.new_record(toolchain, records.new_baseline(
        fingerprint, content, validation_fixture(toolchain, directory / 'smoke.lean')))
    path = directory / 'records' / (record['id'] + '.json')
    records.write_record(path, record)
    return {"operation": "register", "toolchain": toolchain, "allowed_axioms": sorted(AXIOMS),
            "toolchain_record": {"path": str(path), "id": record['id']}, "binding": records.binding(record)}


def trust_environment(request, *, environment_id='TE-fixture', status='active', source_ref='fixture:trust'):
    """The instance record and runtime binding that registering this request produces.

    Store the record in instance['trust_environments'] and the binding in
    runtime['trust_bindings'] under the same ID.
    """
    environment = {'id': environment_id, 'status': status, 'toolchain': deepcopy(request['toolchain']),
                   'allowed_axioms': list(request['allowed_axioms']), 'source_ref': source_ref,
                   'toolchain_record': deepcopy(request['toolchain_record'])}
    return environment, deepcopy(request['binding'])


def send_control(engine, action, **kwargs):
    from do_math.engine import control
    request = control(engine.store.repository, engine.instance["id"], action, **kwargs)
    engine.process_controls()
    rejected = [h for h in engine.runtime["history"] if h.get("kind") == "rejected_user_control"
                and h.get("request", {}).get("id") == request["request_id"]]
    if rejected:
        raise AssertionError("Public fixture control was rejected: " + repr(rejected))
    return request


def charter_change(engine, **content_changes):
    """Propose explicit changes to the actual current charter; approval stays public."""
    from do_math.repository import new_id
    current = engine._governance()["charter"]
    return {"kind": "charter", "record": {"id": new_id("CH"), "kind": "charter",
        "revision": current["revision"] + 1, "supersedes": [current["id"]],
        "content": {**deepcopy(current["content"]), **deepcopy(content_changes)}}}


def policy_change(engine, text):
    from do_math.repository import new_id
    return {"kind": "policy", "record": {"id": new_id("PO"), "kind": "policy", "revision": 1,
        "supersedes": [], "content": {"rule_id": "fixture-domain", "text": text,
            "scope": [engine._governance()["goal"]], "reason_refs": [engine._governance()["charter"]["id"]],
            "audit_refs": []}}}


def charter(identifier="CH1", goal="Prove P", **content):
    """A charter record proposing ``goal``; ``content`` replaces its other content fields. It grants no approval."""
    return {"id": identifier, "kind": "charter", "revision": 1, "supersedes": [],
            "content": {"rationale": "Research P", "goal": goal, "desired_result": "A proof",
                        "success_criteria": ["P proved"], "partial_success_criteria": ["Cases settled"],
                        "included_scope": ["P"], "excluded_scope": [], "priorities": ["P"],
                        "preferences": [], "evidence_boundary": "Proof, not preference",
                        "academic_requirements": [], "decision_authority": "user", "stop_conditions": [], **content}}


def charter_record(goal):
    """Author explicit synthetic charter content; this grants no approval."""
    return charter("CH-fixture", goal, rationale="Exercise the explicit synthetic research scenario",
        desired_result="A proof of the supplied mathematical goal", success_criteria=[goal],
        partial_success_criteria=["Record an explicit unresolved obligation"], included_scope=[goal],
        priorities=["Proof"], evidence_boundary="Synthetic model and compiler inputs in a temporary repository")


def approved_governance(instance, records, *, source=("S", "User approves P"), approval_id="D"):
    """``instance`` with ``records`` adopted by one explicit synthetic user approval.

    ``source`` is the preserved user text ``(ID, text)``; the approval
    ``approval_id`` binds its hash and each record's exact content hash, as
    ``governance.initialize_governance`` requires. ``instance`` gains the empty
    governance families first (``governance_start``).
    """
    from do_math import governance
    from do_math.repository import exact_content_hash
    preserved = governance.preserve_source(*source, origin="user")
    approval = {"id": approval_id, "actor": "user", "source_ref": preserved["id"], "source_sha256": preserved["sha256"],
                "record_hashes": {record["id"]: exact_content_hash(record) for record in records}}
    return governance.initialize_governance(governance_start(instance), preserved, approval, records)


def activate(engine, root, *, initialization_runner, external_policy="disabled", review_policy=None):
    """Fill activation through public controls and two actual interpretation executions.

    The fixture supplies synthetic approval, trust, and capability observations.
    The engine applies lifecycle changes and checks the activation gates.
    """
    from do_math.engine import control
    # This fixture explicitly approves observation windows before adopting the
    # resulting profiles. Production deliberately has no implicit defaults.
    windows = {key: value for key, value in {
        "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}.items()
        if key not in engine.instance["config"]}
    if windows:
        send_control(engine, "configure", config=windows)
    expiry = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    from do_math.repository import exact_content_hash
    config_sha256 = exact_content_hash(engine.instance["config"])
    from do_math.model_policy import selection
    initial_ref = selection(engine.instance["config"], {"role": "intent_interpretation"},
        {}, engine.instance["knowledge"], instance=engine.instance)["profile_ref"]
    charter = charter_record(engine.instance["lifecycle"]["immutable_input"]["text"])
    controls = [("decision", {"change": {"kind": "initialization", "operation": "governance", "records": [charter]}}),
        ("decision", {"change": {"kind": "grant", "grant": {
        "id": "GR-initial-fixture", "kind": "local", "roles": ["intent_interpretation"],
        "reuse": "reusable", "expires_at": expiry}}}),
        ("decision", {"change": {"kind": "grant", "grant": {"id": "GR-research-fixture",
        "kind": "local", "roles": list(ROLES) + ["formal_check"], "reuse": "reusable", "expires_at": expiry}}})]
    controls += [("decision", {"change": {"kind": "initialization", "operation": "probe",
                                         "config_sha256": config_sha256}})]
    controls += [("trust", trust_fixture(root, engine.instance["config"]["lean_command"]))]
    for action, config in controls:
        control(engine.store.repository, engine.instance["id"], action,
            text="Synthetic CORE_TESTS input; not actual host verification or user approval", config=config)
    engine.process_controls()
    rejected = [h for h in engine.runtime["history"] if h.get("kind") == "rejected_user_control"]
    if rejected:
        raise AssertionError("Initialization controls rejected: " + repr(rejected))
    environment = next(iter(engine.instance["trust_environments"]))
    send_control(engine, "trust", config={"operation": "transition", "env_id": environment})
    send_control(engine, "decision", config={"change": {"kind": "initialization",
        "config_sha256": config_sha256, "adopt_current_governance": True,
        "conversation_loss_policy": "continue_authorized", "external_policy": external_policy,
        **({"review_policy": review_policy} if review_policy is not None else {"adopt_default_review_policy": True}),
        "initial_profile_ref": initial_ref, "initial_grant_ids": ["GR-initial-fixture"],
        "research_grant_ids": ["GR-research-fixture"]}})
    previous = engine.runner
    engine.runner = initialization_runner
    try:
        engine.run(until_active=True)
        if engine.instance['lifecycle']['state'] != 'active':
            raise AssertionError("Public initialization did not reach active: " + repr({
                "activation": engine.instance["lifecycle"]["activation"],
                "status": engine.runtime["status"], "history": engine.runtime["history"][-3:]}))
    finally:
        engine.runner = previous
    return engine


def _no_formal_check(**arguments):
    raise AssertionError('Public activation ran a formal check; a template build supplies no verifier')


def activated_instance(root, shared, *, goal, config, external_policy='disabled', review_policy=None):
    """``restore_template`` build: public ``initialize`` and ``activate``; returns the instance ID.

    The repository is ``root / 'repository'`` and the workspace ``root / 'work-0'``.
    The synthetic toolchain goes to ``shared`` so restored copies keep its fingerprint.
    """
    from do_math.engine import ResearchEngine, initialize
    from runner_fixtures import ScriptedRunner
    repository = git_init(root / 'repository')
    with patch('do_math.initialization.adapter_for', side_effect=lambda profile: FixtureAdapter()):
        instance_id = initialize(repository, goal=goal, workspace=root / 'work-0', config=config)['instance_id']
        engine = ResearchEngine(repository, instance_id, runner=ScriptedRunner(), formal_verifier=_no_formal_check)
        activate(engine, shared, initialization_runner=ScriptedRunner(), external_policy=external_policy,
                 review_policy=review_policy)
    return instance_id


_EMPTY_GIT_DIR = []


def git_init(path):
    """Make ``path`` a new empty Git repository, as ``git init -q <path>`` does.

    The first call runs ``git init`` once for this process; every call copies
    that repository's ``.git`` directory, which names no path of its own.
    """
    path = Path(path)
    if not _EMPTY_GIT_DIR:
        model = Path(tempfile.mkdtemp(prefix='do-math-empty-git-'))
        atexit.register(shutil.rmtree, model, True)
        import subprocess
        subprocess.run(['git', 'init', '-q', str(model)], check=True)
        _EMPTY_GIT_DIR.append(model / '.git')
    path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(_EMPTY_GIT_DIR[0], path / '.git')
    return path


def run_cli(*arguments, cwd=None):
    """Run the CLI's ``main`` in this process, as ``python do_math.py *arguments`` would.

    Returns a ``subprocess.CompletedProcess`` with ``returncode`` and text
    ``stdout``/``stderr``. ``cwd`` is the working directory during the call.
    Nothing about the process is exercised: stream encoding, interpreter
    start-up and process-wide state stay those of the test process.
    """
    import io
    import subprocess
    from contextlib import redirect_stderr, redirect_stdout
    from do_math.cli import main
    arguments = [os.fspath(argument) for argument in arguments]
    stdout, stderr = io.StringIO(), io.StringIO()
    previous = os.getcwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = main(arguments)
            except SystemExit as exit:
                # As the interpreter does: None is success, other non-integers print and fail.
                code = 0 if exit.code is None else exit.code if isinstance(exit.code, int) else 1
                if not isinstance(exit.code, (int, type(None))):
                    print(exit.code, file=sys.stderr)
    finally:
        os.chdir(previous)
    return subprocess.CompletedProcess(['do_math.py', *arguments], code, stdout.getvalue(), stderr.getvalue())


def cli_result(root, *arguments):
    """The public command's ``result`` run with ``run_cli`` in ``root``; the command must succeed."""
    completed = run_cli(*arguments, cwd=root)
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    envelope = json.loads(completed.stdout)
    if envelope["exit_code"] != 0:
        raise AssertionError(envelope)
    return envelope["result"]


def remove_tree(path):
    """Delete a directory tree, including the read-only object files Git writes."""
    def writable(function, target, _error):
        os.chmod(target, stat.S_IWRITE)
        function(target)
    shutil.rmtree(path, onexc=writable)


class _Template:
    """One built tree, its untouched copy, and the fixed path copies are restored to."""

    def __init__(self, build, parameters):
        self.base = Path(tempfile.mkdtemp(prefix='do-math-template-')).resolve()
        atexit.register(self.remove)
        self.live, self.pristine, self.shared = (self.base / name for name in ('live', 'pristine', 'shared'))
        self.live.mkdir()
        self.shared.mkdir()
        self.value = build(self.live, self.shared, **parameters)
        shutil.copytree(self.live, self.pristine, symlinks=True)
        self.used = False

    def restore(self):
        if self.used:
            remove_tree(self.live)
            shutil.copytree(self.pristine, self.live, symlinks=True)
        self.used = True
        return self.live, deepcopy(self.value)

    def remove(self):
        try:
            remove_tree(self.base)
        except OSError:
            pass


_TEMPLATES = {}


def restore_template(build, **parameters):
    """Return ``(root, value)``: a fresh copy of what ``build`` made once in this process.

    ``build(root, shared, **parameters)`` runs on the first call for its
    parameters. It creates the state under ``root`` and returns ``value``
    (usually the instance ID). Every call, including the first,
    then hands out ``root`` holding the exact bytes ``build`` left there, so
    the Git state, workspace and control inbox are those the product published.

    ``root`` is the same path on every call: that is what keeps the absolute
    paths inside the state true. A call therefore replaces the previous copy;
    finish with an engine before asking for the next one. ``shared`` is never
    copied or cleared. Put there only files the product reads and never writes
    whose stat fingerprint the state records, such as ``trust_fixture``
    toolchains: a copy would change their creation time. Parameters must be
    JSON values; together with ``build``'s name they select the template.
    """
    import inspect
    # Defaults are part of the key, so omitting one names the same template.
    bound = inspect.signature(build).bind(None, None, **parameters)
    bound.apply_defaults()
    parameters = dict(list(bound.arguments.items())[2:])
    key = (build.__module__, build.__qualname__, json.dumps(parameters, sort_keys=True))
    template = _TEMPLATES.get(key)
    if template is None:
        # A failed build is not retried: each later test would repeat its cost.
        _TEMPLATES[key] = 'failed'
        template = _TEMPLATES[key] = _Template(build, parameters)
    elif template == 'failed':
        raise AssertionError('This template failed to build earlier in this process: ' + repr(key))
    return template.restore()


def sealed_maintenance_submission(workspace, execution_id):
    """Create real central seal bytes for lifecycle/storage fixture assertions."""
    from do_math import contracts, submission
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    context = {'action': {'id': 'AC-fixture', 'role': 'maintenance'},
               'execution_id': execution_id, 'snapshot': 'fixture-input',
               'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {}}
    schema = contracts.schema_for('maintenance')
    submission.install_tools(workspace, context, schema, None)
    output = {'summary': 'Inspect fixture', 'used_sources': [], 'questions': [],
              'report': 'Explicit synthetic maintenance output.', 'remaining_work': []}
    seal_response(output, context, workspace)
    (workspace / 'draft.json').write_bytes(canonical_json(output))
    sealed = submission.seal_submission(workspace, 'draft.json', execution_id=execution_id,
        context=context, schema=schema, max_artifact_bytes=1024*1024)
    if not sealed['passed']:
        raise AssertionError(sealed['check']['issues'])
    prefix = 'runtime/artifacts/BA-fixture-submission/'
    return ({**sealed['intent'], 'output_ref': prefix + 'output.json'},
            {prefix + path: raw for path, raw in sealed['artifacts'].items()})


def scope_assessment(policy, slots):
    """Explicit synthetic full-proposal scope authored by the fixture reviewer."""
    return {"assessment_id": "fixture-full-proposal-scope", "policy_id": policy["id"],
        "required_perspectives": policy["required_perspectives"],
        "initial_slots": [{"id": slot, "perspective": slot, "required_source_refs": ["proposal"]} for slot in slots],
        "selected_profile_ref": None, "activity_execution_limit": policy["activity_execution_limit"],
        "overflow_disposition": policy["overflow_disposition"]}


def start_scoped_review(engine, knowledge_id, assessment, previous_cycle_id=None):
    """Open a review whose scope stage the fixture has already settled with ``assessment``.

    The engine opens every review at its scope stage. A test about the later
    stages takes the cycle it opened and gives it the scope that the pure
    ``start_review(..., scope_assessment=...)`` path gives, as sealed replay does,
    instead of running a scope execution; it returns the cycle ID.
    """
    from do_math.input_basis import capture_review_input_basis
    from do_math.review_cycle import start_review
    cycle_id = engine._start_identity_review(knowledge_id, previous_cycle_id)
    cycle = engine.runtime['review_cycles'][cycle_id]
    previous = engine.runtime['review_cycles'][previous_cycle_id] if previous_cycle_id else None
    scoped = start_review(cycle['proposal'], cycle['requested_reviewer_slots'], cycle['judge_slots'],
                          cycle['max_rounds'], previous, policy=cycle['review_policy'], scope_assessment=assessment)
    cycle.update({key: scoped[key] for key in ('scope_assessment', 'reviewer_slots', 'activity_execution_limit',
                                               'required_source_refs', 'phase')})
    cycle['review_input_basis'] = capture_review_input_basis(cycle)
    engine.runtime['queue'][:] = [action for action in engine.runtime['queue']
                                  if action.get('review_cycle_id') != cycle_id]
    engine._queue_identity_actions(knowledge_id, cycle_id)
    return cycle_id
