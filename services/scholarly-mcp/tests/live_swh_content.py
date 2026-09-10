"""Check archived byte identity and SWHID fragments through the stdio interface."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
core='swh:1:cnt:4d99d2d18326621ccdd70f5ea66c2e2ac236ad8b'
async def main():
    report={'source':'software-heritage','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-swh-content-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            data=(await session.call_tool(tool,args)).structuredContent
            report['calls'].append({'tool':tool,'arguments':args,'result':data});save()
            print(json.dumps({'tool':tool,'status':data['status'],'code':data.get('code')}),flush=True)
            return data
        found=await call('fetch',{'source':'software-heritage','target':core+';origin=https://gitorious.org/ocamlp3l/ocamlp3l_cvs.git;path=/Examples/SimpleFarm/simplefarm.ml;lines=9-15','parts':['metadata','fulltext']})
        assert found['status']=='ok' and found['context_verified'] is False
        content=found['components']['fulltext'];assert content['integrity']['verified'] and content['complete_content']['bytes']==527
        fragment=await call('extract',{'ref':content['artifact']['ref'],'count':10})
        complete=await call('extract',{'ref':content['complete_content']['ref'],'count':30})
        assert fragment['returned']==7 and complete['total']==27 and fragment['items']==complete['items'][8:15]
        single=await call('fetch',{'source':'software-heritage','target':'https://archive.softwareheritage.org/'+core+';lines=9','parts':['fulltext']})
        assert single['status']=='ok' and single['components']['fulltext']['selection']['last_line']==9
        outside=await call('fetch',{'source':'software-heritage','target':core+';lines=30-32','parts':['metadata','fulltext']})
        assert outside['status']=='partial' and outside['components']['fulltext']['code']=='selection_out_of_range'
        empty=await call('fetch',{'source':'software-heritage','target':'swh:1:cnt:e69de29bb2d1d6434b8b29ae775ad8c2e48c5391','parts':['metadata','fulltext']})
        assert empty['status']=='ok' and empty['components']['fulltext']['artifact']['bytes']==0
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
