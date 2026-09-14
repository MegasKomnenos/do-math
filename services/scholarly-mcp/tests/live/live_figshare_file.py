"""Verify a selected Figshare file delivered by a non-AIP storage bucket."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2]
PRIVATE=SERVICE.parents[1]/'.credentials/scholarly-mcp/probes/limitations-audit/figshare-file-sdk'
REPORT=SERVICE/'data/access-research/limitations-audit/figshare-file-sdk.json'

async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False}
    try:
        server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE)])
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            result=(await session.call_tool('fetch',{'source':'figshare','target':'3625458#file:5714205','parts':['metadata','fulltext']})).structuredContent
            report['status']=result.get('status')
            files=result.get('components',{}).get('fulltext',{}).get('files',[])
            assert len(files)==1 and files[0]['id']==5714205 and files[0]['status']=='available'
            artifact=files[0]['artifact']
            report.update(bytes=artifact['bytes'],checksum_verified=artifact['checksum_verified'],media_type=artifact['media_type'])
            assert artifact['bytes']==39316 and artifact['checksum_verified']
            extracted=(await session.call_tool('extract',{'ref':artifact['ref'],'count':2})).structuredContent
            report['extract']={key:extracted.get(key) for key in ('status','returned','total')}
            assert extracted['status']=='ok';report['completed']=True
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)
    return report['completed']

if __name__=='__main__':sys.exit(0 if asyncio.run(main()) else 1)
