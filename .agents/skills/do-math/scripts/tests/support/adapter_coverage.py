"""T4 adapter reach, independent of the T3 gate/index/store.

Measurement supplies the same branch tracer, context lifecycle and bookkeeping
pause as T3. Only LAYERS adapters are traced here. Explicit source morfs include
untouched files in the denominator; reach is information, never a threshold.
Worker publications are bound to this run, request and complete Python edition.
Missing/invalid publications leave a partial union with explicit reasons.
Python in arbitrary product children, PowerShell and Lean internals is outside
this measurement. Test outcomes remain in the runner report.
"""
from __future__ import annotations

import json
from pathlib import Path

from support.branch_gate import DATA, ENTERED, OPENED, Measurement, SCRIPTS

MANIFEST = 'adapter-measurement.json'
FORMAT = 'do-math-t4-adapter/1'


def source_edition():
    from do_math.file_io import sha256_file
    return {p.relative_to(SCRIPTS).as_posix(): sha256_file(p)
            for p in sorted(SCRIPTS.rglob('*.py')) if '__pycache__' not in p.parts}


def validate_publication(directory, expected):
    """Shared producer/consumer validation; exceptions identify unusable evidence."""
    from do_math.file_io import sha256_file
    directory = Path(directory)
    manifest = json.loads((directory / MANIFEST).read_text(encoding='utf-8'))
    if manifest['request'] != expected:
        raise ValueError('different run, request or source edition')
    if manifest['source_after'] != expected['source_sha256']:
        raise ValueError('source edition changed in worker')
    if set(manifest['artifacts']) != {DATA, OPENED, ENTERED}:
        raise ValueError('measurement artifact population mismatch')
    for name, digest in manifest['artifacts'].items():
        if sha256_file(directory / name) != digest:
            raise ValueError('measurement artifact digest mismatch: ' + name)
    # Parse before combining: a corrupt SQLite file is not an empty measurement.
    from coverage import CoverageData
    data = CoverageData(basename=str(directory / DATA))
    data.read()
    if not data.has_arcs():
        raise ValueError('worker did not record branch data')
    json.loads((directory / OPENED).read_text(encoding='utf-8'))
    json.loads((directory / ENTERED).read_text(encoding='utf-8'))
    return data


class AdapterMeasurement(Measurement):
    def __init__(self, root, *, data_file, request):
        super().__init__(root, data_file=data_file)
        from do_math.layers import LAYERS
        self.modules = sorted(p for p, layer in LAYERS.items() if layer == 'adapter')
        self.coverage.set_option('run:include', [str(SCRIPTS / p) for p in self.modules])
        # source= overrides include in coverage.py, so use include alone.
        self.coverage.set_option('run:source', None)
        self.request = request
        self.workers = []
        self.problems = []
        self.source_before = source_edition()

    def save(self, directory):
        from do_math.file_io import sha256_file
        super().save(directory)
        manifest = {'request': self.request, 'source_after': source_edition(),
                    'artifacts': {name: sha256_file(Path(directory) / name) for name in (DATA, OPENED, ENTERED)}}
        if self.source_before != self.request['source_sha256']:
            raise ValueError('worker started on a different source edition')
        (Path(directory) / MANIFEST).write_text(json.dumps(manifest), encoding='utf-8')
        validate_publication(directory, self.request)

    def merge_workers(self, reports):
        """Merge only validated, requested workers; retain failures without inventing zero reach."""
        self._stop()
        for report in reports:
            directory = Path(report['directory'])
            record = {'directory': str(directory), 'manifest': str(directory / MANIFEST),
                      'requested': report['requested'], 'returncode': report.get('returncode')}
            expected = {**self.request, 'requested': report['requested']}
            try:
                data = validate_publication(directory, expected)
                self.coverage.get_data().update(data)
                record['status'] = 'merged'
            except Exception as error:
                record.update(status='invalid', reason=f'{type(error).__name__}: {error}')
                self.problems.append({'path': str(directory / MANIFEST), 'reason': record['reason']})
            self.workers.append(record)

    def finish_report(self, directory, *, reports, changed):
        """Report after tracing stopped; file analysis/serialization adds no test reach."""
        self.merge_workers(reports)
        if self.source_before != self.request['source_sha256'] or source_edition() != self.request['source_sha256']:
            self.problems.append({'path': str(SCRIPTS), 'reason': 'source edition mismatch'})
        if changed:
            self.problems.append({'path': str(SCRIPTS), 'reason': 'source changed during run: ' + ', '.join(changed)})
        target = Path(directory) / 'adapter-coverage.json'
        self.coverage.json_report(morfs=[str(SCRIPTS / p) for p in self.modules], outfile=str(target))
        coverage_report = json.loads(target.read_text(encoding='utf-8'))
        entries = {(Path.cwd() / p).resolve(): value for p, value in coverage_report['files'].items()}
        modules = {p: {'path': (SCRIPTS / p).relative_to(self.root).as_posix(),
                       'source_sha256': self.request['source_sha256'][p], **entries[(SCRIPTS / p).resolve()]}
                   for p in self.modules}
        result = {'format': FORMAT, 'run_id': self.request['run_id'],
                  'complete': not self.problems, 'problems': self.problems, 'workers': self.workers,
                  'modules': modules, 'totals': coverage_report['totals'], 'meta': coverage_report['meta'],
                  'scope': 'Python adapters in boundary tests/fixtures in the runner and requested workers '
                           '(workers also observe discovery imports); '
                           'excludes runner bookkeeping and arbitrary product children/PowerShell/Lean internals'}
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return result
