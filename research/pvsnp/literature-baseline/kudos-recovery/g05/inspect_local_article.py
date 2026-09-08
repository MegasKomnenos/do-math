import json,os,sys,time,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from collect import BASE,WORK,artifact,save_json
import fulltext_html
pid='VER-2bb97c857e10d1adb8a73f9a';root=BASE/'intake/kudos-recovery/g05'/pid
run=WORK/'runs'/time.strftime('%Y%m%d-%H%M%S-offline-html');run.mkdir()
save_json(run/'manifest.json',{'pid':os.getpid(),'argv':sys.argv,'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in WORK.glob('*.py')}})
parts={name:(root/f'source-dom-{name}.html').read_text() for name in ['body','abstracts','author-group','bibliography']}
value=fulltext_html.document('Reachability in arborescence packings',parts)
asset=artifact(pid,'fulltext-offline-candidate.html',value,'https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/S0166218X22001809','text/html','publisher-fulltext-html-candidate')
with sync_playwright() as pw:
 b=pw.firefox.launch(headless=True);c=b.new_context(offline=True,viewport={'width':1250,'height':1000});page=c.new_page();requests=[];page.on('request',lambda request:requests.append(request.url) if request.url.startswith(('http:','https:')) else None)
 page.goto((BASE/asset['path']).as_uri());page.screenshot(path=str(root/'offline-article-first-v2.png'))
 page.locator('.formula').first.screenshot(path=str(root/'offline-article-formula-v2.png'))
 last=page.locator('#references li').last;last.scroll_into_view_if_needed();page.screenshot(path=str(root/'offline-article-references-v2.png'))
 proof={'network_offline':True,'http_requests':requests,'math_count':page.locator('#body math').count(),'visible_math':page.locator('#body math').evaluate_all('(es)=>es.filter(e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0).length'),'body_headings':page.locator('#body h2,#body h3').all_inner_texts(),'reference_items':page.locator('#references ol.references > li').count(),'reference_last':last.inner_text(),'body_last':page.locator('#body').inner_text()[-300:],'image_count':page.locator('#body img').count(),'asset':asset}
 b.close()
 print(json.dumps(proof,ensure_ascii=False));artifact(pid,'offline-article-validation.json',json.dumps(proof,ensure_ascii=False,indent=2),asset['url'],'application/json','actual-offline-article-validation')
