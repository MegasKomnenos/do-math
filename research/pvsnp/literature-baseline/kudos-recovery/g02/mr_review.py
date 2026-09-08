"""Check an MR-scoped bibliography and explicitly delimited complete summary."""
import re
from mr_fields import bibliography
from response_recovery import norm
from abstract_kind import classify
def inspect_mr(p,body):
 header=bibliography(p,body)
 if not header or re.search(r'\\[A-Za-z]|[=<>≤≥$]',p['title']):return None
 if norm(p['title']) not in norm(header) or not re.search(r'\b'+str(p.get('year'))+r'\b',header):return None
 if not p.get('authors'):return None
 for author in p['authors']:
  surname=norm(author.split(',')[0] if ',' in author else author.split()[0])
  if not re.search(r'(?<!\w)'+re.escape(surname)+r'(?!\w)',norm(header)):return None
 result={'identity':True,'abstract':None,'reason':'Exact assigned MR identifier selected its bibliographic header; title, all author surnames and publication year match. Shared review text is outside identity scope.'}
 if len(re.findall(r'(?m)^MR\d+',body))!=1:return result
 match=re.search(r"(?s)\nSummary\s*\nSummary:\s*``(.*?)''\s*$",body)
 if match and classify(match.group(1))=='database_indexing_abstract':result['abstract']=match.group(1)
 return result
