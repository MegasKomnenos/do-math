"""Fresh SDK comparison of arbitrary windows in Zenodo and GitHub."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1]
PRIVATE=SERVICE.parents[1]/'.credentials/scholarly-mcp/probes/limitations-audit/public-window-sdk'
REPORT=SERVICE/'data/access-research/limitations-audit/public-window-sdk.json'

async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'sources':[],'completed':False}
    def save():REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save()
    try:
        server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE)])
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            for source,query,options,selection in [('github','user:octocat',{'sort':'updated','order':'asc'},'/items'),
                    ('zenodo','algebra',{'sort':'mostrecent'},'/hits/hits')]:
                row={'source':source,'calls':[],'completed':False};report['sources'].append(row);save()
                found=[]
                for start,limit in [(0,4),(1,2)]:
                    result=(await session.call_tool('search',{'source':source,'query':query,'options':options,'start':start,'limit':limit,'export':'native'})).structuredContent
                    call={'start':start,'limit':limit,'status':result.get('status'),'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}
                    row['calls'].append(call);save()
                    if result.get('status')!='ok' or result.get('received')!=limit:break
                    extracted=(await session.call_tool('extract',{'ref':result['records']['ref'],'fields':['id'],'count':limit})).structuredContent
                    assert extracted['status']=='ok'
                    ids=[item['id'] for item in extracted['items']];call['ids']=ids;found.append(ids)
                    selected=[]
                    for page in result['native_pages']:
                        raw=(await session.call_tool('extract',{'ref':page['artifact']['ref'],'selection':selection,'fields':['id'],'count':100})).structuredContent
                        assert raw['status']=='ok'
                        lo=max(0,start-page['native_start']);hi=start+limit-page['native_start']
                        selected.extend(item['id'] for item in raw['items'][lo:hi])
                    assert selected==ids;save()
                if len(found)==2:
                    assert found[0][1:3]==found[1]
                    row['completed']=True;save()
            report['completed']=all(row['completed'] for row in report['sources'])
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(report),flush=True)
    return report['completed']

if __name__=='__main__':sys.exit(0 if asyncio.run(main()) else 1)
