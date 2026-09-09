import hashlib
import re
from urllib.parse import urljoin
from html.parser import HTMLParser
from html import unescape
import pymupdf

TITLE = 'Discontinuous groups acting on homogeneous spaces of reductive type'
AUTHOR_URL = 'https://www.ms.u-tokyo.ac.jp/~toshi/pub/19.html'

def normalize(text):
    return re.sub(r'\W+', ' ', unescape(re.sub('<[^>]*>', ' ', text))).strip().casefold()

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.links=[]; self.current=None
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            self.current={'href':dict(attrs).get('href',''),'text':''}
    def handle_data(self,data):
        self.text.append(data)
        if self.current is not None: self.current['text']+=data
    def handle_endtag(self,tag):
        if tag=='a' and self.current is not None:
            self.links.append(self.current);self.current=None

def author_record(html):
    parser=PageParser();parser.feed(html)
    text = ' '.join(parser.text)
    if normalize(TITLE) not in normalize(text) or 'Kobayashi' not in text:
        return None
    link = next((a for a in parser.links if a['text'].strip() == 'preprint version(pdf)'), None)
    publication = re.search(r'World\s+Scientific,\s*(\d{4}),\s*pp\.\s*(\d+)-(\d+)', text)
    if link is None or publication is None:
        return None
    return {'title':TITLE, 'authors':['Toshiyuki Kobayashi'], 'year':None,
            'pdf_url':urljoin(AUTHOR_URL, link['href']), 'record_type':'preprint',
            'related_publication':{'year':int(publication[1]),'pages':publication[2]+'-'+publication[3],
                                   'relation':'same_work_different_version'}}

def inspect_pdf(data):
    result = {'pages':0, 'target_preprint':False, 'has_abstract_heading':False}
    if not data.startswith(b'%PDF-'):
        return result
    with pymupdf.open(stream=data, filetype='pdf') as doc:
        if doc.needs_pass:
            return result
        texts = [p.get_text() for p in doc]
        result.update(pages=len(doc), first_page=texts[0], last_page=texts[-1],
                      page_text_lengths=[len(t) for t in texts], sha256=hashlib.sha256(data).hexdigest(),
                      has_abstract_heading=any(re.search(r'^\s*(abstract|summary)\s*[:.]?\s*$',t,re.I|re.M) for t in texts))
        result['target_preprint'] = (len(doc)==26 and normalize(TITLE) in normalize(texts[0])
            and 'Toshiyuki KOBAYASHI' in texts[0] and texts[-1].strip().endswith('26')
            and all(len(t)>50 for t in texts))
    return result

def assess_search(data):
    docs = data['documents']
    if data['record_count'] != len(docs):
        raise ValueError('Unvisited result pages remain')
    result=[]
    for doc in docs:
        same=normalize(doc.get('title','')) == normalize(TITLE)
        is_toc=any('The Table of Contents for the book is as follows:' in a.get('abstract','') for a in doc.get('abstracts',[]))
        result.append({'same_title':same,'preprint_abstract':False,
                       'reason':('Same title is insufficient to identify the undated 26-page preprint; no target preprint abstract established.' if same else
                                 'Different title; book table of contents is not this preprint abstract.' if is_toc else
                                 'Different title and publication; not the registered preprint.'),
                       'id':doc.get('id'),'abstract_value_count':len(doc.get('abstracts',[]))})
    return result

def safe_search(data):
    allowed = {'id','title','full_title','authors','publication_years','publication_title','start_pages','end_pages',
               'page_counts','dois','abstracts','content_type'}
    query=data.get('query',{})
    return {'record_count':data['record_count'], 'page_count':data['page_count'],
            'query':{k:query.get(k) for k in ['original_query','page_number','page_size','query_string']},
            'documents':[{k:v for k,v in doc.items() if k in allowed} for doc in data['documents']]}
