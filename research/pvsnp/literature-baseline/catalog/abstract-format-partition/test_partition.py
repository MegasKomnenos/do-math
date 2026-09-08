import csv
import io
import json
import re
from pathlib import Path
import unittest
import tempfile
import subprocess
import sys

import partition as p

BASE = Path(__file__).resolve().parents[2]


class ScopusTests(unittest.TestCase):
    def test_long_export_field_is_not_truncated(self):
        text = 'Long text. ' * 20000
        raw = 'EID,Title,Abstract,Source\n2-s2.0-1,Title,' + text + ',Scopus\n'
        try:
            records = p.read_export(raw, 'scopus')
        except csv.Error as exc:
            self.fail('Valid long export field was rejected: ' + str(exc))
        self.assertEqual(records[0]['fields']['abstract'], [text])

    def test_actual_first_record(self):
        paper = json.loads((Path(__file__).parent / 'input.jsonl').read_text(encoding='utf-8').splitlines()[0])
        locator = paper['source_records'][0]['provenance'][0]
        raw = (BASE / locator['path']).read_text(encoding='utf-8-sig')
        rows = p.read_export(raw, 'scopus')
        self.assertGreaterEqual(len(rows), locator['rank'], 'The export must expose the first candidate row')
        row = rows[locator['rank'] - 1]
        self.assertEqual(row['id'], '2-s2.0-85122848425')
        expected = list(csv.DictReader(io.StringIO(raw)))[locator['rank'] - 1]['Abstract']
        self.assertTrue(expected.startswith('The events and processes of the recent decades'))
        self.assertTrue(expected.endswith('All rights reserved.'))
        self.assertEqual(p.abstract_fields(row['fields']), [{'field': 'abstract', 'text': expected}])

    def test_csv_quotes_multiline_unicode_and_inequalities(self):
        stream = io.StringIO(newline='')
        csv.writer(stream).writerows([
            ['EID', 'Title', 'Abstract', 'Source'],
            ['2-s2.0-1', '한글', 'For x < y, "yes".\nAnd y > z.', 'Scopus']])
        rows = p.read_export('\ufeff' + stream.getvalue(), 'scopus')
        self.assertEqual(len(rows), 1)
        self.assertEqual(p.abstract_fields(rows[0]['fields'])[0]['text'], 'For x < y, "yes".\nAnd y > z.')

    def test_absence_markers_are_not_abstracts(self):
        for value in ['', ' ', '[No abstract available]', 'No abstract available.', 'N/A', 'Abstract', '...']:
            with self.subTest(value=value):
                self.assertEqual(p.abstract_fields({'abstract': [value]}), [])

    def test_real_sentence_containing_absence_words_is_kept(self):
        value = 'No abstract model is available for these data.'
        self.assertEqual(p.abstract_fields({'abstract': [value]}), [{'field': 'abstract', 'text': value}])

    def test_title_keyword_and_reference_are_not_abstracts(self):
        self.assertEqual(p.abstract_fields({'title': ['Abstract algebra'], 'keywords': ['abstract'],
                                          'references': ['AB - A cited abstract']}), [])

    def test_other_csv_is_not_scopus(self):
        with self.assertRaises(ValueError):
            p.read_export('Title,Abstract\nTitle,Wrong\n', 'scopus')

    def test_damaged_csv_rejected(self):
        for raw in ['EID,Title,Abstract,Source\nx,t,a,Scopus,extra\n',
                    'EID,Title,Abstract,Source\nx,t\n',
                    'EID,Title,Abstract,Abstract,Source\nx,t,a,b,Scopus\n']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                p.read_export(raw, 'scopus')

    def test_wrong_rank_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            p.bound_record([{'id': 'other'}], 1, 'expected')

    def test_bad_rank_is_rejected(self):
        for rank in [0, -1, 2, True, '1']:
            with self.subTest(rank=rank), self.assertRaises(ValueError):
                p.bound_record([{'id': 'expected'}], rank, 'expected')


class PartitionTests(unittest.TestCase):
    def test_repository_exposes_source_readers(self):
        for name in ['path', 'export', 'export_sources', 'sources']:
            self.assertTrue(callable(getattr(p.Repository, name, None)), name)

    def test_all_same_format_sources_match_even_if_not_preferred(self):
        rows = [{'paper_id': 'a'}, {'paper_id': 'b'}, {'paper_id': 'c'}]
        decisions = {
            'a': p.choose([{'family': 'bib', 'abstracts': [{'text': 'A'}]}]),
            'b': p.choose([{'family': 'ris', 'abstracts': [{'text': 'B'}]},
                           {'family': 'bib', 'abstracts': [{'text': 'C'}]}]),
            'c': p.choose([{'family': 'bib', 'abstracts': []}])}
        removed, remaining = p.partition_step(rows, decisions, 'bib', 'extracted')
        self.assertEqual(removed, rows[:2])
        self.assertEqual(remaining, rows[2:])

    def test_deferred_group_also_checks_nonpreferred_format(self):
        rows = [{'paper_id': 'a'}, {'paper_id': 'b'}]
        decisions = {'a': p.choose([{'family': 'fields', 'abstracts': []}]),
                     'b': p.choose([{'family': 'bib', 'abstracts': []}, {'family': 'fields', 'abstracts': []}])}
        removed, remaining = p.partition_step(rows, decisions, 'fields', 'needs-source')
        self.assertEqual(removed, rows)
        self.assertEqual(remaining, [])

    def test_step_persists_members_abstracts_script_and_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = '{"paper_id": "a"}\n{"paper_id": "b"}\n'
            (folder / 'remaining.jsonl').write_text(original, encoding='utf-8')
            decisions = {'a': {'family': 'csv', 'outcome': 'extracted',
                               'sources': [{'family': 'csv', 'abstracts': [{'field': 'abstract', 'text': 'Exact text.'}]}]}}
            p.save_step(folder, decisions, 'csv', 'extracted')
            groups = list((folder / 'groups').glob('*')) if (folder / 'groups').exists() else []
            self.assertEqual(len(groups), 1)
            self.assertEqual((groups[0] / 'members.jsonl').read_text(), '{"paper_id": "a"}\n')
            self.assertEqual((folder / 'remaining.jsonl').read_text(), '{"paper_id": "b"}\n')
            self.assertTrue((groups[0] / 'format.py').exists())
            abstract = p.read_jsonl(groups[0] / 'abstracts.jsonl')[0]
            self.assertEqual(abstract['text'], 'Exact text.')
            self.assertEqual(abstract['paper_id'], 'a')
            iteration = p.read_jsonl(folder / 'iterations.jsonl')[0]
            self.assertEqual((iteration['first_paper_id'], iteration['removed'], iteration['remaining']), ('a', 1, 1))

    def test_remove_all_matches_preserving_order_and_contents(self):
        rows = [{'paper_id': 'a'}, {'paper_id': 'b'}, {'paper_id': 'c'}]
        decisions = {'a': {'family': 'csv', 'outcome': 'extracted'},
                     'b': {'family': 'ris', 'outcome': 'extracted'},
                     'c': {'family': 'csv', 'outcome': 'extracted'}}
        removed, remaining = p.partition_step(rows, decisions, 'csv', 'extracted')
        self.assertEqual(removed, [rows[0], rows[2]])
        self.assertEqual(remaining, [rows[1]])

    def test_first_item_must_belong_to_requested_group(self):
        with self.assertRaises(ValueError):
            p.partition_step([{'paper_id': 'a'}], {}, 'csv', 'extracted')

    def test_duplicate_paper_ids_are_not_silently_merged(self):
        with self.assertRaises(ValueError):
            p.partition_step([{'paper_id': 'a'}, {'paper_id': 'a'}],
                             {'a': {'family': 'csv', 'outcome': 'extracted'}}, 'csv', 'extracted')

    def test_no_abstract_and_other_formats_are_not_removed_as_success(self):
        rows = [{'paper_id': str(i)} for i in range(4)]
        decisions = {'0': {'family': 'csv', 'outcome': 'extracted'},
                     '1': {'family': 'csv', 'outcome': 'needs-source'},
                     '2': {'family': 'ris', 'outcome': 'extracted'}}
        removed, remaining = p.partition_step(rows, decisions, 'csv', 'extracted')
        self.assertEqual(removed, rows[:1])
        self.assertEqual(remaining, rows[1:])

    def test_bound_source_hash_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'raw'
            path.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                p.checked_bytes(path, '0' * 64)

    def test_repository_reads_actual_source_with_identity(self):
        paper = json.loads((Path(__file__).parent / 'input.jsonl').read_text(encoding='utf-8').splitlines()[0])
        repository = p.Repository(BASE)
        sources = repository.export_sources(paper, 'scopus-csv')
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]['source_record_id'], '2-s2.0-85122848425')
        self.assertEqual(sources[0]['family'], 'scopus-csv')
        self.assertTrue(sources[0]['abstracts'][0]['text'].startswith('The events and processes'))


class MetadataTests(unittest.TestCase):
    def test_title_markup_does_not_hide_same_doi_abstract(self):
        for raw_title, title in [('On <i>k</i>-Hulls and Related Problems', 'On k-hulls and related problems'),
                                 ("Bak's work on the<i>K</i>-theory of rings", "Bak's work on the K-theory of rings")]:
            with self.subTest(raw_title=raw_title):
                envelope = {'message': {'DOI': '10.1/x', 'title': [raw_title], 'abstract': 'Actual abstract.'}}
                self.assertEqual(p.cache_record(envelope, 'crossref', [title], ['10.1/x'])['abstracts'],
                                 [{'field': 'message.abstract', 'text': 'Actual abstract.'}])

    def test_empty_or_placeholder_jats_is_not_an_abstract(self):
        for value in ['<jats:abstract/>', '<jats:abstract><jats:title>Abstract</jats:title></jats:abstract>',
                      '<p>[No abstract available]</p>']:
            with self.subTest(value=value):
                self.assertEqual(p.abstract_fields({'abstract': [value]}), [])

    def test_actual_next_mathscinet_record_has_no_abstract(self):
        rows = p.read_jsonl(BASE / 'catalog/B002-candidates.jsonl')
        record = next(r for r in rows if r['candidate_id'] == 'MR2499435')
        source = p.field_record(record)
        self.assertEqual(source.get('family'), 'mathscinet-fields-json')
        self.assertEqual(source['abstracts'], [])

    def test_field_aliases_repeated_values_and_case(self):
        record = {'candidate_id': 'MR1', 'schema_version': 'pvsnp-literature-candidate/1',
                  'fields': [{'name': 'TITLE', 'value': 'A title'}, {'name': 'N2', 'value': 'First abstract.'},
                             {'name': 'N2', 'value': 'Second abstract.'}]}
        source = p.field_record(record)
        self.assertEqual(source.get('abstracts'), [{'field': 'n2', 'text': 'First abstract.'},
                                                 {'field': 'n2', 'text': 'Second abstract.'}])

    def test_crossref_abstract_only_and_jats_preserved(self):
        abstract = '<jats:abstract><jats:p>For x &lt; y, O(n<jats:sup>2</jats:sup>).</jats:p></jats:abstract>'
        envelope = {'http_status': 200, 'doi': '10.1/x', 'response_text': json.dumps({'message': {
            'DOI': '10.1/x', 'title': ['Title'], 'abstract': abstract,
            'reference': [{'abstract': 'Wrong abstract.'}]}})}
        source = p.cache_record(envelope, 'crossref', ['Title'], ['10.1/x'])
        self.assertEqual(source.get('family'), 'crossref-json')
        self.assertEqual(source['abstracts'], [{'field': 'message.abstract', 'text': abstract}])

    def test_cache_title_and_doi_both_must_match(self):
        e = {'message': {'DOI': '10.1/x', 'title': ['Other'], 'abstract': 'Wrong paper.'}}
        source = p.cache_record(e, 'crossref', ['Title'], ['10.1/x'])
        self.assertEqual(source.get('abstracts'), [])
        self.assertEqual(source.get('reason'), 'identity-mismatch')
        e['message']['title'] = ['Title']
        self.assertEqual(p.cache_record(e, 'crossref', ['Title'], ['10.1/y']).get('abstracts'), [])

    def test_split_title_and_subtitle_match(self):
        e = {'message': {'DOI': '10.1/x', 'title': ['Title'], 'subtitle': ['A subtitle'], 'abstract': 'Actual abstract.'}}
        self.assertEqual(p.cache_record(e, 'crossref', ['Title: A subtitle'], ['10.1/x']).get('abstracts'),
                         [{'field': 'message.abstract', 'text': 'Actual abstract.'}])

    def test_crossref_reference_is_not_top_level_abstract(self):
        e = {'message': {'DOI': '10.1/x', 'title': ['Title'], 'reference': [{'abstract': 'Wrong.'}]}}
        self.assertEqual(p.cache_record(e, 'crossref', ['Title'], ['10.1/x']).get('abstracts'), [])

    def test_failed_request_not_success_even_with_response_body(self):
        e = {'http_status': 403, 'message': {'DOI': '10.1/x', 'title': ['Title'], 'abstract': 'Denied'}}
        source = p.cache_record(e, 'crossref', ['Title'], ['10.1/x'])
        self.assertEqual(source.get('abstracts'), [])
        self.assertEqual(source.get('reason'), 'http-403')

    def test_datacite_only_abstract_description(self):
        e = {'data': {'attributes': {'doi': '10.1/x', 'titles': [{'title': 'Title'}], 'descriptions': [
            {'descriptionType': 'Other', 'description': 'Not an abstract'},
            {'descriptionType': 'Abstract', 'description': 'Actual abstract.'}]}}}
        source = p.cache_record(e, 'datacite', ['Title'], ['10.1/x'])
        self.assertEqual(source.get('abstracts'), [{'field': 'descriptions[1]', 'text': 'Actual abstract.'}])

    def test_corrupt_response_hash_rejected(self):
        with self.assertRaises(ValueError):
            p.cache_record({'http_status': 200, 'response_text': '{}', 'response_sha256': '0' * 64},
                           'crossref', [], [])

    def test_choose_local_abstract_before_deferring(self):
        sources = [{'family': 'mathscinet-fields-json', 'abstracts': []},
                   {'family': 'crossref-json', 'abstracts': [{'field': 'abstract', 'text': 'Actual.'}]}]
        choice = p.choose(sources)
        self.assertEqual((choice.get('family'), choice.get('outcome')), ('crossref-json', 'extracted'))

    def test_defer_retains_actual_format_and_reason(self):
        choice = p.choose([{'family': 'mathscinet-fields-json', 'abstracts': []}])
        self.assertEqual((choice.get('family'), choice.get('outcome')),
                         ('mathscinet-fields-json', 'needs-source'))


class ExportTests(unittest.TestCase):
    def test_actual_first_pending_ris_abstract(self):
        papers = p.read_jsonl(Path(__file__).parent / 'input.jsonl')
        paper = next(r for r in papers if r['paper_id'] == 'VER-007a2b0a66a599e781f9b1f9')
        ref = paper['source_records'][0]
        locator = ref['provenance'][0]
        raw = (BASE / locator['path']).read_text(encoding='utf-8-sig')
        block = re.split(r'(?m)^ER  -[^\n]*\n?', raw)[locator['rank'] - 1]
        expected = re.search(r'(?ms)^AB  - ?(.*?)(?=\n[A-Z0-9]{2}  -|\Z)', block).group(1).strip()
        self.assertTrue(expected.startswith('English:Given the numerous challenges'))
        row = self.parse(raw, locator['source_id'])[locator['rank'] - 1]
        self.assertEqual(p.abstract_fields(row['fields']), [{'field': 'ab', 'text': expected}])

    def parse(self, raw, provider):
        try:
            return p.read_export(raw, provider)
        except ValueError as exc:
            self.fail('Supported export rejected: ' + str(exc))

    def test_ris_multiline_repeated_tags_and_alias(self):
        raw = 'TY  - JOUR\nUT  - WOS:1\nTI  - Title\nAB  - First line.\nSecond line.\nN2  - Another abstract.\nER  -\n'
        records = self.parse(raw, 'wos')
        self.assertEqual(records[0]['id'], 'WOS:1')
        self.assertEqual(p.abstract_fields(records[0]['fields']), [
            {'field': 'ab', 'text': 'First line.\nSecond line.'}, {'field': 'n2', 'text': 'Another abstract.'}])

    def test_ris_reference_and_missing_terminator(self):
        records = self.parse('TY  - THES\nAN  - 123\nT1  - Title\nCR  - AB - Cited text\nER  -\n', 'pqdt')
        self.assertEqual(records[0]['id'], '123')
        self.assertEqual(p.abstract_fields(records[0]['fields']), [])
        with self.assertRaises(ValueError):
            p.read_export('TY  - JOUR\nAB  - Truncated\n', 'wos')

    def test_bibtex_nested_braces_quoted_fields_and_inline_entries(self):
        raw = '@article{x, title="Title", abstract={For {nested} values, @article{fake} is text.}, doi={10.1/x}}'
        records = self.parse(raw, 'acm-dl')
        self.assertEqual(len(records), 1)
        self.assertEqual(p.abstract_fields(records[0]['fields']), [
            {'field': 'abstract', 'text': 'For {nested} values, @article{fake} is text.'}])

    def test_field_like_line_inside_bibtex_abstract_is_not_field(self):
        raw = '@article{x,\ntitle={Title},\nabstract={First.\nkeywords = {still abstract}\nLast.},\nyear={2000}\n}'
        records = self.parse(raw, 'acm-dl')
        self.assertEqual(p.abstract_fields(records[0]['fields'])[0]['text'],
                         'First.\nkeywords = {still abstract}\nLast.')

    def test_actual_acm_ieee_and_mathscinet_exports(self):
        examples = [
            ('intake/B001/acm-dl/A03/acm (2).bib', 'acm-dl', 450, '10.1145/3651151', 'bibtex', True),
            ('intake/B001/ieee-xplore/I01/IEEE Xplore Citation BibTeX Download 2026.9.4.15.42.2.bib',
             'ieee-xplore', 1, '8204814', 'bibtex', True),
            ('intake/B001/mathscinet/M01/export', 'mathscinet', 1, 'MR1251285', 'mathscinet-bibtex', False)]
        for relative, provider, rank, identity, family, available in examples:
            with self.subTest(relative=relative):
                records = self.parse((BASE / relative).read_text(encoding='utf-8-sig'), provider)
                row = p.bound_record(records, rank, identity)
                self.assertEqual(row['family'], family)
                self.assertEqual(bool(p.abstract_fields(row['fields'])), available)

    def test_damaged_acm_abstract_keeps_both_paragraphs_and_stops_before_booktitle(self):
        raw = (BASE / 'intake/B001/acm-dl/A02/acm (1).bib').read_text(encoding='utf-8-sig')
        row = self.parse(raw, 'acm-dl')[111]
        self.assertEqual(row['id'], '10.4230/LIPIcs.CCC.2025.32')
        expected = raw.split('abstract = {Random Δ-CNF formulas', 1)[1].split('},\nbooktitle =', 1)[0]
        self.assertEqual(p.abstract_fields(row['fields'])[0]['text'], 'Random Δ-CNF formulas' + expected)
        self.assertTrue(row.get('parse_warning'))


class PageTests(unittest.TestCase):
    def test_inline_web_line_numbers_and_end_boundary(self):
        text = 'L1: # Title L2: ## Abstract L3: First paragraph. L4: Second paragraph. L5: ## References L6: Wrong.'
        self.assertEqual(p.page_abstract(text), 'First paragraph.\nSecond paragraph.')

    def test_missing_end_boundary_is_not_complete_abstract(self):
        self.assertEqual(p.page_abstract('L1: ## Abstract\nL2: Truncated text'), '')

    def test_navigation_abstract_word_is_not_section(self):
        self.assertEqual(p.page_abstract('Abstract\nA search snippet.\n## References'), '')

    def test_actual_three_captured_pages(self):
        for file in sorted((BASE / 'intake/abstract-recovery/pages').glob('*.json')):
            with self.subTest(file=file.name):
                record = json.loads(file.read_text(encoding='utf-8'))
                text = (BASE / record['capture_path']).read_text(encoding='utf-8')
                self.assertEqual(p.page_abstract(text), record['abstract'])


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository = p.Repository(BASE)
        cls.papers = {r['paper_id']: r for r in p.read_jsonl(Path(__file__).parent / 'input.jsonl')}

    def test_next_candidate_is_deferred_only_after_cached_metadata_check(self):
        sources = self.repository.sources(self.papers['VER-00076a8018bfd0fedd6121ad'])
        self.assertIn('mathscinet-fields-json', [s['family'] for s in sources])
        self.assertIn('crossref-json', [s['family'] for s in sources])
        self.assertEqual(p.choose(sources)['outcome'], 'needs-source')

    def test_page_can_supply_abstract_missing_in_primary_metadata(self):
        sources = self.repository.sources(self.papers['VER-8a23b7cd72b2672b87945837'])
        self.assertTrue(any(s['family'] == 'captured-page' and s['abstracts'] for s in sources))

    def test_discovery_evidence_is_not_an_abstract(self):
        sources = self.repository.sources(self.papers['VER-c654aca561b693097c66a740'])
        self.assertTrue(sources)
        self.assertTrue(any(s['family'] == 'author-page-evidence-json' for s in sources))
        self.assertFalse(any(s['abstracts'] for s in sources))


    def test_local_originals_are_included_in_no_abstract_evidence(self):
        sources = self.repository.sources(self.papers['VER-112ef81e47937307790fd36e'])
        self.assertTrue(any(s['family'] == 'local-pdf' for s in sources))
        self.assertFalse(any(s['abstracts'] for s in sources))


class ReplayTests(unittest.TestCase):
    def test_group_recognizer_filters_mixed_actual_records(self):
        papers = p.read_jsonl(Path(__file__).parent / 'input.jsonl')
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'mixed.jsonl'
            p.write_jsonl(source, [papers[0], papers[2]])
            script = Path(__file__).parent / 'groups/01-extracted-scopus-csv/format.py'
            result = subprocess.run([sys.executable, str(script), '--recognize', '--input', str(source)],
                                    capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([json.loads(line)['paper_id'] for line in result.stdout.splitlines()], [papers[0]['paper_id']])

    def test_cli_explains_commands(self):
        result = subprocess.run([sys.executable, str(Path(__file__).parent / 'partition.py'), '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('run', result.stdout)
        self.assertIn('verify', result.stdout)

    def test_cli_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / 'keep.txt').write_text('Keep this.', encoding='utf-8')
            result = subprocess.run([sys.executable, str(Path(__file__).parent / 'partition.py'),
                                     'run', '--output', tmp], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((path / 'keep.txt').read_text(), 'Keep this.')

    def fixture(self, folder):
        rows = [{'paper_id': 'a'}, {'paper_id': 'b'}, {'paper_id': 'c'}]
        p.write_jsonl(folder / 'input.jsonl', rows)
        p.write_jsonl(folder / 'remaining.jsonl', rows)
        return {'a': [{'family': 'csv', 'abstracts': [{'field': 'abstract', 'text': 'Actual.'}]}],
                'b': [{'family': 'fields', 'abstracts': []}],
                'c': [{'family': 'csv', 'abstracts': [{'field': 'abstract', 'text': 'Other.'}]}]}

    def test_run_terminates_and_verifies_complete_partition(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            sources = self.fixture(folder)
            p.run_all(folder, lambda row: sources[row['paper_id']])
            self.assertEqual((folder / 'remaining.jsonl').read_bytes(), b'')
            report = p.verify_partition(folder)
            self.assertEqual(report.get('passed'), True)
            self.assertEqual(report.get('input_count'), 3)
            self.assertEqual(report.get('extracted'), 2)
            self.assertEqual(report.get('needs_source'), 1)

    def test_verification_detects_missing_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            sources = self.fixture(folder)
            p.run_all(folder, lambda row: sources[row['paper_id']])
            groups = sorted((folder / 'groups').glob('*')) if (folder / 'groups').exists() else []
            self.assertEqual(len(groups), 2)
            (groups[0] / 'members.jsonl').write_text('{"paper_id": "a"}\n', encoding='utf-8')
            report = p.verify_partition(folder)
            self.assertFalse(report['passed'])
            self.assertTrue(report['false_negatives'])

    def test_verification_detects_changed_abstract(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            sources = self.fixture(folder)
            p.run_all(folder, lambda row: sources[row['paper_id']])
            groups = sorted((folder / 'groups').glob('*')) if (folder / 'groups').exists() else []
            self.assertEqual(len(groups), 2)
            abstracts = p.read_jsonl(groups[0] / 'abstracts.jsonl')
            abstracts[0]['text'] = 'Wrong paper.'
            p.write_jsonl(groups[0] / 'abstracts.jsonl', abstracts)
            report = p.verify_partition(folder)
            self.assertFalse(report['passed'])
            self.assertTrue(report['text_mismatches'])

    def test_saved_group_script_is_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            sources = self.fixture(folder)
            p.run_all(folder, lambda row: sources[row['paper_id']])
            groups = sorted((folder / 'groups').glob('*')) if (folder / 'groups').exists() else []
            self.assertEqual(len(groups), 2)
            environment = dict(__import__('os').environ)
            environment['PYTHONPATH'] = str(Path(__file__).parent)
            result = subprocess.run([sys.executable, str(groups[0] / 'format.py'), '--help'],
                                    capture_output=True, text=True, env=environment)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--extract', result.stdout)

if __name__ == '__main__':
    unittest.main()
