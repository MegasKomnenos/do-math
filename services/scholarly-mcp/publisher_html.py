"""Explicit publisher HTML and its document-bound figure files."""
from urllib.parse import urljoin,urlsplit,unquote
from bs4 import BeautifulSoup
from browser_adapters import browser_download,clean_html
from scholarly import ServiceError


def nature_body(raw):
    soup=BeautifulSoup(raw,'html.parser')
    bodies=soup.select('.c-article-body')
    if len(bodies)!=1 or not any(n.get_text(strip=True) for n in bodies[0].select('.main-content .c-article-section__content')):
        raise ServiceError('html_fulltext_not_identified','The page has no recognized Nature full article body',status='not_implemented')
    body=bodies[0]
    for node in body.select('.c-article-recommendations,.app-explore-related-subjects'):
        node.decompose()
    return body


def fetch_html(adapter,page,identifier,source_page):
    if urlsplit(page.url).hostname not in ('www.nature.com','www-nature-com.libproxy.knu.ac.kr'):
        raise ServiceError('html_layout_not_implemented','Explicit fulltext_html currently supports the observed Nature article layout',status='not_implemented')
    body=nature_body(page.content());figures=[]
    for number,img in enumerate(body.select('figure img'),1):
        url=urljoin(page.url,img.get('src',''));figure=img.find_parent('figure')
        caption=figure.select_one('figcaption')
        item={'number':number,'id':figure.get('id'),'url':url,'alt':img.get('alt'),
            'caption':caption.get_text(' ',strip=True) if caption else None}
        try:
            path=unquote(urlsplit(url).path)
            if not identifier or ('/art:'+identifier+'/MediaObjects/').casefold() not in path.casefold():
                raise ServiceError('source_boundary','Figure path is not bound to the selected Nature DOI')
            data,media,actual=browser_download(adapter.gateway.context,url,adapter.profile.download_hosts)
            if data.startswith(b'\x89PNG\r\n\x1a\n'):media='image/png'
            elif data.startswith(b'\xff\xd8\xff'):media='image/jpeg'
            else:raise ServiceError('unexpected_content','The figure control returned no supported PNG or JPEG image')
            import pymupdf
            pixmap=pymupdf.Pixmap(data)
            artifact=adapter.store.put(data,media,adapter.source,actual,preserve_bytes=True,role='article_figure',
                doi=identifier,width=pixmap.width,height=pixmap.height,parent_ref=source_page['ref'])
            img['src']=artifact['ref']
            figures.append({**item,'status':'available','artifact':artifact})
        except ServiceError as error:
            img.attrs.pop('src',None)
            figures.append({**item,**error.result})
        except Exception as error:
            img.attrs.pop('src',None)
            figures.append({**item,'status':'error','code':'figure_retrieval_failed','error_type':type(error).__name__})
        img.attrs.pop('srcset',None)
    for node in body.select('picture source'):
        node.decompose()
    for anchor in body.select('a[href]'):
        if not anchor['href'].startswith('#'):anchor['href']=urljoin(page.url,anchor['href'])
    artifact=adapter.store.put(clean_html(str(body),adapter.store.sanitizer),'text/html',adapter.source,page.url,
        role='fulltext_html',doi=identifier,parent_ref=source_page['ref'],figure_refs=[f['artifact']['ref'] for f in figures if f['status']=='available'])
    return {'status':'available' if all(f['status']=='available' for f in figures) else 'partial','artifact':artifact,'figures':figures,
        'format':'sanitized_publisher_html','scope':'Publisher article body and its displayed figures; source TeX is retained without AI interpretation or script execution'}
