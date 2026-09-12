"""Retrieve verified file objects for the release whose Vault job is unprepared."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1]
PRIVATE=SERVICE.parents[1]/'.credentials/scholarly-mcp/probes/limitations-audit/swh-files-sdk'
REPORT=SERVICE/'data/access-research/limitations-audit/swh-files-sdk.json'

async def main():
    cached='--verified-cache' in sys.argv[1:]
    data_dir=SERVICE.parents[1]/'.credentials/scholarly-mcp/probes/limitations-audit/swh-direct-tree/artifacts' if cached else PRIVATE
    report_path=REPORT.with_name('swh-files-cache-sdk.json') if cached else REPORT
    data_dir.mkdir(parents=True,exist_ok=True);report_path.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False,
        'validation_mode':'previously_retrieved_live_objects' if cached else 'source_and_verified_cache'}
    def save():report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'stage':'started','report':str(report_path)}),flush=True)
    try:
        server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(data_dir)])
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            result=(await session.call_tool('fetch',{'source':'software-heritage',
                'target':'swh:1:dir:7057a716afab8ca80728aa7c6c2cc4bd03b0f45b' if cached else 'swh:1:rel:fc8e44c5bb3fabe81e5ebe46ac013a2510271616',
                'parts':['metadata','files']})).structuredContent
            component=result.get('components',{}).get('files',{})
            report.update(status=result.get('status'),component_status=component.get('status'),
                complete=component.get('complete'),directories=component.get('directories'),files=component.get('files'),
                symlinks=component.get('symlinks'),cached_directories=component.get('cached_directories'),cached_files=component.get('cached_files'),
                errors=[{'code':e.get('code'),'retry_after':e.get('retry_after')} for e in component.get('errors',[])])
            save();assert component.get('status')=='available' and component.get('complete')
            assert component['directory_swhid']=='swh:1:dir:7057a716afab8ca80728aa7c6c2cc4bd03b0f45b'
            extracted=(await session.call_tool('extract',{'ref':component['artifact']['ref'],'count':1000})).structuredContent
            assert extracted['status']=='ok';rows=extracted['items']
            blobs={r['swhid']:r['artifact'] for r in rows if r['kind'] in ('file','symlink') and r['status']=='available'}
            report.update(manifest_entries=len(rows),unique_blobs=len(blobs),bytes=sum(v['bytes'] for v in blobs.values()))
            assert len(blobs)==92 and report['bytes']==2763387
            if cached:assert component['cached_files']==92 and component['cached_directories']==20
            assert all(r.get('identity_verified') for r in rows if r['kind']=='directory')
            assert all(v.get('integrity',{}).get('verified') for v in blobs.values())
            selected=next(r for r in rows if r['kind']=='file' and r['artifact']['media_type']=='text/plain')
            text=(await session.call_tool('extract',{'ref':selected['artifact']['ref'],'count':2})).structuredContent
            assert text['status']=='ok'
            report['text_extract']={key:text.get(key) for key in ('status','returned','total')};report['completed']=True
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(report),flush=True)
    return report['completed']

if __name__=='__main__':sys.exit(0 if asyncio.run(main()) else 1)
