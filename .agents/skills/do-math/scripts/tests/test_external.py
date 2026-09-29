from __future__ import annotations
import os, sys, threading, unittest
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import MagicMock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.canonical import exact_content_hash
from do_math.external import *
from do_math import external, http_transport
from provider_fixtures import HTTPFixtureHandler
class Tests(unittest.TestCase):
 def test_method_body_contract_matches_preparation_validation_and_http_bytes(self):
  grant={**self.grant,'allowed_methods':['GET','POST','PUT','DELETE'],'credential_env':{}}
  for method in ('GET','POST','PUT','DELETE'):
   for body in (None,'','é',7):
    with self.subTest(method=method,body=body):
     request={'method':method,'url':self.origin+'/ok'}
     if body is not None: request['body']=body
     rejected=body == 7 or (method in ('GET','DELETE') and body == 'é')
     if rejected:
      with self.assertRaises(ValueError):prepare_operation(request,'G','S')
      continue
     operation=prepare_operation(request,'G','S')
     validate_operation(operation,grant,'2026-01-01T00:00:00Z')
     response=MagicMock();response.__enter__.return_value.status=200;response.__enter__.return_value.read.return_value=b'ok'
     with patch.object(http_transport,'build_opener') as opener:
      opener.return_value.open.return_value=response
      self.assertEqual(http_transport._http(operation,[],5)['body'],b'ok')
      sent=opener.return_value.open.call_args.args[0]
      self.assertEqual(sent.get_method(),method)
      self.assertEqual(sent.data,b'\xc3\xa9' if body == 'é' else None)
     if method in ('GET','DELETE'):
      old={**operation,'request':{**operation['request'],'body':'legacy'}}
      old['request_sha256']=exact_content_hash(old['request'])
      old['idempotency_key']=__import__('hashlib').sha256((old['id']+old['request_sha256']).encode()).hexdigest()
      calls=[]
      with self.assertRaises(ValueError):execute_operation(old,grant,persist=lambda _:True,
                                                           transport=lambda *_:calls.append(1))
      self.assertEqual(calls,[])

 def setUp(self):
  self.server=HTTPServer(('127.0.0.1',0),HTTPFixtureHandler);threading.Thread(target=self.server.serve_forever,daemon=True).start();self.origin=f'http://127.0.0.1:{self.server.server_port}'
  self.grant={'id':'G','status':'active','expires_at':None,'allowed_origins':[self.origin],'allowed_methods':['POST','GET'],'allowed_path_prefixes':['/ok'],'credential_env':{'X-Key':'EXT_TEST_KEY'}}
  self.enterContext(patch.dict(os.environ, {'EXT_TEST_KEY': 'secret'}))
 def tearDown(self):self.server.shutdown();self.server.server_close()
 def test_persist_before_send_confirm_and_redact(self):
  calls=[];op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':'x'},'G','S');out=execute_operation(op,self.grant,persist=lambda x:calls.append(x) or True)
  self.assertEqual([x['status'] for x in calls],['prepared','prepared','confirmed']);self.assertTrue(calls[1]['transmitted']);self.assertEqual(out['status'],'confirmed');self.assertNotIn('secret',str(out))
 def test_unknown_retry_reconcile_and_scope(self):
  op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':''},'G','S');unknown=execute_operation(op,self.grant,persist=lambda x:True,transport=lambda *_:(_ for _ in ()).throw(TimeoutError()))
  self.assertEqual(unknown['status'],'unknown');
  with self.assertRaises(ValueError):execute_operation(unknown,self.grant,persist=lambda x:True)
  with self.assertRaises(ValueError):reconcile_operation(unknown,'receipt','confirmed',source='adapter')
  evidence={'operation_id':unknown['id'],'request_sha256':unknown['request_sha256'],'idempotency_key':unknown['idempotency_key'],'fact':'succeeded','evidence_ref':'remote-receipt','observed_at':'2026-09-20T00:00:00Z'}
  self.assertEqual(reconcile_operation(unknown,evidence,'confirmed',source='adapter',succeeded=True)['status'],'confirmed')
  with self.assertRaises(ValueError):validate_operation(op,{**self.grant,'expires_at':'2000-01-01T00:00:00Z'},'2026-01-01T00:00:00Z')
  with self.assertRaises(ValueError):prepare_operation({'method':'GET','url':self.origin.replace('http://','http://x@')+'/ok'},'G','S')
  with self.assertRaises(ValueError):prepare_operation({'method':'GET','url':self.origin+'/ok/%2e%2e/outside'},'G','S')
 def test_redirect_and_stale_ledger(self):
  op=prepare_operation({'method':'GET','url':self.origin+'/ok','body':''},'G','S')
  with self.assertRaises(ValueError):execute_operation(op,self.grant,persist=lambda _:False)
  with self.assertRaises(ValueError):execute_operation(op,self.grant,persist=lambda _:True)
 def test_tampered_key_and_terminal_persist(self):
  calls=[];op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':''},'G','S');op['idempotency_key']='bad'
  with self.assertRaises(ValueError):validate_operation(op,self.grant,'2026-01-01T00:00:00Z')
  op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':''},'G','S');os.environ.pop('EXT_TEST_KEY');out=execute_operation(op,self.grant,persist=lambda x:calls.append(x) or True);self.assertEqual(out['status'],'prepared');self.assertFalse(out['transmitted']);self.assertEqual(calls[-1]['waiting_reason']['kind'],'credential_unavailable')
 def test_stop_before_send_is_explicitly_untransmitted(self):
  op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':''},'G','S');out=execute_operation(op,self.grant,persist=lambda _:True,should_stop=lambda:True)
  self.assertEqual((out['status'],out['transmitted']),('cancelled',False))

 def test_terminal_persist_failure_is_not_returned_as_committed_success(self):
  op=prepare_operation({'method':'POST','url':self.origin+'/ok'},'G','S');calls=[]
  def persist(record):
   if record['status']=='confirmed':return False
   calls.append(record);return True
  with self.assertRaises(ValueError):execute_operation(op,self.grant,persist=persist)
  recovered=recover_operation(calls[-1]);self.assertEqual(recovered['status'],'unknown')
  with self.assertRaises(ValueError):execute_operation(recovered,self.grant,persist=lambda _:True)

 def test_fresh_revocation_before_send_prevents_transport(self):
  op=prepare_operation({'method':'POST','url':self.origin+'/ok'},'G','S');current=dict(self.grant);sent=[]
  def persist(record):current['status']='revoked';return True
  with self.assertRaises(ValueError):execute_operation(op,self.grant,persist=persist,current_grant=lambda _:current,transport=lambda *_:sent.append(1))
  self.assertEqual(sent,[])

 def test_retries_need_exact_nonexpired_idempotency_evidence(self):
  op=prepare_operation({'method':'POST','url':self.origin+'/ok'},'G','S')
  op=execute_operation(op,self.grant,persist=lambda _:True,transport=lambda *_:(_ for _ in ()).throw(TimeoutError()))
  evidence={'kind':'verified_idempotency','request_sha256':op['request_sha256'],'idempotency_key':op['idempotency_key'],'valid_until':'2099-01-01T00:00:00Z','evidence_ref':'verified-service-contract'}
  with self.assertRaises(ValueError):prepare_retry(op,{**evidence,'request_sha256':'wrong'},source='adapter')
  retry=prepare_retry(op,evidence,source='adapter')
  self.assertEqual(execute_operation(retry,self.grant,persist=lambda _:True)['status'],'confirmed')

 def test_credential_resume_loopback_clears_wait_and_preserves_identity(self):
  from unittest.mock import patch
  grant={**self.grant,'kind':'http','reuse':'reusable'}
  op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':'credential-resume'},'G','S','OP-resume')
  runtime={'external_operations':{},'executions':{}}
  def persist(row):runtime['external_operations'][row['id']]=row;return True
  with patch.dict(os.environ,{},clear=True):
   waiting=execute_operation(op,grant,persist=persist,runtime=runtime)
  self.assertEqual(waiting['waiting_reason']['kind'],'credential_unavailable')
  result=execute_operation(waiting,grant,persist=persist,runtime=runtime)
  self.assertEqual(result['status'],'confirmed');self.assertNotIn('waiting_reason',result)
  for key in ('id','request_sha256','idempotency_key'):self.assertEqual(result[key],op[key])
  with self.assertRaises(ValueError):execute_operation(result,grant,persist=persist,runtime=runtime)
if __name__=='__main__':unittest.main()
