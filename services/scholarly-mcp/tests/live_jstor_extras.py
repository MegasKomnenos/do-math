"""Verify native audio, transcript, supplement PDF and disabled video download."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'jstor','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-jstor-extras-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent;report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'components':{k:v['status'] for k,v in result.get('components',{}).items()}}),flush=True);return result
        audio=await call('fetch',{'source':'jstor','target':'community.41259097','parts':['metadata','fulltext','supplementary']})
        if audio['status']!='ok':return
        assert audio['components']['fulltext']['artifact']['media_type']=='audio/mpeg'
        assert audio['components']['fulltext']['artifact']['bytes']==24416379
        transcripts=audio['components']['supplementary']['files'];assert len(transcripts)==1
        assert transcripts[0]['artifact']['media_type']=='text/vtt'
        text=await call('extract',{'ref':transcripts[0]['artifact']['ref'],'count':6});assert text['status']=='ok' and 'WEBVTT' in json.dumps(text)
        attached=await call('fetch',{'source':'jstor','target':'26581894','parts':['metadata','supplementary']})
        if attached['status']!='ok':return
        files=attached['components']['supplementary']['files'];assert len(files)==1 and files[0]['artifact']['bytes']==863887
        selected=await call('extract',{'ref':files[0]['artifact']['ref'],'count':1});assert selected['status']=='ok'
        assert 'ATHEY, TIBSHIRANI AND WAGER' in ' '.join(selected['items'][0]['text'].split())
        assert files[0]['artifact']['pages']==21
        video=await call('fetch',{'source':'jstor','target':'community.39197180','parts':['metadata','fulltext','supplementary']})
        assert video['components']['fulltext']['status']=='not_offered'
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
