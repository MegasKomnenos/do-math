"""Select document recovery controls, excluding reference and catalog branches."""
import re
from urllib.parse import urlsplit,unquote,parse_qsl,urlencode,urlunsplit

CONTEXT_SELECTOR='[id*="reference"],[class*="reference"],[id*="bibliography"],[class*="bibliography"],[id^="ref-"],[id*="related"],[class*="related"],[id*="recommend"],[class*="recommend"],[class*="annotationLayer"],[data-annotation-id],footer'
LINK_SCRIPT='''es=>es.map(e=>{let p=e.closest('''+repr(CONTEXT_SELECTOR)+''');return {text:e.textContent.trim(),url:e.href,excluded_context:p?{tag:p.tagName,id:p.id,classes:p.className}:null}})'''
PRIVATE_KEYS={'_csrf','csrf','access_token','token','auth-callid'}

def public_link(link):
 value=dict(link);u=urlsplit(value['url']);query=parse_qsl(u.query,keep_blank_values=True);clean=[(key,text) for key,text in query if key.lower() not in PRIVATE_KEYS]
 if len(clean)!=len(query):value.update(url=urlunsplit(u._replace(query=urlencode(clean))),redacted_session_query=True)
 return value

def doi(url):
 match=re.search(r'10\.\d{4,9}/[^?#\s]+',unquote(url),re.I)
 if not match:return None
 return re.sub(r'(?:/pdf|[.]pdf|/html)$','',match[0].lower()).rstrip('/')

def pdf_route(url):
 path=urlsplit(url).path.lower()
 return bool(re.search(r'\.pdf$|/pdf(?:/|$)|/pdfdirect/|/epdf/|/content/pdf/|/download(?:/|$)',path))

def excluded(link,page_url=''):
 url=link.get('url','');label=' '.join(link.get('text','').split());path=urlsplit(url).path
 if not url.startswith(('https://','http://')):return 'Non-HTTP recovery target.'
 if re.match(r'^(?:save|share|cite|sign in|log in|register|my account|account|add to (?:cart|library))\b',label,re.I):return 'Save/share/citation/account action is outside document recovery.'
 if link.get('excluded_context'):return 'Link belongs to observed references, recommendations, related-content or footer context.'
 if any(key.lower()=='linklocation' and value.lower()=='reference' for key,value in parse_qsl(urlsplit(url).query,keep_blank_values=True)):return 'Publisher explicitly marks this linkout as a Reference location.'
 if any(key.lower() in PRIVATE_KEYS for key,value in parse_qsl(urlsplit(url).query,keep_blank_values=True)):return 'Session-bound download control requires actual source UI interaction.'
 if re.search(r'^/(?:ftp|bulk)(?:/|$)',path,re.I) or re.search(r'\bbulk\s+(?:download|export)|\bFTP\b',label,re.I):return 'Global bulk/FTP service, not the assigned document.'
 if re.search(r'\.(?:zip|tar|gz|tgz)(?:$|/)',path,re.I):return 'Archive file requires document-specific review; not an ordinary target PDF control.'
 if re.fullmatch(r'review pdf|references|cited by|table of contents|cover(?: image)?',label,re.I) or re.search(r'(?:export|download)\s+(?:a\s+)?citation',label,re.I):return 'Bibliographic or review apparatus.'
 if re.search(r'/(?:download/)?(?:cited-by|citation|bibtex|ris)(?:[/?]|$)',url,re.I):return 'Citation export route.'
 if 'perlego.com' in (urlsplit(url).hostname or '') and '/book/' in path:
  actual=re.search(r'/book/(\d+)',path);current=re.search(r'/book/(\d+)',urlsplit(page_url).path)
  if not (actual and current and actual[1]==current[1] and re.match(r'^(?:read|view|open)\b',label,re.I)):return 'Perlego product/navigation link; a -pdf title slug is not a download.'
 if label.lower()=='article' and page_url:
  target=doi(url);current=doi(page_url)
  if 'mathscinet' not in (urlsplit(page_url).hostname or '') and (not target or target!=current):return 'Generic Article link is not bound to the current document.'
 return None

def select_links(links,page_url=''):
 selected=[]
 for link in links:
  if excluded(link,page_url):continue
  label=' '.join(link.get('text','').split())
  control=bool(re.match(r'^(?:download|view|read|open)\s+(?:(?:the|this|a|all|full|entire|complete)\s+)*(?:pdf|full[ -]?text|articles?|chapters?|book|issue|volume|proceedings|online)\b',label,re.I))
  if label.lower()=='article' or pdf_route(link['url']) or control or re.fullmatch(r'PDF|Full.?text|원문(?:보기)?',label,re.I):selected.append(link)
 return selected

def download_kind(link):
 if 'perlego.com' in (urlsplit(link['url']).hostname or '') and '/book/' in urlsplit(link['url']).path:return 'source'
 return 'pdf' if pdf_route(link['url']) or re.search(r'\bPDF\b',link.get('text',''),re.I) else 'source'
