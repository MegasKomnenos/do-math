import copy
import json
import unittest
import recover as r
import fulltext_scope

def record(pid):
    return json.loads((r.ROOT/'tdd/fixtures'/f'{pid}-source-scope.json').read_text(encoding='utf-8'))

class FulltextScopeTests(unittest.TestCase):
    def test_actual_jstor_captcha_is_limitation_not_absence(self):
        x=record('VER-1aad75ee74ec137660f79887')
        self.assertEqual(fulltext_scope.assess(x)['status'],'unavailable')

    def test_pending_source_prevents_terminal_review(self):
        x=record('VER-1aad75ee74ec137660f79887')
        x['work_state']['tasks'].append({'kind':'source','status':'pending','target':'unvisited'})
        self.assertIsNone(fulltext_scope.assess(x))

    def test_google_catalogue_and_empty_resolver_do_not_supply_fulltext(self):
        x=record('VER-0adb4adf5b422dd3cf1ae5e3')
        self.assertEqual(fulltext_scope.assess(x)['status'],'not_found')

    def test_unreadable_proof_cannot_close_scope(self):
        x=record('VER-1aad75ee74ec137660f79887')
        next(t for t in x['work_state']['tasks'] if t['kind']=='source' and t['target']!='MathSciNet detail')['evidence_paths']=[]
        self.assertIsNone(fulltext_scope.assess(x))

    def test_sciencedirect_cpe_requires_new_browser_path(self):
        self.assertIsNone(fulltext_scope.classify({'url':'https://www.sciencedirect.com','text':'CPE00001 Content providing error','links':[]}))

if __name__=='__main__':unittest.main()
