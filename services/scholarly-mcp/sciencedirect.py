"""ScienceDirect institutional citation exports and document retrieval."""
import csv,io,json,mimetypes,re
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit, unquote

from bs4 import BeautifulSoup
from browser_adapters import browser_download,clean_html,goto_source,is_access_challenge
from api_adapters import doi
from publishers import Publisher, PROFILES
from scholarly import ServiceError, bibliography, encoded

FORMATS = {'ris': 'application/x-research-info-systems', 'bibtex': 'text/x-bibtex', 'plain': 'text/plain'}
SEARCH_FIELDS={'Anywhere':'qs','Title':'title','TitleAbstractKeywords':'tak','Author':'authors','Affiliation':'affiliations',
               'Publication':'pub','References':'references','ISSNISBN':'docId'}
FACET_GROUPS={'articleTypes':'article_type','publicationTitles':'publication_title','subjectAreas':'subject_area',
              'languages':'language','accessTypes':'access_type'}
FACET_OPTIONS={'article_types':'articleTypes','publication_titles':'publicationTitles','subject_areas':'subjectAreas',
               'languages':'languages','access_types':'accessTypes'}


def pii_from_url(url):
    match = re.search(r'/pii/([A-Z0-9]+)(?:/|$)', unquote(urlsplit(url).path))
    if not match:
        raise ServiceError('invalid_target', 'The ScienceDirect URL has no PII')
    return match[1]


def citation_record(data, pii, expected_doi=None):
    rows = bibliography(data, 'application/x-research-info-systems')
    if len(rows) != 1:
        raise ServiceError('identity_mismatch', 'ScienceDirect returned no unique citation')
    row = rows[0]
    if not any(pii_from_url(url) == pii for url in row['fields'].get('ur', []) if '/pii/' in url):
        raise ServiceError('identity_mismatch', 'ScienceDirect citation identifies another PII')
    observed = row['fields'].get('do', [None])[0]
    if expected_doi and (not observed or doi(observed).casefold() != expected_doi.casefold()):
        raise ServiceError('identity_mismatch', 'ScienceDirect citation identifies another DOI')
    return {'id':pii, 'pii':pii, 'title':row['fields'].get('t1',row['fields'].get('ti',[None]))[0],
            'doi':doi(observed) if observed else None, **row}


def search_page(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    count=soup.select_one('span.search-body-results-text')
    match=re.fullmatch(r'\s*([\d,]+)\s+results?(?:\s+found)?\s*',count.get_text(' ',strip=True) if count else '',re.I)
    if not match:
        empty=soup.select_one('div.error-zero-results')
        if empty and re.search(r'\b(?:no|0)\s+(?:search\s+)?results?\b',empty.get_text(' ',strip=True),re.I):return [],0,0,0
        raise ServiceError('invalid_response','ScienceDirect returned no recognized native result count')
    total=int(match[1].replace(',',''))
    rows=[];seen=set()
    for item in soup.select('li.ResultItem'):
        anchor=item.select_one('a.result-list-title-link[href*="/science/article/pii/"]')
        checkbox=item.select_one('input.checkbox-input[type="checkbox"][id]')
        if anchor is None or checkbox is None:
            raise ServiceError('invalid_response','ScienceDirect result is missing its native PII controls')
        url=urljoin(base,anchor['href']);pii=pii_from_url(url)
        if checkbox.get('id')!=pii or pii in seen:
            raise ServiceError('identity_mismatch','ScienceDirect result controls identify different or duplicate PII records')
        seen.add(pii)
        source=item.select_one('.srctitle-date-fields');publication=source.select_one('a.subtype-srctitle-link') if source else None
        source_text=source.get_text(' ',strip=True) if source else ''
        publication_text=publication.get_text(' ',strip=True) if publication else None
        published=source_text[len(publication_text):].strip() if publication_text and source_text.startswith(publication_text) else source_text or None
        pdf=None
        for candidate in item.select('a.download-link[href*="/pdfft"]'):
            value=urljoin(base,candidate['href'])
            try:matches=pii_from_url(value)==pii
            except ServiceError:matches=False
            if matches:
                pdf=value;break
        rows.append({'id':pii,'pii':pii,'doi':None,'title':anchor.get_text(' ',strip=True),'url':url,
                     'publication':publication_text,'publication_date':published,'pdf_url':pdf,
                     'authors':[node.get_text(' ',strip=True) for node in item.select('ol.Authors span.author')],
                     'listing':item.get_text('\n',strip=True)})
    if total==0 and rows:
        raise ServiceError('range_mismatch','ScienceDirect returned rows for a zero-result search')
    if total and not rows:
        raise ServiceError('invalid_response','ScienceDirect result count has no native PII rows')
    indicator=next((node for node in soup.select('ol#srp-pagination > li')
                    if re.fullmatch(r'Page\s+[\d,]+\s+of\s+[\d,]+',node.get_text(' ',strip=True),re.I)),None)
    if total and indicator is None:
        raise ServiceError('invalid_response','ScienceDirect returned no native page indicator')
    if indicator:
        current,pages=(int(value.replace(',','')) for value in re.fullmatch(
            r'Page\s+([\d,]+)\s+of\s+([\d,]+)',indicator.get_text(' ',strip=True),re.I).groups())
        if current<1 or pages<current:raise ServiceError('range_mismatch','ScienceDirect returned an invalid page indicator')
    else:current=pages=0
    return rows,total,current,pages


def search_records(raw,base):
    rows,total,_,_=search_page(raw,base)
    return rows,total


def facet_candidates(raw):
    soup=BeautifulSoup(raw,'html.parser');found=[]
    for node in soup.select('input[type="checkbox"][id]'):
        match=re.fullmatch(r'(articleTypes|publicationTitles|subjectAreas|languages|accessTypes)-(.+)',node['id'])
        if not match:continue
        native,value=match.groups();label=str(node.get('name') or '').strip()
        if not label:continue
        container=node.find_parent('label') or node.parent
        numbers=re.findall(r'[\d,]+',container.get_text(' ',strip=True) if container else '')
        count=int(numbers[-1].replace(',','')) if numbers else None
        found.append({'group':FACET_GROUPS[native],'native_group':native,'value':value,'label':label,'count':count,
                      'selected':node.has_attr('checked') or node.get('aria-checked')=='true'})
    return found


def result_filter_state(raw):
    soup=BeautifulSoup(raw,'html.parser')
    subscribed=soup.select_one('#subscribedJournalsToggle')
    mode=soup.select_one('input[name="years-facet-mode"]:checked')
    start=soup.select_one('#year-range-start');end=soup.select_one('#year-range-end')
    return {'subscribed':bool(subscribed and (subscribed.has_attr('checked') or subscribed.get('aria-checked')=='true')),
            'year_mode':mode.get('value') if mode else None,'year_start':start.get('value') if start else None,
            'year_end':end.get('value') if end else None}


def facet_group_state(raw):
    soup=BeautifulSoup(raw,'html.parser');facets=facet_candidates(raw);result={}
    for native,public in FACET_GROUPS.items():
        count=sum(item['native_group']==native for item in facets)
        expandable=bool(soup.select_one('button[aria-label="Show more '+native+' filters"]'))
        if count:result[public]={'native_group':native,'complete':not expandable,'expandable':expandable,'visible_candidates':count}
    return result


def expand_result_facets(page):
    """Expand every current result-facet group that offers a native Show more control."""
    expanded=[]
    for native in ('articleTypes','publicationTitles','subjectAreas','languages'):
        button=page.locator(f'button[aria-label="Show more {native} filters"]')
        if not button.count() or not button.is_visible():continue
        before=page.locator(f'input[id^="{native}-"]').count()
        button.click()
        try:
            page.wait_for_function("value => document.querySelectorAll('input[id^=\"'+value.native+'-\"]').length > value.before",
                                   arg={'native':native,'before':before},timeout=10000)
        except Exception:
            raise ServiceError('facet_expansion_failed','ScienceDirect did not expand a current result facet group',field=FACET_GROUPS[native]) from None
        expanded.append(native)
    return expanded


def supplementary_links(raw,base,pii,hosts):
    """Read only document-bound ScienceDirect multimedia-component links."""
    soup=BeautifulSoup(raw,'html.parser');result=[];seen=set()
    pattern=re.compile(r'/content/image/1-s2\.0-([A-Z0-9]+)-mmc\d+(?:\.[A-Za-z0-9]+)?$',re.I)
    for anchor in soup.select('a[href]'):
        url=urljoin(base,anchor['href']);parsed=urlsplit(url);match=pattern.fullmatch(parsed.path)
        if not match:continue
        if match[1].casefold()!=pii.casefold():
            raise ServiceError('identity_mismatch','ScienceDirect supplementary control identifies another PII')
        if parsed.hostname not in hosts:
            raise ServiceError('source_boundary','ScienceDirect supplementary control left the publisher file hosts',blocked_host=parsed.hostname)
        if url in seen:continue
        seen.add(url);label=' '.join((anchor.get('title') or anchor.get_text(' ',strip=True) or '').split())
        result.append({'url':url,'path':parsed.path,'label':label})
    return result


def native_supplementary(publisher,pii,source_page):
    """Download the native mmc files named for the exact article PII."""
    _,raw=publisher.store.read(source_page['ref'])
    links=supplementary_links(raw.decode('utf-8'),source_page['url'],pii,publisher.profile.download_hosts)
    page=None
    if not links:
        try:
            page=publisher.document('https://www.sciencedirect.com/science/article/pii/'+pii)
            try:page.locator(f'a[href*="-{pii}-mmc"]').first.wait_for(state='attached',timeout=12000)
            except Exception:pass
            live=page.content()
            source_page=publisher.store.put(clean_html(live,publisher.store.sanitizer),'text/html',publisher.source,page.url,
                role='supplementary_source_page',pii=pii,parent_ref=source_page['ref'])
            links=supplementary_links(live,page.url,pii,publisher.profile.download_hosts)
        except ServiceError:
            if page is not None:page.close()
            raise
        except Exception as error:
            if page is not None:page.close()
            raise ServiceError('supplementary_page_failed','ScienceDirect supplementary controls could not be read',error_type=type(error).__name__) from None
    if not links:
        if page is not None:page.close()
        return {'status':'source_page','artifact':source_page,
                'reason':'No document-bound ScienceDirect supplementary file control was identified on this article'}
    files=[];errors=[]
    try:
        for link in links:
            try:
                data,media,actual=browser_download(publisher.gateway.context,link['url'],publisher.profile.download_hosts)
                if not data or data.lstrip().startswith(b'<'):
                    raise ServiceError('unexpected_content','ScienceDirect supplementary control returned no file')
                suffix=link['path'].rsplit('/',1)[-1].rsplit('.',1)[-1].casefold() if '.' in link['path'].rsplit('/',1)[-1] else ''
                if suffix=='mp4' and (len(data)<12 or data[4:8]!=b'ftyp'):
                    raise ServiceError('unexpected_content','ScienceDirect supplementary video is not an MP4 file')
                expected_media=mimetypes.guess_type(link['path'])[0]
                artifact=publisher.store.put(data,expected_media or media or 'application/octet-stream',publisher.source,actual,
                    preserve_bytes=True,role='supplementary',pii=pii,suggested_filename=link['path'].rsplit('/',1)[-1],
                    source_control_path=link['path'])
                files.append({'label':link['label'] or link['path'].rsplit('/',1)[-1],'artifact':artifact})
            except ServiceError as error:errors.append({'label':link['label'],**error.result})
            except Exception as error:errors.append({'label':link['label'],'status':'error','code':'supplementary_retrieval_failed','error_type':type(error).__name__})
    finally:
        if page is not None:page.close()
    return {'status':'partial' if errors and files else 'error' if errors else 'available','files':files,'errors':errors,
            'artifact':source_page,'scope':'Native multimedia-component files whose source path contains the exact article PII'}


def validate_search_location(url,expected):
    parsed=urlsplit(url)
    if parsed.path!='/search':raise ServiceError('query_mismatch','ScienceDirect did not retain the native search path')
    actual=parse_qs(parsed.query,keep_blank_values=True)
    wanted={key:[str(value)] for key,value in expected.items()}
    if any(actual.get(key)!=value for key,value in wanted.items()):
        raise ServiceError('query_mismatch','ScienceDirect did not retain the requested native search fields')
    semantic=set(SEARCH_FIELDS.values())|{'date','volume','issue','page','sortBy','cid','subs','years'}|set(FACET_GROUPS)
    if any(key not in wanted and any(value for value in values) for key,values in actual.items() if key in semantic):
        raise ServiceError('query_mismatch','ScienceDirect retained an unrequested native search filter')


def search_params(query,options,offset,show):
    if not isinstance(query,str) or not isinstance(options,dict) or type(offset) is not int or type(show) is not int:
        raise ServiceError('invalid_options','ScienceDirect query, options and result range have invalid types')
    allowed={'field','publication','publication_exact','date','subscribed_only','authors','affiliations','volume','issue','page','title','references','doc_id','sort'}|set(FACET_OPTIONS)
    if set(options)-allowed:raise ServiceError('invalid_options','Use the documented ScienceDirect advanced-search fields')
    if any(key not in ({'field','subscribed_only'}|set(FACET_OPTIONS)) and not isinstance(value,str) for key,value in options.items()):
        raise ServiceError('invalid_options','ScienceDirect advanced-search values must be strings')
    if 'subscribed_only' in options and type(options['subscribed_only']) is not bool:
        raise ServiceError('invalid_options','subscribed_only must be true or false')
    field=options.get('field','Anywhere')
    if not isinstance(field,str) or field not in SEARCH_FIELDS:
        raise ServiceError('invalid_options','Use a documented ScienceDirect native search field')
    aliases={'publication':'pub','date':'date','authors':'authors','affiliations':'affiliations','volume':'volume','issue':'issue',
             'page':'page','title':'title','references':'references','doc_id':'docId'}
    primary=SEARCH_FIELDS[field]
    params={primary:query} if query.strip() else {}
    for key,native in aliases.items():
        if key in options:
            if native==primary:raise ServiceError('invalid_options','The primary field and an additional field must not overlap')
            params[native]=str(options[key])
    if 'date' in params:
        years=re.fullmatch(r'(\d{4})(?:-(\d{4}))?',params['date'].strip())
        if not years or years[2] and int(years[2])<int(years[1]):
            raise ServiceError('invalid_options','ScienceDirect date must be YYYY or an ordered YYYY-YYYY range')
    for name in ('volume','issue','page'):
        if name in params and not re.fullmatch(r'\d+(?:-\d+)?',params[name].strip()):
            raise ServiceError('invalid_options','ScienceDirect volume, issue and page values must be a number or numeric range')
    for option,native in FACET_OPTIONS.items():
        if option not in options:continue
        values=options[option]
        if not isinstance(values,list) or not values or any(not isinstance(value,str) or not value or ',' in value for value in values) or len(set(values))!=len(values):
            raise ServiceError('invalid_options','ScienceDirect facet arrays need unique current values without commas')
        params[native]=','.join(values)
    if options.get('subscribed_only'):params['subs']='true'
    if not any(str(value).strip() for value in params.values()) and not str(options.get('publication_exact','')).strip():
        raise ServiceError('invalid_query','Provide at least one nonempty ScienceDirect search field or current result filter')
    sort=options.get('sort','relevance')
    if sort not in ('relevance','date'):raise ServiceError('invalid_options','sort must be relevance or date')
    if sort=='date':params['sortBy']='date'
    params.update(offset=offset,show=show)
    return params


def title_key(value):
    """Compare text-node spacing without changing letters, symbols or source bytes."""
    return re.sub(r'\s+','',value) if isinstance(value,str) else None


def native_search_citation(publisher,page,row,index,format='ris',expected_doi=None):
    """Download one citation from the exact native search-result control."""
    formats={'ris':('Export citation to RIS','application/x-research-info-systems'),
             'bibtex':('Export citation to BibTeX','application/x-bibtex'),
             'plain':('Export citation to text','text/plain')}
    if format not in formats:raise ServiceError('invalid_export','Use ris, bibtex or plain for ScienceDirect native citations')
    if not hasattr(publisher.gateway,'native_download'):
        raise ServiceError('native_browser_required','ScienceDirect result citation export requires the native Chrome gateway',status='restricted')
    item=page.locator('li.ResultItem').nth(index)
    checkbox=item.locator('input.checkbox-input[type="checkbox"]')
    title=item.locator('a.result-list-title-link[href*="/science/article/pii/"]')
    if checkbox.get_attribute('id')!=row['pii'] or pii_from_url(urljoin(page.url,title.get_attribute('href')))!=row['pii'] or title_key(title.inner_text())!=title_key(row['title']):
        raise ServiceError('identity_mismatch','ScienceDirect citation controls do not match the selected result row')
    label,media=formats[format]
    choice=item.get_by_role('button',name=label,exact=True)
    if not choice.count() or not choice.is_visible():
        trigger=item.get_by_role('button',name='Export',exact=True)
        try:trigger.wait_for(state='visible',timeout=10000)
        except Exception:
            raise ServiceError('native_export_not_offered','This ScienceDirect result row has no native Export control',status='not_offered') from None
        trigger.click()
        choice=item.get_by_role('button',name=label,exact=True)
    try:choice.wait_for(state='visible',timeout=10000)
    except Exception:
        raise ServiceError('native_export_not_offered','This ScienceDirect result row does not offer the requested citation format',status='not_offered') from None
    data,filename,actual=publisher.gateway.native_download(
        page,lambda:choice.click(),publisher.profile.hosts,'/search/api/export-citations')
    if format=='ris':
        record=citation_record(data,row['pii'],expected_doi)
        observed_title=record.get('title');observed_doi=record.get('doi')
    elif format=='bibtex':
        parsed=bibliography(data,media)
        if len(parsed)!=1:raise ServiceError('identity_mismatch','ScienceDirect BibTeX is not one selected record')
        record=parsed[0];observed_title=record.get('title');observed=record.get('doi')
        observed_doi=doi(observed) if observed else None
        if row['pii'].casefold().encode() not in data.lower():raise ServiceError('identity_mismatch','ScienceDirect BibTeX does not identify the selected PII')
    else:
        if not data.strip() or data.lstrip().startswith(b'<'):
            raise ServiceError('unexpected_content','ScienceDirect returned no plain citation')
        text=data.decode('utf-8-sig')
        observed_title=row['title'] if title_key(row['title']) in title_key(text) else None
        observed_doi=expected_doi if expected_doi and expected_doi.casefold() in text.casefold() else None
        if row['pii'].casefold() not in text.casefold():raise ServiceError('identity_mismatch','ScienceDirect plain citation does not identify the selected PII')
    if title_key(observed_title)!=title_key(row['title']) or expected_doi and (not observed_doi or observed_doi.casefold()!=expected_doi.casefold()):
        raise ServiceError('identity_mismatch','ScienceDirect citation title or DOI differs from the selected result row')
    parsed=urlsplit(actual);safe_url=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,'',''))
    artifact=publisher.store.put(data,media,publisher.source,safe_url,role='native_search_citation',
                                 pii=row['pii'],doi=observed_doi,suggested_filename=filename,parent_title=row['title'],format=format)
    return {'status':'available','artifact':artifact,'pii':row['pii'],'doi':observed_doi,'title':observed_title,
            'format':format,'scope':'One native search-result citation selected by PII'}


def native_result_pdf(publisher,page,row,index,expected_doi):
    """Download the PII-bound result PDF and verify its source identity."""
    if not hasattr(publisher.gateway,'native_download'):
        raise ServiceError('native_browser_required','ScienceDirect PDF requires the native Chrome gateway',status='restricted')
    item=page.locator('li.ResultItem').nth(index)
    checkbox=item.locator('input.checkbox-input[type="checkbox"]')
    title=item.locator('a.result-list-title-link[href*="/science/article/pii/"]')
    if checkbox.get_attribute('id')!=row['pii'] or pii_from_url(urljoin(page.url,title.get_attribute('href')))!=row['pii'] or title_key(title.inner_text())!=title_key(row['title']):
        raise ServiceError('identity_mismatch','ScienceDirect PDF controls do not match the selected result row')
    control=item.get_by_role('link',name='View PDF',exact=True)
    if not control.count():raise ServiceError('fulltext_not_offered','This ScienceDirect result row has no View PDF control',status='not_offered')
    control_url=urljoin(page.url,control.get_attribute('href'))
    if pii_from_url(control_url)!=row['pii'] or not urlsplit(control_url).path.endswith('/pdfft'):
        raise ServiceError('identity_mismatch','ScienceDirect PDF control identifies another publication')
    def path_matches(path):return row['pii'] in path and path.endswith('/main.pdf')
    data,filename,actual=publisher.gateway.native_download(page,lambda:control.click(),publisher.profile.download_hosts,path_matches)
    if not data.startswith(b'%PDF-'):
        raise ServiceError('unexpected_content','ScienceDirect View PDF returned no PDF')
    import pymupdf
    try:
        with pymupdf.open(stream=data,filetype='pdf') as document:
            pages=len(document);metadata_title=document.metadata.get('title') or ''
            first='\n'.join(document[number].get_text() for number in range(min(2,pages)))
    except Exception:
        raise ServiceError('invalid_document','ScienceDirect PDF could not be read') from None
    normalized=lambda value:re.sub(r'[^a-z0-9]+','',value.casefold())
    title_identity=normalized(metadata_title)==normalized(row['title']) or normalized(row['title']) in normalized(first)
    if pages<1 or not title_identity or not expected_doi or normalized(expected_doi) not in normalized(first):
        raise ServiceError('identity_mismatch','ScienceDirect PDF metadata or first pages differ from the selected publication')
    obtained=urlsplit(actual);safe_url=urlunsplit((obtained.scheme,obtained.netloc,obtained.path,'',''))
    artifact=publisher.store.put(data,'application/pdf',publisher.source,safe_url,preserve_bytes=True,role='fulltext',
                                 pii=row['pii'],doi=expected_doi,pages=pages,suggested_filename=filename,
                                 source_control_path=urlsplit(control_url).path)
    return {'status':'available','artifact':artifact,'pii':row['pii'],'doi':expected_doi,'pages':pages,
            'source_control_path':urlsplit(control_url).path}


class ScienceDirect(Publisher):
    def __init__(self, store, gateway):
        super().__init__(store,gateway,next(p for p in PROFILES if p.source=='science-direct'))
        self.known={}

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
            raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
        if cursor:raise ServiceError('invalid_cursor','ScienceDirect uses numeric result offsets')
        if export not in (None,'json','csv','html','native','ris','bibtex','plain'):
            raise ServiceError('invalid_export','Use json, csv, html, native HTML evidence, ris, bibtex or plain')
        page=self.gateway.open(self.source,self.profile.gateway_label,self.profile.hosts,'body')
        origin=urlsplit(page.url);base=urlunsplit((origin.scheme,origin.netloc,'','',''))
        show=25
        selected=[];evidence=[];html_pages=[];citations=[];citation_errors=[];expanded_groups=[]
        exact_publication=options.get('publication_exact')
        if exact_publication and ('publication' in options or 'publication_titles' in options or options.get('field')=='Publication'):
            raise ServiceError('invalid_options','publication_exact cannot be combined with publication text, a Publication primary field or publication-title facets')
        resolved_publication={}
        if exact_publication:
            entry=urlunsplit((origin.scheme,origin.netloc,'/search/entry','',''))
            goto_source(page,entry,self.profile.hosts,wait_until='domcontentloaded',timeout=45000)
            publication=page.locator('#pub');publication.wait_for(state='visible',timeout=30000);page.wait_for_timeout(5000)
            publication=page.locator('#pub');publication.fill(exact_publication);page.wait_for_timeout(1500)
            if publication.input_value()!=exact_publication:
                publication=page.locator('#pub');publication.fill(exact_publication);page.wait_for_timeout(1500)
            candidates=page.locator('[role="option"]:visible, ul.ui-autocomplete:visible li, .autocomplete-suggestions:visible li')
            try:candidates.first.wait_for(state='visible',timeout=10000)
            except Exception:pass
            labels=[];matches=[]
            for index in range(candidates.count()):
                label=' '.join(candidates.nth(index).inner_text().split())
                if label:labels.append(label)
                if label==exact_publication:matches.append(candidates.nth(index))
            if len(matches)!=1:
                raise ServiceError('selection_required','Select one exact publication from current ScienceDirect autocomplete candidates',
                                   status='selection_required',candidates=list(dict.fromkeys(labels)))
            matches[0].click(timeout=10000);page.wait_for_timeout(500)
            with page.expect_navigation(wait_until='domcontentloaded',timeout=45000):
                page.get_by_role('button',name='Submit advanced search',exact=True).click()
            actual=parse_qs(urlsplit(page.url).query,keep_blank_values=True)
            if urlsplit(page.url).path!='/search' or actual.get('pub')!=[exact_publication] or len(actual.get('cid',[]))!=1:
                raise ServiceError('query_mismatch','ScienceDirect autocomplete did not retain the exact publication label and cid')
            resolved_publication={'pub':exact_publication,'cid':actual['cid'][0]}
            raw=page.content()
            evidence.append(self.store.put(clean_html(raw,self.store.sanitizer),'text/html',self.source,page.url,
                                           role='publication_candidate_page',query=query,options=options))
        total=None;offset=(start//show)*show;skip=start-offset;continuation_limited=False
        facets=[];facet_groups={};filter_state={}
        while len(selected)<limit:
            params=search_params(query,options,offset,show)
            params.update(resolved_publication)
            url=urlunsplit((origin.scheme,origin.netloc,'/search',urlencode(params),''))
            response=goto_source(page,url,self.profile.hosts,wait_until='domcontentloaded',timeout=45000)
            validate_search_location(page.url,params)
            try:page.wait_for_function("() => document.querySelector('span.search-body-results-text,li.ResultItem,div.error-zero-results')",timeout=30000)
            except Exception as error:
                raw=page.content()
                if is_access_challenge(raw):
                    raise ServiceError('publisher_access_challenge','ScienceDirect search reached an access challenge',status='restricted') from None
                raise ServiceError('search_interface_not_ready','ScienceDirect did not render native results',error_type=type(error).__name__) from None
            if page.locator('li.ResultItem').count():
                try:page.wait_for_function("() => document.querySelectorAll('input[id^=\"articleTypes-\"],input[id^=\"publicationTitles-\"],input[id^=\"subjectAreas-\"],input[id^=\"languages-\"],input[id^=\"accessTypes-\"]').length > 0",timeout=10000)
                except Exception:pass
            for group in expand_result_facets(page):
                if group not in expanded_groups:expanded_groups.append(group)
            raw=page.content();rows,reported,current,pages=search_page(raw,page.url);facets=facet_candidates(raw);facet_groups=facet_group_state(raw);filter_state=result_filter_state(raw)
            selected_facets={(item['native_group'],item['value']) for item in facets if item['selected']}
            for option,native in FACET_OPTIONS.items():
                if option in options and any((native,value) not in selected_facets for value in options[option]):
                    raise ServiceError('filter_mismatch','ScienceDirect did not retain the requested result facet values')
            if options.get('subscribed_only') and not filter_state['subscribed']:
                raise ServiceError('filter_mismatch','ScienceDirect did not retain the subscribed-journals filter')
            if 'date' in options and '-' in options['date']:
                first,last=options['date'].split('-',1)
                if filter_state.get('year_mode')!='range' or filter_state.get('year_start')!=first or filter_state.get('year_end')!=last:
                    raise ServiceError('filter_mismatch','ScienceDirect did not retain the requested result year range')
            if total is not None and reported!=total:raise ServiceError('range_mismatch','ScienceDirect changed the result total between pages')
            total=reported
            expected=min(show,max(0,total-offset))
            if len(rows)!=expected:
                raise ServiceError('range_mismatch','ScienceDirect rows do not match the requested native result range')
            if rows and current!=offset//show+1:
                raise ServiceError('range_mismatch','ScienceDirect page indicator does not match the requested offset')
            proof=self.store.put(clean_html(raw,self.store.sanitizer),'text/html',self.source,page.url,role='native_search_page',
                                 query=query,options=options,offset=offset,total=total)
            evidence.append(proof)
            for index,row in enumerate(rows):
                self.known[row['pii']]={'row':row,'query':query,'options':dict(options),'page_offset':offset}
            if export in ('html','native'):html_pages.append(proof)
            needed=limit-len(selected);chunk=rows[skip:skip+needed]
            if export in ('ris','bibtex','plain'):
                for index,row in enumerate(chunk,start=skip):
                    try:citations.append(native_search_citation(self,page,row,index,format=export))
                    except ServiceError as error:citation_errors.append({'pii':row['pii'],**error.result})
                    except Exception as error:citation_errors.append({'pii':row['pii'],'status':'error','code':'native_citation_failed','error_type':type(error).__name__})
            selected.extend(chunk);skip=0
            if not rows or offset+len(rows)>=total:break
            if current>=pages:
                continuation_limited=offset+len(rows)<total
                break
            offset+=show
        records=self.store.put(encoded(selected),'application/json',self.source,page.url,role='records',query=query,options=options,start=start,total=total)
        exported=records
        if export in ('html','native'):
            exported={'artifacts':html_pages,'scope':'Visited native HTML pages covering the requested result window'}
        elif export=='csv':
            fields=list(dict.fromkeys(key for row in selected for key in row))
            output=io.StringIO(newline='');writer=csv.DictWriter(output,fieldnames=fields);writer.writeheader();writer.writerows(selected)
            exported=self.store.put(output.getvalue(),'text/csv',self.source,page.url,role='mechanical_export',parent_ref=records['ref'])
        elif export in ('ris','bibtex','plain'):
            exported={'status':'partial' if citation_errors else 'available' if citations else 'error','artifacts':citations,
                      'errors':citation_errors,'scope':'One native '+export+' citation per selected PII in result order'}
        more=start+len(selected)<(total or 0)
        next_value={'start':start+len(selected)} if more and not continuation_limited else None
        status='partial' if citation_errors else 'ok' if selected else 'not_found'
        return {'status':status,'source':self.source,'query':query,'options':options,'start':start,
                'requested':limit,'received':len(selected),'total':total,'has_more':more,
                'next':next_value,'continuation_limited':continuation_limited,'records':records,'export':exported,'evidence':evidence,
                'facets':facets,'facet_groups':facet_groups,'publication_exact':resolved_publication or None,
                'filter_state':filter_state,'expanded_facet_groups':expanded_groups,
                'facet_scope':'Current native candidates after every available Show more facet control was expanded',
                'preview':[{key:row.get(key) for key in ('pii','doi','title','url')} for row in selected[:3]]}

    def citation(self, pii, format='ris', expected_doi=None):
        page = self.gateway.open(self.source,self.profile.gateway_label,self.profile.hosts,'body')
        origin = urlsplit(page.url)
        url = urlunsplit((origin.scheme,origin.netloc,'/sdfe/arp/cite',urlencode({'pii':pii,'format':FORMATS[format],'withabstract':'true'}),''))
        data, media, actual = browser_download(self.gateway.context,url,self.profile.hosts)
        canonical = 'application/x-bibtex' if format=='bibtex' else FORMATS[format]
        if format in ('ris','bibtex'):
            rows = bibliography(data,canonical)
            if len(rows)!=1:
                raise ServiceError('identity_mismatch','ScienceDirect citation is not a single record')
            observed = rows[0].get('doi') if format=='bibtex' else rows[0].get('fields',{}).get('do',[None])[0]
            if expected_doi and (not observed or doi(observed).casefold()!=expected_doi.casefold()):
                raise ServiceError('identity_mismatch','ScienceDirect export identifies another DOI')
        elif not data.strip() or data.lstrip().startswith(b'<'):
            raise ServiceError('unexpected_content','ScienceDirect returned no plain citation')
        elif expected_doi and expected_doi.casefold() not in data.decode('utf-8').casefold():
            raise ServiceError('identity_mismatch','ScienceDirect plain citation does not identify the requested DOI')
        artifact = self.store.put(data,canonical,self.source,actual,role='native_citation',pii=pii,format=format,source_media_type=media)
        return data, artifact

    def fetch(self,target,*,parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Use the documented content parts')
        expected_doi = None
        if re.fullmatch(r'[SB][A-Z0-9]{8,30}',target):
            pii = target
            url='https://www.sciencedirect.com/science/article/pii/'+pii
        elif target.startswith(('http://','https://','10.','doi:')):
            url, expected_doi = self.resolve_target(target)
            pii = pii_from_url(url)
        else:
            candidates=self.search(target,options={'field':'Title'},limit=20)
            return {**candidates,'status':'selection_required' if candidates.get('received') else candidates['status'],
                    'message':'Select the exact ScienceDirect PII, DOI or publisher URL from the preserved candidates'}
        document_parts=[part for part in parts if part!='export']
        source=super().fetch(url,parts=document_parts or ['metadata'])
        components={part:source['components'][part] for part in document_parts}
        native=None
        selection=None
        observed=(source.get('identity') or {}).get('observed_dois') or []
        citation_doi=expected_doi or (observed[0] if len(observed)==1 else None)
        if 'supplementary' in parts:
            try:components['supplementary']=native_supplementary(self,pii,source['source_page'])
            except ServiceError as error:components['supplementary']=error.result
            except Exception as error:components['supplementary']={'status':'error','code':'supplementary_retrieval_failed','error_type':type(error).__name__}
        def exact_result():
            nonlocal selection
            if selection:return selection
            source_rows=json.loads(self.store.read(source['records']['ref'])[1])
            if len(source_rows)!=1:
                raise ServiceError('identity_mismatch','ScienceDirect source page did not identify one publication')
            metadata=source_rows[0].get('metadata') or {}
            if metadata.get('citation_pii',[])!=[pii]:
                raise ServiceError('identity_mismatch','ScienceDirect source page PII differs from the requested publication')
            title=source_rows[0].get('title')
            if not isinstance(title,str) or not title.strip():
                raise ServiceError('identity_mismatch','ScienceDirect source page has no publication title')
            known=self.known.get(pii)
            if not known:
                candidates=self.search('"'+title.replace('"','')+'"',options={'field':'Title'},limit=100)
                all_rows=json.loads(self.store.read(candidates['records']['ref'])[1])
                if sum(row.get('pii')==pii for row in all_rows)!=1:
                    raise ServiceError('selection_required','ScienceDirect title candidates do not contain one exact requested PII',status='unsupported')
                known=self.known.get(pii)
                if not known:
                    raise ServiceError('selection_required','ScienceDirect did not retain the page containing the requested PII',status='unsupported')
            candidates=self.search(known['query'],options=known['options'],start=known['page_offset'],limit=25)
            candidate_rows=json.loads(self.store.read(candidates['records']['ref'])[1])
            matches=[(index,row) for index,row in enumerate(candidate_rows) if row.get('pii')==pii]
            if len(matches)!=1:
                raise ServiceError('selection_required','ScienceDirect candidates do not contain one exact requested PII',status='unsupported')
            index,row=matches[0]
            if title_key(row.get('title'))!=title_key(title):
                raise ServiceError('identity_mismatch','ScienceDirect exact PII candidate has another title')
            page=self.gateway.pages.get(self.source)
            selection=(page,row,index)
            return selection
        if 'export' in parts:
            try:
                page,row,index=exact_result()
                artifacts=[];errors=[]
                for format in ('ris','bibtex','plain'):
                    try:
                        artifact=native_search_citation(self,page,row,index,format=format,expected_doi=citation_doi)
                        artifacts.append({'format':format,'artifact':artifact['artifact']})
                        if format=='ris':native=artifact['artifact']
                    except ServiceError as error:errors.append({'format':format,**error.result})
                    except Exception as error:errors.append({'format':format,'status':'error','code':'native_citation_failed','error_type':type(error).__name__})
                components['export']={'status':'partial' if errors and artifacts else 'error' if errors else 'available',
                                      'artifacts':artifacts,'errors':errors,'scope':'Current source-page PII matched to one native title-search result'}
                if native:components['export']['artifact']=native
            except ServiceError as error:
                components['export']=error.result
            except Exception as error:
                components['export']={'status':'error','code':'citation_export_failed','error_type':type(error).__name__}
        if 'fulltext' in parts and components['fulltext']['status']!='available':
            try:
                page,row,index=exact_result()
                components['fulltext']=native_result_pdf(self,page,row,index,citation_doi)
            except ServiceError as error:components['fulltext']=error.result
            except Exception as error:components['fulltext']={'status':'error','code':'fulltext_retrieval_failed','error_type':type(error).__name__}
        status='ok' if all(component['status']=='available' for component in components.values()) else 'partial'
        result={**source,'status':status,'source':self.source,'target':target,'pii':pii,'components':components}
        if native:result['native_citation']=native
        return result
