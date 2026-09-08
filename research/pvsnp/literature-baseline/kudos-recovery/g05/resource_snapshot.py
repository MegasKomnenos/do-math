"""Preserve publisher math inputs and only images actually used by the article DOM."""

def selected_image_assets(images,assets):
    selected=[];seen=set();wanted={item['src'] for item in images}
    for asset in assets:
        if asset.get('url') in wanted and asset['url'] not in seen:
            seen.add(asset['url']);selected.append(asset)
    return selected

SNAPSHOT_JS=r'''(element)=>{
 const clone=element.cloneNode(true);let items=[];
 try{items=Array.from(window.MathJax.startup.document.math)}catch(error){}
 const mapping=new Map(items.map(item=>[item.typesetRoot,item]));
 const original=Array.from(element.querySelectorAll('mjx-container'));
 const copied=Array.from(clone.querySelectorAll('mjx-container'));
 let missing=0;const inputs=[];
 original.forEach((node,index)=>{
   const item=mapping.get(node);
   if(!item||item.inputJax?.name!=='MathML'||typeof item.math!=='string'||!/^\s*<math\b/.test(item.math)){missing++;return}
   const template=document.createElement('template');template.innerHTML=item.math;
   const math=template.content.firstElementChild;
   if(!math||math.localName!=='math'){missing++;return}
   copied[index].replaceWith(math);inputs.push({input:'MathML',math:item.math});
 });
 return {html:clone.innerHTML,text:clone.textContent,missing_math:missing,restored_math:inputs.length,math_inputs:inputs,math_count:clone.querySelectorAll('math').length,original_chtml:original.length};
}'''

def snapshot(locator):
    return locator.evaluate(SNAPSHOT_JS)

def watch_images(page):
    """Retain response handles; read bytes only for exact, used DOM resources."""
    responses={}
    def observed(response):
        if response.status==200 and response.headers.get('content-type','').startswith('image/'):
            responses[response.url]=response
    page.on('response',observed)
    page._article_image_responses=responses

def image_resources(node,page):
    import base64
    from playwright.sync_api import TimeoutError
    for image in node.locator('img').all():
        image.scroll_into_view_if_needed()
    if node.locator('img').count():
        try:page.wait_for_function('(node)=>Array.from(node.querySelectorAll("img")).every(e=>e.complete&&e.naturalWidth>0&&e.naturalHeight>0)',arg=node.element_handle(),timeout=15000)
        except TimeoutError:raise ValueError('Article image has not loaded')
    images=node.locator('img').evaluate_all('(es)=>es.map(e=>({src:e.currentSrc,width:e.naturalWidth,height:e.naturalHeight}))')
    result=[]
    for image in images:
        response=getattr(page,'_article_image_responses',{}).get(image['src'])
        if response is None:raise ValueError('No observed browser response for article currentSrc')
        media=response.headers.get('content-type','').split(';')[0]
        if media not in {'image/jpeg','image/png','image/gif','image/webp'}:raise ValueError('Unsupported article image media')
        data=response.body()
        result.append(dict(image,data=data,media_type=media,data_uri='data:'+media+';base64,'+base64.b64encode(data).decode()))
    return result


import re,html

def embed_images(fragment,images):
    position=0
    def replace(match):
        nonlocal position
        if position>=len(images):raise ValueError('Missing article image resource')
        data=images[position]['data_uri'];position+=1
        if not re.match(r'^data:image/(?:jpeg|png|gif|webp);base64,',data):raise ValueError('Unsupported or external image resource')
        tag=re.sub(r'\s+(?:src|srcset|data-src|data-srcset|loading)\s*=\s*([\"\x27]).*?\1','',match[0],flags=re.I)
        return tag[:-1]+' src="'+html.escape(data,quote=True)+'">'
    value=re.sub(r'<img\b[^>]*>',replace,fragment,flags=re.I)
    if position!=len(images):raise ValueError('Image resource count mismatch')
    return re.sub(r'<source\b[^>]*>','',value,flags=re.I)
