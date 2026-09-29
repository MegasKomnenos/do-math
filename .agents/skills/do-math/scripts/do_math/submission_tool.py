"""Command-line side of the workspace submission tool (layer 3).

``input/tools/check_submission.py`` runs ``main`` inside the producer's own
process, and the MCP control server calls ``request_control``. Both only wire
the shared checks in ``submission`` to the control transport; the engine never
runs them, so the IDs they mint come from the operating system's clock.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import submission
from .submission import producer_check
from .system_clock import SystemClock


def request_control(workspace, draft, *, kind, wait_seconds, binding=None):
    """Send one draft locator; central capture owns validation and immutable receipt bytes."""
    from .control_server import wait_receipt
    from .control_transport import ControlTransport
    from .control_protocol import SUBMISSION_PREVIEW
    binding, payload = submission.control_request_payload(workspace, draft, kind=kind, wait_seconds=wait_seconds,
                                                          binding=binding)
    # A locator is mutable; a corrected draft at the same path is a new call.
    # Query the returned request_id to resume waiting on the existing call.
    request_id = ("preview-" if kind == SUBMISSION_PREVIEW else "submit-") + SystemClock().new_id("RQ")
    delivery = ControlTransport.worker_submit(binding, request_id=request_id, kind=kind, payload=payload)
    if delivery["state"] == "closed":
        return delivery
    return wait_receipt(binding, request_id, wait_seconds) or delivery


def main(argv=None):
    parser = argparse.ArgumentParser(description=submission.__doc__)
    parser.add_argument("--output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--submit", action="store_true")
    mode.add_argument("--new-knowledge-id", action="store_true",
                      help="Print a fresh KN replacement_id for sibling references; does not reserve or publish it")
    parser.add_argument("--wait-seconds", type=float)
    args = parser.parse_args(argv)
    if args.new_knowledge_id:
        if args.output is not None or args.wait_seconds is not None:
            parser.error("--new-knowledge-id does not take output or wait arguments")
        print(json.dumps({"replacement_id": SystemClock().new_id("KN")}))
        return 0
    if args.output is None:
        parser.error("--output is required for checking, preview and submission")
    if (args.preview or args.submit) and args.wait_seconds is None:
        parser.error("central control requires an explicit --wait-seconds budget")
    from .control_protocol import SUBMISSION_PREVIEW, SUBMIT_INTENT
    workspace = Path.cwd().resolve()
    if args.submit:
        try:
            delivery = request_control(workspace, args.output, kind=SUBMIT_INTENT, wait_seconds=args.wait_seconds)
        except (ValueError, TypeError, KeyError, OSError) as error:
            delivery = {"state": "rejected", "reason": str(error)}
        print(json.dumps({"delivery": delivery}, ensure_ascii=False))
        return 0 if delivery.get("state") == "accepted" else 1
    result = producer_check(workspace, args.output)
    if args.preview:
        try:
            delivery = request_control(workspace, args.output, kind=SUBMISSION_PREVIEW, wait_seconds=args.wait_seconds)
        except (ValueError, TypeError, KeyError, OSError) as error:
            delivery = {"state": "rejected", "reason": str(error)}
        print(json.dumps({"check": result, "delivery": delivery}, ensure_ascii=False))
        return 0 if delivery.get("state") == "previewed" else 1
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 1
