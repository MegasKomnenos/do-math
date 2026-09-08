"""Preserve verified publisher article DOM; unresolved external resources stay open."""
import html,re

def document(title,parts):
    content=''.join(parts.values())
    if re.search(r'<(?:iframe|video|audio|object|embed|source|mglyph)\b',content,re.I):
        raise ValueError('External or unreviewed media resource requires capture before standalone full text')
    for image in re.findall(r'<img\b[^>]*>',content,re.I):
        if not re.search(r'\bsrc=[\"\x27]data:image/(?:jpeg|png|gif|webp);base64,',image,re.I) or re.search(r'\bsrcset=',image,re.I):raise ValueError('External image resource requires capture')
    style="""body{max-width:1000px;margin:2rem auto;padding:1rem;line-height:1.5;font-family:serif}h1{font-size:1.8rem}h2{margin-top:1.5rem}#body .u-margin-s-bottom{margin-bottom:.8rem}.display{display:block;overflow-x:auto;margin:1rem 0}.formula{display:flex;align-items:center;gap:1rem;width:100%}.formula>.math{flex:1}.formula>.label{order:2;white-space:nowrap;margin-left:auto}math{font-size:1em}.sr-only{display:none}header svg,#references svg{display:none}button{font:inherit;color:inherit;border:0;background:none;padding:0}table{border-collapse:collapse;max-width:100%}td,th{padding:.3rem;vertical-align:top}a{color:#154c82}img{max-width:100%;height:auto}ol.references{list-style:none;padding-left:0}ol.references>li{margin-bottom:.7rem}"""
    return '<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; base-uri \'none\'; form-action \'none\'"><title>'+html.escape(title)+'</title><style>'+style+'</style></head><body><header><h1>'+html.escape(title)+'</h1>'+parts.get('author-group','')+'</header><section id="abstracts">'+parts.get('abstracts','')+'</section><main id="body">'+parts['body']+'</main><section id="references">'+parts['bibliography']+'</section></body></html>'
