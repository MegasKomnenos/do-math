import importlib.util,json,unittest
from collect import BASE
ROOT=BASE/'intake/kudos-recovery/g05/VER-0500a5b14fb9aea2d4cf5f0f'
class SavedArticleTests(unittest.TestCase):
    def test_actual_saved_math_inputs_restore_reference_and_title_structure(self):
        observed=json.loads((ROOT/'article-source-observation.json').read_text())
        if importlib.util.find_spec('saved_article'):
            from saved_article import restore_saved_math
        else:restore_saved_math=lambda value,proof:value
        for part in ['bibliography','abstracts','title_html']:
            raw=(ROOT/f'article-source-{part}.html').read_text();proof=observed['math_recovery'][part]
            value=restore_saved_math(raw,proof)
            self.assertNotIn('<mjx-container',value)
            for item in proof['math_inputs']:self.assertIn(item['math'],value)
            with self.assertRaises(ValueError):restore_saved_math(raw,dict(proof,math_inputs=[]))
if __name__=='__main__':unittest.main()
