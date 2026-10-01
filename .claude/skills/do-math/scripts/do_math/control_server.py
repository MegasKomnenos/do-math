"""The worker side of the control transport (layer 3).

The provider CLI runs this file by name as the worker's MCP server
(``mcp_server_config``), and a worker tool waits for its receipt in real time
(``wait_receipt``). The transport itself, its files and its rules, is the
layer-2 ``control_transport``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
if __package__:
    from .control_protocol import (SUBMIT_TOOL, RECEIPT_TOOL, SELF_CHECK_TOOL, SUBMIT_INTENT, SUBMISSION_PREVIEW,
                                   REQUEST_KINDS, BINDING_FIELDS, SELF_CHECK_RESPONSE_SCHEMA)
    from .control_transport import FINAL_RECEIPTS, ControlTransport
else:
    from control_protocol import (SUBMIT_TOOL, RECEIPT_TOOL, SELF_CHECK_TOOL, SUBMIT_INTENT, SUBMISSION_PREVIEW,
                                  REQUEST_KINDS, BINDING_FIELDS, SELF_CHECK_RESPONSE_SCHEMA)
    from control_transport import FINAL_RECEIPTS, ControlTransport


def mcp_server_config(binding: dict) -> dict:
    if any(key not in binding for key in BINDING_FIELDS):
        raise ValueError("file transport binding lacks an MCP endpoint")
    arguments = [str(Path(__file__).resolve()), "mcp",
                 *("--" + key.replace("_", "-") + "=" + binding[key] for key in BINDING_FIELDS)]
    if binding.get("workspace"):
        arguments.append("--workspace=" + binding["workspace"])
    if binding.get("self_check"):
        arguments.append("--self-check")
    return {"command": sys.executable, "args": arguments}


def wait_receipt(binding: dict, request_id: str, timeout_seconds: float | None, *, clock) -> dict | None:
    if timeout_seconds is not None and (isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or timeout_seconds < 0):
        raise ValueError("timeout_seconds must be nonnegative or null")
    until = None if timeout_seconds is None else clock.monotonic() + timeout_seconds
    while True:
        receipt = ControlTransport.worker_receipt(binding, request_id)
        if receipt is not None and receipt.get("state") in FINAL_RECEIPTS:
            return receipt
        if until is not None and clock.monotonic() >= until:
            return receipt
        clock.sleep(0.05)


def _mcp_result(value: Any) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, sort_keys=True)}]}


def _mcp_server(binding: dict, *, clock) -> int:
    # Tool input schemas keep the node shapes preserved provider runs accepted; the
    # exact answer shape is described in text and checked by self_check_response_errors.
    tools = [
        {"name": "submit_draft", "description": "Validate and submit one workspace-relative draft; internal checks and hashes are derived automatically.",
         "inputSchema": {"type": "object", "properties": {"draft_path": {"type": "string"}, "preview": {"type": "boolean"}, "wait_seconds": {"type": "number", "minimum": 0}}, "required": ["draft_path"]}},
        {"name": SUBMIT_TOOL, "description": "Submit a safety boundary, a workspace-relative draft (payload draft_path) for submission or preview, or a self-check answer to the central execution pump.",
         "inputSchema": {"type": "object", "properties": {"request_id": {"type": "string"}, "kind": {"enum": sorted(REQUEST_KINDS)}, "payload": {"type": "object"}, "wait_seconds": {"type": "number", "minimum": 0}}, "required": ["request_id", "kind", "payload"]}},
        {"name": RECEIPT_TOOL, "description": "Read or wait for the central receipt using a caller-provided duration.",
         "inputSchema": {"type": "object", "properties": {"request_id": {"type": "string"}, "wait_seconds": {"type": "number", "minimum": 0}}, "required": ["request_id"]}},
        {"name": SELF_CHECK_TOOL, "description": "Poll or answer a central self-check request. Omit response to poll. "
            "An answer's response must match this JSON Schema: " + json.dumps(SELF_CHECK_RESPONSE_SCHEMA, sort_keys=True),
         "inputSchema": {"type": "object", "properties": {"self_check_id": {"type": "string"}, "response": {"type": "object"}}, "required": ["self_check_id"]}}
    ]
    if not binding.get("self_check"):
        tools = [tool for tool in tools if tool["name"] != SELF_CHECK_TOOL]
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
                        from .submission_tool import request_control
                    else:
                        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                        from do_math.submission_tool import request_control
                    kind = SUBMISSION_PREVIEW if arguments.get("preview") else SUBMIT_INTENT
                    delivery = request_control(binding["workspace"], arguments["draft_path"], kind=kind,
                        wait_seconds=arguments.get("wait_seconds", 0), binding=binding, clock=clock)
                    value = {"delivery": delivery}
                    result = _mcp_result(value)
                elif name == SUBMIT_TOOL:
                    value = ControlTransport.worker_submit(binding, request_id=arguments["request_id"], kind=arguments["kind"], payload=arguments["payload"])
                    if "wait_seconds" in arguments:
                        value["receipt"] = wait_receipt(binding, arguments["request_id"], arguments["wait_seconds"], clock=clock)
                    result = _mcp_result(value)
                elif name == RECEIPT_TOOL:
                    result = _mcp_result(wait_receipt(binding, arguments["request_id"], arguments.get("wait_seconds", 0), clock=clock))
                elif name == SELF_CHECK_TOOL and binding.get("self_check"):
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


def main(argv=None, *, ports=None, environment=None):
    import os
    if not __package__:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from do_math.wiring import real_ports
    environment = dict(os.environ) if environment is None else environment
    ports = real_ports(environment=environment) if ports is None else ports
    clock, jobs, backend = ports.clock, ports.jobs, ports.git_backend
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    mcp = subparsers.add_parser("mcp")
    for name in BINDING_FIELDS:
        mcp.add_argument("--" + name.replace("_", "-"), required=True)
    mcp.add_argument("--workspace")
    mcp.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    return _mcp_server({**{name: getattr(args, name) for name in BINDING_FIELDS},
                        **({"workspace": args.workspace} if args.workspace else {}),
                        **({"self_check": True} if args.self_check else {})}, clock=clock)


if __name__ == "__main__":
    raise SystemExit(main())
