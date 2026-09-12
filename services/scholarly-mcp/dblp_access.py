"""DBLP's observed non-JavaScript Anubis timed refresh, within the API client."""
import json,re,time
from urllib.parse import urljoin,urlsplit,parse_qs,parse_qsl
import httpx
from bs4 import BeautifulSoup
from scholarly import ServiceError


def same_request(left,right):
    a,b=urlsplit(left),urlsplit(right)
    return (a.scheme,a.netloc,a.path,parse_qsl(a.query,keep_blank_values=True),a.fragment)==(b.scheme,b.netloc,b.path,parse_qsl(b.query,keep_blank_values=True),b.fragment)


def timed_refresh(adapter,response):
    if response.status_code!=200 or 'html' not in response.headers.get('content-type',''):return response
    soup=BeautifulSoup(response.content,'html.parser');node=soup.select_one('script#anubis_challenge[type="application/json"]')
    if node is None:return response
    try:state=json.loads(node.get_text())
    except ValueError:raise ServiceError('access_challenge','DBLP returned an unreadable verification challenge',status='restricted') from None
    if not isinstance(state,dict) or not isinstance(state.get('rules'),dict) or state['rules'].get('algorithm')!='metarefresh':return response
    meta=soup.select_one('meta[http-equiv="refresh"]');value=response.headers.get('refresh') or (meta.get('content','') if meta else '')
    match=re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*;\s*url\s*=\s*(.+)',value,re.I)
    if not match or not 0<=float(match[1])<=10:
        raise ServiceError('unsupported_verification','DBLP timed refresh is missing or exceeds 10 seconds',status='restricted')
    original=str(response.url);target=urljoin(original,match[2].strip().strip('"\''));parts=urlsplit(target);origin=urlsplit(original);query=parse_qs(parts.query)
    challenge=state.get('challenge',{})
    redirect=query.get('redir',[])
    if (not adapter.allowed_url(target) or parts.netloc!=origin.netloc or parts.path!='/.within.website/x/cmd/anubis/api/pass-challenge'
            or len(redirect)!=1 or not same_request(urljoin(original,redirect[0]),original)
            or not isinstance(challenge,dict) or not challenge.get('id') or not challenge.get('randomData')
            or query.get('id')!=[challenge['id']] or query.get('challenge')!=[challenge['randomData']]):
        raise ServiceError('verification_boundary','DBLP verification does not preserve the source and requested API URL',status='restricted')
    time.sleep(float(match[1]));adapter.last_request=time.monotonic()
    try:verified=adapter.client.get(target,follow_redirects=False)
    except httpx.HTTPError:raise ServiceError('verification_connection_failed','DBLP verification connection failed',status='restricted') from None
    if not verified.is_redirect or not same_request(urljoin(target,verified.headers.get('location','')),original):
        raise ServiceError('verification_failed','DBLP did not return from verification to the requested API URL',status='restricted',http_status=verified.status_code)
    # Never preserve the challenge page, token-bearing refresh URL, or cookie as an artifact.
    return verified
