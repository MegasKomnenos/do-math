"""HTTP port contract (설계 2.2): the urllib transport and the fake answer the same response table alike.

``make(table)`` builds the implementation over ``{path: (status, body, location)}``;
the real side serves the table from a loopback server.
"""


TABLE = {'/created': (201, b'created body', None), '/missing': (404, b'not here', None),
         '/moved': (302, b'', '/created')}

def _request(base, path, method='GET'):
    return {'idempotency_key': 'IK-1', 'request': {'method': method, 'url': base + path, 'headers': {}, 'body': ''}}

class HttpContract:
    base = 'http://127.0.0.1:9'

    def make(self, table):
        raise NotImplementedError

    def setUp(self):
        self.http = self.make(TABLE)

    def test_a_success_returns_status_and_exact_body(self):
        self.assertEqual(self.http.request(_request(self.base, '/created'), [], 5),
                         {'http_status': 201, 'body': b'created body'})

    def test_an_error_status_is_returned_not_raised(self):
        self.assertEqual(self.http.request(_request(self.base, '/missing'), [], 5),
                         {'http_status': 404, 'body': b'not here'})

    def test_a_redirect_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'redirect forbidden'):
            self.http.request(_request(self.base, '/moved'), [], 5)
