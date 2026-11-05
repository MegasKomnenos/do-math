"""A local, side-effect-free MCP tool for verifying explicit worker tool wiring."""
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    if 'id' not in request:
        continue
    method = request.get('method')
    if method == 'initialize':
        result = {'protocolVersion': request['params']['protocolVersion'], 'capabilities': {'tools': {}},
                  'serverInfo': {'name': 'do-math-probe', 'version': '1'}}
    elif method == 'tools/list':
        result = {'tools': [{'name': 'do_math_probe', 'description': 'Return the fixed do-math wiring probe value.',
                             'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}}]}
    elif method == 'tools/call':
        result = {'content': [{'type': 'text', 'text': 'MCP_PROBE_OK'}]}
    else:
        result = {}
    print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)
