import importlib
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ServiceError


class WOSAdvancedContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod=importlib.import_module('browser_adapters')
        cls.adapter=cls.mod.WebOfScience(None,None)

    def test_native_analyze_candidates_are_exposed_as_copyable_facet_values(self):
        events=[{'key':'analyze','payload':{
            'DT.Value.6':{'Name':'DT','Values':[{'Key':'DT.ARTICLE','Value':16},{'Key':'DT.PROCEEDINGS PAPER','Value':1}]},
            'OA.Value.6':{'Name':'OA','Values':[{'Key':'OA.OPEN ACCESS','Value':2}]},
            'ECR.Value.6':{'Name':'ECR','Values':[{'Key':'ECR.Y','Value':1}]},
            'PEERREVIEW.Value.6':{'Name':'PEERREVIEW','Values':[{'Key':'PEERREVIEW.No','Value':18}]},
        }}]
        self.assertEqual(self.mod.wos_facet_candidates(events),[
            {'group':'DT','value':'DT.ARTICLE','label':'ARTICLE','count':16,'control_section':'DT'},
            {'group':'DT','value':'DT.PROCEEDINGS PAPER','label':'PROCEEDINGS PAPER','count':1,'control_section':'DT'},
            {'group':'OA','value':'OA.OPEN ACCESS','label':'Open Access','count':2,'control_section':'FB'},
            {'group':'ECR','value':'ECR.Y','label':'Enriched Cited References','count':1,'control_section':'FB'},
        ])

    def test_options_preserve_verified_sort_editions_and_facet_values(self):
        options=self.adapter.advanced_options({'sort':'citations-highest','editions':['CPCI-S'],'facets':['OA.OPEN ACCESS','DT.PROCEEDINGS PAPER']})
        self.assertEqual(options['sort'],('Citations: highest first','times-cited-descending'))
        self.assertEqual(options['editions'],[('CPCI-S','WOS.ISTP')])
        self.assertEqual(options['facets'],[('OA','OPEN ACCESS','OA.OPEN ACCESS'),('DT','PROCEEDINGS PAPER','DT.PROCEEDINGS PAPER')])
        self.assertEqual(self.adapter.advanced_options({'sort':'conference-title-asc'})['sort'],('Conference title: A to Z',None))
        for bad in ({'sort':'unknown'},{'editions':[]},{'editions':['MADE-UP']},{'facets':'OA.OPEN ACCESS'},{'facets':['OA.OPEN ACCESS','OA.OPEN ACCESS']}):
            with self.subTest(bad=bad),self.assertRaises(ServiceError):self.adapter.advanced_options(bad)

    def test_native_requests_must_retain_editions_facets_and_sort(self):
        self.assertEqual(self.adapter.validate_advanced_request({'search':{'editions':None},'retrieve':{'sort':'date-descending'}},
                                                               list(self.adapter.edition_values.values()),None),'date-descending')
        self.assertEqual(self.adapter.validate_advanced_request({'search':{'editions':None},'retrieve':{'sort':'provider-current-sort'}},
                                                               list(self.adapter.edition_values.values()),None),'provider-current-sort')
        self.adapter.validate_advanced_request({'search':{'editions':None},'retrieve':{'sort':'relevance'}},
                                               list(self.adapter.edition_values.values()),'relevance')
        self.adapter.validate_advanced_request({'search':{'editions':['WOS.ISTP']},'retrieve':{'sort':'relevance'}},
                                               ['WOS.ISTP'],'relevance')
        self.adapter.validate_refine_request({'qid':'current-qid','refines':[{'index':'OA','value':['OPEN ACCESS']},{'index':'DT','value':['PROCEEDINGS PAPER']}],
                                              'retrieve':{'sort':'relevance'}},
                                             [('OA','OPEN ACCESS','OA.OPEN ACCESS'),('DT','PROCEEDINGS PAPER','DT.PROCEEDINGS PAPER')],'relevance','current-qid')
        with self.assertRaises(ServiceError):
            self.adapter.validate_advanced_request({'search':{'editions':['WOS.SCI']},'retrieve':{'sort':'relevance'}},['WOS.ISTP'],'relevance')
        with self.assertRaises(ServiceError):
            self.adapter.validate_refine_request({'qid':'current-qid','refines':[{'index':'OA','value':['GOLD']}],'retrieve':{'sort':'relevance'}},
                                                 [('OA','OPEN ACCESS','OA.OPEN ACCESS')],'relevance','current-qid')
        with self.assertRaises(ServiceError):
            self.adapter.validate_refine_request({'refines':[{'index':'OA','value':['OPEN ACCESS']}],'retrieve':{'sort':'relevance'}},
                                                 [('OA','OPEN ACCESS','OA.OPEN ACCESS')],'relevance','current-qid')

    def test_result_qid_and_final_facets_are_bound_to_the_current_result(self):
        url='https://www.webofscience.com/wos/woscc/summary/current-qid/relevance/1'
        self.assertEqual(self.adapter.result_qid(url),'current-qid')
        with self.assertRaises(ServiceError):self.adapter.result_qid('https://www.webofscience.com/wos/woscc/advanced-search')
        final={'events':[{'key':'analyze','payload':{'DT.Value.6':{'Name':'DT','Values':[{'Key':'DT.ARTICLE','Value':1}]}}}]}
        self.assertEqual(self.adapter.final_facets(final),[{'group':'DT','value':'DT.ARTICLE','label':'ARTICLE','count':1,'control_section':'DT'}])

    def test_optional_requested_export_preserves_the_successful_plain_export(self):
        from unittest.mock import Mock
        adapter=self.mod.WebOfScience(None,None);adapter.export_records=Mock(side_effect=ServiceError('export_failed','failed',source_export={'ref':'raw'}))
        fallback={'ref':'plain'}
        exported,error=adapter.requested_export(Mock(),0,1,'bibtex',fallback,fallback)
        self.assertEqual(exported['code'],'export_failed')
        self.assertEqual(exported['source_export'],{'ref':'raw'})
        self.assertEqual(error['code'],'export_failed')

    def test_publication_search_accepts_advanced_options_before_opening_wos(self):
        gateway=Mock();gateway.open.side_effect=RuntimeError('opened')
        adapter=self.mod.WebOfScience(None,gateway)
        with self.assertRaisesRegex(RuntimeError,'opened'):
            adapter.search('TI=("P versus NP")',options={'sort':'date-newest','editions':['CPCI-S'],'facets':['OA.OPEN ACCESS']},limit=1)
        with self.assertRaisesRegex(RuntimeError,'opened'):
            adapter.search('TI=("P versus NP")',options={'facet_filters':{'publication_titles':['COMMUNICATIONS OF THE ACM']},
                                                         'facet_group':'languages','facet_query':'English'},limit=1)

    def test_friendly_collapsed_facet_options_do_not_expose_native_indices(self):
        options=self.adapter.advanced_options({'facet_filters':{'publication_titles':['COMMUNICATIONS OF THE ACM'],'languages':['English']},
                                               'facet_group':'publication_titles','facet_query':'computational'})
        self.assertEqual(options['facet_filters'],[
            ('publication_titles','SO','Publication Titles',['COMMUNICATIONS OF THE ACM']),
            ('languages','LA','Languages',['English'])])
        self.assertEqual(options['facet_preview'],('publication_titles','SO','Publication Titles','computational'))
        for bad in ({'facet_filters':[]},{'facet_filters':{'unknown':['x']}},{'facet_filters':{'languages':'English'}},
                    {'facet_filters':{'languages':[' English']}},{'facet_group':'unknown'},{'facet_query':'English'}):
            with self.subTest(bad=bad),self.assertRaises(ServiceError):self.adapter.advanced_options(bad)

    def test_control_candidates_keep_visible_labels_and_native_identity_separate(self):
        raw='''<div><input type="checkbox" name="SO" value="SO.COMPUTATIONAL COMPLEXITY" aria-label="COMPUTATIONAL COMPLEXITY, 1">
                 <input type="checkbox" name="OAJ" value="OAJ.BRONZE" aria-label="Free to Read, 3"></div>'''
        self.assertEqual(self.mod.wos_control_candidates(raw,'publication_titles','SO'),[
            {'field':'publication_titles','label':'COMPUTATIONAL COMPLEXITY','count':1,'native_group':'SO','native_value':'SO.COMPUTATIONAL COMPLEXITY'}])
        self.assertEqual(self.mod.wos_control_candidates(raw,'open_access_types','OAJ'),[
            {'field':'open_access_types','label':'Free to Read','count':3,'native_group':'OAJ','native_value':'OAJ.BRONZE'}])


if __name__=='__main__':unittest.main()
