"""Read bibliographic header only from an actual captured MR detail."""
import re
def bibliography(p,body):
 mr=next((s['record_id'] for s in p.get('source_records',[]) if s.get('record_id','').startswith('MR')),None)
 if not mr:return ''
 token=r'MR0*'+str(int(mr[2:]))+r'(?=\D|$)'
 found=re.search(r'(?m)^'+token,body)
 if not found:return ''
 section=body[found.start():]
 section=re.split(r'(?m)^Classifications\s*$|^MR\d+',section[section.index('\n')+1:],maxsplit=1)[0]
 return section.strip()
def source_title(p,body):
 section=bibliography(p,body);lines=[line.strip() for line in section.splitlines() if line.strip()]
 index=next((i for i,line in enumerate(lines) if 'Article' in line and 'Cite' in line),None)
 if index is None or index+2>=len(lines):return ''
 title=lines[index+2]
 title=re.sub(r'\.(?:\([A-Za-z]+\))?\[.*?\]$','',title)
 return title.rstrip('.')
