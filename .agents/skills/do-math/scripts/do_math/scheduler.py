"""Instance scheduler: model calls run concurrently, state transitions run serially."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import time

from .model_policy import ASSESSMENT_SCHEMA, assessment_tier, selection
from .parallel import ModelCalls
from .session_slots import SessionSlots

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
        entries = self.runtime["executions"][execution_id].get("extensions", {}).get("model_assessments", [])
        if entries and action["role"] not in {"research_preparation", "research_plan"}:
            raise ValueError("only preparation and planning author model assessments")
        identified = {}
        for entry in entries:
            key_name = "task_title" if action["role"] == "research_preparation" else "task_id"
            if set(entry) != {key_name, "difficulty", "importance", "reason"}:
                raise ValueError("model assessment fields differ from the role contract")
            key = entry[key_name]
            if not isinstance(key, str) or key in identified:
                raise ValueError("model assessments require distinct task identities")
            assessment = {k: entry[k] for k in ("difficulty", "importance", "reason")}
            assessment_tier(assessment)
            identified[key] = assessment
        if action["role"] == "research_preparation":
            titles = {candidate["title"] for candidate in output["candidates"]}
            if set(identified) - titles:
                raise ValueError("model assessment does not name a prepared task")
            for candidate in output["candidates"]:
                if candidate["title"] in identified:
                    candidate["model_assessment"] = identified[candidate["title"]]
        elif action["role"] == "research_plan":
            if set(identified) - set(output["selections"]):
                raise ValueError("model assessment does not name a selected task")
            self.runtime["executions"][execution_id]["model_decisions"] = identified

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

    def _dispatchable(self, action, resources):
        live = [e for e in self.runtime["executions"].values() if e["status"] != "ended"]
        if any(e.get("action", {}).get("id") == action.get("id") for e in live if action.get("id")):
            return False
        role, target = action["role"], action.get("target")
        identity_keys = ("role", "target", "stage", "slot", "round", "review_cycle_id", "basis")
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
        pool = "work" if role in WORK_ROLES else "operations"
        cell = resources[pool].get(chosen["model"], {"available": 0})
        return cell["available"] > 0

    def _run_parallel(self, *, max_steps=None, watch=False):
        from .repository import new_id
        self._slots = SessionSlots(Path(self.instance["workspace"]), self.instance["id"])
        self._slots.configure(self.instance["config"]["session_limits"])
        self._calls = ModelCalls()
        deadline = time.monotonic() + self.instance["config"]["run_timeout_seconds"]
        steps = 0
        try:
            while True:
                self._controls()
                self._calls.collect()
                if self._installation_manifest() != self._installation:
                    self.runtime["status"] = "paused"
                    message = "Installed code or role documents changed. Restart the executor to load one consistent version, then resume."
                    if message not in self.runtime["questions"]:
                        self.runtime["questions"].append(message)
                    self._save()
                stopping = self.runtime["status"] in {"paused", "closed", "completed"} or time.monotonic() >= deadline
                if stopping:
                    if not self._calls.futures:
                        break
                    time.sleep(.02)
                    continue
                draining = max_steps is not None and steps >= max_steps
                if draining:
                    if not self._calls.futures:
                        break
                self.instance["available_input_refs"] = self._available_inputs()
                self._refresh_readiness()
                if self.runtime["status"] in {"paused", "closed", "completed"}:
                    continue
                if not self.runtime["queue"] and not self._calls.futures:
                    if self.runtime["questions"] or self.runtime["cycles"] >= self.instance["config"]["max_cycles"]:
                        self.runtime["status"] = "waiting"
                    else:
                        self.runtime["queue"].append({"id": new_id("AC"), "role": "research_preparation", "reason": "use prior results and remaining research questions"})
                        self.runtime["cycles"] += 1
                        self.runtime["status"] = "ready"
                resources = self._slots.snapshot()
                action = next((a for a in list(self.runtime["queue"])
                               if (not draining or a.get("live")) and self._dispatchable(a, resources)), None)
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
                self.runtime["status"] = "waiting" if not self.runtime["queue"] else "capacity_waiting"
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
