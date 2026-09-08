import unittest
from pathlib import Path
import recovery

class RecoveryTests(unittest.TestCase):
    def test_doi_case_url(self):
        self.assertEqual(recovery.doi_key('https://doi.org/10.1109/MCS.2008.931718'), '10.1109/mcs.2008.931718')
    def test_wrong_article_rejected(self):
        self.assertFalse(recovery.identity_matches({'paper_id':'a','title':'hybrid dynamical systems','identifiers':{'doi':['10.1109/mcs.2008.931718']}},'unrelated article','https://doi.org/10.1000/other'))
    def test_actual_mr_identity(self):
        body=(Path(__file__).parent.parent.parent/'intake/kudos-recovery/g02/fixtures/mr2499435.txt').read_text(encoding='utf-8')
        self.assertTrue(recovery.identity_matches({'title':'hybrid dynamical systems robust stability and control for systems that combine continuous time and discrete time dynamics','identifiers':{'doi':['10.1109/mcs.2008.931718']}},body,'https://doi-org.libproxy.knu.ac.kr/10.1109/MCS.2008.931718'))
    def test_excerpt_not_abstract(self):
        body=(Path(__file__).parent.parent.parent/'intake/kudos-recovery/g02/fixtures/mr2499435.txt').read_text(encoding='utf-8')
        self.assertEqual(recovery.review_kind(body),'text-excerpt')
    def test_actual_traffic_block(self):
        self.assertEqual(recovery.barrier((Path(__file__).parent.parent.parent/'intake/kudos-recovery/g02/fixtures/ieee418.txt').read_text(encoding='utf-8')),'traffic-restriction')
    def test_html_not_pdf(self):
        self.assertFalse(recovery.pdf_valid(b'<html>Login</html>'))
    def test_login_required(self):
        self.assertEqual(recovery.barrier('Please log in to access this content'),'login-required')
    def test_resume_preserves_complete(self):
        self.assertFalse(recovery.needs_work({'identity':{'status':'confirmed'},'abstract':{'status':'found'},'fulltext':{'status':'unavailable'}}))
        self.assertTrue(recovery.needs_work({'identity':{'status':'confirmed'},'abstract':{'status':'unresolved'},'fulltext':{'status':'unavailable'}}))

if __name__=='__main__': unittest.main()
