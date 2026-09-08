import json
from playwright.sync_api import sync_playwright
import resume
pid='VER-03d4f40f5e02f445ed375c27'
p=next(json.loads(l) for l in (resume.BASE/resume.ASSIGN['members_path']).read_text(encoding='utf-8').splitlines() if pid in l)
r=resume.new_result(p);t=resume.task(r,'source','https://www2.stat.duke.edu/~sayan/ambrosio.pdf')
run_path,record=resume.manifest(['test_live_pdf_fallback.py'])
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='chrome',headless=True);c=b.new_context(storage_state=resume.ASSIGN['browser_state'])
 resume.visit_source(c,p,r,t,record['metrics']);b.close()
resume.store_json(run_path,record)
assert r.get('fulltext_candidates'),'Actual observed Duke PDF URL was rendered as empty browser viewer and not recovered'
print(json.dumps({'passed':True,'candidate':r['fulltext_candidates'][0]['artifact']['path'],'pages':r['fulltext_candidates'][0]['page_count']}))
