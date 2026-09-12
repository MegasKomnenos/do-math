"""Verify one arbitrary APS Harvest result window through a fresh SDK server."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1]
PRIVATE=SERVICE.parents[1]/'.credentials/scholarly-mcp/probes/limitations-audit/aps-public-window'

async def main():
    stamp=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}'
    report_path=SERVICE/'data/validation'/(stamp+'-aps-public-window-mcp.json')
    PRIVATE.mkdir(parents=True,exist_ok=True)
    report={'source':'aps','started_at':datetime.now(timezone.utc).isoformat(),'completed':False}
    def save():report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(report_path)}),flush=True)
    try:
        server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/stamp)])
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            options={'from':'2026-09-01','until':'2026-09-02','date':'published'}
            first=(await session.call_tool('search',{'source':'aps','query':'','options':options,'start':0,'limit':4})).structuredContent
            shifted=(await session.call_tool('search',{'source':'aps','query':'','options':options,'start':1,'limit':2,'export':'native'})).structuredContent
            first_rows=(await session.call_tool('extract',{'ref':first['records']['ref'],'count':4})).structuredContent
            shifted_rows=(await session.call_tool('extract',{'ref':shifted['records']['ref'],'count':2})).structuredContent
            first_ids=[row.get('id') for row in first_rows.get('items',[])]
            shifted_ids=[row.get('id') for row in shifted_rows.get('items',[])]
            artifacts=shifted.get('export',{}).get('artifacts',[])
            report.update(first_status=first.get('status'),first_received=first.get('received'),
                shifted_status=shifted.get('status'),shifted_received=shifted.get('received'),
                exact_overlap=shifted_ids==first_ids[1:3],native_pages=len(shifted.get('native_pages',[])),
                native_export_artifacts=len(artifacts),next=shifted.get('next'))
            report['completed']=first.get('status')=='ok' and len(first_ids)>=3 and shifted.get('status')=='ok' \
                and report['exact_overlap'] and report['native_pages']==2 and report['native_export_artifacts']==2
    except Exception as error:
        report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:report.get(k) for k in ('completed','first_status','first_received','shifted_status','shifted_received','exact_overlap','native_pages','native_export_artifacts','next','error_type')}),flush=True)
    return report['completed']

if __name__=='__main__':sys.exit(0 if asyncio.run(main()) else 1)
