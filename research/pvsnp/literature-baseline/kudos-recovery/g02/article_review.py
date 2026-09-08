"""Inspect the observed digitally typeset journal first-page/citation format."""
import re,fitz
from response_recovery import norm
from recovery import doi_key
def inspect_article(p,path):
 if p.get('record_type')!='article' or not p.get('identifiers',{}).get('doi'):return None
 publication=p.get('publication',{});pages=publication.get('pages') or []
 if isinstance(pages,str):pages=[pages]
 numbers=re.findall(r'\d+',' '.join(pages));volumes=publication.get('volume') or []
 if isinstance(volumes,str):volumes=[volumes]
 if len(numbers)!=2 or len(volumes)!=1:return None
 start,end=map(int,numbers)
 with fitz.open(path) as doc:
  if doc.needs_pass or len(doc)!=end-start+1:return None
  first=doc[0].get_text();last=doc[-1].get_text();blocks=doc[0].get_text('blocks')
  if norm(p['title']) not in norm(first[:600]):return None
  header=first.split('ABSTRACT',1)[0]
  for author in p.get('authors',[]):
   surname=norm(author.split(',')[0] if ',' in author else author.split()[0])
   if not re.search(r'(?<!\w)'+re.escape(surname)+r'(?!\w)',norm(header)):return None
  if not p.get('authors'):return None
  observed={doi_key(v) for v in re.findall(r'10\.\d{4,9}/[^\s<>()]+',first)}
  if not observed.intersection(doi_key(v) for v in p['identifiers']['doi']):return None
  if not re.search(r'\b'+re.escape(str(volumes[0]))+r'\s*\(\s*'+str(p['year'])+r'\s*\)',first):return None
  if not re.search(r'\b'+str(start)+r'\s*[-–]\s*'+str(end)+r'\b',first):return None
  if not re.search(r'(?m)^\s*'+str(end)+r'\s*$',last):return None
  result={'page_count':len(doc),'page_range':[start,end],'reason':'First-page title, all author surnames, printed DOI, journal volume/publication year, printed range, PDF page count and final printed page match. Received year is not substituted for publication year.','abstract_text':None,'abstract_bbox':None}
  label=next((i for i,b in enumerate(blocks) if b[4].strip()=='ABSTRACT'),None)
  stop=next((i for i,b in enumerate(blocks) if b[4].lstrip().startswith('Key words:')),None)
  if label is not None and stop is not None and stop>label+1:
   selected=blocks[label:stop];result['abstract_text']='\n'.join(b[4].strip() for b in blocks[label+1:stop])
   result['abstract_bbox']=[min(b[0] for b in selected)-3,min(b[1] for b in selected)-3,max(b[2] for b in selected)+3,max(b[3] for b in selected)+3]
  return result
