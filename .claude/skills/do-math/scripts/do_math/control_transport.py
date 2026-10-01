"""File-delivered local control messages for one execution.

Transport files are delivery material, not research state.  The engine is the
sole authority: it validates a request and publishes the authoritative record
before this module emits ``accepted``.  A local capability binds a cooperating
worker to an execution; it is not strong same-user authentication.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable
if __package__:
    from .control_protocol import (CONTROL_SERVER, SUBMIT_TOOL, RECEIPT_TOOL, SELF_CHECK_TOOL, SAFETY_BOUNDARY, SUBMIT_INTENT, SELF_CHECK_RESPONSE, SUBMISSION_PREVIEW, REQUEST_KINDS, SUBMISSION_KINDS, BINDING_FIELDS, SELF_CHECK_RESPONSE_SCHEMA, self_check_request_id, self_check_response_errors)
    from .file_io import read_bytes_shared, file_fingerprint, fingerprint_settled, write_bytes_atomic
    from .values import compact_json_bytes, check_path_segment, json_digest, require_text
else:
    from control_protocol import (CONTROL_SERVER, SUBMIT_TOOL, RECEIPT_TOOL, SELF_CHECK_TOOL, SAFETY_BOUNDARY, SUBMIT_INTENT, SELF_CHECK_RESPONSE, SUBMISSION_PREVIEW, REQUEST_KINDS, SUBMISSION_KINDS, BINDING_FIELDS, SELF_CHECK_RESPONSE_SCHEMA, self_check_request_id, self_check_response_errors)
    from file_io import read_bytes_shared, file_fingerprint, fingerprint_settled, write_bytes_atomic
    from values import compact_json_bytes, check_path_segment, json_digest, require_text


FINAL_RECEIPTS = frozenset({"accepted", "rejected", "closed", "previewed"})


def _require_text(value: Any, name: str) -> str:
    """Nonempty text (``values.require_text``) that a transport file or path can also carry: no NUL."""
    if "\0" in require_text(value, name):
        raise ValueError(f"{name} must be NUL-free")
    return value


def _require_file_name(value: Any, name: str) -> str:
    """One Windows file name segment (``values.check_path_segment``) that also has no ``[`` or ``]``."""
    value = _require_text(value, name)
    try:
        check_path_segment(value)
    except ValueError:
        raise ValueError(f"{name} must be a safe file name component") from None
    if "[" in value or "]" in value:
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



def _token(clock, nbytes: int) -> str:
    """``secrets.token_urlsafe(nbytes)``'s format, drawn from the clock port's random source."""
    return base64.urlsafe_b64encode(bytes.fromhex(clock.random_hex(nbytes))).rstrip(b"=").decode("ascii")


class ControlTransport:
    """A pumpable local transport; it neither starts a daemon nor owns state."""

    def __init__(self, root: Path | str | None = None, *, clock):
        """``clock`` is the clock port; its random source draws the transport and capability tokens."""
        self.clock = clock
        self.root = None if root is None else Path(root).resolve()
        self._capabilities: dict[str, dict] = {}
        self._receipts: dict[tuple[str | None, str], dict] = {}  # (transport_id, request_id) -> receipt
        self._pump_cache: dict[Path, tuple[tuple, dict]] = {}
        # Only open transports can receive new deliveries; a pump reads their inboxes alone.
        # The set is read from disk at the first pump: commands that never pump read no transport.
        self._open: set[str] | None = None

    def issue(self, execution_id: str, grant_id: str, *, workspace: Path | str | None = None,
              self_check: bool = False) -> dict:
        _require_text(execution_id, "execution_id")
        _require_text(grant_id, "grant_id")
        transport_id, capability = _token(self.clock, 18), _token(self.clock, 32)
        binding = {"transport_id": transport_id, "capability": capability,
                   "execution_id": execution_id, "grant_id": grant_id}
        if workspace is not None:
            binding["workspace"] = str(Path(workspace).resolve())
        if self_check:
            binding["self_check"] = True
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
            if previous.get("state") in FINAL_RECEIPTS:
                return previous
        try:
            request = self._validate_request(request)
        except ValueError as error:
            return self._reject_unvalidated(request, str(error))
        state = self._state(request)
        if state["state"] != "open":
            return self._store(request, {"state": "closed", "reason": state.get("reason", "transport is not open")})
        if publish is None:
            return self._store(request, {"state": "received"})
        decision = publish(deepcopy(request))
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

    def pump(self, publish: Callable[[dict], dict] | None = None) -> list[dict]:
        """Read delivery files and call the engine's validation-and-CAS hook."""
        if self.root is None:
            raise ValueError("a memory-only transport has no inbox to pump")
        if self._open is None:
            # issue and close keep state.json current, so this scan sees every earlier issue and close.
            self._open = ({path.parent.name for path in self.root.glob("*/binding.json") if _is_open(path.parent)}
                          if self.root.is_dir() else set())
        paths = [path for transport_id in sorted(self._open)
                 for path in sorted((self.root / transport_id / "inbox").glob("*.json"))]
        return self._pump_paths(paths, publish)

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
            if (receipt.get('state') in FINAL_RECEIPTS and fingerprint_settled(mark)
                    and file_fingerprint(path) == mark):
                self._pump_cache[path] = (mark, deepcopy(receipt))
        return results

    def close(self, binding: dict, *, reason: str) -> dict:
        endpoint = self._endpoint(binding)
        _require_text(reason, "reason")
        state = {"state": "closed", "reason": reason}
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
            raise ValueError("a closed transport cannot request a self-check")
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
            return {"request_id": request_id, "state": "closed", "reason": state.get("reason", "transport is not open")}
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
