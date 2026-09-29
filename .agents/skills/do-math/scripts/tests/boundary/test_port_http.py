"""Real side of the HTTP port contract: urllib against a loopback server serving the same table."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest

from contracts.test_port_http import HttpContract
from do_math.wiring import real_ports


def _server(table):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, body, location = table[self.path]
            self.send_response(status)
            if location:
                self.send_header('Location', location)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *arguments):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class UrllibHttpContract(HttpContract, unittest.TestCase):
    def make(self, table):
        server = _server(table)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.base = f'http://127.0.0.1:{server.server_address[1]}'
        return real_ports().http


if __name__ == '__main__':
    unittest.main()
