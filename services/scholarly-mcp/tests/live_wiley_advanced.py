"""Verify Wiley native advanced rows beyond the former three-row cap."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import parse_qs,urlsplit
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/limitations-audit/wiley'
REPORT=SERVICE/'data/access-research/limitations-audit/independent-wiley-sdk.json'

def native_state(result):
    url=result['evidence'][0]['url'];params=parse_qs(urlsplit(url).query)
    return {'path':urlsplit(url).path,'rows':[{'field':params.get('field'+str(i),[None])[0],'text':params.get('text'+str(i),[None])[0]}
        for i in range(1,10) if 'field'+str(i) in params or 'text'+str(i) in params],'sortBy':params.get('sortBy')}

async def main():
    report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'sdk-data'),
        '--credential-root',str(PRIVATE/'credentials')])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            five=(await session.call_tool('search',{'source':'wiley','query':'algebra','options':{'field':'Title','terms':[
                {'field':'Anywhere','query':'matrix'},{'field':'Anywhere','query':'methods'},
                {'field':'Anywhere','query':'analysis'},{'field':'Anywhere','query':'polynomial'}]},'limit':1})).structuredContent
            three=(await session.call_tool('search',{'source':'wiley','query':'algebra','options':{'field':'Anywhere','terms':[
                {'field':'Anywhere','query':'algebra'},{'field':'Anywhere','query':'algebra'}],'sort':'date'},'limit':1})).structuredContent
            report['five_rows']={'status':five.get('status'),'received':five.get('received'),'total':five.get('total'),'native':native_state(five) if five.get('evidence') else None}
            report['three_rows_date']={'status':three.get('status'),'received':three.get('received'),'total':three.get('total'),'native':native_state(three) if three.get('evidence') else None}
            expected=[{'field':'Title','text':'algebra'},{'field':'AllField','text':'matrix'},{'field':'AllField','text':'methods'},
                {'field':'AllField','text':'analysis'},{'field':'AllField','text':'polynomial'}]
            report['completed']=five.get('status')=='ok' and report['five_rows']['native']['rows']==expected \
                and three.get('status')=='ok' and len(report['three_rows_date']['native']['rows'])==3 and report['three_rows_date']['native']['sortBy']==['Earliest']
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'five_rows':report.get('five_rows'),'three_rows_date':report.get('three_rows_date'),'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
