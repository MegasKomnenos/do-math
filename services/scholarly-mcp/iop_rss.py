"""Keyless IOP RSS API; this endpoint always orders results by recency."""
import csv,io,re,time
from urllib.parse import urlsplit,urljoin,urlencode
from defusedxml import ElementTree as ET
from api_adapters import APIAdapter,doi
from scholarly import ServiceError,Sanitizer

RSS='{http://purl.org/rss/1.0/}'
RDF='{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
DC='{http://purl.org/dc/elements/1.1/}'
IOP='{http://iopscience.iop.org}'
PRISM='{http://prismstandard.org/namespaces/basic/1.2/}'


def feed_records(data,sanitizer=None):
    sanitizer=sanitizer or Sanitizer()
    try:root=ET.fromstring(data)
    except Exception:raise ServiceError('invalid_response','IOP did not return a readable RSS XML document') from None
    if root.tag!=RDF+'RDF':raise ServiceError('invalid_response','IOP response is not the observed RDF/RSS feed')
    sequence=root.find('./'+RSS+'channel/'+RSS+'items/'+RDF+'Seq')
    if sequence is None:raise ServiceError('invalid_response','IOP RSS has no native item sequence')
    items=root.findall(RSS+'item');index={item.get(RDF+'about'):item for item in items}
    order=[entry.get(RDF+'resource') for entry in sequence];warnings=[]
    if len(sequence)==len(items) and all(not entry.attrib and not (entry.text or '').strip() and not (entry.tail or '').strip() and len(entry)==0 for entry in sequence):
        order=[item.get(RDF+'about') for item in items]
        warnings=['empty_rdf_sequence_used_item_order']
    if None in index or None in order or len(index)!=len(items) or len(set(order))!=len(order) or set(order)!=set(index):
        raise ServiceError('invalid_response','IOP RSS item identities and sequence do not agree')
    rows=[]
    for key in order:
        item=index[key]
        def value(tag):
            node=item.find(tag)
            return ''.join(node.itertext()) if node is not None else None
        identifier=value(PRISM+'doi');title=value(RSS+'title');url=value(RSS+'link')
        if not identifier or not title or not url:raise ServiceError('invalid_response','IOP RSS item has no DOI, title or link')
        identifier=doi(identifier)
        rows.append({'id':identifier,'doi':identifier,'title':title,'url':url,'parse_warnings':warnings,
            'authors':[''.join(node.itertext()) for node in item.findall(DC+'creator')],
            'description_html':value(RSS+'description'),'citation':value(IOP+'citation'),'source_display':value(DC+'source'),
            'pdf_url':value(IOP+'pdf'),'publication':value(PRISM+'publicationName'),'volume':value(PRISM+'volume'),
            'number':value(PRISM+'number'),'starting_page':value(PRISM+'startingPage'),
            'xml':sanitizer.xml(ET.tostring(item,encoding='utf-8')).decode('utf-8')})
    return rows


class IOPRSS(APIAdapter):
    source='iop'
    hosts=('iopscience.iop.org',)
    options=('sort','period','journals','page_size')
    max_limit=1000
    min_interval=1.0

    def __init__(self,store,client=None,*,gateway=None,hosts=None):
        super().__init__(store,client)
        self.gateway=gateway;self.session_hosts=hosts

    def request_feed(self,params):
        if self.gateway is None:
            return self.request('https://iopscience.iop.org/nsearch/rss',params=params,accept='xml')
        from browser_adapters import browser_download
        page=self.gateway.open(self.source,'IOP',self.session_hosts,'body')
        delay=self.min_interval-(time.monotonic()-self.last_request)
        if delay>0:time.sleep(delay)
        self.last_request=time.monotonic()
        url=urljoin(page.url,'/nsearch/rss?'+urlencode(params,doseq=True))
        data,media,actual=browser_download(self.gateway.context,url,self.session_hosts)
        proof=self.store.put(data,media,self.source,actual,role='rss_api_response',request=params)
        return data,proof

    def allowed_url(self,url):
        if urlsplit(url).hostname in ('validate.perfdrive.com','challenges.cloudflare.com'):
            raise ServiceError('publisher_access_challenge','IOP public API redirected to access verification',status='restricted')
        return super().allowed_url(url)

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        self.validate(options,start,limit,cursor)
        if cursor or options.get('sort','newest')!='newest':raise ServiceError('invalid_options','IOP RSS supports newest order and numeric start only')
        if not isinstance(query,str) or not query.strip():raise ServiceError('invalid_query','Use a nonempty IOP search term')
        if export not in (None,'json','csv','rss','xml','native'):raise ServiceError('invalid_export','Use json, csv or original rss/xml/native pages')
        period=options.get('period','anytime');size=options.get('page_size',20);journals=options.get('journals',[])
        if period not in ('anytime','lastThirtyDays','lastTwelveMonths','lastFiveYears') or type(size) is not int or size not in (10,20,50):
            raise ServiceError('invalid_options','Use a documented period and page_size 10/20/50')
        if not isinstance(journals,list) or any(not isinstance(x,str) or not re.fullmatch(r'\d{4}-\d{3}[\dXx]',x) for x in journals):
            raise ServiceError('invalid_options','journals must be native ISSN values')
        journals=[x.upper() for x in journals]
        if len(set(journals))!=len(journals):raise ServiceError('invalid_options','Do not repeat an ISSN')
        params={'terms':query,'searchDatePeriod':period,'orderBy':'newest','pageLength':size,'currentPage':start//size+1}
        if journals:params['journals']=journals
        rows=[];proofs=[];errors=[];seen=set();more=False
        while True:
            try:
                data,proof=self.request_feed(params)
                proofs.append(proof)
                native=feed_records(data,self.store.sanitizer)
                if len(native)>size:raise ServiceError('range_mismatch','IOP RSS exceeded the requested native page size')
                ids={row['id'] for row in native}
                if seen&ids:raise ServiceError('range_mismatch','IOP repeated documents across RSS pages')
                seen.update(ids);offset=(params['currentPage']-1)*size
                rows.extend(row for index,row in enumerate(native,offset) if start<=index<start+limit)
                more=start+len(rows)<offset+len(native) or len(native)==size
                if len(rows)>=limit or len(native)<size:break
                params['currentPage']+=1
            except ServiceError as error:
                if proofs:error.result['evidence']=proofs
                if not rows:raise
                errors.append(error.result);more=True;break
        result=self.page(rows,None,proofs[-1],query,options,start,limit,more=more,evidence_refs=[p['ref'] for p in proofs])
        result.update(order='newest',retrieval='rss_api',access='institutional_proxy' if self.gateway is not None else 'anonymous',evidence=proofs,errors=errors,
            scope='IOP newest-first RSS API window. No global match count is supplied; the web UI top-500 bound is not imposed on this API.')
        result['preview']=[{k:row[k] for k in ('id','doi','title','url')} for row in rows[:3]]
        if errors:result['status']='partial'
        if export in ('rss','xml','native'):
            result['export']=proofs[0] if len(proofs)==1 else {'artifacts':proofs,'scope':'Native XML pages covering the exact records window'}
        elif export=='csv':
            import json
            stream=io.StringIO(newline='');fields=list(dict.fromkeys(k for row in rows for k in row));writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
            writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in rows)
            result['export']=self.store.put(stream.getvalue(),'text/csv',self.source,proofs[-1]['url'],role='mechanical_export',parent_ref=result['records']['ref'])
        return result
