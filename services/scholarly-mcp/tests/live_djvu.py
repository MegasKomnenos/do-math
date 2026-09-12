"""Fresh MCP extraction of an already retrieved native DjVu artifact."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1]


async def main(args):
    report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False,
        'basis':'previously_retrieved_native_djvu; fresh SDK and local decoding, no mock'}
    try:
        server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(args.data_dir)])
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            first=(await session.call_tool('extract',{'ref':args.ref,'start':0,'count':1,'render':True})).structuredContent
            middle=(await session.call_tool('extract',{'ref':args.ref,'start':1,'count':2})).structuredContent
            last=(await session.call_tool('extract',{'ref':args.ref,'start':9,'count':2})).structuredContent
            image=await session.call_tool('extract',{'ref':first['items'][0]['image']['ref']})
            report.update(first_status=first.get('status'),total=first.get('total'),
                title_matches='three complexity functions' in first['items'][0]['text'].casefold(),
                doi_matches='10.1051/ita/2011126' in first['items'][0]['text'],
                middle_pages=[row['page'] for row in middle.get('items',[])],middle_next=middle.get('next_start'),
                last_pages=[row['page'] for row in last.get('items',[])],last_next=last.get('next_start'),
                first_image_blocks=sum(item.type=='image' for item in image.content),
                first_image_bytes=first['items'][0]['image']['bytes'])
            report['completed']=first.get('status')==middle.get('status')==last.get('status')=='ok' \
                and report['total']==10 and report['title_matches'] and report['doi_matches'] \
                and report['middle_pages']==[2,3] and report['middle_next']==3 \
                and report['last_pages']==[10] and report['last_next'] is None and report['first_image_blocks']==1
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        target=SERVICE/'data/access-research/limitations-audit/djvu-sdk.json'
        target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    return report['completed']


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ref',required=True)
    parser.add_argument('--data-dir',type=Path,default=SERVICE/'data');arguments=parser.parse_args()
    sys.exit(0 if asyncio.run(main(arguments)) else 1)
