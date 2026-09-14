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
def _now(value: str) -> datetime: return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def _url(request: dict):
    if not isinstance(request, dict) or request.get("method") not in {"GET","POST","PUT","DELETE"} or not isinstance(request.get("url"),str): raise ValueError("request needs HTTP method and URL")
    parsed=urlsplit(request["url"])
    if parsed.scheme not in {"http","https"} or not parsed.netloc or parsed.username or parsed.password or parsed.fragment: raise ValueError("unsafe external URL")
    decoded=unquote(parsed.path)
    if any(part in {".",".."} for part in decoded.split("/")): raise ValueError("path traversal forbidden")
    return parsed

def prepare_operation(request: dict, grant_id: str, source_ref: str, operation_id: str|None=None) -> dict:
    parsed=_url(request)
    if not isinstance(grant_id,str) or not isinstance(source_ref,str) or not grant_id or not source_ref: raise ValueError("grant and source refs required")
    normalized={"method":request["method"],"url":parsed.geturl(),"body":request.get("body","")}
    if not isinstance(normalized["body"],str): raise ValueError("body must be text")
    digest=_hash(normalized); oid=operation_id or hashlib.sha256((grant_id+source_ref+digest).encode()).hexdigest()[:24]
    return {"id":oid,"request":normalized,"request_sha256":digest,"grant_id":grant_id,"source_ref":source_ref,"status":"prepared","idempotency_key":hashlib.sha256((oid+digest).encode()).hexdigest(),"attempts":[],"credential_env":None}

def validate_operation(operation: dict, grant: dict, now_iso: str) -> None:
    if grant.get("id")!=operation.get("grant_id") or grant.get("status")!="active": raise ValueError("grant is inactive")
    if grant.get("expires_at") and _now(now_iso)>=_now(grant["expires_at"]): raise ValueError("grant expired")
    if grant.get("valid_from") and _now(now_iso)<_now(grant["valid_from"]): raise ValueError("grant is not effective yet")
    if any(header.lower() in {"idempotency-key", "host", "content-length"} for header in grant.get("credential_env", {})):
        raise ValueError("credential headers cannot override operation identity or routing")
    parsed=_url(operation.get("request")); origin=f"{parsed.scheme}://{parsed.netloc}"
    if origin not in grant.get("allowed_origins",[]): raise ValueError("origin outside grant")
    if operation["request"]["method"] not in grant.get("allowed_methods",[]): raise ValueError("method outside grant")
    if not any(parsed.path.startswith(prefix) for prefix in grant.get("allowed_path_prefixes",[])): raise ValueError("path outside grant")
    if _hash(operation["request"])!=operation.get("request_sha256"): raise ValueError("request bytes changed")
    if operation.get("idempotency_key")!=hashlib.sha256((operation["id"]+operation["request_sha256"]).encode()).hexdigest(): raise ValueError("idempotency key changed")
    if operation.get("status") not in {"prepared","running"}: raise ValueError("operation is not startable")

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*_): raise ValueError("redirect forbidden")

def _http(request: dict, header: list[tuple[str,str]], timeout: int) -> dict:
    headers={"Idempotency-Key":request["idempotency_key"]}
    for name,value in header: headers[name]=value
    data=request["request"]["body"].encode() if request["request"]["method"] in {"POST","PUT"} else None
    req=Request(request["request"]["url"],data=data,headers=headers,method=request["request"]["method"])
    try:
        with build_opener(_NoRedirect).open(req,timeout=timeout) as response: body=response.read(); return {"http_status":response.status,"body":body}
    except HTTPError as error: return {"http_status":error.code,"body":error.read()}

def execute_operation(operation: dict, grant: dict, *, persist: Callable[[dict],Any], timeout_seconds=30, should_stop=None, transport=None) -> dict:
    if operation.get("status")=="unknown": raise ValueError("unknown operation requires reconciliation")
    if operation.get("attempts") and not operation.get("retry_authorized") and not grant.get("allow_idempotent_retry"): raise ValueError("retry is not granted")
    validate_operation(operation,grant,datetime.now(timezone.utc).isoformat())
    prepared={**operation,"status":"prepared","transmitted":False}
    if persist(prepared) is False: raise ValueError("prepared ledger is stale")
    running={**prepared,"status":"running","attempts":[*prepared.get("attempts",[]),{"request_sha256":prepared["request_sha256"]}]}
    if persist(running) is False: raise ValueError("running ledger is stale")
    if should_stop and should_stop():
        result={**running,"status":"failed","error":"stopped before transmission","transmitted":False}; persist(result); return result
    credential=[]
    if grant.get("credential_env"):
        names=[]
        for header,env in grant["credential_env"].items():
            value=os.environ.get(env)
            if value is None:
                result={**running,"status":"failed","error":"credential unavailable","credential_env":env,"transmitted":False}; persist(result); return result
            credential.append((header,value)); names.append(env)
        running["credential_env"]=names
    try:
        sending={**running,"transmitted":True}
        if persist(sending) is False: raise ValueError("sending ledger is stale")
        response=(transport or _http)(sending,credential,timeout_seconds)
    except (TimeoutError,URLError,OSError):
        result={**running,"status":"unknown","error":"transport outcome unknown","transmitted":True}; persist(result); return result
    body=response.get("body",b"")
    if not isinstance(body,bytes): raise ValueError("transport body must be bytes")
    result={**sending,"status":"confirmed","http_status":response["http_status"],"body_base64":base64.b64encode(body).decode(),"body_sha256":hashlib.sha256(body).hexdigest()}
    persist(result); return result

def reconcile_operation(operation: dict, evidence: str, result: str, *, source: str, succeeded: bool | None = None) -> dict:
    if operation.get("status")!="unknown" or source not in {"user","adapter"} or result not in {"confirmed","failed","cancelled"} or not evidence: raise ValueError("invalid reconciliation")
    if succeeded is not None and (not isinstance(succeeded, bool) or result != "confirmed"):
        raise ValueError("success evidence must be an explicit boolean for a confirmed reconciliation")
    return {**operation,"status":result,"reconciliation":{"source":source,"evidence":evidence,"succeeded":succeeded}}
