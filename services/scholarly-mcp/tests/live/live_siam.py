"""SIAM search, native citations and document fetch through a fresh SDK server."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE = Path(__file__).resolve().parents[2]


async def main(args):
    report = {'started': datetime.now(timezone.utc).isoformat(), 'source': 'siam', 'calls': [], 'completed': False}
    output = SERVICE / 'data/validation' / f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-siam-mcp.json'
    def save():
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    server_args = [str(SERVICE / 'server.py')]
    if args.credential_root:
        server_args += ['--credential-root', str(args.credential_root)]
    print(json.dumps({'report': str(output)}), flush=True)
    save()
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable, args=server_args)) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            async def call(tool, arguments):
                result = (await session.call_tool(tool, arguments)).structuredContent
                report['calls'].append({'tool': tool, 'arguments': arguments, 'result': result}); save()
                print(json.dumps({'tool': tool, 'status': result['status'], 'code': result.get('code'),
                                  'received': result.get('received'), 'total': result.get('total')}), flush=True)
                return result
            guide = await call('describe_source', {'source': 'siam'})
            assert 'search' in guide['capabilities']
            first = await call('search', {'source': 'siam', 'query': 'algebra', 'options': {'field': 'Title'}, 'limit': 2, 'export': 'csv'})
            if first['status'] != 'ok':
                return
            rows = await call('extract', {'ref': first['records']['ref'], 'count': 2})
            csv = await call('extract', {'ref': first['export']['ref'], 'count': 2})
            assert [row['doi'] for row in rows['items']] == [row['doi'] for row in csv['items']]
            for format in ('bibtex', 'ris', 'endnote', 'medlars', 'refworks'):
                result = await call('search', {'source': 'siam', 'query': 'algebra', 'options': {'field': 'Title'},
                                               'start': 19, 'limit': 2, 'export': format})
                if result['status'] != 'ok':
                    return
                assert result['received'] == 2 and len(result['export']['artifacts']) == 2
                selected = await call('extract', {'ref': result['records']['ref'], 'fields': ['doi', 'title'], 'count': 2})
                assert len({row['doi'] for row in selected['items']}) == 2
                for artifact in result['export']['artifacts']:
                    extracted = await call('extract', {'ref': artifact['ref'], 'count': 3})
                    assert extracted['status'] == 'ok'
            document = await call('fetch', {'source': 'siam', 'target': rows['items'][0]['url'], 'parts': ['metadata', 'export']})
            if document['status'] != 'ok':
                return
            assert len(document['components']['export']['artifacts']) == 5
            observed = await call('extract', {'ref': document['records']['ref'], 'fields': ['doi', 'title'], 'count': 1})
            assert observed['items'][0]['doi'] == rows['items'][0]['doi']
            empty = await call('search', {'source': 'siam', 'query': 'zz_no_such_siam_title_20260912',
                                         'options': {'field': 'Title'}, 'limit': 1})
            assert empty['status'] == 'not_found' and empty['total'] == 0
            report['completed'] = True
    finally:
        report['finished'] = datetime.now(timezone.utc).isoformat(); save()
        print(json.dumps({'completed': report['completed']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--credential-root', type=Path)
    asyncio.run(main(parser.parse_args()))
