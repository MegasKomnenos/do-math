"""ScienceDirect native citation, PDF and current result filters through stdio."""
import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]
TITLE = 'Autograding Mathematical Induction Proofs with Natural Language Processing'
PII = 'S156042922600065X'
DOI = '10.1007/s40593-025-00498-2'


async def main(credential_root=None, scope='all'):
    report = {'source': 'science-direct', 'scope': scope, 'calls': [], 'completed': False}
    path = ROOT / 'data/validation' / f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-science-direct-extended-mcp.json'

    def save():
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    args = [str(ROOT / 'server.py')]
    if credential_root:
        args += ['--credential-root', str(credential_root)]
    save()
    print(json.dumps({'report': str(path)}), flush=True)
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable, args=args)) as (read, write), ClientSession(read, write) as session:
            await session.initialize()

            async def call(tool, arguments):
                result = (await session.call_tool(tool, arguments)).structuredContent
                report['calls'].append({'tool': tool, 'arguments': arguments, 'result': result})
                save()
                print(json.dumps({'tool': tool, 'status': result['status'], 'code': result.get('code'),
                                  'received': result.get('received'), 'total': result.get('total')}), flush=True)
                return result

            await call('describe_source', {'source': 'science-direct'})
            if scope in ('all', 'supplementary'):
                supplement = await call('fetch', {'source': 'science-direct', 'target': 'S0167278924001155',
                                                  'parts': ['metadata', 'supplementary']})
                if supplement['status'] != 'ok':
                    return
                component = supplement['components']['supplementary']
                assert component['status'] == 'available' and len(component['files']) == 1
                artifact = component['files'][0]['artifact']
                assert artifact['media_type'] == 'video/mp4' and artifact['bytes'] == 1315119
                import base64
                resource = await session.read_resource(artifact['ref'])
                assert len(resource.contents) == 1
                data = base64.b64decode(resource.contents[0].blob)
                assert len(data) == artifact['bytes'] and data[4:8] == b'ftyp'
                report['supplementary_resource_read'] = {'bytes': len(data), 'ftyp_verified': True}
                save()
            if scope in ('all', 'content'):
                for format in ('ris', 'bibtex', 'plain'):
                    found = await call('search', {'source': 'science-direct', 'query': '"' + TITLE + '"',
                                                 'options': {'field': 'Title'}, 'limit': 1, 'export': format})
                    if found['status'] != 'ok':
                        return
                    rows = await call('extract', {'ref': found['records']['ref'], 'count': 1})
                    assert rows['items'][0]['pii'] == PII and rows['items'][0]['title'] == TITLE
                    assert len(found['export']['artifacts']) == 1
                    artifact = found['export']['artifacts'][0]['artifact']
                    parsed = await call('extract', {'ref': artifact['ref'], 'count': 20})
                    assert parsed['status'] == 'ok' and DOI.casefold() in json.dumps(parsed).casefold()
                fetched = await call('fetch', {'source': 'science-direct', 'target': PII,
                                              'parts': ['metadata', 'abstract', 'export', 'fulltext']})
                if fetched['status'] != 'ok':
                    return
                components = fetched['components']
                assert {item['format'] for item in components['export']['artifacts']} == {'ris', 'bibtex', 'plain'}
                abstract = await call('extract', {'ref': components['abstract']['artifact']['ref'], 'count': 2})
                assert abstract['status'] == 'ok'
                pdf = components['fulltext']['artifact']
                assert pdf['media_type'] == 'application/pdf' and pdf['pages'] == 31
                first = await call('extract', {'ref': pdf['ref'], 'count': 2})
                assert first['status'] == 'ok' and DOI.casefold() in json.dumps(first).casefold()
            if scope in ('all', 'facets'):
                options = {'article_types': ['FLA', 'REV'], 'subject_areas': ['2600'],
                           'subscribed_only': True, 'date': '2020-2025'}
                filtered = await call('search', {'source': 'science-direct', 'query': 'algebra',
                                                'options': options, 'limit': 2, 'export': 'csv'})
                if filtered['status'] != 'ok':
                    return
                rows = await call('extract', {'ref': filtered['records']['ref'], 'count': 2})
                csv = await call('extract', {'ref': filtered['export']['ref'], 'count': 2})
                assert [row['pii'] for row in rows['items']] == [row['pii'] for row in csv['items']]
                assert filtered['filter_state']['subscribed']
                exact = await call('search', {'source': 'science-direct', 'query': 'algebra',
                                             'options': {'publication_exact': 'Journal of Algebra'}, 'limit': 2})
                if exact['status'] != 'ok':
                    return
                rows = await call('extract', {'ref': exact['records']['ref'], 'count': 2})
                assert all(row.get('publication') == 'Journal of Algebra' for row in rows['items'])
                assert str(exact['publication_exact']['cid']) == '272332'
            report['completed'] = True
    finally:
        report['finished'] = datetime.now(timezone.utc).isoformat()
        save()
        print(json.dumps({'completed': report['completed']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--credential-root', type=Path)
    parser.add_argument('--scope', choices=('all', 'content', 'facets', 'supplementary'), default='all')
    options = parser.parse_args()
    try:
        asyncio.run(main(options.credential_root, options.scope))
    except Exception as error:
        print(json.dumps({'verification_error': type(error).__name__}), flush=True)
        sys.exit(1)
