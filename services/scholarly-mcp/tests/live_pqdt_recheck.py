"""Recheck fixed BibTeX scope after PQDT contract review."""
import argparse,asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
async def main(credential_root):
 report={'source':'pqdt','completed':False};path=ROOT/'data/access-research/pqdt-final/sdk-recheck.json'
 try:
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py'),'--credential-root',str(credential_root)])) as (read,write),ClientSession(read,write) as session:
   await session.initialize();found=(await session.call_tool('search',{'source':'pqdt','query':'TI("P versus NP")','options':{},'limit':1,'export':'bibtex'})).structuredContent
   extracted=(await session.call_tool('extract',{'ref':found['export']['ref'],'count':2})).structuredContent
   rejected=(await session.call_tool('search',{'source':'pqdt','query':'TI("P versus NP")','options':{'export_content':'citation_abstract'},'limit':1,'export':'bibtex'})).structuredContent
   report={'status':found['status'],'total':found['total'],'scope':found['options']['export_content'],'warning':extracted['items'][0]['parse_warnings'],
           'id':extracted['items'][0]['id'],'explicit_content_code':rejected.get('code'),'completed':found['status']=='ok' and found['total']==1
           and found['options']['export_content']=='fixed_cite_bibtex' and extracted['items'][0]['id']==''
           and extracted['items'][0]['parse_warnings']==['citation_key_missing'] and rejected.get('code')=='invalid_options'}
 finally:path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path,required=True);args=parser.parse_args();asyncio.run(main(args.credential_root))
