"""Recover a title from the exact assigned catalog record without erasing math."""
import hashlib,json,re
from functools import lru_cache
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]

@lru_cache(maxsize=4)
def records(path):
 result={}
 for line in (BASE/path).read_text(encoding='utf-8-sig').splitlines():
  value=json.loads(line);result[value.get('candidate_id')]=(hashlib.sha256(line.encode()).hexdigest(),value)
 return result

def source_title(p,mr):
 wanted=mr.upper().replace('MR','').lstrip('0')
 for source in p.get('source_records',[]):
  if source.get('record_id','').upper().replace('MR','').lstrip('0')!=wanted:continue
  found=records(source['path']).get(source['record_id'])
  if not found or found[0]!=source.get('record_sha256'):continue
  titles=[field['value'] for field in found[1].get('fields',[]) if field['name']=='title']
  if len(titles)==1:return titles[0]
 return None

def font_title(title):
 if '<' in title or '>' in title or '\0' in title or title.count('$')%2:return None
 fonts=[]
 def replace_font(match):
  style=match[1] or match[3];content=match[2] or match[4];style={'mathrm':'rm','mathbf':'bf','mathit':'it'}.get(style,style)
  fonts.append((style,content));return '\0FONT'+str(len(fonts)-1)+'\0'
 text=re.sub(r'\{\\(rm|bf|it)\s+([A-Za-z0-9]+)\}|\\(mathrm|mathbf|mathit|mathsf|mathtt)\{([A-Za-z0-9]+)\}',replace_font,title)
 if '\\' in text:return None
 text=text.replace('$','')
 while True:
  changed=re.sub(r'(?<![_^])\{([^{}]*)\}',r'\1',text)
  if changed==text:break
  text=changed
 text=' '.join(text.split()).strip()
 if text.endswith('.'):text=text[:-1]
 return text,tuple(fonts)
