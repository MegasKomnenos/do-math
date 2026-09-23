#!/usr/bin/env python3
"""Validate explicit semantic mappings and bounded, fixed-edition run claims.

AST resolution proves a coordinate exists, not that its assertion proves a
requirement. Human-reviewed `asserts`, `scope`, and `gaps` carry that distinction.
No test is run by this checker and structural validity is never a feature pass.
"""
from __future__ import annotations
import argparse
import ast
from functools import lru_cache
import hashlib
import json
import re
from pathlib import Path
import sys


def _load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _path(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute(): return None
    result = (root / value).resolve()
    return result if result.is_relative_to(root.resolve()) and result.is_file() else None


@lru_cache(maxsize=128)
def _syntax(source):
    # Cache by exact text, never filename: concurrent edits cannot reuse a
    # previous edition's AST. A single test can support many source vectors.
    return ast.parse(source)


def _coordinate_exists(root, coordinate, *, test=False, cache=None):
    if not isinstance(coordinate, str): return False
    key = (coordinate, test)
    if cache is not None and key in cache: return cache[key]
    filename, sep, symbol = coordinate.partition('::')
    path = _path(root, filename)
    if path is None or not sep or not symbol or path.suffix != '.py': return False
    try: tree = _syntax(path.read_text(encoding='utf-8-sig'))
    except (SyntaxError, UnicodeError, OSError): return False
    node = tree
    for part in symbol.split('.'):
        node = next((n for n in getattr(node, 'body', []) if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == part), None)
        if node is None: return False
    result = not test or (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_'))
    if cache is not None: cache[key] = result
    return result


def _text(value): return isinstance(value, str) and bool(value.strip())


def unproven_errors(label, row):
    errors, covered = [], set()
    for item in row.get('unproven', []):
        indexes = item.get('gap_indexes', [])
        if (not isinstance(indexes, list) or any(type(i) is not int or i < 0 or i >= len(row.get('gaps', [])) for i in indexes)):
            errors.append(f'{label}: invalid gap indexes'); continue
        covered.update(indexes)
        if item.get('category') not in {'a', 'b', 'c', 'd'}:
            errors.append(f'{label}: invalid unproven category')
        if not _text(item.get('basis')) or not item.get('owners'):
            errors.append(f'{label}: unproven basis and owners required')
    if covered != set(range(len(row.get('gaps', [])))):
        errors.append(f'{label}: unclassified gap')
    return errors


def unittest_outcomes(log):
    """Read completed verbose unittest outcomes, never infer from exit code."""
    outcomes = {}
    for name, qualified, result in re.findall(
            r'^(test_\w+) \(([\w.]+)\) \.\.\. (ok|FAIL|ERROR|skipped[^\r\n]*)$', log, re.M):
        parts = qualified.split('.')
        if parts[-1] != name: parts.append(name)
        coordinate = '.claude/skills/do-math/scripts/tests/' + parts[0] + '.py::' + '.'.join(parts[1:])
        outcomes[coordinate] = 'passed' if result == 'ok' else 'skipped' if result.startswith('skipped') else 'failed'
    # A subtest's failure can replace its parent's single-line outcome.
    for qualified in re.findall(r'^(?:FAIL|ERROR): test_\w+ \(([\w.]+)\)', log, re.M):
        parts = qualified.split('.')
        coordinate = '.claude/skills/do-math/scripts/tests/' + parts[0] + '.py::' + '.'.join(parts[1:])
        outcomes[coordinate] = 'failed'
    return outcomes


def _archive_directory(root, value):
    if not _text(value) or Path(value).is_absolute() or '..' in Path(value).parts:
        return None
    # MAIN freezes skill + normative docs, not the append-only execution
    # archive. A paired snapshot may read that archive from its workspace
    # ancestor; no path depth or session cwd assumption is used.
    for base in (root, *root.parents):
        path = (base / value).resolve()
        if path.is_relative_to(base.resolve()) and (path / 'run.json').is_file():
            return path
    return None


def validate_observations(trace, root, *, editions=None):
    """Validate historical assertion runs, not current-edition feature passes."""
    errors, manifests = [], {}
    runs = trace.get('observed_runs', {})
    for identifier, run in runs.items():
        directory = _archive_directory(root, run.get('directory'))
        if directory is None:
            errors.append(f'{identifier}: archive directory unavailable'); continue
        meta_path, log_path = directory / 'run.json', directory / 'stderr.txt'
        try:
            meta, log = _load(meta_path), log_path.read_text(encoding='utf-8-sig')
            if hashlib.sha256(meta_path.read_bytes()).hexdigest() != run.get('manifest_sha256'):
                errors.append(f'{identifier}: manifest digest differs')
            if hashlib.sha256(log_path.read_bytes()).hexdigest() != run.get('log_sha256'):
                errors.append(f'{identifier}: log digest differs')
            if not meta.get('ended_at') or not meta.get('command') or 'returncode' not in meta:
                errors.append(f'{identifier}: completed run required')
            if not re.search(r'^Ran \d+ tests? in ', log, re.M):
                errors.append(f'{identifier}: completed run summary missing')
            if unittest_outcomes(log) != run.get('tests'):
                errors.append(f'{identifier}: observed outcomes differ from log')
            manifest = {'.claude/skills/do-math/' + k.replace('\\', '/'): v for k, v in meta.get('files', {}).items()}
            manifest.update({k.replace('\\', '/'): v for k, v in meta.get('support_files', {}).items()})
            if not manifest: errors.append(f'{identifier}: snapshot manifest required')
            snapshot = directory / 'repository'
            for filename, expected in manifest.items():
                path = _path(snapshot, filename)
                if path is None or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                    errors.append(f'{identifier}: snapshot bytes differ: {filename}')
            for coordinate in run.get('tests', {}):
                if (coordinate.partition('::')[0] not in manifest
                        or not _coordinate_exists(snapshot, coordinate, test=True)):
                    errors.append(f'{identifier}: observed test absent from snapshot')
            manifests[identifier] = manifest
        except (ValueError, OSError, TypeError) as error:
            errors.append(f'{identifier}: unreadable archive: {error}')
    rows = [*trace.get('vectors', {}).values(), *trace.get('quality_contracts', {}).values(),
            *trace.get('walkthroughs', [])]
    for row in rows:
        for evidence in row.get('evidence', []):
            for observation in evidence.get('observations', []):
                identifier, outcome = observation.get('run_id'), observation.get('outcome')
                actual = runs.get(identifier, {}).get('tests', {}).get(evidence.get('coordinate'))
                if outcome not in {'passed', 'failed', 'skipped'} or actual != outcome:
                    errors.append('observation: cited test outcome is not in the run')
                required = {c.partition('::')[0] for c in row.get('implementation', [])}
                if not required.issubset(manifests.get(identifier, {})):
                    errors.append('observation: implementation edition absent from run')
    if editions is not None:
        editions.update(manifests)
    return errors


def _item(root, label, row, groups, runs, errors, cache=None):
    if not isinstance(row, dict):
        errors.append(f'{label}: explicit mapping object required'); return
    for key in ('rationale', 'scope'):
        if not _text(row.get(key)): errors.append(f'{label}: {key} required')
    status = row.get('mapping')
    if status not in {'mapped', 'partial', 'gap', 'replaced', 'withdrawn', 'out_of_scope'}:
        errors.append(f'{label}: invalid semantic mapping')
    if not isinstance(row.get('gaps'), list) or any(not _text(v) for v in row.get('gaps', [])):
        errors.append(f'{label}: gaps must be explicit strings')
    if status in {'partial', 'gap', 'out_of_scope'} and not row.get('gaps'):
        errors.append(f'{label}: incomplete mapping requires gaps')
    if status == 'mapped' and row.get('gaps'): errors.append(f'{label}: mapped cannot hide gaps')
    if status in {'replaced', 'withdrawn', 'out_of_scope'}:
        reason = row.get('disposition', {})
        if not _text(reason.get('reason')) or not _text(reason.get('source')):
            errors.append(f'{label}: disposition source and reason required')
    group_ids = row.get('groups', [])
    if not isinstance(group_ids, list) or not group_ids or any(g not in groups for g in group_ids):
        errors.append(f'{label}: explicit semantic group required')
    implementations = row.get('implementation')
    if not isinstance(implementations, list):
        errors.append(f'{label}: implementation coordinates required'); implementations = []
    for coordinate in implementations:
        if not _coordinate_exists(root, coordinate, cache=cache): errors.append(f'{label}: nonexistent implementation coordinate: {coordinate}')
    evidence = row.get('evidence')
    if not isinstance(evidence, list):
        errors.append(f'{label}: evidence must be a list'); evidence = []
    for entry in evidence:
        if not isinstance(entry, dict): errors.append(f'{label}: evidence object required'); continue
        if not _coordinate_exists(root, entry.get('coordinate'), test=True, cache=cache):
            errors.append(f'{label}: nonexistent evidence coordinate: {entry.get("coordinate")}')
        if not _text(entry.get('asserts')): errors.append(f'{label}: evidence asserts scope required')
        if not isinstance(entry.get('boundary'), list) or not entry['boundary']:
            errors.append(f'{label}: real/stub boundary required')
    if status in {'mapped', 'partial'} and not implementations:
        errors.append(f'{label}: applicable mapping requires implementation coordinates')
    if status == 'mapped' and not evidence: errors.append(f'{label}: mapped needs assertion evidence')
    execution = row.get('execution', {})
    state = execution.get('state')
    if state not in {'not_run', 'partial', 'passed', 'failed', 'not_applicable'}:
        errors.append(f'{label}: execution state must be separate from mapping')
    ids = execution.get('run_ids')
    if not isinstance(ids, list): errors.append(f'{label}: execution.run_ids required'); ids = []
    if state in {'partial', 'passed', 'failed'} and (not ids or any(i not in runs for i in ids)):
        errors.append(f'{label}: execution requires a fixed run')
    if state == 'not_run' and ids: errors.append(f'{label}: not_run cannot cite runs')
    if state == 'passed':
        if status != 'mapped' or row.get('gaps'):
            errors.append(f'{label}: pass requires complete semantic mapping')
        if any(runs.get(i, {}).get('tests', {}).get(e.get('coordinate')) == 'failed'
               for i in ids for e in evidence if isinstance(e, dict)):
            errors.append(f'{label}: pass includes a cited failure')
        coordinates = {e.get('coordinate') for e in evidence if isinstance(e, dict)}
        passed = {c for i in ids if i in runs for c, outcome in runs[i].get('tests', {}).items() if outcome == 'passed'}
        if not coordinates or not coordinates.issubset(passed): errors.append(f'{label}: run does not pass every cited test')
        required_files = {c.partition('::')[0] for c in implementations}
        for identifier in ids:
            if identifier in runs and not required_files.issubset(runs[identifier].get('file_sha256', {})):
                errors.append(f'{label}: fixed run omits implementation edition')
    if state == 'failed' and not any(
            runs.get(i, {}).get('tests', {}).get(e.get('coordinate')) == 'failed'
            for i in ids for e in evidence if isinstance(e, dict)):
        errors.append(f'{label}: failed state requires a cited failing test')
    if state == 'partial':
        if not any(runs.get(i, {}).get('tests', {}).get(e.get('coordinate')) in {'passed', 'failed', 'skipped'}
                   for i in ids for e in evidence if isinstance(e, dict)):
            errors.append(f'{label}: partial execution needs a cited observed test')
        required_files = {c.partition('::')[0] for c in implementations}
        for identifier in ids:
            if identifier in runs and not required_files.issubset(runs[identifier].get('file_sha256', {})):
                errors.append(f'{label}: fixed run omits implementation edition')


def scope_artifact_errors(trace, root):
    """Bind scope sources and bounded observations, never infer a feature pass."""
    errors = []
    artifacts = trace.get('scope_artifacts', {})
    for name, item in artifacts.items():
        value = item.get('path')
        path = None
        if _text(value) and not Path(value).is_absolute() and '..' not in Path(value).parts:
            for base in (root, *root.parents):
                candidate = (base / value).resolve()
                if candidate.is_relative_to(base.resolve()) and candidate.is_file():
                    path = candidate
                    break
        if path is None:
            errors.append(f'{name}: scope artifact unavailable')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item.get('sha256'):
            errors.append(f'{name}: scope artifact bytes differ')
        if not _text(item.get('scope')) or not _text(item.get('boundary')):
            errors.append(f'{name}: scope and evidence boundary required')
    for key in ('vectors', 'quality_contracts'):
        for name, row in trace.get(key, {}).items():
            adopted = row.get('adopted_scope')
            if adopted is None:
                continue
            refs = adopted.get('source_refs', [])
            if not refs or any(ref not in artifacts for ref in refs):
                errors.append(f'{name}: unknown scope source')
            if not all(_text(adopted.get(k)) for k in ('retained_effects', 'changed_or_conditional')):
                errors.append(f'{name}: adopted scope requires retained and changed effects')
    return errors


def validate_data(trace, source, root, source_path):
    editions = {}
    errors = validate_observations(trace, root, editions=editions)
    errors.extend(scope_artifact_errors(trace, root))
    if trace.get('contract', {}).get('unproven_classification'):
        for key in ('vectors', 'quality_contracts'):
            for label, row in trace.get(key, {}).items():
                errors.extend(unproven_errors(label, row))
        for row in trace.get('walkthroughs', []):
            errors.extend(unproven_errors('W' + str(row.get('id')), row))
    # One validation observes each coordinate once; the next validation reads
    # afresh. This is not a persistent path/mtime cache across code editions.
    cache = {}
    if trace.get('schema_version') != 2: errors.append('schema_version must be 2; defaults are not mappings')
    if trace.get('defaults'): errors.append('defaults cannot replace explicit mappings')
    contract = trace.get('source_vector_map', {})
    if contract.get('path') != source_path.relative_to(root).as_posix(): errors.append('wrong source_vector_map.path')
    if contract.get('sha256') != hashlib.sha256(source_path.read_bytes()).hexdigest(): errors.append('source_vector_map.sha256 mismatch')
    groups = trace.get('semantic_groups', {})
    for name, group in groups.items():
        if not all(_text(group.get(k)) for k in ('requirement', 'observed', 'limit')):
            errors.append(f'{name}: semantic group requires requirement/observed/limit')
    runs = trace.get('runs', {})
    for identifier, run in runs.items():
        if not _text(run.get('command')) or not isinstance(run.get('tests'), dict) or not run.get('tests'):
            errors.append(f'{identifier}: fixed run command and test outcomes required')
        manifest = run.get('file_sha256', {})
        if not isinstance(manifest, dict) or not manifest: errors.append(f'{identifier}: fixed run needs a file manifest')
        else:
            for filename, digest in manifest.items():
                path = _path(root, filename)
                if path is None or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    errors.append(f'{identifier}: run edition differs: {filename}')
        log = _path(root, run.get('log_path'))
        if log is None or hashlib.sha256(log.read_bytes()).hexdigest() != run.get('log_sha256'):
            errors.append(f'{identifier}: run log missing or changed')
        for coordinate, outcome in run.get('tests', {}).items():
            if not _coordinate_exists(root, coordinate, test=True) or outcome not in {'passed', 'failed', 'skipped'}:
                errors.append(f'{identifier}: invalid test outcome')
            if coordinate.partition('::')[0] not in manifest: errors.append(f'{identifier}: test absent from edition manifest')
        # A successful shell command alone cannot manufacture per-test results.
        report = _path(root, run.get('report_path'))
        if report is None: errors.append(f'{identifier}: machine test report required')
        else:
            try: result = _load(report)
            except (ValueError, OSError): result = {}
            if result.get('tests') != run.get('tests') or result.get('file_sha256') != manifest:
                errors.append(f'{identifier}: machine report differs from declared outcomes/edition')
            if hashlib.sha256(report.read_bytes()).hexdigest() != run.get('report_sha256'):
                errors.append(f'{identifier}: machine report digest differs')
    runs = {**runs, **{identifier: {**run, 'file_sha256': editions.get(identifier, {})}
                      for identifier, run in trace.get('observed_runs', {}).items()}}
    for key in ('vectors', 'quality_contracts'):
        originals = {r['id']: r for r in source[key]}
        rows = trace.get(key, {})
        missing, unknown = originals.keys() - rows.keys(), rows.keys() - originals.keys()
        if missing: errors.append(f'{key}: missing source IDs: {sorted(missing)}')
        if unknown: errors.append(f'{key}: unknown source IDs: {sorted(unknown)}')
        for identifier in originals.keys() & rows.keys():
            row, original = rows[identifier], originals[identifier]
            for field in ('input', 'expected', 'source_row_sha256') if key == 'vectors' else ('guarantee', 'source_vectors', 'source_row_sha256'):
                if row.get(field) != original.get(field): errors.append(f'{identifier}: source requirement {field} differs')
            _item(root, identifier, row, groups, runs, errors, cache)
    walks = trace.get('walkthroughs', [])
    if len(walks) != 12 or sorted(r.get('id', 0) for r in walks) != list(range(1, 13)):
        errors.append('walkthroughs must identify twelve scenarios exactly once')
    coordinates = []
    for row in walks:
        label = 'walkthrough ' + str(row.get('id'))
        _item(root, label, row, groups, runs, errors, cache)
        coordinates.extend(e.get('coordinate') for e in row.get('evidence', []))
        for key in ('input', 'transitions', 'stubbed', 'real'):
            if not row.get(key): errors.append(f'{label}: {key} required')
    if len(set(coordinates)) != len(coordinates): errors.append('walkthroughs require distinct scenario tests, not twelve aliases')
    return errors


def validate(trace_path, source_path, root):
    return validate_data(_load(trace_path), _load(source_path), root.resolve(), source_path.resolve())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    parser.add_argument('--traceability', default='docs/do-math/implementation-v5/traceability.json')
    parser.add_argument('--source', default='docs/do-math/통합-설계-명세-v9/source-vector-map.json')
    args = parser.parse_args(argv); root = Path(args.root).resolve()
    try: errors = validate(root / args.traceability, root / args.source, root)
    except (OSError, ValueError, TypeError, KeyError) as error: errors = [f'invalid trace: {error}']
    if errors:
        print('\n'.join(errors), file=sys.stderr); return 1
    print('Explicit semantic mappings structurally valid; no implied execution pass.')
    return 0


if __name__ == '__main__': raise SystemExit(main())
