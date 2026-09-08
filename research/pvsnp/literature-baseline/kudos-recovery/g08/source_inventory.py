"""Recover actual outgoing links from retained resolver captures."""
from urllib.parse import urlsplit

def incomplete_body(text):
    return text.strip().lower() in {'','불러오는 중...','loading','loading...','loading…'}

def capture_ready(page,expand_label=None,observation=None):
    main=page.locator('main')
    read=lambda: main.first.inner_text() if main.count() else page.locator('body').inner_text()
    if incomplete_body(read()):
        try:
            page.wait_for_function('()=>!["","불러오는 중...","loading","loading...","loading…"].includes((document.querySelector("main")||document.body).innerText.trim().toLowerCase())',timeout=25000)
        except Exception:
            pass
    before=read()
    if expand_label:
        controls=[x for x in page.get_by_text(expand_label,exact=True).all() if x.is_visible()]
        requests=[]
        def observed(request):requests.append(True)
        clicked=False
        if controls:
            page.on('request',observed)
            try:
                controls[0].click();clicked=True;page.wait_for_timeout(1000)
            finally:page.remove_listener('request',observed)
        after=read()
        if observation is not None:
            observation.update(label=expand_label,visible_controls=len(controls),clicked=clicked,before_text=before,after_text=after,requests_observed_after_click=len(requests))
        return after
    return before

def followups(payload):
    host=urlsplit(payload.get('url','')).netloc.lower()
    if not host.endswith('search.serialssolutions.com'):
        return []
    ignored={'인용문 편집','이메일','내보내기','도서관에 도움 요청하기','Privacy Policy','Edit Citation','Email','Export','Get help from your library'}
    links=[]
    for link in payload.get('links',[]):
        if not link.get('url','').startswith(('https://','http://')) or link.get('text','').strip() in ignored:
            continue
        if link['url']==payload['url'] or 'SS_Page=refiner' in link['url']:
            continue
        if link['url'] not in {x['url'] for x in links}:
            links.append(link)
    return links
