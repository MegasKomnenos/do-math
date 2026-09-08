import json,hashlib,os,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from collect import BASE,WORK,artifact,save_json,norm,safe_url
from link_scope import observe_links,select_downloads,classify
run=WORK/'runs'/time.strftime('%Y%m%d-%H%M%S-link-scope');run.mkdir()
save_json(run/'manifest.json',{'pid':os.getpid(),'argv':sys.argv,'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in WORK.glob('*.py')}})
items=[('VER-0c26fc7b79631b63b132fbae','https://link-springer-com.libproxy.knu.ac.kr/book/10.1007/978-3-031-92932-8'),('VER-6ca41f512673a1b0643f9f14','https://proceedings.neurips.cc/paper/1990/hash/8dd48d6a2e2cad213179a3992c0be53c-Abstract.html')]
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='chrome',headless=True);c=b.new_context(storage_state='C:/math/.credentials/kudos-recovery/bootstrap.json')
 try:
  for pid,url in items:
   p=c.new_page();p.goto(url,wait_until='domcontentloaded');p.wait_for_timeout(1500);r=json.loads((WORK/'results'/f'{pid}.json').read_text());links=observe_links(p);heading=p.locator('h1');title_matches=bool(heading.count()) and norm(r['metadata']['title']) in norm(heading.first.inner_text());chosen=select_downloads(r['metadata'],p.url,links,title_matches=title_matches);result={'url':safe_url(p.url),'title_matches':title_matches,'selected':[dict(x,url=safe_url(x['url'])) for x in chosen],'decisions':[{'url':safe_url(x['url']),'text':x.get('text',''),'scope_role':classify(r['metadata'],p.url,x,title_matches=title_matches)[0]} for x in links]};artifact(pid,'live-download-scope.json',json.dumps(result,ensure_ascii=False,indent=2),p.url,'application/json','actual-target-download-scope');print(json.dumps({'paper_id':pid,'selected':[(x['scope_role'],safe_url(x['url'])) for x in chosen]},ensure_ascii=False));p.close()
 finally:b.close()
