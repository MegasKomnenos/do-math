"""Native DBLP publication metadata, candidate names and seven citation formats."""
import json,re
from urllib.parse import urlsplit,unquote
from lxml import etree
from scholarly import ServiceError, bibliography, failure_details, xml_tree

FORMATS={'xml':('xml','application/xml'),'bibtex':('bib','application/x-bibtex'),'ris':('ris','application/x-research-info-systems'),
    'ntriples':('nt','application/n-triples'),'turtle':('ttl','text/turtle'),'rdf':('rdf','application/rdf+xml'),'plain':('txt','text/plain')}


def record_key(adapter,target):
    value=target
    if value.startswith(('https://','http://')):
        parsed=urlsplit(value)
        if not adapter.allowed_url(value) or not parsed.path.startswith('/rec/'):
            raise ServiceError('source_boundary','Use a DBLP publication key, record URL or name')
        value=unquote(parsed.path[5:])
    value=re.sub(r'\.(?:html|xml|bib|ris|nt|ttl|rdf|txt)$','',value)
    if re.fullmatch(r'(?:journals|conf|books|reference|phd|tr)/[\w/.-]+',value) and '..' not in value:return value
    if re.match(r'^(?:journals|conf|books|reference|phd|tr)/',value):raise ServiceError('invalid_target','Malformed DBLP publication key')
    return None


def xml_record(data,key):
    root=xml_tree(data).getroot()
    if root.tag!='dblp' or len(root)!=1 or root[0].get('key')!=key:
        raise ServiceError('identity_mismatch','DBLP XML does not contain the selected publication key')
    child=root[0]
    return {'kind':child.tag,'attributes':dict(child.attrib),'fields':[{'name':f.tag,'value':''.join(f.itertext()),'attributes':dict(f.attrib),
        **({'xml':etree.tostring(f,encoding='unicode')} if len(f) else {})} for f in child]}


def native_export(adapter,key,format,*,record=None,xml=None):
    extension,media=FORMATS[format]
    if format=='xml' and xml:return xml
    data,proof=adapter.request('https://dblp.org/rec/'+key+'.'+extension,accept='binary')
    artifact=adapter.store.put(data,media,adapter.source,proof['url'],preserve_bytes=True,role='native_citation',format=format,publication_key=key,source_media_type=proof['media_type'])
    try:
        if format=='xml':xml_record(data,key)
        elif format in ('bibtex','ris'):
            rows=bibliography(data,media)
            actual=rows[0].get('id') if format=='bibtex' and len(rows)==1 else (rows[0].get('fields',{}).get('id') or [None])[0] if len(rows)==1 else None
            if actual!='DBLP:'+key:raise ServiceError('identity_mismatch','DBLP citation identifies another publication key')
        elif format in ('rdf','turtle','ntriples'):
            from rdflib import Graph,URIRef
            rdf=etree.tostring(xml_tree(data).getroot()) if format=='rdf' else data
            graph=Graph().parse(data=rdf,format={'rdf':'xml','turtle':'turtle','ntriples':'nt'}[format])
            if not any(graph.triples((URIRef('https://dblp.org/rec/'+key),None,None))):
                raise ServiceError('identity_mismatch','DBLP RDF has no statements about the selected publication')
        else:
            title=record.get('title') if record else None
            if record and not title:title=next((f['value'] for f in record.get('fields',[]) if f['name']=='title'),None)
            text=' '.join(data.decode('utf-8').split())
            if not text or not title or ' '.join(title.split()).casefold() not in text.casefold():
                raise ServiceError('identity_mismatch','DBLP plain citation does not contain the selected title')
    except ServiceError as error:error.result['source_export']=artifact;raise
    except Exception as error:raise ServiceError('invalid_native_citation','DBLP returned an unreadable native citation',source_export=artifact,**failure_details(error)) from None
    return artifact


def export_rows(adapter,rows,format):
    files=[];errors=[]
    for row in rows:
        key=row['key']
        try:files.append({'key':key,'format':format,'artifact':native_export(adapter,key,format,record=row)})
        except ServiceError as error:errors.append({'key':key,'format':format,**error.result})
    return {'status':'partial' if errors else 'available','format':format,'artifacts':files,'errors':errors}


def fetch(adapter,target,parts):
    if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:raise ServiceError('invalid_parts','Use the documented content parts')
    key=record_key(adapter,target)
    if key is None:
        result=adapter.search(target,options={},limit=20)
        return {**result,'status':'selection_required' if result.get('received') else result['status'],'requested_target':target}
    data,proof=adapter.request('https://dblp.org/rec/'+key+'.xml',accept='binary');row=xml_record(data,key)
    native=adapter.store.put(data,'application/xml',adapter.source,proof['url'],preserve_bytes=True,role='native_citation',format='xml',publication_key=key)
    result=adapter.fetched([row],native,parts,('metadata','export'))
    if 'export' in parts:
        files=[];errors=[]
        for format in FORMATS:
            try:files.append({'format':format,'artifact':native_export(adapter,key,format,record=row,xml=native)})
            except ServiceError as error:errors.append({'format':format,**error.result})
        result['components']['export']={'status':'partial' if errors else 'available','artifact':native,'artifacts':files,'errors':errors}
    result['status']='ok' if all(c['status']=='available' for c in result['components'].values()) else 'partial'
    result.update(publication_key=key,native_metadata=native)
    return result
