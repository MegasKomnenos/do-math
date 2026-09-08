import argparse,json,re,time
from pathlib import Path
from playwright.sync_api import sync_playwright
import pymupdf
from collect import BASE,WORK,RAW,artifact,save_json,save_progress,norm,pdf_valid,publisher_failure,get_download,nonpdf_body

SEED='https://dl-acm-org.libproxy.knu.ac.kr/doi/abs/10.1145/2488608.2488677'

def pdf_abstract(text):
    m=re.search(r'(?m)^\s*(?:ABSTRACT|Abstract)\s*[:.]?\s+(.*?)(?=\n\s*(?:KEY WORDS|Keywords|Key Words|Categories and Subject|CCS CONCEPTS|CR CATEGORIES|1[. ]+Introduction|1[. ]+INTRODUCTION))',text,re.S)
    return m.group(1).strip() if m and len(m.group(1).strip())>40 else None

def pdf_identity(paper,first_page,pages):
    header=re.split(r'(?im)^\s*(?:References|Bibliography)\s*$',first_page)[0]
    if norm(paper['title']) not in norm(header): return False
    if any(norm(a.split(',')[0]) not in norm(header) for a in paper.get('authors',[])):return False
    if paper.get('year') and str(paper['year']) not in header:return False
    span=re.fullmatch(r'\s*(\d+)\s*[–—-]\s*(\d+)\s*',str(paper.get('publication',{}).get('pages','')))
    if span and pages!=int(span[2])-int(span[1])+1:return False
    return True

def select_title_link(paper,links):
    dois=paper.get('identifiers',{}).get('doi',[])
    if dois:links=[x for x in links if any(d.casefold() in x['url'].casefold() for d in dois)]
    direct=next((x for x in links if norm(x['text'])==norm(paper['title']) and '/doi/' in x['url']),None)
    if direct:return direct
    groups={}
    for link in links:
        if '/doi/' in link['url'] and link['text'].strip():groups.setdefault(link['url'],[]).append(link['text'])
    for url,parts in groups.items():
        title=''.join(dict.fromkeys(parts))
        if norm(title)==norm(paper['title']):return {'url':url,'text':title}
    return None

def collect(c,s,paper):
    pid=paper['paper_id'];out=WORK/'results'/f'{pid}.json'
    r=json.loads(out.read_text()) if out.exists() else {'schema_version':'kudos-recovery-result/1','paper_id':pid,'version_sha256':paper['version_sha256'],'metadata':{k:paper.get(k) for k in ['title','authors','year','identifiers']},'identity':{'status':'unresolved','reason':'ACM target detail pending'},'abstract':{'status':'unresolved','reason':'ACM target abstract pending'},'fulltext':{'status':'unresolved','reason':'ACM target fulltext pending'},'attempts':[],'evidence':[]}
    doi=(paper.get('identifiers',{}).get('doi') or [''])[0]
    term=doi or paper['title']
    # Search-result pages retain prior query chips outside the text input.
    # A fresh observed article page provides an empty global search form.
    s.goto(SEED,wait_until='domcontentloaded')
    s.locator('input[name=AllField]:visible').first.fill(term);s.locator('input[name=AllField]:visible').first.press('Enter');s.wait_for_load_state('domcontentloaded');s.wait_for_timeout(1200)
    body=s.locator('body').inner_text();r['evidence'].append(artifact(pid,'acm-search.txt',body,s.url,kind='search-results'))
    r['attempts'].append({'method':'playwright','query':term,'url':s.url,'outcome':'Actual ACM search UI results preserved'})
    links=s.locator('a[href]').evaluate_all('(es)=>es.map(e=>({text:e.innerText,url:e.href}))')
    target=select_title_link(paper,links)
    if not target:
        r['identity']={'status':'unresolved','reason':'ACM UI search did not yet yield exact target title; further title/author search required'};return r
    s.goto(target['url'],wait_until='domcontentloaded');s.wait_for_timeout(1000)
    body=s.locator('body').inner_text();h1=' '.join(s.locator('h1').all_inner_texts())
    r['evidence'].append(artifact(pid,'acm-detail.txt',body,s.url,kind='publisher-page'))
    r['attempts'].append({'method':'playwright','query':term,'url':s.url,'outcome':'Opened target title link from actual ACM search results'})
    if norm(paper['title']) not in norm(h1) or (doi and doi not in body):
        r['identity']={'status':'unresolved','reason':'ACM detail title or DOI does not match target'};return r
    r['identity']={'status':'confirmed','reason':'Actual ACM publisher h1 matches target title and publisher DOI matches; author/date/page metadata preserved in acm-detail.txt'}
    abstracts=s.locator('#abstracts').inner_text().strip() if s.locator('#abstracts').count() else ''
    if abstracts and len(abstracts)>50:
        r['abstract']={'status':'found','artifacts':[artifact(pid,'abstract.txt',abstracts,s.url)],'source_kind':'Publisher target abstracts container; excludes recommendation snippets'}
    links=s.locator('a[href]').evaluate_all('(es)=>es.filter(e=>e.href.includes("/doi/pdf/")).map(e=>({text:e.innerText,url:e.href}))')
    urls=list(dict.fromkeys(x['url'] for x in links if doi in x['url']))
    for url in urls:
        try:
            response=get_download(c,url,r['attempts'],term);data=response.body()
            r['attempts'].append({'method':'playwright','query':term,'url':url,'outcome':f'UI-observed PDF link received via browser context request: HTTP {response.status}, {len(data)} bytes, valid_pdf={pdf_valid(data)}'})
            if not pdf_valid(data):
                body=nonpdf_body(data)
                r['evidence'].append(artifact(pid,'acm-nonpdf-body.txt',body,url,kind='observed-nonpdf-response'))
                r['fulltext']={'status':'unresolved','reason':'Observed publisher PDF link returned non-PDF; additional access investigation required'};continue
            with pymupdf.open(stream=data,filetype='pdf') as doc:
                first='\n'.join(doc[i].get_text() for i in range(min(3,len(doc))));pages=len(doc)
                if not pdf_identity(paper,doc[0].get_text(),pages):
                    r['fulltext']={'status':'unresolved','reason':'PDF title extraction did not match; visual verification required'}
                    r['evidence'].append(artifact(pid,'pdf-pending.pdf',data,url,'application/pdf','pending-identity'))
                    r['evidence'].append(artifact(pid,'pdf-first-pages.txt',first,url,kind='pdf-extract'))
                    continue
                r['fulltext']={'status':'found','artifacts':[artifact(pid,'fulltext.pdf',data,url,'application/pdf')],'pages':pages,'validation':'Observed publisher target DOI PDF link; first-page title before references, author surnames and year match; page count matches target numeric page range where supplied'}
                r['evidence'].append(artifact(pid,'pdf-first-pages.txt',first,url,kind='pdf-extract'))
                if r['abstract']['status']!='found':
                    value=pdf_abstract(first)
                    if value:
                        r['abstract']={'status':'found','artifacts':[artifact(pid,'abstract.txt',value,url)],'extraction_quality':'raw_pdf_text_unreviewed','source_kind':'PDF text from explicit ABSTRACT heading to keyword/classification/introduction boundary','warning':'PDF text layer preserved verbatim; OCR or mathematical glyph errors may remain. Original PDF is authoritative.'}
                    else:r['abstract']={'status':'unresolved','reason':'Publisher HTML has no target abstract; PDF first pages preserved for explicit abstract-boundary reading'}
            break
        except Exception as e:r['fulltext']=publisher_failure(e)
    if not urls:r['fulltext']={'status':'unresolved','reason':'Target ACM page provides no observed PDF link; further reading required'}
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);ap.add_argument('--start',type=int,default=0);ap.add_argument('--only-link-misses',action='store_true');args=ap.parse_args()
    a=json.loads((WORK/'assignment.json').read_text());papers=[json.loads(x) for x in (BASE/a['members_path']).read_text().splitlines()]
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True);c=b.new_context(storage_state=a['browser_state']);s=c.new_page();s.goto(SEED);n=0
        for i,paper in enumerate(papers):
            if i<args.start or not any(d.startswith('10.1145/') for d in paper['identifiers'].get('doi',[])):continue
            out=WORK/'results'/f"{paper['paper_id']}.json"
            if args.only_link_misses:
                if not out.exists():continue
                previous=json.loads(out.read_text())
                if any('/acm-detail' in e['path'] for e in previous.get('evidence',[])):continue
            if out.exists() and json.loads(out.read_text()).get('fulltext',{}).get('status')=='found':continue
            save_progress('ACM collecting',i,paper,len(papers),'python research/pvsnp/literature-baseline/kudos-recovery/g05/acm_collect.py')
            try:
                r=collect(c,s,paper);save_json(out,r);n+=1;print(json.dumps({'index':i,'paper_id':paper['paper_id'],'abstract':r['abstract']['status'],'fulltext':r['fulltext']['status']}),flush=True)
            except Exception as e:
                print(json.dumps({'index':i,'error':type(e).__name__}),flush=True)
                s.goto(SEED,wait_until='domcontentloaded')
            if args.limit and n>=args.limit:break
        b.close()

if __name__=='__main__':main()
