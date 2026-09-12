import csv
import io
import sys
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ServiceError
from scholarly import ArtifactStore
from scopus import displayed_query,filter_count_records,query_key


class ScopusQueryIdentity(unittest.TestCase):
    def csv_for(self,query):
        rows=list(csv.reader(io.StringIO((ROOT/'tests/fixtures/scopus-filter-counts.csv').read_text(encoding='utf-8-sig'))))
        rows[2]=['Your query : ('+query+')'];stream=io.StringIO();csv.writer(stream).writerows(rows)
        return stream.getvalue().encode()

    def test_distinct_word_and_exact_phrase_boundaries_cannot_identify_same_export(self):
        for actual,wrong in [('TITLE(alpha beta)','TITLE(alphabeta)'),
                             ('TITLE({alpha beta})','TITLE({alphabeta})'),
                             ('TITLE("alpha  beta")','TITLE("alpha beta")'),
                             (r'TITLE(alpha\ beta)',r'TITLE(alpha\beta)')]:
            with self.subTest(actual=actual),self.assertRaises(ServiceError):
                filter_count_records(self.csv_for(actual),wrong)

    def test_cosmetic_function_spacing_preserves_quoted_and_escaped_literals(self):
        self.assertEqual(query_key('TITLE ( alpha beta ) AND ( LIMIT-TO ( DOCTYPE , "ar" ) )'),
                         query_key('TITLE(alpha beta) AND(LIMIT-TO(DOCTYPE,"ar"))'))
        query=r'TITLE("a\" b") AND TITLE({a\} b})'
        self.assertEqual(filter_count_records(self.csv_for(query),query)['native_query'],query)

    def page_with_copy(self,current,hidden):
        page=MagicMock();page.locator.return_value.filter.return_value.all.return_value=[]
        copy=page.get_by_role.return_value.filter.return_value;copy.count.return_value=1
        page.evaluate.side_effect=lambda script:current if script=='window.__scholarlyCopiedQuery' else hidden if 'getModels' in script else None
        return page,copy

    def test_current_copy_is_used_even_when_hidden_models_match_old_base(self):
        current='TITLE(x)';page,copy=self.page_with_copy(current,[current,current+' AND ( LIMIT-TO ( DOCTYPE,"ar" ) )'])
        self.assertEqual(displayed_query(page,current),current)
        copy.click.assert_called_once()

    def test_current_copy_preserves_multiple_spaces_inside_a_phrase(self):
        current='TITLE("alpha  beta")';page,copy=self.page_with_copy(current,[])
        self.assertEqual(displayed_query(page,current),current)

    def test_multiple_visible_queries_are_ambiguous_when_copy_is_unavailable(self):
        page=MagicMock();page.get_by_role.return_value.filter.return_value.count.return_value=0
        page.locator.return_value.filter.return_value.all.return_value=[SimpleNamespace(inner_text=lambda:'TITLE(x)'),
            SimpleNamespace(inner_text=lambda:'TITLE(x) AND ( LIMIT-TO ( DOCTYPE,"ar" ) )')]
        with self.assertRaises(ServiceError):displayed_query(page,'TITLE(x)')

    def test_copy_interaction_failure_is_typed_for_search_partial_handling(self):
        from scopus import Scopus
        page,copy=self.page_with_copy('TITLE(x)',[])
        page.wait_for_function.side_effect=TimeoutError('private diagnostic details')
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ServiceError) as error:
                Scopus(ArtifactStore(folder),None).facet_count_export(page,'TITLE(x)',1,[])
        self.assertEqual(error.exception.result['code'],'export_interaction_failed')
        self.assertNotIn('private diagnostic',str(error.exception.result))


if __name__=='__main__':unittest.main()
