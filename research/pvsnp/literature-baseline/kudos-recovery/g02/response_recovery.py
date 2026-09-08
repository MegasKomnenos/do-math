"""Parse only responses caused by an observed Summon UI search."""
import re,unicodedata,time,weakref,html
# Observed UI asset applies leading debounce(runSearch,500,true).
_LAST_SUBMIT=weakref.WeakKeyDictionary()
SUBMIT_INTERVAL_SECONDS=0.55
from urllib.parse import parse_qs
from recovery import doi_key
FIELDS=['title','full_title','dois','isbn','isbns','eisbns','authors','editors','corporate_authors','publication_years','publication_date','content_type','content_types','abstracts','page_count','page_counts','pages','start_pages','end_pages','volumes','issues','publication_title','publishers','publisher','genres','editions','edition','edition_statement','link','fulltext_link','link_to_html','uris','open_access_link']

def display_text(s):
 return re.sub(r'</?(?:mark|i|b|em|strong)(?:\s+[^<>]*?)?>','',html.unescape(str(s)),flags=re.I)

def norm(s):
 s=unicodedata.normalize('NFKD',display_text(s)).lower().replace('ø','o').replace('ł','l')
 s=''.join(c for c in s if not unicodedata.combining(c))
 return ' '.join(re.findall(r'\w+',s))

def document_matches(p,d):
 wanted_raw=display_text(p['title']);actual_raw=display_text(d.get('full_title') or d.get('title') or '')
 if re.search(r'<(?:mml:)?math\b|<mml:',wanted_raw+actual_raw,re.I) and wanted_raw!=actual_raw:return False
 wanted=norm(wanted_raw);actual=norm(actual_raw)
 if not wanted or not actual or not (wanted==actual or wanted.startswith(actual+' ') or actual.startswith(wanted+' ') or wanted.replace(' ','')==actual.replace(' ','')):return False
 year=str(p.get('year') or '')
 if not year or year not in [str(v) for v in d.get('publication_years',[])]:return False
 observed=d.get('authors',[])
 if not p.get('authors') or not observed:return False
 for author in p['authors']:
  surname=norm(author.split(',')[0] if ',' in author else author.split()[0])
  if not surname or not any(re.search(r'(?<!\w)'+re.escape(surname)+r'(?!\w)',norm(a.get('surname') or a.get('fullname',''))) for a in observed):return False
 kind=' '.join([str(d.get('content_type') or '')]+[str(v) for v in d.get('content_types',[])]).lower();ptype=p.get('record_type')
 if ptype in ('book','proceedings') and not any(v in kind for v in ('book','conference proceeding')):return False
 if ptype=='article' and not any(v in kind for v in ('article','journal','magazine')):return False
 if ptype=='incollection' and 'chapter' not in kind:return False
 if ptype=='inproceedings' and not any(v in kind for v in ('conference','proceeding','article')):return False
 expected=p.get('identifiers',{})
 dois=expected.get('doi',[]);observed_dois=d.get('dois') or []
 isbn=lambda v:re.sub('[^0-9Xx]','',str(v)).upper()
 observed_isbns=(d.get('isbns') or [])+(d.get('eisbns') or [])+([d['isbn']] if isinstance(d.get('isbn'),str) else [])
 isbn_match=bool(set(map(isbn,expected.get('isbn',[]))).intersection(map(isbn,observed_isbns)))
 if dois and observed_dois:
  if not set(map(doi_key,dois)).intersection(map(doi_key,observed_dois)):return False
 elif (dois or expected.get('isbn')) and not isbn_match:
  if expected.get('isbn') and observed_isbns:return False
  # Missing source identifiers are not conflicting identifiers. A library's
  # double-parenthesized book classification is not part of the work title.
  bibliographic_title=norm(re.sub(r'\s*\(\(Book\b.*?\)\)\s*$','',actual_raw,flags=re.I))
  if wanted!=bibliographic_title:return False
 elif not dois and not expected.get('isbn') and wanted!=actual:
  # A separated subtitle needs independent volume and page anchors.
  if not (p.get('publication',{}).get('volume') and d.get('volumes') and p.get('publication',{}).get('pages') and d.get('start_pages') and d.get('end_pages')):return False
 pub=p.get('publication',{})
 for source,target in [('volume','volumes'),('issue','issues')]:
  values=pub.get(source); values=values if isinstance(values,list) else [values] if values else []
  if values and d.get(target) and not set(map(str,values)).intersection(map(str,d[target])):return False
 if ptype in ('article','incollection','inproceedings'):
  pg=pub.get('pages');pg=' '.join(pg) if isinstance(pg,list) else str(pg or '')
  parts=re.findall(r'\d+',pg)
  if len(parts)==2:
   if d.get('start_pages') and parts[0] not in [str(v) for v in d['start_pages']]:return False
   if d.get('end_pages') and parts[1] not in [str(v) for v in d['end_pages']]:return False
 return True

def validate_response(payload,query):
 q=payload.get('query',{})
 if q.get('original_query')!=query:raise ValueError('Response belongs to a different UI query')
 if parse_qs(q.get('query_string','')).get('s.ho')!=['f']:raise ValueError('Response excludes non-holdings')
 if not isinstance(payload.get('documents'),list):raise ValueError('Missing response document list')

def select_documents(paper,payload,query):
 validate_response(payload,query)
 return [d for d in payload['documents'] if document_matches(paper,d)]

def selected_payload(payload):
 return {'capture_kind':'selected-fields-from-observed-ui-response','ui_retry_observations':payload.get('_ui_retry_observations',[]),'query':payload['query'],'record_count':payload['record_count'],'documents':[{k:d[k] for k in FIELDS if k in d} for d in payload['documents']]}

def search_ui(page,query):
 from playwright.sync_api import TimeoutError as PlaywrightTimeout
 from urllib.parse import urlsplit
 observations=[]
 for attempt in range(2):
  page.get_by_text('Done Loading Results',exact=True).first.wait_for(state='attached')
  chosen=page.locator('input[id^=searchBox_]:visible').first
  box_id=chosen.get_attribute('id')
  box=page.locator('[id="'+box_id+'"]')
  box.fill(query)
  remaining=_LAST_SUBMIT.get(page,0)+SUBMIT_INTERVAL_SECONDS-time.monotonic()
  if remaining>0:page.wait_for_timeout(remaining*1000)
  try:
   with page.expect_response(lambda r:'/api/search' in r.url,timeout=30000) as response:
    box.locator('xpath=ancestor::form[1]').locator('button[type=submit][aria-label="검색"]:visible').click()
    _LAST_SUBMIT[page]=time.monotonic()
  except PlaywrightTimeout:
   fragment=urlsplit(page.url).fragment
   params=parse_qs(fragment.split('?',1)[1]) if '?' in fragment else {}
   observations.append({'event':'No observed search response after submit button click','requested_query':query,'displayed_url_query':params.get('q',[]),'input_value':box.input_value() if box.count() else None,'attempt':attempt+1})
   if attempt==0:continue
   raise RuntimeError('UI response timeout: '+str(observations))
  response=response.value
  if response.status!=200:raise RuntimeError('Observed UI search HTTP status '+str(response.status))
  payload=response.json();validate_response(payload,query)
  page.wait_for_function('(q)=>document.title.includes(q)',arg=query)
  page.get_by_text('Done Loading Results',exact=True).first.wait_for(state='attached')
  if observations:payload['_ui_retry_observations']=observations
  return payload

def primary_identifier(p):
 ids=p.get('identifiers',{});values=ids.get('doi',[]) or ids.get('isbn',[])
 return values[0] if values else None
def batch_query(papers):
 import json
 return ' OR '.join(json.dumps(primary_identifier(p),ensure_ascii=False) for p in papers)
def batch_truncated(payload):return int(payload.get('record_count',0))>len(payload.get('documents',[]))
