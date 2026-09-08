"""Observed institutional Springer search and whole-book download; review follows."""
import json
import pymupdf
from collect import BASE,WORK,artifact,save_json,norm,pdf_valid,get_download,safe_url

SEED='https://link-springer-com.libproxy.knu.ac.kr/'

def book_pdf_link(links):
    return next((x for x in links if ' '.join(x.get('text','').split()).lower()=='download book pdf'),None)

def collect(context,page,paper):
    pid=paper['paper_id'];r=json.loads((WORK/'results'/f'{pid}.json').read_text());doi=paper['identifiers']['doi'][0]
    page.goto(SEED,wait_until='domcontentloaded');box=page.locator('input[name=query]:visible').first;box.fill(doi);box.press('Enter');page.wait_for_load_state('domcontentloaded');page.wait_for_timeout(1200)
    body=page.locator('body').inner_text();r['evidence'].append(artifact(pid,'springer-search.txt',body,page.url,kind='search-results'));r['attempts'].append({'method':'playwright','query':doi,'url':safe_url(page.url),'outcome':'Actual Springer search UI DOI query'})
    links=page.locator('a[href]').evaluate_all('(es)=>es.map(e=>({text:e.innerText,url:e.href}))');target=next((a for a in links if '/book/' in a['url'] and doi in a['url']),None)
    if not target:return r
    page.goto(target['url'],wait_until='domcontentloaded');page.wait_for_timeout(1200);body=page.locator('body').inner_text();r['evidence'].append(artifact(pid,'springer-institution-detail.txt',body,page.url,kind='publisher-page'));r['attempts'].append({'method':'playwright','query':doi,'url':safe_url(page.url),'outcome':'Opened target title link from actual Springer DOI search'})
    if norm(paper['title']) not in norm(body) or not all(norm(a) in norm(body) for a in paper.get('authors',[])):
        r['springer_review']='Observed book title/editor metadata requires comparison';return r
    r['identity']={'status':'confirmed','reason':'Institutional Springer target book page title/subtitle, input DOI, editor names and year/edition metadata observed; exact displayed metadata preserved.'}
    links=page.locator('a[href]').evaluate_all('(es)=>es.filter(e=>/pdf|download/i.test(e.innerText+e.getAttribute("href"))).map(e=>({text:e.innerText,url:e.href}))');r['evidence'].append(artifact(pid,'springer-download-links.json',json.dumps([dict(a,url=safe_url(a['url'])) for a in links],ensure_ascii=False,indent=2),page.url,'application/json','observed-source-links'))
    link=book_pdf_link(links)
    if link:
        response=get_download(context,link['url'],r['attempts'],doi);data=response.body()
        if pdf_valid(data):
            ar=artifact(pid,'springer-whole-book.pdf',data,link['url'],'application/pdf','pending-bibliographic-verification');r['evidence'].append(ar)
            with pymupdf.open(stream=data,filetype='pdf') as doc:
                preview='\n'.join(doc[i].get_text() for i in range(min(4,len(doc))));pages=len(doc)
            r['evidence'].append(artifact(pid,'springer-book-first-pages.txt',preview,link['url'],kind='pdf-extract'))
            r['fulltext']={'status':'unresolved','reason':'Observed Download book PDF acquired; first/final pages, edition and full book boundary require worker review','candidate_pages':pages}
    return r
