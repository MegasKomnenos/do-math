"""DBLP's explicitly selected, keyless public knowledge-graph API."""
import csv,io,json,re
from urllib.parse import quote,urlsplit,unquote
from rdflib import BNode,Literal,URIRef
from rdflib.namespace import XSD
from rdflib.plugins.sparql.parser import parseQuery, BLANK_NODE_LABEL
from rdflib.plugins.sparql.parserutils import CompValue
from pyparsing import ParseResults
from api_adapters import APIAdapter,doi
from scholarly import ServiceError,encoded

ENDPOINT='https://sparql.dblp.org/sparql'
SCHEMA='https://dblp.org/rdf/schema#'

# Parse raw tokens before decoding escapes so UCHAR cannot change delimiters.
# RDFLib's query subgrammar normalizes numbers and omits the top-level Unicode
# preprocessing; neither behavior is suitable for preserving TSV lexical forms.
TSV_ESCAPE = r'''\\(?:["'tbnrf\\]|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})'''
TSV_STRING = rf'''(?:"(?:[^"\\\r\n]|{TSV_ESCAPE})*"|'(?:[^'\\\r\n]|{TSV_ESCAPE})*')'''
TSV_IRI = r'<(?:[^<>"{}|^`\\\x00-\x20]|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})*>'
TSV_LITERAL = re.compile(rf'(?P<string>{TSV_STRING})(?:@(?P<lang>[a-zA-Z]+(?:-[a-zA-Z0-9]+)*)|\^\^(?P<datatype>{TSV_IRI}))?')
TSV_BNODE = BLANK_NODE_LABEL.copy()


def tsv_unescape(value):
    escapes = {'"':'"', "'":"'", '\\':'\\', 't':'\t', 'b':'\b', 'n':'\n', 'r':'\r', 'f':'\f'}
    def replace(match):
        token = match.group()[1:]
        return chr(int(token[1:], 16)) if token[0] in 'uU' else escapes[token]
    decoded = re.sub(TSV_ESCAPE, replace, value)
    if any(0xD800 <= ord(character) <= 0xDFFF for character in decoded):
        raise ValueError('Invalid Unicode surrogate')
    return decoded


def tsv_term(cell):
    if not cell or cell != cell.strip():
        raise ServiceError('invalid_response','Native TSV contains an invalid RDF term')
    try:
        match = TSV_LITERAL.fullmatch(cell)
        if match:
            datatype = match.group('datatype')
            return Literal(tsv_unescape(match.group('string')[1:-1]), lang=match.group('lang'),
                           datatype=URIRef(tsv_unescape(datatype[1:-1])) if datatype else None, normalize=False)
        if re.fullmatch(TSV_IRI, cell):
            return URIRef(tsv_unescape(cell[1:-1]))
        if cell.startswith('_:'):
            return TSV_BNODE.parse_string(cell, parse_all=True)[0]
        for pattern, datatype in ((r'[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+|[0-9]+)[eE][+-]?[0-9]+', XSD.double),
                                  (r'[+-]?[0-9]*\.[0-9]+', XSD.decimal),
                                  (r'[+-]?[0-9]+', XSD.integer), (r'true|false', XSD.boolean)):
            if re.fullmatch(pattern, cell):
                return Literal(cell, datatype=datatype, normalize=False)
        raise ValueError('Invalid TSV term')
    except Exception:
        raise ServiceError('invalid_response','Native TSV contains an invalid RDF term') from None


def same_rdf_term(observed, expected):
    if isinstance(observed, Literal) and isinstance(expected, Literal):
        # RDF 1.1 plain strings denote xsd:string; language tags ignore case.
        # Numeric/boolean value equality must not replace lexical/type equality.
        return (str(observed) == str(expected)
                and (observed.datatype or XSD.string) == (expected.datatype or XSD.string)
                and (observed.language or '').casefold() == (expected.language or '').casefold())
    return type(observed) is type(expected) and observed == expected


def bounded_query(query,start,limit):
    try:parsed=parseQuery(query)
    except Exception:raise ServiceError('invalid_query','Use a valid SPARQL SELECT query') from None
    if parsed[1].name!='SelectQuery':
        raise ServiceError('unsupported_query_form','This adapter accepts SELECT queries',status='unsupported')
    if 'limitoffset' in parsed[1]:
        raise ServiceError('invalid_range','Use tool start/limit instead of outer SPARQL LIMIT/OFFSET')
    def visit(node):
        if isinstance(node,CompValue):
            if node.name in ('ServiceGraphPattern','DatasetClause'):
                raise ServiceError('source_boundary','SERVICE and FROM would change the selected dataset; they are not allowed')
            for value in node.values():visit(value)
        elif isinstance(node,(list,tuple,ParseResults)):
            for value in node:visit(value)
    visit(parsed)
    return query+f'\nLIMIT {limit} OFFSET {start}'


def bindings(raw):
    variables=raw.get('head',{}).get('vars');rows=raw.get('results',{}).get('bindings')
    if not isinstance(variables,list) or any(not isinstance(v,str) for v in variables) or len(set(variables))!=len(variables) or not isinstance(rows,list):
        raise ServiceError('invalid_response','DBLP KG returned no variable list and bindings')
    for row in rows:
        if not isinstance(row,dict) or set(row)-set(variables):
            raise ServiceError('invalid_response','A binding contains an undeclared variable')
        for term in row.values():
            if not isinstance(term,dict) or term.get('type') not in ('uri','literal','typed-literal','bnode') or not isinstance(term.get('value'),str):
                raise ServiceError('invalid_response','A binding has no valid RDF term')
            if any(key in term and not isinstance(term[key],str) for key in ('datatype','xml:lang')):
                raise ServiceError('invalid_response','RDF datatype and language must be strings')
    return variables,rows


def validate_table(data,format,variables,rows):
    if format=='csv':
        table=list(csv.reader(io.StringIO(data.decode('utf-8-sig'))))
        expected=[variables]+[[row.get(v,{}).get('value','') for v in variables] for row in rows]
        if table!=expected:raise ServiceError('export_range_mismatch','Native CSV differs from the selected bindings')
        return
    table=list(csv.reader(io.StringIO(data.decode('utf-8-sig')),delimiter='\t',quoting=csv.QUOTE_NONE))
    if not table or table[0]!=['?'+v for v in variables] or len(table)!=len(rows)+1 or any(len(row)!=len(variables) for row in table):
        raise ServiceError('export_range_mismatch','Native TSV has a different variable list or row count')
    for cells,row in zip(table[1:],rows):
        for cell,variable in zip(cells,variables):
            term=row.get(variable)
            if term is None:
                if cell:raise ServiceError('export_range_mismatch','Native TSV bound a missing variable')
                continue
            expected=URIRef(term['value']) if term['type']=='uri' else BNode(term['value']) if term['type']=='bnode' else Literal(term['value'],lang=term.get('xml:lang'),datatype=term.get('datatype'),normalize=False)
            observed=tsv_term(cell)
            if not same_rdf_term(observed,expected):
                raise ServiceError('export_term_mismatch','Native TSV differs from the selected RDF terms',variable=variable,
                    expected_datatype=term.get('datatype'),observed_datatype=str(observed.datatype) if isinstance(observed,Literal) and observed.datatype else None)


def exact_tsv(variables,rows):
    def render(term):
        if term['type']=='uri':return URIRef(term['value']).n3()
        if term['type']=='bnode':return BNode(term['value']).n3()
        value=term['value']
        if any(0xD800<=ord(character)<=0xDFFF for character in value):
            raise ServiceError('invalid_response','An RDF literal contains an invalid Unicode surrogate')
        language=term.get('xml:lang');datatype=term.get('datatype')
        if language and datatype:
            raise ServiceError('invalid_response','An RDF literal has both a language and datatype')
        suffix='@'+language if language else '^^'+URIRef(datatype).n3() if datatype else ''
        return json.dumps(value,ensure_ascii=False)+suffix
    lines=['\t'.join('?'+variable for variable in variables)]
    lines.extend('\t'.join(render(row[variable]) if variable in row else '' for variable in variables) for row in rows)
    return ('\n'.join(lines)+'\n').encode('utf-8')


class DBLPKG(APIAdapter):
    source='dblp-kg'
    hosts=('sparql.dblp.org',)
    max_limit=1000
    min_interval=1.05

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        self.validate(options,start,limit)
        if cursor:raise ServiceError('invalid_cursor','Use start instead of a cursor')
        if export not in (None,'json','native','csv','tsv','tsv_exact'):
            raise ServiceError('unsupported_export','Use json, native, csv, tsv or tsv_exact',status='unsupported')
        requested=bounded_query(query,start,limit)
        raw,evidence=self.request(ENDPOINT,params={'query':requested},headers={'Accept':'application/sparql-results+json'})
        variables,rows=bindings(raw)
        if len(rows)>limit:raise ServiceError('range_mismatch','DBLP KG exceeded the requested result window')
        result=self.page(rows,None,evidence,query,options,start,limit,more=len(rows)==limit)
        result.update(variables=variables,provider_result_size=raw.get('meta',{}).get('result-size-total'),
            preview=[{key:term['value'] for key,term in row.items()} for row in rows[:3]],
            scope='Only the selected DBLP knowledge graph. RDF term type, language and datatype are preserved; missing bindings stay missing.')
        if export=='native':result['export']=evidence
        elif export=='tsv_exact':
            try:
                data=exact_tsv(variables,rows)
                validate_table(data,'tsv',variables,rows)
                result['export']=self.store.put(data,'text/tab-separated-values',self.source,ENDPOINT,role='generated_lossless_tsv',
                    request={'query':query,'start':start,'limit':limit},basis_format='application/sparql-results+json',evidence_refs=[evidence['ref']])
            except ServiceError as error:
                result.update(status='partial',export=error.result)
            except Exception as error:
                result.update(status='partial',export={'status':'error','code':'invalid_export','error_type':type(error).__name__})
        elif export in ('csv','tsv'):
            native=None
            try:
                data,native=self.request(ENDPOINT,params={'query':requested},headers={'Accept':'text/csv' if export=='csv' else 'text/tab-separated-values'},accept='binary')
                validate_table(data,export,variables,rows)
                result['export']=native
            except ServiceError as error:
                result.update(status='partial',export={**error.result,**({'source_export':native} if native else {})})
            except Exception as error:
                result.update(status='partial',export={'status':'error','code':'invalid_export','error_type':type(error).__name__,**({'source_export':native} if native else {})})
        return result

    def fetch(self,target,*,parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Use the documented content parts')
        value=target
        if value.startswith(('https://','http://')) and urlsplit(value).hostname not in ('doi.org','dx.doi.org'):
            parsed=urlsplit(value)
            if parsed.username or parsed.password or parsed.port not in (None,80,443) or parsed.hostname not in ('dblp.org','www.dblp.org','dblp.uni-trier.de','dblp.dagstuhl.de') or not parsed.path.startswith('/rec/'):
                raise ServiceError('source_boundary','Use a DBLP record URL or DOI')
            value=unquote(parsed.path[5:])
        if re.match(r'^(?:journals|conf|books|reference|phd|tr)/',value):
            value=re.sub(r'\.(?:html|xml|bib)$','',value)
            if not re.fullmatch(r'(?:journals|conf|books|reference|phd|tr)/[\w/.-]+',value) or '..' in value:
                raise ServiceError('invalid_target','Use a valid DBLP publication key')
        expected=None;requested_doi=None
        if re.fullmatch(r'(?:journals|conf|books|reference|phd|tr)/[\w/.-]+',value) and '..' not in value:
            expected='https://dblp.org/rec/'+quote(value,safe='/')
            pattern=f'BIND(<{expected}> AS ?publ) ?publ ?predicate ?object .'
        elif value.startswith(('10.','doi:','https://doi.org/','http://doi.org/','https://dx.doi.org/')):
            requested_doi='https://doi.org/'+quote(doi(value),safe='/')
            pattern=f'?publ <{SCHEMA}doi> ?doi_mapping . FILTER(LCASE(STR(?doi_mapping))={json.dumps(requested_doi.lower())}) ?publ ?predicate ?object .'
        else:
            query=f'SELECT ?publ ?title WHERE {{ ?publ <{SCHEMA}title> ?title . FILTER(CONTAINS(LCASE(STR(?title)), LCASE({json.dumps(target,ensure_ascii=False)}))) }} ORDER BY ?publ'
            result=self.search(query,options={},limit=20)
            return {**result,'target':target,'status':'selection_required' if result['received'] else result['status']}
        query='SELECT ?publ ?predicate ?object WHERE { '+pattern+' } ORDER BY ?publ ?predicate ?object'
        rows=[];proofs=[];errors=[];start=0
        while True:
            try:result=self.search(query,options={},start=start,limit=1000)
            except ServiceError as error:
                if not rows:raise
                errors.append(error.result);break
            page=json.loads(self.store.read(result['records']['ref'])[1]);rows.extend(page);proofs.append(result['evidence'])
            if not result['has_more']:break
            start+=len(page)
        subjects={r['publ']['value'] for r in rows}
        if any(r['publ']['type']!='uri' or r['predicate']['type']!='uri' for r in rows):
            raise ServiceError('invalid_response','Statement subjects and predicates must be RDF IRIs')
        if expected and subjects-{expected}:raise ServiceError('identity_mismatch','DBLP KG returned another record')
        if requested_doi and rows and not any(r['predicate']['value']==SCHEMA+'doi' and r['object']['value'].casefold()==requested_doi.casefold() for r in rows):
            raise ServiceError('identity_mismatch','DBLP KG statements do not identify the requested DOI')
        artifact=self.store.put(encoded(rows),'application/json',self.source,ENDPOINT,role='rdf_statements',target=target,evidence_refs=[p['ref'] for p in proofs])
        components={p:({'status':'partial' if errors else 'available' if rows else 'not_found','artifact':artifact} if p in ('metadata','export','supplementary') else {'status':'not_offered','reason':'The knowledge graph provides bibliographic statements and links, not article abstracts or full text'}) for p in parts}
        status='not_found' if not rows else 'selection_required' if len(subjects)>1 else 'partial' if errors or any(c['status'] not in ('available','not_found') for c in components.values()) else 'ok'
        return {'status':status,'source':self.source,'target':target,'records':artifact,'components':components,'statement_count':len(rows),'subjects':sorted(subjects),'errors':errors,
            'scope':'Statements about matching DBLP publications; linked entities are not recursively fetched. A missing DOI mapping is not global document absence.'}
