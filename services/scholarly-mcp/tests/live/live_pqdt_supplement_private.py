"""Verify PQDT supplemental PNG through a fresh SDK server with an isolated credential state."""
import argparse,asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[2]
async def main(credential_root):
 report={'source':'pqdt','completed':False};path=ROOT/'data/access-research/pqdt-final/sdk-supplement.json'
 try:
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py'),'--credential-root',str(credential_root)])) as (read,write),ClientSession(read,write) as session:
   await session.initialize();found=(await session.call_tool('fetch',{'source':'pqdt','target':'2485541561','parts':['metadata','supplementary']})).structuredContent
   files=found['components']['supplementary']['files'];extracted=await session.call_tool('extract',{'ref':files[0]['artifact']['ref']})
   report.update(status=found['status'],files=len(files),bytes=files[0]['artifact']['bytes'],extract_status=extracted.structuredContent['status'],image_content=any(x.type=='image' for x in extracted.content))
   report['completed']=found['status']=='ok' and len(files)==1 and report['bytes']==529775 and report['extract_status']=='ok' and report['image_content']
 finally:path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path,required=True);args=parser.parse_args();asyncio.run(main(args.credential_root))
