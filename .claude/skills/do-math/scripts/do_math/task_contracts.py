"""Feature-5 task obligations, derived readiness, and repeat lineages.

The module is deliberately pure: activity waiting and lifecycle transitions remain
with their owners.  It supplies the task facts those owners must consume.
"""
from __future__ import annotations

from copy import deepcopy
from collections import Counter

from .file_io import require_text

from .contracts import ITEM_DISPOSITION


LIFECYCLE_STATES = frozenset({"planned", "active", "waiting", "completed", "closed"})
# The item disposition kinds, as the wire schema ITEM_DISPOSITION defines them.
DISPOSITION_KINDS = frozenset(option["properties"]["kind"]["const"] for option in ITEM_DISPOSITION["anyOf"])
REPEAT_LINEAGES = ("import_rework", "selection_failure", "exhaustion_empty", "proposal_version", "contract_revision")
# Governance views every role receives; like tool references they name no file.
CONTEXT_INPUT_REFS = frozenset({"context:goal", "context:policy"})
# Configured tools a task may name as inputs.
TOOL_INPUT_REFS = frozenset({"tool:lean", "tool:scholarly"})
# Documents and governance views every role receives, whatever the host.
FIXED_INPUT_REFS = frozenset({"SKILL.md", "GLOSSARY.md"}) | CONTEXT_INPUT_REFS
# The record family whose citation stands in for each specialist judge (designated_judgment).
JUDGE_EVIDENCE_FAMILIES = {"formal_check": "formal-result", "identity_review": "identity-assessment",
                           "goal_audit": "goal-judgment"}


def available_input_refs(instance: dict, runtime: dict, *, lean_available: bool) -> list[str]:
    """Input references a role may copy into a task, derived on demand and never stored.

    Fixed documents, configured tools, knowledge, tasks and source aliases come
    from state. Whether a local Lean was discovered is a host fact the caller passes.
    """
    from .input_basis import aliases
    config = instance.get("config", {})
    result = set(FIXED_INPUT_REFS)
    if config.get("lean_command") or lean_available:
        result.add("tool:lean")
    if config.get("scholarly_enabled") and config.get("scholarly_server"):
        result.add("tool:scholarly")
    result.update(instance.get("knowledge", {}))
    result.update(runtime.get("tasks", {}))
    for source in instance.get("sources", []):
        result.update(aliases(source))
    return sorted(result)


def unsupplied_task_inputs(refs, supplied, *, admit_named_sources: bool) -> list[str]:
    """Task inputs and reuse must name a supplied input or an existing record.

    This is the common execution contract (`available_input_refs` or a supplied
    record). A candidate may name a `source:` input that does not exist yet;
    readiness passes admit_named_sources=False and waits until it does.
    """
    return sorted({ref for ref in refs if ref not in supplied
                   and not (admit_named_sources and ref.startswith("source:"))})


def prepared_dependencies(candidate, condition, titles=None):
    """An extension adds prerequisites; omitted fields never erase the contract."""
    names = titles or {}
    return list(dict.fromkeys(names.get(ref, ref) for ref in
        [*candidate.get('dependencies', []), *condition.get('dependencies', [])]))


def _distinct_ids(rows: list[dict], name: str) -> None:
    values = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(values) != len(rows) or any(not isinstance(value, str) or not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{name} must have distinct stable IDs")


def contract_obligations(task: dict) -> list[dict]:
    """Return the authoritative completion obligations, never a cached remainder."""
    obligations = task.get("completion_obligations", [])
    if not isinstance(obligations, list):
        raise ValueError("completion_obligations must be a list")
    return obligations


def validate_contract_meaning(task: dict) -> None:
    """What no task schema expresses: distinct obligation, criterion and profile IDs."""
    for name in ("progress_criteria", "completion_obligations"):
        _distinct_ids(task[name], name)
    profiles = [ref["id"] for ref in task.get("profile_refs", [])]
    if len(profiles) != len(set(profiles)):
        raise ValueError('profile_refs must identify distinct profiles')


def validate_task_contract(task: dict) -> None:
    """A stored or engine-built contract in memory: the stored task schema, then its rules.

    These are the two checks the storage gate applies when the task is saved;
    the stored schema is the one shape rule (nonempty text and lists, positive
    revision, judged obligations, distinct evidence). A produced candidate is
    checked by the wire TASK_CANDIDATE and validate_contract_meaning instead
    (contracts.task_candidate_record).
    """
    from .state_contract import default_state_contract, validate_record
    validate_record(default_state_contract().family("runtime", "tasks").checker, task, "task")
    validate_contract_meaning(task)


def judge_coverage_errors(role: str, execution_id: str, task: dict, assessment: dict, families: dict) -> list[str]:
    """A fulfilment by an assessor outside an obligation's judges must cite its judges' evidence.

    `families` maps the cited IDs the caller can see to their record family. The
    producer derives it from its catalog; the receiver from current records and
    then also checks that the cited judgment is current (task_scope.designated_judgment).
    """
    obligations = {row["id"]: row for row in contract_obligations(task)}
    errors = []
    for row in assessment.get("item_dispositions", []):
        obligation = obligations.get(row.get("obligation_id"))
        if row.get("kind") != "fulfilled" or obligation is None:
            continue
        judges = obligation["judges"]
        if role in judges or execution_id in judges:
            continue
        wanted = {JUDGE_EVIDENCE_FAMILIES[judge] for judge in judges if judge in JUDGE_EVIDENCE_FAMILIES}
        if not any(families.get(ref) in wanted for ref in row.get("evidence_refs", [])):
            errors.append("fulfilled obligation " + row["obligation_id"] + " needs its designated judge "
                          + repr(sorted(judges)) + " or cited evidence of the family " + repr(sorted(wanted)))
    return errors


def _row_by_obligation(assessment: dict) -> dict[str, dict]:
    rows = assessment.get("item_dispositions", [])
    if not isinstance(rows, list):
        raise ValueError("item_dispositions must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("item disposition must be an object")
        identifier = row.get("obligation_id")
        if not isinstance(identifier, str) or not identifier or identifier in result:
            raise ValueError("item dispositions must identify each obligation at most once")
        if row.get("kind") not in DISPOSITION_KINDS:
            raise ValueError("unknown item disposition")
        if "evidence_refs" not in row:
            raise ValueError("item disposition requires evidence_refs")
        evidence = row["evidence_refs"]
        if not isinstance(evidence, list) or not all(isinstance(value, str) and value for value in evidence) or len(evidence) != len(set(evidence)):
            raise ValueError("item disposition evidence_refs must be distinct references")
        result[identifier] = row
    return result


def validate_item_dispositions(task: dict, assessment: dict, *, require_complete: bool = False) -> None:
    validate_task_contract(task)
    if not isinstance(assessment, dict):
        raise ValueError("assessment must be an object")
    terminal = assessment.get('decision') in {'completed', 'closed'}
    require_complete = require_complete or terminal
    if task.get('status') in {'completed', 'closed'} and assessment.get('decision') != task['status']:
        raise ValueError('terminal task status differs from its assessment decision')
    obligations = {row["id"]: row for row in contract_obligations(task)}
    rows = _row_by_obligation(assessment)
    if set(rows) - set(obligations):
        raise ValueError("item disposition names an unknown obligation")
    unresolved = assessment.get("unresolved", [])
    if not isinstance(unresolved, list):
        raise ValueError("unresolved must be a list")
    unresolved_ids = set()
    for row in unresolved:
        if not isinstance(row, dict) or set(row) != {"obligation_id", "missing_inputs", "next_owner"}:
            raise ValueError("unresolved inspection needs obligation_id, missing_inputs, and next_owner")
        identifier = row["obligation_id"]
        if identifier not in obligations or identifier in unresolved_ids or identifier in rows:
            raise ValueError("unresolved inspection must name one undisposed obligation")
        unresolved_ids.add(identifier)
        if not isinstance(row["missing_inputs"], list) or not row["missing_inputs"] or any(not isinstance(v,str) or not v for v in row['missing_inputs']):
            raise ValueError("unresolved inspection needs missing inputs")
        require_text(row["next_owner"], "unresolved.next_owner")
    for identifier, row in rows.items():
        obligation = obligations[identifier]
        required = set(obligation.get("evidence_required", []))
        if row["kind"] == "fulfilled" and not required <= set(row["evidence_refs"]):
            raise ValueError("item disposition lacks required evidence: " + identifier)
        if row["kind"] == "waived":
            if not isinstance(row.get("authority_ref"), str) or not row["authority_ref"]:
                raise ValueError("waived obligation needs authority_ref")
        if row["kind"] == "transferred":
            if not all(isinstance(row.get(key), str) and row[key] for key in ("authority_ref", "target_task_id", "target_obligation_id")):
                raise ValueError("transferred obligation needs authority and target obligation")
    if set(obligations) != set(rows) | unresolved_ids:
        raise ValueError("every obligation requires a disposition or unresolved inspection")
    if require_complete and (set(obligations) - set(rows) or unresolved_ids):
        raise ValueError("unresolved or undisposed completion obligations remain")
    if require_complete and any(row['kind'] == 'open' for row in rows.values()):
        raise ValueError("terminal assessment retains open obligations")
    if assessment.get('decision') == 'completed' and any(row['kind'] == 'transferred' for row in rows.values()):
        raise ValueError('completed assessment retains transferred obligations; use closed for authorized scope termination')
    if assessment.get('decision') == 'closed' and not any(row['kind'] in {'waived', 'transferred'} for row in rows.values()):
        raise ValueError('closure needs an authoritative scope disposition')


def remaining_obligations(task: dict, assessment: dict | None = None) -> list[str]:
    """Compute residual task scope from current obligation dispositions."""
    obligations = {row["id"] for row in contract_obligations(task)}
    if assessment:
        validate_item_dispositions(task, assessment)
    rows = _row_by_obligation(assessment or {})
    closed = {identifier for identifier, row in rows.items() if row["kind"] in {"fulfilled", "waived", "transferred"}}
    return sorted(obligations - closed)


def returned_task_ids(tasks):
    from .planning import contract_hash
    from .repository import exact_content_hash
    return sorted(identifier for identifier, task in tasks.items()
        if task.get('status') not in {'completed', 'closed'} and task.get('results') and (
            task.get('assessment', {}).get('results_sha256') != exact_content_hash(task['results']) or
            task.get('assessment', {}).get('contract_sha256') != contract_hash(task) or
            task.get('assessment', {}).get('current') is False))


def selected_task_ids(plan):
    return [row['task_id'] for row in plan['dispositions'] if row['kind'] == 'selected']


def validate_plan_dispositions(plan: dict, tasks: dict, ready_ids: list[str]) -> None:
    """The meaning of a plan the research_plan wire schema has already shaped (PLAN_DISPOSITION)."""
    if set(ready_ids)-set(tasks):
        raise ValueError('ready population names an unknown task')
    supplied = [row['task_id'] for row in plan['dispositions']]
    counts = Counter(supplied)
    if len(supplied) != len(counts) or set(counts) != set(ready_ids):
        raise ValueError("plan must dispose every derived-ready task exactly once: "
            f"missing={sorted(set(ready_ids) - set(counts))}; "
            f"unexpected={sorted(set(counts) - set(ready_ids))}; "
            f"duplicate={sorted(identifier for identifier, count in counts.items() if count > 1)}")
    for row in plan['dispositions']:
        if row['kind'] == 'selected':
            require_text(row.get('expected_research_change'), 'expected_research_change')
        else:
            revisit = row.get('revisit', {})
            if not revisit.get('event_refs') and not revisit.get('at'):
                raise ValueError('nonselection requires a reobservation condition')
            if revisit.get('at'):
                from .file_io import parse_utc
                parse_utc(revisit['at'])
        if row['kind'] == 'not_assessable' and not row.get('missing_inputs'):
            raise ValueError('not_assessable requires missing inputs')
        parallel = row.get('parallel_task_ids', [])
        if len(parallel) != len(set(parallel)) or set(parallel) - set(tasks) or row['task_id'] in parallel:
            raise ValueError('parallel references must identify distinct other tasks')
    assessments = plan['task_assessments']
    assessed = [row['task_id'] for row in assessments]
    if len(assessed) != len(set(assessed)) or set(assessed) != set(returned_task_ids(tasks)):
        raise ValueError('plan must assess every returned task exactly once')
    if set(selected_task_ids(plan)) & set(assessed):
        raise ValueError('returned tasks require disposition before a later selection')
    for assessment in assessments:
        task = tasks.get(assessment["task_id"])
        if task is None:
            raise ValueError("assessment names an unknown task")
        validate_item_dispositions(task, assessment, require_complete=assessment.get("decision") in {"completed", "closed"})


def repetition_lineages(runtime: dict, task_id: str | None = None, *,
                        include_events: bool = True) -> dict[str, dict]:
    """Count independent histories without turning a count into an authority decision."""
    rows = runtime.get("history", [])
    result = {name: {"count": 0, "owner": "ai", "events": []} for name in REPEAT_LINEAGES}
    baselines={}
    for row in rows:
        if not isinstance(row, dict) or row.get('kind') != 'task_repetition' or row.get('lineage') not in result:
            continue
        if task_id is not None and row['lineage'] == 'contract_revision' and row['lineage_id'] != task_id:
            continue
        name = row['lineage']
        counts = result[name].setdefault('by_lineage', {})
        key = row['lineage_id']
        if row['outcome']=='continued':baselines[name,key]=row.get('baseline_revision',0)
        if row['outcome'] in {'accepted', 'contracts_preserved', 'continued'}:
            counts[key] = 0
        elif 'version' in row:
            counts[key] = row['version']-baselines.get((name,key),0)
        elif row['outcome'] not in {'premises_changed', 'capacity_wait', 'input_overflow', 'waiting', 'transport_failure','unclassified_failure'}:
            counts[key] = counts.get(key, 0) + 1
        result[name]["count"] = sum(counts.values())
        if include_events:
            result[name]["events"].append(deepcopy(row))
        if row.get("owner") == "user":
            result[name]["owner"] = "user"
    return result
