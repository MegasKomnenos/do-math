"""Show that the last SIAM and Numdam advanced row changes result semantics."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/semantic-cap-live'
CREDENTIALS=PRIVATE/'credentials';DATA=PRIVATE/'data';REPORT=SERVICE/'data/access-research/semantic-cap-live.json'

async def main():
    report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False,'credential_root':'explicit_private','data_root':'explicit_private','cases':[]}
    try:
        server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--credential-root',str(CREDENTIALS),'--data-dir',str(DATA)])
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(source,query,options,label,native_fields):
                result=(await session.call_tool('search',{'source':source,'query':query,'options':options,'limit':1})).structuredContent
                ids=[]
                if result.get('records'):
                    extracted=(await session.call_tool('extract',{'ref':result['records']['ref'],'count':1})).structuredContent
                    ids=[str(row.get('doi') or row.get('id') or row.get('url')) for row in extracted.get('items',[])]
                row={'source':source,'label':label,'status':result.get('status'),'code':result.get('code'),'total':result.get('total'),
                    'received':result.get('received'),'first_ids':ids,'requested_terms':len(options.get('terms',[]))+1,
                    'preserved_terms':len(result.get('options',{}).get('terms',[]))+1,'native_fields':native_fields}
                report['cases'].append(row);print(json.dumps({k:row[k] for k in ('source','label','status','code','total','received')},ensure_ascii=False),flush=True)
                return result
            siam_positive=[{'field':'Author','query':'Stetter'} for _ in range(51)]
            positive=await call('siam','algebra',{'field':'Title','terms':siam_positive},'52_positive',
                {'field1':'Title','text1':'algebra','field2_to_52':'Contrib=Stetter'})
            if positive.get('status')=='ok':
                siam_negative=[{'field':'Author','query':'Stetter'} for _ in range(50)]+[{'field':'Author','query':'zzqv_no_such_author_52'}]
                await call('siam','algebra',{'field':'Title','terms':siam_negative},'52_last_impossible',
                    {'field1':'Title','text1':'algebra','field2_to_51':'Contrib=Stetter','field52':'Contrib','text52':'zzqv_no_such_author_52'})
            numdam_positive=[{'field':'all','query':'algebra'} for _ in range(10)]
            positive=await call('numdam','algebra',{'field':'all','terms':numdam_positive},'11_positive',
                {'q0_to_q10':'all=algebra'})
            if positive.get('status')=='ok':
                numdam_negative=[{'field':'all','query':'algebra'} for _ in range(9)]+[{'field':'all','query':'zzqv_no_such_term_11'}]
                await call('numdam','algebra',{'field':'all','terms':numdam_negative},'11_last_impossible',
                    {'q0_to_q9':'all=algebra','q10':'all=zzqv_no_such_term_11'})
            report['completed']=len(report['cases'])==4 and all(
                ((row['total'] or 0)>0 and row['status']=='ok' if row['label'].endswith('_positive') else row['total']==0 and row['status']=='not_found')
                and row['preserved_terms']==row['requested_terms'] for row in report['cases'])
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'cases':len(report['cases']),'error_type':report.get('error_type')},ensure_ascii=False));return report['completed']
if __name__=='__main__':sys.exit(0 if asyncio.run(main()) else 1)
