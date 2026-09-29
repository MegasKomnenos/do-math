"""The request shape an external operation may send (layer 1): method, safe URL and text body."""
from urllib.parse import unquote, urlsplit


def check_url(request: dict):
    if not isinstance(request, dict) or request.get("method") not in {"GET","POST","PUT","DELETE"} or not isinstance(request.get("url"),str): raise ValueError("request needs HTTP method and URL")
    parsed=urlsplit(request["url"])
    if parsed.scheme not in {"http","https"} or not parsed.netloc or parsed.username or parsed.password or parsed.fragment: raise ValueError("unsafe external URL")
    decoded=unquote(parsed.path)
    if any(part in {".",".."} for part in decoded.split("/")): raise ValueError("path traversal forbidden")
    return parsed


def check_body(request: dict) -> str:
    body = request.get("body", "")
    if not isinstance(body, str):
        raise ValueError("body must be text")
    if request["method"] in {"GET", "DELETE"} and body:
        raise ValueError("GET and DELETE cannot carry a nonempty body")
    return body
