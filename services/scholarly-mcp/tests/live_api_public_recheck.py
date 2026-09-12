"""One bounded current-adapter check after a positive direct CORE work lookup."""
import asyncio,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/access-research/api-recheck/core-sdk.json'
async def main():
 report={'source':'core','started':datetime.now(timezone.utc).isoformat(),'completed':False};start=time.monotonic()
 try:
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py')])) as (read,write),ClientSession(read,write) as session:
   await session.initialize();result=(await session.call_tool('fetch',{'source':'core','target':'https://core.ac.uk/works/340524929','parts':['metadata']})).structuredContent
   report['result']={'status':result.get('status'),'code':result.get('code'),'metadata_status':result.get('components',{}).get('metadata',{}).get('status'),'has_records':bool(result.get('records')),'has_evidence':bool(result.get('evidence'))}
   report['completed']=report['result']['status']=='ok' and report['result']['metadata_status']=='available' and report['result']['has_records'] and report['result']['has_evidence']
 finally:
  report['elapsed_seconds']=round(time.monotonic()-start,3);report['finished']=datetime.now(timezone.utc).isoformat();OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
