"""Preserving BibTeX and RIS parsers used by scholarly extraction."""


from __future__ import annotations


import hashlib
import re
from collections import defaultdict
from typing import NamedTuple


class BibTeXError(ValueError):
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


class _BibScanner:
    def __init__(self, text: str, source_name: str, *, allow_key_whitespace: bool = False,
                 allow_missing_key: bool = False) -> None:
        self.text = text
        self.source_name = source_name
        self.position = 0
        self.allow_key_whitespace = allow_key_whitespace
        self.allow_missing_key = allow_missing_key

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

        field_first = self.allow_missing_key and re.match(
            r'[A-Za-z][A-Za-z0-9_-]*\s*=\s*\{', self.text[self.position:])
        if field_first:
            key = ""
            warnings.append("citation_key_missing")
        else:
            key_start = self.position
            while self.position < len(self.text) and self.text[self.position] != ",":
                if self.text[self.position] == closing:
                    raise self.error("entry has no fields")
                self.position += 1
            if self.position >= len(self.text):
                raise self.error("unclosed entry header")
            key = self.text[key_start : self.position].strip()
            if not key:
                if not self.allow_missing_key:
                    raise self.error("invalid BibTeX key")
                warnings.append("citation_key_missing")
            if any(character.isspace() for character in key):
                if not self.allow_key_whitespace:
                    raise self.error("invalid BibTeX key")
                warnings.append("citation_key_contains_whitespace")
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


class B001CatalogError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_RIS_TAG = re.compile(r"^(?P<tag>[A-Z0-9]{2})  - ?(?P<value>.*)$")


def parse_ris(text: str, *, source_name: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    lines: list[str] = []
    fields: dict[str, list[str]] = defaultdict(list)
    last_tag: str | None = None

    def finish() -> None:
        nonlocal lines, fields, last_tag
        if not fields and not any(line.strip() for line in lines):
            lines = []
            last_tag = None
            return
        raw_text = "\n".join(lines).strip()
        records.append(
            {
                "fields": dict(fields),
                "raw_text": raw_text,
                "parsed_record_sha256": _sha256_bytes(raw_text.encode("utf-8")),
            }
        )
        lines = []
        fields = defaultdict(list)
        last_tag = None

    for line_number, raw_line in enumerate(text.lstrip("\ufeff").splitlines(), start=1):
        line = raw_line.rstrip("\r")
        lines.append(line)
        match = _RIS_TAG.match(line)
        if match:
            tag = match.group("tag").casefold()
            value = match.group("value")
            if tag == "er":
                finish()
                continue
            fields[tag].append(value)
            last_tag = tag
        elif line.strip():
            if last_tag is None or not fields[last_tag]:
                raise B001CatalogError(
                    f"{source_name}:{line_number}: continuation without a field"
                )
            fields[last_tag][-1] += "\n" + line
    if fields or any(line.strip() for line in lines):
        raise B001CatalogError(f"{source_name}: final RIS record lacks ER terminator")
    return records
