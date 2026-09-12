"""Verify PQDT filters, page boundary and every downloadable native export through SDK."""
import argparse,asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];TITLE='Resource Bounded Measure and P Versus NP Problem-A Critical Study';DOC='2618193239'
async def main(credential_root):
 report={'source':'pqdt','started_at':datetime.now(timezone.utc).isoformat(),'calls':[],'formats':[],'completed':False};path=ROOT/'data/access-research/pqdt-final/sdk-live.json'
 def save():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 save()
 try:
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py'),'--credential-root',str(credential_root)])) as (read,write),ClientSession(read,write) as session:
   await session.initialize()
   async def call(tool,args):
    result=(await session.call_tool(tool,args)).structuredContent;report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
    print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True);return result
   options={'sort':'recent','publication_date':{'from':'2020-01-01','to':'2024-12-31'},'facets':{
    'subjects':{'include':['mathematics','computer science'],'exclude':['mathematics education']},'languages':{'include':['English'],'exclude':[]}},'export_content':'citation_abstract'}
   filtered=await call('search',{'source':'pqdt','query':'TI(algebra)','options':options,'start':19,'limit':2,'export':'text'})
   assert filtered['status']=='ok' and filtered['received']==2 and len(filtered['evidence'])==2
   rows=await call('extract',{'ref':filtered['records']['ref'],'count':2});text=await call('extract',{'ref':filtered['export']['ref'],'count':100})
   assert len({row['id'] for row in rows['items']})==2 and text['status']=='ok'
   facets=await call('extract',{'ref':filtered['facets']['ref'],'count':10});assert {x['field'] for x in facets['items']}=={'subjects','index_terms','universities','locations','languages'}
   zero=await call('search',{'source':'pqdt','query':'TI("zzzzqxjv-no-such-dissertation")','options':{},'limit':1});assert zero['status']=='not_found' and zero['total']==0
   for format in ('ris','text','rtf','xls','pdf','endnote','bibtex'):
    fmt_options={} if format=='bibtex' else {'export_content':'citation_abstract'}
    found=await call('search',{'source':'pqdt','query':'TI("P versus NP")','options':fmt_options,'limit':1,'export':format})
    assert found['status']=='ok' and found['received']==1
    records=await call('extract',{'ref':found['records']['ref'],'count':1});assert records['items'][0]['id']==DOC and records['items'][0]['title']==TITLE
    extracted=await call('extract',{'ref':found['export']['ref'],'count':100});assert extracted['status']=='ok'
    if format=='bibtex':assert extracted['items'][0]['id']=='' and extracted['items'][0]['parse_warnings']==['citation_key_missing'] and DOC in json.dumps(extracted)
    report['formats'].append({'format':format,'bytes':found['export']['bytes'],'media_type':found['export']['media_type'],'extract_total':extracted.get('total'),'pages':found['export'].get('pages')});save()
   fetched=await call('fetch',{'source':'pqdt','target':DOC,'parts':['metadata','abstract','fulltext','export']})
   assert fetched['status']=='ok' and fetched['components']['fulltext']['artifact']['pages']==40
   report['completed']=len(report['formats'])==7
 finally:
  report['finished_at']=datetime.now(timezone.utc).isoformat();save();print(json.dumps({'completed':report['completed'],'formats':len(report['formats']),'report':str(path)}),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path,required=True);args=parser.parse_args();asyncio.run(main(args.credential_root))
