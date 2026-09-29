"""The local control protocol's vocabulary (layer 1): tool and request names, the
binding fields and the self-check answer that workers send and the engine checks.

Workers load this module without the package inside their Windows Job, so it
imports only the standard library and ``jsonschema``.
"""
from typing import Any

# Control vocabulary shared by the workers, the MCP server and the observers.
CONTROL_SERVER = "execution_control"
SUBMIT_TOOL, RECEIPT_TOOL, SELF_CHECK_TOOL = "control_submit", "control_receipt", "control_self_check"
SAFETY_BOUNDARY, SUBMIT_INTENT = "safety_boundary", "submit_intent"
SELF_CHECK_RESPONSE, SUBMISSION_PREVIEW = "self_check_response", "submission_preview"
REQUEST_KINDS = frozenset({SAFETY_BOUNDARY, SUBMIT_INTENT, SELF_CHECK_RESPONSE, SUBMISSION_PREVIEW})
SUBMISSION_KINDS = frozenset({SUBMIT_INTENT, SUBMISSION_PREVIEW})
# A binding names one execution's endpoint and capability; ``workspace`` is optional, and
# ``self_check`` (true) marks an execution that answers self checks and so gets that tool.
BINDING_FIELDS = ("endpoint", "transport_id", "capability", "execution_id", "grant_id")

_TEXT = {"type": "string", "minLength": 1}
_REFS = {"type": "array", "items": _TEXT, "uniqueItems": True}
# The worker checks its answer before sending it; the engine checks it again on receipt.
SELF_CHECK_RESPONSE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["obligation_id", "execution_id", "rule_revision", "rule_results", "progress", "attempts", "next_method"],
    "properties": {
        "obligation_id": _TEXT, "execution_id": _TEXT,
        "rule_revision": {"type": "integer", "minimum": 0},
        "progress": {"enum": ["progress", "no_progress", "contract_mismatch"]},
        "attempts": {"type": "array", "items": _TEXT, "minItems": 1}, "next_method": _TEXT,
        "rule_results": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["rule_id", "status", "evidence_refs", "missing_evidence_refs", "reason"],
            "properties": {"rule_id": _TEXT, "status": {"enum": ["normal", "defect", "indeterminate"]},
                "evidence_refs": _REFS, "missing_evidence_refs": _REFS, "reason": _TEXT}}},
        "rule_proposal": {},
    },
}


def self_check_request_id(self_check_id: str) -> str:
    """The control request ID under which a self-check answer is submitted."""
    return "self-check-" + self_check_id


def self_check_response_errors(response: Any) -> list[str]:
    from jsonschema import Draft202012Validator
    return [error.message for error in Draft202012Validator(SELF_CHECK_RESPONSE_SCHEMA).iter_errors(response)]
