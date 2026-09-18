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

    def test_the_sources_own_error_screen_is_read_instead_of_waited_out(self):
        """WoS가 자기 오류 화면으로 보내면 제어는 영영 나타나지 않는다. 그 화면을 읽고 끝낸다."""
        host='https://www-webofscience-com.libproxy.knu.ac.kr'
        self.assertEqual(self.mod.wos_error_message(host+'/wos/error/generic?message=Server.internalError'),'Server.internalError')
        self.assertEqual(self.mod.wos_error_message(host+'/wos/error/generic'),'unknown')
        self.assertIsNone(self.mod.wos_error_message(host+'/wos/woscc/basic-search'))
        self.assertIsNone(self.mod.wos_error_message(host+'/wos/woscc/summary/abc-1/relevance/1'))

    def test_an_error_event_inside_a_200_stream_is_the_providers_transient_failure(self):
        """실측: 같은 getHistory·runQuerySearch 요청에 WoS가 HTTP 200으로 {"key":"error","payload":["Server.internalError"]}를
        간헐적으로 돌려줬다. 이를 'result count 없음'으로 보고하면 호출자는 질의를 의심하게 된다."""
        with self.assertRaises(ServiceError) as raised:
            self.mod.wos_events('{"id":0,"key":"error","payload":["Server.internalError"]}')
        self.assertEqual(raised.exception.result['code'],'provider_error')
        self.assertEqual(raised.exception.result['provider_message'],['Server.internalError'])
        self.assertTrue(raised.exception.result['retryable'])

    def test_transient_provider_failures_are_retried_and_other_failures_are_not(self):
        calls=[]
        def flaky():
            calls.append(1)
            if len(calls)<3:raise ServiceError('provider_error','transient',retryable=True)
            return 'done'
        from unittest.mock import patch
        with patch.object(self.mod.time,'sleep') as sleep:
            self.assertEqual(self.mod.retry_transient(flaky,attempts=5),'done')
        self.assertEqual(len(calls),3)
        # 실측: WoS의 일시 오류는 몰려서 온다(1.5초 안에 5회 연속). 곧바로 다시 시도하면 같은 몰림 안에서 전부 실패한다.
        pauses=[call.args[0] for call in sleep.call_args_list]
        self.assertEqual(len(pauses),2);self.assertGreater(pauses[1],pauses[0]);self.assertGreater(pauses[0],0)
        calls.clear()
        def always():
            calls.append(1);raise ServiceError('provider_error','transient',retryable=True)
        with patch.object(self.mod.time,'sleep'),self.assertRaises(ServiceError) as raised:self.mod.retry_transient(always,attempts=4)
        self.assertEqual((len(calls),raised.exception.result['attempts']),(4,4))
        calls.clear()
        def wrong():
            calls.append(1);raise ServiceError('query_mismatch','not transient')
        with self.assertRaises(ServiceError):self.mod.retry_transient(wrong,attempts=4)
        self.assertEqual(len(calls),1)

    def test_quick_filter_groups_keyed_by_another_index_do_not_invalidate_the_search(self):
        """실측: 결과가 큰 검색의 analyze에는 REVIEW·EARLY ACCESS 그룹이 오며 그 키는 DT.REVIEW·DT.EARLY ACCESS다.
        이 어댑터가 쓰지 않는 그룹인데도 '키는 그룹 이름으로 시작한다'는 검사에 걸려 검색 전체가 invalid_response가 되었다."""
        events=[{'key':'analyze','payload':{
            'REVIEW.Value.6':{'Name':'REVIEW','Values':[{'Key':'DT.REVIEW','Value':150}]},
            'EARLY ACCESS.Value.6':{'Name':'EARLY ACCESS','Values':[{'Key':'DT.EARLY ACCESS','Value':251}]},
            'DT.Value.6':{'Name':'DT','Values':[{'Key':'DT.ARTICLE','Value':16}]}}}]
        self.assertEqual(self.mod.wos_facet_candidates(events),[
            {'group':'DT','value':'DT.ARTICLE','label':'ARTICLE','count':16,'control_section':'DT'}])
        broken=[{'key':'analyze','payload':{'DT.Value.6':{'Name':'DT','Values':[{'Key':'PY.2024','Value':1}]}}}]
        with self.assertRaises(ServiceError):self.mod.wos_facet_candidates(broken)

    def test_export_survives_the_error_screen_that_replaces_its_dialog(self):
        """실측: 내보내기 오버레이가 열릴 때 runQueryGetRecordsStream이 일시 오류를 받으면 WoS는 /wos/error/generic으로 이동하고
        대화상자가 사라진다. 입력란을 기다리던 조작은 대기를 소진한 뒤 TimeoutError로만 보고되었다."""
        from types import SimpleNamespace
        result='https://www.webofscience.com/wos/woscc/summary/qid-1/relevance/1'
        page=SimpleNamespace(url=result,goto=Mock(),wait_for_function=Mock(),locator=Mock(return_value=SimpleNamespace(wait_for=Mock())))
        adapter=self.mod.WebOfScience(None,None);calls=[]
        def once(page_,start,end,format):
            calls.append(page_.url)
            if len(calls)==1:
                page_.url='https://www.webofscience.com/wos/error/generic?message=Server.internalError'
                raise TimeoutError('dialog vanished')
            return {'ref':'export'}
        def goto(url,**kwargs):page.url=url
        page.goto=Mock(side_effect=goto)
        adapter.export_once=once
        from unittest.mock import patch
        with patch.object(self.mod.time,'sleep'):
            self.assertEqual(adapter.export_records(page,0,5,'plain'),{'ref':'export'})
        self.assertEqual(calls,[result,result]);page.goto.assert_called_once()
        self.assertEqual(page.goto.call_args.args[0],result)
        def broken(page_,start,end,format):raise TimeoutError('not the provider')
        adapter.export_once=broken
        with self.assertRaises(TimeoutError):adapter.export_records(page,0,5,'plain')

    def test_a_search_blocked_by_the_institutional_proxy_is_a_query_rejection(self):
        """실측: TS=("a") AND PY=(2024)처럼 불리언 연산자와 필드=(…)가 결합한 검색식은 runQuerySearch가 기관 프록시의 HTML 400으로 끝난다.
        WoS가 본 적도 없는 요청이므로 'WOS browser search failed'(제공자 오류)로 보고하면 호출자가 고칠 곳을 알 수 없다."""
        from types import SimpleNamespace
        blocked=SimpleNamespace(status=400,headers={'content-type':'text/html; charset=UTF-8'})
        failure=self.mod.wos_search_failure(blocked,'TS=("a") AND PY=(2024)')
        self.assertEqual((failure.result['code'],failure.result['rejected_by'],failure.result['http_status']),('query_rejected','institutional_proxy',400))
        self.assertNotIn('retryable',failure.result)
        own=SimpleNamespace(status=500,headers={'content-type':'application/json'})
        failure=self.mod.wos_search_failure(own,'TS=(a)')
        self.assertEqual((failure.result['code'],failure.result['http_status']),('provider_error',500))

    def test_the_error_screen_is_not_mistaken_for_a_lost_query_identity(self):
        """실측: facet을 적용하던 중 WoS가 일시 오류로 자기 오류 화면에 갔고, 결과 주소에서 qid를 찾지 못한 어댑터는
        이를 query_mismatch(검색식 문제)로 보고했다. 같은 호출을 되풀이하면 되는 일시 오류다."""
        with self.assertRaises(ServiceError) as raised:
            self.adapter.result_qid('https://www.webofscience.com/wos/error/generic?message=Server.internalError')
        self.assertEqual((raised.exception.result['code'],raised.exception.result['retryable']),('provider_error',True))
        with self.assertRaises(ServiceError) as raised:
            self.adapter.result_qid('https://www.webofscience.com/wos/woscc/advanced-search')
        self.assertEqual(raised.exception.result['code'],'query_mismatch')

    def test_an_already_exhausted_inner_retry_is_not_multiplied_by_an_outer_one(self):
        from unittest.mock import patch
        calls=[]
        def exhausted():
            calls.append(1);raise ServiceError('provider_error','transient',retryable=True,attempts=5)
        with patch.object(self.mod.time,'sleep'),self.assertRaises(ServiceError):self.mod.retry_transient(exhausted,attempts=5)
        self.assertEqual(len(calls),1)

    def test_facet_counts_with_thousands_separators_do_not_leak_into_the_label(self):
        """실측: 화면의 aria-label "2025, 12,369"를 표지 "2025, 12"·건수 369로 읽어, facet_filters의 publication_years=["2025"]가
        selection_required로 끝났다. 건수의 천 단위 쉼표는 구분자가 아니다."""
        raw='<div><input type="checkbox" name="PY" value="PY.2025" aria-label="2025, 12,369"><input type="checkbox" name="PY" value="PY.2024" aria-label="2024, 987">'             '<input type="checkbox" name="SO" value="SO.X" aria-label="PROC, PART 2, 1,234,567"></div>'
        self.assertEqual([(item['label'],item['count']) for item in self.mod.wos_control_candidates(raw,'publication_years','PY')],[('2025',12369),('2024',987)])
        self.assertEqual([(item['label'],item['count']) for item in self.mod.wos_control_candidates(raw,'publication_titles','SO')],[('PROC, PART 2',1234567)])


if __name__=='__main__':unittest.main()
