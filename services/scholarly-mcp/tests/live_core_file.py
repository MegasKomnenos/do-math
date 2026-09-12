"""Fresh SDK retrieval and extraction of one explicitly selected public CORE PDF."""
import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE = Path(__file__).resolve().parents[1]
ROOT = SERVICE.parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


async def main(args):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    private = ROOT / '.credentials/scholarly-mcp/probes/access-research-20260913/core-file-sdk' / stamp
    private.mkdir(parents=True)
    report = {'started_at': now(), 'basis': 'fresh_SDK_and_actual_public_CORE_file_requests', 'completed': False}
    try:
        server = StdioServerParameters(command=sys.executable,
            args=[str(SERVICE / 'server.py'), '--data-dir', str(private / 'artifacts'),
                  '--credential-root', str(private / 'credentials')])
        async with stdio_client(server) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            result = (await session.call_tool('fetch', {'source': 'core', 'target': args.target,
                      'parts': ['metadata', 'fulltext', 'export']})).structuredContent
            report['fetch'] = {key: result.get(key) for key in ('status', 'code', 'received') if key in result}
            component = result.get('components', {}).get('fulltext', {})
            if component.get('status') != 'available':
                return False
            artifact = component['artifact']
            report['file'] = {key: artifact[key] for key in ('bytes', 'sha256', 'pages', 'core_output_id')}
            first = (await session.call_tool('extract', {'ref': artifact['ref'], 'start': 0, 'count': 1, 'render': True})).structuredContent
            last = (await session.call_tool('extract', {'ref': artifact['ref'], 'start': args.pages-1, 'count': 2})).structuredContent
            page = first['items'][0]
            image = await session.call_tool('extract', {'ref': page['image']['ref']})
            text = ' '.join(page['text'].split()).casefold()
            report['checks'] = {'fetch': result.get('status') == 'ok', 'total_pages': first.get('total') == args.pages,
                'first_title': ' '.join(args.title.split()).casefold() in text,
                'last_page': [item['page'] for item in last.get('items', [])] == [args.pages] and last.get('next_start') is None,
                'first_image': sum(item.type == 'image' for item in image.content) == 1}
            if args.doi:
                report['checks']['first_doi'] = args.doi.casefold() in text
            report['completed'] = all(report['checks'].values())
            (private / 'sdk-results.json').write_text(json.dumps({'fetch': result, 'first': first, 'last': last}, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as error:
        report['error_type'] = type(error).__name__
    finally:
        report['finished_at'] = now()
        report['private_evidence_directory'] = str(private.relative_to(ROOT))
        directory = SERVICE / 'data/access-research/core-public-reader'
        directory.mkdir(parents=True, exist_ok=True)
        output = json.dumps(report, ensure_ascii=False, indent=2)
        (directory / f'{stamp}-{args.report_name}.json').write_text(output, encoding='utf-8')
        (directory / f'{args.report_name}.json').write_text(output, encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False))
    return report['completed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', default='https://fileserver-az.core.ac.uk/download/287883844.pdf')
    parser.add_argument('--title', default='Pseudorandomness and the Minimum Circuit Size Problem')
    parser.add_argument('--doi', default='10.4230/LIPIcs.ITCS.2020.68')
    parser.add_argument('--pages', type=int, default=26)
    parser.add_argument('--report-name', choices=['core-file-sdk', 'core-file-ui-sdk'], default='core-file-sdk')
    sys.exit(0 if asyncio.run(main(parser.parse_args())) else 1)
