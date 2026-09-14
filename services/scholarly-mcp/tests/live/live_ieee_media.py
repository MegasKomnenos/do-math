"""Verify native graphical media and the no-media record through stdio."""
import argparse,asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--native-tab',action='store_true');args=parser.parse_args()
    report={'source':'ieee-xplore','calls':[],'completed':False}
    suffix='ieee-media-tab-mcp.json' if args.native_tab else 'ieee-media-mcp.json'
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{suffix}'
    def preserve(): path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preserve(); print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        for identifier in ['8626436'] if args.native_tab else ['11259066','10488889']:
            found=(await session.call_tool('fetch',{'source':'ieee-xplore','target':identifier,'parts':['metadata','supplementary']})).structuredContent
            report['calls'].append(found);preserve()
            print(json.dumps({'article':identifier,'status':found['status'],'code':found.get('code')}),flush=True)
            assert 'components' in found
            media=found['components']['supplementary']['attachments']
            print(json.dumps({'media_status':media['status'],'received':media.get('received'),'files':[{k:f.get(k) for k in ['role','status','code']} for f in media.get('files',[])]}),flush=True)
            if identifier=='8626436':
                assert media['status']=='available' and media['received']==1
                assert media['multimedia']['status']=='available' and media['multimedia']['discovered']==1
                video=media['files'][0]
                assert video['role']=='supplementary_media' and video['filename']=='BioLSTM_RA-L_video.mp4'
                assert video['artifact']['media_type']=='video/mp4' and video['artifact']['bytes']>1_000_000
            elif identifier=='11259066':
                assert media['status']=='available' and media['received']==2
                cover=next(f['artifact'] for f in media['files'] if f['role']=='graphical_abstract_cover')
                extracted=(await session.call_tool('extract',{'ref':cover['ref']})).structuredContent
                report['calls'].append(extracted);preserve()
                assert extracted['status']=='ok' and extracted['unit']=='image'
                video=next(f['artifact'] for f in media['files'] if f['role']=='graphical_abstract')
                assert video['media_type']=='video/mp4' and video['bytes']>90_000_000
            else:
                assert media['status']=='not_found' and media['received']==0
                assert found['components']['supplementary']['references']['count']==22
        report['completed']=True; preserve();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
