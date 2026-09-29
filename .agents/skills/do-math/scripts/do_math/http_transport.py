"""Real HTTP port (boundary adapter): one urllib request, redirects refused, error statuses returned."""
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .http_request import check_body, check_url


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*_): raise ValueError("redirect forbidden")

def _http(request: dict, header: list[tuple[str,str]], timeout: int) -> dict:
    headers={"Idempotency-Key":request["idempotency_key"]}
    for name,value in header: headers[name]=value
    check_url(request["request"])
    body = check_body(request["request"])
    data=body.encode() if request["request"]["method"] in {"POST", "PUT"} and body else None
    req=Request(request["request"]["url"],data=data,headers=headers,method=request["request"]["method"])
    try:
        with build_opener(_NoRedirect).open(req,timeout=timeout) as response: body=response.read(); return {"http_status":response.status,"body":body}
    except HTTPError as error: return {"http_status":error.code,"body":error.read()}

class UrllibHttp:
    """Real HTTP port."""

    def request(self, request: dict, header: list, timeout: int) -> dict:
        return _http(request, header, timeout)
