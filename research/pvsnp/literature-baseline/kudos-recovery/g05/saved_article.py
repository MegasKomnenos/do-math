"""Rebuild exact observed MathML and image resources from preserved browser evidence."""
import base64,json,re
from collect import BASE,WORK,artifact
import fulltext_html,resource_snapshot

def restore_saved_math(fragment,proof):
    inputs=proof.get('math_inputs',[])
    pattern=r'<mjx-container\b[^>]*>.*?</mjx-container>'
    if proof.get('missing_math') or len(re.findall(r'<mjx-container\b',fragment))!=len(inputs) or len(re.findall(pattern,fragment,re.S))!=len(inputs):raise ValueError('Missing or ambiguous original MathML mapping')
    if any(item.get('input')!='MathML' or not re.match(r'^\s*<math\b',item.get('math','')) for item in inputs):raise ValueError('Unsupported original math input')
    source=iter(inputs)
    return re.sub(pattern,lambda match:next(source)['math'],fragment,flags=re.S)

def build(pid):
    record=json.loads((WORK/'results'/f'{pid}.json').read_text());root=BASE/'intake/kudos-recovery/g05'/pid
    observed=json.loads((root/'article-source-observation.json').read_text());parts={}
    if observed.get('resource_errors'):raise ValueError('Unresolved resource capture')
    for part,proof in observed['math_recovery'].items():
        raw=(root/f'article-source-{part}.html').read_text();value=restore_saved_math(raw,proof)
        if part in {'body','abstracts'}:
            images=[]
            for index in range(len(re.findall(r'<img\b',value))):
                name=f'article-{part}-image-{index}.bin'
                entries=[e for e in record['evidence'] if e.get('kind')=='actual-article-image-response' and (BASE/e['path']).name==name]
                if len(entries)!=1:raise ValueError('Image source artifact is ambiguous')
                entry=entries[0];images.append({'data_uri':'data:'+entry['media_type']+';base64,'+base64.b64encode((BASE/entry['path']).read_bytes()).decode()})
            value=resource_snapshot.embed_images(value,images)
        parts[part]=value
    title=record['metadata']['title'];document=fulltext_html.document(title,parts)
    import html
    document=document.replace('<h1>'+html.escape(title)+'</h1>','<h1>'+parts['title_html']+'</h1>',1)
    item=artifact(pid,'saved-publisher-fulltext.html',document,observed['url'],'text/html','pending-full-html-validation')
    return item,observed

if __name__=='__main__':
    import sys
    item,observed=build(sys.argv[1]);print(json.dumps({'artifact':item,'math_count':observed['math_count'],'reference_count':observed['reference_count'],'image_dimensions':observed['image_dimensions']},ensure_ascii=False))
