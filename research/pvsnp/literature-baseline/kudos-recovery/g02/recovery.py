"""Boundary checks for the observed KUDOS/MathSciNet recovery path."""
import re
import unicodedata

def doi_key(value):
    match=re.search(r'10\.\d{4,9}/[^\s]+',value.lower())
    return match.group(0).rstrip('/') if match else value.lower().strip()

def words(value):
    return ' '.join(re.findall(r'\w+',unicodedata.normalize('NFKD',value).lower()))

def identity_matches(candidate, body, link):
    expected=candidate.get('identifiers',{}).get('doi',[])
    if link and expected and doi_key(link) not in [doi_key(v) for v in expected]:
        return False
    title=words(candidate['title'])
    return bool(title and title in words(body) and (not expected or (link and doi_key(link) in [doi_key(v) for v in expected])))

def review_kind(body):
    if re.search(r'From the (?:text|preface|introduction)',body,re.I): return 'text-excerpt'
    if re.search(r'(?:Authors?.? abstract|From the abstract|Summary:)',body,re.I): return 'author-summary'
    return 'review-or-summary'

def barrier(body):
    if 'Unusual Traffic Detected' in body: return 'traffic-restriction'
    if re.search(r'please (?:log in|sign in) to access',body,re.I): return 'login-required'
    return None

def pdf_valid(data):
    if not data.startswith(b'%PDF-'): return False
    import fitz
    try:
        with fitz.open(stream=data,filetype='pdf') as doc: return doc.page_count>0 and not doc.needs_pass
    except Exception: return False

def needs_work(result):
    return not result or any(result.get(k,{}).get('status')=='unresolved' for k in ('identity','abstract','fulltext'))

def summon_abstract(page):
    node=page.locator('#quick-look-abstract [data-aid=abstract]')
    return node.inner_text().strip() if node.count() else ''
def zero_results(body): return '관련된 검색결과가 없습니다' in body

def source_links(page):
    return page.locator('a[data-aid="full text"], a[href*="doi.org/"]').evaluate_all("es => es.map(e => ({text: e.textContent.trim(), url: e.getAttribute('href')})).filter(e => /^https?:/.test(e.url))")

def mathscinet_section(page,mr):
    display='MR'+str(int(mr[2:])).zfill(7)
    heading=page.locator('h1').filter(has_text=re.compile('^'+re.escape(display)+r'(?:\(|\s|$)'))
    heading.first.wait_for(state='visible')
    if page.locator('main h1').filter(has_text=re.compile(r'^MR\d+')).count()==1 and heading.count()==1:
        section=page.locator('main')
    else:
        section=page.locator('div.article').filter(has=heading)
    section.wait_for(state='visible')
    section.get_by_text('Classifications',exact=True).wait_for(state='visible')
    return section
