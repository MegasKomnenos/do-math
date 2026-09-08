"""Read-only stage audit of retained book PDFs under the current book rule."""
import json,re,hashlib
from collections import Counter
from pathlib import Path
import pymupdf
from response_recovery import norm
from pdf_review import book_match
from copyright_notice import matches_year
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]

def inspect(p,c):
 result={'paper_id':p['paper_id'],'title':p['title'],'candidate_status':c.get('status'),'artifact':c['artifact'],'checks':{}}
 ids=p.get('identifiers',{}).get('isbn',[]);extent=p.get('publication',{}).get('pages') or []
 if isinstance(extent,str):extent=[extent]
 numbers=re.findall(r'\d+',' '.join(extent));result['checks']['isbn_input']=bool(ids);result['checks']['extent_input']=len(numbers)==1
 if not ids or len(numbers)!=1:return result
 expected_pages=int(numbers[0]);path=BASE/c['artifact']['path']
 with pymupdf.open(path) as doc:
  front=[doc[i].get_text() for i in range(min(len(doc),10))];text='\n'.join(front);expected=norm(p['title']);title_pages=[i for i,v in enumerate(front) if expected in norm(v)]
  surnames=[norm(a.split(',')[0] if ',' in a else a.split()[0]) for a in p.get('authors',[])]
  byline=[i for i in title_pages if surnames and all(re.search(r'(?<!\w)'+re.escape(s)+r'(?!\w)',norm(front[i])) for s in surnames)]
  isbn_lines=[re.sub(r'[^0-9X]','',v.upper()) for v in text.splitlines() if 'ISBN' in v.upper()]
  result['checks'].update(extent=not doc.needs_pass and expected_pages<=len(doc)<=expected_pages+60,title=bool(title_pages),author_byline=bool(byline),copyright=matches_year(text,p.get('year')),isbn=any(re.sub(r'[^0-9X]','',v.upper()) in line for v in ids for line in isbn_lines),last_page=any(re.search(r'(?m)^\s*'+str(expected_pages)+r'\s*$',doc[i].get_text()) for i in range(max(0,len(doc)-3),len(doc))))
  result.update(physical_pages=len(doc),expected_body_pages=expected_pages,copyright_lines=[v for v in text.splitlines() if '©' in v or re.search('copyright',v,re.I)][:6],isbn_lines=[v for v in text.splitlines() if 'ISBN' in v][:6])
 result['current_rule_accepts']=bool(book_match(p,path));return result

if __name__=='__main__':
 assignment=json.loads((ROOT/'assignment.json').read_text(encoding='utf-8-sig'));papers={p['paper_id']:p for p in [json.loads(line) for line in (BASE/assignment['members_path']).read_text(encoding='utf-8-sig').splitlines()]};rows=[]
 for file in (ROOT/'results').glob('*.json'):
  record=json.loads(file.read_text(encoding='utf-8'));paper=papers[record['paper_id']]
  if paper.get('record_type')!='book':continue
  for candidate in record.get('fulltext_candidates',[]):rows.append(inspect(paper,candidate))
 order=['isbn_input','extent_input','extent','title','author_byline','copyright','isbn','last_page']
 for row in rows:row['first_failure']=next((key for key in order if row['checks'].get(key) is False),None)
 summary={}
 for name,selected in [('all_book_candidates',rows),('pending_review',[r for r in rows if r['candidate_status']=='needs_review'])]:
  summary[name]={'candidate_count':len(selected),'paper_count':len({r['paper_id'] for r in selected}),'first_failure':dict(Counter(r['first_failure'] or 'passed' for r in selected)),'all_failed_checks':{key:sum(r['checks'].get(key) is False for r in selected) for key in order}}
 output={'rule_sha256':hashlib.sha256((ROOT/'pdf_review.py').read_bytes()).hexdigest(),'summary':summary,'candidates':rows};(ROOT/'book-pdf-stage-audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
