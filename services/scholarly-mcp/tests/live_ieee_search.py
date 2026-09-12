"""Verify IEEE result options, exact windows, facets and CSV through a fresh SDK server."""
import argparse,asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
async def main(credential_root):
    report={'source':'ieee-xplore','started_at':datetime.now(timezone.utc).isoformat(),'calls':[],'completed':False}
    path=ROOT/'data/access-research/ieee-search/sdk-live.json'
    def save():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save()
    args=[str(ROOT/'server.py'),'--credential-root',str(credential_root)]
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable,args=args)) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(tool,arguments):
                result=(await session.call_tool(tool,arguments)).structuredContent
                report['calls'].append({'tool':tool,'arguments':arguments,'result':result});save()
                print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
                return result
            options={'sort':'newest','content_types':['Journals'],'publication_titles':['IEEE Access'],'year':'2020-2024'}
            found=await call('search',{'source':'ieee-xplore','query':'"Document Title":complexity','options':options,'start':24,'limit':2,'export':'csv'})
            assert found['status']=='ok' and found['received']==2 and len(found['evidence'])==2
            rows=await call('extract',{'ref':found['records']['ref'],'count':2})
            assert len({row['articleNumber'] for row in rows['items']})==2
            assert all(row['publicationTitle']=='IEEE Access' and '2020'<=row['publicationYear']<='2024' for row in rows['items'])
            assert len(found['export']['artifacts'])==2
            extracted=[]
            for artifact in found['export']['artifacts']:
                item=await call('extract',{'ref':artifact['ref'],'count':2});extracted.extend(item['items'])
            assert [row['DOI'].casefold() for row in extracted]==[row['doi'].casefold() for row in rows['items']]
            facets=await call('extract',{'ref':found['facets']['ref'],'count':20})
            assert {'content_types','publication_titles'}<={group['field'] for group in facets['items']}
            reset=await call('search',{'source':'ieee-xplore','query':'"Article Number":10488889','options':{},'limit':1})
            assert reset['status']=='ok' and reset['total']==1 and reset['filter_state']=={'sort':'relevance','access':'all'}
            opened=await call('search',{'source':'ieee-xplore','query':'"Document Title":complexity','options':{'access':'open_access'},'limit':1})
            openrows=await call('extract',{'ref':opened['records']['ref'],'count':1})
            assert openrows['items'][0]['accessType']['type']=='open-access'
            report['completed']=True
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();save();print(json.dumps({'completed':report['completed'],'report':str(path)}),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path,required=True);args=parser.parse_args()
    asyncio.run(main(args.credential_root))
