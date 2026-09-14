from __future__ import annotations
import os,sys,threading,time,unittest
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.external import *
class H(BaseHTTPRequestHandler):
 def do_POST(self): self.send_response(201);self.end_headers();self.wfile.write(b'ok')
 def do_GET(self): self.send_response(302);self.send_header('Location','http://evil/');self.end_headers()
 def log_message(self,*a):pass
class Tests(unittest.TestCase):
 def setUp(self):
  self.server=HTTPServer(('127.0.0.1',0),H);threading.Thread(target=self.server.serve_forever,daemon=True).start();time.sleep(.02);self.origin=f'http://127.0.0.1:{self.server.server_port}'
  self.grant={'id':'G','status':'active','expires_at':None,'allowed_origins':[self.origin],'allowed_methods':['POST','GET'],'allowed_path_prefixes':['/ok'],'credential_env':{'X-Key':'EXT_TEST_KEY'},'allow_idempotent_retry':True};os.environ['EXT_TEST_KEY']='secret'
 def tearDown(self):self.server.shutdown();self.server.server_close();os.environ.pop('EXT_TEST_KEY',None)
 def test_persist_before_send_confirm_and_redact(self):
  calls=[];op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':'x'},'G','S');out=execute_operation(op,self.grant,persist=lambda x:calls.append(x) or True)
  self.assertEqual([x['status'] for x in calls],['prepared','running','running','confirmed']);self.assertTrue(calls[2]['transmitted']);self.assertEqual(out['status'],'confirmed');self.assertNotIn('secret',str(out))
 def test_unknown_retry_reconcile_and_scope(self):
  op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':''},'G','S');unknown=execute_operation(op,self.grant,persist=lambda x:True,transport=lambda *_:(_ for _ in ()).throw(TimeoutError()))
  self.assertEqual(unknown['status'],'unknown');
  with self.assertRaises(ValueError):execute_operation(unknown,self.grant,persist=lambda x:True)
  self.assertEqual(reconcile_operation(unknown,'receipt','confirmed',source='adapter')['status'],'confirmed')
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
  op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':''},'G','S');os.environ.pop('EXT_TEST_KEY');out=execute_operation(op,self.grant,persist=lambda x:calls.append(x) or True);self.assertEqual(out['status'],'failed');self.assertFalse(out['transmitted']);self.assertEqual(calls[-1]['status'],'failed')
 def test_stop_before_send_is_explicitly_untransmitted(self):
  op=prepare_operation({'method':'POST','url':self.origin+'/ok','body':''},'G','S');out=execute_operation(op,self.grant,persist=lambda _:True,should_stop=lambda:True)
  self.assertEqual((out['status'],out['transmitted']),('failed',False))
if __name__=='__main__':unittest.main()
