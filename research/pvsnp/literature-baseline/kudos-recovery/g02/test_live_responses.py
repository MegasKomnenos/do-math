import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from response_recovery import search_ui,select_documents,selected_payload
import run
papers=[json.loads(l) for l in (run.BASE/run.ASSIGN['members_path']).read_text(encoding='utf-8').splitlines()]
with sync_playwright() as pw:
 b=pw.chromium.launch();c=b.new_context(storage_state=run.ASSIGN['browser_state']);page=c.new_page();page.goto('https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q=')
 page.locator('#ho0').focus();page.locator('#ho0').press('Space');page.wait_for_function("document.querySelector('#ho0').checked");page.wait_for_timeout(1500)
 for i,(q,paper,expected) in enumerate([('10.1109/mcs.2008.931718',papers[0],True),('g02nonexistentliteraturezzzz12345',papers[0],False),('10.1007/978-1-84800-998-1',papers[1],True)]):
  payload=search_ui(page,q);rows=select_documents(paper,payload,q);assert bool(rows)==expected
  run.capture('fixtures',f'live-response-transition-{i}.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response')
  print(json.dumps({'case':i,'query':q,'records':payload['record_count'],'matches':len(rows),'passed':True}),flush=True)
 b.close()
