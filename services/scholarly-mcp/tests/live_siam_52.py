import argparse,asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
async def main(credential_root):
 report={'completed':False};path=ROOT/'data/access-research/siam-52-live.json'
 try:
  terms=[{'field':'Author','query':'Stetter'} for _ in range(51)]
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py'),'--credential-root',str(credential_root)])) as (read,write),ClientSession(read,write) as session:
   await session.initialize();result=(await session.call_tool('search',{'source':'siam','query':'algebra','options':{'field':'Title','terms':terms},'limit':1})).structuredContent
   report={'status':result['status'],'code':result.get('code'),'total':result.get('total'),'received':result.get('received'),'requested_fields':52,'preserved_terms':len(result.get('options',{}).get('terms',[])),'completed':result['status'] in ('ok','not_found') and len(result.get('options',{}).get('terms',[]))==51}
 finally:path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--credential-root',type=Path,required=True);a=p.parse_args();asyncio.run(main(a.credential_root))
