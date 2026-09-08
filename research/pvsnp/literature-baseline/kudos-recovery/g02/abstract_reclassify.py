"""Reclassify retained Summon fields only after rechecking their source bindings."""
import json,hashlib
from pathlib import Path
from urllib.parse import urlsplit
from abstract_kind import classify,database_abstract
from response_recovery import document_matches
from run import BASE,ROOT,modal_matches,store_json

def valid_bytes(artifact):
 p=(BASE/artifact['path']).resolve()
 if not p.is_relative_to(BASE):return None
 try:data=p.read_bytes()
 except OSError:return None
 return data if data and hashlib.sha256(data).hexdigest()==artifact['sha256'] else None

def binding(record,paper,text):
 for e in record.get('evidence',[]):
  if urlsplit(e.get('url','')).hostname!='knu.summon.serialssolutions.com':continue
  data=valid_bytes(e)
  if data is None:continue
  if e['path'].endswith('.json'):
   try:payload=json.loads(data.decode('utf-8-sig'))
   except (UnicodeError,ValueError):continue
   for d in payload.get('documents',[]):
    if document_matches(paper,d):
     for a in d.get('abstracts') or []:
      if isinstance(a.get('abstract'),str) and a['abstract'].strip()==text.strip():return e,d.get('content_type'),a.get('attribution','')
  elif 'summon-detail' in e['path']:
   try:body=data.decode('utf-8-sig')
   except UnicodeError:continue
   if text.strip() in body and modal_matches(paper,body):return e,None,''
 return None

def candidate_abstract(record,paper):
 choices=[]
 for item in record.get('additional_content',[]):
  if item.get('kind') not in ('summon-book-description','summon-book-or-chapter-description'):continue
  artifact=item.get('artifact',{});data=valid_bytes(artifact)
  if data is None:continue
  try:text=data.decode('utf-8-sig')
  except UnicodeError:continue
  if classify(text)!='database_indexing_abstract':continue
  bound=binding(record,paper,text)
  if bound:
   e,kind,attribution=bound;new_artifact=dict(artifact);new_artifact['url']=e['url'];new_artifact['kind']='database-indexing-abstract'
   result=database_abstract(text,new_artifact,kind,attribution);result['binding_evidence']=[e];choices.append((len(text),result))
 return max(choices,key=lambda x:x[0])[1] if choices else None

def main():
 papers={p['paper_id']:p for p in [json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines()]}
 promoted=annotated=withdrawn=0
 for path in (ROOT/'results').glob('*.json'):
  record=json.loads(path.read_text(encoding='utf-8'));paper=papers[record['paper_id']]
  old=record['abstract']
  if old.get('status')=='found':
   artifacts=old.get('artifacts',[])
   if len(artifacts)!=1 or urlsplit(artifacts[0]['url']).hostname!='knu.summon.serialssolutions.com':continue
   data=valid_bytes(artifacts[0])
   if data is None:raise ValueError('Existing acquired artifact is invalid: '+record['paper_id'])
   text=data.decode('utf-8-sig');kind=classify(text)
   if kind!='database_indexing_abstract':
    record.setdefault('additional_content',[]).append({'kind':kind,'artifact':artifacts[0],'previous_status':'found'})
    record['abstract']={'status':'unresolved','reason':'Actual Summon abstract field is '+kind+'; other normal sources remain to be inspected.'};withdrawn+=1
   else:
    record['abstract']=database_abstract(text,artifacts[0],old.get('source_content_type'),old.get('attribution',''));annotated+=1
  else:
   promoted_abstract=candidate_abstract(record,paper)
   if not promoted_abstract:continue
   record['abstract']=promoted_abstract
   if record['identity']['status']!='confirmed':record['identity']={'status':'confirmed','reason':'Previously captured Summon source metadata and exact abstract text were rebound to assigned title, authors, year and identifiers during reclassification.'}
   promoted+=1
  store_json(path,record)
 print(json.dumps({'promoted':promoted,'annotated_existing':annotated,'withdrawn_nonabstracts':withdrawn},ensure_ascii=False))
if __name__=='__main__':main()
