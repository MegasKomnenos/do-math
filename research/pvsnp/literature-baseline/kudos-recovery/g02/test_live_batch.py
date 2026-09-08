import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from response_recovery import search_ui,select_documents,selected_payload
import run
papers=[json.loads(l) for l in (run.BASE/run.ASSIGN['members_path']).read_text(encoding='utf-8').splitlines()]
with sync_playwright() as pw:
 b=pw.chromium.launch();c=b.new_context(storage_state=run.ASSIGN['browser_state']);page=c.new_page();page.goto('https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q=')
 page.locator('#ho0').focus();page.locator('#ho0').press('Space');page.wait_for_function("document.querySelector('#ho0').checked");page.wait_for_timeout(1500)
 q='"10.1109/mcs.2008.931718" OR "10.1007/978-1-84800-998-1"'
 payload=search_ui(page,q)
 one=select_documents(papers[0],payload,q);two=select_documents(papers[1],payload,q)
 assert len(one)==1 and len(two)==3
 assert len(payload['documents'])>=len(one)+len(two)
 run.capture('fixtures','response-batch.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response')
 print(json.dumps({'query':q,'records':payload['record_count'],'first_matches':len(one),'book_matches':len(two),'passed':True}),flush=True)
 b.close()
