"""Document-bound attachment controls; no cross-provider discovery."""
import re
from urllib.parse import urljoin,urlsplit,unquote
from bs4 import BeautifulSoup
from browser_adapters import browser_download
from scholarly import ServiceError,encoded


def springer_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    rows=[]
    for anchor in soup.select('.c-article-supplementary__title a[href]'):
        url=urljoin(base,anchor['href'])
        match=re.search(r'/art:(10\..+?)/MediaObjects/',unquote(urlsplit(url).path),re.I)
        item=anchor.find_parent(class_='c-article-supplementary__item')
        description=item.select_one('.c-article-supplementary__description') if item else None
        rows.append({'label':anchor.get_text(' ',strip=True),'description':description.get_text(' ',strip=True) if description else None,
                     'url':url,'linked_doi':match[1] if match else None})
    return rows


def fetch_springer(adapter,page,identifier,source_page):
    rows=springer_links(page.content(),page.url)
    if not rows:
        return {'status':'source_page','artifact':source_page,'reason':'No recognized document attachment controls; other supplementary layouts remain in development'}
    index=adapter.store.put(encoded(rows),'application/json',adapter.source,page.url,role='supplementary_index',doi=identifier,parent_ref=source_page['ref'])
    files=[]
    for row in rows:
        try:
            if row['linked_doi'] and identifier and row['linked_doi'].casefold()!=identifier.casefold():
                raise ServiceError('linked_publication_differs','The attachment path identifies another publication; select that publication explicitly',status='selection_required',linked_doi=row['linked_doi'])
            data,media,url=browser_download(adapter.gateway.context,row['url'],adapter.profile.download_hosts)
            if media in ('text/html','application/xhtml+xml') or data.lstrip().lower().startswith((b'<!doctype html',b'<html')):
                raise ServiceError('unexpected_content','Attachment control returned an HTML page')
            if (media=='application/pdf' or urlsplit(row['url']).path.lower().endswith('.pdf')) and not data.startswith(b'%PDF-'):
                raise ServiceError('invalid_document','The supplementary PDF control returned no PDF')
            metadata={}
            if data.startswith(b'%PDF-'):
                import pymupdf
                with pymupdf.open(stream=data,filetype='pdf') as document:
                    metadata['pages']=len(document)
                media='application/pdf'
            artifact=adapter.store.put(data,media,adapter.source,url,role='supplementary_file',doi=identifier,label=row['label'],parent_ref=index['ref'],**metadata)
            files.append({**row,'status':'available','artifact':artifact})
        except ServiceError as error:
            files.append({**row,**error.result})
        except Exception as error:
            files.append({**row,'status':'error','code':'attachment_retrieval_failed','error_type':type(error).__name__})
    return {'status':'available' if all(item['status']=='available' for item in files) else 'partial','index':index,'files':files,
            'discovered':len(rows),'received':sum(item['status']=='available' for item in files)}
