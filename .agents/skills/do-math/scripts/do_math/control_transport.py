"""File-delivered local control messages for one execution.

Transport files are delivery material, not research state.  The engine is the
sole authority: it validates a request and publishes the authoritative record
before this module emits ``accepted``.  A local capability binds a cooperating
worker to an execution; it is not strong same-user authentication.
"""
from __future__ import annotations

from copy import deepcopy
import argparse
import hashlib
import json
import os
from pathlib import Path
from secrets import token_urlsafe
import sys
import tempfile
import time
from typing import Any, Callable
if __package__:
    from .file_io import (compact_json_bytes, read_bytes_shared, file_fingerprint, fingerprint_settled,
                          json_digest, require_text, write_bytes_atomic)
else:
    from file_io import (compact_json_bytes, read_bytes_shared, file_fingerprint, fingerprint_settled,
                         json_digest, require_text, write_bytes_atomic)


# Control vocabulary shared by the workers, the MCP server and the observers.
CONTROL_SERVER = "execution_control"
SUBMIT_TOOL, RECEIPT_TOOL, SELF_CHECK_TOOL = "control_submit", "control_receipt", "control_self_check"
SAFETY_BOUNDARY, SUBMIT_INTENT = "safety_boundary", "submit_intent"
SELF_CHECK_RESPONSE, SUBMISSION_PREVIEW = "self_check_response", "submission_preview"
REQUEST_KINDS = frozenset({SAFETY_BOUNDARY, SUBMIT_INTENT, SELF_CHECK_RESPONSE, SUBMISSION_PREVIEW})
SUBMISSION_KINDS = frozenset({SUBMIT_INTENT, SUBMISSION_PREVIEW})
# A binding names one execution's endpoint and capability; ``workspace`` is optional.
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


_FINAL_RECEIPTS = frozenset({"accepted", "rejected", "withdrawn", "closed", "previewed"})
_WINDOWS_DEVICE_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{number}" for number in range(1, 10)}
    | {f"LPT{number}" for number in range(1, 10)}
)


def _require_text(value: Any, name: str) -> str:
    """Nonempty text (``file_io.require_text``) that a transport file or path can also carry: no NUL."""
    if "\0" in require_text(value, name):
        raise ValueError(f"{name} must be NUL-free")
    return value


def _require_file_name(value: Any, name: str) -> str:
    value = _require_text(value, name)
    invalid = '<>:"/\\|?*[]'
    device = value.split(".", 1)[0].upper()
    if (value in {".", ".."} or value[-1] in {" ", "."}
            or any(character in invalid or ord(character) < 32 for character in value)
            or device in _WINDOWS_DEVICE_NAMES):
        raise ValueError(f"{name} must be a safe file name component")
    return value


def _atomic_json(path: Path, value: Any) -> None:
    write_bytes_atomic(path, compact_json_bytes(value))


def _create_json_once(path: Path, value: Any) -> bool:
    """Publish complete JSON only when the final name is still unclaimed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp") as handle:
            handle.write(compact_json_bytes(value))
            temporary = Path(handle.name)
        try:
            os.link(temporary, path)
        except FileExistsError:
            return False
        return True
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _json(path: Path) -> dict | None:
    try:
        raw = read_bytes_shared(path)
    except FileNotFoundError:
        return None
    return _decode_json(path, raw)


def _is_open(endpoint: Path) -> bool:
    try:
        state = _json(endpoint / "state.json")
    except ValueError:
        return True  # An unreadable state is read, and rejected, by the next receipt.
    return state is None or state.get("state") == "open"


def _decode_json(path: Path, raw: bytes) -> dict:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"transport file {path} is not valid UTF-8 JSON: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"transport file {path} is not an object")
    return value


class ControlTransport:
    """A pumpable local transport; it neither starts a daemon nor owns state."""

    def __init__(self, root: Path | str | None = None,
                 publish: Callable[[dict], dict] | None = None):
        self.root = None if root is None else Path(root).resolve()
        self._publish = publish
        self._capabilities: dict[str, dict] = {}
        self._receipts: dict[tuple[str | None, str], dict] = {}  # (transport_id, request_id) -> receipt
        self._pump_cache: dict[Path, tuple[tuple, dict]] = {}
        # Only open transports can receive new deliveries; a pump reads their inboxes alone.
        # The set is read from disk at the first pump: commands that never pump read no transport.
        self._open: set[str] | None = None

    def issue(self, execution_id: str, grant_id: str, *, workspace: Path | str | None = None) -> dict:
        _require_text(execution_id, "execution_id")
        _require_text(grant_id, "grant_id")
        transport_id, capability = token_urlsafe(18), token_urlsafe(32)
        binding = {"transport_id": transport_id, "capability": capability,
                   "execution_id": execution_id, "grant_id": grant_id}
        if workspace is not None:
            binding["workspace"] = str(Path(workspace).resolve())
        if self.root is not None:
            endpoint = self.root / transport_id
            binding["endpoint"] = str(endpoint)
            for name in ("inbox", "outbox", "worker-inbox", "worker-outbox"):
                (endpoint / name).mkdir(parents=True, exist_ok=True)
            _atomic_json(endpoint / "binding.json", binding)
            _atomic_json(endpoint / "state.json", {"state": "open"})
            if self._open is not None:
                self._open.add(transport_id)
        self._capabilities[transport_id] = deepcopy(binding)
        return deepcopy(binding)

    @staticmethod
    def validate_binding(binding: Any, *, execution_id: str, cwd: str | None = None) -> None:
        """A worker's binding names this execution, an absolute endpoint and, when given, its cwd."""
        if (not isinstance(binding, dict) or set(BINDING_FIELDS) - set(binding)
                or set(binding) - set(BINDING_FIELDS) - {"workspace"}
                or any(not isinstance(binding[key], str) or not binding[key].strip() or "\0" in binding[key]
                       for key in BINDING_FIELDS)
                or binding["execution_id"] != execution_id
                or not Path(binding["endpoint"]).is_absolute()):
            raise ValueError("control binding must identify this execution and an absolute local endpoint")
        if "workspace" in binding:
            workspace = binding["workspace"]
            if (not isinstance(workspace, str) or not workspace.strip() or "\0" in workspace
                    or not Path(workspace).is_absolute()):
                raise ValueError("control binding workspace must be an absolute local path")
            if cwd is not None and (not isinstance(cwd, str) or not cwd.strip() or "\0" in cwd
                    or not Path(cwd).is_absolute() or Path(workspace).resolve() != Path(cwd).resolve()):
                raise ValueError("control binding workspace differs from execution cwd")

    @staticmethod
    def mcp_server_config(binding: dict) -> dict:
        if any(key not in binding for key in BINDING_FIELDS):
            raise ValueError("file transport binding lacks an MCP endpoint")
        arguments = [str(Path(__file__).resolve()), "mcp",
                     *("--" + key.replace("_", "-") + "=" + binding[key] for key in BINDING_FIELDS)]
        if binding.get("workspace"):
            arguments.append("--workspace=" + binding["workspace"])
        return {"command": sys.executable, "args": arguments}

    def receive(self, request: dict, *, publish: Callable[[dict], dict] | None = None) -> dict:
        """Validate and publish a request, or record its non-final receipt.

        A publisher may return ``accepted`` only with ``published: true`` and a
        nonempty authoritative snapshot.  The engine's callback must have made
        that CAS publication before returning.
        """
        if not isinstance(request, dict):
            raise ValueError("control request must be an object")
        request_id = _require_file_name(request.get("request_id"), "request_id")
        request_sha256 = json_digest(request)
        try:
            sender = _require_file_name(request.get("transport_id"), "transport_id")
        except ValueError:
            sender = None
        previous = self._receipt(request_id, sender)
        if previous is not None:
            if previous.get("request_sha256") != request_sha256:
                raise ValueError("request_id was reused with different content")
            if previous.get("state") in _FINAL_RECEIPTS:
                return previous
        try:
            request = self._validate_request(request)
        except ValueError as error:
            return self._reject_unvalidated(request, str(error))
        state = self._state(request)
        if state["state"] != "open":
            return self._store(request, {"state": "withdrawn" if state["state"] == "withdrawn" else "closed",
                                         "reason": state.get("reason", "transport is not open")})
        publisher = publish or self._publish
        if publisher is None:
            return self._store(request, {"state": "received"})
        decision = publisher(deepcopy(request))
        if request["kind"] == SUBMISSION_PREVIEW:
            if (not isinstance(decision, dict) or decision.get("state") not in {"previewed", "rejected"}
                    or decision.get("published") is True):
                raise ValueError("preview must return a check result without publication")
            if decision["state"] == "previewed" and not isinstance(decision.get("result"), dict):
                raise ValueError("previewed receipt requires a structured check result")
            return self._store(request, decision)
        if not isinstance(decision, dict) or decision.get("state") not in {"accepted", "rejected"}:
            raise ValueError("transport publisher must return accepted or rejected")
        if decision["state"] == "accepted":
            if decision.get("published") is not True or not isinstance(decision.get("snapshot"), str) or not decision["snapshot"]:
                raise ValueError("accepted receipt requires a published authoritative snapshot")
        return self._store(request, decision)

    def pump(self, publish: Callable[[dict], dict] | None = None, *, limit: int | None = None) -> list[dict]:
        """Read delivery files and call the engine's validation-and-CAS hook."""
        if self.root is None:
            raise ValueError("a memory-only transport has no inbox to pump")
        if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 1):
            raise ValueError("limit must be a positive integer or null")
        if self._open is None:
            # issue and close keep state.json current, so this scan sees every earlier issue and close.
            self._open = ({path.parent.name for path in self.root.glob("*/binding.json") if _is_open(path.parent)}
                          if self.root.is_dir() else set())
        paths = [path for transport_id in sorted(self._open)
                 for path in sorted((self.root / transport_id / "inbox").glob("*.json"))]
        return self._pump_paths(paths[:limit], publish)

    def _pump_paths(self, paths: list[Path], publish: Callable[[dict], dict] | None) -> list[dict]:
        results = []
        for path in paths:
            try:
                mark = file_fingerprint(path)
            except FileNotFoundError:
                continue
            # A delivery with a final receipt is not read again while its settled
            # fingerprint is unchanged; a rewritten delivery is read and received.
            cached = self._pump_cache.get(path)
            if cached is not None and cached[0] == mark:
                results.append(deepcopy(cached[1]))
                continue
            self._pump_cache.pop(path, None)
            try:
                try:
                    raw = path.read_bytes()
                except FileNotFoundError:
                    continue
                receipt = self.receive(_decode_json(path, raw), publish=publish)
            except ValueError as error:
                receipt = self._reject_delivery_file(path, error)
            results.append(receipt)
            if (receipt.get('state') in _FINAL_RECEIPTS and fingerprint_settled(mark)
                    and file_fingerprint(path) == mark):
                self._pump_cache[path] = (mark, deepcopy(receipt))
        return results

    def close(self, binding: dict, *, reason: str, withdrawn: bool = False) -> dict:
        endpoint = self._endpoint(binding)
        _require_text(reason, "reason")
        state = {"state": "withdrawn" if withdrawn else "closed", "reason": reason}
        _atomic_json(endpoint / "state.json", state)
        # A delivery that raced the close gets its closed receipt now; later pumps skip this transport.
        inbox = sorted((endpoint / "inbox").glob("*.json"))
        unsettled = []
        for path in inbox:
            try:
                self._pump_paths([path], None)
            except ValueError as error:
                # A changed redelivery keeps the receipt it already has; the closed state records why.
                unsettled.append({"source": "inbox/" + path.name, "reason": str(error)})
        if unsettled:
            state["unsettled_deliveries"] = unsettled
            _atomic_json(endpoint / "state.json", state)
        if self._open is not None:
            self._open.discard(endpoint.name)
        for path in inbox:
            self._pump_cache.pop(path, None)
        return state

    def request_self_check(self, binding: dict, *, request: dict) -> dict:
        """Deliver the issued request object; the tracker hashes this same object."""
        if (not isinstance(request, dict) or set(request) != {"self_check_id", "execution_id", "payload"}
                or request["execution_id"] != binding.get("execution_id")
                or not isinstance(request["payload"], dict)):
            raise ValueError("self-check request must be this execution's exact issued request")
        self_check_id = _require_file_name(request["self_check_id"], "self_check_id")
        _require_file_name(binding.get("transport_id"), "transport_id")
        endpoint = self._endpoint(binding)
        state = _json(endpoint / "state.json") or {}
        if state.get("state") != "open":
            raise ValueError("a closed or withdrawn transport cannot request a self-check")
        request = deepcopy(request)
        path = endpoint / "worker-inbox" / (self_check_id + ".json")
        existing = _json(path)
        if existing is None and _create_json_once(path, request):
            existing = request
        else:
            existing = _json(path)
        if existing != request:
            raise ValueError("self_check_id was reused with different content")
        if binding.get('workspace'):
            from .context_store import safe_path
            surface = safe_path(Path(binding['workspace']), '.control/self-checks/' + self_check_id + '.json')
            if not _create_json_once(surface, request) and _json(surface) != request:
                raise ValueError('workspace self-check notice differs from its issued request')
        return request

    @staticmethod
    def worker_submit(binding: dict, *, request_id: str, kind: str, payload: dict | None = None) -> dict:
        _require_file_name(request_id, "request_id")
        if kind not in REQUEST_KINDS:
            raise ValueError("unsupported control kind")
        if payload is not None and not isinstance(payload, dict):
            raise ValueError("control payload must be an object")
        if kind == SELF_CHECK_RESPONSE:
            errors = self_check_response_errors((payload or {}).get("response"))
            if errors:
                raise ValueError("self-check response does not match its schema: " + errors[0])
        endpoint = ControlTransport._endpoint(binding)
        _require_file_name(binding.get("transport_id"), "transport_id")
        state = _json(endpoint / "state.json") or {}
        if state.get("state") != "open":
            return {"request_id": request_id, "state": "withdrawn" if state.get("state") == "withdrawn" else "closed",
                    "reason": state.get("reason", "transport is not open")}
        request = {key: binding[key] for key in BINDING_FIELDS if key != "endpoint"}
        request.update(request_id=request_id, kind=kind, payload=deepcopy(payload or {}))
        path = endpoint / "inbox" / (request_id + ".json")
        receipt = _json(endpoint / "outbox" / (request_id + ".json"))
        if receipt is not None:
            if receipt.get("request_sha256") != json_digest(request):
                raise ValueError("request_id was already received with different content")
            return {"request_id": request_id, "state": "already_received"}
        existing = _json(path)
        if existing is None and _create_json_once(path, request):
            return {"request_id": request_id, "state": "submitted"}
        existing = _json(path)
        if existing != request:
            raise ValueError("request_id was already submitted with different content")
        return {"request_id": request_id, "state": "submitted"}

    @staticmethod
    def worker_receipt(binding: dict, request_id: str) -> dict | None:
        _require_file_name(request_id, "request_id")
        _require_file_name(binding.get("transport_id"), "transport_id")
        return _json(ControlTransport._endpoint(binding) / "outbox" / (request_id + ".json"))

    @staticmethod
    def wait_receipt(binding: dict, request_id: str, timeout_seconds: float | None) -> dict | None:
        if timeout_seconds is not None and (isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or timeout_seconds < 0):
            raise ValueError("timeout_seconds must be nonnegative or null")
        until = None if timeout_seconds is None else time.monotonic() + timeout_seconds
        while True:
            receipt = ControlTransport.worker_receipt(binding, request_id)
            if receipt is not None and receipt.get("state") in _FINAL_RECEIPTS:
                return receipt
            if until is not None and time.monotonic() >= until:
                return receipt
            time.sleep(0.05)

    @staticmethod
    def worker_self_check(binding: dict, *, self_check_id: str, response: dict | None = None) -> dict | None:
        _require_file_name(self_check_id, "self_check_id")
        _require_file_name(binding.get("transport_id"), "transport_id")
        endpoint = ControlTransport._endpoint(binding)
        if response is None:
            return _json(endpoint / "worker-inbox" / (self_check_id + ".json"))
        if _json(endpoint / "worker-inbox" / (self_check_id + ".json")) is None:
            raise ValueError("unknown self-check request")
        return ControlTransport.worker_submit(binding, request_id=self_check_request_id(self_check_id),
                                               kind=SELF_CHECK_RESPONSE,
                                               payload={"self_check_id": self_check_id, "response": response})

    def _validate_request(self, request: dict) -> dict:
        if not isinstance(request, dict):
            raise ValueError("control request must be an object")
        result = deepcopy(request)
        for key in ("request_id", "transport_id"):
            _require_file_name(result.get(key), key)
        for key in ("capability", "execution_id", "grant_id"):
            _require_text(result.get(key), key)
        if (not isinstance(result.get("kind"), str) or result["kind"] not in REQUEST_KINDS
                or not isinstance(result.get("payload"), dict)):
            raise ValueError("unsupported control kind or payload")
        binding = self._binding(result)
        if any(result[key] != binding[key] for key in ("execution_id", "grant_id", "capability")):
            raise ValueError("execution, grant, or capability differs from transport binding")
        if result["kind"] == SAFETY_BOUNDARY and result["payload"].get("inflight_calls") is not False:
            raise ValueError("boundary report has an in-flight call")
        if result["kind"] == SELF_CHECK_RESPONSE:
            sid = result["payload"].get("self_check_id")
            _require_file_name(sid, "self_check_id")
            if _json(self._endpoint(binding) / "worker-inbox" / (sid + ".json")) is None:
                raise ValueError("self-check response has no issued request")
        return result

    def _store(self, request: dict, decision: dict) -> dict:
        receipt = {"request_id": request["request_id"], "request_sha256": json_digest(request), "kind": request["kind"],
                   "execution_id": request["execution_id"], "state": decision["state"]}
        fields = (("reason", "result") if request["kind"] == SUBMISSION_PREVIEW else
                  ("reason", "result", "snapshot", "publication_id"))
        for key in fields:
            if key in decision:
                receipt[key] = deepcopy(decision[key])
        self._receipts[(request["transport_id"], request["request_id"])] = deepcopy(receipt)
        binding = self._binding(request)
        if binding.get("endpoint"):
            _atomic_json(self._endpoint(binding) / "outbox" / (request["request_id"] + ".json"), receipt)
        return receipt

    def _reject_unvalidated(self, request: dict, reason: str) -> dict:
        """Return a queryable rejection when the transport endpoint is known."""
        receipt = {"request_id": request["request_id"], "request_sha256": json_digest(request),
                   "kind": request.get("kind"), "execution_id": request.get("execution_id"),
                   "state": "rejected", "reason": reason}
        transport_id = request.get("transport_id")
        try:
            safe_transport_id = _require_file_name(transport_id, "transport_id")
        except ValueError:
            safe_transport_id = None
        self._receipts[(safe_transport_id, request["request_id"])] = deepcopy(receipt)
        binding = self._capabilities.get(safe_transport_id) if safe_transport_id is not None else None
        if binding is None and self.root is not None and safe_transport_id is not None:
            binding = _json(self.root / safe_transport_id / "binding.json")
        if binding is not None and binding.get("endpoint"):
            _atomic_json(self._endpoint(binding) / "outbox" / (request["request_id"] + ".json"), receipt)
        return receipt

    def _reject_delivery_file(self, path: Path, error: ValueError) -> dict:
        request_id = _require_file_name(path.stem, "request_id")
        raw = path.read_bytes()
        receipt = {"request_id": request_id, "state": "rejected", "stage": "delivery_validation",
                   "reason": str(error), "source": "inbox/" + path.name,
                   "source_sha256": hashlib.sha256(raw).hexdigest(), "source_bytes": len(raw)}
        receipt_path = path.parent.parent / "outbox" / (request_id + ".json")
        if _create_json_once(receipt_path, receipt):
            return receipt
        existing = _json(receipt_path)
        if existing is None:
            raise RuntimeError("delivery rejection disappeared after publication")
        if (existing.get("state") == "rejected" and existing.get("stage") == "delivery_validation"
                and existing.get("source_sha256") == receipt["source_sha256"]):
            return existing
        raise ValueError("request_id was already received with different content")

    def _receipt(self, request_id: str, transport_id: str | None = None) -> dict | None:
        """The receipt of ``request_id``: the sender's own first, then any transport's.

        Request IDs are unique across the instance's transports, so another
        transport's receipt for the ID rejects a reuse. The sender's own receipt
        is read first: a rejection another transport earned for reusing this ID
        must not stand in for the sender's receipt when the sender redelivers.
        """
        _require_file_name(request_id, "request_id")
        name = request_id + ".json"
        if transport_id is not None:
            entry = self._receipts.get((transport_id, request_id))
            if entry is not None:
                return deepcopy(entry)
            if self.root is not None and os.path.exists(self.root / transport_id / "outbox" / name):
                return _json(self.root / transport_id / "outbox" / name)
        for (_, known_id), entry in self._receipts.items():
            if known_id == request_id:
                return deepcopy(entry)
        if self.root is None or not self.root.is_dir():
            return None
        # A new ID is checked against every outbox by one existence test per transport.
        for entry in os.scandir(self.root):
            path = Path(entry.path) / "outbox" / name
            if os.path.exists(path):
                return _json(path)
        return None

    def _binding(self, request: dict) -> dict:
        transport_id = _require_file_name(request["transport_id"], "transport_id")
        binding = self._capabilities.get(transport_id)
        if binding is not None:
            return binding
        if self.root is None:
            raise ValueError("unknown transport capability")
        binding = _json(self.root / transport_id / "binding.json")
        if binding is None:
            raise ValueError("unknown transport capability")
        self._capabilities[transport_id] = binding
        return binding

    def _state(self, request: dict) -> dict:
        binding = self._binding(request)
        if not binding.get("endpoint"):
            return {"state": "open"}
        endpoint = self._endpoint(binding)
        return _json(endpoint / "state.json") or {"state": "open"}

    @staticmethod
    def _endpoint(binding: dict) -> Path:
        endpoint = binding.get("endpoint")
        if not isinstance(endpoint, str) or not endpoint:
            raise ValueError("transport binding has no file endpoint")
        return Path(endpoint).resolve()


def _mcp_result(value: Any) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, sort_keys=True)}]}


def _mcp_server(binding: dict) -> int:
    # Tool input schemas keep the node shapes preserved provider runs accepted; the
    # exact answer shape is described in text and checked by self_check_response_errors.
    tools = [
        {"name": "submit_draft", "description": "Validate and submit one workspace-relative draft; internal checks and hashes are derived automatically.",
         "inputSchema": {"type": "object", "properties": {"draft_path": {"type": "string"}, "preview": {"type": "boolean"}, "wait_seconds": {"type": "number", "minimum": 0}}, "required": ["draft_path"]}},
        {"name": SUBMIT_TOOL, "description": "Submit a boundary, manifest or self-check answer to the central execution pump.",
         "inputSchema": {"type": "object", "properties": {"request_id": {"type": "string"}, "kind": {"enum": sorted(REQUEST_KINDS)}, "payload": {"type": "object"}, "wait_seconds": {"type": "number", "minimum": 0}}, "required": ["request_id", "kind", "payload"]}},
        {"name": RECEIPT_TOOL, "description": "Read or wait for the central receipt using a caller-provided duration.",
         "inputSchema": {"type": "object", "properties": {"request_id": {"type": "string"}, "wait_seconds": {"type": "number", "minimum": 0}}, "required": ["request_id"]}},
        {"name": SELF_CHECK_TOOL, "description": "Poll or answer a central self-check request. Omit response to poll. "
            "An answer's response must match this JSON Schema: " + json.dumps(SELF_CHECK_RESPONSE_SCHEMA, sort_keys=True),
         "inputSchema": {"type": "object", "properties": {"self_check_id": {"type": "string"}, "response": {"type": "object"}}, "required": ["self_check_id"]}}
    ]
    for line in sys.stdin:
        message = {}
        try:
            message = json.loads(line)
            method, params = message.get("method"), message.get("params", {})
            if method == "notifications/initialized":
                continue
            if method == "initialize":
                result = {"protocolVersion": params.get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}},
                          "serverInfo": {"name": "do-math-control-transport", "version": "5"}}
            elif method == "tools/list":
                result = {"tools": tools}
            elif method == "tools/call":
                arguments, name = params.get("arguments", {}), params.get("name")
                if name == "submit_draft":
                    if not binding.get("workspace"):
                        raise ValueError("submission binding has no workspace")
                    if __package__:
                        from .submission import request_control
                    else:
                        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                        from do_math.submission import request_control
                    kind = SUBMISSION_PREVIEW if arguments.get("preview") else SUBMIT_INTENT
                    delivery = request_control(binding["workspace"], arguments["draft_path"], kind=kind,
                        wait_seconds=arguments.get("wait_seconds", 0), binding=binding)
                    value = {"delivery": delivery}
                    result = _mcp_result(value)
                elif name == SUBMIT_TOOL:
                    value = ControlTransport.worker_submit(binding, request_id=arguments["request_id"], kind=arguments["kind"], payload=arguments["payload"])
                    if "wait_seconds" in arguments:
                        value["receipt"] = ControlTransport.wait_receipt(binding, arguments["request_id"], arguments["wait_seconds"])
                    result = _mcp_result(value)
                elif name == RECEIPT_TOOL:
                    result = _mcp_result(ControlTransport.wait_receipt(binding, arguments["request_id"], arguments.get("wait_seconds", 0)))
                elif name == SELF_CHECK_TOOL:
                    result = _mcp_result(ControlTransport.worker_self_check(binding, self_check_id=arguments["self_check_id"], response=arguments.get("response")))
                else:
                    raise ValueError("unknown control tool")
            else:
                raise ValueError("unsupported MCP method")
            if "id" in message:
                print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}, ensure_ascii=False), flush=True)
        except Exception as error:
            if "id" in message:
                print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32602, "message": str(error)}}, ensure_ascii=False), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    mcp = subparsers.add_parser("mcp")
    for name in BINDING_FIELDS:
        mcp.add_argument("--" + name.replace("_", "-"), required=True)
    mcp.add_argument("--workspace")
    args = parser.parse_args(argv)
    return _mcp_server({**{name: getattr(args, name) for name in BINDING_FIELDS},
                        **({"workspace": args.workspace} if args.workspace else {})})


if __name__ == "__main__":
    raise SystemExit(main())
