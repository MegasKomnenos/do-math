"""Final fresh SDK checks for searched MathSciNet facet selection and preview."""
import argparse,asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/mathscinet-portal-diagnostic/credentials'
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/mathscinet-final-sdk-recheck'
REPORT=SERVICE/'data/access-research/limitations-audit/institutional-mathscinet-final-sdk-recheck.json';QUERY='ti:(algebra)'
def now():return datetime.now(timezone.utc).isoformat()
def safe(label,value):return {key:item for key,item in {'label':label,'status':value.get('status'),'code':value.get('code'),'total':value.get('total'),'received':value.get('received'),'native_query':value.get('native_query'),'filter_evidence_count':len(value.get('filter_evidence') or []),'stage':value.get('stage'),'error_type':value.get('error_type'),'observed_host':value.get('observed_host'),'facet_candidates':value.get('facet_candidates')}.items() if item is not None}
async def main(label):
 PRIVATE.mkdir(parents=True,exist_ok=True);snapshot=REPORT.with_name(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-mathscinet-final-sdk.json')
 report={'source':'mathscinet','started_at':now(),'outside_exact_label':label,'calls':[],'completed':False}
 server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'artifacts'),'--credential-root',str(CREDENTIALS)])
 try:
  async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
   await session.initialize();outside=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'facet_filters':{'journals':{'include':[label]}}},'limit':1})).structuredContent;report['calls'].append(safe('outside_journal',outside))
   if outside.get('code') in ('gateway_navigation_failed','publisher_access_challenge','authentication_failed'):
    report['stopped_after_gateway_failure']=True;return
   preview=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'facet_group':'journals','facet_query':'Topology'},'limit':1})).structuredContent;report['calls'].append(safe('journal_preview',preview));extracted=None
   if preview.get('facet_candidates'):
    extracted=(await session.call_tool('extract',{'ref':preview['facet_candidates']['ref'],'start':0,'count':10})).structuredContent
   report['preview_extract']={key:extracted.get(key) for key in ('status','total','returned') if extracted and extracted.get(key) is not None}
   report['checks']={'outside':outside.get('status')=='ok' and outside.get('received')==1 and len(outside.get('filter_evidence') or [])==1 and outside.get('native_query','').startswith(QUERY+' ji:'),
                     'preview':preview.get('status')=='ok' and extracted is not None and extracted.get('status')=='ok' and extracted.get('total',0)>0}
   report['completed']=all(report['checks'].values())
 except Exception as error:report['runner_error_type']=type(error).__name__
 finally:
  report['finished_at']=now();text=json.dumps(report,ensure_ascii=False,indent=2)
  snapshot.write_text(text,encoding='utf-8');REPORT.write_text(text,encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('label',nargs='?',default='Topology Appl.');args=parser.parse_args()
 asyncio.run(main(args.label))
