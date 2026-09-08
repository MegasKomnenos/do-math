"""Conservative complete-book check for digitally readable title/copyright pages."""
import re,fitz
from response_recovery import norm
from copyright_notice import matches_year
def book_match(p,path):
 if p.get('record_type')!='book':return None
 ids=p.get('identifiers',{}).get('isbn',[])
 if not ids:return None
 extent=p.get('publication',{}).get('pages') or []
 if isinstance(extent,str):extent=[extent]
 numbers=re.findall(r'\d+',' '.join(extent))
 if len(numbers)!=1:return None
 body_pages=int(numbers[0]);expected=norm(p['title'])
 with fitz.open(path) as doc:
  if doc.needs_pass or not body_pages<=len(doc)<=body_pages+60:return None
  text=[doc[i].get_text() for i in range(min(len(doc),10))]
  title_pages=[]
  for i,page in enumerate(text):
   normalized=norm(page)
   if expected not in normalized:continue
   surnames=[norm(a.split(',')[0] if ',' in a else a.split()[0]) for a in p.get('authors',[])]
   if surnames and all(re.search(r'(?<!\w)'+re.escape(s)+r'(?!\w)',normalized) for s in surnames):title_pages.append(i+1)
  if not title_pages:return None
  front='\n'.join(text)
  if not matches_year(front,p.get('year')):return None
  isbn_lines=[re.sub(r'[^0-9X]','',line.upper()) for line in front.splitlines() if 'ISBN' in line.upper()]
  if not any(re.sub(r'[^0-9X]','',v.upper()) in line for v in ids for line in isbn_lines):return None
  if not any(re.search(r'(?m)^\s*'+str(body_pages)+r'\s*$',doc[i].get_text()) for i in range(max(0,len(doc)-3),len(doc))):return None
  return {'page_count':len(doc),'title_pages':title_pages,'printed_body_last_page':body_pages,'reason':'Digital book title and all author surnames on the same preliminary page, copyright year, ISBN, expected body extent and last printed page independently match. Front/back matter and wrong-year candidates rejected by actual PDF regression tests.'}
