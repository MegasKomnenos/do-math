import importlib.util
import unittest
import fitz
import recover as r

class ArticleRegionTests(unittest.TestCase):
    def test_real_vakil_issue_excludes_lenstra_and_keeps_seven_article_pages(self):
        self.assertIsNotNone(importlib.util.find_spec('article_region'))
        import article_region
        source=r.BASE/'intake/kudos-recovery/g08/VER-314684f8fca9344b61ba09da/linked-source-67ecf31c13106a80.pdf'
        data=article_region.extract(source,25,31,500)
        with fitz.open(stream=data,filetype='pdf') as doc:
            self.assertEqual(len(doc),7)
            self.assertNotIn('Hendrik Lenstra',doc[0].get_text())
            self.assertIn('Algebraic Geometry and the Ongoing',doc[0].get_text())
            self.assertIn('Ravi Vakil',doc[0].get_text())
            self.assertIn('Bibliography',doc[-1].get_text())
            self.assertIn('30',doc[-1].get_text())

if __name__=='__main__':unittest.main()
