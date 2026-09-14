"""Verify one IEEE facet value resolved beyond the initial candidates."""
import argparse,asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[2]
async def main(credential_root):
 report={'source':'ieee-xplore','completed':False};path=ROOT/'data/access-research/ieee-search/sdk-extended-facet.json'
 def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 save()
 try:
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py'),'--credential-root',str(credential_root)])) as (read,write),ClientSession(read,write) as session:
   await session.initialize();result=(await session.call_tool('search',{'source':'ieee-xplore','query':'"Document Title":complexity','options':{'publication_titles':['Artificial Life']},'limit':1})).structuredContent
   rows=(await session.call_tool('extract',{'ref':result['records']['ref'],'count':1})).structuredContent
   facets=(await session.call_tool('extract',{'ref':result['facets']['ref'],'count':20})).structuredContent
   publication=next(x for x in facets['items'] if x['field']=='publication_titles');extra=next(x for x in publication['candidates'] if x['value']=='Artificial Life')
   report.update(status=result['status'],total=result['total'],received=result['received'],publication=rows['items'][0]['publicationTitle'],extra_candidate=extra)
   report['completed']=result['status']=='ok' and result['total']==24 and report['publication']=='Artificial Life' and extra.get('basis')=='native_typeahead'
 finally:save();print(json.dumps({'completed':report['completed'],'status':report.get('status'),'total':report.get('total')}),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path,required=True);args=parser.parse_args();asyncio.run(main(args.credential_root))
