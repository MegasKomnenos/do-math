"""Document-bound attachment controls; no cross-provider discovery."""
import re,io,zipfile
from pathlib import PurePosixPath
from urllib.parse import urljoin,urlsplit,unquote,parse_qs
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
                     'url':url,'linked_doi':match[1] if match else None,'filename':PurePosixPath(urlsplit(url).path).name})
    return rows


def wiley_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    rows=[]
    for anchor in soup.select('.support-info__table a[href*="/action/downloadSupplement"]'):
        url=urljoin(base,anchor['href'])
        query=parse_qs(urlsplit(url).query)
        identifiers,names=query.get('doi',[]),query.get('file',[])
        cells=anchor.find_parent('tr').find_all('td',recursive=False)
        item={'label':anchor.get_text(' ',strip=True),'description':cells[1].get_text(' ',strip=True) if len(cells)>1 else None,
              'url':url,'linked_doi':identifiers[0] if len(identifiers)==1 else None,'filename':names[0] if len(names)==1 else None}
        if len(identifiers)!=1 or len(names)!=1:
            item['invalid_link']=True
        rows.append(item)
    return rows


def aip_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser'); rows=[]; seen=set()
    for anchor in soup.select('.article-section-wrapper a[href]'):
        if not re.search(r'supplement(?:ary|al)\s+material',anchor.get_text(' ',strip=True),re.I): continue
        url=urljoin(base,anchor['href']); parsed=urlsplit(url)
        if parsed.hostname not in ('doi.org','doi-org.libproxy.knu.ac.kr'): continue
        target=unquote(parsed.path).lstrip('/')
        if not re.fullmatch(r'10\.60893/figshare\.aip\.(?:c\.)?\d+(?:\.v\d+)?',target,re.I) or target in seen: continue
        seen.add(target)
        rows.append({'label':anchor.get_text(' ',strip=True),'url':url,'source':'figshare','target':target,'status':'selection_required',
            'reason':'Supplementary material is hosted by Figshare; select that source explicitly'})
    return rows


def fetch_supplementary(adapter,page,identifier,source_page):
    rows={'springer':springer_links,'wiley':wiley_links,'aip':aip_links}[adapter.source](page.content(),page.url)
    if not rows:
        return {'status':'source_page','artifact':source_page,'reason':'No recognized document attachment controls; other supplementary layouts remain in development'}
    index=adapter.store.put(encoded(rows),'application/json',adapter.source,page.url,role='supplementary_index',doi=identifier,parent_ref=source_page['ref'])
    if adapter.source=='aip':
        return {'status':'selection_required','artifact':index,'references':rows,'discovered':len(rows),'received':0,
                'reason':'External supplement references; files require an explicit Figshare call'}
    files=[]
    for row in rows:
        try:
            if row.get('invalid_link'):
                raise ServiceError('invalid_response','The supplementary control does not identify one document and file')
            if row['linked_doi'] and identifier and row['linked_doi'].casefold()!=identifier.casefold():
                raise ServiceError('linked_publication_differs','The attachment path identifies another publication; select that publication explicitly',status='selection_required',linked_doi=row['linked_doi'])
            data,media,url=browser_download(adapter.gateway.context,row['url'],adapter.profile.download_hosts)
            if media in ('text/html','application/xhtml+xml') or data.lstrip().lower().startswith((b'<!doctype html',b'<html')):
                raise ServiceError('unexpected_content','Attachment control returned an HTML page')
            suffix=PurePosixPath(row.get('filename') or urlsplit(row['url']).path).suffix.lower()
            if (media=='application/pdf' or suffix=='.pdf') and not data.startswith(b'%PDF-'):
                raise ServiceError('invalid_document','The supplementary PDF control returned no PDF')
            if suffix=='.zip':
                if not zipfile.is_zipfile(io.BytesIO(data)):
                    raise ServiceError('invalid_document','The supplementary ZIP control returned no readable archive')
                media='application/zip'
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
