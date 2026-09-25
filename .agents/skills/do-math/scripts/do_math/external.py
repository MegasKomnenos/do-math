"""Auditable, grant-bounded external HTTP operations."""
from __future__ import annotations
import base64, hashlib, json, os
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, unquote
from urllib.request import HTTPRedirectHandler, Request, build_opener


def _canon(value: Any) -> bytes: return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
def _hash(value: Any) -> str: return hashlib.sha256(_canon(value)).hexdigest()
def _now(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError('external authority time must be a nonempty timestamp string')
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None: raise ValueError("external authority time requires timezone")
    return result.astimezone(timezone.utc)

def _url(request: dict):
    if not isinstance(request, dict) or request.get("method") not in {"GET","POST","PUT","DELETE"} or not isinstance(request.get("url"),str): raise ValueError("request needs HTTP method and URL")
    parsed=urlsplit(request["url"])
    if parsed.scheme not in {"http","https"} or not parsed.netloc or parsed.username or parsed.password or parsed.fragment: raise ValueError("unsafe external URL")
    decoded=unquote(parsed.path)
    if any(part in {".",".."} for part in decoded.split("/")): raise ValueError("path traversal forbidden")
    return parsed


def _body(request: dict) -> str:
    body = request.get("body", "")
    if not isinstance(body, str):
        raise ValueError("body must be text")
    if request["method"] in {"GET", "DELETE"} and body:
        raise ValueError("GET and DELETE cannot carry a nonempty body")
    return body

def prepare_operation(request: dict, grant_id: str, source_ref: str, operation_id: str|None=None, *,
                      target_id=None, purpose=None, subject=None, budget_kind=None, actor_kind=None) -> dict:
    parsed=_url(request)
    if not isinstance(grant_id,str) or not isinstance(source_ref,str) or not grant_id or not source_ref: raise ValueError("grant and source refs required")
    normalized={"method":request["method"],"url":parsed.geturl(),"body":_body(request)}
    digest=_hash(normalized); oid=operation_id or hashlib.sha256((grant_id+source_ref+digest).encode()).hexdigest()[:24]
    scope = {key: value for key, value in {"target_id": target_id, "purpose": purpose, "subject": subject,
             "budget_kind": budget_kind, "actor_kind": actor_kind}.items() if value is not None}
    if any(not isinstance(value, str) or not value.strip() for value in scope.values()):
        raise ValueError("external action scope fields must be nonempty text")
    return {"id":oid,"request":normalized,"request_sha256":digest,"grant_id":grant_id,"source_ref":source_ref,"status":"prepared","idempotency_key":hashlib.sha256((oid+digest).encode()).hexdigest(),"attempts":[],"credential_env":None, **scope}

def validate_operation(operation: dict, grant: dict, now_iso: str, *, runtime=None, academic_check=None) -> None:
    if grant.get("id")!=operation.get("grant_id") or grant.get("status")!="active": raise ValueError("grant is inactive")
    if grant.get("expires_at") and _now(now_iso)>=_now(grant["expires_at"]): raise ValueError("grant expired")
    if grant.get("valid_from") and _now(now_iso)<_now(grant["valid_from"]): raise ValueError("grant is not effective yet")
    if any(header.lower() in {"idempotency-key", "host", "content-length"} for header in grant.get("credential_env", {})):
        raise ValueError("credential headers cannot override operation identity or routing")
    parsed=_url(operation.get("request")); origin=f"{parsed.scheme}://{parsed.netloc}"
    _body(operation["request"])
    if origin not in grant.get("allowed_origins",[]): raise ValueError("origin outside grant")
    if operation["request"]["method"] not in grant.get("allowed_methods",[]): raise ValueError("method outside grant")
    if not any(parsed.path.startswith(prefix) for prefix in grant.get("allowed_path_prefixes",[])): raise ValueError("path outside grant")
    if any(parsed.path.startswith(prefix) for prefix in grant.get("excluded_path_prefixes", [])): raise ValueError("path explicitly excluded")
    if origin in grant.get("excluded_origins", []): raise ValueError("origin explicitly excluded")
    if grant.get("kind") == "http":
        from .governance import grant_scope_reason
        action = {"id": operation.get("action_id", operation.get("id")), "target": operation.get("target_id"),
                  "role": "external_operation", "subject": operation.get("subject", "external_operation"),
                  "purpose": operation.get("purpose"), "budget_kind": operation.get("budget_kind"),
                  "actor_kind": operation.get("actor_kind")}
        reason = grant_scope_reason(grant, action, runtime, at=now_iso)
        if reason: raise ValueError(reason)
    if grant.get("academic_only") or grant.get("requires_academic") or operation.get("academic_binding") or operation.get("academic_basis"):
        if academic_check is None or not academic_check(operation, grant): raise ValueError("current academic prerequisite is not established")
    if _hash(operation["request"])!=operation.get("request_sha256"): raise ValueError("request bytes changed")
    if operation.get("idempotency_key")!=hashlib.sha256((operation["id"]+operation["request_sha256"]).encode()).hexdigest(): raise ValueError("idempotency key changed")
    if operation.get("status") != "prepared": raise ValueError("operation is not startable")

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*_): raise ValueError("redirect forbidden")

def _http(request: dict, header: list[tuple[str,str]], timeout: int) -> dict:
    headers={"Idempotency-Key":request["idempotency_key"]}
    for name,value in header: headers[name]=value
    _url(request["request"])
    body = _body(request["request"])
    data=body.encode() if request["request"]["method"] in {"POST", "PUT"} and body else None
    req=Request(request["request"]["url"],data=data,headers=headers,method=request["request"]["method"])
    try:
        with build_opener(_NoRedirect).open(req,timeout=timeout) as response: body=response.read(); return {"http_status":response.status,"body":body}
    except HTTPError as error: return {"http_status":error.code,"body":error.read()}

def execute_operation(operation: dict, grant: dict, *, persist: Callable[[dict],Any], timeout_seconds=30, should_stop=None, transport=None,
                      runtime=None, academic_check=None, current_grant=None) -> dict:
    if operation.get("status")=="unknown": raise ValueError("unknown operation requires reconciliation")
    if operation.get("transmitted") or operation.get("transmission_phase") == "recorded":
        raise ValueError("recorded transmission requires recovery before another send")
    if operation.get("attempts"):
        retry = operation.get("retry_evidence", {})
        if retry.get("request_sha256") != operation.get("request_sha256") or retry.get("idempotency_key") != operation.get("idempotency_key") or not retry.get("evidence_ref"):
            raise ValueError("retry lacks request-bound evidence")
        if retry.get("kind") not in {"effect_absent", "verified_idempotency"}: raise ValueError("invalid retry evidence kind")
        if retry["kind"] == "verified_idempotency" and (not retry.get("valid_until") or _now(retry["valid_until"]) <= datetime.now(timezone.utc)):
            raise ValueError("idempotency assurance expired")
    grant = current_grant(operation["grant_id"]) if current_grant else grant
    validate_operation(operation,grant,datetime.now(timezone.utc).isoformat(),runtime=runtime,academic_check=academic_check)
    def save(record):
        if persist(record) is False: raise ValueError("operation ledger is stale; recover recorded transmission before retry")
        return record
    prepared={**operation,"status":"prepared","transmitted":False,"transmission_phase":"not_started"}
    # Re-evaluate resources for this attempt; an old wait is not its outcome.
    prepared.pop("waiting_reason", None)
    save(prepared)
    if should_stop and should_stop():
        result={**prepared,"status":"cancelled","error":"stopped before transmission","transmitted":False}; return save(result)
    credential=[]
    if grant.get("credential_env"):
        names=[]
        for header,env in grant["credential_env"].items():
            value=os.environ.get(env)
            if value is None:
                result={**prepared,"credential_env":[env],"waiting_reason":{"kind":"credential_unavailable","secret_ref":env},"transmitted":False}; return save(result)
            credential.append((header,value)); names.append(env)
        prepared["credential_env"]=names
    if should_stop and should_stop(): return save({**prepared,"status":"cancelled","transmitted":False})
    grant = current_grant(operation["grant_id"]) if current_grant else grant
    validate_operation(operation,grant,datetime.now(timezone.utc).isoformat(),runtime=runtime,academic_check=academic_check)
    try:
        sending={**prepared,"transmitted":True,"transmission_phase":"recorded","attempts":[*prepared.get("attempts",[]),{"request_sha256":prepared["request_sha256"]}]}
        save(sending)
        response=(transport or _http)(sending,credential,timeout_seconds)
    except (TimeoutError,URLError,OSError):
        result={**sending,"status":"unknown","error":"transport outcome unknown","transmitted":True}; return save(result)
    body=response.get("body",b"")
    if not isinstance(body,bytes): raise ValueError("transport body must be bytes")
    status = response["http_status"]
    if 200 <= status < 300:
        result={**sending,"status":"confirmed","succeeded":True,"effect_absent":False}
    elif response.get("effect_absent") is True:
        result={**sending,"status":"failed","succeeded":False,"effect_absent":True}
    else:
        result={**sending,"status":"unknown","succeeded":None,"error":"non-success response does not establish effect absence"}
    result.update(http_status=status, body_base64=base64.b64encode(body).decode(), body_sha256=hashlib.sha256(body).hexdigest())
    return save(result)


def recover_operation(operation):
    """A durable send marker is uncertainty, not proof of either success or absence."""
    if operation.get("status") == "prepared" and (operation.get("transmitted") or operation.get("transmission_phase") == "recorded"):
        return {**operation, "status": "unknown", "handling": "reconciliation_required"}
    return dict(operation)


def prepare_retry(operation, evidence, *, source, now_iso=None):
    if operation.get("status") not in {"unknown", "failed"} or source not in {"user", "adapter"}:
        raise ValueError("retry needs an uncertain or absent-effect operation and authorized evidence source")
    if evidence.get("request_sha256") != operation["request_sha256"] or evidence.get("idempotency_key") != operation["idempotency_key"] or not evidence.get("evidence_ref"):
        raise ValueError("retry evidence must bind exact request and key")
    if evidence.get("kind") == "effect_absent":
        if operation.get("status") != "failed" or operation.get("effect_absent") is not True: raise ValueError("effect absence not established")
    elif evidence.get("kind") == "verified_idempotency":
        if not evidence.get("valid_until") or _now(evidence["valid_until"]) <= _now(now_iso or datetime.now(timezone.utc).isoformat()): raise ValueError("idempotency evidence expired")
    else: raise ValueError("unsupported retry evidence")
    return {**operation,"status":"prepared","transmitted":False,"transmission_phase":"not_started",
            "retry_evidence": {**evidence, "source":source}, "previous_outcome":operation["status"]}

def reconcile_operation(operation: dict, evidence: dict, result: str, *, source: str, succeeded: bool | None = None,
                        effect_absent: bool | None = None, idempotency_evidence: str | None = None) -> dict:
    if operation.get("status") != "unknown" or source not in {"user", "adapter"} or not isinstance(evidence, dict):
        raise ValueError("invalid reconciliation")
    if (evidence.get("operation_id") != operation["id"] or evidence.get("request_sha256") != operation["request_sha256"]
            or evidence.get("idempotency_key") != operation["idempotency_key"] or not evidence.get("evidence_ref") or not evidence.get("observed_at")):
        raise ValueError("reconciliation evidence must bind the exact external operation")
    _now(evidence["observed_at"])
    expected = {"confirmed":"succeeded", "failed":"effect_absent", "cancelled":"not_transmitted"}.get(result)
    if evidence.get("fact") != expected: raise ValueError("evidence fact differs from asserted outcome")
    if result == "confirmed" and succeeded is True:
        pass
    elif result == "failed" and effect_absent is True:
        succeeded = False
    elif result == "cancelled" and evidence["fact"] == "not_transmitted":
        pass
    else:
        raise ValueError("reconciliation needs evidence for the asserted external-effect fact")
    return {**operation, "status": result, "succeeded": succeeded, "effect_absent": effect_absent,
            "handling": "reconciled", "external_id": evidence.get("external_id", operation.get("external_id")),
            "reconciliation": {"source": source, "evidence": evidence, "succeeded": succeeded,
                                 "effect_absent": effect_absent, "idempotency_evidence": idempotency_evidence}}
