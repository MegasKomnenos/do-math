import importlib.util,json,unittest
from pathlib import Path
from collect import BASE,WORK
ROOT=BASE/'intake/kudos-recovery/g05/VER-022f997d68492e3705be19c6'
class ResourceSnapshotTests(unittest.TestCase):
    def test_actual_title_script_order_uses_original_mathml_dom(self):
        from playwright.sync_api import sync_playwright
        from collect import norm
        import resource_snapshot
        root=BASE/'intake/kudos-recovery/g05/VER-0500a5b14fb9aea2d4cf5f0f'
        proof=json.loads((root/'article-source-observation.json').read_text());raw=(root/'article-source-title_html.html').read_text()
        with sync_playwright() as pw:
            browser=pw.firefox.launch(headless=True);page=browser.new_page();page.set_content('<h1>'+raw+'</h1>')
            page.evaluate('(inputs)=>{const roots=Array.from(document.querySelectorAll("mjx-container"));window.MathJax={startup:{document:{math:inputs.map((x,i)=>({math:x.math,inputJax:{name:x.input},typesetRoot:roots[i]}))}}}}',proof['math_recovery']['title_html']['math_inputs'])
            result=resource_snapshot.snapshot(page.locator('h1'));browser.close()
        self.assertEqual(norm(result.get('text','')),norm(proof['metadata']['citation_title'][0]))
    def test_actual_figure_selection_excludes_thumbnail_and_telemetry(self):
        observed=json.loads((ROOT/'mathjax-observation.json').read_text())
        if importlib.util.find_spec('resource_snapshot'):
            from resource_snapshot import selected_image_assets
            assets=selected_image_assets(observed['images'],observed['image_assets'])
        else:assets=observed['image_assets']
        self.assertEqual(len(assets),1);self.assertEqual(assets[0]['media_type'],'image/jpeg');self.assertTrue(assets[0]['url'].endswith('-gr1.jpg'))
    def test_actual_figure_bytes_are_embedded_without_remote_src(self):
        import base64,resource_snapshot
        data=(ROOT/'article-observed-figure-48b71ddae3806c45.jpg').read_bytes();uri='data:image/jpeg;base64,'+base64.b64encode(data).decode()
        original='<figure><img src="https://ars-els--cdn-com.libproxy.knu.ac.kr/content/image/1-s2.0-S1572528623000634-gr1.jpg" height="208" alt=""><figcaption>Figure 1</figcaption></figure>'
        value=getattr(resource_snapshot,'embed_images',lambda text,items:text)(original,[{'data_uri':uri}])
        self.assertIn(uri,value);self.assertNotIn('src="https:',value);self.assertIn('Figure 1',value)
    def test_mathjax_clone_uses_actual_original_mathml_input(self):
        from playwright.sync_api import sync_playwright
        observed=json.loads((ROOT/'mathjax-observation.json').read_text());source=observed['first'][0]['math']
        raw=next(p.read_text() for p in ROOT.glob('article-source-abstracts*.html') if '<mjx-container' in p.read_text())
        with sync_playwright() as pw:
            b=pw.firefox.launch(headless=True);p=b.new_page();p.set_content(raw)
            p.evaluate('(math)=>{const old=document.querySelector("mjx-container").outerHTML;document.body.innerHTML="<div id=root>"+old+"</div>";window.MathJax={startup:{document:{math:[{math:math,inputJax:{name:"MathML"},typesetRoot:document.querySelector("mjx-container")}]}}}}',source)
            if importlib.util.find_spec('resource_snapshot'):
                from resource_snapshot import snapshot
                result=snapshot(p.locator('#root'))
            else:result={'html':p.locator('#root').inner_html(),'missing_math':0}
            b.close()
        self.assertNotIn('<mjx-container',result['html']);self.assertIn(source,result['html']);self.assertEqual(result['missing_math'],0)
if __name__=='__main__':unittest.main()
