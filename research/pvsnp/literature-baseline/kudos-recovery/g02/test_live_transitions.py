import argparse,json
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from playwright.sync_api import sync_playwright
import run

def live():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline-no-expand',action='store_true');args=ap.parse_args()
 with sync_playwright() as pw:
  b=pw.chromium.launch();c=b.new_context(storage_state=run.ASSIGN['browser_state']);page=c.new_page();page.set_default_timeout(15000)
  page.goto('https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q=');page.locator('#ho0').wait_for()
  if not args.baseline_no_expand:
   page.locator('#ho0').focus();page.locator('#ho0').press('Space');page.wait_for_function("document.querySelector('#ho0').checked")
  # The previous configuration fails this live assertion before any corpus result is accepted.
  assert page.locator('#ho0').is_checked(),'Search must include non-holdings before corpus queries'
  cases=[('10.1109/mcs.2008.931718',False),('g02nonexistentliteraturezzzz12345',True),('10.1007/978-1-84800-998-1',False)]
  for i,(q,zero) in enumerate(cases):
   body=run.search_summon(page,q)
   effective=parse_qs(urlsplit(page.url).fragment.split('?',1)[1])
   assert effective.get('ho')==['f'],('lost expanded scope',i)
   assert effective.get('q')==[q],('stale query',i)
   assert run.zero_results(body)==zero,('wrong zero-state',i)
   if not zero:
    page.locator('button.quick-look-button:visible').first.click();db=page.locator('[role=dialog]:visible').first.inner_text()
    assert q.lower() in db.lower(),('wrong returned detail',i)
    run.capture('fixtures',f'live-transition-{i}.txt',db,page.url,'live-transition-test')
    page.get_by_role('button',name='닫기',exact=True).click();page.locator('#quick-look-close-btn').wait_for(state='hidden')
   else:run.capture('fixtures',f'live-transition-{i}.txt',body,page.url,'live-transition-test')
   print(json.dumps({'case':i,'query':q,'expanded':True,'zero_results':zero,'passed':True}),flush=True)
  b.close()
if __name__=='__main__':live()
