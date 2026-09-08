import unittest
import recover as r
import source_summary

class SourceSummaryTests(unittest.TestCase):
    def test_actual_complete_dynamic_models_source_quotation(self):
        import json
        record=json.loads((r.ROOT/'results/VER-4ddce9d9fb8c603eabfef37e.json').read_text(encoding='utf-8'))
        text=(r.BASE/record['review']['artifacts'][0]['path']).read_text(encoding='utf-8')
        value=source_summary.source_quote(text)
        self.assertTrue(value.startswith('This monograph considers four general types'))
        self.assertTrue(value.endswith('frequently recurring social phenomena.'))
        self.assertIsNone(source_summary.source_quote(text+'\nThe reviewer recommends the book.'))
        self.assertIsNone(source_summary.source_quote('Review\nAn excellent textbook.'))

if __name__=='__main__':unittest.main()
