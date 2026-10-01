"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from copy import deepcopy


def complete_academic_task(engine, task, basis):
    """Supply a returned report and apply the real independent assessment rules."""
    from do_math.execution_lifecycle import transition_execution
    from do_math.task_scope import apply_task_assessments
    from support.role_answers import assessment

    executions = []
    for role in ("research_work", "research_plan"):
        action = {"id": engine.ports.clock.new_id("AC"), "role": role, "target": task["id"]}
        execution = engine._register_execution(action, {
            "id": engine.ports.clock.new_id("EX"), "role": role, "status": "running",
            "input_solution_basis": deepcopy(basis)})
        at = engine._lifecycle_now().isoformat()
        transition_execution(execution, "stopping", at=at)
        transition_execution(execution, "ended", at=at, outcome="execution_incomplete")
        executions.append(execution["id"])
    task["results"] = [{"execution_id": executions[0], "report": "Synthetic returned academic account."}]
    completed = assessment(task)
    engine.instance, engine.runtime = apply_task_assessments(
        engine.instance, engine.runtime, [completed], execution_id=executions[1],
        input_tasks=deepcopy(engine.runtime["tasks"]), clock=engine.ports.clock)
    engine._record_academic_assessment(engine.runtime["tasks"][task["id"]], completed, executions[1])
    engine._ensure_academic_followup()
    engine._save()
