"""Deterministic content checks limited to tested retained source structures."""
import hashlib
import json
import re
import sys
from pathlib import Path
import fitz
import recover as r
sys.path.insert(0,str(r.ROOT.parent))
import work_queue as w

def text(asset):
    path=r.BASE/asset['path']
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=asset['sha256']:
        raise ValueError('Artifact digest mismatch: '+asset['path'])
    return data.decode('utf-8')

def assess(record,paper):
    reviews={}
    code_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    def review(component,reason,paths):
        reviews[component]={'basis_sha256':w.component_basis(record,component),'reason':reason,'evidence_paths':list(dict.fromkeys(paths)),'rule_code_sha256':code_sha,'test':'kudos-recovery/g08/test_content_review.py'}
    for asset in reversed(record['evidence']):
        if asset.get('kind')=='mr-scoped-bibliography':
            body=text(asset)
            lines=body.splitlines()
            if lines and r.bind_mr(paper,lines[0],'\n'.join(lines[1:])) and record['identity']['status']=='confirmed':
                review('identity','Retained per-record MR heading number, normalized complete target title, every named author and input year pass bind_mr; grouped review sections are scoped independently.',[asset['path']])
            break
    if 'identity' not in reviews:
        return reviews
    for asset in record.get('fulltext',{}).get('artifacts',[]):
        if asset.get('media_type')!='application/pdf' or record['fulltext']['status']!='found':
            continue
        data=(r.BASE/asset['path']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=asset['sha256'] or not r.valid_pdf(data):
            continue
        with fitz.open(stream=data,filetype='pdf') as doc:
            front='\n'.join(p.get_text() for p in list(doc)[:3])
            last=doc[-1].get_text()
            expected=paper.get('publication',{}).get('pages') or ''
            span=re.fullmatch(r'(\d+)\s*[-–]+\s*(\d+)',expected)
            # Books, scans and uncertain page ranges require direct review.
            if paper.get('record_type') in {'book','proceedings'} or not span:
                continue
            if len(doc)<int(span[2])-int(span[1])+1 or not last.strip():
                continue
            if r.normalize_title(r.plain_title(paper['title'])) in r.normalize_title(front) and all(r.author_matches(a,front) for a in r.named_authors(paper)):
                review('fulltext','PDF opens; first three pages contain the complete normalized target title and all named authors; numeric expected page span is covered and last page has readable content. MR scoped identity independently confirms the target edition.',reviews['identity']['evidence_paths']+[asset['path']])
    if record['abstract']['status']=='found':
        assets=record['abstract'].get('artifacts',[])
        if len(assets)==1 and assets[0].get('media_type','text/plain')=='text/plain':
            value=text(assets[0]).strip()
            norm=lambda s:re.sub(r'\s+',' ',s).strip()
            if len(value)>80 and not r.abstract_quality_issue(value):
                for source in record['evidence']:
                    if source.get('media_type','text/plain')!='text/plain':continue
                    body=text(source)
                    summary=r.abstract_from_review(body) if source.get('kind')=='review' else None
                    if (summary and norm(summary)==norm(value) and not record.get('review',{}).get('grouped')) or (source.get('url')==assets[0].get('url') and re.search(r'\bAbstract\b',body) and norm('Abstract '+value) in norm(body)):
                        review('abstract','Saved complete text exactly matches the explicit source Abstract boundary or ungrouped, explicitly labelled quoted Summary; source and MR identity were independently checked.',reviews['identity']['evidence_paths']+[source['path'],assets[0]['path']])
                        break
                if 'abstract' not in reviews:
                    for source in record['evidence']:
                        if source.get('kind')!='ui-search-response':continue
                        payload=json.loads(text(source))
                        for doc in r.response_documents(paper,payload):
                            if any(norm(a.get('abstract',''))==norm(value) for a in doc.get('abstracts') or []) and paper.get('record_type') not in {'book','proceedings'}:
                                review('abstract','Exact retained UI-response abstract matches verified title, authors, year, available DOI and page boundaries. Source is a database indexing abstract; this rule excludes books pending type/content review.',reviews['identity']['evidence_paths']+[source['path'],assets[0]['path']])
    return reviews
