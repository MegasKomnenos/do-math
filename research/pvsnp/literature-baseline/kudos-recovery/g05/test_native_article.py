import importlib.util,json,unittest
from pathlib import Path
from collect import BASE,WORK
ROOT=BASE/'intake/kudos-recovery/g05/VER-2bb97c857e10d1adb8a73f9a'
class NativeArticleTests(unittest.TestCase):
    def test_offline_check_validates_embedded_actual_figure(self):
        import base64,tempfile,native_article
        from playwright.sync_api import sync_playwright
        data=(BASE/'intake/kudos-recovery/g05/VER-022f997d68492e3705be19c6/article-observed-figure-48b71ddae3806c45.jpg').read_bytes()
        with tempfile.TemporaryDirectory(dir=WORK/'tdd') as folder:
            path=Path(folder)/'figure.html';path.write_text('<div id="body"><h2>1. Introduction</h2><img src="data:image/jpeg;base64,'+base64.b64encode(data).decode()+'"></div><div id="references"><ol class="references"><li>Reference</li></ol></div>')
            with sync_playwright() as pw:
                browser=pw.firefox.launch(headless=True);context=browser.new_context()
                result=native_article.offline_check(context,{'path':path.relative_to(BASE).as_posix()},{'math_count':0,'headings':['1. Introduction'],'reference_count':1,'image_count':1,'image_dimensions':[[640,208]]})
                browser.close()
            self.assertTrue(result['passed']);self.assertEqual(result['image_dimensions'],[[640,208]])
    def functions(self):
        if importlib.util.find_spec('native_article'):
            import native_article
            return native_article.binding,native_article.layout_ready
        return lambda *args:False,lambda *args:False
    def test_actual_publisher_identity_uses_byline_not_reference_mentions(self):
        record=json.loads((WORK/'results/VER-2bb97c857e10d1adb8a73f9a.json').read_text());metadata=json.loads((ROOT/'native-publisher-metadata.json').read_text());binding,_=self.functions()
        self.assertTrue(binding(record['metadata'],metadata,'Reachability in arborescence packings','Florian Hörsch a, Zoltán Szigeti b'))
        self.assertFalse(binding(record['metadata'],dict(metadata,citation_doi=['10.1016/unrelated']),'Reachability in arborescence packings','Florian Hörsch a, Zoltán Szigeti b'))
        self.assertFalse(binding(record['metadata'],metadata,'Reachability in arborescence packings','Unrelated Author'))
    def test_actual_complete_body_is_not_abstract_only_or_section_snippets(self):
        _,layout=self.functions();body=(ROOT/'source-dom-body.html').read_text();refs=(ROOT/'source-dom-bibliography.html').read_text();text=(ROOT/'full-html-probe-body.txt').read_text()
        self.assertTrue(layout(text,body,refs,['1. Introduction','Acknowledgment']))
        self.assertFalse(layout(text,'',refs,[]))
        self.assertFalse(layout(text+'\nSection snippets',body,refs,['1. Introduction']))
        self.assertFalse(layout(text,body,'',['1. Introduction']))
    def test_actual_mathjax_html_requires_original_math_recovery(self):
        import native_article
        root=BASE/'intake/kudos-recovery/g05/VER-022f997d68492e3705be19c6'
        body=max(root.glob('article-source-body*.html'),key=lambda p:p.stat().st_mtime).read_text()
        self.assertIn('<mjx-container',body)
        self.assertTrue(getattr(native_article,'requires_mathml_recovery',lambda value:False)(body))
    def test_reference_queries_are_preserved_while_authentication_queries_are_redacted(self):
        import native_article
        value='<a href="https://scholar.google.com/scholar_lookup?title=Matroid&amp;author=Szigeti">ref</a><a href="https://example.org/paper.pdf?md5=synthetic-secret&amp;pid=target.pdf">PDF</a><a href="https://example.org/save-research?_csrf=synthetic-csrf">Save</a>'
        result=getattr(native_article,'public_fragment',lambda x:x)(value)
        self.assertIn('title=Matroid&amp;author=Szigeti',result);self.assertIn('pid=target.pdf',result)
        self.assertNotIn('synthetic-secret',result);self.assertNotIn('synthetic-csrf',result)
    def test_capture_roundtrip_uses_actual_dom_fragments_and_offline_validation(self):
        import copy,hashlib,tempfile,html
        from unittest.mock import patch
        from playwright.sync_api import sync_playwright
        import native_article
        r=json.loads((WORK/'results/VER-2bb97c857e10d1adb8a73f9a.json').read_text());r['fulltext']={'status':'unresolved','reason':'test copy'};r['identity']={'status':'unresolved','reason':'test copy'};r['abstract']={'status':'unresolved','reason':'test copy'}
        meta=json.loads((ROOT/'native-publisher-metadata.json').read_text())
        parts={name:(ROOT/f'source-dom-{name}.html').read_text() for name in ['body','abstracts','author-group','bibliography']}
        tags=''.join('<meta name="'+key+'" content="'+html.escape(value,quote=True)+'">' for key,values in meta.items() for value in values)
        fixture='<html><head>'+tags+'</head><body><h1>Reachability in arborescence packings</h1><div>Full text access</div>'+''.join('<div id="'+ident+'">'+parts[name]+'</div>' for ident,name in [('author-group','author-group'),('abstracts','abstracts'),('body','body'),('references','bibliography')])+'</body></html>'
        with tempfile.TemporaryDirectory(dir=WORK/'tdd') as folder:
            folder=Path(folder);source=folder/'source.html';source.write_text(fixture,encoding='utf-8')
            def save(pid,name,data,url,media='text/plain',kind=None):
                path=folder/name;blob=data if isinstance(data,bytes) else data.encode();path.write_bytes(blob)
                return {'path':path.relative_to(BASE).as_posix(),'sha256':hashlib.sha256(blob).hexdigest(),'url':url,'media_type':media,'kind':kind}
            with sync_playwright() as pw:
                browser=pw.firefox.launch(headless=True);context=browser.new_context();page=context.new_page();page.goto(source.as_uri())
                page.evaluate('(value)=>{const node=document.querySelector("#body");node.innerHTML="Loading...";setTimeout(()=>node.innerHTML=value,1200)}',parts['body'])
                with patch.object(native_article,'artifact',save,create=True):
                    fn=getattr(native_article,'capture',lambda *args:{'status':'unimplemented'});result=fn(context,page,dict(r['metadata'],paper_id=r['paper_id']),r)
                browser.close()
            self.assertEqual(result['status'],'needs_review',result)
            self.assertIn('math/figure resources',result['reason']);self.assertEqual(r['identity']['status'],'confirmed');self.assertEqual(r['abstract']['status'],'found')
            self.assertEqual(r['fulltext']['status'],'unresolved')
if __name__=='__main__':unittest.main()
