import importlib.util,unittest
from pathlib import Path
from collect import BASE
ROOT=BASE/'intake/kudos-recovery/g05/VER-2bb97c857e10d1adb8a73f9a'
class FulltextHTMLTests(unittest.TestCase):
    def test_actual_complete_body_math_and_references_survive(self):
        parts={name:(ROOT/f'source-dom-{name}.html').read_text() for name in ['body','abstracts','author-group','bibliography']}
        if importlib.util.find_spec('fulltext_html'):
            import fulltext_html
            value=fulltext_html.document('Reachability in arborescence packings',parts)
        else:value=parts['abstracts']
        self.assertIn(parts['body'],value);self.assertIn(parts['bibliography'],value)
        self.assertEqual(value.count('<math'),1291)
        self.assertNotIn('Recommended articles',value)
        self.assertIn('<meta charset="utf-8">',value)
    def test_equation_label_is_inside_visible_formula_in_offline_browser(self):
        import tempfile,fulltext_html
        from playwright.sync_api import sync_playwright
        parts={name:(ROOT/f'source-dom-{name}.html').read_text() for name in ['body','abstracts','author-group','bibliography']}
        with tempfile.TemporaryDirectory(dir=BASE/'kudos-recovery/g05/tdd') as folder:
            file=Path(folder)/'article.html';file.write_text(fulltext_html.document('Target',parts),encoding='utf-8')
            with sync_playwright() as pw:
                browser=pw.firefox.launch(headless=True);page=browser.new_page(offline=True);page.goto(file.as_uri())
                formula=page.locator('.formula').first.bounding_box();label=page.locator('.formula > .label').first.bounding_box()
                browser.close()
            self.assertGreaterEqual(label['y'],formula['y']-1)
            self.assertLessEqual(label['y']+label['height'],formula['y']+formula['height']+1)
            self.assertLessEqual(label['x']+label['width'],formula['x']+formula['width']+1)
    def test_locally_embedded_actual_article_figure_is_allowed(self):
        import base64,fulltext_html
        image=(BASE/'intake/kudos-recovery/g05/VER-022f997d68492e3705be19c6/article-observed-figure-48b71ddae3806c45.jpg').read_bytes()
        uri='data:image/jpeg;base64,'+base64.b64encode(image).decode()
        value=fulltext_html.document('Target',{'body':'<img src="'+uri+'">','bibliography':'References'})
        self.assertIn(uri,value)
    def test_uncaptured_external_figure_cannot_be_a_self_contained_original(self):
        import fulltext_html
        parts={'body':'<section><img src="https://observed.example/figure.png"></section>','bibliography':'References','abstracts':'Abstract','author-group':'Authors'}
        with self.assertRaisesRegex(ValueError,'resource'):fulltext_html.document('Target',parts)
if __name__=='__main__':unittest.main()
