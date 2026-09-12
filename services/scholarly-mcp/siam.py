"""SIAM native search and citation export."""
import csv
import io
import json
import re
import unicodedata
import time
from urllib.parse import parse_qs,unquote,urlencode,urljoin,urlsplit

from bs4 import BeautifulSoup

from api_adapters import doi
from browser_adapters import clean_html,goto_source,is_access_challenge
from publishers import Publisher
from scholarly import ServiceError,bibliography,encoded


FIELDS={'Anywhere':'AllField','Title':'Title','Author':'Contrib','Keywords':'Keyword','Abstract':'Abstract','Affiliation':'Affiliation'}
SORTS={'relevance':None,'date':'EpubDate','most_read':'downloaded','most_cited':'cited','title':'TitleSort'}
CONTENT_TYPES={'article':'103','chapter':'109','book':'105'}
SEARCH_READY_TIMEOUT=75000
NATIVE_FORMATS={'bibtex':'application/x-bibtex','ris':'application/x-research-info-systems',
                'endnote':'application/x-endnote-refer','medlars':'text/plain',
                'refworks':'application/x-research-info-systems'}


def search_params(query,options):
    allowed={'field','terms','topic','publication','published_within','published_after','published_before','content_type','sort','page_size'}
    if not isinstance(options,dict) or set(options)-allowed:
        raise ServiceError('invalid_options','Use one documented SIAM field and its exposed filters; Boolean rows are not confirmed')
    field=options.get('field','Anywhere');sort=options.get('sort','relevance');size=options.get('page_size',20)
    if field not in FIELDS or sort not in SORTS or size not in (20,50,100):
        raise ServiceError('invalid_options','Use a documented SIAM field, sort order and page size')
    if 'field' in options:
        params={'field1':FIELDS[field],'text1':query,'ConceptID':['',''],'publication':'','Ppub':'','pageSize':size}
    else:
        params={'AllField':query,'pageSize':size}
    terms=options.get('terms',[])
    if not isinstance(terms,list):
        raise ServiceError('invalid_options','Additional SIAM search fields must be an array')
    for index,term in enumerate(terms,2):
        if not isinstance(term,dict) or set(term)!={'field','query'} or term['field'] not in FIELDS or not isinstance(term['query'],str) or not term['query'].strip():
            raise ServiceError('invalid_options','Each additional SIAM term requires a documented field and non-empty query')
        params['field'+str(index)]=FIELDS[term['field']];params['text'+str(index)]=term['query']
    for option in ('topic','publication'):
        if option in options and (not isinstance(options[option],str) or not options[option].strip()):
            raise ServiceError('invalid_options','Topic and publication require an exact non-empty visible label')
    within=options.get('published_within')
    after=options.get('published_after');before=options.get('published_before')
    if within is not None:
        if within not in ('month','six_months','year') or after is not None or before is not None:
            raise ServiceError('invalid_options','Use one native relative period or one complete custom date range')
    if (after is None)!=(before is None):
        raise ServiceError('invalid_options','Custom publication dates require both after and before')
    if after is not None:
        for value in (after,before):
            if not isinstance(value,dict) or set(value)!={'year','month'} or type(value['year']) is not int or type(value['month']) is not int or not 1<=value['year']<=9999 or not 1<=value['month']<=12:
                raise ServiceError('invalid_options','Custom publication bounds require integer year and month')
        if (after['year'],after['month'])>(before['year'],before['month']):
            raise ServiceError('invalid_options','The custom publication range start must not follow its end')
        params.update({'AfterYear':after['year'],'AfterMonth':after['month'],'BeforeYear':before['year'],'BeforeMonth':before['month']})
    if 'content_type' in options:
        if options['content_type'] not in CONTENT_TYPES:
            raise ServiceError('invalid_options','Use content_type article, chapter or book')
        params['PubType']=CONTENT_TYPES[options['content_type']]
    if SORTS[sort]:params['sortBy']=SORTS[sort]
    return params


def records(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    heading=soup.select_one('div.pull-left.search__result.search__result--space')
    match=re.search(r'Results:\s*([\d,]+)\s*[-–]\s*([\d,]+)\s+of\s+([\d,]+)',heading.get_text(' ',strip=True) if heading else '',re.I)
    if not match:
        raise ServiceError('invalid_response','SIAM returned no recognized result range')
    first,last,total=[int(value.replace(',','')) for value in match.groups()]
    rows=[]
    for item in soup.select('li.search-item'):
        title=item.select_one('.search-item__title a[href]')
        selected=item.select_one('input[name=doi][value]')
        if title is None or selected is None:
            raise ServiceError('invalid_response','SIAM result is missing its title or DOI selection control')
        url=urljoin(base,title['href'])
        identity=re.search(r'/doi/(?:book/|abs/|full/|pdf/|epdf/)?(10\..+)',unquote(urlsplit(url).path))
        identifier=doi(selected['value'])
        if not identity or doi(identity.group(1)).lower()!=identifier.lower():
            raise ServiceError('identity_mismatch','SIAM result title and DOI selection control identify different publications')
        date=item.select_one('div.meta__date')
        year=re.search(r'\b(\d{4})\b',date.get_text(' ',strip=True) if date else '')
        abstract=item.select_one('span.hlFld-Abstract')
        publication=item.select_one('a.meta__serial[href]')
        parent_path=urlsplit(urljoin(base,publication['href'])).path if publication else ''
        kind='book' if urlsplit(url).path.startswith('/doi/book/') else 'chapter' if parent_path.startswith('/doi/book/') else 'article' if parent_path.startswith('/journal/') else None
        rows.append({'id':identifier,'doi':identifier,'title':title.get_text(' ',strip=True),'url':url,
                     'authors':[node.get_text(' ',strip=True) for node in item.select('ul.meta__authors span.hlFld-ContribAuthor')],
                     'year':int(year.group(1)) if year else None,
                     'abstract':abstract.get_text(' ',strip=True) if abstract else None,'type':kind,
                     'publication':publication.get_text(' ',strip=True) if publication else None,
                     'publication_url':urljoin(base,publication['href']) if publication else None,
                     'listing':item.get_text('\n',strip=True)})
    expected=max(0,min(last,total)-first+1) if total else 0
    if len(rows)!=expected:
        raise ServiceError('range_mismatch','SIAM result rows do not match the displayed range')
    return rows,total,max(0,first-1)


def next_page(raw,base,params,number):
    link=BeautifulSoup(raw,'html.parser').select_one('a.pagination__btn--next[href]')
    if link is None:
        return None
    url=urljoin(base,link['href']);parts=urlsplit(url)
    if parts.hostname!=urlsplit(base).hostname or parts.path!='/action/doSearch':
        raise ServiceError('source_boundary','SIAM next-page control leaves the search source')
    observed=parse_qs(parts.query,keep_blank_values=True)
    expected={key:[str(item) for item in value] if isinstance(value,list) else [str(value)] for key,value in params.items() if key!='startPage'}
    if observed.get('startPage')!=[str(number+1)] or any(observed.get(key)!=value for key,value in expected.items()):
        raise ServiceError('query_mismatch','SIAM next-page control changed or dropped search fields')
    return url


def citation_identities(data,format):
    if format=='medlars':
        records=[]
        for block in re.split(r'(?:\r?\n)[ \t]*(?:\r?\n)+',data.decode('utf-8-sig').strip()):
            fields={}
            for line in block.splitlines():
                match=re.match(r'^([A-Z0-9]{2,4})[ \t]+-[ \t]?(.*)$',line)
                if match:fields.setdefault(match.group(1),[]).append(match.group(2))
            if fields:records.append(fields)
        identifiers=[];titles=[]
        for fields in records:
            identifiers.extend(match.group(1) for value in fields.get('AID',[]) if (match:=re.fullmatch(r'(.+?)[ \t]+\[doi\][ \t]*',value,re.I)))
            title=next((value for value in fields.get('TI',[]) if value.strip()),None)
            if title is None and any('book' in value.casefold() for value in fields.get('PT',[])):
                title=next((value for value in fields.get('TA',[]) if value.strip()),None)
            if title is not None:titles.append(title)
        return identifiers,titles
    rows=bibliography(data,NATIVE_FORMATS[format])
    if format=='endnote':
        return ([row.get('fields',{}).get('R',[None])[0] for row in rows],
                [row.get('fields',{}).get('T',[None])[0] for row in rows])
    return ([row.get('doi') or row.get('fields',{}).get('do',[None])[0] for row in rows],
            [row.get('title') or row.get('fields',{}).get('ti',[None])[0] for row in rows])


def normalized_title(value):
    text=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',value or '')).strip()
    return re.sub(r'\s+([,.;:!?])',r'\1',text).casefold()


def refworks_payload(raw):
    soup=BeautifulSoup(raw,'html.parser');matches=[]
    for form in soup.select('form[method][action]'):
        target=urlsplit(form['action'])
        if form.get('method','').lower()!='post' or target.hostname!='api.refworks.proquest.com' or target.path!='/api-ipa/express':
            continue
        if set(parse_qs(target.query,keep_blank_values=True))!={'encoding','filter','vendor'}:
            continue
        field=form.select_one('textarea[name=ImportData]')
        if field is not None:matches.append(field.get_text())
    if len(matches)!=1 or not matches[0].strip():
        raise ServiceError('invalid_response','SIAM RefWorks response has no unique citation payload')
    return matches[0].encode('utf-8')


def _exact_suggestion(page,field,label):
    field.fill(label)
    nodes=page.locator('[role="option"]:visible, ul.ui-autocomplete:visible li, .autocomplete-suggestions:visible li')
    deadline=time.monotonic()+5
    while not nodes.count() and time.monotonic()<deadline:page.wait_for_timeout(250)
    candidates=[];matches=[]
    for index in range(nodes.count()):
        node=nodes.nth(index);text=re.sub(r'\s+',' ',node.inner_text()).strip()
        if not text:continue
        identifier=node.get_attribute('data-value') or node.get_attribute('value') or node.get_attribute('data-id')
        candidate={'label':text,'id':identifier}
        if candidate not in candidates:candidates.append(candidate)
        if text.casefold()==label.casefold():matches.append(node)
    if len(matches)!=1:
        raise ServiceError('filter_selection_required','Select one exact current SIAM autocomplete value',status='selection_required',
                           field=field.get_attribute('name'),candidates=candidates)
    matches[0].click();page.wait_for_timeout(500)


def configure_advanced(publisher,page,query,options):
    goto_source(page,'https://'+publisher.profile.domains[0]+'/search/advanced',publisher.profile.hosts,wait_until='domcontentloaded',timeout=45000)
    form=page.locator('form#frmSearch').first
    form.wait_for(state='visible',timeout=30000)
    primary=options.get('field','Anywhere')
    form.locator('select[name=field1]').select_option(FIELDS[primary]);form.locator('input[name=text1]').fill(query)
    expected={'field1':[FIELDS[primary]],'text1':[query]}
    for index,term in enumerate(options.get('terms',[]),2):
        form.get_by_role('button',name='Add search field').click()
        form.locator('select[name=field'+str(index)+']').select_option(FIELDS[term['field']])
        form.locator('input[name=text'+str(index)+']').fill(term['query'])
        expected['field'+str(index)]=[FIELDS[term['field']]];expected['text'+str(index)]=[term['query']]
    for option,native in [('topic','ConceptID'),('publication','publication')]:
        if option in options:
            _exact_suggestion(page,form.locator('input[name='+native+']').filter(visible=True).first,options[option])
            selected=form.locator('input[name="'+native+'[]"]')
            values=[selected.nth(index).input_value() for index in range(selected.count())]
            if len(values)!=1 or not values[0]:
                raise ServiceError('filter_selection_required','SIAM did not retain one selected autocomplete value',status='selection_required',field=option)
            expected[native+'[]']=values
    if 'published_within' in options:
        form.locator('#staticRange').focus();form.locator('#staticRange').press('Space')
        labels={'month':'Month','six_months':'6 Months','year':'Year'}
        relative=form.locator('select[name=Ppub]');relative.select_option(label=labels[options['published_within']])
        expected['Ppub']=['',relative.input_value()]
    elif 'published_after' in options:
        form.locator('#customRange').focus();form.locator('#customRange').press('Space')
        after=options['published_after'];before=options['published_before']
        for name,value in [('AfterMonth',after['month']),('AfterYear',after['year']),('BeforeMonth',before['month']),('BeforeYear',before['year'])]:
            control=form.locator('select[name='+name+']')
            if control.locator('option[value="'+str(value)+'"]').count()!=1:
                raise ServiceError('invalid_options','The requested date is absent from current SIAM controls',field=name,value=value)
            control.select_option(str(value))
            expected[name]=[str(value)]
    button=form.locator('#advanced-search-btn');button.click(timeout=15000);page.wait_for_timeout(10000)
    observed=parse_qs(urlsplit(page.url).query,keep_blank_values=True)
    if any(observed.get(key)!=value for key,value in expected.items()):
        raise ServiceError('query_mismatch','SIAM advanced search changed a submitted field or date')
    for option,native in [('topic','ConceptID[]'),('publication','publication[]')]:
        if option in options and len([value for value in observed.get(native,[]) if value])!=1:
            raise ServiceError('query_mismatch','SIAM autocomplete selection did not produce one native filter',field=option)
        if option not in options and any(observed.get(native,[])):
            raise ServiceError('query_mismatch','SIAM retained an unrequested autocomplete filter',field=option)
    if 'published_within' not in options and 'published_after' not in options and any(observed.get('Ppub',[])):
        raise ServiceError('query_mismatch','SIAM retained an unrequested publication period')
    allowed=set(expected)|{'ConceptID','publication','Ppub','ConceptID[]','publication[]','pageSize','sortBy','startPage','PubType'}
    unexpected=sorted(key for key,values in observed.items() if key not in allowed and any(values))
    if unexpected:
        raise ServiceError('query_mismatch','SIAM advanced search retained unexpected non-empty fields',fields=unexpected)
    return observed


def citation(publisher,page,identifiers,base,format='bibtex',titles=None):
    if format not in NATIVE_FORMATS:
        raise ServiceError('invalid_export','Use BibTeX, RIS, EndNote, Medlars or the RefWorks import payload')
    identifiers=[doi(value) for value in identifiers]
    boxes=page.locator('input[name=doi]')
    controls={}
    for index in range(boxes.count()):
        box=boxes.nth(index)
        value=doi(box.input_value())
        if value in controls:
            raise ServiceError('identity_mismatch','SIAM returned duplicate DOI selection controls')
        controls[value]=box
    if any(value not in controls for value in identifiers):
        raise ServiceError('identity_mismatch','SIAM result controls do not contain every requested DOI')
    requested=set(identifiers)
    for identifier,box in controls.items():
        expected=identifier in requested
        if box.is_checked()!=expected:
            box.focus();box.press('Space')
        if box.is_checked()!=expected:
            raise ServiceError('selection_failed','SIAM did not create the exact requested publication selection')
    actions=page.locator('select[name=bulkActions]').first
    if not hasattr(publisher.gateway,'native_download'):
        raise ServiceError('native_browser_required','SIAM citation export requires the native Chrome download gateway',status='restricted')
    if format=='bibtex':
        action=lambda:actions.select_option(label='Download BibTeX')
    else:
        actions.select_option(label='Export Citations')
        radio=page.locator('input[name=format][value='+format+']')
        radio.wait_for(state='visible',timeout=30000);radio.check()
        buttons=page.get_by_role('button',name=re.compile(r'download|export|save',re.I))
        button=None
        for index in range(buttons.count()):
            candidate=buttons.nth(index)
            if candidate.is_visible():button=candidate;break
        if button is None:
            raise ServiceError('download_control_missing','SIAM citation modal has no visible download control')
        action=lambda:button.click()
    media=NATIVE_FORMATS[format]
    extra={}
    if format=='refworks':
        with page.expect_response(lambda response:urlsplit(response.url).hostname in publisher.profile.hosts and
                                  urlsplit(response.url).path=='/action/downloadCitation',timeout=45000) as pending:
            action()
        response=pending.value;actual=response.url
        if response.status!=200:
            raise ServiceError('citation_export_failed','SIAM RefWorks wrapper returned an unsuccessful response',http_status=response.status)
        data=refworks_payload(response.body());filename=''
        extra={'transport':'refworks_import_wrapper','provider_format':'RIS Format','decoded_textarea':True}
    else:
        data,filename,actual=publisher.gateway.native_download(
            page,action,publisher.profile.hosts,'/action/downloadCitation')
    artifact=publisher.store.put(data,media,publisher.source,actual,role='native_citation_payload' if format=='refworks' else 'native_citations',
                                 requested_dois=identifiers,request_method='POST',suggested_filename=filename,**extra)
    found,found_titles=citation_identities(data,format)
    if [doi(str(value)).lower() for value in found]!=[value.lower() for value in identifiers]:
        raise ServiceError('identity_mismatch','Native SIAM citations do not match the selected publication DOIs',evidence=artifact)
    if titles is not None and [normalized_title(value) for value in found_titles]!=[normalized_title(value) for value in titles]:
        raise ServiceError('identity_mismatch','Native SIAM citation titles do not match the selected publications',evidence=artifact)
    return artifact


def search(publisher,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    if cursor:
        raise ServiceError('invalid_options','SIAM uses start and limit rather than cursors')
    if export not in (None,'json','html','csv',*NATIVE_FORMATS):
        raise ServiceError('invalid_export','Use json, html, csv, BibTeX, RIS, EndNote or Medlars')
    params=search_params(query,options)
    size=params['pageSize']
    profile=publisher.profile
    page=publisher.gateway.public_page(publisher.source)
    base='https://'+(urlsplit(page.url).hostname or profile.domains[0])
    dynamic=bool(set(options)&{'terms','topic','publication','published_within','published_after','published_before'})
    if dynamic:
        params=configure_advanced(publisher,page,query,options)
        params['pageSize']=[str(size)]
        if 'content_type' in options:params['PubType']=[CONTENT_TYPES[options['content_type']]]
        if SORTS[options.get('sort','relevance')]:params['sortBy']=[SORTS[options['sort']]]
    rows,evidence,citations,failures,total,actual=[],[],[],[],None,None
    first_page=start//size;last_page=(start+limit-1)//size
    following=None
    for number in range(first_page,last_page+1):
        params['startPage']=number
        requested=following or base+'/action/doSearch?'+urlencode(params,doseq=True)
        response=goto_source(page,requested,profile.hosts,wait_until='domcontentloaded',timeout=45000)
        if response is not None and response.status>=400:
            raise ServiceError('provider_error','SIAM rejected the requested native search expression',http_status=response.status)
        try:
            page.wait_for_function("() => document.querySelector('li.search-item,.search-result__no-result') || /Results:\\s*0\\b|No results/i.test(document.body.innerText)",timeout=SEARCH_READY_TIMEOUT)
        except Exception as error:
            if is_access_challenge(page.content()):
                raise ServiceError('publisher_access_challenge','SIAM displayed an access verification page',status='restricted') from None
            raise ServiceError('search_response_not_received','SIAM did not provide a native search response',error_type=type(error).__name__,http_status=response.status if response else None) from None
        actual=page.url
        observed=parse_qs(urlsplit(actual).query,keep_blank_values=True)
        expected={key:[str(item) for item in value] if isinstance(value,list) else [str(value)] for key,value in params.items()}
        if any(observed.get(key)!=value for key,value in expected.items()):
            raise ServiceError('query_mismatch','SIAM returned a different query or page')
        source_raw=page.content()
        native,found,first=records(source_raw,base)
        raw=clean_html(source_raw,publisher.store.sanitizer)
        evidence.append(publisher.store.put(raw,'text/html',publisher.source,actual,role='search_page',query=query,options=options,page=number,
                                            http_status=response.status if response else None))
        if found and first!=number*size or total is not None and total!=found:
            raise ServiceError('range_mismatch','SIAM returned a changed result range',evidence=evidence)
        total=found
        selected=[row for index,row in enumerate(native,first) if start<=index<start+limit]
        rows.extend(selected)
        if export in NATIVE_FORMATS and selected:
            try:
                citations.append(citation(publisher,page,[row['doi'] for row in selected],base,export,titles=[row['title'] for row in selected]))
            except ServiceError as error:
                failures.append(error.result)
            except Exception as error:
                failures.append({'status':'error','code':'citation_export_failed','error_type':type(error).__name__})
        if (number+1)*size>=total:
            break
        if number==last_page:
            continue
        following=next_page(source_raw,base,params,number)
        if following is None:
            raise ServiceError('range_mismatch','SIAM result page has more records but no native next-page control')
    artifact=publisher.store.put(encoded(rows),'application/json',publisher.source,actual,role='records',query=query,options=options,start=start,requested=limit,total=total)
    exported=artifact
    if export=='html':
        exported={'artifacts':evidence}
    elif export=='csv':
        stream=io.StringIO(newline='')
        writer=csv.DictWriter(stream,fieldnames=['id','doi','title','url','authors','year','abstract','type','publication','publication_url','listing'])
        writer.writeheader()
        for row in rows:writer.writerow({**row,'authors':'; '.join(row['authors'])})
        exported=publisher.store.put(stream.getvalue(),'text/csv',publisher.source,actual,role='mechanical_export',parent_ref=artifact['ref'])
    elif export in NATIVE_FORMATS:
        exported={'status':'partial' if failures else 'available','artifacts':citations,'failures':failures}
    more=start+len(rows)<total
    return {'status':'partial' if failures else 'ok' if rows else 'not_found','source':publisher.source,'query':query,'options':options,'start':start,'requested':limit,
            'received':len(rows),'total':total,'has_more':more,'next':{'start':start+len(rows)} if more else None,
            'records':artifact,'export':exported,'evidence':evidence,'preview':[{k:row[k] for k in ('doi','title')} for row in rows[:3]]}


class SIAM(Publisher):
    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)

    def fetch(self,target,*,parts):
        result=super().fetch(target,parts=parts)
        component=result.get('components',{}).get('export')
        if 'export' not in parts or component is None or component.get('format')=='pdf':
            return result
        try:
            document_rows=json.loads(self.store.read(result['records']['ref'])[1])
            identifiers=[row.get('doi') for row in document_rows if row.get('doi')]
            if len(identifiers)!=1:
                raise ServiceError('citation_not_identified','SIAM native citation requires one DOI identified by the document page',status='not_implemented')
            identifier=doi(identifiers[0])
            artifacts=[];errors=[]
            for format in NATIVE_FORMATS:
                try:
                    candidates=self.search(identifier,options={},start=0,limit=20)
                    rows=json.loads(self.store.read(candidates['records']['ref'])[1])
                    matches=[row for row in rows if row['doi'].lower()==identifier.lower()]
                    if len(matches)!=1:
                        raise ServiceError('citation_not_found','SIAM search did not return the exact document DOI',status='not_found')
                    page=self.gateway.pages.get(self.source)
                    if page is None or page.is_closed():
                        raise ServiceError('citation_page_closed','SIAM citation search page is unavailable',status='error')
                    base='https://'+(urlsplit(str(page.url)).hostname or self.profile.domains[0])
                    artifacts.append({'format':format,'artifact':citation(self,page,[identifier],base,format,titles=[matches[0]['title']])})
                except ServiceError as error:errors.append({'format':format,**error.result})
                except Exception as error:errors.append({'format':format,'status':'error','code':'citation_export_failed','error_type':type(error).__name__})
            result['components']['export']={'status':'partial' if errors else 'available','artifacts':artifacts,'errors':errors}
            if artifacts:result['components']['export']['artifact']=artifacts[0]['artifact']
        except ServiceError as error:
            result['components']['export']=error.result
        result['status']='ok' if all(item['status']=='available' for item in result['components'].values()) else 'partial'
        return result
