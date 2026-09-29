"""Fake HTTP port: a response table keyed by URL path, with the product's request checks and redirect refusal."""
from urllib.parse import urlsplit

from do_math.http_request import check_body, check_url


class FakeHttp:
    def __init__(self, table):
        self.table, self.requests = dict(table), []

    def request(self, request, header, timeout):
        check_url(request["request"])
        check_body(request["request"])
        self.requests.append((request, list(header), timeout))
        status, body, location = self.table[urlsplit(request["request"]["url"]).path]
        if location is not None and 300 <= status < 400:
            raise ValueError("redirect forbidden")
        return {"http_status": status, "body": body}


def make_fake(table=()):
    return FakeHttp(dict(table))
