"""Public, credential-free Mwmbl search for general web candidate discovery."""
import csv
import io
from urllib.parse import urlsplit

from api_adapters import APIAdapter
from scholarly import ServiceError


def styled_text(value):
    if isinstance(value,str):
        return value
    if not isinstance(value,list) or any(not isinstance(part,dict) or not isinstance(part.get('value'),str) for part in value):
        raise ServiceError('invalid_response','Mwmbl returned an unrecognized styled text field')
    return ''.join(part['value'] for part in value)


def candidate_rows(raw):
    if not isinstance(raw,list):
        raise ServiceError('invalid_response','Mwmbl returned no result array')
    rows=[]
    for item in raw:
        if not isinstance(item,dict) or not isinstance(item.get('url'),str) or urlsplit(item['url']).scheme not in ('http','https'):
            raise ServiceError('invalid_response','Mwmbl candidate has no public web URL')
        rows.append({'id':item['url'],'url':item['url'],'title':styled_text(item.get('title',[])),
                     'snippet':styled_text(item.get('extract',[])), 'index_source':item.get('source'), 'native':item})
    return rows


class GeneralWeb(APIAdapter):
    source='general-web'
    hosts=('api.mwmbl.org',)
    max_limit=100
    min_interval=1.0

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        self.validate(options,start,limit)
        if not query.strip() or cursor or export not in (None,'json','native','csv'):
            raise ServiceError('invalid_options','Use a nonempty keyword query, start/limit and json/native/csv export; this endpoint has no cursor')
        raw,evidence=self.request('https://api.mwmbl.org/search/',params={'s':query})
        try:
            rows=candidate_rows(raw)
        except ServiceError as error:
            error.result['evidence']=evidence
            raise
        result=self.page(rows[start:start+limit],len(rows),evidence,query,options,start,limit)
        result['total']=None
        result['returned_set_size']=len(rows)
        result['scope']='Mwmbl public web index candidates; global hit count and additional server pages are not supplied'
        result['range_note']='start/limit select within the returned set. The complete native array remains in evidence for extraction without another search.'
        if export=='csv':
            buffer=io.StringIO(newline='')
            writer=csv.DictWriter(buffer,fieldnames=['url','title','snippet','index_source'])
            writer.writeheader()
            writer.writerows({k:row[k] for k in writer.fieldnames} for row in rows[start:start+limit])
            result['export']=self.store.put(buffer.getvalue(),'text/csv',self.source,evidence['url'],role='candidate_csv',parent_ref=evidence['ref'],start=start,requested=limit)
            return result
        return self.export_page(result,export)

    def fetch(self,target,*,parts):
        raise ServiceError('candidate_source_required','This search engine supplies candidate links and snippets. Select the publisher or public-document source to retrieve a candidate.',status='selection_required',source=self.source)
