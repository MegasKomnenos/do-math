import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from collect import BASE,WORK
import summon_collect
import acm_collect

class RestartTests(unittest.TestCase):
    def test_fixed_title_match_reopens_unresolved_identity_from_actual_saved_response(self):
        import resume
        r=json.loads((WORK/'results/VER-1e93042fe2d9050b89a289fd.json').read_text());r['identity']={'status':'unresolved','reason':'Earlier named TeX accent mismatch'}
        resume.review_saved(r,dict(r['metadata'],paper_id=r['paper_id']),[])
        self.assertEqual(r['identity']['status'],'confirmed')

    def test_new_native_source_work_prevents_reclosing_old_cpe_scope(self):
        import resume
        r=json.loads((WORK/'results/VER-022f997d68492e3705be19c6.json').read_text());a=json.loads((WORK/'assignment.json').read_text());paper=next(p for p in map(json.loads,(BASE/a['members_path']).read_text().splitlines()) if p['paper_id']==r['paper_id'])
        r['work_state']['tasks'].append({'key':'new-native-source','kind':'source','target':'https://www.sciencedirect.com/science/article/pii/S1572528623000634','status':'pending','reason':'Newly available native route has not been inspected'})
        self.assertFalse(resume.restricted_scope_evidence(r,paper))
    def test_actual_flat_math_field_requires_source_review(self):
        import resume
        text=(BASE/'intake/kudos-recovery/g05/VER-44b62514b8f18a8d525b1228/summon-abstract-live.txt').read_text()
        fn=getattr(resume,'provider_text_issue',lambda text:None)
        self.assertIsNotNone(fn(text))
        self.assertIsNone(fn('Runtime 2^{O(t)} n^{O(1)} and class Sigma with explicit indices.'))
    def test_stale_closed_component_task_is_reopened_from_common_queue(self):
        import resume
        r=json.loads((WORK/'results/VER-028dadfb49623dd97a98242c.json').read_text());r['work_state']['reviews'].pop('abstract',None)
        task=next(t for t in r['work_state']['tasks'] if t['key']=='review:abstract');task['status']='done'
        resume.refresh_inventory(r,dict(r['metadata']),[])
        self.assertEqual(task['status'],'needs_review')
    def test_manual_provider_variant_judgment_survives_automatic_reassessment(self):
        import resume
        r=json.loads((WORK/'results/VER-5a638ef98dced21506bd348b.json').read_text())
        raw=r['abstract'].get('candidate_artifacts') or r['abstract']['raw_provider_artifacts']
        r['abstract']={'status':'found','artifacts':raw,'raw_provider_artifacts':raw,'source_kind':'database_indexing_abstract'}
        r['work_state']['reviews']['abstract']={'method':'manual','basis_sha256':resume.component_basis(r,'abstract'),'reason':'Fixture of an explicitly completed manual variant judgment','evidence_paths':[raw[0]['path']]}
        before=copy.deepcopy(r['abstract']);resume.review_saved(r,dict(r['metadata'],paper_id=r['paper_id'],record_type='proceedings'),[])
        self.assertEqual(r['abstract'],before)
    def test_existing_inventory_pending_source_uses_saved_capture_but_explicit_retry_stays(self):
        import resume
        r=json.loads((WORK/'results/VER-022f997d68492e3705be19c6.json').read_text());url='https://doi.org/10.1016/j.disopt.2023.100821';paper=dict(r['metadata'],source_urls=[url])
        task={'key':'source:'+url,'kind':'source','target':url,'status':'pending','reason':'Assess observed source path or visit missing input source'}
        r['work_state']['tasks']=[task];resume.refresh_inventory(r,paper,[])
        self.assertEqual(task['status'],'needs_review')
        task.update(status='retry',reason='Operator reopened after a source repair');resume.refresh_inventory(r,paper,[])
        self.assertEqual(task['status'],'retry')
    def test_saved_source_capture_is_reviewed_without_browser_replay(self):
        import resume
        r=json.loads((WORK/'results/VER-022f997d68492e3705be19c6.json').read_text())
        paper=dict(r['metadata'],source_urls=['https://doi.org/10.1016/j.disopt.2023.100821'])
        t=next(t for t in resume.inventory(r,paper,[]) if t['key'].startswith('source:'))
        self.assertEqual(t['status'],'needs_review')
    def test_actual_provider_prefix_variant_preserves_long_complete_text_and_math_conflict(self):
        import resume
        r=json.loads((WORK/'results/VER-0c26fc7b79631b63b132fbae.json').read_text())
        response=next(json.loads((BASE/e['path']).read_text()) for e in reversed(r['evidence']) if e.get('kind')=='actual-ui-search-response')
        doc=next(d for d in response['documents'] if '9783031929311' in (d.get('isbns') or []) and d.get('abstracts'))
        values=[a['abstract'] for a in doc['abstracts']]
        fn=getattr(resume,'complete_provider_variant',lambda values:None)
        self.assertEqual(fn(values),values[0])
        conflict=json.loads((WORK/'results/VER-3b82bf030dc937915b35b0be.json').read_text())['observed_metadata']['abstracts']
        self.assertIsNone(fn([a['abstract'] for a in conflict]))
    def test_prior_visual_review_note_can_be_in_source_kind(self):
        import resume
        r=json.loads((WORK/'results/VER-0337e1f072679837dc638f9e.json').read_text());r['work_state']['reviews'].pop('abstract',None)
        resume.review_saved(r,dict(r['metadata'],paper_id=r['paper_id']),[])
        self.assertIn('abstract',r['work_state']['reviews'])
    def test_actual_acm_download_attempts_are_counted(self):
        import resume
        r=json.loads((WORK/'results/VER-ac145acc0fc054b8adb633c1.json').read_text())
        expected=sum(a.get('outcome','').startswith('Observed download request attempt') for a in r['attempts'])
        self.assertGreater(expected,0)
        value=getattr(resume,'count_actions',lambda attempts:{'downloads':0})(r['attempts'])
        self.assertEqual(value['downloads'],expected)
    def test_legacy_visual_transcription_review_is_reused_with_bound_sources(self):
        import resume
        r=json.loads((WORK/'results/VER-028dadfb49623dd97a98242c.json').read_text());r['work_state']['reviews'].pop('abstract',None)
        paper=dict(r['metadata'],paper_id=r['paper_id'],publication={'pages':'604–618'})
        resume.review_saved(r,paper,[])
        self.assertEqual(r['work_state']['reviews'].get('abstract',{}).get('basis_sha256'),resume.component_basis(r,'abstract'))
        self.assertEqual(r['abstract']['extraction_quality'],'visually_corrected')
    def test_later_empty_response_does_not_hide_earlier_complete_abstract(self):
        import resume,tempfile,hashlib
        r=json.loads((WORK/'results/VER-18224046ee9e0512522464a3.json').read_text());r['abstract']={'status':'unresolved','reason':'Needs saved-data recovery'}
        original=next(e for e in r['evidence'] if e.get('kind')=='actual-ui-search-response')
        data=json.loads((BASE/original['path']).read_text())
        for d in data['documents']:d['abstracts']=[]
        with tempfile.TemporaryDirectory(dir=WORK/'tdd') as tmp:
            path=Path(tmp)/'empty-abstract-response.json';path.write_text(json.dumps(data),encoding='utf-8')
            r['evidence'].append(dict(original,path=path.relative_to(BASE).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            resume.review_saved(r,dict(r['metadata'],record_type='article',paper_id=r['paper_id']),[])
        self.assertEqual(r['abstract']['status'],'found')
    def test_actual_restricted_scope_requires_every_input_source_and_no_pending_pdf(self):
        import resume
        r=json.loads((WORK/'results/VER-022f997d68492e3705be19c6.json').read_text())
        a=json.loads((WORK/'assignment.json').read_text());paper=next(p for p in map(json.loads,(BASE/a['members_path']).read_text().splitlines()) if p['paper_id']==r['paper_id'])
        fn=getattr(resume,'restricted_scope_evidence',lambda *a:[])
        reopened=copy.deepcopy(r)
        reopened['work_state']['tasks'].append({'key':'new-observed-source','kind':'source','target':'https://www.sciencedirect.com/new-observed-route','status':'pending'})
        self.assertFalse(fn(reopened,paper))
        r['work_state']['tasks']=[t for t in r['work_state']['tasks'] if not t['key'].startswith('sciencedirect-')] # Original captured restriction fixture before the new native routes.
        r['fulltext']={'status':'unavailable','reason':'Original individual CPE fixture, before subsequently discovered normal HTML route'}
        r['evidence']=[e for e in r['evidence'] if not Path(e['path']).name.startswith('native-')]
        self.assertTrue(fn(r,paper))
        broken=copy.deepcopy(r);broken['scope_review']['source_urls_attempted_this_pass']=[]
        self.assertFalse(fn(broken,paper))
        broken=copy.deepcopy(r);broken['evidence'].append({'path':'pending.pdf','kind':'pending-identity'})
        self.assertFalse(fn(broken,paper))
    def test_saved_later_document_without_previous_candidate_is_recovered(self):
        import resume
        r=json.loads((WORK/'results/VER-5e89856450ccdd4ba5209072.json').read_text());r['abstract']={'status':'unresolved','reason':'Previous first record had no abstract'}
        paper=dict(r['metadata'],record_type='article',paper_id=r['paper_id'])
        resume.review_saved(r,paper,[])
        self.assertEqual(r['abstract']['status'],'found')
    def test_missing_acm_original_uses_institutional_source_after_public_wall(self):
        import resume
        r=json.loads((WORK/'results/VER-00f77d85ac0cd436f632594e.json').read_text())
        tasks=resume.inventory(r,dict(r['metadata']),[])
        self.assertTrue(any(t['key']=='acm' and t['status']=='pending' for t in tasks))
    def test_retry_timeout_recovers_but_invalid_data_does_not_repeat(self):
        import resume
        fn=getattr(resume,'retry_step',lambda operation,wait:operation())
        calls=[]
        def operation():
            calls.append(1)
            if len(calls)==1:raise TimeoutError('transient timeout')
            return 'recovered'
        try:result=fn(operation,lambda seconds:None)
        except TimeoutError:result='failed'
        self.assertEqual(result,'recovered')
        self.assertEqual(len(calls),2)
    def test_run_finish_executes_actual_assignment_check(self):
        import resume
        result=getattr(resume,'finish_run',lambda path: {})(WORK/'tdd')
        self.assertIn('complete',result)
        self.assertEqual(result.get('assigned'),382)
        self.assertFalse(result.get('complete'))
        progress=json.loads((WORK/'progress.json').read_text())
        self.assertEqual(progress['fulltext_found'],result['counts'].get('fulltext:found',0))
        self.assertEqual(progress['remaining'],result['papers_with_remaining_work'])
    def test_actual_provider_highlights_split_from_body(self):
        import resume
        for pid in ['VER-15fb8ccf45a3fd2659bfcc80','VER-1e9cddd39be20f7603f239ea']:
            raw=(BASE/'intake/kudos-recovery/g05'/pid/'summon-abstract.txt').read_text()
            parts=getattr(resume,'provider_parts',lambda t:{'body':t,'highlights':''})(raw)
            self.assertNotIn('•',parts['body'])
            self.assertIn('•',parts['highlights'])
            self.assertGreater(len(parts['body']),200)
    def test_acm_first_other_pdf_keeps_next_target(self):
        source=json.loads((WORK/'results/VER-028dadfb49623dd97a98242c.json').read_text())
        paper=dict(source['metadata'],paper_id=source['paper_id'],version_sha256=source['version_sha256'],publication={'pages':'604–618'})
        doi=paper['identifiers']['doi'][0]
        right=(BASE/source['fulltext']['artifacts'][0]['path']).read_bytes()
        wrong=(BASE/'intake/kudos-recovery/g05/VER-014dd490736be8ba7793740c/pdf-pending.pdf').read_bytes()
        class Loc:
            def __init__(self,sel):self.sel=sel
            @property
            def first(self):return self
            def fill(self,x):pass
            def press(self,x):pass
            def count(self):return 0
            def inner_text(self):return paper['title']+' '+doi
            def all_inner_texts(self):return [paper['title']]
            def evaluate_all(self,js):
                if 'filter' in js:return [{'text':'PDF','url':'https://example.org/doi/pdf/'+doi+'?first'},{'text':'PDF','url':'https://example.org/doi/pdf/'+doi+'?second'}]
                return [{'text':paper['title'],'url':'https://example.org/doi/'+doi}]
        class Page:
            url='https://example.org/acm'
            def locator(self,s):return Loc(s)
            def goto(self,*a,**kw):pass
            def wait_for_load_state(self,*a):pass
            def wait_for_timeout(self,*a):pass
        class Context:
            @property
            def request(self):return self
            def get(self,url,**kw):
                class Response:
                    status=200
                    def body(self):return wrong if '?first' in url else right
                return Response()
        with patch.object(acm_collect,'artifact',side_effect=lambda pid,name,data,url,*a,**k:{'path':name,'url':url}):
            r=acm_collect.collect(Context(),Page(),paper)
        self.assertEqual(r['fulltext']['status'],'found')
    def test_saved_complete_database_abstract_is_recovered(self):
        import resume
        r=json.loads((WORK/'results/VER-18224046ee9e0512522464a3.json').read_text())
        assignment=json.loads((WORK/'assignment.json').read_text())
        paper=next(p for p in map(json.loads,(BASE/assignment['members_path']).read_text().splitlines()) if p['paper_id']==r['paper_id'])
        getattr(resume,'review_saved',lambda *a:None)(r,paper,[])
        self.assertEqual(r['abstract']['status'],'found')
        self.assertEqual(r['abstract']['source_kind'],'database_indexing_abstract')
        self.assertEqual(r['abstract']['authorship'],'unknown')
    def test_saved_citation_is_not_promoted(self):
        import resume
        r=json.loads((WORK/'results/VER-fb4619113c1561c4871fa01b.json').read_text())
        getattr(resume,'review_saved',lambda *a:None)(r,dict(r['metadata'],paper_id=r['paper_id']),[])
        self.assertNotEqual(r['abstract']['status'],'found')
    def test_new_candidate_joins_existing_work_state(self):
        import resume
        r={'identity':{'status':'confirmed'},'abstract':{'status':'unresolved'},'fulltext':{'status':'found'},'evidence':[], 'work_state':{'version':'remaining-work/1','tasks':[],'reviews':{}}}
        r['evidence'].append({'path':'new.pdf','kind':'pending-identity'})
        refresh=getattr(resume,'refresh_inventory',lambda r,p,x:None)
        refresh(r,{'title':'target'},[])
        self.assertTrue(any(t['target']=='new.pdf' for t in r['work_state']['tasks']))
    def test_new_source_does_not_erase_closed_task(self):
        import resume
        old={'key':'source:https://example.org/old','kind':'source','target':'https://example.org/old','status':'done','reason':'Observed','evidence_paths':['old.txt']}
        r={'identity':{'status':'confirmed'},'abstract':{'status':'unresolved'},'fulltext':{'status':'found'},'evidence':[], 'work_state':{'version':'remaining-work/1','tasks':[old.copy()],'reviews':{}}}
        getattr(resume,'refresh_inventory',lambda r,p,x:None)(r,{'title':'target','source_urls':['https://example.org/old','https://example.org/new']},[])
        self.assertIn(old,r['work_state']['tasks'])
        self.assertTrue(any(t['target']=='https://example.org/new' for t in r['work_state']['tasks']))
    def test_first_other_pdf_does_not_hide_next_target(self):
        record=json.loads((WORK/'results/VER-028dadfb49623dd97a98242c.json').read_text())
        target=(BASE/record['fulltext']['artifacts'][0]['path']).read_bytes()
        other=json.loads((WORK/'results/VER-014dd490736be8ba7793740c.json').read_text())
        wrong=(BASE/other['fulltext']['artifacts'][0]['path']).read_bytes()
        r=copy.deepcopy(record);r['fulltext']={'status':'unresolved'}
        paper=dict(record['metadata'],paper_id=record['paper_id'],publication={'pages':'604–618'})
        class Locator:
            def count(self):return 1
            def inner_text(self):return 'Observed publisher target page'
            def evaluate_all(self,code):return [{'text':'PDF','url':'https://example.org/doi/pdf/'+paper['identifiers']['doi'][0]+'?candidate='+name} for name in ['failed','other','target']]
            @property
            def first(self):return self
        class Page:
            url='https://example.org/observed'
            def goto(self,*a,**k):pass
            def wait_for_timeout(self,*a):pass
            def locator(self,*a):return Locator()
            def title(self):return 'Target publisher'
            def close(self):pass
        class Context:
            def new_page(self):return Page()
            @property
            def request(self):return self
            def get(self,url,**kwargs):
                if 'candidate=failed' in url:raise TimeoutError('one candidate timed out')
                class Response:
                    status=200
                    def body(self):return wrong if 'candidate=other' in url else target
                return Response()
        from functools import partial
        from collect import get_download
        with patch.object(summon_collect,'artifact',side_effect=lambda pid,name,data,url,*a,**k:{'path':name,'url':url}),patch.object(summon_collect,'get_download',partial(get_download,wait=lambda seconds:None)):
            summon_collect.publisher(Context(),r,paper,'https://example.org/observed','fixture')
        self.assertEqual(r['fulltext']['status'],'found')
        self.assertEqual(len([a for a in r['attempts'] if 'UI-observed PDF/download' in a.get('outcome','')]),2)

    def test_saved_fulltext_keeps_abstract_review_and_scope_flag_keeps_work(self):
        import resume
        r=json.loads((WORK/'results/VER-028dadfb49623dd97a98242c.json').read_text())
        r['abstract']={'status':'unresolved','candidate_artifacts':[{'path':'candidate.txt'}]}
        r['scope_review']={'summon_beyond_holdings':True}
        tasks=resume.inventory(r,{},[])
        self.assertTrue(any(t['kind']=='review' and t['status']=='needs_review' for t in tasks))
        self.assertFalse(any(t.get('status')=='done' for t in tasks))

if __name__=='__main__':unittest.main()
