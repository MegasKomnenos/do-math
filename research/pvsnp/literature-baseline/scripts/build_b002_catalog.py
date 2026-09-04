#!/usr/bin/env python3
"""Build the deterministic B002 MathSciNet candidate and relation indexes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import NamedTuple, Sequence


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_BASELINE_ROOT = SCRIPT_PATH.parents[1]
SCHEMA_VERSION = "pvsnp-b002-normalized/1"
REQUIRED_FIELDS = ("title", "mrclass", "mrnumber")
PUBLICATION_FIELDS = (
    "journal",
    "fjournal",
    "booktitle",
    "series",
    "volume",
    "number",
    "publisher",
    "pages",
)


class BibTeXError(ValueError):
    pass


class CorpusError(RuntimeError):
    pass


class BibEntry(NamedTuple):
    entry_type: str
    key: str
    field_items: tuple[tuple[str, str], ...]
    raw_text: str
    parse_warnings: tuple[str, ...] = ()

    def field_values(self, name: str) -> tuple[str, ...]:
        name = name.lower()
        return tuple(value for field_name, value in self.field_items if field_name == name)


class Occurrence(NamedTuple):
    entry: BibEntry
    provenance: dict[str, object]


class Corpus(NamedTuple):
    occurrences: tuple[Occurrence, ...]
    artifacts: tuple[dict[str, object], ...]
    metadata_count: int
    source_manifest_sha256: str
    source_manifest: dict[str, object]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class _BibScanner:
    def __init__(self, text: str, source_name: str) -> None:
        self.text = text
        self.source_name = source_name
        self.position = 0

    def error(self, message: str) -> BibTeXError:
        line = self.text.count("\n", 0, self.position) + 1
        return BibTeXError(f"{self.source_name}:{line}: {message}")

    def skip_space_and_comments(self) -> None:
        while self.position < len(self.text):
            if self.text[self.position].isspace():
                self.position += 1
                continue
            if self.text[self.position] == "%":
                newline = self.text.find("\n", self.position)
                self.position = len(self.text) if newline < 0 else newline + 1
                continue
            break

    def read_name(self, label: str) -> str:
        start = self.position
        while self.position < len(self.text):
            character = self.text[self.position]
            if not (character.isalnum() or character in "_-"):
                break
            self.position += 1
        if self.position == start:
            raise self.error(f"expected {label}")
        return self.text[start : self.position]

    def expect(self, character: str) -> None:
        if self.position >= len(self.text) or self.text[self.position] != character:
            raise self.error(f"expected {character!r}")
        self.position += 1

    def read_braced_value(self) -> str:
        self.expect("{")
        start = self.position
        depth = 1
        while self.position < len(self.text):
            character = self.text[self.position]
            if character == "\\":
                self.position += 2
                continue
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    value = self.text[start : self.position]
                    self.position += 1
                    return value
            self.position += 1
        raise self.error("unclosed braced value")

    def read_quoted_value(self) -> str:
        self.expect('"')
        start = self.position
        brace_depth = 0
        while self.position < len(self.text):
            character = self.text[self.position]
            if character == "\\":
                self.position += 2
                continue
            if character == "{":
                brace_depth += 1
            elif character == "}":
                if brace_depth == 0:
                    raise self.error("unmatched brace in quoted value")
                brace_depth -= 1
            elif character == '"' and brace_depth == 0:
                value = self.text[start : self.position]
                self.position += 1
                return value
            self.position += 1
        raise self.error("unclosed quoted value")

    def read_bare_value(self, closing: str) -> str:
        start = self.position
        while self.position < len(self.text):
            character = self.text[self.position]
            if character in {",", closing} or character.isspace():
                break
            if character == "#":
                raise self.error("concatenated BibTeX values are unsupported")
            self.position += 1
        value = self.text[start : self.position]
        if not value:
            raise self.error("expected field value")
        return value

    def read_value(self, closing: str) -> str:
        if self.position >= len(self.text):
            raise self.error("expected field value")
        if self.text[self.position] == "{":
            return self.read_braced_value()
        if self.text[self.position] == '"':
            return self.read_quoted_value()
        return self.read_bare_value(closing)

    def read_entry(self) -> BibEntry:
        start = self.position
        warnings: list[str] = []
        self.expect("@")
        entry_type = self.read_name("entry type").lower()
        self.skip_space_and_comments()
        if self.position >= len(self.text) or self.text[self.position] not in "{(":
            raise self.error("expected entry opening delimiter")
        opening = self.text[self.position]
        closing = "}" if opening == "{" else ")"
        self.position += 1
        self.skip_space_and_comments()

        key_start = self.position
        while self.position < len(self.text) and self.text[self.position] != ",":
            if self.text[self.position] == closing:
                raise self.error("entry has no fields")
            self.position += 1
        if self.position >= len(self.text):
            raise self.error("unclosed entry header")
        key = self.text[key_start : self.position].strip()
        if not key or any(character.isspace() for character in key):
            raise self.error("invalid BibTeX key")
        self.position += 1

        field_items: list[tuple[str, str]] = []
        while True:
            self.skip_space_and_comments()
            if self.position >= len(self.text):
                raise self.error("unclosed entry")
            if self.text[self.position] == closing:
                self.position += 1
                break

            name = self.read_name("field name").lower()
            self.skip_space_and_comments()
            self.expect("=")
            self.skip_space_and_comments()
            value = self.read_value(closing)

            extra_start = self.position
            while self.position < len(self.text) and self.text[self.position] == "}":
                self.position += 1
            after_extra = self.position
            while after_extra < len(self.text) and self.text[after_extra].isspace():
                after_extra += 1
            if self.position > extra_start and (
                after_extra < len(self.text) and self.text[after_extra] == ","
            ):
                value += self.text[extra_start:after_extra]
                warnings.append(f"extra_closing_brace:{name}")
                self.position = after_extra
            else:
                self.position = extra_start
            field_items.append((name, value))

            self.skip_space_and_comments()
            if self.position >= len(self.text):
                raise self.error("unclosed entry")
            if self.text[self.position] == ",":
                self.position += 1
                continue
            if self.text[self.position] == closing:
                self.position += 1
                break
            raise self.error("expected comma or entry closing delimiter")

        return BibEntry(
            entry_type=entry_type,
            key=key,
            field_items=tuple(field_items),
            raw_text=self.text[start : self.position],
            parse_warnings=tuple(warnings),
        )


def parse_bibtex(text: str, *, source_name: str = "<bibtex>") -> list[BibEntry]:
    scanner = _BibScanner(text, source_name)
    entries: list[BibEntry] = []
    while True:
        scanner.skip_space_and_comments()
        if scanner.position == len(text):
            return entries
        if text[scanner.position] != "@":
            raise scanner.error("unexpected text outside an entry")
        entries.append(scanner.read_entry())


def validate_entry(entry: BibEntry, *, source_name: str) -> None:
    key_match = re.fullmatch(r"MR([1-9][0-9]*)", entry.key)
    if not key_match:
        raise CorpusError(f"{source_name}: invalid MR key {entry.key!r}")
    missing = [
        name
        for name in REQUIRED_FIELDS
        if not entry.field_values(name) or not entry.field_values(name)[0].strip()
    ]
    if missing:
        raise CorpusError(
            f"{source_name}:{entry.key}: missing required fields: {', '.join(missing)}"
        )
    duplicated_required = [
        name for name in REQUIRED_FIELDS if len(entry.field_values(name)) != 1
    ]
    if duplicated_required:
        raise CorpusError(
            f"{source_name}:{entry.key}: required fields must occur once: "
            + ", ".join(duplicated_required)
        )
    mr_number = entry.field_values("mrnumber")[0].strip()
    if not re.fullmatch(r"[1-9][0-9]*", mr_number):
        raise CorpusError(f"{source_name}:{entry.key}: invalid MRNUMBER {mr_number!r}")
    if int(key_match.group(1)) != int(mr_number):
        raise CorpusError(
            f"{source_name}:{entry.key}: MR key and MRNUMBER disagree"
        )


def _derive_year(entry: BibEntry) -> tuple[int | None, str | None]:
    raw_values = entry.field_values("year")
    if not raw_values or not any(value.strip() for value in raw_values):
        return None, "missing_year"
    year_values = {
        year
        for raw in raw_values
        for year in re.findall(r"(?<![0-9])([0-9]{4})(?![0-9])", raw)
    }
    if len(year_values) != 1:
        return None, "ambiguous_year"
    year = int(next(iter(year_values)))
    if len(raw_values) != 1 or not re.fullmatch(r"[0-9]{4}", raw_values[0].strip()):
        return year, "noncanonical_year"
    return year, None


_ACCENT_MARKS = {
    '"': "\u0308",
    "'": "\u0301",
    "`": "\u0300",
    "^": "\u0302",
    "~": "\u0303",
    "=": "\u0304",
    ".": "\u0307",
    "u": "\u0306",
    "v": "\u030c",
    "H": "\u030b",
    "c": "\u0327",
    "k": "\u0328",
    "b": "\u0331",
    "d": "\u0323",
    "r": "\u030a",
}
_SPECIAL_TEX = {
    "aa": "å",
    "AA": "Å",
    "ae": "æ",
    "AE": "Æ",
    "l": "ł",
    "L": "Ł",
    "o": "ø",
    "O": "Ø",
    "oe": "œ",
    "OE": "Œ",
    "ss": "ß",
}
_FORMATTING_COMMANDS = {
    "Bbb",
    "bf",
    "boldsymbol",
    "cal",
    "em",
    "emph",
    "hbox",
    "it",
    "mathbb",
    "mathbf",
    "mathcal",
    "mathfrak",
    "mathit",
    "mathrm",
    "mathsf",
    "mathtt",
    "rm",
    "text",
    "textbf",
    "textit",
    "textrm",
    "textsf",
    "texttt",
}
_LITERAL_COMMANDS = {
    "alpha",
    "beta",
    "chi",
    "delta",
    "epsilon",
    "eta",
    "gamma",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "omega",
    "phi",
    "pi",
    "psi",
    "rho",
    "sigma",
    "tau",
    "theta",
    "upsilon",
    "xi",
    "zeta",
    "Gamma",
    "Delta",
    "Lambda",
    "Omega",
    "Phi",
    "Pi",
    "Psi",
    "Sigma",
    "Theta",
    "Upsilon",
    "Xi",
    "LaTeX",
    "TeX",
}


def _tex_projection(value: str) -> tuple[str, set[str]]:
    unknown: set[str] = set()

    def replace_accent(match: re.Match[str]) -> str:
        return unicodedata.normalize(
            "NFC", match.group(2) + _ACCENT_MARKS[match.group(1)]
        )

    symbolic_accent = re.compile(
        r"\\([\"'`^~=\.])\s*\{?\s*([A-Za-z])\s*\}?"
    )
    word_accent = re.compile(
        r"\\(u|v|H|c|k|b|d|r)(?![A-Za-z])\s*\{?\s*([A-Za-z])\s*\}?"
    )
    value = symbolic_accent.sub(replace_accent, value)
    value = word_accent.sub(replace_accent, value)

    def replace_command(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in _SPECIAL_TEX:
            return _SPECIAL_TEX[name]
        if name in _FORMATTING_COMMANDS:
            return ""
        if name in _LITERAL_COMMANDS:
            return f" {name.casefold()} "
        unknown.add(name)
        return f" {name} "

    value = re.sub(r"\\([A-Za-z]+)\b", replace_command, value)
    value = re.sub(r"\\([&%#$##_{}])", r"\1", value)
    value = value.replace("\\~", " ").replace("~", " ")
    value = value.replace("\\\\", " ")
    value = value.replace("{", "").replace("}", "").replace("$", "")
    return unicodedata.normalize("NFKC", value), unknown


def normalize_text(value: str) -> tuple[str, set[str]]:
    projected, unknown = _tex_projection(value)
    characters = [
        character.casefold() if character.isalnum() else " "
        for character in projected
    ]
    return " ".join("".join(characters).split()), unknown


def _split_people(value: str) -> list[str]:
    people: list[str] = []
    start = 0
    depth = 0
    index = 0
    while index < len(value):
        character = value[index]
        if character == "\\":
            index += 2
            continue
        if character == "{":
            depth += 1
            index += 1
            continue
        if character == "}":
            depth = max(0, depth - 1)
            index += 1
            continue
        if depth == 0:
            match = re.match(r"\s+and\s+", value[index:], re.IGNORECASE)
            if match:
                people.append(value[start:index].strip())
                index += match.end()
                start = index
                continue
        index += 1
    people.append(value[start:].strip())
    return [person for person in people if person]


def normalize_doi(value: str) -> list[str]:
    dois: list[str] = []
    for item in (value,):
        item = item.strip()
        item = re.sub(r"^doi\s*:\s*", "", item, flags=re.IGNORECASE)
        item = re.sub(
            r"^https?://(?:dx\.)?doi\.org/", "", item, flags=re.IGNORECASE
        )
        item = item.replace(r"\_", "_")
        item = item.strip().rstrip(".,").casefold()
        if item and item not in dois:
            dois.append(item)
    return dois


def _normalize_isbns(value: str) -> list[str]:
    isbns: list[str] = []
    for item in value.split(";"):
        normalized = re.sub(r"[^0-9Xx]", "", item).upper()
        if normalized and normalized not in isbns:
            isbns.append(normalized)
    return isbns


def normalize_entry(entry: BibEntry) -> dict[str, object]:
    unknown: set[str] = set()
    normalization_warnings: list[str] = []
    title, title_unknown = normalize_text(entry.field_values("title")[0])
    unknown.update(title_unknown)

    creator_role: str | None = None
    creator_values: tuple[str, ...] = ()
    author_values = tuple(value for value in entry.field_values("author") if value.strip())
    editor_values = tuple(value for value in entry.field_values("editor") if value.strip())
    if author_values:
        creator_role = "author"
        creator_values = author_values
    elif editor_values:
        creator_role = "editor"
        creator_values = editor_values

    creators: list[str] = []
    if creator_role:
        for creator_value in creator_values:
            for person in _split_people(creator_value):
                normalized, person_unknown = normalize_text(person)
                unknown.update(person_unknown)
                if normalized:
                    creators.append(normalized)

    editions: list[str] = []
    for edition_value in entry.field_values("edition"):
        if not edition_value.strip():
            continue
        edition, edition_unknown = normalize_text(edition_value)
        unknown.update(edition_unknown)
        editions.append(edition)

    publication: dict[str, object] = {"entry_type": entry.entry_type}
    for name in PUBLICATION_FIELDS:
        normalized_values: list[str] = []
        for field_value in entry.field_values(name):
            if not field_value.strip():
                continue
            normalized, field_unknown = normalize_text(field_value)
            unknown.update(field_unknown)
            normalized_values.append(normalized)
        if normalized_values:
            publication[name] = normalized_values

    dois: list[str] = []
    for doi_value in entry.field_values("doi"):
        for doi in normalize_doi(doi_value):
            if doi not in dois:
                dois.append(doi)
    isbns: list[str] = []
    for isbn_value in entry.field_values("isbn"):
        for isbn in _normalize_isbns(isbn_value):
            if isbn not in isbns:
                isbns.append(isbn)

    year, year_warning = _derive_year(entry)
    if year_warning:
        normalization_warnings.append(year_warning)

    return {
        "title": title,
        "creator_role": creator_role,
        "creators": creators,
        "year": year,
        "dois": dois,
        "isbns": isbns,
        "edition": editions,
        "publication": publication,
        "normalization_warnings": normalization_warnings,
        "unrecognized_tex_commands": sorted(unknown, key=str.casefold),
    }


def _safe_relative_path(root: Path, value: str) -> Path:
    if not value or "\\" in value:
        raise CorpusError(f"invalid POSIX relative path in manifest: {value!r}")
    pure_parts = Path(value.replace("/", os.sep)).parts
    if Path(value).is_absolute() or ".." in pure_parts:
        raise CorpusError(f"unsafe relative path in manifest: {value!r}")
    root = root.resolve()
    resolved = (root / Path(*pure_parts)).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise CorpusError(f"manifest path escapes baseline root: {value!r}") from error
    return resolved


def _load_query_table(path: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
    except OSError as error:
        raise CorpusError(f"cannot read query table: {path}") from error
    by_code: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, 2):
        code = (row.get("field_code") or "").strip()
        name = (row.get("field_name") or "").strip()
        query = (row.get("query") or "").strip()
        if not re.fullmatch(r"[0-9]{2}", code) or not name or not query:
            raise CorpusError(f"invalid query-table row {row_number}")
        if code in by_code:
            raise CorpusError(f"duplicate query-table field code: {code}")
        by_code[code] = {"field_code": code, "field_name": name, "query": query}
    if not rows:
        raise CorpusError("query table is empty")
    return rows, by_code


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise CorpusError(f"cannot read {label}: {path}") from error
    if not isinstance(value, dict):
        raise CorpusError(f"{label} must be a JSON object: {path}")
    return value


def _expected_msc_codes(raw_query: str) -> tuple[str, ...]:
    return tuple(
        item.strip()
        for item in re.split(r"\s+OR\s+", raw_query, flags=re.IGNORECASE)
        if item.strip()
    )


def _classification_counts(
    entries: Sequence[BibEntry], field_code: str, expected_codes: Sequence[str]
) -> tuple[int, int]:
    exact = 0
    family = 0
    family_pattern = re.compile(rf"(?<![0-9]){re.escape(field_code)}(?:-|[A-Z])")
    for entry in entries:
        value = entry.field_values("mrclass")[0]
        if any(code in value for code in expected_codes):
            exact += 1
        if family_pattern.search(value):
            family += 1
    return exact, family


def load_corpus(baseline_root: Path, manifest_path: Path) -> Corpus:
    baseline_root = baseline_root.resolve()
    manifest_path = manifest_path.resolve()
    manifest_bytes = manifest_path.read_bytes()
    manifest = _read_json(manifest_path, "B002 manifest")
    if manifest.get("batch_id") != "B002" or manifest.get("source_id") != "mathscinet":
        raise CorpusError("manifest is not the B002 MathSciNet manifest")
    artifacts_value = manifest.get("artifacts")
    if not isinstance(artifacts_value, list) or not artifacts_value:
        raise CorpusError("manifest has no artifacts")

    query_path = _safe_relative_path(baseline_root, str(manifest.get("query_table", "")))
    if _sha256_file(query_path) != manifest.get("query_table_sha256"):
        raise CorpusError("query-table SHA-256 does not match the manifest")
    rows, queries = _load_query_table(query_path)

    collector_path = _safe_relative_path(baseline_root, str(manifest.get("collector", "")))
    if _sha256_file(collector_path) != manifest.get("collector_sha256"):
        raise CorpusError("collector SHA-256 does not match the manifest")

    artifacts: list[dict[str, object]] = []
    occurrences: list[Occurrence] = []
    metadata_count = 0
    expected_files: set[Path] = set()
    seen_fields: set[str] = set()

    for artifact_value in artifacts_value:
        if not isinstance(artifact_value, dict):
            raise CorpusError("manifest artifact is not an object")
        artifact = artifact_value
        field_code = str(artifact.get("field_code", ""))
        if field_code in seen_fields or field_code not in queries:
            raise CorpusError(f"unexpected or duplicate manifest field: {field_code!r}")
        seen_fields.add(field_code)
        query_row = queries[field_code]
        expected_query = f"pcsc:({query_row['query']})"
        if artifact.get("field_name") != query_row["field_name"]:
            raise CorpusError(f"field-name mismatch for {field_code}")
        if artifact.get("query") != expected_query:
            raise CorpusError(f"query mismatch for {field_code}")

        relative_path = str(artifact.get("path", ""))
        path = _safe_relative_path(baseline_root, relative_path)
        expected_files.add(path)
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise CorpusError(f"cannot read artifact for field {field_code}: {path}") from error
        if len(raw) != artifact.get("bytes"):
            raise CorpusError(f"byte-count mismatch for field {field_code}")
        if _sha256_bytes(raw) != artifact.get("sha256"):
            raise CorpusError(f"SHA-256 mismatch for field {field_code}")
        try:
            text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeError as error:
            raise CorpusError(f"artifact is not UTF-8 for field {field_code}") from error
        entries = parse_bibtex(text, source_name=relative_path)
        if len(entries) != artifact.get("record_count"):
            raise CorpusError(f"record-count mismatch for field {field_code}")
        keys = [entry.key for entry in entries]
        if len(keys) != len(set(keys)):
            raise CorpusError(f"duplicate MR key inside field {field_code}")
        for entry in entries:
            validate_entry(entry, source_name=relative_path)

        expected_codes = _expected_msc_codes(query_row["query"])
        exact_matches, family_matches = _classification_counts(
            entries, field_code, expected_codes
        )
        if exact_matches != artifact.get("requested_msc_matches"):
            raise CorpusError(f"requested MSC match count mismatch for field {field_code}")
        if family_matches != artifact.get("field_family_matches"):
            raise CorpusError(f"MSC family match count mismatch for field {field_code}")

        retrieved_at: str | None = None
        method = str(artifact.get("collection_method", ""))
        result_path = path.parent / "result.json"
        if method == "playwright":
            expected_files.add(result_path)
            result = _read_json(result_path, f"field {field_code} metadata")
            metadata_count += 1
            checks = {
                "field_code": field_code,
                "query": expected_query,
                "exported_records": artifact.get("record_count"),
                "result_count": artifact.get("total_results"),
                "requested_msc_matches": artifact.get("requested_msc_matches"),
                "selectable_records": artifact.get("record_count"),
                "sort": "citations_desc",
                "status": "collected",
            }
            for name, expected in checks.items():
                if result.get(name) != expected:
                    raise CorpusError(
                        f"metadata mismatch for field {field_code}: {name}"
                    )
            retrieved_value = result.get("retrieved_at")
            if not isinstance(retrieved_value, str) or not retrieved_value.endswith("Z"):
                raise CorpusError(f"invalid retrieval time for field {field_code}")
            retrieved_at = retrieved_value
        elif result_path.exists():
            raise CorpusError(f"unexpected metadata file for manual field {field_code}")

        artifact_summary = {
            "field_code": field_code,
            "path": relative_path,
            "bytes": len(raw),
            "sha256": _sha256_bytes(raw),
            "record_count": len(entries),
            "requested_msc_matches": exact_matches,
            "field_family_matches": family_matches,
        }
        artifacts.append(artifact_summary)
        for rank, entry in enumerate(entries, 1):
            provenance: dict[str, object] = {
                "source_id": "mathscinet",
                "batch_id": "B002",
                "field_code": field_code,
                "field_name": query_row["field_name"],
                "query": expected_query,
                "rank": rank,
                "path": relative_path,
                "artifact_sha256": artifact["sha256"],
                "entry_sha256": _sha256_bytes(entry.raw_text.encode("utf-8")),
                "collection_method": method,
                "retrieved_at": retrieved_at,
                "search_result_count": artifact.get("total_results"),
            }
            occurrences.append(Occurrence(entry=entry, provenance=provenance))

    if seen_fields != set(queries) or len(rows) != len(seen_fields):
        raise CorpusError("query table and manifest field sets differ")

    intake_root = baseline_root / "intake" / "B002" / "mathscinet"
    actual_files = {path.resolve() for path in intake_root.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        extra = sorted(str(path) for path in actual_files - expected_files)
        missing = sorted(str(path) for path in expected_files - actual_files)
        raise CorpusError(
            f"intake file set differs from manifest; extra={extra}, missing={missing}"
        )

    return Corpus(
        occurrences=tuple(occurrences),
        artifacts=tuple(artifacts),
        metadata_count=metadata_count,
        source_manifest_sha256=_sha256_bytes(manifest_bytes),
        source_manifest=manifest,
    )


def _mr_sort_key(value: str) -> int:
    return int(value[2:])


def aggregate_candidates(occurrences: Sequence[Occurrence]) -> list[dict[str, object]]:
    grouped: dict[str, list[Occurrence]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[occurrence.entry.key].append(occurrence)

    candidates: list[dict[str, object]] = []
    for key in sorted(grouped, key=_mr_sort_key):
        group = grouped[key]
        first = group[0].entry
        payload = (first.entry_type, first.field_items)
        for occurrence in group[1:]:
            candidate_payload = (
                occurrence.entry.entry_type,
                occurrence.entry.field_items,
            )
            if candidate_payload != payload:
                raise CorpusError(f"conflicting bibliographic payload for {key}")
        provenance = sorted(
            (dict(occurrence.provenance) for occurrence in group),
            key=lambda item: (
                int(str(item["field_code"])),
                int(item["rank"]),
                str(item["path"]),
            ),
        )
        raw_hashes = sorted(
            {_sha256_bytes(occurrence.entry.raw_text.encode("utf-8")) for occurrence in group}
        )
        parse_warnings = sorted(
            {
                warning
                for occurrence in group
                for warning in occurrence.entry.parse_warnings
            }
        )
        candidates.append(
            {
                "schema_version": "pvsnp-literature-candidate/1",
                "candidate_id": key,
                "entry_type": first.entry_type,
                "fields": [
                    {"name": name, "value": value}
                    for name, value in first.field_items
                ],
                "field_order": [name for name, _ in first.field_items],
                "duplicate_fields": {
                    name: count
                    for name, count in sorted(Counter(
                        name for name, _ in first.field_items
                    ).items())
                    if count > 1
                },
                "raw_entry_sha256s": raw_hashes,
                "parse_warnings": parse_warnings,
                "normalized": normalize_entry(first),
                "provenance": provenance,
            }
        )
    return candidates


def _relation_id(relation_type: str, signal: dict[str, object]) -> str:
    encoded = json.dumps(
        {"relation_type": relation_type, "signal": signal},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "B002-REL-" + hashlib.sha256(encoded).hexdigest()[:20]


def build_relation_groups(candidates: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    by_doi: dict[str, set[str]] = defaultdict(set)
    by_fingerprint: dict[tuple[object, ...], set[str]] = defaultdict(set)
    by_work_signal: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)

    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        normalized = candidate["normalized"]
        assert isinstance(normalized, dict)
        for doi in normalized["dois"]:
            by_doi[str(doi)].add(candidate_id)
        creator_key = (
            normalized["title"],
            normalized["creator_role"],
            tuple(normalized["creators"]),
        )
        if (
            normalized["title"]
            and normalized["creator_role"]
            and normalized["creators"]
            and normalized["year"] is not None
        ):
            by_fingerprint[creator_key + (normalized["year"],)].add(candidate_id)
            by_work_signal[creator_key].append(candidate)

    relations: list[dict[str, object]] = []

    def add_relation(
        relation_type: str,
        signal: dict[str, object],
        members: Sequence[str],
        member_metadata: list[dict[str, object]] | None = None,
    ) -> None:
        ordered_members = sorted(set(members), key=_mr_sort_key)
        if len(ordered_members) < 2:
            return
        record: dict[str, object] = {
            "schema_version": "pvsnp-literature-relation-candidate/1",
            "relation_id": _relation_id(relation_type, signal),
            "relation_type": relation_type,
            "status": "unverified_candidate",
            "signal": signal,
            "members": ordered_members,
        }
        if member_metadata is not None:
            record["member_metadata"] = sorted(
                member_metadata, key=lambda item: _mr_sort_key(str(item["candidate_id"]))
            )
        relations.append(record)

    for doi, members in by_doi.items():
        add_relation("same_doi_candidate", {"doi": doi}, list(members))

    for key, members in by_fingerprint.items():
        title, role, creators, year = key
        add_relation(
            "same_bibliographic_fingerprint_candidate",
            {
                "title": title,
                "creator_role": role,
                "creators": list(creators),
                "year": year,
            },
            list(members),
        )

    for key, group in by_work_signal.items():
        if len(group) < 2:
            continue
        signatures = set()
        member_metadata: list[dict[str, object]] = []
        for candidate in group:
            normalized = candidate["normalized"]
            assert isinstance(normalized, dict)
            publication = normalized["publication"]
            signature = (
                normalized["year"],
                tuple(normalized["edition"]),
                json.dumps(publication, ensure_ascii=False, sort_keys=True),
            )
            signatures.add(signature)
            member_metadata.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "year": normalized["year"],
                    "edition": normalized["edition"],
                    "publication": publication,
                }
            )
        if len(signatures) < 2:
            continue
        title, role, creators = key
        add_relation(
            "edition_or_version_candidate",
            {
                "title": title,
                "creator_role": role,
                "creators": list(creators),
            },
            [str(candidate["candidate_id"]) for candidate in group],
            member_metadata,
        )

    return sorted(
        relations,
        key=lambda item: (
            str(item["relation_type"]),
            json.dumps(item["signal"], ensure_ascii=False, sort_keys=True),
        ),
    )


def _jsonl_bytes(records: Sequence[dict[str, object]]) -> bytes:
    lines = [
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        for record in records
    ]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _relative_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _field_statistics(
    corpus: Corpus, candidates: Sequence[dict[str, object]]
) -> list[dict[str, object]]:
    occurrence_by_field: dict[str, list[Occurrence]] = defaultdict(list)
    candidate_field_count: dict[str, int] = {}
    for candidate in candidates:
        provenance = candidate["provenance"]
        assert isinstance(provenance, list)
        candidate_field_count[str(candidate["candidate_id"])] = len(provenance)
    for occurrence in corpus.occurrences:
        occurrence_by_field[str(occurrence.provenance["field_code"])].append(occurrence)

    statistics: list[dict[str, object]] = []
    for artifact in corpus.source_manifest["artifacts"]:
        code = str(artifact["field_code"])
        occurrences = occurrence_by_field[code]
        entry_types = Counter(item.entry.entry_type for item in occurrences)
        cross_field = sum(
            1 for item in occurrences if candidate_field_count[item.entry.key] > 1
        )
        missing_creators = 0
        missing_year = 0
        noncanonical_year = 0
        parse_recoveries = 0
        duplicate_fields = 0
        with_doi = 0
        for item in occurrences:
            normalized = normalize_entry(item.entry)
            if not normalized["creators"]:
                missing_creators += 1
            if normalized["dois"]:
                with_doi += 1
            warnings = normalized["normalization_warnings"]
            if "missing_year" in warnings:
                missing_year += 1
            if "noncanonical_year" in warnings:
                noncanonical_year += 1
            if item.entry.parse_warnings:
                parse_recoveries += 1
            counts = Counter(name for name, _ in item.entry.field_items)
            duplicate_fields += sum(count - 1 for count in counts.values() if count > 1)
        statistics.append(
            {
                "field_code": code,
                "field_name": artifact["field_name"],
                "occurrence_count": len(occurrences),
                "unique_mr_count": len({item.entry.key for item in occurrences}),
                "cross_field_candidate_count": cross_field,
                "with_doi_count": with_doi,
                "missing_creator_count": missing_creators,
                "missing_year_count": missing_year,
                "noncanonical_year_count": noncanonical_year,
                "parse_recovery_count": parse_recoveries,
                "duplicate_field_extra_count": duplicate_fields,
                "entry_types": dict(sorted(entry_types.items())),
                "total_results": artifact["total_results"],
                "top_100_truncated": artifact["total_results"] > artifact["record_count"],
                "requested_msc_matches": artifact["requested_msc_matches"],
                "field_family_matches": artifact["field_family_matches"],
            }
        )
    return statistics


def build_outputs(
    baseline_root: Path,
    manifest_path: Path,
    candidates_path: Path,
    relations_path: Path,
    output_manifest_path: Path,
) -> dict[str, object]:
    corpus = load_corpus(baseline_root, manifest_path)
    candidates = aggregate_candidates(corpus.occurrences)
    relations = build_relation_groups(candidates)
    candidate_bytes = _jsonl_bytes(candidates)
    relation_bytes = _jsonl_bytes(relations)

    _atomic_write(candidates_path, candidate_bytes)
    _atomic_write(relations_path, relation_bytes)

    repeated_groups = sum(1 for item in candidates if len(item["provenance"]) > 1)
    repeated_occurrences = sum(
        len(item["provenance"]) - 1 for item in candidates
    )
    relation_counts = Counter(str(item["relation_type"]) for item in relations)
    entry_types = Counter(str(item["entry_type"]) for item in candidates)
    unknown_commands = Counter()
    candidates_with_unknown = 0
    parse_warnings = Counter()
    candidates_with_parse_warnings = 0
    duplicate_fields = Counter()
    candidates_with_duplicate_fields = 0
    normalization_warnings = Counter()
    candidates_with_normalization_warnings = 0
    missing_creators = 0
    candidates_with_doi = 0
    for candidate in candidates:
        normalized = candidate["normalized"]
        assert isinstance(normalized, dict)
        commands = normalized["unrecognized_tex_commands"]
        if commands:
            candidates_with_unknown += 1
            unknown_commands.update(str(command) for command in commands)
        candidate_parse_warnings = candidate["parse_warnings"]
        if candidate_parse_warnings:
            candidates_with_parse_warnings += 1
            parse_warnings.update(str(warning) for warning in candidate_parse_warnings)
        candidate_duplicate_fields = candidate["duplicate_fields"]
        if candidate_duplicate_fields:
            candidates_with_duplicate_fields += 1
            duplicate_fields.update(
                {
                    str(name): int(count) - 1
                    for name, count in candidate_duplicate_fields.items()
                }
            )
        candidate_normalization_warnings = normalized["normalization_warnings"]
        if candidate_normalization_warnings:
            candidates_with_normalization_warnings += 1
            normalization_warnings.update(
                str(warning) for warning in candidate_normalization_warnings
            )
        if not normalized["creators"]:
            missing_creators += 1
        if normalized["dois"]:
            candidates_with_doi += 1

    manifest: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "batch_id": "B002",
        "source_id": "mathscinet",
        "normalizer": _relative_posix(SCRIPT_PATH, baseline_root),
        "normalizer_sha256": _sha256_file(SCRIPT_PATH),
        "source_manifest": _relative_posix(manifest_path, baseline_root),
        "source_manifest_sha256": corpus.source_manifest_sha256,
        "source_generated_at": corpus.source_manifest.get("generated_at"),
        "inputs": {
            "artifact_count": len(corpus.artifacts),
            "metadata_count": corpus.metadata_count,
            "occurrence_count": len(corpus.occurrences),
            "artifacts": list(corpus.artifacts),
        },
        "outputs": [
            {
                "path": _relative_posix(candidates_path, baseline_root),
                "bytes": len(candidate_bytes),
                "sha256": _sha256_bytes(candidate_bytes),
                "record_count": len(candidates),
            },
            {
                "path": _relative_posix(relations_path, baseline_root),
                "bytes": len(relation_bytes),
                "sha256": _sha256_bytes(relation_bytes),
                "record_count": len(relations),
            },
        ],
        "counts": {
            "candidate_count": len(candidates),
            "repeated_mr_group_count": repeated_groups,
            "repeated_occurrence_count": repeated_occurrences,
            "entry_types": dict(sorted(entry_types.items())),
            "candidates_with_doi": candidates_with_doi,
            "candidates_missing_creator": missing_creators,
            "relation_groups": dict(sorted(relation_counts.items())),
        },
        "exceptions": {
            "parse_errors": 0,
            "manifest_mismatches": 0,
            "metadata_mismatches": 0,
            "mr_identity_conflicts": 0,
            "candidates_with_parse_warnings": candidates_with_parse_warnings,
            "parse_warnings": dict(sorted(parse_warnings.items())),
            "candidates_with_duplicate_fields": candidates_with_duplicate_fields,
            "duplicate_field_extra_occurrences": dict(sorted(duplicate_fields.items())),
            "candidates_with_normalization_warnings": candidates_with_normalization_warnings,
            "normalization_warnings": dict(sorted(normalization_warnings.items())),
            "candidates_with_unrecognized_tex_commands": candidates_with_unknown,
            "unrecognized_tex_commands": dict(sorted(unknown_commands.items())),
        },
        "field_statistics": _field_statistics(corpus, candidates),
    }
    manifest_bytes = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    _atomic_write(output_manifest_path, manifest_bytes)
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse and normalize every B002 MathSciNet BibTeX occurrence."
    )
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_BASELINE_ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--candidates", type=Path)
    parser.add_argument("--relations", type=Path)
    parser.add_argument("--output-manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    root = args.baseline_root.resolve()
    manifest = (args.manifest or root / "manifests" / "B002.json").resolve()
    candidates = (
        args.candidates or root / "catalog" / "B002-candidates.jsonl"
    ).resolve()
    relations = (
        args.relations or root / "catalog" / "B002-relations.jsonl"
    ).resolve()
    output_manifest = (
        args.output_manifest or root / "manifests" / "B002-normalized.json"
    ).resolve()
    result = build_outputs(root, manifest, candidates, relations, output_manifest)
    counts = result["counts"]
    print(
        "built "
        f"occurrences={result['inputs']['occurrence_count']} "
        f"candidates={counts['candidate_count']} "
        f"relations={sum(counts['relation_groups'].values())}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BibTeXError, CorpusError, OSError) as error:
        print(f"error: {error}", file=os.sys.stderr)
        raise SystemExit(2)
