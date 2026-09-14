"""Compare overlapping public Figshare windows beyond the offset ceiling."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2]
PRIVATE=SERVICE.parents[1]/'.credentials/scholarly-mcp/probes/limitations-audit/figshare-sdk'
REPORT=SERVICE/'data/access-research/limitations-audit/figshare-pagination-sdk.json'

async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'calls':[],'completed':False}
    def save():REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save()
    try:
        server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE)])
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();windows={}
            for start in (5000,5001,5002):
                result=(await session.call_tool('search',{'source':'figshare','query':'data',
                    'options':{'order':'published_date','order_direction':'asc'},'start':start,'limit':2,'export':'native'})).structuredContent
                row={'start':start,'status':result.get('status'),'code':result.get('code'),'received':result.get('received')}
                report['calls'].append(row);save()
                assert result.get('status')=='ok' and result.get('received')==2
                extracted=(await session.call_tool('extract',{'ref':result['records']['ref'],'fields':['id'],'count':2})).structuredContent
                assert extracted.get('status')=='ok'
                windows[start]=[item['id'] for item in extracted['items']];row['ids']=windows[start]
                native=result['export'].get('artifacts',[result['export']]);row['native_pages']=len(native)
                selected=[]
                for page in result['native_pages']:
                    value=(await session.call_tool('extract',{'ref':page['artifact']['ref'],'fields':['id'],'count':1000})).structuredContent
                    assert value.get('status')=='ok'
                    lo=max(0,start-page['native_start']);hi=start+2-page['native_start']
                    selected.extend(item['id'] for item in value['items'][lo:hi])
                assert selected==windows[start]
                assert result['next']=={'start':start+2};save()
            assert windows[5000][1]==windows[5001][0]
            assert windows[5001][1]==windows[5002][0]
            assert len(set(windows[5000]+windows[5002]))==4
            report['completed']=True
    except Exception as error:
        report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(report),flush=True)
    return report['completed']

if __name__=='__main__':sys.exit(0 if asyncio.run(main()) else 1)
