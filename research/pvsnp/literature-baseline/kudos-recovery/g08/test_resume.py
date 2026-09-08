import json
import unittest
from pathlib import Path
import recover
import reconcile
import inspect

ROOT=Path(__file__).parent
PAPERS={p['paper_id']:p for p in map(json.loads,(recover.BASE/recover.ASSIGNMENT['members_path']).read_text(encoding='utf-8').splitlines())}

class RestartTests(unittest.TestCase):
    def test_actual_review_artifact_is_attached_to_result_evidence(self):
        import resume
        record=json.loads((ROOT/'results/VER-0e548f4255daeae971f0dcbd.json').read_text(encoding='utf-8'))
        artifact=record['review']['artifacts'][0]
        record['evidence']=[a for a in record['evidence'] if a['path']!=artifact['path']]
        resume.attach_source_evidence(record)
        self.assertIn(artifact['path'],{a['path'] for a in record['evidence']})
        size=len(record['evidence']);resume.attach_source_evidence(record)
        self.assertEqual(len(record['evidence']),size)
    def test_actual_publisher_pdf_candidate_enters_content_queue(self):
        import resume
        pid='VER-1b8f83e449cb75e1d0925466';record=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
        path='intake/kudos-recovery/g08/VER-1b8f83e449cb75e1d0925466/candidate-6fd0871fb8c8ce3f.pdf'
        record['fulltext']={'status':'unresolved'}
        record['work_state']['tasks']=[t for t in record['work_state']['tasks'] if not (t['kind']=='pdf' and t['target']==path)]
        tasks=resume.inventory(record,PAPERS[pid])
        self.assertTrue(any(t['kind']=='pdf' and t['target']==path for t in tasks))
    def test_native_provider_tasks_run_only_in_requested_browser(self):
        import resume
        record={'work_state':{'tasks':[{'key':'normal','kind':'source','target':'https://example.org','status':'pending'},{'key':'native','kind':'source','target':'https://www.sciencedirect.com','status':'pending','browser':'firefox'}]}}
        self.assertEqual([t['key'] for t in resume.pending_ui_tasks(record)],['normal'])
        self.assertEqual([t['key'] for t in resume.pending_ui_tasks(record,engine='firefox')],['native'])

    def test_actual_subtitle_match_opens_observed_source(self):
        import resume
        pid='VER-064f3fe56f66b7313daeda8d';record=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
        record['work_state']['tasks']=[]
        tasks=resume.inventory(record,PAPERS[pid])
        self.assertTrue(any(t['kind']=='source' and '/2.0.0/link/' in t['target'] for t in tasks))
    def test_explicit_source_retry_is_not_closed_by_old_capture(self):
        import resume
        pid='VER-09b5e675f4d3706945f363cf'
        record=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
        url='https://diposit.ub.edu/items/f873c894-dad5-4b56-8e4e-3b53b03a2f1c'
        p=dict(PAPERS[pid],source_urls=[url])
        t=next(x for x in record['work_state']['tasks'] if x['target']==url)
        t.update(status='retry',reason='Actual abstract expansion still required',expand_label='Show more')
        current=next(x for x in resume.inventory(record,p) if x['target']==url)
        self.assertEqual(current['status'],'retry')
        self.assertEqual(current['expand_label'],'Show more')
    def test_actual_duplicate_stub_is_not_missing_bibliography(self):
        import resume
        self.assertTrue(callable(getattr(resume,'parse_duplicate_stub',None)))
        p=PAPERS['VER-e2a2a3edac889302e7a94733']
        text=(recover.BASE/'intake/kudos-recovery/g08/VER-e2a2a3edac889302e7a94733/exception-page-8ce29ebb8233eb85.txt').read_text(encoding='utf-8')
        self.assertTrue(resume.parse_duplicate_stub(text,p))
    def test_resolver_aliases_need_matching_observed_specific_destinations(self):
        import resume
        self.assertTrue(callable(getattr(resume,'deduplicate_resolver_sources',None)))
        record=json.loads((ROOT/'results/VER-0e3537e04be3bd1376ba6518.json').read_text(encoding='utf-8'))
        specific=[t for t in record['work_state']['tasks'] if 'SS_jc=TC0000970516' in t['target']]
        generic=[t for t in record['work_state']['tasks'] if 'SS_jc=TC0001958124' in t['target']]
        self.assertGreater(len(specific),2)
        specific[-1]['status']='pending';specific[-1]['evidence_paths']=[]
        generic[-1]['status']='pending';generic[-1]['evidence_paths']=[]
        resume.deduplicate_resolver_sources(record)
        self.assertEqual(specific[-1]['status'],'not_needed')
        self.assertEqual(generic[-1]['status'],'pending')
    def test_missing_mr_detail_has_live_handler(self):
        import resume
        self.assertTrue(callable(getattr(resume,'visit_mathscinet',None)))

    def test_saved_search_can_defer_links_to_source_queue(self):
        self.assertIn('inspect_links',inspect.signature(recover.summon_query).parameters)

    def test_new_source_tasks_are_consumed_after_search(self):
        import resume
        self.assertTrue(callable(getattr(resume,'pending_ui_tasks',None)))
        one=resume.task('source','https://doi.org/10.1007/BFb0067053','done','Visited',['proof'])
        two=resume.task('source','https://books.google.com/books?id=H1ODjgEACAAJ','pending','Observed new source')
        record={'work_state':{'tasks':[one,two]}}
        self.assertEqual(resume.pending_ui_tasks(record,{one['key']}),[two])
    def test_actual_fielded_doob_search_has_all_declared_records(self):
        record=json.loads((ROOT/'results/VER-0e3537e04be3bd1376ba6518.json').read_text(encoding='utf-8'))
        pages=[json.loads((recover.BASE/a['path']).read_text(encoding='utf-8')) for a in record['evidence'] if a.get('kind')=='ui-search-response']
        latest=[d for d in pages if d.get('original_query')=='(TitleCombined:(Stochastic processes)) AND (AuthorCombined:(Doob))'][-1]
        self.assertEqual(len(latest['documents']),latest['record_count'])
    def test_shared_fielded_refinement_is_inventoried_once(self):
        import resume
        p=PAPERS['VER-1451d64298741c60bee5b720']
        record=json.loads((ROOT/'results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'))
        keys=[t['key'] for t in resume.inventory(record,p)]
        self.assertEqual(len(keys),len(set(keys)))
    def test_fielded_query_matches_observed_advanced_dialog_syntax(self):
        import resume
        self.assertTrue(callable(getattr(resume,'fielded_query',None)))
        self.assertEqual(resume.fielded_query({'title':'Gradient Flows','authors':['Ambrosio, Luigi']}),'(TitleCombined:(Gradient Flows)) AND (AuthorCombined:(Ambrosio))')

    def test_truncated_search_gets_fielded_refinement_task(self):
        import resume
        p=PAPERS['VER-299d3105cede6b2302ad9759']
        record=json.loads((ROOT/'results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'))
        self.assertTrue(any(t['kind']=='search' and t['target'].startswith('(TitleCombined:') for t in resume.inventory(record,p)))
    def test_direct_observed_pdf_is_preserved_for_content_review(self):
        import resume
        self.assertTrue(callable(getattr(resume,'accept_linked_pdf',None)))
        existing=json.loads((ROOT/'results/VER-05eea17a72a07d16d806738b.json').read_text(encoding='utf-8'))
        asset=existing['fulltext']['artifacts'][0]
        record={'evidence':[],'fulltext':{'status':'unresolved'},'work_state':{'tasks':[]}}
        self.assertTrue(resume.accept_linked_pdf({'paper_id':'restart-direct-pdf-test'},record,(recover.BASE/asset['path']).read_bytes(),asset['url']))
        self.assertEqual(record['fulltext']['status'],'unresolved')
        self.assertTrue(any(t['kind']=='pdf' and t['status']=='needs_review' for t in record['work_state']['tasks']))
        alias=asset['url']+'?observed-alias=1'
        self.assertTrue(resume.accept_linked_pdf({'paper_id':'restart-direct-pdf-test'},record,(recover.BASE/asset['path']).read_bytes(),alias))
        self.assertTrue(any(a['url']==alias for a in record['evidence']))

    def test_targeted_resume_parameter_exists(self):
        import resume
        self.assertIn('paper_id',inspect.signature(resume.run).parameters)
    def test_shared_checker_is_connected(self):
        import resume
        self.assertTrue(callable(getattr(resume,'verify_results',None)))
    def test_pdf_candidate_loop_has_no_unreported_three_link_cap(self):
        self.assertNotIn('candidates[:3]',inspect.getsource(recover._inspect_publisher))
        self.assertIn('pdf_candidate_visits',inspect.getsource(recover._inspect_publisher))

    def test_fulltext_negative_does_not_imply_abstract_negative(self):
        self.assertNotIn("if result['abstract']['status']=='unresolved' and result['fulltext']['status']",inspect.getsource(recover.collect))

    def test_article_navigation_checks_same_tab(self):
        self.assertTrue(callable(getattr(recover,'click_article',None)))

    def test_real_unvisited_source_does_not_establish_absence(self):
        r=json.loads((ROOT/'results/VER-100ededc2c64ac34d061ddb4.json').read_text(encoding='utf-8'))
        r['unvisited_link']=True
        r['abstract']={'status':'not_found','reason':'Old fulltext-derived absence'}
        fixed=reconcile.reconcile(r,PAPERS[r['paper_id']],recover.BASE)
        self.assertEqual(fixed['abstract']['status'],'unresolved')
        self.assertTrue(fixed['unvisited_link'])

    def test_book_abstract_is_a_review_candidate_not_automatically_description(self):
        self.assertTrue(callable(getattr(recover,'preserve_database_abstract',None)))

    def test_resume_uses_saved_evidence_without_browser_replay(self):
        import resume
        r=json.loads((ROOT/'results/VER-03ffef9bcb026605ecb23809.json').read_text(encoding='utf-8'))
        tasks=resume.inventory(r,PAPERS[r['paper_id']])
        self.assertFalse(any(t['target']=='MathSciNet detail' and t['status']=='pending' for t in tasks))
        self.assertTrue(any(t['kind']=='review' for t in tasks))

    def test_discovered_followup_survives_offline_inventory(self):
        import resume
        r=json.loads((ROOT/'results/VER-03ffef9bcb026605ecb23809.json').read_text(encoding='utf-8'))
        followup=resume.task('source','https://books.google.com/books?id=H1ODjgEACAAJ','pending','Observed source followup')
        r.setdefault('work_state',{}).setdefault('tasks',[]).append(followup)
        self.assertIn(followup,resume.inventory(r,PAPERS[r['paper_id']]))

    def test_truncated_query_can_be_narrowed_by_observed_year(self):
        import resume
        p=PAPERS['VER-03ffef9bcb026605ecb23809']
        self.assertEqual(getattr(resume,'narrow_query',lambda q,p:q)('"Higher algebraic K-theory. I" Quillen',p),'"Higher algebraic K-theory. I" Quillen 1973')

    def test_saved_narrow_search_does_not_repeat_broad_ui(self):
        import resume
        p=PAPERS['VER-03ffef9bcb026605ecb23809']
        r=json.loads((ROOT/'results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'))
        self.assertTrue(r.get('narrowed_searches'))
        # Isolate the retained year-refinement stage before the later indexed-field proof.
        r['work_state']={}
        r['evidence']=[a for a in r['evidence'] if a.get('kind')!='ui-search-response' or not json.loads((recover.BASE/a['path']).read_text(encoding='utf-8')).get('original_query','').startswith('(TitleCombined:')]
        broad=[t for t in resume.inventory(r,p) if t['kind']=='search' and t['target']=='"Higher algebraic K-theory. I" Quillen'][0]
        self.assertEqual(broad['status'],'needs_review')

    def test_same_observed_document_link_variants_share_one_source_visit(self):
        import resume
        self.assertTrue(callable(getattr(resume,'deduplicate_sources',None)))
        record=json.loads((ROOT/'results/VER-05eea17a72a07d16d806738b.json').read_text(encoding='utf-8'))
        for t in record['work_state']['tasks']:
            if t['kind']=='source' and 'summon.serialssolutions.com/2.0.0/link' in t['target']:
                t['status']='pending'
        before=sum(t['status']=='pending' for t in record['work_state']['tasks'])
        resume.deduplicate_sources(record)
        self.assertLess(sum(t['status']=='pending' for t in record['work_state']['tasks']),before)

if __name__=='__main__':
    unittest.main()
