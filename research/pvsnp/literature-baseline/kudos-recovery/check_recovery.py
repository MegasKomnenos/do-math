"""Validate worker result bindings, evidence and acquired artifacts."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

STATES = {'found', 'not_found', 'unavailable', 'unresolved'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def artifact_errors(artifact, root, component):
    errors = []
    if not isinstance(artifact, dict):
        return [component + ': artifact must be an object']
    if not all(isinstance(artifact.get(k), str) and artifact[k].strip() for k in ['path', 'sha256', 'url']):
        return [component + ': path, sha256 and url required']
    path = (root / artifact['path']).resolve()
    if not path.is_relative_to(root):
        return [component + ': artifact outside baseline']
    try:
        data = path.read_bytes()
        if not data:
            errors.append(component + ': empty artifact')
        if hashlib.sha256(data).hexdigest() != artifact['sha256']:
            errors.append(component + ': hash mismatch')
        if artifact.get('media_type') == 'application/pdf' or (component == 'fulltext' and path.suffix.lower() == '.pdf'):
            if not data.startswith(b'%PDF-'):
                errors.append(component + ': not a PDF')
            else:
                import pymupdf
                try:
                    with pymupdf.open(path) as doc:
                        if len(doc) == 0:
                            errors.append(component + ': PDF has no pages')
                except Exception:
                    errors.append(component + ': PDF cannot be opened')
        if component == 'abstract':
            value = data.decode('utf-8-sig').strip().strip(' [].').casefold()
            if value in {'no abstract available', 'abstract', 'n/a', 'no abstract', ''}:
                errors.append('abstract: placeholder or empty text')
    except (OSError, UnicodeError):
        errors.append(component + ': artifact unreadable')
    return errors


def validate_record(record, paper, root):
    root = Path(root).resolve()
    errors = []
    if not isinstance(record, dict):
        return ['result must be an object']
    if record.get('schema_version') != 'kudos-recovery-result/1':
        errors.append('schema_version mismatch')
    for key in ['paper_id', 'version_sha256']:
        if record.get(key) != paper.get(key):
            errors.append(key + ': input binding mismatch')
    identity = record.get('identity', {})
    if identity.get('status') not in {'confirmed', 'not_found', 'unresolved'} or not identity.get('reason'):
        errors.append('identity: status and reason required')
    attempts = record.get('attempts', [])
    if not attempts or not any(a.get('method') == 'playwright' and all(a.get(k) for k in ['query', 'url', 'outcome']) for a in attempts):
        errors.append('attempts: actual Playwright query and outcome required')
    evidence = record.get('evidence', [])
    if not evidence:
        errors.append('evidence: at least one local capture required')
    for artifact in evidence:
        errors += artifact_errors(artifact, root, 'evidence')
    for component in ['abstract', 'fulltext']:
        asset = record.get(component, {})
        status = asset.get('status')
        if status not in STATES:
            errors.append(component + ': unknown status')
        elif status == 'found':
            if identity.get('status') != 'confirmed':
                errors.append(component + ': identity must be confirmed')
            if not asset.get('artifacts'):
                errors.append(component + ': found requires artifacts')
            for artifact in asset.get('artifacts', []):
                if not artifact.get('media_type'):
                    errors.append(component + ': media_type required')
                errors += artifact_errors(artifact, root, component)
        elif not asset.get('reason'):
            errors.append(component + ': non-found state requires reason')
    return errors


def check_assignment(assignment_path, partial=False):
    assignment_path = Path(assignment_path).resolve()
    assignment = json.loads(assignment_path.read_text(encoding='utf-8-sig'))
    base = next(p for p in assignment_path.parents if (p / 'catalog/abstract-format-partition/input.jsonl').exists())
    members = base / assignment['members_path']
    errors = []
    if digest(members) != assignment['members_sha256']:
        errors.append({'paper_id': None, 'errors': ['Assigned input changed']})
    papers = {r['paper_id']: r for r in (json.loads(l) for l in members.read_text(encoding='utf-8-sig').splitlines() if l.strip())}
    result_dir = base / assignment['worker_root'] / 'results'
    seen, counts = set(), Counter()
    for path in sorted(result_dir.glob('*.json')):
        try:
            record = json.loads(path.read_text(encoding='utf-8-sig'))
            pid = record.get('paper_id')
            if pid not in papers or pid in seen:
                errors.append({'paper_id': pid, 'errors': ['Unassigned or duplicate result']})
                continue
            seen.add(pid)
            problems = validate_record(record, papers[pid], base)
            if problems:
                errors.append({'paper_id': pid, 'errors': problems})
            for component in ['abstract', 'fulltext']:
                counts[component + ':' + record.get(component, {}).get('status', 'invalid')] += 1
            counts['identity:' + record.get('identity', {}).get('status', 'invalid')] += 1
            if not partial and (record.get('identity', {}).get('status') == 'unresolved' or
                    any(record.get(c, {}).get('status') == 'unresolved' for c in ['abstract', 'fulltext'])):
                errors.append({'paper_id': pid, 'errors': ['Unresolved work remains']})
        except (OSError, ValueError, TypeError, AttributeError):
            errors.append({'paper_id': path.stem, 'errors': ['Result file is malformed']})
    missing = sorted(set(papers) - seen)
    if missing and not partial:
        errors.append({'paper_id': None, 'errors': ['Assigned candidates have no result']})
    return {'passed': not errors, 'complete': not errors and not missing and not counts['identity:unresolved'] and
            not any(counts[c + ':unresolved'] for c in ['abstract', 'fulltext']),
            'group_id': assignment['group_id'], 'assigned': len(papers), 'processed': len(seen),
            'missing': len(missing), 'counts': dict(counts), 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assignment', type=Path, required=True)
    parser.add_argument('--partial', action='store_true')
    args = parser.parse_args()
    result = check_assignment(args.assignment, args.partial)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
