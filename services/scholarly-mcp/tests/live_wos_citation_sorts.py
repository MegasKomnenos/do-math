"""Fresh stdio check for non-default WOS citing-result sort."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
SERVICE=Path(__file__).resolve().parents[1];ROOT=SERVICE.parents[1]
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/wos-citations/sdk-qid-export-final-2/credentials'
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/limitations-audit-wos/sdk'
REPORT=SERVICE/'data/access-research/limitations-audit/institutional-wos-citing-sdk.json'
def now():return datetime.now(timezone.utc).isoformat()
async def main():
    sort=sys.argv[1] if len(sys.argv)>1 else 'relevance';PRIVATE.mkdir(parents=True,exist_ok=True);report={'source':'wos','started_at':now(),'sort':sort,'completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'artifacts'),'--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();value=(await session.call_tool('search',{'source':'wos','query':'WOS:000269418800023',
                'options':{'kind':'citations','sort':sort},'start':124,'limit':2,'export':'plain'})).structuredContent
            report['call']={key:value.get(key) for key in ('status','code','kind','target','start','requested','received','total','has_more','next','native_sort','error_type')}
            report['call']['sort_evidence']=bool(value.get('sort_evidence'));report['call']['export_error']=value.get('export_error')
            report['completed']=value.get('status')=='ok' and value.get('received')==1 and value.get('total')==125 and isinstance(value.get('native_sort'),str) and bool(value.get('native_sort')) and bool(value.get('sort_evidence'))
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=now();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
