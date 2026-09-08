"""Choose document-bound download controls; unbound links remain review work."""
import re
from urllib.parse import urlsplit,unquote,parse_qs

PDF_CONTROL=re.compile(r'^\s*(?:(?:view|download|get)\s+)?(?:(?:full\s+text|full\s+issue|book|chapter|article|issue)\s+)?PDF(?:\s*\([^)]*\))?\s*$',re.I)
ACCOUNT_CONTROL=re.compile(r'^(?:save\b|log\s*in\b|sign\s*in\b|register\b|buy\b|purchase\b|add\s+to\s+(?:cart|binder))',re.I)

def classify(paper,page_url,link,*,title_matches=False,observed_dois=(),reviewed_parents=()):
    url=link.get('url','');label=' '.join(link.get('text','').split());s=urlsplit(url);path=unquote(s.path);source=unquote(urlsplit(page_url).path)
    if s.scheme not in {'http','https'}:return 'excluded','Not an HTTP(S) document link'
    if ACCOUNT_CONTROL.search(label) or re.search(r'/(?:save-research|login|checkout|oauth|auth)(?:/|$)',path,re.I):return 'excluded','Account/save/purchase action is not a document download'
    for parent in reviewed_parents:
        if parent.get('url')==url and parent.get('target_paper_id')==paper.get('paper_id') and parent.get('review_status')=='verified' and parent.get('reason') and parent.get('evidence_paths'):
            return 'parent','Explicit reviewed containing-volume link; acquired file still requires target boundary review'
    query={k.casefold():[v.casefold() for v in values] for k,values in parse_qs(s.query).items()}
    if 'reference' in query.get('linklocation',[]):return 'excluded','Explicit Reference link location is not target full text, regardless of linkSource'
    if re.search(r'\.(?:zip|gz|tgz|tar|epub|bib|ris|enw)$',path,re.I):return 'excluded','Archive, ebook package or citation export is not a direct PDF'
    if link.get('excluded_context'):return 'excluded','Actual reference/recommendation/navigation context is outside target download scope'
    if not (PDF_CONTROL.fullmatch(label) or re.search(r'\.pdf$|/(?:pdf|pdfft)(?:/|$)',path,re.I)):
        return 'excluded','No direct PDF resource or explicit PDF control; a -pdf catalogue slug is not a PDF'
    dois=list(paper.get('identifiers',{}).get('doi',[]))
    if not dois and title_matches:dois=list(observed_dois)
    bound=any(re.search(re.escape(doi)+r'(?=$|\.pdf$|/)',path,re.I) for doi in dois)
    source_dois={x.casefold() for x in observed_dois};wanted={x.casefold() for x in dois}
    pii=re.search(r'/science/article/(?:abs/)?pii/([^/]+)$',source)
    if not bound and pii and title_matches and source_dois.intersection(wanted):
        bound=bool(re.search(r'/pii/'+re.escape(pii[1])+r'(?:/|$)',path))
    nips=re.search(r'/(?:paper|paper_files/paper)/\d{4}/(?:hash|file)/([a-f0-9]{32})',source,re.I)
    if not bound and nips and title_matches:bound=bool(re.search('/'+nips[1]+r'(?:-|\.|/|$)',path,re.I))
    arxiv=re.search(r'/(?:abs|pdf)/(\d{4}\.\d+(?:v\d+)?)',source)
    if not bound and arxiv and title_matches and 'arxiv.org' in (s.hostname or ''):bound=bool(re.search(r'/pdf/'+re.escape(arxiv[1])+r'(?:\.pdf)?$',path))
    if not bound:
        other_doi=re.search(r'(10\.\d{4,9}/.+)$',path)
        if dois and other_doi:return 'excluded','Resource carries a different DOI, not the assigned target'
        if path.endswith('/'):return 'excluded','Unbound directory/index is not an individual document'
        return 'needs_review','PDF-like control has no target identifier or reviewed containing-volume binding'
    if re.search(r'preview|front.?matter|/bfm:',label+' '+path,re.I):return 'preview','Target-bound preview/front matter is additional material, not the full target'
    if re.search(r'supplement|poster|slides',label+' '+path,re.I):return 'supplement','Target-bound supplementary/presentation material is not the full article'
    if re.search(r'/(?:book|proceedings)/',source):return 'container','Target book/proceedings PDF needs complete-container review'
    return 'primary','PDF control is bound to the target DOI or observed target document identifier'

def select_downloads(paper,page_url,links,**kwargs):
    selected=[];seen=set()
    for link in links:
        role,reason=classify(paper,page_url,link,**kwargs)
        if role not in {'primary','container','preview','supplement','parent'} or link.get('url') in seen:continue
        seen.add(link['url']);selected.append(dict(link,scope_role=role,scope_reason=reason))
    return selected


def observe_links(page):
    return page.locator('a[href]').evaluate_all('''(es)=>es.filter(e=>/pdf|download|save chapter/i.test(e.innerText+e.getAttribute("href"))).map(e=>{const p=e.closest('[class*="references"],[id^="ref-"],.bibliography,[class*="recommend"],[class*="related"],footer');return {text:e.innerText,url:e.href,excluded_context:p?{tag:p.tagName,id:p.id,classes:p.className}:null}})''')
