import copy,json,unittest
from pathlib import Path
from test_response import PAPERS,load
import resume
from unittest.mock import patch

class ResumeTests(unittest.TestCase):
 def test_fulltext_source_precedes_extra_search(self):
  r=resume.new_result(PAPERS[0]);resume.task(r,'search','extra title query');source=resume.task(r,'source','https://example.org/observed-fulltext')
  self.assertIs(resume.next_task(r,set()),source)
 def test_verified_goal_closes_extra_work_but_partial_does_not(self):
  r=resume.new_result(PAPERS[0]);r['identity']={'status':'confirmed','reason':'State-machine fixture; semantic validators tested separately.'};r['abstract']={'status':'found','artifacts':[{'path':'verified-abstract.txt'}]};r['fulltext']={'status':'found','artifacts':[{'path':'verified-fulltext.pdf'}]}
  t=resume.task(r,'search','unused query');r['unvisited_search_pages']=[{'query':'unused query'}]
  for component in ('identity','abstract','fulltext'):r['work_state']['reviews'][component]={'basis_sha256':resume.component_basis(r,component),'reason':'Validated fixture precondition.','evidence_paths':['verified-abstract.txt','verified-fulltext.pdf']}
  resume.close_satisfied_work(r);self.assertEqual(t['status'],'not_needed');self.assertNotIn('unvisited_search_pages',r)
  partial=resume.new_result(PAPERS[0]);u=resume.task(partial,'search','still needed');resume.close_satisfied_work(partial);self.assertEqual(u['status'],'pending')
 def test_actual_empty_source_is_preserved_as_failed_observation(self):
  p=PAPERS[3];r=json.loads((resume.ROOT/'results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'))
  old='intake/kudos-recovery/g02/VER-0035cae79b9bac8b129cb9d6/source-a802a3ec4675082d.txt'
  resume.repair_empty_evidence(r)
  self.assertFalse(any(e['path']==old for e in r['evidence']));self.assertTrue((resume.BASE/old).exists())
  self.assertTrue(any(x.get('previous_reference',{}).get('path')==old for x in r['superseded_capture_records']))
 def test_narrow_query_uses_observed_matching_title(self):
  p=PAPERS[1];payload=load('response-book.json')
  query=resume.narrow_query(p,payload)
  self.assertTrue(query.startswith('"Digraphs : theory, algorithms and applications"'));self.assertIn('2009',query)
 def test_actual_book_secondary_type_is_usable_with_exact_identifiers(self):
  payload=json.loads((resume.BASE/'intake/kudos-recovery/g02/_batches/resume-7c8e13b0a45e5278.json').read_text(encoding='utf-8'))
  self.assertTrue(resume.document_matches(PAPERS[3],payload['documents'][0]))
 def test_actual_hartley_bibliography_without_observed_isbn(self):
  payload=json.loads((resume.BASE/'intake/kudos-recovery/g02/VER-00126d6a637a84bd1afd7c40/search-e3a5c02787a6-1.json').read_text(encoding='utf-8'))
  self.assertTrue(resume.document_matches(PAPERS[2],payload['documents'][1]))
 def test_actual_ieee_scope_closes_only_after_all_sources_visited(self):
  p=PAPERS[0];r=json.loads((resume.ROOT/'results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'))
  resume.close_restricted_fulltext(r)
  self.assertEqual(r['fulltext']['status'],'unavailable');self.assertTrue(r['work_state']['reviews']['fulltext']['scope_complete'])
  r['fulltext']={'status':'unresolved','reason':'fixture'};resume.task(r,'source','https://example.org/unvisited')
  resume.close_restricted_fulltext(r);self.assertEqual(r['fulltext']['status'],'unresolved')
 def test_prefetch_reuses_complete_batch_in_candidate_tasks(self):
  p=PAPERS[0];r=resume.new_result(p);resume.inventory(p,r);payload=load('response-positive.json')
  payload['query']['original_query']='"10.1109/mcs.2008.931718"'
  with patch.object(resume,'search_ui',return_value=payload),patch.object(resume,'store_json'):
   resume.prefetch_identifiers(type('Page',(),{'url':'https://knu.summon.serialssolutions.com/'})(),[(p,r)],{})
  t=next(t for t in r['work_state']['tasks'] if t['target']=='10.1109/mcs.2008.931718');self.assertEqual(t['status'],'done')
 def test_saved_pdf_does_not_increment_request_attempts(self):
  p=PAPERS[1];r=resume.new_result(p);real=json.loads((resume.ROOT/'results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'));candidate=real['fulltext_candidates'][0];metrics={'downloads':0,'download_attempts':0}
  resume.save_pdf(p,r,(resume.BASE/candidate['artifact']['path']).read_bytes(),candidate['artifact']['url'],metrics)
  self.assertEqual(metrics['download_attempts'],0);self.assertEqual(metrics['downloads'],0);self.assertEqual(metrics['pdf_responses'],1)
 def test_automatic_positive_uses_real_source_identity_and_boundary(self):
  p=PAPERS[1];r=resume.new_result(p);payload=load('response-book.json')
  e={'path':'intake/kudos-recovery/g02/fixtures/response-book.json','sha256':resume.sha((resume.BASE/'intake/kudos-recovery/g02/fixtures/response-book.json').read_bytes()),'url':'https://knu.summon.serialssolutions.com/'}
  r['evidence']=[e];resume.inventory(p,r)
  resume.adjudicate_saved(p,r)
  self.assertEqual(r['identity']['status'],'confirmed');self.assertEqual(r['abstract']['status'],'found');self.assertEqual(r['abstract']['source_kind'],'database_indexing_abstract')
  self.assertIn('abstract',r['work_state']['reviews']);self.assertEqual(r['fulltext']['status'],'unresolved')
 def test_one_failed_source_does_not_stop_next(self):
  p=PAPERS[0];r=resume.new_result(p)
  first=resume.task(r,'source','https://example.org/failed');second=resume.task(r,'source','https://example.org/next');visited=[]
  def visit(context,paper,record,t,metrics):
   visited.append(t['target'])
   if t is first:raise RuntimeError('Observed UI search HTTP status 500')
   t.update(status='done',reason='Test source read.',evidence_paths=['fixture'])
  with patch.object(resume,'visit_source',side_effect=visit),patch.object(resume,'store_json'):
   resume.process_tasks(None,None,None,p,r,{'source_visits':0})
  self.assertEqual(visited,[first['target'],second['target']]);self.assertEqual(first['status'],'retry');self.assertEqual(second['status'],'done')
 def test_single_query_pages_preserve_unvisited_count(self):
  r=resume.new_result(PAPERS[0]);t=resume.task(r,'search','q')
  resume.page_progress(t,80,25,['response.json'])
  self.assertEqual(t['status'],'pending');self.assertEqual(t['remaining'],55)
  resume.page_progress(t,80,80,['response.json','response2.json'])
  self.assertEqual(t['status'],'done');self.assertEqual(t['remaining'],0)
 def test_pdf_and_fulltext_links_exclude_review_pdf(self):
  links=[{'text':'Review PDF','url':'https://example.org/review.pdf'},{'text':'Download PDF','url':'https://example.org/full.pdf'},{'text':'Full text','url':'https://example.org/article'},{'text':'Log in','url':'https://example.org/login'}]
  self.assertEqual([x['url'] for x in resume.fulltext_links(links)],['https://example.org/full.pdf','https://example.org/article'])
 def test_saved_sources_survive_abstract_found(self):
  r=json.loads((resume.ROOT/'results'/f"{PAPERS[0]['paper_id']}.json").read_text(encoding='utf-8'))
  resume.inventory(PAPERS[0],r)
  tasks=r['work_state']['tasks']
  self.assertTrue(any(t['kind']=='source' and t['target']==r['provider_link'] for t in tasks))
  self.assertTrue(any(t['kind']=='source' and t['target']==PAPERS[0]['source_urls'][0] for t in tasks))
 def test_all_observed_source_links_are_kept(self):
  r=resume.new_result(PAPERS[0]); r['observed_source_links']=[{'url':f'https://example.org/paper{i}'} for i in range(5)]
  resume.inventory(PAPERS[0],r)
  self.assertTrue(all(any(t['target']==v['url'] for t in r['work_state']['tasks']) for v in r['observed_source_links']))
 def test_saved_complete_query_does_not_repeat(self):
  r=resume.new_result(PAPERS[0]);payload=load('response-positive.json')
  e={'path':'intake/kudos-recovery/g02/fixtures/response-positive.json','sha256':resume.sha((resume.BASE/'intake/kudos-recovery/g02/fixtures/response-positive.json').read_bytes()),'url':'https://knu.summon.serialssolutions.com/'}
  r['evidence']=[e];resume.inventory(PAPERS[0],r)
  task=next(t for t in r['work_state']['tasks'] if t['target']=='10.1109/mcs.2008.931718')
  self.assertEqual(task['status'],'done')
 def test_book_database_abstract_is_candidate(self):
  r=resume.new_result(PAPERS[1]);payload=load('response-book.json')
  e={'path':'intake/kudos-recovery/g02/fixtures/response-book.json','sha256':resume.sha((resume.BASE/'intake/kudos-recovery/g02/fixtures/response-book.json').read_bytes()),'url':'https://knu.summon.serialssolutions.com/'}
  resume.consume_response(PAPERS[1],r,payload,e,save=False)
  self.assertTrue(r.get('abstract_candidates'))
 def test_http_error_retries_and_returns(self):
  attempts=[]
  def f():
   attempts.append(1)
   if len(attempts)==1:raise RuntimeError('Observed UI search HTTP status 500')
   return 'ok'
  waits=[];self.assertEqual(resume.retry(f,waits.append),'ok');self.assertEqual(len(attempts),2)
 def test_retry_exhaustion_is_finite(self):
  calls=[]
  def f():calls.append(1);raise RuntimeError('Observed UI search HTTP status 500')
  with self.assertRaises(RuntimeError):resume.retry(f,lambda _:None)
  self.assertEqual(len(calls),3)

if __name__=='__main__':unittest.main()
