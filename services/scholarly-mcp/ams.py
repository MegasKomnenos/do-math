"""AMS Digital Library native institutional browse records."""
import csv,io,json,re
from urllib.parse import urlsplit,urljoin,parse_qs,urlencode,urlunsplit
from browser_adapters import goto_source,clean_html,dismiss_cookies
from publishers import Publisher,PROFILES
from scholarly import ServiceError,encoded


def product_records(payload):
    rows=payload.get('Products')
    total,page,capacity=(payload.get(key) for key in ('TotalRows','PageNumber','RowsPerPage'))
    if not isinstance(rows,list) or any(not isinstance(row,dict) or not row.get('Title') for row in rows) or any(type(v) is not int for v in (total,page,capacity)):
        raise ServiceError('invalid_response','AMS returned no native product range')
    if total<0 or page<1 or capacity<1 or len(rows)!=min(capacity,max(0,total-(page-1)*capacity)):
        raise ServiceError('range_mismatch','AMS products do not match the declared range')
    return rows,total,(page-1)*capacity


class AMS(Publisher):
    fields={'Title':('advancedSearchTitleInput','ProductTitle'),'Author':('advancedSearchAuthorInput','Author'),
            'ProductCode':('advancedSearchFreeformInput','ProductCode'),'BookText':('advancedSearchAnywhereInput','Anywhere'),
            'ISBN':('advancedSearchISBNInput','ISBN'),'MSC':('advancedSearchMSCInput','MSC')}

    def __init__(self,store,gateway):
        super().__init__(store,gateway,next(p for p in PROFILES if p.source=='ams'))
        self.known={}

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
            raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
        if cursor or set(options)-{'field','title','author','product_code','book_text','isbn','msc','content_type'} or options.get('field','Title') not in self.fields:
            raise ServiceError('invalid_options','Use the documented AMS advanced-search fields')
        if export not in (None,'json','native','csv','html'):
            raise ServiceError('export_not_implemented','AMS native file export remains unverified after access restrictions; use json, native, csv or html',status='not_implemented')
        content=options.get('content_type','All')
        if content not in ('All','EBook','Journal','Abstracts'):
            raise ServiceError('invalid_options','content_type must be All, EBook, Journal or Abstracts')
        page=self.gateway.open('ams','AMS',self.profile.hosts,'body')
        goto_source(page,'https://'+urlsplit(page.url).hostname+'/AdvancedSearch',self.profile.hosts,wait_until='domcontentloaded',timeout=45000)
        dismiss_cookies(page)
        for control,_ in self.fields.values():
            if page.locator('#'+control).input_value():
                page.locator('#'+control).fill('')
        field=options.get('field','Title')
        values={field:query}
        aliases={'title':'Title','author':'Author','product_code':'ProductCode','book_text':'BookText','isbn':'ISBN','msc':'MSC'}
        for key,name in aliases.items():
            if key in options:
                if name in values:
                    raise ServiceError('invalid_options','The primary field and an additional field must not overlap',field=name)
                values[name]=str(options[key])
        for name,value in values.items():
            page.locator('#'+self.fields[name][0]).fill(value)
        if not page.locator('#advancedSearchContentTypeInput'+content).is_checked():
            page.locator('label[for="advancedSearchContentTypeInput'+content+'"]').click()

        def matches(response):
            return urlsplit(response.url).hostname in self.profile.hosts and urlsplit(response.url).path=='/product/browseproducts' and response.request.method=='POST'

        try:
            with page.expect_response(matches,timeout=60000) as pending:
                page.locator('#advancedSearchGo').filter(visible=True).first.click()
                if re.search(r'^(Just a moment|Access Denied|Attention Required)',page.title(),re.I):
                    raise ServiceError('publisher_access_challenge','AMS displayed an access verification page',status='restricted')
        except ServiceError:
            raise
        except Exception as error:
            challenged=bool(re.search(r'^(Just a moment|Access Denied|Attention Required)',page.title(),re.I))
            raise ServiceError('publisher_access_challenge' if challenged else 'search_response_not_received','AMS did not provide a native search response',status='restricted' if challenged else 'error',error_type=type(error).__name__) from None
        response=pending.value
        selected,evidence,html_pages=[],[],[]
        total=None
        search_url=None
        page_number=1
        while True:
            if response.status in (401,403):
                raise ServiceError('access_restricted','AMS restricted this search response',status='restricted')
            if response.status!=200:
                raise ServiceError('provider_error','AMS search failed',http_status=response.status)
            request=parse_qs(response.request.post_data or '')
            advanced=parse_qs(request.get('advancedSearch',[''])[0])
            if any(advanced.get(self.fields[name][1])!=[value] for name,value in values.items()):
                raise ServiceError('query_mismatch','AMS native request does not retain the submitted fields')
            payload=response.json()
            native,reported,first=product_records(payload)
            expected_type={'EBook':'B','Journal':'A','Abstracts':'ABS'}.get(content)
            if expected_type and any(row.get('ContentType')!=expected_type for row in native):
                raise ServiceError('filter_mismatch','AMS returned a product outside the requested content type')
            if payload['PageNumber']!=page_number or total is not None and total!=reported:
                raise ServiceError('range_mismatch','AMS changed the page or result total')
            total=reported
            proof=self.store.put(encoded(payload),'application/json',self.source,response.url,role='native_search_response',query=query,options=options)
            evidence.append(proof)
            selector='#productBrowseListContainer > li.productBrowseListItem:not(.placeHolderItem) a.productBrowseTitleLink'
            page.wait_for_function('(arg) => document.querySelectorAll(arg.selector).length === arg.count',arg={'selector':selector,'count':len(native)},timeout=30000)
            if native:
                expected='Showing '+str(first+1)+' - '+str(first+len(native))+' of '+str(total)+' results'
                page.wait_for_function('(expected) => document.querySelector("#productBrowseResultCountTopOneColumn")?.textContent.replace(/\\s+/g," ").trim() === expected',arg=expected,timeout=30000)
            anchors=page.locator(selector).all()
            for i,(row,anchor) in enumerate(zip(native,anchors),first):
                row={**row,'target':urljoin(page.url,anchor.get_attribute('href'))}
                for key in (row['target'],row.get('DOI'),row.get('ProductCode') if row['ContentType']=='B' else None):
                    if key:
                        self.known[key.casefold()]=(row,proof)
                if start<=i<start+limit:
                    selected.append(row)
            search_url=page.url
            if export=='html':
                html_pages.append(self.store.put(clean_html(page.content(),self.store.sanitizer),'text/html',self.source,page.url,role='search_page',first=first,total=total))
            if first+len(native)>=min(start+limit,total):
                break
            page_number=max(page_number+1,start//payload['RowsPerPage']+1)
            parsed=urlsplit(page.url)
            params=parse_qs(parsed.query)
            params['PageNumber']=[str(page_number)]
            with page.expect_response(matches,timeout=60000) as pending:
                goto_source(page,urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(params,doseq=True),'')),self.profile.hosts,wait_until='domcontentloaded',timeout=45000)
            response=pending.value
        artifact=self.store.put(encoded(selected),'application/json',self.source,search_url,role='records',query=query,options=options,start=start,total=total)
        exported=artifact
        if export=='native':
            exported={'artifacts':evidence,'scope':'Whole native pages covering the requested window'}
        elif export=='html':
            exported={'artifacts':html_pages,'scope':'Visited native pages; records contains the exact requested window'}
        elif export=='csv':
            buffer=io.StringIO(newline='')
            fields=list(dict.fromkeys(k for row in selected for k in row))
            writer=csv.DictWriter(buffer,fieldnames=fields)
            writer.writeheader()
            writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in selected)
            exported=self.store.put(buffer.getvalue(),'text/csv',self.source,search_url,role='mechanical_export',parent_ref=artifact['ref'])
        more=start+len(selected)<total
        return {'status':'ok' if selected else 'not_found','source':self.source,'query':query,'options':options,'start':start,'requested':limit,
                'received':len(selected),'total':total,'has_more':more,'next':{'start':start+len(selected)} if more else None,
                'records':artifact,'export':exported,'evidence':evidence,'preview':[{k:row.get(k) for k in ('Title','Subtitle','ProductCode','DOI','target')} for row in selected[:3]]}

    def fetch(self,target,*,parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Unknown requested content')
        key=target
        explicit_code=False
        if target.startswith(('http://','https://')):
            parsed=urlsplit(target)
            if parsed.hostname in self.profile.hosts and parsed.path.lower()=='/view':
                values=parse_qs(parsed.query).get('ProductCode',[])
                if len(values)==1:
                    key=values[0]
                    explicit_code=True
        code=explicit_code or re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*/[\w./-]+',key) or key.isupper() and re.fullmatch(r'[A-Z][A-Z0-9_-]*',key)
        if code and key.casefold() not in self.known:
            found=self.search(key,options={'field':'ProductCode'},limit=2)
            if found['total']!=1:
                return {**found,'status':'selection_required' if found['received'] else 'not_found'}
        if key.casefold() not in self.known:
            return super().fetch(target,parts=parts)
        row,proof=self.known[key.casefold()]
        artifact=self.store.put(encoded([row]),'application/json',self.source,row['target'],role='records',evidence_ref=proof['ref'])
        components={}
        for part in parts:
            if part in ('metadata','export'):
                components[part]={'status':'available','artifact':artifact,'format':'native_product_json'}
            elif part=='abstract':
                field='Abstract' if row.get('Abstract') else 'ProductDescription' if row.get('ProductDescription') else None
                components[part]={'status':'available','artifact':artifact,'field':field,'kind':'publisher_abstract' if field=='Abstract' else 'publisher_product_description'} if field else {'status':'not_found','reason':'This native AMS product record contains neither Abstract nor ProductDescription'}
        document_parts=[part for part in parts if part in ('fulltext','supplementary')]
        if document_parts:
            try:
                obtained=super().fetch(row['target'],parts=document_parts)
                components.update(obtained.get('components',{}))
            except ServiceError as error:
                components.update({part:error.result for part in document_parts})
            except Exception as error:
                components.update({part:{'status':'error','code':'document_retrieval_failed','error_type':type(error).__name__} for part in document_parts})
        return {'status':'ok' if all(part['status']=='available' for part in components.values()) else 'partial',
                'source':self.source,'target':target,'records':artifact,'components':components,'evidence':[proof]}
