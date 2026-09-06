"""Check the reconstruction's document evidence, not runtime or math validity."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DRAFT=HERE.parent/'통합-설계-초안.md'
errors=[]
checks={}

def require(condition, rule, detail):
    if not condition:
        errors.append({'rule':rule,'detail':detail})

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read_json(name): return json.loads((HERE/name).read_text(encoding='utf-8'))

def prose_lines(path):
    fence=None
    for i,line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
        match=re.match(r'^\s*(`{3,}|~{3,})',line)
        if match:
            token=match[1][0]
            if fence is None: fence=token
            elif fence==token: fence=None
            yield i,''
        elif fence is None:
            yield i,line
        else:
            yield i,''
    require(fence is None,'fence_closed',str(path.relative_to(ROOT)))

baseline=read_json('기준.json')['sources']
for source in baseline:
    p=HERE/source['copy']
    require(sha(p)==source['sha256'],'baseline_hash',source['copy'])
    require(len(p.read_bytes())==source['bytes'],'baseline_bytes',source['copy'])
    require(len(p.read_text(encoding='utf-8-sig').splitlines())==source['lines'],'baseline_lines',source['copy'])
    if source['source']!='docs/do-math/통합-설계-초안.md':
        require(sha(ROOT/source['source'])==source['sha256'],'canonical_unchanged',source['source'])
checks['baseline_files']=len(baseline)

new_prose=list(prose_lines(DRAFT))
numbers=[m[1] for _,line in new_prose if (m:=re.match(r'^#{2,4} (\d+(?:\.\d+)*)(?:\.)? ',line))]
require(len(numbers)==len(set(numbers)),'unique_sections',numbers)
anchors=re.findall(r'<a id="([^"]+)"',DRAFT.read_text(encoding='utf-8'))
require(anchors==[f'd{i:02d}' for i in range(19)],'major_anchors',anchors)
for i,line in new_prose:
    for m in re.finditer(r'(?<![\w.])(\d+(?:\.\d+)*)절',line):
        require(m[1] in numbers,'section_reference',{'line':i,'section':m[1]})
checks['draft_sections']=len(numbers)

correspondence=read_json('원문대응.json')
require(correspondence['draft_sha256']==sha(DRAFT),'mapping_current_draft',correspondence['draft_sha256'])
for tag,filename,expected in [('old','기준-기존안.md',192),('draft3','기준-3차-초안.md',100)]:
    rows=[x for x in correspondence['rows'] if x['source']==tag]
    require(len(rows)==expected,'mapping_count',{'source':tag,'count':len(rows)})
    require(len({x['section'] for x in rows})==len(rows),'mapping_unique',tag)
    next_line=1
    for row in rows:
        start,end=row['lines']
        require(start==next_line and end>=start,'mapping_line_partition',row)
        next_line=end+1
        require(bool(row['rationale']),'mapping_rationale',row['section'])
        require(all(t in numbers for t in row['target_sections']),'mapping_target',row)
    require(next_line==len((HERE/filename).read_text(encoding='utf-8').splitlines())+1,'mapping_end',tag)
checks['source_clause_rows']=len(correspondence['rows'])

new_vectors=re.findall(r'^\| (V\d+) \|',DRAFT.read_text(encoding='utf-8'),re.M)
require(len(new_vectors)==len(set(new_vectors)),'vector_unique',new_vectors)
require([int(x[1:]) for x in new_vectors]==list(range(1,len(new_vectors)+1)),'vector_contiguous',new_vectors)
old_raw=(HERE/'기준-기존안.md').read_text(encoding='utf-8').splitlines()
old_vectors={re.match(r'^\| ([ISEOCTLPMD]\d+[a-z]?) \|',line)[1]:i for i,line in enumerate(old_raw,1) if re.match(r'^\| ([ISEOCTLPMD]\d+[a-z]?) \|',line)}
mapped=read_json('벡터대응.json')['vectors']
require(len(mapped)==len(old_vectors)==246,'old_vector_count',len(mapped))
require({x['id'] for x in mapped}==set(old_vectors),'vector_coverage',len(mapped))
for row in mapped:
    require(old_vectors.get(row['id'])==row['source_line'],'vector_source_line',row['id'])
    require(all(v in new_vectors for v in row['vectors']),'vector_target',row['id'])
    require(all(s in numbers for s in row['sections']),'vector_section',row['id'])
checks['old_vectors']=len(old_vectors);checks['new_vectors']=len(new_vectors)

glossary=read_json('정의대응.json')
old_terms=re.findall(r'^\*\*([^\n]+)\*\*:',(HERE/'기준-CONTEXT.md').read_text(encoding='utf-8'),re.M)
candidate_terms=re.findall(r'^\*\*([^\n]+)\*\*:',(HERE/'CONTEXT-개정안.md').read_text(encoding='utf-8'),re.M)
require({x['term'] for x in glossary['terms']}==set(old_terms),'glossary_coverage',len(old_terms))
expected={x['term'] for x in glossary['terms'] if x['disposition']!='제거'}|set(glossary['added'])
require(set(candidate_terms)==expected and len(candidate_terms)==len(expected),'glossary_candidate',len(candidate_terms))
checks['glossary_source_terms']=len(old_terms);checks['glossary_candidate_terms']=len(candidate_terms)

files=[DRAFT,HERE/'검토기록.md',HERE/'원문대응.md',HERE/'벡터대응.md',HERE/'CONTEXT-개정안.md',HERE/'지도-컨텍스트-개정안.md']
link_count=0;table_count=0
for path in files:
    raw=path.read_bytes()
    rel=str(path.relative_to(ROOT)).replace('\\','/')
    require(not raw.startswith(b'\xef\xbb\xbf') and b'\r' not in raw and raw.endswith(b'\n'),'text_encoding',rel)
    lines=list(prose_lines(path))
    for i,line in lines:
        require(line.rstrip()==line,'trailing_space',{'file':rel,'line':i})
        # Ignore code spans, where paths and normative examples are not hyperlinks.
        clean=re.sub(r'`[^`]*`','',line)
        for m in re.finditer(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',clean):
            target=m[1]
            if re.match(r'^[a-zA-Z]+://',target): continue
            part,sep,fragment=target.partition('#')
            p=(path.parent/part).resolve() if part else path
            # This invocation creates its own report after all checks. A write
            # failure raises instead of returning a successful verification.
            require(p.exists() or p==HERE/'검증.json','local_link',{'file':rel,'line':i,'target':target})
            if p.exists() and sep and fragment.startswith('d') and re.fullmatch(r'd\d\d',fragment):
                require(f'id="{fragment}"' in p.read_text(encoding='utf-8'),'local_anchor',{'file':rel,'target':target})
            link_count+=1
    j=0
    while j<len(lines):
        if not lines[j][1].startswith('|'):
            j+=1;continue
        block=[]
        while j<len(lines) and lines[j][1].startswith('|'):
            block.append(lines[j]);j+=1
        table_count+=1
        widths=[len(re.split(r'(?<!\\)\|',line))-2 for _,line in block]
        require(len(block)>=2 and re.fullmatch(r'\|(?:\s*:?-+:?\s*\|)+',block[1][1]) is not None,'table_header',{'file':rel,'line':block[0][0]})
        require(len(set(widths))==1,'table_width',{'file':rel,'line':block[0][0],'widths':sorted(set(widths))})
checks['markdown_files']=len(files);checks['local_links']=link_count;checks['tables']=table_count

patch=subprocess.run(['git','apply','--check',str(HERE/'동기화.patch')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
require(patch.returncode==0,'sync_patch_applies',patch.stderr)
checks['sync_patch_applies']=patch.returncode==0
decisions=read_json('결정.json')
pending=[key for key,value in decisions.items() if value['status']=='awaiting_user']
result={'scope':'문서·원문 대응·로컬 참조·패치 검사. 의미 검토는 검토기록, 실운전 검증은 별도다.',
        'result':'passed' if not errors else 'failed','checks':checks,'errors':errors,
        'pending_user_decisions':pending,'runtime_tests_executed':False,
        'draft':{'path':str(DRAFT.relative_to(ROOT)).replace('\\','/'),'sha256':sha(DRAFT),'bytes':len(DRAFT.read_bytes()),'lines':len(DRAFT.read_text(encoding='utf-8').splitlines())},
        'file_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files}}
(HERE/'검증.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
