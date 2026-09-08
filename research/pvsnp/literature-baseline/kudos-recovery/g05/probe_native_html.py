import json,os,sys,time,hashlib,re
from pathlib import Path
from playwright.sync_api import sync_playwright
from collect import BASE,WORK,artifact,save_json,safe_url
import science_direct
pid=sys.argv[1] if len(sys.argv)>1 else 'VER-2bb97c857e10d1adb8a73f9a'
run=WORK/'runs'/time.strftime('%Y%m%d-%H%M%S-native-html-probe');run.mkdir()
save_json(run/'manifest.json',{'pid':os.getpid(),'argv':sys.argv,'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in WORK.glob('*.py')}})
r=json.loads((WORK/'results'/f'{pid}.json').read_text())
with sync_playwright() as pw:
 b=pw.firefox.launch(headless=True);c=b.new_context(storage_state='C:/math/.credentials/kudos-recovery/bootstrap.json')
 try:
  gateway=science_direct.institution_gateway(c);p=c.new_page();url=science_direct.source_url(r,r['metadata'],True);body,timed_out=science_direct.visit_body(p,url);p.wait_for_timeout(9000)
  body=p.locator('body').inner_text();e=artifact(pid,'full-html-probe-body.txt',body,p.url,kind='actual-full-html-probe');info={'url':safe_url(p.url),'gateway':gateway,'navigation_timed_out':timed_out,'body_artifact':e,'selectors':{},'headings':p.locator('h1,h2,h3').all_inner_texts()}
  for selector in ['article','#body','.Body','.ArticleBody','.Bibliography','#bibliography','.References','figure','.author-group','#abstracts']:
   nodes=p.locator(selector);info['selectors'][selector]={'count':nodes.count(),'nodes':[]}
   for node in nodes.all()[:3]:info['selectors'][selector]['nodes'].append(node.evaluate('(e)=>({tag:e.tagName,id:e.id,class:e.className,text_length:e.innerText.length,first:e.innerText.slice(0,100),last:e.innerText.slice(-150),images:e.querySelectorAll("img").length,math:e.querySelectorAll("math").length})'))
  refs=p.get_by_role('heading',name='References',exact=True)
  if refs.count()==1:
   info['reference_ancestors']=refs.evaluate('(e)=>{let a=e;return Array.from({length:4},()=>{let x={tag:a.tagName,id:a.id,class:a.className,length:a.innerText.length,children:Array.from(a.children).slice(0,8).map(c=>({tag:c.tagName,id:c.id,class:c.className}))};a=a.parentElement;return x})}')
  info['h1']=p.locator('h1').all_inner_texts()
  info['math_example']=p.locator('#body math').first.evaluate('(e)=>e.outerHTML') if p.locator('#body math').count() else None
  parts={}
  for selector in ['#body','#abstracts','.author-group','.bibliography','.references']:
   if p.locator(selector).count()==1:
    raw=p.locator(selector).inner_html()
    raw=re.sub(r'(https?://[^\s"?]+)\?[^\s"]+',r'\1',raw)
    parts[selector]=artifact(pid,'source-dom-'+selector.strip('#.')+'.html',raw,p.url,'text/html','actual-scholar-dom-query-redacted')
  info['parts']=parts
  proof=artifact(pid,'full-html-dom-observation.json' ,json.dumps(info,ensure_ascii=False,indent=2),p.url,'application/json','actual-full-html-dom-observation');print(json.dumps(info,ensure_ascii=False))
 finally:b.close()
