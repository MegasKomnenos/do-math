"""Verify generic GitHub search and the same pinned file in a repository ZIP."""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def main():
    report = {'source': 'github', 'calls': [], 'completed': False}
    path = ROOT / 'data/validation' / f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-github-mcp.json'

    def save():
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    save()
    print(json.dumps({'report': str(path)}), flush=True)
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable, args=[str(ROOT / 'server.py')])) as (read, write), ClientSession(read, write) as session:
            await session.initialize()

            async def call(tool, arguments):
                result = (await session.call_tool(tool, arguments)).structuredContent
                report['calls'].append({'tool': tool, 'arguments': arguments, 'result': result})
                save()
                print(json.dumps({'tool': tool, 'status': result['status'], 'code': result.get('code'),
                                  'received': result.get('received'), 'total': result.get('total')}), flush=True)
                return result

            await call('describe_source', {'source': 'github'})
            found = await call('search', {'source': 'github', 'query': 'Hello-World user:octocat in:name',
                                         'options': {'kind': 'repositories'}, 'limit': 1, 'export': 'native'})
            if found['status'] != 'ok':
                return
            rows = await call('extract', {'ref': found['records']['ref'], 'fields': ['id', 'full_name'], 'count': 1})
            assert rows['items'][0]['full_name'] == 'octocat/Hello-World'
            native = await call('extract', {'ref': found['export']['ref'], 'selection': '/items',
                                            'fields': ['id', 'full_name'], 'count': 1})
            assert rows['items'] == native['items']
            archive = await call('fetch', {'source': 'github', 'target': 'octocat/Hello-World',
                                          'parts': ['metadata', 'fulltext']})
            if archive['status'] != 'ok':
                return
            commit = archive['revision']
            zipped = archive['components']['fulltext']['artifact']
            listing = await call('extract', {'ref': zipped['ref'], 'count': 20})
            assert listing['status'] == 'ok'
            candidates = [item['path'] for item in listing['items'] if item['path'].endswith('/README')]
            assert len(candidates) == 1
            selected = await call('extract', {'ref': zipped['ref'], 'selection': candidates[0]})
            assert selected['status'] == 'ok'
            inner = await call('extract', {'ref': selected['items'][0]['artifact']['ref'], 'count': 20})
            file = await call('fetch', {'source': 'github', 'target': 'octocat/Hello-World@' + commit + ':README',
                                       'parts': ['metadata', 'fulltext']})
            if file['status'] != 'ok':
                return
            assert file['revision'] == commit
            text = await call('extract', {'ref': file['components']['fulltext']['artifact']['ref'], 'count': 20})
            assert text['items'] == inner['items'] and text['total'] == inner['total']
            report['completed'] = True
    finally:
        report['finished'] = datetime.now(timezone.utc).isoformat()
        save()
        print(json.dumps({'completed': report['completed']}), flush=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as error:
        print(json.dumps({'verification_error': type(error).__name__}), flush=True)
        sys.exit(1)
