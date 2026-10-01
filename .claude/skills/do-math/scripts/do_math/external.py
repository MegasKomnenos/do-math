"""Auditable, grant-bounded external HTTP operations."""
from __future__ import annotations
import base64, hashlib, os
from typing import Any, Callable
from urllib.error import URLError

from .values import parse_utc
from .canonical import exact_content_hash
from .http_request import check_body, check_url

# The states of one external operation; its EX execution reports the same set.
OPERATION_STATUSES = frozenset({"prepared", "confirmed", "failed", "unknown", "cancelled"})


def idempotency_key(operation_id: str, request_sha256: str) -> str: return hashlib.sha256((operation_id + request_sha256).encode()).hexdigest()
def request_binding_current(operation: dict) -> bool:
    """The stored request bytes and idempotency key still bind this operation ID."""
    digest = exact_content_hash(operation.get("request"))
    return operation.get("request_sha256") == digest and operation.get("idempotency_key") == idempotency_key(operation.get("id", ""), digest)

def retry_evidence_bound(operation: dict, evidence: dict) -> bool:
    """Retry evidence names this operation's exact request hash, idempotency key and an evidence ref."""
    return (evidence.get("request_sha256") == operation.get("request_sha256")
            and evidence.get("idempotency_key") == operation.get("idempotency_key") and bool(evidence.get("evidence_ref")))

def prepare_operation(request: dict, grant_id: str, source_ref: str, operation_id: str|None=None, *,
                      target_id=None, purpose=None, subject=None, actor_kind=None) -> dict:
    parsed=check_url(request)
    if not isinstance(grant_id,str) or not isinstance(source_ref,str) or not grant_id or not source_ref: raise ValueError("grant and source refs required")
    normalized={"method":request["method"],"url":parsed.geturl(),"body":check_body(request)}
    digest=exact_content_hash(normalized); oid=operation_id or hashlib.sha256((grant_id+source_ref+digest).encode()).hexdigest()[:24]
    scope = {key: value for key, value in {"target_id": target_id, "purpose": purpose, "subject": subject,
             "actor_kind": actor_kind}.items() if value is not None}
    if any(not isinstance(value, str) or not value.strip() for value in scope.values()):
        raise ValueError("external action scope fields must be nonempty text")
    return {"id":oid,"request":normalized,"request_sha256":digest,"grant_id":grant_id,"source_ref":source_ref,"status":"prepared","idempotency_key":idempotency_key(oid,digest),"attempts":[],"credential_env":None, **scope}

def validate_operation(operation: dict, grant: dict, now_iso: str, *, runtime=None, academic_check=None) -> None:
    if grant.get("id")!=operation.get("grant_id") or grant.get("status")!="active": raise ValueError("grant is inactive")
    from .governance import grant_time_reason
    time_reason = grant_time_reason(grant, parse_utc(now_iso))
    if time_reason: raise ValueError(time_reason)
    if any(header.lower() in {"idempotency-key", "host", "content-length"} for header in grant.get("credential_env", {})):
        raise ValueError("credential headers cannot override operation identity or routing")
    parsed=check_url(operation.get("request")); origin=f"{parsed.scheme}://{parsed.netloc}"
    check_body(operation["request"])
    if origin not in grant.get("allowed_origins",[]): raise ValueError("origin outside grant")
    if operation["request"]["method"] not in grant.get("allowed_methods",[]): raise ValueError("method outside grant")
    if not any(parsed.path.startswith(prefix) for prefix in grant.get("allowed_path_prefixes",[])): raise ValueError("path outside grant")
    if any(parsed.path.startswith(prefix) for prefix in grant.get("excluded_path_prefixes", [])): raise ValueError("path explicitly excluded")
    if origin in grant.get("excluded_origins", []): raise ValueError("origin explicitly excluded")
    if grant.get("kind") == "http":
        from .governance import grant_scope_reason
        action = {"id": operation.get("action_id", operation.get("id")), "target": operation.get("target_id"),
                  "role": "external_operation", "subject": operation.get("subject", "external_operation"),
                  "purpose": operation.get("purpose"), "actor_kind": operation.get("actor_kind")}
        reason = grant_scope_reason(grant, action, runtime, at=now_iso)
        if reason: raise ValueError(reason)
    if grant.get("academic_only") or grant.get("requires_academic") or operation.get("academic_binding") or operation.get("academic_basis"):
        if academic_check is None or not academic_check(operation, grant): raise ValueError("current academic prerequisite is not established")
    if not request_binding_current(operation): raise ValueError("request bytes or idempotency key changed")
    if operation.get("status") != "prepared": raise ValueError("operation is not startable")

def execute_operation(operation: dict, grant: dict, *, persist: Callable[[dict],Any], timeout_seconds=30, should_stop=None, transport,
                      runtime=None, academic_check=None, current_grant=None, clock, environment) -> dict:
    if operation.get("status")=="unknown": raise ValueError("unknown operation requires reconciliation")
    if operation.get("transmitted") or operation.get("transmission_phase") == "recorded":
        raise ValueError("recorded transmission requires recovery before another send")
    if operation.get("attempts"):
        retry = operation.get("retry_evidence", {})
        if not retry_evidence_bound(operation, retry):
            raise ValueError("retry lacks request-bound evidence")
        if retry.get("kind") not in {"effect_absent", "verified_idempotency"}: raise ValueError("invalid retry evidence kind")
        if retry["kind"] == "verified_idempotency" and (not retry.get("valid_until") or parse_utc(retry["valid_until"]) <= clock.wall()):
            raise ValueError("idempotency assurance expired")
    grant = current_grant(operation["grant_id"]) if current_grant else grant
    validate_operation(operation,grant,clock.now(),runtime=runtime,academic_check=academic_check)
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
            value=environment.get(env)  # layer: a credential is read only at send time and never stored
            if value is None:
                result={**prepared,"credential_env":[env],"waiting_reason":{"kind":"credential_unavailable","secret_ref":env},"transmitted":False}; return save(result)
            credential.append((header,value)); names.append(env)
        prepared["credential_env"]=names
    if should_stop and should_stop(): return save({**prepared,"status":"cancelled","transmitted":False})
    grant = current_grant(operation["grant_id"]) if current_grant else grant
    validate_operation(operation,grant,clock.now(),runtime=runtime,academic_check=academic_check)
    try:
        sending={**prepared,"transmitted":True,"transmission_phase":"recorded","attempts":[*prepared.get("attempts",[]),{"request_sha256":prepared["request_sha256"]}]}
        save(sending)
        response=transport(sending,credential,timeout_seconds)
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


def prepare_retry(operation, evidence, *, source, now_iso):
    if operation.get("status") not in {"unknown", "failed"} or source not in {"user", "adapter"}:
        raise ValueError("retry needs an uncertain or absent-effect operation and authorized evidence source")
    if not retry_evidence_bound(operation, evidence):
        raise ValueError("retry evidence must bind exact request and key")
    if evidence.get("kind") == "effect_absent":
        if operation.get("status") != "failed" or operation.get("effect_absent") is not True: raise ValueError("effect absence not established")
    elif evidence.get("kind") == "verified_idempotency":
        if not evidence.get("valid_until") or parse_utc(evidence["valid_until"]) <= parse_utc(now_iso): raise ValueError("idempotency evidence expired")
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
    parse_utc(evidence["observed_at"])
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
