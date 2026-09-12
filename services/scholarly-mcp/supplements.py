"""Document-bound attachment controls; no cross-provider discovery."""
import re,io,zipfile
from pathlib import PurePosixPath
from urllib.parse import urljoin,urlsplit,urlunsplit,unquote,parse_qs
from bs4 import BeautifulSoup
from browser_adapters import browser_download,clean_html
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


def cambridge_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser'); rows=[]
    for item in soup.select('#supplementary-materials-tab .materials-table__item'):
        title=item.select_one('.materials-table__row__title')
        description=item.select_one('.materials-table__row__description')
        for anchor in item.select('a.materials-table__row__download-button[href]'):
            url=urljoin(base,anchor['href']); path=unquote(urlsplit(url).path)
            match=re.search(r'/urn:cambridge\.org:id:article:([^/]+)/resource/name/',path)
            rows.append({'label':title.get_text(' ',strip=True) if title else anchor.get_text(' ',strip=True),
                'description':description.get_text(' ',strip=True) if description else None,'url':url,
                'linked_doi':None,'linked_pii':match[1] if match else None,'filename':PurePosixPath(path).name})
    return rows


def oxford_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser'); rows=[]
    for anchor in soup.select('.widget-ArticleDataSupplements .dataSuppLink a[href]'):
        url=urljoin(base,anchor['href']); path=unquote(urlsplit(url).path)
        match=re.search(r'/(10\.\d{4,9}_[^/]+)/',path)
        rows.append({'label':anchor.get_text(' ',strip=True),'description':anchor.parent.get_text(' ',strip=True),
            'url':url,'linked_doi':None,'linked_doi_path':match[1] if match else None,'filename':PurePosixPath(path).name})
    return rows


def taylor_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser'); rows=[]
    for selector,role in [('#supplemental-material-section a[href*="/action/downloadSupplement"]','supplementary_file'),
                          ('.tableDownloadOption a[href*="/action/downloadTable"]','article_table')]:
        for anchor in soup.select(selector):
            url=urljoin(base,anchor['href']); query=parse_qs(urlsplit(url).query)
            identifiers=query.get('doi',[]); names=query.get('file' if role=='supplementary_file' else 'id',[])
            valid=len(identifiers)==len(names)==1
            if role=='article_table':valid=valid and query.get('downloadType')==['CSV']
            rows.append({'role':role,'label':anchor.get_text(' ',strip=True),'description':None,'url':url,
                         'linked_doi':identifiers[0] if len(identifiers)==1 else None,'invalid_link':not valid,
                         'filename':names[0]+('.csv' if role=='article_table' else '') if len(names)==1 else None,
                         **({'table_id':names[0]} if role=='article_table' and len(names)==1 else {})})
    return rows


def degruyter_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser');rows=[]
    for anchor in soup.select('.supplementary-material-list a.ga_download_supplementary[href]'):
        url=urljoin(base,anchor['href']);path=unquote(urlsplit(url).path)
        match=re.fullmatch(r'/document/doi/(10\..+?)/downloadAsset/(?:suppl/)?([^/]+)',path)
        rows.append({'label':anchor.get_text(' ',strip=True),'description':None,'url':url,
                     'linked_doi':match[1] if match else None,'filename':match[2] if match else None,'invalid_link':match is None})
    return rows


def acm_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser');rows=[]
    for item in soup.select('.core-supplementary-materials .core-supplementary-material'):
        label=item.select_one('.core-label');description=item.select_one('.core-description > div')
        for anchor in item.select('.core-link a[href]'):
            url=urljoin(base,anchor['href']);path=unquote(urlsplit(url).path)
            match=re.fullmatch(r'/doi/suppl/(10\..+?)/suppl_file/([^/]+)',path)
            rows.append({'label':label.get_text(' ',strip=True) if label else anchor.get_text(' ',strip=True),
                'description':description.get_text(' ',strip=True) if description else None,'url':url,
                'linked_doi':match[1] if match else None,'filename':match[2] if match else None,'invalid_link':match is None})
    return rows


def euclid_links(raw,base):
    soup=BeautifulSoup(raw,'html.parser');rows=[]
    for anchor in soup.select('#divARTICLECONTENTCITEDTop .ArticleContentAnchorRow a.ArticleContentAnchorText[href]'):
        url=urljoin(base,anchor['href']);path=unquote(urlsplit(url).path)
        match=re.fullmatch(r'/journals/supplementalcontent/(10\..+)/([^/]+)',path)
        download_row=anchor.find_parent(class_='ArticleContentAnchorRow')
        doi_row=download_row.find_previous_sibling('div',class_='ArticleContentRow')
        content_row=doi_row.find_previous_sibling('div',class_='ArticleContentRow') if doi_row else None
        title=content_row.select_one('b') if content_row else None
        description=content_row.select_one('p') if content_row else None
        supplement=re.search(r'Digital Object Identifier:\s*(10\.\S+)',doi_row.get_text(' ',strip=True)) if doi_row else None
        rows.append({'label':title.get_text(' ',strip=True) if title else anchor.get_text(' ',strip=True),
            'description':description.get_text(' ',strip=True) if description else None,'url':url,
            'linked_doi':match[1] if match else None,'filename':match[2] if match else None,
            'supplement_doi':supplement[1] if supplement else None,'invalid_link':match is None})
    return rows


def iop_links(raw,base):
    match=re.fullmatch(r'/article/(10\.\d{4,9}/.+)/data',unquote(urlsplit(base).path))
    if not match:raise ServiceError('identity_mismatch','IOP attachments require the selected article data page')
    soup=BeautifulSoup(raw,'html.parser');rows=[]
    for anchor in soup.select('#supplementarydata a[href]'):
        native=urljoin(base,anchor['href']);location=urlsplit(native);url=native;path=unquote(location.path)
        storage='cfn-live-content-bucket-iop-org.s3.eu-west-1.amazonaws.com'
        # The observed proxy rewrite makes a 65-byte DNS label; use the signed storage URL.
        if location.hostname==storage.replace('-','--').replace('.','-')+'.libproxy.knu.ac.kr' and not location.username and not location.password and location.port is None:
            url=urlunsplit((location.scheme,storage,location.path,location.query,location.fragment))
        rows.append({'label':anchor.get_text(' ',strip=True),'description':anchor.parent.get_text(' ',strip=True),
            'url':url,'native_url':native,'linked_doi':match[1],'filename':PurePosixPath(path).name,
            'identity_basis':'Native file control on the selected DOI supplementary page'})
    return rows


def fetch_supplementary(adapter,page,identifier,source_page,*,download_hosts=None):
    if adapter.source=='project-euclid' and page.locator('#sup').count():
        try:
            page.locator('#sup').click(timeout=20000)
            page.locator('#divARTICLECONTENTCITEDTop .ArticleContentAnchorRow a.ArticleContentAnchorText').first.wait_for(state='attached',timeout=20000)
        except Exception as error:
            return {'status':'error','code':'supplementary_tab_not_ready','error_type':type(error).__name__,'artifact':source_page}
        source_page=adapter.store.put(clean_html(page.content(),adapter.store.sanitizer),'text/html',adapter.source,page.url,
            role='supplementary_source_page',doi=identifier,parent_ref=source_page['ref'])
    raw=page.content()
    rows={'springer':springer_links,'wiley':wiley_links,'aip':aip_links,'cambridge':cambridge_links,'oxford':oxford_links,'taylor-francis':taylor_links,'de-gruyter':degruyter_links,'acm-dl':acm_links,'project-euclid':euclid_links,'iop':iop_links}[adapter.source](raw,page.url)
    if not rows:
        return {'status':'source_page','artifact':source_page,'reason':'No recognized document attachment controls; other supplementary layouts remain in development'}
    index=adapter.store.put(encoded(rows),'application/json',adapter.source,page.url,role='supplementary_index',doi=identifier,parent_ref=source_page['ref'])
    if adapter.source=='aip':
        return {'status':'selection_required','artifact':index,'references':rows,'discovered':len(rows),'received':0,
                'reason':'External supplement references; files require an explicit Figshare call'}
    files=[]
    expected_pii=set()
    if adapter.source=='cambridge':
        soup=BeautifulSoup(raw,'html.parser')
        expected_pii={m[1] for tag in soup.select('meta[name="citation_pdf_url"][content]') if (m:=re.search(r'/(S\d+[A-Z]?)a\.pdf/',tag['content']))}
    for row in rows:
        try:
            if row.get('invalid_link'):
                raise ServiceError('invalid_response','The supplementary control does not identify one document and file')
            if row['linked_doi'] and identifier and row['linked_doi'].casefold()!=identifier.casefold():
                raise ServiceError('linked_publication_differs','The attachment path identifies another publication; select that publication explicitly',status='selection_required',linked_doi=row['linked_doi'])
            if row.get('linked_doi_path') and identifier and row['linked_doi_path'].casefold()!=identifier.replace('/','_').casefold():
                raise ServiceError('linked_publication_differs','The attachment path differs from the encoded document DOI',status='selection_required',linked_doi_path=row['linked_doi_path'])
            if row.get('linked_pii') and expected_pii and row['linked_pii'] not in expected_pii:
                raise ServiceError('linked_publication_differs','The attachment PII differs from the document PDF metadata',status='selection_required',linked_pii=row['linked_pii'])
            data,media,url=browser_download(adapter.gateway.context,row['url'],adapter.profile.download_hosts if download_hosts is None else download_hosts)
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
            if suffix=='.csv':
                media='text/csv'
            if data.startswith(b'%PDF-'):
                import pymupdf
                with pymupdf.open(stream=data,filetype='pdf') as document:
                    metadata['pages']=len(document)
                media='application/pdf'
            artifact=adapter.store.put(data,media,adapter.source,url,preserve_bytes=True,role=row.get('role','supplementary_file'),doi=identifier,label=row['label'],parent_ref=index['ref'],**metadata)
            files.append({**row,'status':'available','artifact':artifact})
        except ServiceError as error:
            files.append({**row,**error.result})
        except Exception as error:
            files.append({**row,'status':'error','code':'attachment_retrieval_failed','error_type':type(error).__name__})
    return {'status':'available' if all(item['status']=='available' for item in files) else 'partial','index':index,'files':files,
            'discovered':len(rows),'received':sum(item['status']=='available' for item in files)}
