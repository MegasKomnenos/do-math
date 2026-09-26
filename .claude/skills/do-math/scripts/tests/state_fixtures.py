"""Validated starting states for tests whose subject is after initialization.

Synthetic adapter, trust and interpretation evidence is assembled by the
existing lifecycle fixture. Real repository validation/publication is retained;
this helper does not establish that the public initialization workflow works.
Each call creates independent state in the caller's temporary repository.
"""
from copy import deepcopy
import json
from unittest.mock import patch

from do_math.engine import ResearchEngine
from do_math.repository import ResearchRepository, new_id

# FakeEngine.activate registers its active trust environment for this command.
# Formal checks pin the configured command and must equal that environment, as
# public activation arranges; callers whose rule needs formal checks configure it.
ACTIVE_LEAN_COMMAND = ('synthetic-lean', 'base')


def active_engine(repository, workspace, *, config=None, runner=None, formal_verifier=None):
    from test_lifecycle_engine import AdapterDouble, FakeEngine

    workspace.mkdir(parents=True, exist_ok=True)
    with patch("do_math.initialization.adapter_for", return_value=AdapterDouble()):
        seed = FakeEngine(workspace, config=config)
        seed.activate()
    seed.runtime.update(active_execution=None, processed_controls=[], reservations={},
                        provider_waits={}, updated_at=seed.runtime["last_observed_utc"],
                        next_research_reconsider_at="2100-01-01T00:00:00+00:00")
    identifier = new_id("RI")
    instance, runtime = json.loads(json.dumps([seed.instance, seed.runtime]).replace("RI-test", identifier))
    ResearchRepository(repository, identifier).initialize(instance, runtime)
    return ResearchEngine(repository, identifier, runner=runner, formal_verifier=formal_verifier)


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
        transition_execution(execution, "stopping", at=at, stop_phase="terminating")
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
