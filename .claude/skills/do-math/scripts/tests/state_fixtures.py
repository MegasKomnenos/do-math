"""Validated starting states for tests whose subject is after initialization, and owner-loop helpers.

``active_instance`` is a template build (``research_fixtures.restore_template``)
that assembles synthetic adapter, trust and interpretation evidence with
``engine_fixtures.FakeEngine`` and publishes the result through the real
repository validation; it does not establish that the public initialization
workflow works. ``active_repository()`` is a copy of that state with
``ACTIVE_CONFIG``; ``start_active_copy(test)`` gives a test such a copy with
the adapter observation replaced.

``owner_calls(engine)`` and ``start_model_call(engine, action)`` run machine
steps and model calls as the scheduler's owner loop does.
``complete_academic_task`` completes a task with a synthetic returned report.
"""
from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

from do_math.repository import ResearchRepository
from do_math.system_clock import new_id

# FakeEngine.activate registers its active trust environment for this command.
# Formal checks pin the configured command and must equal that environment, as
# public activation arranges; callers whose rule needs formal checks configure it.
ACTIVE_LEAN_COMMAND = ('synthetic-lean', 'base')


def active_instance(root, shared, *, config, external_policy='explicit_grants', review_policy=None):
    """``restore_template`` build of the synthetic active state; returns the instance ID.

    The repository is ``root / 'repository'`` and the workspace ``root / 'work-0'``.
    The synthetic toolchain goes to ``shared`` so restored copies keep its fingerprint.
    ``external_policy`` and ``review_policy`` go to the adoption decision, as in
    ``research_fixtures.activate``; ``review_policy`` None adopts the default.
    """
    from engine_fixtures import FakeEngine
    from research_fixtures import FixtureAdapter, git_init

    repository = root / "repository"
    git_init(repository)
    workspace = root / "work-0"
    workspace.mkdir(parents=True, exist_ok=True)
    with patch("do_math.local_host.adapter_for", return_value=FixtureAdapter()):
        seed = FakeEngine(workspace, config=config)
        seed.root = Path(shared)
        seed.activate(external_policy=external_policy, review_policy=review_policy)
    seed.runtime.update(processed_controls=[], reservations={},
                        provider_waits={}, updated_at=seed.runtime["last_observed_utc"],
                        next_research_reconsider_at="2100-01-01T00:00:00+00:00")
    identifier = new_id("RI")
    instance, runtime = json.loads(json.dumps([seed.instance, seed.runtime]).replace("RI-test", identifier))
    ResearchRepository(repository, identifier).initialize(instance, runtime)
    return identifier


# The settings of the copy most tests start from (``active_repository``).
ACTIVE_CONFIG = {'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}


def active_repository():
    """A copy of the validated active state with ``ACTIVE_CONFIG``: ``(root, repository, instance ID)``.

    It is ``restore_template(active_instance, config=ACTIVE_CONFIG)``; the
    workspace is ``root / 'work-0'`` (the instance names it).
    """
    from research_fixtures import restore_template
    root, identifier = restore_template(active_instance, config=ACTIVE_CONFIG)
    return root, root / "repository", identifier


def start_active_copy(test):
    """Give ``test`` an ``active_repository`` copy: sets ``root``, ``repo`` and ``identifier``.

    The adapter observation stays replaced by ``FixtureAdapter`` until the test ends.
    """
    from research_fixtures import FixtureAdapter
    test.enterContext(patch("do_math.local_host.adapter_for", return_value=FixtureAdapter()))
    test.root, test.repo, test.identifier = active_repository()


@contextmanager
def owner_calls(engine):
    """Run the calls started inside the block on ModelCalls, as the scheduler does.

    The engine has no synchronous call path: machine steps and model calls
    start on ``engine._calls``. Leaving the block answers their callbacks,
    receives their control transport requests (a submission intent waits for
    its receipt), collects every call and resumes its continuation once.
    """
    from do_math.parallel import ModelCalls
    calls = engine._calls = ModelCalls(on_returned=engine._local_call_returned,
                                       on_observation_error=engine._observation_failed)
    try:
        yield calls
        while calls.futures:
            calls.wait(0.05)
            calls.pump()
            # The owner loop pumps the transport every pass (engine._controls).
            if engine._transport is not None:
                engine._transport.pump(engine._publish_control_request)
            calls.collect()
    finally:
        calls.close()
        engine._calls = None


def start_model_call(engine, action):
    """Begin one AI action's call as the scheduler does; use inside ``owner_calls``.

    The scheduler passes the action's lifecycle gate (``_dispatchable``) in the
    pass that starts it, so this passes the same gate first.
    """
    engine._action_lifecycle_gate(action)
    generator = engine._call_steps(action)
    try:
        arguments = next(generator)
    except StopIteration as done:
        return done.value
    engine._calls.start_call(generator, engine.runner.run, arguments, execution_id=arguments.get('execution_id'))
    return False


def complete_academic_task(engine, task, basis):
    """Supply a returned report and apply the real independent assessment rules."""
    from do_math.execution_lifecycle import transition_execution
    from do_math.task_scope import apply_task_assessments
    from research_fixtures import assessment

    executions = []
    for role in ("research_work", "research_plan"):
        action = {"id": new_id("AC"), "role": role, "target": task["id"]}
        execution = engine._register_execution(action, {
            "id": new_id("EX"), "role": role, "status": "running",
            "input_solution_basis": deepcopy(basis)})
        at = engine._lifecycle_now().isoformat()
        transition_execution(execution, "stopping", at=at)
        transition_execution(execution, "ended", at=at, outcome="execution_incomplete")
        executions.append(execution["id"])
    task["results"] = [{"execution_id": executions[0], "report": "Synthetic returned academic account."}]
    completed = assessment(task)
    engine.instance, engine.runtime = apply_task_assessments(
        engine.instance, engine.runtime, [completed], execution_id=executions[1],
        input_tasks=deepcopy(engine.runtime["tasks"]))
    engine._record_academic_assessment(engine.runtime["tasks"][task["id"]], completed, executions[1])
    engine._ensure_academic_followup()
    engine._save()
