"""APS custom facets, original citations and PDF through the real SDK."""
import argparse,asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]

async def main(credential_root=None,supplement_only=False):
    report={'source':'aps-institutional','scope':'supplement-only' if supplement_only else 'search-citation-pdf','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-aps-extended-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    args=[str(root/'server.py')]
    if credential_root:args+=['--credential-root',str(credential_root)]
    save();print(json.dumps({'report':str(path)}),flush=True)
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable,args=args)) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(tool,args):
                result=(await session.call_tool(tool,args)).structuredContent
                report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
                print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
                return result
            await call('describe_source',{'source':'aps-institutional'})
            if supplement_only:
                result=await call('fetch',{'source':'aps-institutional','target':'https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.115.250402','parts':['supplementary']})
                if result['status']!='ok':return
                component=result['components']['supplementary']
                assert component['status']=='available' and len(component['files'])==1
                artifact=component['files'][0]['artifact']
                extracted=await call('extract',{'ref':artifact['ref'],'count':1})
                assert extracted['status']=='ok' and extracted['total']==16
                report['completed']=True
                return
            found=await call('search',{'source':'aps-institutional','query':'algebra',
                'options':{'journal':['prd','prl'],'start_date':'1960-01-01','end_date':'1980-12-31'},'limit':1,'export':'ris'})
            if found['status']!='ok':return
            selected=await call('extract',{'ref':found['records']['ref'],'count':1})
            row=selected['items'][0]
            for exported in found['export']['artifacts']:
                cited=await call('extract',{'ref':exported['artifact']['ref'],'count':1})
                assert row['doi'].casefold() in json.dumps(cited).casefold()
            fetched=await call('fetch',{'source':'aps-institutional','target':row['url'],'parts':['metadata','abstract','export','fulltext']})
            if fetched['status']!='ok':return
            for exported in fetched['components']['export']['artifacts']:
                cited=await call('extract',{'ref':exported['artifact']['ref'],'count':1})
                assert row['doi'].casefold() in json.dumps(cited).casefold()
            abstract=await call('extract',{'ref':fetched['components']['abstract']['artifact']['ref'],'count':2})
            assert abstract['status']=='ok'
            pdf=fetched['components']['fulltext']['artifact']
            assert pdf['media_type']=='application/pdf' and pdf['pages']>0
            extracted=await call('extract',{'ref':pdf['ref'],'start':0,'count':1})
            assert extracted['status']=='ok'
            report['completed']=True
    finally:
        report['finished']=datetime.now(timezone.utc).isoformat();save()
        print(json.dumps({'completed':report['completed']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path);parser.add_argument('--supplement-only',action='store_true')
    options=parser.parse_args()
    asyncio.run(main(options.credential_root,options.supplement_only))
