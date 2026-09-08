"""Partition the candidate snapshot by verified local abstract representation."""
import csv
import argparse
import hashlib
import html
import io
import json
import re
import sys
import shutil
import unicodedata
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from functools import lru_cache
from functools import cached_property


ABSENCE = {'no abstract available', 'abstract not available', 'no abstract', 'not available',
           'n/a', 'na', 'none', 'null', 'abstract unavailable', 'no abstract supplied', 'abstract'}
BASE = next(parent for parent in Path(__file__).resolve().parents
            if (parent / 'scripts/build_b001_catalog.py').is_file())
sys.path.insert(0, str(BASE / 'scripts'))
import build_b001_catalog as export_parser
import build_b002_catalog as bib_parser


def read_export(text, source_id):
    if source_id in {'wos', 'pqdt'}:
        try:
            parsed = export_parser.parse_ris(text, source_name=source_id)
        except export_parser.B001CatalogError as exc:
            raise ValueError(str(exc)) from exc
        records = []
        for row in parsed:
            if 'ty' not in row['fields']:
                raise ValueError('RIS record has no TY field')
            occurrence = export_parser._ris_occurrence(row, source_id)
            records.append({'id': occurrence['source_record_id'], 'title': occurrence['bibliographic']['title'],
                            'family': 'ris', 'fields': row['fields']})
        return records
    if source_id in {'acm-dl', 'ieee-xplore', 'mathscinet'}:
        try:
            entries = [(e, None) for e in bib_parser.parse_bibtex(text)]
        except bib_parser.BibTeXError:
            # Seven existing ACM records have broken braces in the exported prose.
            # Retain their field spans without repairing the source's mathematics.
            entries = []
            for row in export_parser.parse_bibtex_tolerant(text, source_name=source_id):
                try:
                    entries.append((bib_parser.parse_bibtex(row['raw_text'])[0], None))
                except bib_parser.BibTeXError as exc:
                    entries.append((row, str(exc)))
        records = []
        for entry, warning in entries:
            fields = defaultdict(list)
            if warning:
                fields.update(entry['fields'])
                key = entry['key']
            else:
                key = entry.key
                for name, value in entry.field_items:
                    fields[name].append(value.strip())
            if source_id == 'mathscinet' and fields.get('mrnumber'):
                key = 'MR' + fields['mrnumber'][0]
            records.append({'id': key, 'title': ' '.join(fields.get('title', [])), 'fields': dict(fields),
                            'family': 'mathscinet-bibtex' if source_id == 'mathscinet' else 'bibtex',
                            'parse_warning': warning})
        return records
    if source_id != 'scopus':
        raise ValueError('Unsupported export: ' + source_id)
    csv.field_size_limit(max(csv.field_size_limit(), len(text)))
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff'), newline=''), strict=True)
    names = reader.fieldnames or []
    if not {'EID', 'Title', 'Abstract', 'Source'} <= set(names) or len(names) != len(set(names)):
        raise ValueError('Not an unambiguous Scopus CSV export')
    records = []
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('CSV row width differs from header')
        if row['Source'].strip().casefold() != 'scopus' or not row['EID'].strip():
            raise ValueError('CSV source or EID missing')
        records.append({'id': row['EID'].strip(), 'title': row['Title'],
                        'family': 'scopus-csv',
                        'fields': {k.casefold(): [v] for k, v in row.items()}})
    return records


def abstract_fields(fields):
    abstracts = []
    for name, values in fields.items():
        if name.casefold() not in {'abstract', 'abstract note', 'ab', 'n2'}:
            continue
        for value in values:
            if not isinstance(value, str):
                raise ValueError('Abstract must be a string')
            text = value.strip()
            visible = text
            if re.match(r'<[A-Za-z][\w:.-]*(?:\s|/?>)', text):
                parser = _VisibleText()
                parser.feed(text)
                visible = ''.join(parser.parts)
            marker = visible.strip(' \t\r\n.[]{}').casefold()
            if any(c.isalnum() for c in visible) and marker not in ABSENCE:
                abstracts.append({'field': name, 'text': text})
    return abstracts


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def bound_record(records, rank, expected_id):
    if type(rank) is not int or not 1 <= rank <= len(records):
        raise ValueError('Source rank out of range')
    row = records[rank - 1]
    if row['id'].casefold() != str(expected_id).casefold():
        raise ValueError('Source record identity mismatch')
    return row


def partition_step(rows, decisions, family, outcome):
    ids = [row['paper_id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate paper IDs')
    def matches(row):
        d = decisions.get(row['paper_id'], {})
        return matches_group(d, family, outcome)
    if not rows or not matches(rows[0]):
        raise ValueError('Requested group does not contain the first pending item')
    return ([row for row in rows if matches(row)], [row for row in rows if not matches(row)])


def matches_group(decision, family, outcome):
    sources = decision.get('sources')
    if sources is None:
        return (decision.get('family'), decision.get('outcome')) == (family, outcome)
    if outcome == 'extracted':
        return any(s['family'] == family and s['abstracts'] for s in sources)
    return (outcome == 'needs-source' and not any(s['abstracts'] for s in sources)
            and any(s['family'] == family for s in sources))


def checked_bytes(path, expected=None):
    data = path.read_bytes()
    if expected and hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Source hash mismatch: ' + str(path))
    return data


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def object_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def save_step(folder, decisions, family, outcome):
    folder = Path(folder)
    raw_lines = (folder / 'remaining.jsonl').read_bytes().splitlines(keepends=True)
    rows = [json.loads(line) for line in raw_lines if line.strip()]
    removed, remaining = partition_step(rows, decisions, family, outcome)
    removed_ids = {row['paper_id'] for row in removed}
    iterations_path = folder / 'iterations.jsonl'
    history = read_jsonl(iterations_path) if iterations_path.exists() else []
    sequence = len(history) + 1
    group = folder / 'groups' / f'{sequence:02d}-{outcome}-{family}'
    group.mkdir(parents=True)
    (group / 'members.jsonl').write_bytes(b''.join(line for line in raw_lines if json.loads(line)['paper_id'] in removed_ids))
    abstracts, evidence = [], []
    for paper in removed:
        decision = decisions[paper['paper_id']]
        audit_sources = []
        for source in decision.get('sources', []):
            metadata = {k: v for k, v in source.items() if k != 'abstracts'}
            audit_sources.append({**metadata, 'abstract_count': len(source.get('abstracts', []))})
            if outcome == 'extracted' and source['family'] == family:
                for abstract in source.get('abstracts', []):
                    abstracts.append({'paper_id': paper['paper_id'], **abstract,
                                      'text_sha256': hashlib.sha256(abstract['text'].encode()).hexdigest(),
                                      'source': metadata})
        evidence.append({'paper_id': paper['paper_id'], 'family': family, 'outcome': outcome,
                         'sources': audit_sources, 'reason': decision.get('reason')})
    write_jsonl(group / 'abstracts.jsonl', abstracts)
    write_jsonl(group / 'evidence.jsonl', evidence)
    config = {'family': family, 'outcome': outcome}
    (group / 'format.py').write_text(
        '"""Recognize and re-extract this group from the pinned local sources."""\n'
        'from pathlib import Path\nimport sys\n'
        'sys.path.insert(0, str(Path(__file__).resolve().parents[2]))\n'
        'from partition import group_main\n'
        f'FORMAT = {config!r}\n'
        "if __name__ == '__main__':\n    group_main(Path(__file__).parent, FORMAT)\n", encoding='utf-8')
    iteration = {'iteration': sequence, 'first_paper_id': rows[0]['paper_id'],
                 'family': family, 'outcome': outcome, 'before': len(rows),
                 'removed': len(removed), 'remaining': len(remaining),
                 'group': group.relative_to(folder).as_posix()}
    write_jsonl(iterations_path, history + [iteration])
    temporary = folder / 'remaining.jsonl.tmp'
    temporary.write_bytes(b''.join(line for line in raw_lines if json.loads(line)['paper_id'] not in removed_ids))
    temporary.replace(folder / 'remaining.jsonl')
    print(json.dumps(iteration, ensure_ascii=False), flush=True)
    return iteration


def write_jsonl(path, rows):
    with Path(path).open('w', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def field_record(record):
    if record.get('schema_version') != 'pvsnp-literature-candidate/1' or not isinstance(record.get('fields'), list):
        raise ValueError('Not a MathSciNet field-list record')
    fields = defaultdict(list)
    for field in record['fields']:
        fields[field['name'].casefold()].append(field['value'])
    return {'family': 'mathscinet-fields-json', 'source_record_id': record['candidate_id'],
            'source_title': ' '.join(fields.get('title', [])), 'abstracts': abstract_fields(fields),
            'field_names': list(fields)}


def title_key(text):
    value = html.unescape(text)
    value = re.sub(r'</?(?:i|b|em|strong|sub|sup|span)(?:\s[^>]*)?>', '', value, flags=re.I)
    value = re.sub(r'\\(?:textit|textbf|emph|mathrm|mathbf|mathcal|operatorname)\s*', '', value)
    value = re.sub(r"\\['\"`^~=.uvHckbr]\s*\{?(\w)\}?", r'\1', value)
    value = unicodedata.normalize('NFKD', value).casefold()
    return ''.join(c for c in value if c.isalnum() and not unicodedata.combining(c))


def doi_key(value):
    return re.sub(r'^https?://(?:dx\.)?doi\.org/', '', str(value).strip().casefold().replace('\\_', '_'))


def cache_record(envelope, provider, titles, dois):
    source = {'family': provider + '-json', 'abstracts': []}
    if envelope.get('http_status', 200) != 200:
        return {**source, 'reason': 'http-' + str(envelope.get('http_status'))}
    payload = envelope
    if isinstance(envelope.get('response_text'), str):
        data = envelope['response_text'].encode('utf-8')
        if envelope.get('response_sha256') and hashlib.sha256(data).hexdigest() != envelope['response_sha256']:
            raise ValueError('Response hash mismatch')
        payload = json.loads(envelope['response_text'])
    if provider == 'crossref':
        message = payload.get('message', payload)
        key = message.get('DOI')
        returned = message.get('title', [])
        returned = [returned] if isinstance(returned, str) else list(returned)
        subtitles = message.get('subtitle', [])
        subtitles = [subtitles] if isinstance(subtitles, str) else subtitles
        returned += [t + ' ' + s for t in returned for s in subtitles]
        entries = [('message.abstract', message.get('abstract', ''))]
    elif provider == 'datacite':
        message = payload['data']['attributes']
        key = message.get('doi')
        returned = [t['title'] for t in message.get('titles', [])]
        entries = [(f'descriptions[{i}]', d['description']) for i, d in enumerate(message.get('descriptions', []))
                   if d.get('descriptionType', '').casefold() == 'abstract']
    else:
        raise ValueError('Unknown metadata provider')
    source.update(source_record_id=key, source_titles=returned)
    if doi_key(key) not in {doi_key(d) for d in dois} or not ({title_key(t) for t in returned} & {title_key(t) for t in titles}):
        return {**source, 'reason': 'identity-mismatch'}
    source['abstracts'] = [{'field': name, 'text': item['text']} for name, value in entries
                           for item in abstract_fields({'abstract': [value]})]
    return source


def choose(sources):
    if not sources:
        raise ValueError('No recognized source representation')
    ready = next((s for s in sources if s['abstracts']), None)
    if ready:
        return {'family': ready['family'], 'outcome': 'extracted', 'sources': sources}
    return {'family': sources[0]['family'], 'outcome': 'needs-source', 'sources': sources,
            'reason': 'No usable abstract in the checked local representations; additional source acquisition or reading is required.'}


def page_abstract(text):
    normalized = re.sub(r'(?<!\n)(?=L\d+(?:@[^:\n]*)?: )', '\n', text)
    lines = [re.sub(r'^L\d+(?:@[^:]*)?:\s?', '', line).rstrip() for line in normalized.splitlines()]
    starts = [i for i, line in enumerate(lines) if re.fullmatch(r'\s*#{1,6}\s+Abstract\s*', line, re.I)]
    if len(starts) != 1:
        return ''
    collected = []
    for line in lines[starts[0] + 1:]:
        if re.match(r'^\s*#{1,6}\s+', line) or line.startswith('This is a preview of subscription content'):
            return '\n'.join(collected).strip()
        collected.append(line)
    return ''


def run_all(folder, observe):
    folder = Path(folder)
    rows = read_jsonl(folder / 'remaining.jsonl')
    observations = {}
    for i, row in enumerate(rows, 1):
        observations[row['paper_id']] = choose(observe(row))
        if i % 1000 == 0:
            print(f'Observed {i}/{len(rows)}', file=sys.stderr, flush=True)
    write_jsonl(folder / 'observations.jsonl', [{'paper_id': key, **value} for key, value in observations.items()])
    while rows:
        head = observations[rows[0]['paper_id']]
        save_step(folder, observations, head['family'], head['outcome'])
        rows = read_jsonl(folder / 'remaining.jsonl')
    return observations


def verify_partition(folder):
    folder = Path(folder)
    original = read_jsonl(folder / 'input.jsonl')
    observations = {r['paper_id']: r for r in read_jsonl(folder / 'observations.jsonl')}
    history = read_jsonl(folder / 'iterations.jsonl')
    pending = list(original)
    report = {'input_count': len(original), 'extracted': 0, 'needs_source': 0, 'groups': [],
              'false_positives': [], 'false_negatives': [], 'text_mismatches': [], 'integrity_errors': []}
    for iteration in history:
        group = folder / iteration['group']
        actual = read_jsonl(group / 'members.jsonl')
        expected = []
        for row in pending:
            sources = observations[row['paper_id']]['sources']
            available = [s for s in sources if s['abstracts']]
            if iteration['outcome'] == 'extracted':
                eligible = any(s['family'] == iteration['family'] for s in available)
            else:
                eligible = not available and any(s['family'] == iteration['family'] for s in sources)
            if eligible:
                expected.append(row)
        actual_ids = [r['paper_id'] for r in actual]
        expected_ids = [r['paper_id'] for r in expected]
        fp = sorted(set(actual_ids) - set(expected_ids))
        fn = sorted(set(expected_ids) - set(actual_ids))
        report['false_positives'].extend(fp)
        report['false_negatives'].extend(fn)
        if actual != expected:
            report['integrity_errors'].append(iteration['group'] + ': membership, order or original record changed')
        if (not pending or iteration['first_paper_id'] != pending[0]['paper_id'] or
                iteration['before'] != len(pending) or iteration['removed'] != len(expected) or
                iteration['remaining'] != len(pending) - len(expected)):
            report['integrity_errors'].append(iteration['group'] + ': iteration boundary changed')
        abstracts = read_jsonl(group / 'abstracts.jsonl')
        wanted = []
        if iteration['outcome'] == 'extracted':
            for row in expected:
                for source in observations[row['paper_id']]['sources']:
                    if source['family'] == iteration['family']:
                        for abstract in source['abstracts']:
                            wanted.append((row['paper_id'], abstract['field'], abstract['text'],
                                           source.get('source_record_id'), source.get('locator')))
        observed = [(a['paper_id'], a['field'], a['text'], a['source'].get('source_record_id'),
                     a['source'].get('locator')) for a in abstracts]
        if observed != wanted:
            report['text_mismatches'].append(iteration['group'])
        if any(hashlib.sha256(a['text'].encode()).hexdigest() != a['text_sha256'] for a in abstracts):
            report['text_mismatches'].append(iteration['group'] + ': text hash mismatch')
        report['extracted' if iteration['outcome'] == 'extracted' else 'needs_source'] += len(actual)
        report['groups'].append({**iteration, 'false_positives': len(fp), 'false_negatives': len(fn),
                                 'abstract_values': len(abstracts)})
        removed_ids = set(expected_ids)
        pending = [r for r in pending if r['paper_id'] not in removed_ids]
    if pending or read_jsonl(folder / 'remaining.jsonl'):
        report['integrity_errors'].append('Remaining list is not empty')
    if len({r['paper_id'] for r in original}) != len(original):
        report['integrity_errors'].append('Input has duplicate paper IDs')
    report['remaining'] = len(read_jsonl(folder / 'remaining.jsonl'))
    report['passed'] = not any(report[k] for k in ['false_positives', 'false_negatives', 'text_mismatches', 'integrity_errors'])
    return report


def group_main(group, config):
    parser = argparse.ArgumentParser(description='Check this format group against its local sources.')
    parser.add_argument('--extract', action='store_true', help='Print freshly extracted abstract JSONL to stdout')
    parser.add_argument('--check', action='store_true', help='Check every saved member (default)')
    parser.add_argument('--input', type=Path, help='Candidate JSONL to recognize; defaults to members.jsonl')
    parser.add_argument('--recognize', action='store_true', help='Print all matching candidate records as JSONL')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    repository = Repository(BASE)
    failures = []
    for paper in read_jsonl(args.input or group / 'members.jsonl'):
        sources = repository.sources(paper)
        if not matches_group(choose(sources), config['family'], config['outcome']):
            if args.check or not (args.extract or args.recognize):
                failures.append(paper['paper_id'])
            continue
        if args.recognize:
            print(json.dumps(paper, ensure_ascii=False))
        if args.extract:
            for source in sources:
                if source['family'] == config['family'] and config['outcome'] == 'extracted':
                    for abstract in source['abstracts']:
                        print(json.dumps({'paper_id': paper['paper_id'], **abstract}, ensure_ascii=False))
    if not (args.extract or args.recognize):
        print(json.dumps({'passed': not failures, 'false_positives': failures, 'group': group.name}))
    if failures:
        raise SystemExit(1)


class Repository:
    def __init__(self, base):
        self.base = Path(base).resolve()
        self.source_hashes = {}
        self.b001 = {r['candidate_id']: r for r in self.catalog('catalog/B001-candidates.jsonl')}

    @cached_property
    def b002(self):
        return {r['candidate_id']: r for r in self.catalog('catalog/B002-candidates.jsonl')}

    @lru_cache(maxsize=None)
    def catalog(self, relative):
        data = self.read(relative)
        if relative.endswith('.jsonl'):
            return [json.loads(line) for line in data.decode('utf-8-sig').splitlines() if line.strip()]
        value = json.loads(data)
        return value if isinstance(value, list) else [value]

    def read(self, relative, expected=None):
        data = checked_bytes(self.path(relative), expected)
        self.source_hashes[relative] = hashlib.sha256(data).hexdigest()
        return data

    @cached_property
    def cache_index(self):
        index = defaultdict(list)
        for relative, provider in [('intake/B002-public/crossref', 'crossref'),
                                   ('intake/abstract-recovery/crossref', 'crossref'),
                                   ('intake/abstract-recovery/datacite', 'datacite')]:
            for path in sorted((self.base / relative).glob('*.json')):
                relative_path = path.relative_to(self.base).as_posix()
                envelope = json.loads(self.read(relative_path))
                key = envelope.get('doi')
                if not key:
                    payload = json.loads(envelope['response_text']) if 'response_text' in envelope else envelope
                    key = payload.get('message', payload).get('DOI')
                if not key:
                    raise ValueError('Metadata cache has no DOI: ' + relative_path)
                index[doi_key(key)].append((relative_path, provider, envelope))
        return index

    @cached_property
    def page_index(self):
        index = defaultdict(list)
        for path in sorted((self.base / 'intake/abstract-recovery/pages').glob('*.json')):
            relative = path.relative_to(self.base).as_posix()
            record = json.loads(self.read(relative))
            if record.get('schema') != 'captured-author-abstract/1':
                raise ValueError('Unrecognized captured page envelope')
            index[record['paper_id']].append((relative, record))
        return index

    def sources(self, paper):
        sources = self.export_sources(paper)
        titles = [paper['title']] + [s['source_title'] for s in sources]
        dois = list(paper.get('identifiers', {}).get('doi', []))
        for reference in paper['source_records']:
            catalog = reference['catalog']
            if catalog == 'B001':
                dois += self.b001[reference['record_id']]['bibliographic'].get('doi', [])
                continue
            if catalog == 'B002':
                record = self.b002[reference['record_id']]
                source = field_record(record)
                dois += [f['value'] for f in record['fields'] if f['name'].casefold() == 'doi']
                titles.append(source['source_title'])
                source['locator'] = {'path': reference['path'], 'record_id': reference['record_id']}
                source['record_sha256'] = object_sha(record)
            elif catalog in {'PUBLIC_MSC', 'PUBLIC_TCS', 'PUBLIC_DIRECT'}:
                record = next(r for r in self.catalog(reference['path']) if r.get('seed_id') == reference['record_id'])
                source = {'family': 'public-seed-json', 'source_record_id': reference['record_id'],
                          'source_title': record['title'],
                          'abstracts': abstract_fields({'abstract': [record.get('abstract', '')]}),
                          'locator': {'path': reference['path'], 'record_id': reference['record_id']}}
                titles.append(record['title'])
                if record.get('identifiers', {}).get('doi'):
                    dois.append(record['identifiers']['doi'])
            elif catalog == 'paper-summary-public':
                record = self.catalog(reference['path'])[0]
                self.read(record['path'], record['sha256'])
                source = {'family': 'author-page-evidence-json', 'source_record_id': reference['record_id'],
                          'abstracts': [], 'locator': {'path': reference['path'], 'page_path': record['path']},
                          'reason': 'The bound author page contains bibliography and version links, with no abstract section.'}
            else:
                raise ValueError('Unrecognized source catalog: ' + catalog)
            if reference.get('record_sha256') and object_sha(record) != reference['record_sha256']:
                raise ValueError('Catalog record hash mismatch: ' + reference['record_id'])
            sources.append(source)
        for key in sorted({doi_key(d) for d in dois}):
            for relative, provider, envelope in self.cache_index.get(key, []):
                source = cache_record(envelope, provider, titles, dois)
                source['locator'] = {'path': relative, 'sha256': self.source_hashes[relative],
                                     'url': envelope.get('endpoint')}
                sources.append(source)
        for relative, record in self.page_index.get(paper['paper_id'], []):
            text = self.read(record['capture_path'], record['capture_sha256']).decode('utf-8-sig')
            abstract = page_abstract(text)
            if not record.get('identity_evidence') or abstract != record['abstract']:
                raise ValueError('Captured page identity or abstract disagrees with receipt')
            sources.append({'family': 'captured-page', 'source_record_id': paper['paper_id'],
                            'locator': {'path': relative, 'capture_path': record['capture_path'],
                                        'capture_sha256': record['capture_sha256'], 'url': record['url']},
                            'identity_evidence': record['identity_evidence'],
                            'abstracts': [{'field': 'Abstract section', 'text': abstract}] if abstract else []})
        if paper.get('local_candidates') and not any(s['abstracts'] for s in sources):
            for candidate in paper['local_candidates']:
                data = self.read(candidate['path'], candidate['sha256'])
                if not data.startswith(b'%PDF-'):
                    raise ValueError('Local PDF signature mismatch')
                source = {'family': 'local-pdf', 'abstracts': [],
                          'locator': {'path': candidate['path'], 'sha256': candidate['sha256']},
                          'reason': 'No bounded abstract was identified in the inspected local document; further source reading may be needed.'}
                fulltext = paper.get('fulltext', {})
                extraction = fulltext.get('extraction', {})
                if fulltext.get('sha256') == candidate['sha256'] and extraction.get('text_path'):
                    text = self.read(extraction['text_path'], extraction['text_sha256']).decode('utf-8-sig')
                    if re.search(r'(?im)^\s*(?:#+\s*)?abstract\s*[:.]?\s*$', text):
                        raise ValueError('Local Abstract boundary needs an extractor: ' + candidate['path'])
                    source['text_path'] = extraction['text_path']
                    source['reason'] = 'Stored fulltext has no explicit Abstract heading; this is not proof that the publication has no abstract.'
                sources.append(source)
        return sources


    def path(self, relative):
        path = (self.base / relative).resolve()
        if not path.is_relative_to(self.base):
            raise ValueError('Source outside baseline')
        return path

    @lru_cache(maxsize=None)
    def export(self, relative, source_id, expected):
        data = checked_bytes(self.path(relative), expected)
        self.source_hashes[relative] = hashlib.sha256(data).hexdigest()
        return read_export(data.decode('utf-8-sig'), source_id)

    def export_sources(self, paper, family=None):
        sources = []
        for reference in paper['source_records']:
            if reference['catalog'] != 'B001':
                continue
            record = self.b001[reference['record_id']]
            if object_sha(record) != reference['record_sha256']:
                raise ValueError('Catalog record hash mismatch: ' + reference['record_id'])
            if family == 'scopus-csv' and record['source_id'] != 'scopus':
                continue
            for locator in record['provenance']:
                rows = self.export(locator['path'], record['source_id'], locator['artifact_sha256'])
                row = bound_record(rows, locator['rank'], record['source_record_id'])
                sources.append({'family': row['family'], 'source_record_id': row['id'],
                                'source_title': row['title'], 'locator': locator,
                                'catalog_record_id': record['candidate_id'],
                                'parse_warning': row.get('parse_warning'),
                                'abstracts': abstract_fields(row['fields'])})
        return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    run_parser = commands.add_parser('run', help='Replay the first-item algorithm into a fresh directory')
    run_parser.add_argument('--output', type=Path, required=True)
    commands.add_parser('verify', help='Verify all saved groups, source hashes and queue conservation')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    if args.command == 'run':
        output = args.output.resolve()
        if output.exists():
            parser.error('Output must be a new directory; existing results are preserved')
        if not output.is_relative_to(BASE):
            parser.error('Output must be inside the literature-baseline directory')
        output.mkdir(parents=True)
        for name in ['partition.py', 'input.jsonl']:
            shutil.copyfile(folder / name, output / name)
        shutil.copyfile(folder / 'input.jsonl', output / 'remaining.jsonl')
        repository = Repository(BASE)
        run_all(output, repository.sources)
        write_jsonl(output / 'source-hashes.jsonl', [{'path': key, 'sha256': value}
                    for key, value in sorted(repository.source_hashes.items())])
        folder = output
    report = verify_partition(folder)
    source_errors = []
    for record in read_jsonl(folder / 'source-hashes.jsonl'):
        try:
            checked_bytes(BASE / record['path'], record['sha256'])
        except (OSError, ValueError) as exc:
            source_errors.append(str(exc))
    report['source_hash_errors'] = source_errors
    report['passed'] = report['passed'] and not source_errors
    (folder / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'groups'}, ensure_ascii=False))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
