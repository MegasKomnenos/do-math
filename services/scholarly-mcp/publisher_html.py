"""Explicit publisher HTML and its document-bound figure files."""
from pathlib import PurePosixPath
from urllib.parse import urljoin,urlsplit,unquote
from bs4 import BeautifulSoup
from browser_adapters import browser_download,clean_html
from scholarly import ServiceError,encoded


def nature_body(raw):
    soup=BeautifulSoup(raw,'html.parser')
    bodies=soup.select('.c-article-body')
    if len(bodies)!=1 or not any(n.get_text(strip=True) for n in bodies[0].select('.main-content .c-article-section__content')):
        raise ServiceError('html_fulltext_not_identified','The page has no recognized Nature full article body',status='not_implemented')
    body=bodies[0]
    for node in body.select('.c-article-recommendations,.app-explore-related-subjects'):
        node.decompose()
    return body


def iop_body(raw):
    soup=BeautifulSoup(raw,'html.parser');bodies=soup.select('.wd-jnl-art-full-text')
    if len(bodies)!=1 or not any(n.get_text(strip=True) for n in bodies[0].select('.article-text p')):
        raise ServiceError('html_fulltext_not_identified','The page has no recognized IOP full article body',status='not_implemented')
    body=bodies[0]
    # Native lazy image URLs must survive clean_html's removal of data attributes.
    for img in body.select('img[data-src]'):img['src']=img['data-src']
    return body


def springer_body(raw):
    soup=BeautifulSoup(raw,'html.parser');bodies=soup.select('.c-article-body')
    if len(bodies)!=1:
        raise ServiceError('html_fulltext_not_identified','The page has no unique Springer article body',status='not_implemented')
    body=bodies[0];sections=[node for node in body.select('[id^="Sec"][id$="-section"]')
                            if node.select_one('.c-article-section__content') and node.select_one('.c-article-section__content').get_text(' ',strip=True)]
    if not sections:
        raise ServiceError('html_fulltext_not_identified','The Springer page exposes no substantive native article section',status='not_implemented')
    for node in body.select('.c-article-recommendations,.app-explore-related-subjects'):node.decompose()
    return body


def fetch_html(adapter,page,identifier,source_page):
    host=urlsplit(page.url).hostname;iop=adapter.source=='iop' and host in ('iopscience.iop.org','iopscience-iop-org.libproxy.knu.ac.kr')
    springer=adapter.source=='springer' and host in ('link.springer.com','link-springer-com.libproxy.knu.ac.kr','link.springernature.com')
    nature=host in ('www.nature.com','www-nature-com.libproxy.knu.ac.kr')
    if not iop and not springer and not nature:
        raise ServiceError('html_layout_not_implemented','Explicit fulltext_html supports the observed Nature, Springer and IOP article layouts',status='not_implemented')
    body=iop_body(page.content()) if iop else springer_body(page.content()) if springer else nature_body(page.content());figures=[]
    iop_asset_directories={str(PurePosixPath(unquote(urlsplit(urljoin(page.url,img.get('src',''))).path)).parent)
                           for img in body.select('figure img.panzoom[src]')} if iop else set()
    for number,img in enumerate(body.select('figure img.panzoom' if iop else 'figure img'),1):
        url=urljoin(page.url,img.get('src',''));figure=img.find_parent('figure',id=True) or img.find_parent('figure')
        caption=figure.select_one('figcaption')
        item={'number':number,'id':figure.get('id'),'url':url,'alt':img.get('alt'),
            'caption':caption.get_text(' ',strip=True) if caption else None}
        try:
            path=unquote(urlsplit(url).path)
            if iop:
                if not identifier or not path.startswith('/journals/'):
                    raise ServiceError('source_boundary','IOP figure is not a native journal content link')
            elif not identifier or ('/art:'+identifier+'/MediaObjects/').casefold() not in path.casefold():
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
    math_files=[]
    if iop:
        controls={}
        for img in body.select('span.texImage > img[src]'):
            controls.setdefault(urljoin(page.url,img.get('src','')),[]).append(img)
        for number,(url,images) in enumerate(controls.items(),1):
            alts=list(dict.fromkeys(img.get('alt') for img in images if img.get('alt')))
            item={'number':number,'url':url,'alt':alts[0] if alts else None,'occurrences':len(images)}
            try:
                parts=urlsplit(url);path=unquote(parts.path);name=PurePosixPath(path).name;parent=str(PurePosixPath(path).parent)
                if parts.hostname not in adapter.profile.download_hosts or '..' in path.split('/') or not path.startswith('/journals/') \
                        or iop_asset_directories and parent not in iop_asset_directories \
                        or not name:
                    raise ServiceError('source_boundary','IOP equation image is not bound to the selected article asset path')
                data,media,actual=browser_download(adapter.gateway.context,url,adapter.profile.download_hosts,headers={'Referer':page.url})
                if unquote(urlsplit(actual).path)!=path:
                    raise ServiceError('source_boundary','IOP equation image download changed the selected article asset path')
                if data.startswith((b'GIF87a',b'GIF89a')):media='image/gif'
                elif data.startswith(b'\x89PNG\r\n\x1a\n'):media='image/png'
                elif data.startswith(b'\xff\xd8\xff'):media='image/jpeg'
                else:raise ServiceError('unexpected_content','The equation image control returned no supported image bytes')
                artifact=adapter.store.put(data,media,adapter.source,actual,preserve_bytes=True,role='equation_image',
                    doi=identifier,equation_number=number,source_control_path=path,parent_ref=source_page['ref'])
                for img in images:img['src']=artifact['ref']
                math_files.append({**item,'status':'available','artifact':artifact})
            except ServiceError as error:
                for img in images:img.attrs.pop('src',None)
                math_files.append({**item,**error.result})
            except Exception as error:
                for img in images:img.attrs.pop('src',None)
                math_files.append({**item,'status':'error','code':'equation_image_retrieval_failed','error_type':type(error).__name__})
            for img in images:img.attrs.pop('srcset',None)
    for node in body.select('picture source'):
        node.decompose()
    for anchor in body.select('a[href]'):
        if not anchor['href'].startswith('#'):anchor['href']=urljoin(page.url,anchor['href'])
    math_available=[f['artifact'] for f in math_files if f['status']=='available']
    math_manifest=adapter.store.put(encoded(math_files),'application/json',adapter.source,page.url,
        role='equation_image_manifest',doi=identifier,parent_ref=source_page['ref'],requested=len(math_files),received=len(math_available)) if iop else None
    artifact=adapter.store.put(clean_html(str(body),adapter.store.sanitizer),'text/html',adapter.source,page.url,
        role='fulltext_html',doi=identifier,parent_ref=source_page['ref'],figure_refs=[f['artifact']['ref'] for f in figures if f['status']=='available'],
        **({'equation_image_manifest_ref':math_manifest['ref']} if iop else {}))
    math_images={'status':'not_found' if not math_files else 'available' if len(math_available)==len(math_files) else 'partial',
        'requested':len(math_files),'received':len(math_available),'manifest':math_manifest,
        'scope':'Native IOP equation images from this article; source TeX remains in the HTML'} if iop else None
    if math_available:math_images['artifact']=math_available[0]
    clean=all(f['status']=='available' for f in figures) and (not iop or math_images['status'] in ('available','not_found'))
    return {'status':'available' if clean else 'partial','artifact':artifact,'figures':figures,
        'format':'sanitized_publisher_html','scope':'Publisher article body and its displayed figures; source TeX is retained without AI interpretation or script execution',
        **({'math_images':math_images} if iop else {})}
