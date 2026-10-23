"""Structural checks for current glossary snapshots, not mathematical certification."""
from pathlib import Path
import re

FIELDS = ('이름·기호', '종류', '정의', '잘 정의됨', '관련 표현', '현재 형식 대응', '출처')
ENTRY = re.compile(r'^## (\d+)\. (.+)$', re.M)
ANCHOR = re.compile(r'<a id="term-(\d+)"></a>')
ROW = re.compile(r'^\| ([^|]+?) \| (.*) \|$')


def check_glossary(output):
    """Validate the single current format for a newly submitted plan."""
    output = Path(output)
    errors = []
    for name in ('glossary.md', 'glossary-history.md', 'research-status.md'):
        path = output / name
        if not path.is_file() or not path.read_text(encoding='utf-8-sig').strip():
            errors.append(f'{name}: nonempty file required for a plan')
    if errors:
        return errors
    source = (output / 'glossary.md').read_text(encoding='utf-8-sig')
    if '<!-- do-math-glossary -->' not in source:
        errors.append('glossary.md: missing current glossary marker')
    if '(glossary-history.md' not in source:
        errors.append('glossary.md: link glossary-history.md in the introduction')
    entries = list(ENTRY.finditer(source))
    if not entries:
        errors.append('glossary.md: expected numbered entries: ## 1. Name')
    ids = [m[1] for m in entries]
    anchors = ANCHOR.findall(source)
    if len(set(ids)) != len(ids) or sorted(ids) != sorted(anchors):
        errors.append('glossary.md: each entry needs one unique matching term-N anchor')
    for i, match in enumerate(entries):
        if not source[:match.start()].rstrip().endswith(f'<a id="term-{match[1]}"></a>'):
            errors.append(f'glossary.md entry {match[1]}: matching anchor must immediately precede the heading')
        body = source[match.end():entries[i+1].start() if i+1 < len(entries) else len(source)]
        body = ANCHOR.sub('', body)
        seen = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line in ('| 칸 | 내용 |', '|---|---|'):
                continue
            row = ROW.fullmatch(line)
            if row is None:
                errors.append(f'glossary.md entry {match[1]}: put current content in fields; move update history to glossary-history.md')
                continue
            field, value = row[1].strip(), row[2].strip()
            seen.append(field)
            if not value:
                errors.append(f'glossary.md entry {match[1]}: {field} must be explicit (use 없음/미형식화 where appropriate)')
        if tuple(seen) != FIELDS:
            errors.append(f'glossary.md entry {match[1]}: expected each field once, in order: {", ".join(FIELDS)}')
    for target in re.findall(r'\]\(#term-(\d+)\)', source):
        if target not in ids:
            errors.append(f'glossary.md: missing local target term-{target}')
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
