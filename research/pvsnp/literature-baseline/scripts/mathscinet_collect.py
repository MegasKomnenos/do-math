#!/usr/bin/env python3
"""Collect one MathSciNet citation page per B002 MSC field through KUDOS."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import NamedTuple, Sequence
from urllib.parse import quote, urlencode, urlsplit, urlunsplit


SCRIPT_PATH = Path(__file__).resolve()
BASELINE_ROOT = SCRIPT_PATH.parents[1]
REPOSITORY_ROOT = SCRIPT_PATH.parents[4]
DEFAULT_QUERY_TABLE = BASELINE_ROOT / "batches" / "B002-queries.tsv"
DEFAULT_OUTPUT_ROOT = BASELINE_ROOT / "intake" / "B002" / "mathscinet"
DEFAULT_CREDENTIALS = REPOSITORY_ROOT / ".credentials" / "kudos.md"

KUDOS_LOGIN_URL = "https://kudos.knu.ac.kr/pages/login.htm"
KUDOS_DATABASES_URL = (
    "https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542"
)
KUDOS_PROXY_URL = "https://kudos.knu.ac.kr/include/proxyGo.php"
MATHSCINET_SEARCH_URL = (
    "https://mathscinet.ams.org/mathscinet/publications-search"
)
MAX_CITATIONS_PER_FIELD = 100


class CollectorError(RuntimeError):
    pass


class CredentialError(CollectorError):
    pass


class ExistingOutputError(CollectorError):
    pass


class OutputValidationError(CollectorError):
    pass


class BrowserContractError(CollectorError):
    pass


class Credentials:
    __slots__ = ("user_id", "password")

    def __init__(self, user_id: str, password: str) -> None:
        self.user_id = user_id
        self.password = password

    def __repr__(self) -> str:
        return "Credentials(user_id=<redacted>, password=<redacted>)"


class Query(NamedTuple):
    field_code: str
    field_name: str
    raw_query: str

    @property
    def expected_codes(self) -> tuple[str, ...]:
        return tuple(
            part.strip()
            for part in re.split(r"\s+OR\s+", self.raw_query, flags=re.IGNORECASE)
            if part.strip()
        )

    @property
    def mathscinet_query(self) -> str:
        return f"pcsc:({' OR '.join(self.expected_codes)})"


class ValidationResult(NamedTuple):
    record_count: int
    matched_count: int


def _unwrap_secret(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "`\"'":
        return value[1:-1]
    return value


def load_credentials(path: Path) -> Credentials:
    values: dict[str, str] = {}
    pattern = re.compile(r"^\s*(?:[-*]\s*)?(ID|PW)\s*:\s*(.*?)\s*$", re.I)
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as error:
        raise CredentialError("KUDOS credential file is unavailable") from error

    for line in lines:
        match = pattern.match(line)
        if not match:
            continue
        key = match.group(1).upper()
        if key in values:
            raise CredentialError(f"duplicate credential key: {key}")
        values[key] = _unwrap_secret(match.group(2))

    if not values.get("ID") or not values.get("PW"):
        raise CredentialError("credential file must contain nonempty ID and PW keys")
    return Credentials(values["ID"], values["PW"])


def load_queries(path: Path) -> list[Query]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
    except OSError as error:
        raise CollectorError("B002 query table is unavailable") from error

    queries: list[Query] = []
    seen: set[str] = set()
    for row_number, row in enumerate(rows, 2):
        code = (row.get("field_code") or "").strip()
        name = (row.get("field_name") or "").strip()
        raw_query = (row.get("query") or "").strip()
        if not re.fullmatch(r"\d{2}", code):
            raise CollectorError(f"invalid field_code at query-table row {row_number}")
        if code in seen:
            raise CollectorError(f"duplicate field_code in query table: {code}")
        query = Query(code, name, raw_query)
        expected = query.expected_codes
        if not name or not expected:
            raise CollectorError(f"incomplete query-table row for field {code}")
        if any(not re.fullmatch(rf"{code}-\d{{2}}", item) for item in expected):
            raise CollectorError(f"query codes do not belong to field {code}")
        seen.add(code)
        queries.append(query)

    if not queries:
        raise CollectorError("query table contains no queries")
    return queries


def _bibtex_entries(text: str) -> list[tuple[str, str]]:
    starts = list(
        re.finditer(r"@([A-Za-z]+)\s*[\{(]\s*([^,\s]+)\s*,", text)
    )
    entries: list[tuple[str, str]] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        entries.append((match.group(2), text[match.start() : end]))
    return entries


def validate_bibtex(
    text: str,
    *,
    expected_codes: Sequence[str],
    expected_count: int | None = None,
) -> ValidationResult:
    entries = _bibtex_entries(text)
    if not entries:
        raise OutputValidationError("citation output contains no BibTeX entries")
    if len(entries) > MAX_CITATIONS_PER_FIELD:
        raise OutputValidationError("citation output exceeds the 100-record limit")
    if expected_count is not None and len(entries) != expected_count:
        raise OutputValidationError(
            f"citation count mismatch: expected {expected_count}, got {len(entries)}"
        )

    keys = [key for key, _ in entries]
    if len(keys) != len(set(keys)):
        raise OutputValidationError("citation output contains duplicate BibTeX keys")

    matched = 0
    for _, entry in entries:
        class_match = re.search(
            r"(?mi)^\s*mrclass\s*=\s*\{([^}]*)\}", entry
        )
        if class_match and any(code in class_match.group(1) for code in expected_codes):
            matched += 1
    if matched == 0:
        raise OutputValidationError("no exported entry matches the requested MSC codes")
    return ValidationResult(len(entries), matched)


def atomic_store(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _valid_result_marker(path: Path, query: Query) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        data.get("field_code") == query.field_code
        and data.get("status") == "no_results"
        and data.get("result_count") == 0
    )


def _existing_valid_export(directory: Path, query: Query) -> Path | None:
    if not directory.exists():
        return None
    files = [
        item
        for item in directory.iterdir()
        if item.is_file() and not item.name.endswith(".tmp")
    ]
    if not files:
        return None

    marker = directory / "result.json"
    if marker in files and _valid_result_marker(marker, query):
        return marker

    candidates = [
        item
        for item in files
        if item.suffix.lower() in {"", ".bib"} and item.name != "result.json"
    ]
    for candidate in candidates:
        try:
            validate_bibtex(
                candidate.read_text(encoding="utf-8-sig"),
                expected_codes=query.expected_codes,
            )
        except (OSError, UnicodeError, OutputValidationError):
            continue
        return candidate
    raise ExistingOutputError(
        f"field {query.field_code} has files but no valid export; refusing overwrite"
    )


def plan_queries(
    queries: Sequence[Query],
    output_root: Path,
    requested_codes: set[str] | None = None,
) -> tuple[list[Query], list[str]]:
    known = {item.field_code for item in queries}
    if requested_codes is not None:
        unknown = requested_codes - known
        if unknown:
            raise CollectorError(f"unknown requested field codes: {', '.join(sorted(unknown))}")

    pending: list[Query] = []
    skipped: list[str] = []
    for query in queries:
        if requested_codes is not None and query.field_code not in requested_codes:
            continue
        if _existing_valid_export(output_root / query.field_code, query):
            skipped.append(query.field_code)
        else:
            pending.append(query)
    return pending, skipped


def build_search_url(
    query: Query, base_url: str = MATHSCINET_SEARCH_URL
) -> str:
    params = [
        ("query", query.mathscinet_query),
        ("page", "1"),
        ("size", str(MAX_CITATIONS_PER_FIELD)),
        ("sort", "citations"),
        ("order", "desc"),
        ("facets", ""),
    ]
    return f"{base_url}?{urlencode(params)}"


def extract_mathscinet_target(html: str) -> str:
    for block in re.findall(
        r'<div\s+class="[^"]*db-tit[^"]*"[^>]*>.*?</div>', html, re.S | re.I
    ):
        plain = re.sub(r"<[^>]+>", " ", block)
        if "MathSciNet" not in unescape(plain):
            continue
        match = re.search(r"popup_gourl\(\s*['\"]([^'\"]+)['\"]\s*\)", block)
        if match:
            return unescape(match.group(1))
    raise BrowserContractError("MathSciNet target is absent from the KUDOS database page")


def _proxy_url(target: str) -> str:
    return f"{KUDOS_PROXY_URL}?url={quote(target, safe='')}"


def _search_base_for_current_page(current_url: str) -> str:
    parsed = urlsplit(current_url)
    if not parsed.scheme or not parsed.netloc:
        raise BrowserContractError("MathSciNet did not provide a usable origin")
    return urlunsplit(
        (parsed.scheme, parsed.netloc, "/mathscinet/publications-search", "", "")
    )


def _parse_total_result_count(texts: Sequence[str]) -> int:
    counts: list[int] = []
    for text in texts:
        for value in re.findall(r"([0-9][0-9,]*)\s+results?\b", text, re.I):
            counts.append(int(value.replace(",", "")))
    if not counts:
        raise BrowserContractError("MathSciNet result count is not visible")
    return max(counts)


def _write_result_marker(directory: Path, data: dict[str, object]) -> None:
    atomic_store(
        directory / "result.json",
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _login_and_open_mathscinet(page, credentials: Credentials, timeout_ms: int) -> None:
    page.goto(KUDOS_LOGIN_URL, wait_until="domcontentloaded", timeout=timeout_ms)
    page.locator("#userid").fill(credentials.user_id)
    page.locator("#passwd").fill(credentials.password)
    page.locator("a.btn_login").click()
    page.wait_for_function(
        "() => !location.pathname.endsWith('/login.htm')",
        timeout=timeout_ms,
    )
    if page.locator("#userid").count() and page.locator("#userid").is_visible():
        raise BrowserContractError("KUDOS login did not complete")

    page.goto(KUDOS_DATABASES_URL, wait_until="domcontentloaded", timeout=timeout_ms)
    target = extract_mathscinet_target(page.content())
    page.goto(_proxy_url(target), wait_until="domcontentloaded", timeout=timeout_ms)
    page.locator('input[name="Search bar"]').wait_for(state="visible", timeout=timeout_ms)
    if "mathscinet" not in page.title().lower():
        raise BrowserContractError("MathSciNet page did not open through KUDOS")


def _collect_one(page, query: Query, output_root: Path, timeout_ms: int) -> None:
    directory = output_root / query.field_code
    directory.mkdir(parents=True, exist_ok=True)
    base_url = _search_base_for_current_page(page.url)
    page.goto(
        build_search_url(query, base_url),
        wait_until="domcontentloaded",
        timeout=timeout_ms,
    )
    page.wait_for_function(
        """() => {
          const resultCheckbox = document.querySelector(
            'input[name="Select article checkbox"]'
          );
          return Boolean(resultCheckbox) || document.body.innerText.includes(
            'No publications that meet this criteria'
          );
        }""",
        timeout=timeout_ms,
    )

    if page.get_by_text("No publications that meet this criteria", exact=False).count():
        _write_result_marker(
            directory,
            {
                "field_code": query.field_code,
                "query": query.mathscinet_query,
                "result_count": 0,
                "status": "no_results",
                "retrieved_at": _utc_now(),
            },
        )
        return

    total = _parse_total_result_count(
        page.locator(".search-results .total").all_inner_texts()
    )
    page.locator('button[name="Export button"]').click()

    subscription_warning = page.get_by_text(
        "You have to be a subscriber to access this feature.", exact=False
    )
    if subscription_warning.count() and subscription_warning.is_visible():
        raise BrowserContractError("MathSciNet subscription was not recognized")

    selectable = page.locator(
        'input[name="Select article checkbox"]:not([disabled])'
    ).count()
    if selectable == 0:
        raise BrowserContractError("search returned results but none can be exported")

    page.locator('div[title="Select all on page"]').wait_for(
        state="visible", timeout=timeout_ms
    )
    select_all = page.locator('input[name="Select all checkbox"]')
    checkbox_id = select_all.get_attribute("id")
    if not checkbox_id:
        raise BrowserContractError("select-all checkbox has no label target")
    page.locator(f'label[for="{checkbox_id}"]').evaluate("element => element.click()")
    page.wait_for_timeout(500)
    if not select_all.is_checked():
        raise BrowserContractError("select-all click did not select the result page")
    page.locator('select[name="Citation format select"]:visible').select_option(
        label="BibTeX"
    )
    page.locator('button[name="Get Citations button"]').click()
    textarea = page.locator("#citationText")
    textarea.wait_for(state="visible", timeout=timeout_ms)
    page.wait_for_function(
        "() => (document.querySelector('#citationText')?.value || '').trim().startsWith('@')",
        timeout=timeout_ms,
    )
    citation_text = textarea.input_value().replace("\r\n", "\n")
    if not citation_text.endswith("\n"):
        citation_text += "\n"

    validated = validate_bibtex(
        citation_text,
        expected_codes=query.expected_codes,
        expected_count=selectable,
    )
    atomic_store(directory / "mathscinet.bib", citation_text)
    _write_result_marker(
        directory,
        {
            "field_code": query.field_code,
            "query": query.mathscinet_query,
            "result_count": total,
            "selectable_records": selectable,
            "exported_records": validated.record_count,
            "requested_msc_matches": validated.matched_count,
            "sort": "citations_desc",
            "status": "collected",
            "retrieved_at": _utc_now(),
        },
    )


def _parse_requested_codes(value: str | None) -> set[str] | None:
    if value is None:
        return None
    codes = {item.strip() for item in value.split(",") if item.strip()}
    if not codes or any(not re.fullmatch(r"\d{2}", item) for item in codes):
        raise CollectorError("--codes must be a comma-separated list of two-digit fields")
    return codes


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Collect the first 100 citation-sorted MathSciNet records for pending "
            "B002 MSC fields through one KUDOS browser session."
        )
    )
    parser.add_argument("--codes", help="only these comma-separated field codes")
    parser.add_argument("--dry-run", action="store_true", help="print the plan only")
    parser.add_argument("--headed", action="store_true", help="show the Chrome window")
    parser.add_argument("--delay-seconds", type=float, default=4.0)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--query-table", type=Path, default=DEFAULT_QUERY_TABLE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    if args.delay_seconds < 0:
        raise CollectorError("--delay-seconds must be nonnegative")
    if args.timeout_seconds <= 0:
        raise CollectorError("--timeout-seconds must be positive")

    queries = load_queries(args.query_table.resolve())
    requested = _parse_requested_codes(args.codes)
    pending, skipped = plan_queries(queries, args.output_root.resolve(), requested)
    print(f"plan pending={len(pending)} skipped={len(skipped)}")
    if skipped:
        print("skip " + ",".join(skipped))
    if pending:
        print("pending " + ",".join(item.field_code for item in pending))
    if args.dry_run or not pending:
        return 0

    credentials = load_credentials(args.credentials.resolve())
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise CollectorError(
            "Playwright is not installed; install scripts/requirements-mathscinet.txt"
        ) from error

    timeout_ms = int(args.timeout_seconds * 1000)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=not args.headed,
        )
        context = browser.new_context(accept_downloads=False)
        page = context.new_page()
        page.set_default_timeout(timeout_ms)
        try:
            print("session opening KUDOS and MathSciNet")
            _login_and_open_mathscinet(page, credentials, timeout_ms)
            print("session ready")
            for index, query in enumerate(pending, 1):
                print(f"collect {query.field_code} ({index}/{len(pending)})")
                _collect_one(page, query, args.output_root.resolve(), timeout_ms)
                print(f"collected {query.field_code}")
                if index < len(pending) and args.delay_seconds:
                    time.sleep(args.delay_seconds)
        except Exception as error:
            detail = f": {error}" if isinstance(error, CollectorError) else ""
            print(
                f"stopped type={type(error).__name__}{detail}; "
                "completed fields remain reusable",
                file=sys.stderr,
            )
            return 2
        finally:
            context.close()
            browser.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CollectorError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
