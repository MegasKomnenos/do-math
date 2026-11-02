"""Structural checks for glossary snapshots, not mathematical certification.

Two snapshots share one entry format. A plan publishes the global glossary
(glossary.md, seven fields, term-N anchors). A research, exploration or peer
record publishes its local glossary (glossary-local.md, the same seven fields
plus Global candidate, local-N anchors), which may have no entries at all.
"""
from pathlib import Path
import re

FIELDS = ('Name and symbol', 'Kind', 'Definition', 'Well-definedness', 'Related expressions', 'Current formal correspondence', 'Provenance')
LOCAL_FIELDS = FIELDS + ('Global candidate',)
MARKER = '<!-- do-math-glossary -->'
LOCAL_MARKER = '<!-- do-math-local-glossary -->'
ENTRY = re.compile(r'^## (\d+)\. (.+)$', re.M)
ROW = re.compile(r'^\| ([^|]+?) \| (.*) \|$')


def _anchor_pattern(prefix):
    return re.compile(rf'<a id="{prefix}-(\d+)"></a>')


def _check_entries(source, name, marker, prefix, fields, allow_empty):
    """Marker, one anchor per numbered heading, and every field once in order."""
    errors = []
    anchor = _anchor_pattern(prefix)
    if marker not in source:
        errors.append(f'{name}: missing marker {marker}')
    entries = list(ENTRY.finditer(source))
    if not entries and not allow_empty:
        errors.append(f'{name}: expected numbered entries: ## 1. Name')
    ids = [m[1] for m in entries]
    anchors = anchor.findall(source)
    if len(set(ids)) != len(ids) or sorted(ids) != sorted(anchors):
        errors.append(f'{name}: each entry needs one unique matching {prefix}-N anchor')
    for i, match in enumerate(entries):
        if not source[:match.start()].rstrip().endswith(f'<a id="{prefix}-{match[1]}"></a>'):
            errors.append(f'{name} entry {match[1]}: matching anchor must immediately precede the heading')
        body = source[match.end():entries[i+1].start() if i+1 < len(entries) else len(source)]
        body = anchor.sub('', body)
        seen = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line in ('| Field | Content |', '|---|---|'):
                continue
            row = ROW.fullmatch(line)
            if row is None:
                errors.append(f'{name} entry {match[1]}: put current content in fields; move update history to glossary-history.md')
                continue
            field, value = row[1].strip(), row[2].strip()
            seen.append(field)
            if not value:
                errors.append(f'{name} entry {match[1]}: {field} must be explicit (use None/Not formalized where appropriate)')
        if tuple(seen) != fields:
            errors.append(f'{name} entry {match[1]}: expected each field once, in order: {", ".join(fields)}')
    for target in re.findall(rf'\]\(#{prefix}-(\d+)\)', source):
        if target not in ids:
            errors.append(f'{name}: missing local target {prefix}-{target}')
    return errors, ids


def check_glossary(output):
    """Validate the global glossary, history and research status of a newly submitted plan."""
    output = Path(output)
    errors = []
    for name in ('glossary.md', 'glossary-history.md', 'research-status.md'):
        path = output / name
        if not path.is_file() or not path.read_text(encoding='utf-8-sig').strip():
            errors.append(f'{name}: nonempty file required for a plan')
    if errors:
        return errors
    source = (output / 'glossary.md').read_text(encoding='utf-8-sig')
    if '(glossary-history.md' not in source:
        errors.append('glossary.md: link glossary-history.md in the introduction')
    found, ids = _check_entries(source, 'glossary.md', MARKER, 'term', FIELDS, allow_empty=False)
    errors += found
    # Family guides are optional. If linked, they must be published with this snapshot.
    for filename in set(re.findall(r'\]\((glossary-[A-Za-z0-9_-]+\.md)(?:#[^)]+)?\)', source)):
        if not (output / filename).is_file():
            errors.append(f'glossary.md: missing companion {filename}')
        elif filename != 'glossary-history.md':
            companion = (output / filename).read_text(encoding='utf-8-sig')
            for target in re.findall(r'\]\(glossary\.md#term-(\d+)\)', companion):
                if target not in ids:
                    errors.append(f'{filename}: missing glossary target term-{target}')
    return errors


def check_local_glossary(output):
    """Validate the local glossary of a research, exploration or peer output.

    A record with no internal terms still publishes the file with its marker
    and preamble; zero entries is valid. Collisions with global names and the
    merit of a global candidate are judged by reviews and plans, not here.
    """
    path = Path(output) / 'glossary-local.md'
    source = path.read_text(encoding='utf-8-sig') if path.is_file() else ''
    if not source.strip():
        return ['glossary-local.md: nonempty file required for research, explore and peer outputs']
    errors, _ = _check_entries(source, 'glossary-local.md', LOCAL_MARKER, 'local', LOCAL_FIELDS, allow_empty=True)
    return errors
