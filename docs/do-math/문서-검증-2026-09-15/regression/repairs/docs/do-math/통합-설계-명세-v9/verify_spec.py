"""Offline validation of the specification, never an execution-engine test."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import io
import json
import re
import platform
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

import spec_checks as checks
import build_spec

ROOT = Path(__file__).resolve().parent
BASE = "https://do-math.invalid/schemas/draft/9/"
SCHEMAS = {p.name.removesuffix(".schema.json"): checks.parse_json(p.read_bytes())
           for p in sorted((ROOT / "schemas").glob("*.schema.json"))}
REGISTRY = Registry().with_resources((schema["$id"], Resource.from_contents(schema))
                                     for schema in SCHEMAS.values())
FORMATS = FormatChecker()


@FORMATS.checks("do-math-duration", raises=(ValueError, TypeError))
def valid_duration(value):
    if not isinstance(value, str):
        return True
    checks.duration_ms(value)
    return True


@FORMATS.checks("do-math-path")
def valid_path(value):
    return not isinstance(value, str) or checks.safe_path(value)


def validator(schema):
    return Draft202012Validator(schema, registry=REGISTRY, format_checker=FORMATS)


def validate(family, value, *, review_policy=None, target_execution=None):
    errors = sorted(validator(SCHEMAS[family]).iter_errors(value), key=lambda e: str(list(e.path)))
    if errors:
        raise checks.ContractError(str(list(errors[0].path)) + ": " + errors[0].message)
    if family == "budget":
        checks.validate_budget(value)
    elif family == "explanation":
        checks.check_explanation_summary(value)
    elif family == "resource-reservation":
        checks.validate_reservation(value)
    elif family == "operational-review" and target_execution is not None:
        checks.check_operational_review(value, target_execution)
    elif family == "execution":
        matches = [row for row in build_spec.ROLE_CONTRACTS if
                   all(row[key] == value[key] for key in ("actor_kind", "activity_kind", "stage"))]
        if len(matches) != 1 or value["output_schema_id"] != BASE + matches[0]["output_family"]:
            raise checks.ContractError("execution output does not match assigned role/stage")
        if matches[0].get("output_phases") and value["output_phase"] not in matches[0]["output_phases"]:
            raise checks.ContractError("execution phase does not match assigned review stage")
    elif family == "review-policy":
        perspectives = value["required_perspectives"]
        names = [p["name"] for p in perspectives]
        if len(names) != len(set(names)) or not {"argument_reconstruction", "adversarial_scope", "semantic_identity"} <= set(names):
            raise checks.ContractError("three distinct basic perspectives required")
        allocation = checks.review_execution_allocation(sum(p["count"] for p in perspectives),
                                                        objection_round_limit=value["objection_round_limit"])
        minimum = sum(allocation.values())
        if value["execution_limit"] < minimum:
            raise checks.ContractError("planning, reviewers, organizer, answers and judges do not fit")
        slots = [j["id"] for j in value["final_judges"]]
        if len(set(slots)) != 3:
            raise checks.ContractError("three distinct judge slots required")
        if {j["perspective"] for j in value["final_judges"]} != {"objection_establishment", "objection_rebuttal", "context_comparison"}:
            raise checks.ContractError("three judge perspectives required")
    elif family == "review-plan":
        slots = value["role_slots"]
        ids = [s["id"] for s in slots]
        if len(ids) != len(set(ids)):
            raise checks.ContractError("duplicate review slot")
        expected_views = {"argument_reconstruction", "adversarial_scope", "semantic_identity",
                          *("domain_expertise:" + d for d in value["required_domains"])}
        if not expected_views <= {s["perspective"] for s in slots}:
            raise checks.ContractError("missing required review perspective")
        n = value["initial_execution_count"]
        allocation = checks.review_execution_allocation(n,
            organize_count=value["reserved_organize_executions"],
            answer_count=value["reserved_answer_executions"], judge_count=value["reserved_final_executions"],
            objection_round_limit=review_policy["objection_round_limit"] if review_policy is not None else None)
        if review_policy is not None and value["execution_limit"] != review_policy["execution_limit"]:
            raise checks.ContractError("review plan limit differs from its resolved policy")
        if n != len(slots) or sum(allocation.values()) > value["execution_limit"]:
            raise checks.ContractError("review plan cannot fund mandatory allocation")
        universe = set(value["proposal_item_ids"])
        for slot in slots:
            if set(slot["scope_item_ids"]) != universe:
                raise checks.ContractError("every reviewer must be assigned the full proposal")
        for conclusion in value["conclusion_dependencies"]:
            closure = {conclusion["conclusion_id"], *conclusion["dependency_item_ids"]}
            if not closure <= universe:
                raise checks.ContractError("conclusion references unknown item")
    elif family == "issue-state":
        checks.validate_review_reserve(value)
        ids = [s["id"] for s in value["role_slots"]]
        if len(ids) != len(set(ids)) or not set(value["judge_slot_ids"]) <= set(ids):
            raise checks.ContractError("invalid issue-state role slots")
        for issue in value["issues"]:
            ids = [row["slot_id"] for row in issue["judge_results"]]
            if len(ids) != len(set(ids)) or not set(ids) <= set(value["judge_slot_ids"]):
                raise checks.ContractError("duplicate or unassigned judge")
            if issue["state"] in ("approved", "rejected"):
                verdict = "approved" if issue["state"] == "approved" else "rejected"
                if set(ids) != set(value["judge_slot_ids"]) or any(row["value"] != verdict for row in issue["judge_results"]):
                    raise checks.ContractError("closed objection needs all assigned judges")
    elif family == "activity-result" and value["kind"] == "research_preparation":
        p = value["payload"]
        if p["regenerate_after"] <= p["observed_at"]:
            raise checks.ContractError("regenerate_after must be in the observed future")
    elif family == "kind-definition":
        if value["family"] == "frontier":
            allowed = set(SCHEMAS["knowledge"]["properties"]) - {
                "from_ref", "to_ref", "assessment_refs", "formal_result_refs", "avoid_terms",
                "information_status", "source_refs", "scope", "excluded_scope",
                "family", "token", "meaning", "constraints", "external_rejection", "related_refs"}
            if not set(value["constraints"]["required_fields"]) <= allowed:
                raise checks.ContractError("kind definition introduces unknown/wrong-family fields")
    elif family == "input-manifest":
        if value["token_count"] > value["max_input_tokens"]:
            raise checks.ContractError("context_overflow")
        for entry in value.get("transcript", []):
            if entry["restore_form"] == "reference" and entry["content_ref"] not in value["reference_read_refs"]:
                raise checks.ContractError("reference-form transcript entry outside read scope")
        order = value["provided_order"]
        stable = [c for c in order if c in ("common_documents", "role_documents", "governance", "transcript", "canon_listing")]
        volatile = [c for c in order if c in ("candidate_listing", "recent_history", "preparation_history", "question")]
        if stable and volatile and max(order.index(c) for c in stable) > min(order.index(c) for c in volatile):
            raise checks.ContractError("stable components must precede per-round components")
        planning = value.get("planning_input")
        if planning:
            for key in ("candidate_listing", "canon_listing"):
                listing = planning[key]
                ids = [item["id"] for item in listing["items"]]
                if (len(ids) != len(set(ids)) or listing["loaded_count"] != len(ids)
                    or listing["total_count"] < len(ids)
                    or listing["truncated"] != (len(ids) < listing["total_count"])):
                    raise checks.ContractError("listing population/count/truncation mismatch")
            if planning["candidate_listing"]["order"] != "sealed_random":
                raise checks.ContractError("candidate listing must use the sealed random order")
            if planning["canon_listing"]["order"] != "id" and not planning["canon_listing"]["truncated"]:
                raise checks.ContractError("full canon listing must be in ID order")
            for item in planning["canon_listing"]["items"]:
                links = item["refs"]["explanation_links"]
                states = [{"assessment_value": link["assessment_value"], "use_state": link["use_state"]} for link in links]
                valid_link = any(link["use_state"] == "active" and link["assessment_value"] == "match" for link in links)
                view = item["view"]
                if (view["explanation_states"] != states or view["valid_explanation_available"] != valid_link
                        or view["recently_changed"] != bool(item["refs"]["change_refs"])):
                    raise checks.ContractError("canon view does not match its references")
    elif family == "plan":
        ids = [row["task_id"] for row in value["candidate_dispositions"]]
        selected = {row["task_id"] for row in value["candidate_dispositions"] if row["value"] == "selected"}
        if len(ids) != len(set(ids)) or set(value["dispatch_order"]) != selected:
            raise checks.ContractError("dispatch order does not match unique selected candidates")
    elif family == "task":
        scope = {item["id"] for item in value["contract"]["scope"]}
        disposition_ids = [item["scope_id"] for item in value["scope_dispositions"]]
        if len(disposition_ids) != len(set(disposition_ids)) or not set(disposition_ids) <= scope:
            raise checks.ContractError("unknown or duplicate scope disposition")
        remaining = set(scope)
        for item in value["scope_dispositions"]:
            if item["value"] in ("fulfilled", "waived", "transferred"):
                if not item["evidence_refs"]:
                    raise checks.ContractError("scope disposition needs evidence")
                if item["value"] == "transferred" and not item["successor_task_ids"]:
                    raise checks.ContractError("transferred scope needs a successor")
                remaining.discard(item["scope_id"])
        if set(value["remaining_scope_ids"]) != remaining:
            raise checks.ContractError("remaining scope does not match obligations")
        if value["state"] == "completed" and (remaining or any(x["value"] == "transferred" for x in value["scope_dispositions"])):
            raise checks.ContractError("completed task has open/transferred scope")
    return True


def deref(schema):
    target = schema["$ref"]
    uri, _, fragment = target.partition("#")
    if not uri.startswith(BASE):
        raise checks.ContractError("external schema reference")
    result = SCHEMAS[uri[len(BASE):]]
    for key in fragment.split("/")[1:]:
        result = result[key.replace("~1", "/").replace("~0", "~")]
    return result


def sample(schema):
    """Create structural examples only; independent negative tests are below."""
    if "$ref" in schema:
        return sample(deref(schema))
    if "const" in schema:
        return copy.deepcopy(schema["const"])
    if "enum" in schema:
        return copy.deepcopy(schema["enum"][0])
    if "oneOf" in schema:
        return sample(schema["oneOf"][0])
    if "allOf" in schema and "type" not in schema and "properties" not in schema:
        return sample(schema["allOf"][0])
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = kind[0]
    if kind == "object" or "properties" in schema:
        value = {key: sample(schema["properties"][key]) for key in schema.get("required", [])}
        apply_constraints(value, schema)
        return value
    if kind == "array":
        return [sample(schema["items"]) for _ in range(schema.get("minItems", 0))]
    if kind == "boolean":
        return False
    if kind == "integer":
        return schema.get("minimum", 0)
    if kind == "null":
        return None
    if kind == "string":
        fmt, pattern = schema.get("format"), schema.get("pattern", "")
        if fmt == "date-time":
            return "2026-09-07T00:00:00.000Z"
        if fmt == "do-math-duration":
            return "PT1S"
        if fmt == "do-math-path":
            return "fixture/input.json"
        if "0-9a-f" in pattern:
            return "1" * (40 if "40" in pattern else 64)
        if "Crockford" in pattern or "0-7" in pattern:
            prefix = re.match(r"^\^([A-Z][A-Z0-9]*)-", pattern)
            return (prefix.group(1) if prefix else "F") + "-" + "0" * 25 + "1"
        if pattern.startswith("^(?:human:"):
            return "human:fixture"
        if pattern.startswith("^[0-9]+"):
            return "1"
        if pattern.startswith("^(?:/"):
            return "/state"
        return "fixture"
    return {}


def apply_constraints(value, schema):
    if "$ref" in schema:
        return apply_constraints(value, deref(schema))
    if not isinstance(value, dict):
        return
    for key in schema.get("required", []):
        if key not in value and key in schema.get("properties", {}):
            value[key] = sample(schema["properties"][key])
    for key, shape in schema.get("properties", {}).items():
        if key not in value:
            continue
        if "const" in shape:
            value[key] = copy.deepcopy(shape["const"])
        elif "enum" in shape and value[key] not in shape["enum"]:
            value[key] = shape["enum"][0]
        elif shape.get("maxItems") == 0:
            value[key] = []
        elif "properties" in shape or "$ref" in shape or "allOf" in shape:
            apply_constraints(value[key], shape)
    for forbidden in schema.get("not", {}).get("anyOf", []):
        for key in forbidden.get("required", []):
            value.pop(key, None)
    for clause in schema.get("allOf", []):
        if "if" in clause:
            if validator(clause["if"]).is_valid(value):
                then = clause["then"]
                for key in then.get("required", []):
                    if key not in value:
                        value[key] = sample(schema.get("properties", {}).get(key, {}))
                apply_constraints(value, then)
        else:
            apply_constraints(value, clause)


def make_examples():
    specimens = {}
    for family, schema in SCHEMAS.items():
        if family == "common":
            continue
        value = sample(schema)
        if "x-id-prefix" in schema:
            value["id"] = schema["x-id-prefix"] + "-" + "0" * 25 + "1"
        if family == "task":
            value["remaining_scope_ids"] = [x["id"] for x in value["contract"]["scope"]]
        if family == "review-policy":
            value["required_perspectives"] = [{"name": n, "count": 1} for n in
                ("argument_reconstruction", "adversarial_scope", "semantic_identity")]
            for i, judge in enumerate(value["final_judges"]):
                judge["id"] = "judge-" + str(i + 1)
                judge["perspective"] = ["objection_establishment", "objection_rebuttal", "context_comparison"][i]
            value["execution_limit"] = 14
            value["objection_round_limit"] = 3
        if family == "trust-environment":
            value["allowed_axioms"] = ["propext", "Quot.sound", "Classical.choice"]
        if family == "input-manifest":
            for i, doc in enumerate(value["common_documents"]):
                doc["path"] = ["SKILL.md", "GLOSSARY.md"][i]
            value["max_input_tokens"] = 100
            value["planning_input"]["actual_preparation_history_window"] = 0
            value["planning_input"]["candidate_listing"].update(order="sealed_random", shuffle_seed="1" * 64, algorithm="hmac-sort-v1")
            value["planning_input"]["canon_listing"].update(order="id")
            value["planning_input"]["canon_listing"].pop("shuffle_seed", None)
            value["planning_input"]["canon_listing"].pop("algorithm", None)
        if family == "activity-result" and value["kind"] == "research_preparation":
            value["payload"]["regenerate_after"] = "2026-09-07T00:00:01.000Z"
        if family == "review-plan":
            value.update(initial_execution_count=3, execution_limit=14, reserved_organize_executions=1, reserved_answer_executions=3,
                         reserved_final_executions=6, required_domains=[],
                         final_judge_slot_ids=["judge-1", "judge-2", "judge-3"])
            item = "MATH-" + "0" * 25 + "1"
            value["proposal_item_ids"] = [item]
            value["conclusion_dependencies"] = [{"conclusion_id": item, "dependency_item_ids": []}]
            for i, slot in enumerate(value["role_slots"]):
                slot.update(id="reviewer-" + str(i + 1), perspective=["argument_reconstruction", "adversarial_scope", "semantic_identity"][i],
                            scope_item_ids=[item])
        if family == "issue-state":
            template = value["role_slots"][0]
            value["role_slots"] = [dict(copy.deepcopy(template), id="judge-" + str(i + 1)) for i in range(3)]
            value["judge_slot_ids"] = ["judge-1", "judge-2", "judge-3"]
        if family == "review-result":
            value.update(scope_complete=True, verdict="match", objections=[], remaining_questions=[])
        if family == "execution":
            value["budget_kind"] = "operations"
            value["execution_deadline"] = "2026-09-07T01:00:00.000Z"
            value.pop("operational_review_mode", None)
            role = next(row for row in build_spec.ROLE_CONTRACTS if
                        all(row[key] == value[key] for key in ("actor_kind", "activity_kind", "stage")))
            value["output_schema_id"] = BASE + role["output_family"]
        if family == "kind-definition":
            value["constraints"] = {"allowed_epistemic_status": ["open"], "required_fields": []}
        if family == "command-response":
            value["result"] = {"instance_id": "RI-" + "0" * 25 + "1",
                               "snapshot_commit": "1" * 40, "activity_ids": []}
        specimens[family] = value
        target = ROOT / "fixtures" / "records" / (family + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(checks.canonical_json(value))
    # Explicit discriminant cases exercise every command branch.
    for direction in ("request", "response"):
        schema = SCHEMAS["command-" + direction]
        for command in schema["properties"]["command"]["enum"]:
            value = sample(schema)
            value["command"] = command
            field = "payload" if direction == "request" else "result"
            clause = next(c for c in schema["allOf"] if
                          c.get("if", {}).get("properties", {}).get("command", {}).get("const") == command)
            shape = clause["then"]["properties"][field]
            family_ref = shape.get("$ref", "").removeprefix(BASE)
            value[field] = copy.deepcopy(specimens[family_ref]) if family_ref in specimens else sample(shape)
            if command == "record" and direction == "response":
                value["result"]["id"] = "RI-" + "0" * 25 + "1"
            target = ROOT / "fixtures" / "commands" / (command + "." + direction + ".json")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(checks.canonical_json(value))
    return specimens


def read_example(family):
    return checks.parse_json((ROOT / "fixtures" / "records" / (family + ".json")).read_bytes())

def rows(values, prefix="reviewer"):
    return [{"slot_id": prefix + "-" + str(i + 1), "value": value} for i, value in enumerate(values)]


INITIAL_SLOTS = ["reviewer-1", "reviewer-2", "reviewer-3"]
JUDGE_SLOTS = ["judge-1", "judge-2", "judge-3"]


def source_map_matches(mapping):
    source = build_spec.DOC
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    vectors, quality = {}, {}
    for number, line in enumerate(lines, 1):
        columns = line.split(" | ")
        match = re.match(r"^\| (V\d+|Q\d+) \| ", line)
        if not match:
            continue
        key = match.group(1)
        if key.startswith("V"):
            vectors[key] = {"source_line": number, "input": columns[1],
                            "expected": columns[2].removesuffix(" |"),
                            "source_row_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest()}
        else:
            quality[key] = {"source_line": number, "guarantee": columns[1], "owner": columns[2],
                            "source_vectors": re.findall(r"V\d+", columns[3]),
                            "source_row_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest()}
    if mapping["source_sha256"] != hashlib.sha256(source.read_bytes()).hexdigest():
        raise checks.ContractError("source hash mismatch")
    if len(mapping["vectors"]) != len(vectors) or len(mapping["quality_contracts"]) != len(quality):
        raise checks.ContractError("source row count mismatch")
    for item in mapping["vectors"]:
        expected = vectors.get(item["id"])
        if expected is None or any(item.get(k) != value for k, value in expected.items()):
            raise checks.ContractError("source vector content mismatch")
        expected_rules = [rid for rid, _, _, ids, _ in build_spec.RULES if item["id"] in ids]
        if item["rule_ids"] != expected_rules or item["owner_section"] != "17.2":
            raise checks.ContractError("source vector owner/rule mismatch")
    for item in mapping["quality_contracts"]:
        expected = quality.get(item["id"])
        if expected is None or any(item.get(k) != value for k, value in expected.items()):
            raise checks.ContractError("quality contract content mismatch")
    return True


class SpecificationTests(unittest.TestCase):
    def test_schema_meta_and_offline_refs(self):
        for family, schema in SCHEMAS.items():
            with self.subTest(family=family):
                Draft202012Validator.check_schema(schema)
                def walk(node):
                    if isinstance(node, dict):
                        if "$ref" in node:
                            deref(node)
                        for item in node.values():
                            walk(item)
                    elif isinstance(node, list):
                        for item in node:
                            walk(item)
                walk(schema)

    def test_registry_exact_bijection_and_hash(self):
        registry = checks.parse_json((ROOT / "schema-registry.json").read_bytes())
        self.assertEqual(set(SCHEMAS), {r["family"] for r in registry["families"]})
        self.assertEqual(len(SCHEMAS), len(registry["families"]))
        for row in registry["families"]:
            self.assertEqual(row["sha256"], hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest())
            self.assertEqual(row["schema_id"], SCHEMAS[row["family"]]["$id"])
            schema = SCHEMAS[row["family"]]
            for field, annotation in (("contract_id", "x-contract-id"), ("owner_section", "x-owner-section"),
                                      ("storage", "x-storage"), ("id_prefix", "x-id-prefix")):
                self.assertEqual(row[field], schema.get(annotation))
        self.assertEqual(registry["identifier_prefixes"], {**build_spec.TYPED_IDS, **build_spec.TYPED_ARRAYS})

    def test_generated_schema_matches_authoring_source(self):
        expected = build_spec.schema_documents()
        self.assertEqual(set(expected), set(SCHEMAS))
        for name, schema in expected.items():
            self.assertEqual(schema, SCHEMAS[name], name)
            self.assertEqual((ROOT / "schemas" / (name + ".schema.json")).read_bytes(), checks.canonical_json(schema), name)

    def test_draft_schema_table_and_owner_sections(self):
        source = build_spec.DOC.read_text(encoding="utf-8-sig")
        table = source.split(build_spec.TABLE_START)[1].split(build_spec.TABLE_END)[0].strip()
        self.assertEqual(table, build_spec.schema_family_table(SCHEMAS))
        sections = set(re.findall(r"^#{2,4} (\d+(?:\.\d+)*)\.? ", source, re.MULTILINE))
        for schema in SCHEMAS.values():
            for section in schema["x-owner-section"].split(","):
                self.assertIn(section, sections, schema["$id"])
        rules = checks.parse_json((ROOT / "semantic-rules.json").read_bytes())["rules"]
        self.assertEqual(rules, [{"id": rid, "owner_section": section, "contract": statement,
            "source_vectors": vectors, "domain": domain,
            "enforcement": "Runtime/AI/evidence validation as described in the owner section; schema validity alone is insufficient."}
            for rid, section, statement, vectors, domain in build_spec.RULES])
        vector_ids = {row["id"] for row in checks.parse_json((ROOT / "source-vector-map.json").read_bytes())["vectors"]}
        for rule in rules:
            self.assertLessEqual(set(rule["source_vectors"]), vector_ids)
            for section in rule["owner_section"].split(","):
                self.assertIn(section, sections, rule["id"])

    def test_toolchain_lock(self):
        lock = checks.parse_json((ROOT / "toolchain-lock.json").read_bytes())
        self.assertEqual(lock["codec_profile"], "do-math-codec/9")
        self.assertEqual(lock["python"], platform.python_version())
        self.assertEqual(lock["implementation"], platform.python_implementation())
        for package, version in lock["packages"].items():
            self.assertEqual(importlib.metadata.version(package), version)

    def test_role_output_contracts_cover_every_stage(self):
        table = checks.parse_json((ROOT / "role-contracts.json").read_bytes())
        self.assertEqual(table["roles"], build_spec.ROLE_CONTRACTS)
        expected = {(kind, stage) for kind, stages in build_spec.STAGES.items() for stage in stages}
        actual = {(r["activity_kind"], r["stage"]) for r in table["roles"] if r["actor_kind"] == "ai"}
        self.assertEqual(actual, expected)
        for row in table["roles"]:
            self.assertIn(row["output_family"], SCHEMAS)

    def test_review_result_phase_authority(self):
        value = read_example("review-result")
        validate("review-result", value)
        value.update(phase="answer", answers=[])
        with self.assertRaises(checks.ContractError):
            validate("review-result", value)

        value.pop("verdict")
        value.pop("objections")
        validate("review-result", value)
        value.update(phase="judge", verdict="match", objection_verdicts=[])
        with self.assertRaises(checks.ContractError):
            validate("review-result", value)

    def test_execution_output_schema_binding(self):
        value = read_example("execution")
        validate("execution", value)
        value["output_schema_id"] = BASE + "assessment"
        with self.assertRaises(checks.ContractError):
            validate("execution", value)

    def test_all_structural_examples(self):
        for family in SCHEMAS:
            if family != "common":
                with self.subTest(family=family):
                    validate(family, read_example(family))

    def test_event_driven_continue_can_finish_without_rescheduling(self):
        review = read_example("operational-review")
        review.update(disposition="continue", uncertainties=[])
        review.pop("next_review_at", None)
        execution = read_example("execution")
        execution.update(activity_kind="research_work", stage="performing", budget_kind="work",
                         operational_review_mode="event_driven", task_id="T-" + "0" * 25 + "1",
                         task_revision=1)
        execution.pop("execution_deadline")
        validate("execution", execution)
        validate("operational-review", review, target_execution=execution)

        review["next_review_at"] = "2026-09-07T01:00:00.000Z"
        with self.assertRaises(checks.ContractError):
            validate("operational-review", review, target_execution=execution)
        review["uncertainties"] = ["The running tool needs another status check."]
        validate("operational-review", review, target_execution=execution)

        review["next_review_at"] = None
        with self.assertRaises(checks.ContractError):
            validate("operational-review", review, target_execution=execution)

    def test_periodic_continue_requires_time_from_bound_execution(self):
        review = read_example("operational-review")
        review.update(disposition="continue", uncertainties=[])
        review.pop("next_review_at", None)
        execution = read_example("execution")
        execution.update(activity_kind="identity_review", stage="planning", budget_kind="work",
                         output_schema_id=BASE + "review-plan", operational_review_mode="periodic",
                         next_operational_review_at="2026-09-07T01:00:00.000Z")
        execution.pop("execution_deadline")
        validate("execution", execution)
        validate("operational-review", review)  # The output alone does not contain the mode.
        with self.assertRaises(checks.ContractError):
            validate("operational-review", review, target_execution=execution)
        review["next_review_at"] = "2026-09-07T02:00:00.000Z"
        validate("operational-review", review, target_execution=execution)
        execution["id"] = "E-" + "0" * 25 + "2"
        with self.assertRaises(checks.ContractError):
            validate("operational-review", review, target_execution=execution)

    def test_every_command_branch(self):
        for path in sorted((ROOT / "fixtures" / "commands").glob("*.json")):
            family = "command-request" if ".request." in path.name else "command-response"
            with self.subTest(path=path.name):
                validate(family, checks.parse_json(path.read_bytes()))

    def test_unknown_record_fields_rejected(self):
        value = read_example("task")
        value["silent_permission"] = True
        with self.assertRaises(checks.ContractError):
            validate("task", value)

    def test_wrong_family_fields_rejected(self):
        value = read_example("knowledge")
        value["information_status"] = "fact"
        with self.assertRaises(checks.ContractError):
            validate("knowledge", value)

    def test_machine_has_no_ai_budget(self):
        value = read_example("execution")
        value["actor_kind"] = "machine"
        value["execution_deadline"] = "2026-09-07T01:00:00.000Z"
        with self.assertRaises(checks.ContractError):
            validate("execution", value)

    def test_queued_execution_has_no_reservation(self):
        value = read_example("execution")
        value["reservation_ids"] = ["RR-" + "0" * 25 + "2"]
        with self.assertRaises(checks.ContractError):
            validate("execution", value)

    def test_ended_execution_requires_end_record(self):
        value = read_example("execution")
        value["state"] = "ended"
        with self.assertRaises(checks.ContractError):
            validate("execution", value)

    def test_exact_ref_rejects_tree_input(self):
        value = read_example("task")
        value["contract"]["required_inputs"] = [{"ref_kind": "tree", "record_id": value["id"]}]
        with self.assertRaises(checks.ContractError):
            validate("task", value)

    def test_json_golden_unicode_and_controls(self):
        value = checks.parse_json('{"z":-0,"e\\u0301":"a\\nb","a":[]}')
        expected = '{\n  "a": [],\n  "z": 0,\n  "é": "a\\nb"\n}\n'.encode("utf-8")
        self.assertEqual(checks.canonical_json(value), expected)
        self.assertEqual(checks.canonical_json(checks.parse_json(expected)), expected)

    def test_json_duplicate_and_normalization_collision(self):
        for raw in ('{"x":1,"x":2}', '{"é":1,"e\\u0301":2}', '{"a":{"x":1,"x":2}}'):
            with self.subTest(raw=raw), self.assertRaises(checks.ContractError):
                checks.parse_json(raw)

    def test_json_forbidden_numbers_and_bom(self):
        for raw in ('{"n":1.0}', '{"n":NaN}', '{"n":9007199254740992}', '\ufeff{}'):
            with self.subTest(raw=raw), self.assertRaises(checks.ContractError):
                checks.parse_json(raw)

    def test_yaml_golden_empty_typed_and_body(self):
        raw = '---\nz: []\na: true\nb: 12\nc: {}\nd: "2026-09-07"\n---\n\n본문 e\u0301\n'
        expected = '---\na: true\nb: 12\nc: {}\nd: "2026-09-07"\nz: []\n---\n\n본문 e\u0301\n'.encode("utf-8")
        self.assertEqual(checks.canonical_knowledge(raw), expected)
        self.assertEqual(checks.canonical_knowledge(expected), expected)
        front, _ = checks.parse_knowledge(expected)
        self.assertIs(front["a"], True)
        self.assertEqual(type(front["b"]), int)
        self.assertEqual(type(front["d"]), str)

    def test_yaml_nested_duplicate_tags_and_aliases(self):
        for raw in ("a: 1\na: 2", "a: &x 1\nb: *x", "a: !!str 1",
                    "a:\n  é: 1\n  e\u0301: 2", "a: {x: 1, x: 2}", "a: 1.2"):
            with self.subTest(raw=raw), self.assertRaises((checks.ContractError, ValueError)):
                checks.canonical_knowledge("---\n" + raw + "\n---\n\nbody\n")

    def test_windows_lexical_paths(self):
        for value in ("../x", "/x", "a\\b", "a//b", "a/./b", "x:ads", "CON.txt", "a/b."):
            self.assertFalse(checks.safe_path(value), value)
        self.assertTrue(checks.safe_path("knowledge/정의.md"))

    def test_duration_positive_and_fixed_units(self):
        self.assertEqual(checks.duration_ms("PT24H"), 86400000)
        self.assertEqual(checks.duration_ms("PT0.001S"), 1)
        for value in ("PT0S", "P1M", "P1D", "PT", "PT0.0001S"):
            with self.assertRaises(checks.ContractError):
                checks.duration_ms(value)

    def test_shared_capacity_overcommit(self):
        value = read_example("budget")
        c = value["constraints"][0]
        c.update(work_slots=3, operations_slots=1, total_slots=3)
        with self.assertRaises(checks.ContractError):
            validate("budget", value)

    def test_reservation_cannot_return_consumed_usage(self):
        value = read_example("resource-reservation")
        value.update(reserved=10, confirmed_consumed=7, returned=4)
        with self.assertRaises(checks.ContractError):
            validate("resource-reservation", value)

    def test_execution_transition_barrier(self):
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        with self.assertRaises(checks.ContractError):
            checks.transition(machines, "execution", "stopping", "ended", {"local_processes_ended": True})
        self.assertEqual(checks.transition(machines, "execution", "stopping", "ended",
            {"local_processes_ended": True, "new_effect_paths_closed": True}), "ended")
        with self.assertRaises(checks.ContractError):
            checks.transition(machines, "execution", "ended", "running", {})

    def test_unknown_external_action_no_blind_retry(self):
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        with self.assertRaises(checks.ContractError):
            checks.transition(machines, "external-action", "unknown", "prepared", {"authority_valid": True})
        with self.assertRaises(checks.ContractError):
            checks.transition(machines, "external-action", "unknown", "cancelled", {})
        self.assertEqual(checks.transition(machines, "external-action", "unknown", "cancelled",
                                         {"not_invoked_proved": True}), "cancelled")

    def test_task_cannot_complete_with_live_execution(self):
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        with self.assertRaises(checks.ContractError):
            checks.transition(machines, "task", "active", "completed", {
                "all_scope_fulfilled_or_authoritatively_waived": True, "completion_assessment_valid": True})

    def test_task_cannot_hide_remaining_scope(self):
        value = read_example("task")
        value["remaining_scope_ids"] = []
        with self.assertRaises(checks.ContractError):
            validate("task", value)

    def test_initializing_pause_resume(self):
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        facts = {"recovery_valid": True, "permission_valid": True, "resume_lifecycle": "initializing"}
        self.assertEqual(checks.transition(machines, "lifecycle", "paused", "initializing", facts), "initializing")
        with self.assertRaises(checks.ContractError):
            checks.transition(machines, "lifecycle", "paused", "active", facts)

    def test_disagreement_is_unresolved(self):
        self.assertEqual(checks.aggregate_identity(rows(["mismatch"]*3), rows(["match", "match", "mismatch"], "judge"), True, True,
            expected_initial_slots=INITIAL_SLOTS, expected_judge_slots=JUDGE_SLOTS), "unresolved")
        self.assertEqual(checks.aggregate_identity(rows(["match"]*3), [], True, False,
            expected_initial_slots=INITIAL_SLOTS), "match")
        self.assertEqual(checks.aggregate_identity(rows([None, "match", "match"]), rows(["match"]*3, "judge"), True, False,
            expected_initial_slots=INITIAL_SLOTS, expected_judge_slots=JUDGE_SLOTS), "unresolved")

    def test_objection_round_boundary(self):
        for values, number, expected in [
            (["approved", "approved", "rejected"], 3, "unresolved"),
            (["rejected"]*3, 2, "answer_required"), (["rejected"]*3, 3, "rejected"),
            (["approved"]*3, 3, "approved")]:
            self.assertEqual(checks.aggregate_objection(rows(values, "judge"), number, 3,
                expected_slots=JUDGE_SLOTS), expected)

    def test_required_perspectives_and_execution_budget(self):
        value = read_example("review-policy")
        value["required_perspectives"][0]["name"] = "optional_view"
        with self.assertRaises(checks.ContractError):
            validate("review-policy", value)
        value = read_example("review-policy")
        value["execution_limit"] = 12
        with self.assertRaises(checks.ContractError):
            validate("review-policy", value)

    def test_review_budget_counts_organizer_and_boundary(self):
        expected = {"planning": 1, "initial": 3, "organize": 1, "answer": 3, "judge": 6}
        self.assertEqual(checks.review_execution_allocation(3), expected)
        self.assertEqual(sum(expected.values()), 14)
        for family in ("review-policy", "review-plan"):
            value = read_example(family)
            value["execution_limit"] = 13
            with self.assertRaises(checks.ContractError):
                validate(family, value)
            value["execution_limit"] = 14
            validate(family, value)
        value = read_example("review-plan")
        value["reserved_organize_executions"] = 2
        with self.assertRaises(checks.ContractError):
            validate("review-plan", value)
        value["execution_limit"] = 15
        validate("review-plan", value)
        value.pop("reserved_organize_executions")
        with self.assertRaises(checks.ContractError):
            validate("review-plan", value)

    def test_review_reserve_protects_pending_mandatory_stages(self):
        state = read_example("issue-state")
        state.update(executions_used=4, reserved_organize_executions=1,
                     reserved_answer_executions=3, reserved_final_executions=6, execution_limit=14)
        validate("issue-state", state)
        state["executions_used"] = 5  # Optional work cannot take the organizer's slot.
        with self.assertRaises(checks.ContractError):
            validate("issue-state", state)
        state["reserved_organize_executions"] = 0  # The assigned organizer consumes its own allocation.
        validate("issue-state", state)
        state.update(executions_used=14, reserved_answer_executions=0, reserved_final_executions=0)
        validate("issue-state", state)
        state["executions_used"] = 15
        with self.assertRaises(checks.ContractError):
            validate("issue-state", state)

    def test_review_output_is_bound_to_assigned_phase_and_slot(self):
        execution = read_example("execution")
        execution.update(activity_kind="identity_review", stage="clarifying",
                         output_schema_id=BASE + "review-result", output_phase="organize", role_slot_id="planner",
                         budget_kind="work", operational_review_mode="periodic",
                         next_operational_review_at="2026-09-07T01:00:00.000Z")
        execution.pop("execution_deadline")
        validate("execution", execution)
        output = read_example("review-result")
        output.pop("verdict")
        output.pop("objections")
        output.update(execution_id=execution["id"], owner_activity_id=execution["owner_activity_id"],
                      input_manifest_ref=execution["input_manifest_ref"], phase="organize", role_slot_id="planner",
                      organization={"issue_refs": [], "answer_requests": [], "supplement_requests": []})
        validate("review-result", output)
        checks.check_review_output(execution, output)
        output.pop("organization")
        output.update(phase="answer", answers=[])
        validate("review-result", output)  # Legal shape, wrong assigned phase.
        with self.assertRaises(checks.ContractError):
            checks.check_review_output(execution, output)
        execution["output_phase"] = "answer"
        checks.check_review_output(execution, output)
        output["role_slot_id"] = "another-reviewer"
        with self.assertRaises(checks.ContractError):
            checks.check_review_output(execution, output)
        execution["stage"] = "judging"
        self.assertFalse(validator(SCHEMAS["execution"]).is_valid(execution))
        with self.assertRaises(checks.ContractError):
            validate("execution", execution)

    def test_assessment_use_requires_confirmation_of_original_judgment(self):
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        facts = {"same_target_scope_inputs": True, "original_basis_current": True}
        for inadequate in ({}, {"new_match_valid": True}, {"new_satisfied_valid": True}):
            with self.assertRaises(checks.ContractError):
                checks.transition(machines, "assessment-use", "suspended", "active", facts | inadequate)
        confirmed = facts | {"original_assessment_revalidated": True}
        self.assertEqual(checks.transition(machines, "assessment-use", "suspended", "active", confirmed), "active")
        for key in facts:
            with self.assertRaises(checks.ContractError):
                checks.transition(machines, "assessment-use", "suspended", "active", confirmed | {key: False})
        for inadequate in ({"mismatch_valid": True}, {"not_satisfied_valid": True}, confirmed):
            with self.assertRaises(checks.ContractError):
                checks.transition(machines, "assessment-use", "suspended", "withdrawn", inadequate)
        self.assertEqual(checks.transition(machines, "assessment-use", "suspended", "withdrawn",
            {"original_assessment_error_confirmed": True}), "withdrawn")

    def test_relation_templates_are_inactive_and_enforce_evidence(self):
        document = checks.parse_json((ROOT / "relation-templates.json").read_bytes())
        self.assertEqual(document["templates"], build_spec.RELATION_TEMPLATES)
        self.assertEqual(len({t["token"] for t in document["templates"]}), 10)
        for template in document["templates"]:
            self.assertFalse({"id", "lifecycle", "origin_refs", "generated"} & set(template))
            definition = read_example("kind-definition")
            definition.update(copy.deepcopy(template))
            validate("kind-definition", definition)
            relation = {"type": "relation", "subkind": template["token"],
                        "evidence_refs": definition["origin_refs"]}
            if template["constraints"]["requires_assessment"]:
                with self.assertRaises(checks.ContractError):
                    checks.check_relation_constraints(relation, definition, from_family="frontier", to_family="frontier")
                relation.update(formal_result_refs=definition["origin_refs"], assessment_refs=definition["origin_refs"])
            checks.check_relation_constraints(relation, definition, from_family="frontier", to_family="frontier")
            with self.assertRaises(checks.ContractError):
                checks.check_relation_constraints(relation, definition, from_family="execution", to_family="frontier")
            definition["lifecycle"] = "withdrawn"
            with self.assertRaises(checks.ContractError):
                checks.check_relation_constraints(relation, definition, from_family="frontier", to_family="frontier")
    def test_listings_fit_or_escalate_without_permission(self):
        result = checks.pack_listings([3, 2], [4, 1], 10)
        self.assertEqual(result, {"mode": "full", "candidates": [0, 1], "canon": [0, 1], "remaining": 0})
        with self.assertRaises(checks.ContractError):
            checks.pack_listings([9, 3, 2], [4, 3], 10)

    def test_truncation_only_under_named_permission(self):
        result = checks.pack_listings([9, 3, 2], [4, 3], 10, permission={"lists": ["candidates"]})
        self.assertEqual(result["mode"], "truncated")
        self.assertEqual((result["candidates"], result["canon"]), ([1], [0, 1]))
        with self.assertRaises(checks.ContractError):
            checks.pack_listings([2], [7, 7], 10, permission={"lists": ["candidates"]})
        result = checks.pack_listings([2], [7, 7], 10, permission={"lists": ["canon"]})
        self.assertEqual((result["candidates"], result["canon"]), ([0], [0]))
        with self.assertRaises(checks.ContractError):
            checks.pack_listings([2], [7, 7], 10, permission={"lists": ["history"]})

    def test_overflow_disposition_and_restore_forms(self):
        self.assertEqual(checks.overflow_disposition(reducible_by_window=True, tool_accumulation=False,
                                                     activity_kind="research_plan"), "reduce_history")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="research_work"), "checkpoint_resume")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="identity_review", restored_fits=True), "reference_restore")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="identity_review", restored_fits=False), "escalate")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=False,
                                                     activity_kind="research_plan"), "escalate")
        with self.assertRaises(checks.ContractError):
            checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True, activity_kind="identity_review")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="research_plan"), "restart_with_failure_input")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="research_plan", prior_overflows=1), "escalate")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="identity_review", restored_fits=True, prior_overflows=1), "escalate")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=False,
                                                     activity_kind="identity_review", proposal_overflow=True), "close_unresolved_next_plan")
        entries = [{"role": "system"}, {"role": "user"}, {"role": "assistant"}, {"role": "tool"},
                   {"role": "user", "prior_version": True}, {"role": "assistant"}]
        self.assertEqual(checks.restore_forms(entries), ["full", "full", "full", "reference", "reference", "full"])
        with self.assertRaises(checks.ContractError):
            checks.restore_forms([{"role": "tool", "relevance_hint": "needed"}])

    def test_plan_binding_and_output_truncation(self):
        manifest = read_example("input-manifest")
        item = sample(SCHEMAS["input-manifest"]["properties"]["planning_input"]["properties"]["candidate_listing"]["properties"]["items"]["items"])
        item["id"] = "T-" + "0" * 25 + "1"
        item["view"]["revision"] = 2
        manifest["planning_input"]["candidate_listing"].update(items=[item], total_count=1, loaded_count=1)
        validate("input-manifest", manifest)
        plan = read_example("plan")
        plan["candidate_dispositions"] = [{"task_id": item["id"], "revision": 2, "value": "not_selected", "reason": "held",
                                           "information_status": "evidence", "uncertainty": "none", "read_scope_refs": []}]
        plan["dispatch_order"] = []
        validate("plan", plan)
        bound = checks.check_plan_binding(plan, manifest)
        self.assertEqual(bound[(item["id"], 2)], item["refs"]["record_ref"])
        plan["candidate_dispositions"][0]["task_id"] = "T-" + "0" * 25 + "2"
        with self.assertRaises(checks.ContractError):
            checks.check_plan_binding(plan, manifest)
        self.assertEqual(checks.plan_receipt_disposition("max_output"), "escalate_user_decision")
        self.assertEqual(checks.plan_receipt_disposition("end_turn"), "receive")

    def test_restoration_profile_requires_compaction_control(self):
        profile = read_example("execution-profile")
        with self.assertRaises(checks.ContractError):
            checks.check_restoration_profile(profile, "identity_review")
        profile["ai"]["compaction"]["disabled"] = True
        self.assertTrue(checks.check_restoration_profile(profile, "identity_review"))
        self.assertTrue(checks.check_restoration_profile(read_example("execution-profile"), "research_work"))

    def test_truncation_permission_alignment(self):
        manifest = read_example("input-manifest")
        planning = manifest["planning_input"]
        permission = {"lists": ["candidates"], "order": "sealed_random", "activity_kinds": ["research_plan"]}
        self.assertTrue(checks.check_truncation_permission(planning, permission))
        planning["candidate_listing"].update(total_count=5, truncated=True)
        self.assertTrue(checks.check_truncation_permission(planning, permission))
        with self.assertRaises(checks.ContractError):
            checks.check_truncation_permission(planning, {"lists": ["canon"], "order": "sealed_random"})
        with self.assertRaises(checks.ContractError):
            checks.check_truncation_permission(planning, {"lists": ["candidates"], "order": "id"})
        governance = read_example("governance")
        governance.update(kind="permission", payload=sample(SCHEMAS["governance"]["allOf"][3]["then"]["properties"]["payload"]))
        governance["payload"]["truncation"] = permission
        validate("governance", governance)
        governance["payload"]["truncation"] = {"lists": ["history"], "order": "id", "activity_kinds": ["research_plan"]}
        with self.assertRaises(checks.ContractError):
            validate("governance", governance)

    def test_provided_order_stable_components_first(self):
        manifest = read_example("input-manifest")
        manifest["provided_order"] = ["common_documents", "role_documents", "governance", "canon_listing",
                                      "candidate_listing", "recent_history", "question"]
        validate("input-manifest", manifest)
        manifest["provided_order"] = ["candidate_listing", "canon_listing"]
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", manifest)
        manifest["provided_order"] = ["listing"]
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", manifest)

    def test_exact_reference_bytes(self):
        data = b"actual bytes"
        ref = {"ref_kind": "artifact", "bundle_id": "AB-fixture", "path": "x",
               "sha256": hashlib.sha256(data).hexdigest()}
        self.assertEqual(checks.resolve_exact(ref, {}, {("AB-fixture", "x"): data}), data)
        with self.assertRaises(checks.ContractError):
            checks.resolve_exact(ref, {}, {("AB-fixture", "x"): b"other bytes"})

    def test_ast_error_dominates_true(self):
        node = {"op": "any", "args": [{"op": "always"}, {"op": "unknown"}]}
        self.assertEqual(checks.evaluate_condition(node, {}), "evaluation_error")
        self.assertEqual(checks.evaluate_condition({"op": "not", "arg": node}, {}), "evaluation_error")

    def test_ast_absence_vs_corruption(self):
        node = {"op": "record_exists", "space": "research", "record_id": "F-x", "family": "frontier"}
        self.assertEqual(checks.evaluate_condition(node, {"research": {}}), "false")
        self.assertEqual(checks.evaluate_condition(node, {"research": {"F-x": {"integrity": False}}}), "evaluation_error")

    def test_ast_cannot_read_prose_or_coerce_boolean(self):
        snapshot = {"research": {"F-x": {"integrity": True, "family": "frontier", "value": {"epistemic_status": "open", "title": "x"}}}}
        node = {"op": "record_field_equals", "space": "research", "record_id": "F-x", "pointer": "/title", "value": "x"}
        self.assertEqual(checks.evaluate_condition(node, snapshot), "evaluation_error")
        node.update(pointer="/epistemic_status", value="open")
        self.assertEqual(checks.evaluate_condition(node, snapshot), "true")

    def test_self_check_retransmission_and_new_anchor(self):
        state = {"seen": [], "anchor_ms": 0, "next_due_ms": 100, "max_interval_ms": 100,
                 "no_progress": 0, "no_progress_limit": 3, "review_due": False, "open_obligations": ["old"]}
        event = {"id": "a", "kind": "valid_response", "received_ms": 100, "value": "no_progress"}
        first = checks.update_self_check(state, event)
        self.assertEqual(first["next_due_ms"], 200)
        self.assertEqual(checks.update_self_check(first, event), first)
        second = checks.update_self_check(first, {**event, "id": "b", "received_ms": 200})
        third = checks.update_self_check(second, {**event, "id": "c", "received_ms": 300})
        self.assertTrue(third["review_due"])
        self.assertEqual(third["open_obligations"], ["old"])
        self.assertEqual(checks.update_self_check(third, {"id": "r", "kind": "rules_only"}), third)

    def test_self_check_deadline_uses_response_boundary(self):
        self.assertEqual(checks.self_check_deadline_ms(100, 20), 120)
        self.assertEqual(checks.self_check_deadline_ms(100, 20, tool_in_flight=True,
                                                     first_safe_boundary_ms=150), 170)
        self.assertIsNone(checks.self_check_deadline_ms(100, 20, tool_in_flight=True))
        with self.assertRaises(checks.ContractError):
            checks.self_check_deadline_ms(100, 20, tool_in_flight=True, first_safe_boundary_ms=99)

    def test_provider_only_call_defers_self_check_deadline(self):
        self.assertIsNone(checks.self_check_deadline_ms(100, 20, provider_in_flight=True))
        self.assertEqual(checks.self_check_deadline_ms(100, 20, provider_in_flight=True,
                                                     first_safe_boundary_ms=150), 170)
        self.assertEqual(checks.self_check_deadline_ms(100, 20, tool_in_flight=True,
                                                     provider_in_flight=True,
                                                     first_safe_boundary_ms=160), 180)
        with self.assertRaises(checks.ContractError):
            checks.self_check_deadline_ms(100, 20, provider_in_flight=None)

    def test_single_round_review_budget_and_resolved_policy(self):
        policy = read_example("review-policy")
        policy.update(objection_round_limit=1, execution_limit=8)
        validate("review-policy", policy)
        plan = read_example("review-plan")
        plan.update(execution_limit=8, reserved_answer_executions=0, reserved_final_executions=3)
        validate("review-plan", plan, review_policy=policy)
        policy["execution_limit"] = plan["execution_limit"] = 7
        with self.assertRaises(checks.ContractError):
            validate("review-policy", policy)
        with self.assertRaises(checks.ContractError):
            validate("review-plan", plan, review_policy=policy)
        policy.update(objection_round_limit=2, execution_limit=14)
        plan["execution_limit"] = 14
        with self.assertRaises(checks.ContractError):
            validate("review-plan", plan, review_policy=policy)
        plan.update(reserved_answer_executions=3, reserved_final_executions=6)
        validate("review-plan", plan, review_policy=policy)

    def test_review_budget_includes_finished_nested_supplements(self):
        activities = {
            "review": {"id": "review", "owner_ref": {"kind": "instance", "id": "instance"},
                       "execution_limit": 15, "assigned_execution_ids": ["p", "a", "b", "c"]},
            "supplement": {"id": "supplement", "owner_ref": {"kind": "activity", "id": "review"},
                           "state": "finished", "assigned_execution_ids": ["s", "build"]},
            "unrelated": {"id": "unrelated", "owner_ref": {"kind": "instance", "id": "instance"},
                          "assigned_execution_ids": ["other"]}}
        executions = {key: {"id": key, "owner_activity_id": "review", "actor_kind": "ai"}
                      for key in ("p", "a", "b", "c")}
        executions.update(s={"id": "s", "owner_activity_id": "supplement", "actor_kind": "ai"},
                          build={"id": "build", "owner_activity_id": "supplement", "actor_kind": "machine"},
                          other={"id": "other", "owner_activity_id": "unrelated", "actor_kind": "ai"})
        state = dict(executions_used=5, execution_limit=15, reserved_organize_executions=1,
                     reserved_answer_executions=3, reserved_final_executions=6)
        context = dict(activity_id="review", activities=activities, executions=executions)
        checks.validate_review_reserve(state, **context)
        state["executions_used"] = 4
        with self.assertRaises(checks.ContractError):
            checks.validate_review_reserve(state, **context)
        activities["nested"] = {"id": "nested", "owner_ref": {"kind": "activity", "id": "supplement"},
                                "assigned_execution_ids": ["retry"]}
        executions["retry"] = {"id": "retry", "owner_activity_id": "nested", "actor_kind": "ai"}
        state["executions_used"] = 6
        with self.assertRaises(checks.ContractError):
            checks.validate_review_reserve(state, **context)

    def test_review_execution_count_rejects_missing_links_and_cycles(self):
        activities = {"review": {"id": "review", "owner_ref": {"kind": "instance", "id": "i"},
                                 "execution_limit": 8, "assigned_execution_ids": ["p"]}}
        executions = {"p": {"id": "p", "owner_activity_id": "review", "actor_kind": "ai"}}
        state = dict(executions_used=1, execution_limit=8, reserved_organize_executions=1,
                     reserved_answer_executions=0, reserved_final_executions=3)
        context = dict(activity_id="review", activities=activities, executions=executions)
        checks.validate_review_reserve(state, **context)
        activities["review"]["assigned_execution_ids"] = []
        with self.assertRaises(checks.ContractError):
            checks.validate_review_reserve(state, **context)
        activities["review"]["assigned_execution_ids"] = ["p", "missing"]
        with self.assertRaises(checks.ContractError):
            checks.validate_review_reserve(state, **context)
        activities["review"]["assigned_execution_ids"] = ["p"]
        activities["review"]["owner_ref"] = {"kind": "activity", "id": "review"}
        with self.assertRaises(checks.ContractError):
            checks.validate_review_reserve(state, **context)

    def test_overflow_prioritizes_common_text_and_distinguishes_restoration(self):
        base = dict(reducible_by_window=False, tool_accumulation=True, activity_kind="identity_review",
                    restored_fits=False)
        self.assertEqual(checks.overflow_disposition(**base, proposal_overflow=True,
                                                    common_overflow=True), "escalate")
        self.assertEqual(checks.overflow_disposition(**base, proposal_overflow=True),
                         "close_unresolved_next_plan")
        self.assertEqual(checks.overflow_disposition(**base), "escalate")
        with self.assertRaises(checks.ContractError):
            checks.overflow_disposition(**base, common_overflow=None)

    def test_source_vectors_and_quality_bijection(self):
        mapping = checks.parse_json((ROOT / "source-vector-map.json").read_bytes())
        ids = [v["id"] for v in mapping["vectors"]]
        self.assertEqual(set(ids), {"V" + str(i).zfill(2) for i in range(1, 255)})
        self.assertEqual(len(ids), 254)
        retired = {v["id"] for v in mapping["vectors"] if v["expected"].startswith("번호 미재사용")}
        self.assertEqual(retired, {"V159", "V162", "V189"})
        rules = checks.parse_json((ROOT / "semantic-rules.json").read_bytes())["rules"]
        for rule in rules:
            self.assertFalse(retired & set(rule["source_vectors"]), rule["id"])
        for q in mapping["quality_contracts"]:
            self.assertFalse(retired & set(q["source_vectors"]), q["id"])
        self.assertEqual({q["id"] for q in mapping["quality_contracts"]}, {"Q" + str(i).zfill(2) for i in range(1, 26)})
        for q in mapping["quality_contracts"]:
            self.assertTrue(set(q["source_vectors"]) <= set(ids))
        self.assertTrue(all(v["execution_status"] == "not_run" for v in mapping["vectors"]))
        source = ROOT.parent / mapping["source"]
        self.assertEqual(mapping["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertTrue(source_map_matches(mapping))

    def test_regression_entire_request_idempotency(self):
        original = checks.parse_json((ROOT / "fixtures" / "commands" / "run.request.json").read_bytes())
        changed = copy.deepcopy(original)
        changed["command"] = "resume"
        validate("command-request", changed)
        self.assertEqual(checks.check_replay(original, original), "return_recorded_result")
        with self.assertRaises(checks.ContractError):
            checks.check_replay(original, changed)
        changed = copy.deepcopy(original)
        changed["caller"]["conversation_id"] = "CV-" + "0"*25 + "2"
        with self.assertRaises(checks.ContractError):
            checks.check_replay(original, changed)

    def test_regression_pause_entry_preserves_stage(self):
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        for facts in ({}, {"resume_lifecycle": "active"}):
            with self.assertRaises(checks.ContractError):
                checks.transition(machines, "lifecycle", "initializing", "paused", facts)
        self.assertEqual(checks.transition(machines, "lifecycle", "initializing", "paused",
                                         {"resume_lifecycle": "initializing"}), "paused")

    def test_regression_activation_and_waiting_guards(self):
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        for machine, before, after in [("lifecycle", "initializing", "active"), ("task", "waiting", "active"), ("activity", "waiting", "ready")]:
            with self.assertRaises(checks.ContractError):
                checks.transition(machines, machine, before, after, {})
        facts = dict.fromkeys(["references_valid", "governance_approved", "operations_capacity_valid",
                               "active_trust_valid", "recovery_valid"], True)
        self.assertEqual(checks.transition(machines, "lifecycle", "initializing", "active", facts), "active")
        self.assertEqual(checks.transition(machines, "activity", "waiting", "ready", {"waiting_condition_resolved": True}), "ready")

    def test_regression_settled_balance(self):
        value = read_example("resource-reservation")
        value.update(reserved=10, confirmed_consumed=3, returned=2, state="settled",
                     evidence_refs=value["authority_refs"])
        with self.assertRaises(checks.ContractError):
            validate("resource-reservation", value)
        value["returned"] = 7
        validate("resource-reservation", value)
        value.update(state="held", returned=2)
        validate("resource-reservation", value)

    def test_regression_satisfied_requires_complete_scope(self):
        for kind in ("goal", "academic", "task_completion", "project_audit"):
            value = read_example("assessment")
            value.update(kind=kind, value="satisfied", scope_complete=False)
            with self.assertRaises(checks.ContractError):
                validate("assessment", value)

    def test_regression_aggregation_needs_exact_slots_and_closed_issues(self):
        self.assertEqual(checks.aggregate_identity(rows(["match"]), [], True, False,
            expected_initial_slots=INITIAL_SLOTS), "unresolved")
        self.assertEqual(checks.aggregate_identity(rows(["mismatch"]*3), rows(["match"]*3, "judge"), True, True,
            expected_initial_slots=INITIAL_SLOTS, expected_judge_slots=JUDGE_SLOTS), "unresolved")
        self.assertEqual(checks.aggregate_identity(rows(["mismatch"]*3), rows(["match"]*3, "judge"), True, False,
            expected_initial_slots=INITIAL_SLOTS, expected_judge_slots=JUDGE_SLOTS), "match")

    def test_regression_duplicate_judge_cannot_be_three_votes(self):
        votes = [{"slot_id": "judge-1", "value": "approved"}]*3
        self.assertEqual(checks.aggregate_objection(votes, 1, 3, expected_slots=JUDGE_SLOTS), "execution_incomplete")
        value = read_example("issue-state")
        issue = sample(SCHEMAS["issue-state"]["properties"]["issues"]["items"])
        issue.update(state="approved", establishment_basis="unanimous_approval",
            judge_results=[{"slot_id": "judge-1", "value": "approved", "reason_ref": value["scope_manifest_ref"]}]*3)
        value["issues"] = [issue]
        with self.assertRaises(checks.ContractError):
            validate("issue-state", value)

    def test_regression_review_plan_allocations(self):
        value = read_example("review-plan")
        validate("review-plan", value)
        value["execution_limit"] = 1
        with self.assertRaises(checks.ContractError):
            validate("review-plan", value)
        value = read_example("review-plan")
        value["role_slots"][1]["id"] = value["role_slots"][0]["id"]
        with self.assertRaises(checks.ContractError):
            validate("review-plan", value)
        value = read_example("review-plan")
        value["role_slots"][2]["scope_item_ids"] = []
        with self.assertRaises(checks.ContractError):
            validate("review-plan", value)

    def test_regression_preparation_future_fallback(self):
        value = read_example("activity-result")
        value["payload"].pop("regenerate_after")
        with self.assertRaises(checks.ContractError):
            validate("activity-result", value)
        value["payload"]["regenerate_after"] = value["payload"]["observed_at"]
        with self.assertRaises(checks.ContractError):
            validate("activity-result", value)

    def test_regression_truncation_requires_recorded_permission(self):
        value = read_example("input-manifest")
        validate("input-manifest", value)
        value["planning_input"]["candidate_listing"].update(total_count=5, truncated=True)
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)
        value["planning_input"]["truncation_permission_ref"] = value["profile_ref"]
        validate("input-manifest", value)
        value["planning_input"]["canon_listing"].update(order="sealed_random", shuffle_seed="1" * 64, algorithm="hmac-sort-v1")
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)
        value["continuity_broken"] = True
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)

    def test_regression_task_terminal_fields_are_exclusive(self):
        value = read_example("task")
        basis = value["contract"]["execution_profile_refs"][0]
        value.update(state="completed", completion_ref=basis, closure_ref=basis, remaining_scope_ids=[])
        value["scope_dispositions"] = [{"scope_id": item["id"], "value": "fulfilled",
            "evidence_refs": [basis], "successor_task_ids": []} for item in value["contract"]["scope"]]
        with self.assertRaises(checks.ContractError):
            validate("task", value)
        value.pop("closure_ref")
        validate("task", value)

    def test_regression_foreign_ids_are_typed(self):
        value = checks.parse_json((ROOT / "fixtures" / "commands" / "init.response.json").read_bytes())
        value["result"]["instance_id"] = "F-" + "0"*25 + "1"
        with self.assertRaises(checks.ContractError):
            validate("command-response", value)
        value = read_example("execution")
        value["owner_activity_id"] = "T-" + "0"*25 + "1"
        with self.assertRaises(checks.ContractError):
            validate("execution", value)

    def test_regression_record_normalize_response_binding(self):
        request = checks.parse_json((ROOT / "fixtures" / "commands" / "record.request.json").read_bytes())
        response = checks.parse_json((ROOT / "fixtures" / "commands" / "record.response.json").read_bytes())
        checks.check_request_response(request, response)
        request["payload"].update(mode="normalize", input_ref=read_example("decision")["answer_ref"])
        validate("command-request", request)
        with self.assertRaises(checks.ContractError):
            checks.check_request_response(request, response)
        response["result"]["mode"] = "normalize"
        with self.assertRaises(checks.ContractError):
            validate("command-response", response)
        response["result"].update(candidate_ref=request["payload"]["input_ref"],
                                  check_ref=read_example("decision")["answer_ref"])
        validate("command-response", response)
        checks.check_request_response(request, response)

    def test_regression_source_map_content_tampering(self):
        mapping = checks.parse_json((ROOT / "source-vector-map.json").read_bytes())
        for collection, key in (("vectors", "expected"), ("quality_contracts", "guarantee"),
                                ("quality_contracts", "owner")):
            changed = copy.deepcopy(mapping)
            changed[collection][0][key] = "CORRUPTED"
            with self.assertRaises(checks.ContractError):
                source_map_matches(changed)

    def test_regression_unknown_kind_fields_and_missing_common_document(self):
        value = read_example("kind-definition")
        value["constraints"]["required_fields"] = ["invented_permission"]
        with self.assertRaises(checks.ContractError):
            validate("kind-definition", value)
        value = read_example("input-manifest")
        value["common_documents"][0]["path"] = "OTHER.md"
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)

    def test_regression_dispatch_requires_selected_disposition(self):
        value = read_example("plan")
        value["dispatch_order"] = ["T-" + "0"*25 + "1"]
        with self.assertRaises(checks.ContractError):
            validate("plan", value)

    def test_current_summary_issue_and_repeat_contracts(self):
        explanation = read_example("explanation")
        validate("explanation", explanation)
        explanation["summary_item_id"] = "F-" + "0" * 25 + "2"
        with self.assertRaises(checks.ContractError):
            validate("explanation", explanation)
        rule = {"id": "fixture", "op": "counter_gte", "required_evidence": [],
                "counter_id": "counter", "source_ref": read_example("task")["contract"]["basis_refs"][0],
                "baseline": 0, "threshold": 1, "repeat_interval": 2}
        validator(SCHEMAS["common"]["$defs"]["observation_rule"]).validate(rule)
        rule["op"] = "event_recorded"
        rule.pop("counter_id"); rule.pop("source_ref"); rule.pop("baseline"); rule.pop("threshold")
        rule["event_kind"] = "fixture"; rule["target_id"] = "F-" + "0" * 25 + "1"
        self.assertFalse(validator(SCHEMAS["common"]["$defs"]["observation_rule"]).is_valid(rule))
        issue_state = read_example("issue-state")
        issue_state["issues"] = [{"id": "IS-" + "0" * 25 + "2", "revision": 1,
            "lineage_id": "IS-" + "0" * 25 + "2", "round": 1, "author_slot_id": "judge-1",
            "answer_role_slot_id": "outside", "source_result_ref": read_example("task")["contract"]["basis_refs"][0],
            "claim_ref": read_example("explanation")["document_ref"], "coordinates": [], "evidence_refs": [],
            "parent_issue_ids": [], "answer_refs": [], "judge_results": [], "state": "open", "establishment_basis": "none"}]
        with self.assertRaises(checks.ContractError):
            checks.check_issue_answer_slots(issue_state, lambda _: {"phase": "initial", "role_slot_id": "judge-1",
                "objections": [{"claim_ref": issue_state["issues"][0]["claim_ref"]}]}, {"judge-1"})

    def test_profile_summary_judge_and_remainder_relations(self):
        task = read_example("task")
        profile_id = task["contract"]["execution_profile_refs"][0]["record_id"]
        manifest = {"planning_input": {"candidate_listing": {"items": [{
            "id": task["id"], "view": {"revision": 1, "profile_availability": [
                {"profile_id": profile_id, "currently_usable": True}]}}]}}}
        plan = {"candidate_dispositions": [{"task_id": task["id"], "revision": 1, "value": "selected"}],
                "execution_requests": [{"task_id": task["id"], "revision": 1,
                                        "execution_profile_id": profile_id}],
                "dispatch_order": [task["id"]]}
        contracts = {(task["id"], 1): task["contract"]}
        self.assertTrue(checks.check_profile_selection(contracts, plan, manifest, lambda ref: ref["record_id"]))
        artifact_contract = copy.deepcopy(task["contract"])
        artifact_contract["execution_profile_refs"] = [{"ref_kind": "artifact", "bundle_id": "AB-fixture",
            "path": "profile.json", "sha256": "1" * 64}]
        artifact_plan = copy.deepcopy(plan)
        artifact_plan["execution_requests"][0]["execution_profile_id"] = "EP-artifact"
        artifact_manifest = copy.deepcopy(manifest)
        artifact_manifest["planning_input"]["candidate_listing"]["items"][0]["view"]["profile_availability"] = [{"profile_id": "EP-artifact", "currently_usable": True}]
        self.assertTrue(checks.check_profile_selection({(task["id"], 1): artifact_contract}, artifact_plan,
            artifact_manifest, lambda ref: "EP-artifact" if ref["ref_kind"] == "artifact" else ref["record_id"]))
        duplicate = copy.deepcopy(task["contract"])
        duplicate["execution_profile_refs"].append(copy.deepcopy(duplicate["execution_profile_refs"][0]))
        with self.assertRaises(checks.ContractError):
            checks.check_profile_selection({(task["id"], 1): duplicate}, plan, manifest, lambda ref: ref["record_id"])
        bad_plan = copy.deepcopy(plan)
        bad_plan["execution_requests"][0]["execution_profile_id"] = "EP-not-allowed"
        with self.assertRaises(checks.ContractError):
            checks.check_profile_selection(contracts, bad_plan, manifest, lambda ref: ref["record_id"])
        expanded = checks.expand_remainder_dispositions([(task["id"], 1), ("T-" + "0" * 25 + "2", 2)],
            [{"task_id": task["id"], "revision": 1, "value": "selected", "reason": "fixture"}],
            {"value": "not_selected", "reason": "fixture"})
        self.assertEqual(expanded[1]["task_id"], "T-" + "0" * 25 + "2")
        self.assertEqual(expanded[1]["revision"], 2)
        with self.assertRaises(checks.ContractError):
            checks.expand_remainder_dispositions([(task["id"], 1), (task["id"], 1)], [], None)
        explanation = read_example("explanation")
        explanation["math_items"][0]["kind"] = "summary"
        canon = {"view": {"valid_explanation_available": True, "summary": "fixture"},
                 "refs": {"explanation_links": [{"explanation_ref": {}, "summary_item_id": explanation["summary_item_id"],
                    "assessment_value": "match", "use_state": "active"}]}}
        self.assertTrue(checks.check_canon_summary(canon, lambda _: explanation, lambda _document, _anchor: "fixture"))
        canon["refs"]["explanation_links"][0]["use_state"] = "suspended"
        with self.assertRaises(checks.ContractError):
            checks.check_canon_summary(canon, lambda _: explanation, lambda _document, _anchor: "fixture")
        canon["refs"]["explanation_links"][0]["use_state"] = "active"
        canon["view"]["valid_explanation_available"] = False
        canon["view"]["summary"] = "wrong"
        with self.assertRaises(checks.ContractError):
            checks.check_canon_summary(canon, lambda _: explanation, lambda _document, _anchor: "fixture")
        claim = {"ref_kind": "artifact", "bundle_id": "AB-00000000000000000000000001", "path": "claim.json", "sha256": "1" * 64}
        source_ref = {"ref_kind": "artifact", "bundle_id": "AB-00000000000000000000000001", "path": "source.json", "sha256": "1" * 64}
        issue = {"author_slot_id": "judge", "answer_role_slot_id": "initial", "source_result_ref": source_ref, "claim_ref": claim}
        source = {"phase": "judge", "role_slot_id": "judge", "new_findings": [{"claim_ref": copy.deepcopy(claim)}]}
        self.assertTrue(checks.check_issue_answer_slots({"issues": [issue]}, lambda _: source, {"initial"}))
        with self.assertRaises(checks.ContractError):
            checks.check_issue_answer_slots({"issues": [issue]}, lambda _: source, {"other"})
        initial = {"phase": "initial", "role_slot_id": "initial", "objections": [{"claim_ref": copy.deepcopy(claim)}]}
        initial_issue = {"author_slot_id": "initial", "answer_role_slot_id": "initial", "source_result_ref": source_ref, "claim_ref": claim}
        self.assertTrue(checks.check_issue_answer_slots({"issues": [initial_issue]}, lambda _: initial, {"other"}))

    def test_paused_maintenance_and_recovery_paths(self):
        ref = read_example("task")["contract"]["basis_refs"][0]
        runtime = {"lifecycle": "paused"}
        execution = {"id": "E-check", "activity_kind": "maintenance",
            "paused_maintenance_authorization": {"procedure_ref": ref, "approval_ref": ref,
                "target_refs": [ref], "scope": [], "authority_refs": [ref]}}
        deterministic = {"execution_id": "E-diagnosing", "stage": "diagnosing", "disposition": "resume_checkpoint",
            "recovery": {"path": "deterministic", "prior_execution_ref": ref, "input_manifest_ref": ref,
                "profile_ref": ref, "authority_refs": [ref], "external_action_refs": [], "scope": [],
                "diagnosing_execution_id": "E-diagnosing"}}
        facts = {key: True for key in ("barrier_confirmed", "inputs_unchanged", "profile_current", "authority_current",
            "external_actions_replay_safe", "basis_current", "procedure_current", "target_in_scope", "start_checks_valid")}
        self.assertTrue(checks.check_paused_recovery(runtime, deterministic, execution, facts))
        broken = copy.deepcopy(deterministic); broken["stage"] = "checking_recovery"
        with self.assertRaises(checks.ContractError):
            checks.check_paused_recovery(runtime, broken, execution, facts)
        meaning = copy.deepcopy(deterministic); meaning["execution_id"] = "E-checking"; meaning["stage"] = "checking_recovery"; meaning["recovery"]["path"] = "meaning_review"
        self.assertTrue(checks.check_paused_recovery(runtime, meaning, execution, facts))
        for key in ("barrier_confirmed", "inputs_unchanged", "profile_current", "authority_current",
                    "external_actions_replay_safe", "basis_current"):
            with self.subTest(missing_recovery_fact=key), self.assertRaises(checks.ContractError):
                checks.check_paused_recovery(runtime, meaning, execution, dict(facts, **{key: False}))
        stopped = dict(facts, new_stop=True, future_assignments_blocked=True, authority_revoked=True,
                       common_stop_started=True, resume_lifecycle_preserved=True, no_automatic_resume=True)
        self.assertTrue(checks.check_paused_maintenance_stop(stopped))
        with self.assertRaisesRegex(checks.ContractError, "closes recovery admission"):
            checks.check_paused_recovery(runtime, deterministic, execution, stopped)
        stopped.pop("no_automatic_resume")
        with self.assertRaises(checks.ContractError):
            checks.check_paused_maintenance_stop(stopped)

    def test_regression_candidate_and_canon_listing_contracts(self):
        props = SCHEMAS["input-manifest"]["properties"]["planning_input"]["properties"]
        candidate_shape = props["candidate_listing"]["properties"]["items"]["items"]
        item = sample(candidate_shape)
        self.assertNotIn("description", item["view"])
        validator(candidate_shape).validate(item)
        for key in ("revision", "question", "scope", "expected_research_change", "work_class", "basis_ids", "review_status"):
            changed = copy.deepcopy(item)
            changed["view"].pop(key)
            self.assertFalse(validator(candidate_shape).is_valid(changed), key)
        for key in ("record_ref", "basis_refs", "author_execution_ids"):
            changed = copy.deepcopy(item)
            changed["refs"].pop(key)
            self.assertFalse(validator(candidate_shape).is_valid(changed), key)
        canon_shape = props["canon_listing"]["properties"]["items"]["items"]
        item = sample(canon_shape)
        for key in ("declaration_kind", "declaration_names", "explanation_states", "valid_explanation_available", "recently_changed"):
            changed = copy.deepcopy(item)
            changed["view"].pop(key)
            self.assertFalse(validator(canon_shape).is_valid(changed), key)
        for key in ("record_ref", "explanation_links", "change_refs"):
            changed = copy.deepcopy(item)
            changed["refs"].pop(key)
            self.assertFalse(validator(canon_shape).is_valid(changed), key)

    def test_transition_references_are_closed(self):
        rules = checks.parse_json((ROOT / "semantic-rules.json").read_bytes())
        rule_ids = {r["id"] for r in rules["rules"]}
        machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
        for machine in machines.values():
            for a, b, rid in machine["edges"]:
                self.assertIn(rid, rule_ids)
                self.assertNotIn(a, machine["terminal"])


def validation_basis():
    paths = [build_spec.DOC, ROOT.parent.parent / "형식과-절차.md"]
    paths.extend(ROOT / name for name in ("build_spec.py", "spec_checks.py", "verify_spec.py",
        "schema-registry.json", "command-contracts.json", "role-contracts.json",
        "semantic-rules.json", "transitions.json", "source-vector-map.json",
        "relation-templates.json", "toolchain-lock.json"))
    paths.extend(sorted((ROOT / "schemas").glob("*.json")))
    paths.extend(sorted((ROOT / "fixtures").rglob("*.json")))
    return [{"path": str(path.relative_to(ROOT.parent.parent)).replace("\\", "/"),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-examples", action="store_true")
    args = parser.parse_args()
    if args.refresh_examples:
        make_examples()
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SpecificationTests)
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    transcript = output.getvalue()
    print(transcript)
    report = {"scope": "offline_specification_checks_only", "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "passed": result.wasSuccessful(), "schema_families": len(SCHEMAS),
        "record_examples": len(list((ROOT / "fixtures" / "records").glob("*.json"))),
        "command_examples": len(list((ROOT / "fixtures" / "commands").glob("*.json"))),
        "source_vectors": {"total": len(checks.parse_json((ROOT / "source-vector-map.json").read_bytes())["vectors"]),
                           "retired": ["V159", "V162", "V189"], "runtime_execution": "not_run"},
        "input_basis": validation_basis(),
        "not_verified": ["actual_adapter", "adapter_compaction_control", "OS_isolation", "remote_termination", "provider_limits",
                         "all_runtime_domain_gates", "Lean_execution", "research_efficacy",
                         "external_definition_synchronization"],
        "python_dependencies": {name: importlib.metadata.version(name) for name in ("jsonschema", "referencing", "PyYAML")},
        "failed_cases": [{"test": str(test), "detail": detail} for test, detail in result.failures + result.errors]}
    (ROOT / "validation-report.json").write_bytes(checks.canonical_json(report))
    (ROOT / "validation-output.txt").write_text(transcript, encoding="utf-8", newline="\n")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
