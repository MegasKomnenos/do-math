"""JSTOR's publicly accessible native citation endpoint."""
import re
from urllib.parse import quote,urlsplit

from api_adapters import APIAdapter
from scholarly import ServiceError,encoded,bibliography


def stable_id(value):
    if value.startswith(('http://','https://')):
        parsed=urlsplit(value)
        if parsed.hostname in ('doi.org','dx.doi.org'):
            value=parsed.path.lstrip('/')
        elif parsed.hostname in ('www.jstor.org','jstor.org','www-jstor-org.libproxy.knu.ac.kr'):
            match=re.fullmatch(r'/stable/(?:pdf/)?(.+?)(?:\.pdf)?/?',parsed.path)
            if not match:
                raise ServiceError('invalid_target','Use a JSTOR stable URL')
            value=match[1]
        else:
            raise ServiceError('source_boundary','Target is outside JSTOR')
    value=re.sub(r'^(?:doi:\s*)?10\.2307/','',value,flags=re.I)
    if not re.fullmatch(r'(?:[0-9]+|j\.[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)?)',value):
        raise ServiceError('invalid_target','Use a JSTOR stable ID, stable URL or 10.2307 DOI')
    return value


class JSTOR(APIAdapter):
    source='jstor'
    hosts=('www.jstor.org','jstor.org')

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        raise ServiceError('web_search_not_implemented','The citation API has no keyword search; institutional web search is not connected because the observed route requires CAPTCHA',status='not_implemented',source=self.source)

    def fetch(self,target,*,parts):
        identifier=stable_id(target)
        if set(parts)-{'metadata','abstract','export','fulltext','supplementary'}:
            raise ServiceError('invalid_parts','Use metadata, abstract, export, fulltext or supplementary')
        data,evidence=self.request('https://www.jstor.org/citation/ris/'+quote(identifier,safe='/'),accept='binary')
        rows=bibliography(data,'application/x-research-info-systems')
        if len(rows)!=1:
            raise ServiceError('identity_mismatch','JSTOR returned no unique citation record',evidence=evidence)
        urls=rows[0]['fields'].get('ur',[])
        if not any(stable_id(url)==identifier for url in urls if urlsplit(url).hostname in self.hosts):
            raise ServiceError('identity_mismatch','JSTOR citation does not identify the requested stable record',evidence=evidence)
        native=self.store.put(data,'application/x-research-info-systems',self.source,evidence['url'],role='native_citation',stable_id=identifier,evidence_ref=evidence['ref'])
        row={'id':identifier,'title':rows[0]['fields'].get('ti',[None])[0],**rows[0]}
        record=self.store.put(encoded([row]),'application/json',self.source,evidence['url'],role='records',parent_ref=native['ref'])
        components={}
        for part in parts:
            if part=='metadata':
                components[part]={'status':'available','artifact':record}
            elif part=='export':
                components[part]={'status':'available','artifact':native,'format':'ris'}
            elif part=='abstract':
                values=row['fields'].get('ab',[])
                if values:
                    abstract=self.store.put('\n\n'.join(values),'text/plain',self.source,evidence['url'],role='abstract',parent_ref=native['ref'])
                    components[part]={'status':'available','artifact':abstract}
                else:
                    components[part]={'status':'not_offered','reason':'This native citation contains no abstract'}
            else:
                components[part]={'status':'not_implemented','reason':'Citation API provides bibliography; institutional document retrieval remains blocked by the observed browser access challenge'}
        return {'status':'ok' if all(v['status']=='available' for v in components.values()) else 'partial','source':self.source,'target':target,
                'records':record,'components':components,'stable_id':identifier}
