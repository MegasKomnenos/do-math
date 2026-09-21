#!/usr/bin/env python3
"""Portable TypeSafe/Jev CLI. Python 3.10+, standard library only."""
import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import http.client
import json
import math
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
RETRYABLE = {429, 500, 502, 503, 504, 529}


class JevError(Exception):
    def __init__(self, kind, message, exit_code=1, status=None):
        super().__init__(message)
        self.kind, self.exit_code, self.status = kind, exit_code, status


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise JevError("input", message, 2)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    # Never forward the API key to a redirected URL.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def require(condition, message):
    if not condition:
        raise JevError("input", message, 2)


def parse_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def number(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("JSON numbers must be finite")
        return parsed

    def constant(value):
        raise ValueError("invalid JSON constant: " + value)

    try:
        return json.loads(text.lstrip("\ufeff"), object_pairs_hook=pairs,
                          parse_float=number, parse_constant=constant)
    except (ValueError, RecursionError) as exc:
        raise JevError("input", "Invalid JSON: " + str(exc), 2) from exc


def read_text(path):
    try:
        if path == "-":
            require(not sys.stdin.isatty(), "Provide --input FILE or pipe JSON to standard input.")
            return sys.stdin.read().lstrip("\ufeff")
        return Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise JevError("input", "Cannot read UTF-8 input: " + str(exc), 2) from exc


def description(value):
    return value is None or isinstance(value, (str, dict, list))


def validate_request(payload):
    require(isinstance(payload, dict), "The request must be a JSON object.")
    require(not payload.keys() - {"state", "questions", "model"}, "Unknown request field; use state, questions, model.")
    require(isinstance(payload.get("state"), (str, dict, list)), "state must be text, an object, or an array.")
    questions = payload.get("questions")
    require(isinstance(questions, dict) and bool(questions), "questions must be a nonempty object keyed by question ID.")
    require(isinstance(payload.get("model"), str) and bool(payload["model"].strip()), "model must be a nonempty string.")
    for qid, question in questions.items():
        require(bool(qid.strip()), "Question IDs must be nonempty strings.")
        prefix = "Question " + qid + ": "
        require(isinstance(question, dict), prefix + "must be an object.")
        require(not question.keys() - {"type", "instructions", "criteria"}, prefix + "unknown field; use type, instructions, criteria.")
        kind = question.get("type")
        require(kind in ("choice", "score", "noul"), prefix + "type must be choice, score, or noul.")
        require("instructions" in question and description(question["instructions"]), prefix + "instructions must be text, an object, an array, or null.")
        criteria = question.get("criteria")
        if kind == "choice":
            require(isinstance(criteria, dict) and 1 <= len(criteria) <= 255, prefix + "Choice criteria must contain 1 to 255 options.")
            values = criteria.values()
        elif kind == "score":
            require(isinstance(criteria, list) and 2 <= len(criteria) <= 10, prefix + "Score criteria must contain 2 to 10 ordered levels.")
            values = criteria
        else:
            require("criteria" not in question or isinstance(criteria, dict), prefix + "Noul criteria must be an object when supplied.")
            require(criteria is None or not criteria.keys() - {"true", "false"}, prefix + "Noul criteria keys must be true or false.")
            values = (criteria or {}).values()
        require(all(description(value) for value in values), prefix + "criterion descriptions must be text, objects, arrays, or null.")


def numeric(value, low=0, high=None):
    return (type(value) in (int, float) and (type(value) is int or math.isfinite(value))
            and value >= low and (high is None or value <= high))


def validate_response(result, questions):
    def check(condition):
        if not condition:
            raise JevError("response", "The service returned an incomplete or invalid judgment response.")

    check(isinstance(result, dict))
    check(isinstance(result.get("model"), str) and bool(result["model"]))
    answers, usage = result.get("answers"), result.get("usage")
    check(isinstance(answers, dict) and set(answers) == set(questions))
    check(isinstance(usage, dict))
    check(all(type(usage.get(key)) is int and usage[key] >= 0 for key in ("input_tokens", "output_tokens")))
    for qid, question in questions.items():
        answer = answers[qid]
        kind = question["type"]
        check(isinstance(answer, dict) and answer.get("type") == kind)
        if kind == "noul":
            check(numeric(answer.get("noul"), high=1))
            continue
        check(numeric(answer.get("confidence"), high=1))
        probabilities = answer.get("probabilities")
        keys = set(question["criteria"]) if kind == "choice" else {str(i) for i in range(len(question["criteria"]))}
        check(isinstance(probabilities, dict) and set(probabilities) == keys)
        check(all(numeric(value, high=1) for value in probabilities.values()))
        if kind == "choice":
            check(isinstance(answer.get("choice"), str) and answer["choice"] in keys)
        else:
            check(numeric(answer.get("score"), high=len(keys) - 1))
            check(isinstance(answer.get("legend"), dict) and set(answer["legend"]) == keys)


def retry_delay(headers, attempt):
    """Honor Retry-After; stop instead of waiting over 30 seconds or retrying early."""
    value = headers.get("Retry-After")
    try:
        if value is not None:
            try:
                delay = float(value)
            except ValueError:
                date = parsedate_to_datetime(value)
                delay = (date - datetime.now(timezone.utc)).total_seconds()
        elif headers.get("retry-after-ms") is not None:
            delay = float(headers["retry-after-ms"]) / 1000
        else:
            delay = min(0.5 * 2 ** attempt, 8)
        if not math.isfinite(delay) or delay > 30:
            return None
        return max(0, delay)
    except (TypeError, ValueError, OverflowError):
        return min(0.5 * 2 ** attempt, 8)


def evaluate(payload, api_key, *, timeout=60, retries=2):
    data = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    request = urllib.request.Request(ENDPOINT, data=data, headers={
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "jev-cli/1.0",
    }, method="POST")
    opener = urllib.request.build_opener(NoRedirect())
    for attempt in range(retries + 1):
        try:
            with opener.open(request, timeout=timeout) as response:
                raw = response.read()
            try:
                result = parse_json(raw.decode("utf-8-sig"))
            except (UnicodeError, JevError) as exc:
                raise JevError("response", "The service did not return valid UTF-8 JSON.") from exc
            validate_response(result, payload["questions"])
            return result
        except urllib.error.HTTPError as exc:
            with exc:
                delay = retry_delay(exc.headers, attempt)
                if exc.code in RETRYABLE and attempt < retries and delay is not None:
                    time.sleep(delay)
                    continue
                try:
                    detail = exc.read(4096).decode("utf-8", errors="replace")
                except (OSError, http.client.HTTPException) as interrupted:
                    raise JevError("network", "The HTTP error response was interrupted; the request was not repeated.") from interrupted
            message = "HTTP " + str(exc.code) + ": " + detail
            if delay is None and exc.code in RETRYABLE:
                message += " (Server retry delay exceeds the 30-second automatic wait limit.)"
            raise JevError("http", message.replace(api_key, "[REDACTED]"), status=exc.code) from exc
        except (urllib.error.URLError, OSError, http.client.HTTPException) as exc:
            # After an interrupted response the server may already have charged the request.
            raise JevError("network", ("Request failed; it was not automatically repeated because server completion is unknown: " + str(exc)).replace(api_key, "[REDACTED]")) from exc


def main(argv=None):
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        parser = Parser(description="Ask Jev typed questions. Read UTF-8 JSON from a file or stdin; emit JSON.", allow_abbrev=False)
        parser.add_argument("--input", metavar="FILE", help="request JSON file; '-' reads stdin (default)")
        parser.add_argument("--state", metavar="FILE", help="separate context file; '-' reads stdin")
        parser.add_argument("--state-format", choices=("text", "json"), default=None, help="format of --state (default: text)")
        parser.add_argument("--questions", metavar="FILE", help="questions JSON file for use with --state")
        parser.add_argument("--model", help="override request model, TYPESAFE_DEFAULT_MODEL, and jev-latest")
        parser.add_argument("--timeout", type=float, default=60, help="socket operation timeout in seconds (default: 60)")
        parser.add_argument("--retries", type=int, default=2, help="extra attempts on transient HTTP errors, 0..10 (default: 2)")
        parser.add_argument("--dry-run", action="store_true", help="validate and print the request without a network call or API key")
        args = parser.parse_args(argv)
        require(math.isfinite(args.timeout) and args.timeout > 0, "--timeout must be a positive finite number.")
        require(0 <= args.retries <= 10, "--retries must be between 0 and 10.")
        separate = args.state is not None or args.questions is not None
        if separate:
            require(args.input is None, "Use --input OR --state with --questions.")
            require(args.state is not None and args.questions is not None, "--state and --questions must be provided together.")
            require(not (args.state == args.questions == "-"), "Only one input may read stdin.")
            state = read_text(args.state)
            if args.state_format == "json":
                state = parse_json(state)
            payload = {"state": state, "questions": parse_json(read_text(args.questions))}
        else:
            require(args.state_format is None, "--state-format requires --state.")
            payload = parse_json(read_text(args.input or "-"))
        require(isinstance(payload, dict), "The request must be a JSON object.")
        payload["model"] = (args.model if args.model is not None else
                            payload.get("model", os.environ.get("TYPESAFE_DEFAULT_MODEL", "jev-latest")))
        validate_request(payload)
        if args.dry_run:
            result = payload
        else:
            api_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
            if not api_key or any(ord(char) < 33 or ord(char) > 126 for char in api_key):
                raise JevError("configuration", "Set TYPESAFE_API_KEY to a valid API key in the calling process environment.", 2)
            result = evaluate(payload, api_key, timeout=args.timeout, retries=args.retries)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except JevError as exc:
        error = {"kind": exc.kind, "message": str(exc)}
        if exc.status is not None:
            error["status"] = exc.status
        print(json.dumps({"error": error}, ensure_ascii=False), file=sys.stderr)
        return exc.exit_code
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(json.dumps({"error": {"kind": "io", "message": str(exc)}}, ensure_ascii=True), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('{"error":{"kind":"interrupted","message":"Interrupted by caller."}}', file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
