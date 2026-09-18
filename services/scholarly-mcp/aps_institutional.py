"""APS native search pages, query clauses, exact windows, citations and files."""
import csv,io,json,mimetypes,re
from datetime import date
from urllib.parse import parse_qs,urljoin,urlsplit,urlunsplit,urlencode,unquote
from bs4 import BeautifulSoup
from browser_adapters import browser_download,clean_html,goto_source,is_access_challenge
from api_adapters import doi
from publishers import Publisher
from scholarly import Sanitizer, ServiceError, bibliography, encoded, failure_details
from waits import SOURCE_WAIT_MS

FIELDS={'all','author','abstract','abstitle','title','refauth','affiliation','collaboration'}
FILTERS={'journal','article_type','category','physh_concept','physh_discipline'}
NATIVE_FORMATS={'bibtex':'application/x-bibtex','ris':'application/x-research-info-systems'}


def query_params(query,options):
    allowed={'field','terms','sort','date','start_date','end_date'}|FILTERS
    if not isinstance(options,dict) or set(options)-allowed:
        raise ServiceError('invalid_options','Use documented APS search fields, clauses, facets and dates')
    field=options.get('field','all');sort=options.get('sort','relevance')
    if not isinstance(field,str) or field not in FIELDS or sort not in ('relevance','recent','oldest','most_cited') or not isinstance(query,str) or not query.strip():
        raise ServiceError('invalid_options','Use a documented field, sort and nonempty query')
    clauses=[{'field':field,'value':query,'operator':'AND'}]
    terms=options.get('terms',[])
    if not isinstance(terms,list):raise ServiceError('invalid_options','terms must be a list of field/query/operator objects')
    for term in terms:
        if not isinstance(term,dict) or set(term)!={'field','query','operator'} or not isinstance(term['field'],str) or term['field'] not in FIELDS or term['operator'] not in ('AND','OR','NOT') or not isinstance(term['query'],str) or not term['query'].strip():
            raise ServiceError('invalid_options','Each additional APS term needs a documented field, nonempty query and AND/OR/NOT operator')
        clauses.append({'field':term['field'],'value':term['query'],'operator':term['operator']})
    params={'clauses':json.dumps(clauses,separators=(',',':')),'sort':sort}
    for key in FILTERS&set(options):
        values=options[key] if isinstance(options[key],list) else [options[key]]
        if not values or any(not isinstance(value,str) or not value.strip() for value in values) or len(values)!=len(set(values)):
            raise ServiceError('invalid_options','Each facet accepts one or more distinct nonempty native values',field=key)
        params[key+'[]' if isinstance(options[key],list) else key]=values if isinstance(options[key],list) else values[0]
    start_date,end_date=options.get('start_date'),options.get('end_date')
    if start_date is not None or end_date is not None:
        if options.get('date') not in (None,'custom') or not isinstance(start_date,str) or not isinstance(end_date,str):
            raise ServiceError('invalid_options','Custom APS dates require start_date and end_date without a relative date')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',start_date) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',end_date):
            raise ServiceError('invalid_options','APS custom dates use YYYY-MM-DD')
        try:after,before=date.fromisoformat(start_date),date.fromisoformat(end_date)
        except ValueError:raise ServiceError('invalid_options','APS custom dates use YYYY-MM-DD') from None
        if after>before:raise ServiceError('invalid_options','APS start_date must not follow end_date')
        params.update(date='custom',start_date=start_date,end_date=end_date)
    elif 'date' in options:
        if options['date'] not in ('week','month','year'):
            raise ServiceError('invalid_options','date supports week, month or year; custom uses start_date and end_date')
        params['date']=options['date']
    return clauses,params


def search_records(raw,base,*,expected_clauses=None,per_page=20):
    if is_access_challenge(raw):raise ServiceError('publisher_access_challenge','APS returned an access verification page',status='restricted')
    soup=BeautifulSoup(raw,'html.parser');main=soup.select_one('#search-main')
    if main is None:raise ServiceError('invalid_response','APS returned no native search results region')
    try:
        total=int(main['data-search-analytics-results-count-value']);clauses=json.loads(main['data-search-clauses'])
    except (KeyError,ValueError,TypeError):raise ServiceError('invalid_response','APS returned no valid search count and clauses') from None
    if total<0:raise ServiceError('invalid_response','APS returned a negative result count')
    if expected_clauses is not None and clauses!=expected_clauses:
        raise ServiceError('query_mismatch','APS did not retain the requested search fields, operators and values')
    current=main.select_one('a[aria-current=page]')
    try:number=int(parse_qs(urlsplit(current['href']).query).get('page',['1'])[0]) if current else 1
    except (ValueError,KeyError):raise ServiceError('invalid_response','APS returned no valid current page') from None
    first=(number-1)*per_page;rows=[];seen=set()
    for anchor in main.select('h3 > a[href]'):
        card=anchor.find_parent('div',class_='border-b');url=urljoin(base,anchor['href'])
        if card is None or url in seen:raise ServiceError('invalid_response','APS result cards are missing or repeated')
        seen.add(url);match=re.search(r'/(10\.\d{4,9}/[^?#\s]+)',unquote(urlsplit(url).path))
        identifier=match[1] if match else None;abstract=card.select_one('.abstract-summary')
        paragraphs=anchor.parent.parent.find_all('p');authors=citation=published=None
        if len(paragraphs)>=2 and 'Published' in paragraphs[1].get_text():
            authors=paragraphs[0].get_text(' ',strip=True)
            spans=paragraphs[1].find_all('span',recursive=False)
            if len(spans)==2:
                citation=spans[0].get_text(' ',strip=True)
                published=re.sub(r'^\s*-\s*Published\s*','',spans[1].get_text(' ',strip=True))
        rows.append({'id':identifier or url,'doi':identifier,'title':anchor.get_text(' ',strip=True),'url':url,
            'authors_display':authors,'citation_display':citation,'publication_date_display':published,
            'listing':card.get_text(' ',strip=True),'html':clean_html(str(card),Sanitizer()),
            'abstract':abstract.get_text(' ',strip=True) if abstract else None,
            'abstract_html':clean_html(str(abstract),Sanitizer()) if abstract else None})
    if len(rows)!=min(per_page,max(0,total-first)):
        raise ServiceError('range_mismatch','APS result cards differ from the declared count and page',received=len(rows),total=total,start=first)
    next_page=main.select_one('a[aria-label="Next page"]')
    facets={}
    for control in soup.select('input[type=checkbox][name][value]'):
        name=control['name'].removesuffix('[]')
        if name not in FILTERS:continue
        value=control['value'];label=control.find_parent('label') or control.parent
        selected=control.has_attr('checked')
        facets.setdefault(name,{})[value]={'value':value,'label':label.get_text(' ',strip=True),'selected':selected,
                                          'selected_basis':'source_response' if selected else None}
    return {'rows':rows,'total':total,'start':first,'page':number,'clauses':clauses,
            'sort':main.get('data-search-analytics-sort-value'),'next_url':urljoin(base,next_page['href']) if next_page else None,
            'facets':{key:list(values.values()) for key,values in facets.items()}}


def supplement_links(raw,base,identifier,hosts):
    identifier=doi(identifier);page=urlsplit(base);segments=page.path.strip('/').split('/')
    if len(segments)<3 or segments[1]!='abstract':return []
    prefix=f'/{segments[0]}/supplemental/{identifier}/'.casefold();result=[];seen={}
    for anchor in BeautifulSoup(raw,'html.parser').select('a[href]'):
        url=urljoin(base,anchor['href']);parts=urlsplit(url)
        if parts.hostname not in hosts or not unquote(parts.path).casefold().startswith(prefix):continue
        label=anchor.get_text(' ',strip=True)
        if url in seen:
            if label and not result[seen[url]]['label']:result[seen[url]]['label']=label
            continue
        seen[url]=len(result);result.append({'url':url,'label':label})
    return result


def search(adapter,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    if cursor:
        raise ServiceError('invalid_options','APS uses start and limit rather than cursors')
    if export not in (None,'json','csv','html','native'):
        raise ServiceError('export_not_implemented','APS search currently supports json, csv and native HTML; citation files are not connected',status='not_implemented')
    clauses,params=query_params(query,options);field=options.get('field','all');sort=options.get('sort','relevance');terms=options.get('terms',[])
    simple=field=='all' and not terms and set(params)=={'clauses','sort'} and sort=='relevance'
    target='https://journals.aps.org/'+('search?'+urlencode({'q':query}) if simple else 'search/results?'+urlencode(params,doseq=True))
    adapter.gateway.start();responses=[];page=None
    def capture(response):
        location=urlsplit(response.url)
        if location.hostname in adapter.profile.hosts and location.path in ('/search','/search/results') and response.status==200 and 'html' in response.headers.get('content-type',''):
            responses.append(response)
    adapter.gateway.context.on('response',capture)
    selected=[];proofs=[];errors=[];total=None;facets=None;expected_page=1
    try:
        cached=adapter.gateway.pages.get(adapter.source)
        previous=getattr(adapter,'_aps_last',None);replay=None
        reusable=cached is not None and not cached.is_closed() and urlsplit(cached.url).hostname in ('journals.aps.org','journals-aps-org.libproxy.knu.ac.kr')
        if reusable and start>0 and previous and previous['params']==params and previous['start']<=start:
            page=cached;replay=previous;expected_page=previous['start']//20+1
        elif reusable:
            page=cached;origin=urlsplit(page.url);requested=urlsplit(target)
            target=urlunsplit((origin.scheme,origin.netloc,requested.path,requested.query,''))
            goto_source(page,target,adapter.profile.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        else:
            page=adapter.document(target)
            adapter.gateway.pages[adapter.source]=page
            if cached is not None and cached!=page and not cached.is_closed():cached.close()
        while True:
            try:
                old_proof=old_facets=None
                if replay:
                    raw,response_url,old_proof,old_facets=replay['raw'],replay['url'],replay['proof'],replay['facets'];replay=None
                else:
                    try:page.wait_for_function("number => { if(document.querySelector('#challenge-error-text,#capInput')) return true; const main=document.querySelector('#search-main'); const current=main?.querySelector('[aria-current=page]'); return main && (current ? Number(new URL(current.href).searchParams.get('page')||1)===number : number===1); }",arg=expected_page,timeout=SOURCE_WAIT_MS)
                    except Exception:
                        if is_access_challenge(page.content()):raise ServiceError('publisher_access_challenge','APS returned an access verification page',status='restricted') from None
                        raise ServiceError('search_response_not_received','APS did not initialize its requested search page') from None
                    if is_access_challenge(page.content()):raise ServiceError('publisher_access_challenge','APS returned an access verification page',status='restricted')
                    # Preserve server HTML before MathJax replaces hidden formulas with lazy placeholders.
                    raw=response_url=None
                    for candidate in reversed(responses):
                        body=candidate.text()
                        if BeautifulSoup(body,'html.parser').select_one('#search-main'):
                            raw=body;response_url=candidate.url;break
                    if raw is None:raise ServiceError('native_response_missing','APS rendered results but their original HTML response was not captured')
                found=search_records(raw,response_url,expected_clauses=clauses)
                if found['sort']!=sort:raise ServiceError('filter_mismatch','APS returned a different sort order')
                for key in FILTERS&set(options):
                    requested=options[key] if isinstance(options[key],list) else [options[key]]
                    selected_values={item['value'] for item in found['facets'].get(key,[]) if item['selected']}
                    if any(value not in selected_values for value in requested):
                        try:
                            controls=page.locator(f'input[name="{key}"]:checked,input[name="{key}[]"]:checked')
                            selected_values.update(controls.nth(index).input_value() for index in range(controls.count()))
                        except Exception:
                            pass
                    if any(value not in selected_values for value in requested):
                        raise ServiceError('filter_mismatch','APS did not retain a requested facet',field=key,
                                           requested_values=requested,selected_values=sorted(selected_values))
                    for item in found['facets'].get(key,[]):
                        if item['value'] in selected_values and not item['selected']:
                            item['selected']=True;item['selected_basis']='rendered_dom'
                if 'date' in params:
                    state=BeautifulSoup(raw,'html.parser');choice=state.select_one('#desktop-date-select option[selected]')
                    if choice is None or choice.get('value')!=params['date']:
                        raise ServiceError('filter_mismatch','APS did not retain the requested date interval')
                    if params['date']=='custom':
                        start_control=state.select_one('#desktop-start-date');end_control=state.select_one('#desktop-end-date')
                        if start_control is None or end_control is None or start_control.get('value')!=params['start_date'] or end_control.get('value')!=params['end_date']:
                            raise ServiceError('filter_mismatch','APS did not retain the requested custom date range')
                if total is not None and total!=found['total']:raise ServiceError('range_mismatch','APS changed the result total during pagination')
                total=found['total']
                proof=old_proof or adapter.store.put(clean_html(raw,adapter.store.sanitizer),'text/html',adapter.source,response_url,
                    role='native_search_html',clauses=clauses,start=found['start'],total=total)
                proofs.append(proof)
                if facets is None:
                    facets=old_facets or adapter.store.put(encoded(found['facets']),'application/json',adapter.source,response_url,role='native_search_facets',parent_ref=proof['ref'])
                adapter._aps_last={'params':dict(params),'raw':raw,'url':response_url,'start':found['start'],'proof':proof,'facets':facets}
                if start>=total:break
                if found['page']!=expected_page:raise ServiceError('range_mismatch','APS returned a different page')
                selected.extend(row for index,row in enumerate(found['rows'],found['start']) if start<=index<start+limit)
                if found['start']+len(found['rows'])>=min(total,start+limit):break
                if not found['next_url']:raise ServiceError('pagination_control_missing','APS has more results but returned no next-page link')
                expected_page=max(found['page']+1,start//20+1)
                location=urlsplit(found['next_url']);values=parse_qs(location.query);values['page']=[str(expected_page)]
                target=urlunsplit((location.scheme,location.netloc,location.path,urlencode(values,doseq=True),''));responses.clear()
                # The observed Turbo fetch is rejected while document navigation serves this native URL.
                goto_source(page,target,adapter.profile.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
            except Exception as error:
                problem=error if isinstance(error,ServiceError) else ServiceError('search_page_failed','APS page retrieval or parsing failed',**failure_details(error))
                if not selected:
                    if proofs:problem.result['evidence']=proofs
                    raise problem from None
                errors.append(problem.result);break
        artifact=adapter.store.put(encoded(selected),'application/json',adapter.source,page.url,role='records',query=query,options=options,start=start,total=total,evidence_refs=[x['ref'] for x in proofs])
        exported=artifact
        if export in ('html','native'):
            exported={'artifacts':proofs,'scope':'Whole native HTML pages used to cover the requested window; records holds the exact window'}
        elif export=='csv':
            stream=io.StringIO(newline='');fields=list(dict.fromkeys(k for row in selected for k in row))
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(selected)
            exported=adapter.store.put(stream.getvalue(),'text/csv',adapter.source,page.url,role='mechanical_export',parent_ref=artifact['ref'])
        more=start+len(selected)<total
        return {'status':'partial' if errors else 'ok' if selected else 'not_found','source':adapter.source,'query':query,'options':options,
            'start':start,'requested':limit,'received':len(selected),'total':total,'has_more':more,'next':{'start':start+len(selected)} if more else None,
            'records':artifact,'export':exported,'evidence':proofs,'facets':facets,'errors':errors,
            'preview':[{key:row[key] for key in ('id','title','doi','url')} for row in selected[:3]]}
    except ServiceError:raise
    except Exception as error:
        raise ServiceError('search_navigation_failed','APS did not complete its search navigation',**failure_details(error)) from None
    finally:
        adapter.gateway.context.remove_listener('response',capture)


class APSInstitutional(Publisher):
    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        if export not in NATIVE_FORMATS:
            return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)
        result=search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=None)
        if result.get('received',0)==0:return result
        rows=json.loads(self.store.read(result['records']['ref'])[1]);artifacts=[];failures=[]
        for row in rows:
            try:artifacts.append({'format':export,'artifact':self.citation_for_url(row['url'],row['doi'],export)})
            except ServiceError as error:failures.append({'doi':row['doi'],**error.result})
            except Exception as error:failures.append({'doi':row['doi'],'status':'error','code':'citation_export_failed',**failure_details(error)})
        result['export']={'status':'partial' if failures else 'available','artifacts':artifacts,'failures':failures}
        if failures:result['status']='partial'
        return result

    def citation(self,page,identifier,format='ris'):
        if format not in NATIVE_FORMATS:raise ServiceError('invalid_export','APS native citation supports BibTeX and RIS')
        identifier=doi(identifier);parts=urlsplit(page.url);segments=parts.path.strip('/').split('/')
        if len(segments)<3 or segments[1]!='abstract':raise ServiceError('source_boundary','APS citation requires the selected abstract page')
        journal=segments[0];expected_path=f'/{journal}/export/{identifier}'
        modal=page.locator('#export-article-dialog')
        if modal.count()==0 or not modal.is_visible():
            page.locator('button.export-article-citation').filter(visible=True).first.click()
        radio=page.locator(f'input[name=export_format][value={format}]');radio.wait_for(state='visible',timeout=SOURCE_WAIT_MS);radio.check()
        if not hasattr(self.gateway,'native_download'):raise ServiceError('native_browser_required','APS citation requires the native Chrome gateway',status='restricted')
        try:
            data,filename,actual=self.gateway.native_download(page,lambda:page.locator('#download-citation').click(),self.profile.hosts,expected_path,timeout=SOURCE_WAIT_MS)
        finally:
            try:
                if modal.count() and modal.is_visible():
                    modal.get_by_role('button',name=re.compile(r'close',re.I)).first.click()
            except Exception:
                pass
        rows=bibliography(data,NATIVE_FORMATS[format])
        if len(rows)!=1:raise ServiceError('identity_mismatch','APS citation is not one selected publication')
        observed=rows[0].get('doi') if format=='bibtex' else rows[0].get('fields',{}).get('do',[None])[0]
        if not observed or doi(str(observed)).casefold()!=identifier.casefold():raise ServiceError('identity_mismatch','APS citation identifies another DOI')
        return self.store.put(data,NATIVE_FORMATS[format],self.source,actual,role='native_citation',format=format,
                              requested_doi=identifier,suggested_filename=filename)

    def citation_for_url(self,url,identifier,format='ris'):
        page=self.document(url)
        try:return self.citation(page,identifier,format)
        finally:page.close()

    def pdf(self,page,identifier):
        identifier=doi(identifier);parts=urlsplit(page.url);segments=parts.path.strip('/').split('/')
        if len(segments)<3 or segments[1]!='abstract':raise ServiceError('source_boundary','APS PDF requires the selected abstract page')
        expected_path=f'/{segments[0]}/pdf/{identifier}';links=page.locator('a[href*="/pdf/"]');matches=[]
        for index in range(links.count()):
            link=links.nth(index);url=urljoin(page.url,link.get_attribute('href') or '')
            if link.is_visible() and urlsplit(url).hostname in self.profile.download_hosts and unquote(urlsplit(url).path).casefold()==expected_path.casefold():
                matches.append((link,url))
        if len(matches)!=1:raise ServiceError('pdf_control_missing','APS page has no unique PDF control for the selected DOI',status='not_found')
        if not hasattr(self.gateway,'native_download'):raise ServiceError('native_browser_required','APS PDF requires the native Chrome gateway',status='restricted')
        try:
            data,filename,actual=self.gateway.native_download(page,lambda:matches[0][0].click(),self.profile.download_hosts,expected_path,timeout=SOURCE_WAIT_MS)
        except ServiceError as error:
            if error.result.get('code')!='download_missing':raise
            origin=urlsplit(page.url);headers={'User-Agent':page.evaluate('navigator.userAgent'),'Referer':origin.scheme+'://'+origin.netloc+'/'}
            data,media,actual=browser_download(self.gateway.context,matches[0][1],self.profile.download_hosts,headers=headers);filename=''
        if not data.startswith(b'%PDF-'):raise ServiceError('unexpected_content','APS PDF control returned no PDF')
        import pymupdf
        with pymupdf.open(stream=data,filetype='pdf') as document:pages=len(document)
        return self.store.put(data,'application/pdf',self.source,actual,role='fulltext',target=identifier,pages=pages,suggested_filename=filename)

    def supplementary(self,page,identifier,source_page):
        identifier=doi(identifier)
        try:page.locator(f'a[href*="/supplemental/{identifier}/"]').first.wait_for(state='attached',timeout=SOURCE_WAIT_MS)
        except Exception:pass
        links=supplement_links(page.content(),page.url,identifier,self.profile.download_hosts)
        if not links:return {'status':'source_page','reason':'No document-bound supplemental file control was identified on this selected APS page','artifact':source_page}
        files=[];errors=[]
        for item in links:
            try:
                target=item['url'];expected=urlsplit(target).path;controls=page.locator('a[href]');matches=[]
                for index in range(controls.count()):
                    control=controls.nth(index);observed=urljoin(page.url,control.get_attribute('href') or '')
                    if control.is_visible() and observed==target:matches.append(control)
                if not matches:raise ServiceError('supplement_control_missing','APS supplemental link has no visible selected-document control',status='not_found')
                filename=''
                if hasattr(self.gateway,'native_download'):
                    try:data,filename,actual=self.gateway.native_download(page,lambda:matches[0].click(),self.profile.download_hosts,expected,timeout=SOURCE_WAIT_MS)
                    except ServiceError as error:
                        if error.result.get('code')!='download_missing':raise
                        data,media,actual=browser_download(self.gateway.context,target,self.profile.download_hosts)
                else:
                    data,media,actual=browser_download(self.gateway.context,target,self.profile.download_hosts)
                if not data or data.lstrip().startswith(b'<'):raise ServiceError('unexpected_content','APS supplemental control returned no file')
                media='application/pdf' if data.startswith(b'%PDF-') else 'application/zip' if data.startswith(b'PK') else mimetypes.guess_type(filename or expected)[0] or 'application/octet-stream'
                context={}
                if media=='application/pdf':
                    import pymupdf
                    with pymupdf.open(stream=data,filetype='pdf') as document:context['pages']=len(document)
                artifact=self.store.put(data,media,self.source,actual,role='supplementary',target=identifier,suggested_filename=filename,**context)
                files.append({'label':item['label'] or filename or expected.rsplit('/',1)[-1],'artifact':artifact})
            except ServiceError as error:errors.append({'label':item['label'],**error.result})
        result={'status':'partial' if errors else 'available','files':files,'errors':errors,'artifact':source_page}
        return result

    def fetch(self,target,*,parts):
        allowed={'metadata','abstract','fulltext','supplementary','export'}
        if set(parts)-allowed:raise ServiceError('invalid_parts','Use documented APS content parts')
        base_parts=[part for part in parts if part in ('metadata','abstract')]
        base=super().fetch(target,parts=base_parts or ['metadata'])
        if not base.get('records') or base.get('status') in ('restricted','error','not_found','selection_required'):return base
        rows=json.loads(self.store.read(base['records']['ref'])[1])
        if len(rows)!=1 or not rows[0].get('doi'):raise ServiceError('identity_mismatch','APS document metadata has no unique DOI')
        row=rows[0];identifier=doi(row['doi']);components={part:base['components'][part] for part in base_parts}
        needs_page=any(part in parts for part in ('export','fulltext','supplementary'))
        if needs_page:
            page=self.document(row['url'])
            try:
                if 'export' in parts:
                    artifacts=[];errors=[]
                    for format in ('bibtex','ris'):
                        try:artifacts.append({'format':format,'artifact':self.citation(page,identifier,format)})
                        except ServiceError as error:errors.append({'format':format,**error.result})
                        except Exception as error:errors.append({'format':format,'status':'error','code':'citation_export_failed',**failure_details(error)})
                    components['export']={'status':'partial' if errors else 'available','artifacts':artifacts,'errors':errors}
                    if artifacts:components['export']['artifact']=artifacts[0]['artifact']
                if 'fulltext' in parts:
                    try:components['fulltext']={'status':'available','artifact':self.pdf(page,identifier)}
                    except ServiceError as error:components['fulltext']=error.result
                if 'supplementary' in parts:
                    components['supplementary']=self.supplementary(page,identifier,base.get('source_page'))
            finally:page.close()
        base['components']=components;base['status']='ok' if components and all(value['status']=='available' for value in components.values()) else 'partial'
        return base
