"""Instance scheduler: model calls run concurrently, state transitions run serially."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import time

from .model_policy import assessment_basis, selection, validate_assessments
from .parallel import ModelCalls
from .session_slots import SessionSlots
from .provider_wait import provider_for
from .execution_window import notice_seconds

MACHINE_ROLES = {"formal_check", "trust_check", "trust_activate", "external_action"}
WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit"}


class SchedulerMixin:
    def _failed_live_review(self, action, reason):
        parent = self.runtime["executions"].get(action.get("target"))
        if action.get("live") and parent and parent["status"] != "ended":
            parent["stop_requested"] = "operating_review_unavailable"
            parent["after_stop"] = {"decision": "wait", "reason": reason}

    def _session_mode(self):
        return self.instance["config"].get("session_limits") is not None

    def _session_resources(self):
        if getattr(self, "_slots", None) is not None:
            return self._slots.snapshot()
        slots = SessionSlots(Path(self.instance["workspace"]), self.instance["id"], observer=True)
        try:
            return slots.snapshot()
        finally:
            slots.close()

    def _select_model(self, action):
        if action.get("model_selection"):
            return deepcopy(action["model_selection"])
        action = deepcopy(action)
        parent = self.runtime["executions"].get(action.get("target"), {})
        if parent.get("model_selection") and not action.get("model_assessment"):
            chosen = parent["model_selection"]
            action["model_assessment"] = chosen.get("assessment") or {
                "difficulty": chosen["tier"], "importance": chosen["tier"],
                "reason": "Preserve the reviewed execution's model requirement."}
        return selection(self.instance["config"], action, self.runtime["tasks"], self.instance["knowledge"])

    def _apply_model_metadata(self, action, output, execution_id):
        extensions = self.runtime["executions"][execution_id].get("extensions", {})
        if action["role"] not in {"research_preparation", "research_plan"}:
            if extensions.get("model_assessments"):
                raise ValueError("only preparation and planning author model assessments")
            return
        identified = validate_assessments(action, output, extensions, required=self._session_mode())
        if "assessment_targets" in action:
            for tid, basis in action["assessment_targets"].items():
                task = self.runtime["tasks"].get(tid)
                if not task or assessment_basis(task) != basis:
                    raise ValueError("model assessment task edition changed: " + tid)
            for tid, assessment in identified.items():
                self.runtime["tasks"][tid]["model_assessment"] = assessment
            return
        if action["role"] == "research_preparation":
            for candidate in output["candidates"]:
                if candidate["title"] in identified:
                    candidate["model_assessment"] = identified[candidate["title"]]
        elif action["role"] == "research_plan":
            self.runtime["executions"][execution_id]["model_decisions"] = identified

    def _assessment_input_version(self):
        return {"goal": self.instance.get("goal_revision", 1), "policy": self.instance.get("policy_revision", 1),
                "sources": [{"name": s["name"], "sha256": s["sha256"]} for s in self.instance["sources"]],
                "inputs": [i.get("id") for i in self.runtime["inputs"]]}

    def _ensure_model_assessments(self):
        """Prepare missing or rejected academic assessments before review."""
        if not self._session_mode():
            return set()
        live = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] != "ended"}
        for tid, task in self.runtime["tasks"].items():
            if (not task.get("academic_requirement_id") or task.get("status") != "needs_revision"
                    or not task.get("model_assessment")):
                continue
            basis = assessment_basis(task)
            review = next((r for r in reversed(task.get("reviews", []))
                           if all(r.get(k) == v for k, v in basis.items())), None)
            if not review or review.get("decision") == "approved":
                continue
            task.setdefault("model_assessment_history", []).append({
                **basis, "assessment": task.pop("model_assessment"),
                "contract_review_execution": review["execution_id"]})
            # Retire the old implementation's unstarted, general revision request.
            self.runtime["queue"][:] = [a for a in self.runtime["queue"] if not (
                a.get("role") == "research_preparation" and a.get("target") == tid
                and a.get("contract_review_execution") == review["execution_id"]
                and a.get("id") not in live)]
        missing = {tid: assessment_basis(task) for tid, task in self.runtime["tasks"].items()
                   if task.get("status") in {"planned", "ready", "waiting", "needs_revision"}
                   and not task.get("model_assessment")}
        for aid, entry in list(self.runtime.get("waiting_actions", {}).items()):
            if entry.get("kind") == "model_assessment_input" and (
                    entry.get("input_version") != self._assessment_input_version()
                    or any(missing.get(tid) != basis for tid, basis in entry["action"]["assessment_targets"].items())):
                self.runtime["history"].append({"kind": "assessment_inputs_changed", "action_id": aid})
                self.runtime["questions"] = [q for q in self.runtime["questions"] if q != entry.get("question")]
                del self.runtime["waiting_actions"][aid]
        self.runtime["queue"][:] = [a for a in self.runtime["queue"] if not (
            a["role"] == "task_contract_review" and a.get("target") in missing and a.get("id") not in live)]
        pending = self.runtime["queue"] + [e["action"] for e in self.runtime.get("waiting_actions", {}).values()]
        covered = {tid for a in pending for tid, basis in a.get("assessment_targets", {}).items() if missing.get(tid) == basis}
        targets = {tid: basis for tid, basis in missing.items() if tid not in covered}
        if targets:
            from .repository import new_id
            self.runtime["queue"].append({"id": new_id("AC"), "role": "research_preparation",
                "assessment_targets": targets, "reason": "Assess these existing contracts without changing their terms before independent review. Read their reviews and model_assessment_history when repairing a rejected assessment."})
        return set(missing)

    def _finish_assessment_preparation(self, action, execution_id):
        deferred = self.runtime["executions"][execution_id].get("extensions", {}).get("model_assessment_deferrals", [])
        deferred_ids = {row["task_id"] for row in deferred}
        for tid in action["assessment_targets"]:
            if tid in deferred_ids:
                continue
            task = self.runtime["tasks"][tid]
            if task.get("academic_requirement_id") and task.get("status") == "needs_revision":
                task["status"] = "planned"
                # Even an unchanged rating needs a fresh judgment after new input.
                self._enqueue("task_contract_review", tid, contract_basis={
                    **assessment_basis(task), "goal_revision": self.instance.get("goal_revision", 1),
                    "policy_revision": self.instance.get("policy_revision", 1)},
                    reason="Reassessed academic contract requires independent review")
        if deferred:
            pending = {row["task_id"]: action["assessment_targets"][row["task_id"]] for row in deferred}
            question = "Model assessment pending: " + "; ".join(row["task_id"] + ": " + row["reason"] for row in deferred)
            self.runtime["questions"].append(question)
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                "action": {**action, "assessment_targets": pending}, "kind": "model_assessment_input",
                "reason": question, "question": question, "input_version": self._assessment_input_version(), "execution_id": execution_id}

    def _apply_queue_plan(self, action, execution_id):
        dispositions = self.runtime["executions"][execution_id].get("extensions", {}).get("queued_requests", [])
        if not dispositions:
            return
        if action["role"] != "research_plan":
            raise ValueError("only research planning reorders queued work")
        _, _, original = self.store.load(self.runtime["executions"][execution_id]["input_snapshot"])
        original_live = {e.get("action", {}).get("id") for e in original["executions"].values() if e["status"] != "ended"}
        allowed = {a["id"] for a in original["queue"] if a.get("id") and a["role"] in WORK_ROLES and a["id"] not in original_live}
        live = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] != "ended"}
        current = {a.get("id"): a for a in self.runtime["queue"]}
        ordered, seen = [], set()
        for row in dispositions:
            if set(row) != {"request_id", "decision", "reason"} or row["decision"] not in {"keep", "cancel"} or not isinstance(row["reason"], str) or not row["reason"].strip():
                raise ValueError("queued request disposition requires identity, keep/cancel and reason")
            aid = row["request_id"]
            if aid not in allowed or aid in seen:
                raise ValueError("queued request was not in the planning input or is repeated")
            seen.add(aid)
            if aid in live or aid not in current:
                self.runtime["history"].append({"kind": "queue_plan_not_applied", "execution_id": execution_id, **row})
                continue
            request = current[aid]
            if row["decision"] == "cancel":
                self._remove_action(request)
                task = self.runtime["tasks"].get(request.get("target"))
                if task and request["role"] in {"research_work", "supplemental_research"} and not request.get("review_cycle_id") and task["status"] == "performing":
                    task.update(status="ready", deferred_reason=row["reason"])
            else:
                ordered.append(request)
            self.runtime["history"].append({"kind": "queue_plan_applied", "execution_id": execution_id, **row})
        # Keep non-work requests in their existing positions and preserve unseen
        # requests, including those created after the planning snapshot.
        reorder_ids = {a["id"] for a in ordered}
        positions = [i for i, a in enumerate(self.runtime["queue"]) if a.get("id") in reorder_ids]
        for position, request in zip(positions, ordered):
            self.runtime["queue"][position] = request

    def _initial_plan_waits(self, action):
        """Delay only pre-research registration, never general planning."""
        basis = action.get("initial_preparation_wait")
        if not basis or action.get("requested_by") or action.get("recovery"):
            return False
        current = {"goal_revision": self.instance.get("goal_revision"),
                   "policy_revision": self.instance.get("policy_revision"),
                   "requirements_sha256": self.instance.get("academic_requirements", {}).get("sha256")}
        if basis != current or self._has_global_user_question() or self.runtime["inputs"]:
            return False
        for event in self.runtime.get("events", []):
            if event["id"] not in action.get("event_refs", []):
                continue
            decision = self.instance.get("decisions", {}).get(event.get("decision_id"), {})
            if event["kind"] != "user_decision_applied" or not decision.get("initial_registration"):
                return False
        tasks = self.runtime["tasks"].values()
        if any(t["status"] in {"ready", "assessing", "needs_revision"} or t.get("results") for t in tasks):
            return False
        preparations = [e for e in self.runtime["executions"].values()
                        if e["role"] == "research_preparation" and not e.get("action", {}).get("assessment_targets")]
        if not preparations:
            return any(a["role"] == "research_preparation" for a in self.runtime["queue"])
        initial = preparations[0]
        if initial["status"] != "ended":
            return True
        if initial.get("outcome") != "output_accepted" or not self.runtime["tasks"]:
            return False
        # Wait for the first usable contract, not for the whole review group.
        # If all reviews end without a usable task, planning must diagnose it.
        return any(a["role"] == "task_contract_review" for a in self.runtime["queue"])

    def _dispatchable(self, action, resources):
        live = [e for e in self.runtime["executions"].values() if e["status"] != "ended"]
        if any(e.get("action", {}).get("id") == action.get("id") for e in live if action.get("id")):
            return False
        role, target = action["role"], action.get("target")
        waits = self._revision_dispatch_waits(action)
        if waits:
            action["dispatch_wait"] = {"kind": "contract_revision", "blockers": waits}
            return False
        if not self._selected_action_current(action):
            return False
        if role == "research_plan" and self._initial_plan_waits(action):
            return False
        identity_keys = ("role", "target", "stage", "slot", "round", "review_cycle_id", "basis", "review_basis_key", "live")
        if any(all(e.get("action", {}).get(key) == action.get(key) for key in identity_keys) for e in live):
            return False
        if role in {"research_preparation", "research_plan"} and any(e["role"] == role for e in live):
            return False
        if role in {"research_work", "supplemental_research"} and not action.get("review_cycle_id") and any(
                e["role"] in {"research_work", "supplemental_research"} and e.get("action", {}).get("target") == target
                and not e.get("action", {}).get("review_cycle_id") for e in live):
            return False
        if role in MACHINE_ROLES:
            return True
        if action.get("live") and self.runtime["executions"].get(target, {}).get("status") == "ended":
            self._remove_action(action)
            return False
        chosen = self._select_model(action)
        action["model_selection"] = chosen
        provider = provider_for(chosen["model"])
        gate = self._provider_status()["providers"].get(provider)
        if gate and (gate["state"] == "checking" or (gate["state"] == "waiting" and not gate["due"])):
            action["dispatch_wait"] = {"kind": "provider_limit", "provider": provider, "retry_at": gate.get("retry_at")}
            return False
        action.pop("dispatch_wait", None)
        pool = "work" if role in WORK_ROLES else "operations"
        cell = resources[pool].get(chosen["model"], {"available": 0})
        return cell["available"] > 0

    def _run_parallel(self, *, max_steps=None, watch=False):
        from .repository import new_id
        self._slots = SessionSlots(Path(self.instance["workspace"]), self.instance["id"])
        self._slots.configure(self.instance["config"]["session_limits"])
        self._calls = ModelCalls()
        deadline = time.monotonic() + self.instance["config"]["run_timeout_seconds"]
        self._run_deadline = deadline
        steps = 0
        try:
            while True:
                self._controls()
                self._calls.collect()
                self._check_installation()
                stopping = self.runtime["status"] in {"paused", "closed", "completed"} or time.monotonic() >= deadline
                if stopping:
                    if not self._calls.futures:
                        break
                    time.sleep(.02)
                    continue
                finishing = deadline - time.monotonic() <= notice_seconds(self.instance["config"])
                draining = finishing or (max_steps is not None and steps >= max_steps)
                if draining:
                    if not self._calls.futures:
                        break
                self.instance["available_input_refs"] = self._available_inputs()
                self._retry_provider_actions()
                self._refresh_readiness()
                if self.runtime["status"] in {"paused", "closed", "completed"}:
                    continue
                if not self.runtime["queue"] and not self._calls.futures:
                    from .questions import open_links
                    if self._has_global_user_question() or self.runtime.get("waiting_actions") or open_links(self.runtime) or self.runtime["cycles"] >= self.instance["config"]["max_cycles"]:
                        self.runtime["status"] = "waiting"
                    else:
                        self.runtime["queue"].append({"id": new_id("AC"), "role": "research_preparation", "reason": "use prior results and remaining research questions"})
                        self.runtime["status"] = "ready"
                resources = self._slots.snapshot()
                action = next((a for a in list(self.runtime["queue"])
                               if (not finishing and (not draining or a.get("live"))) and self._dispatchable(a, resources)), None)
                if action is not None:
                    if action["role"] == "formal_check":
                        self._formal(action)
                    elif self._process_machine_action(action):
                        pass
                    else:
                        generator = self._call_steps(action, deadline)
                        try:
                            arguments = next(generator)
                        except StopIteration:
                            pass
                        else:
                            self._calls.start(generator, self.runner, arguments)
                    if not action.get("live"):
                        steps += 1
                    continue
                if self._calls.futures:
                    time.sleep(.02)
                    continue
                noncapacity = any(a.get("dispatch_wait", {}).get("kind") not in {None, "capacity"} for a in self.runtime["queue"])
                self.runtime["status"] = "waiting" if not self.runtime["queue"] or noncapacity else "capacity_waiting"
                self._save()
                if not watch:
                    break
                time.sleep(.2)
            if self.runtime["status"] not in {"paused", "closed", "completed", "waiting", "capacity_waiting"}:
                self.runtime["status"] = "ready"
            self._save()
        finally:
            self._calls.close()
            self._calls = None
            self._slots.close()
            self._slots = None
