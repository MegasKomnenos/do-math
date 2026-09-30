"""What the real HTTP port puts on the wire for each method and body an external operation may carry
(``http_transport.UrllibHttp``, a boundary adapter); moved from ``test_external``.

The legacy test replaced urllib's opener to read the request object it was
given. Here the request goes to a loopback server that records what actually
arrived: the method, the body bytes, whether the request declared a body
(urllib sends a Content-Type only for request data, so a request without data
has none), and the idempotency key header.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest

from do_math.external import prepare_operation
from do_math.http_transport import UrllibHttp

E_ACUTE = '\N{LATIN SMALL LETTER E WITH ACUTE}'


def _server(received):
    class Handler(BaseHTTPRequestHandler):
        def answer(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            received.append({'method': self.command, 'path': self.path, 'body': body,
                             'declared_body': 'Content-Type' in self.headers,
                             'idempotency_key': self.headers.get('Idempotency-Key')})
            self.send_response(200)
            self.send_header('Content-Length', '2')
            self.end_headers()
            self.wfile.write(b'ok')

        do_GET = do_POST = do_PUT = do_DELETE = answer

        def log_message(self, *arguments):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class HttpBytesTests(unittest.TestCase):
    def test_method_body_contract_matches_preparation_validation_and_http_bytes(self):
        """Every accepted method/body pair is sent with its method; only a nonempty body is request data, UTF-8 encoded.

        The rejected pairs and the validation of the accepted ones: ``unit.test_academic_external_sends``.
        """
        received = []
        server = _server(received)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        http = UrllibHttp()
        accepted = [(method, body) for method in ('GET', 'POST', 'PUT', 'DELETE') for body in (None, '', E_ACUTE)
                    if not (method in ('GET', 'DELETE') and body == E_ACUTE)]
        for method, body in accepted:
            with self.subTest(method=method, body=body):
                request = {'method': method, 'url': origin + '/ok'}
                if body is not None:
                    request['body'] = body
                operation = prepare_operation(request, 'G', 'S')
                received.clear()
                self.assertEqual(http.request(operation, [], 5), {'http_status': 200, 'body': b'ok'})
                data = b'\xc3\xa9' if body == E_ACUTE else None
                self.assertEqual(received, [{'method': method, 'path': '/ok', 'body': data or b'',
                                             'declared_body': data is not None,
                                             'idempotency_key': operation['idempotency_key']}])


if __name__ == '__main__':
    unittest.main()
