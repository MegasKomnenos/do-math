"""Local-browser control-flow regression using a retained genuine article PDF."""
import copy
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import recover as r

class BrowserRestartTests(unittest.TestCase):
    def test_fourth_visible_pdf_is_downloaded_after_three_nonpdf_responses(self):
        papers=list(map(json.loads,(r.BASE/r.ASSIGNMENT['members_path']).read_text(encoding='utf-8').splitlines()))
        paper=copy.deepcopy(next(p for p in papers if p['paper_id']=='VER-05eea17a72a07d16d806738b'))
        record=json.loads((r.ROOT/'results'/f"{paper['paper_id']}.json").read_text(encoding='utf-8'))
        pdf=(r.BASE/record['fulltext']['artifacts'][0]['path']).read_bytes()
        paper['paper_id']='restart-fourth-pdf-test'
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path=='/4.pdf':
                    data=pdf; kind='application/pdf'
                elif self.path=='/':
                    data=('<h1>Attribute-based encryption for circuits</h1><meta name="citation_author" content="Sergey Gorbunov; Vinod Vaikuntanathan; Hoeteck Wee"><meta name="citation_publication_date" content="2013">'+''.join(f'<a href="/{i}.pdf">PDF {i}</a>' for i in range(1,5))).encode(); kind='text/html'
                else:
                    data=b'<html><body>This observed download is not a PDF.</body></html>'; kind='text/html'
                self.send_response(200); self.send_header('Content-Type',kind); self.end_headers(); self.wfile.write(data)
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True); worker.start()
        result={'evidence':[],'attempts':[],'abstract':{'status':'unresolved'},'fulltext':{'status':'unresolved'}}
        try:
            with r.sync_playwright() as pw:
                browser=pw.chromium.launch(channel='chrome',headless=True)
                ctx=browser.new_context(); page=ctx.new_page(); page.goto(f'http://127.0.0.1:{server.server_port}/')
                r.inspect_publisher(page,paper,result)
                browser.close()
            self.assertEqual(result['fulltext']['status'],'found')
            self.assertEqual(result['pdf_candidate_visits'][0]['attempted'],4)
            self.assertEqual(result['pdf_candidate_visits'][0]['remaining'],0)
            self.assertEqual(result.get('collection_metrics',{}).get('download_requests'),4)
            self.assertEqual(result.get('collection_metrics',{}).get('publisher_visits'),1)
        finally:
            server.shutdown(); server.server_close()

    def test_article_anchor_same_and_new_tab_navigation(self):
        with r.sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            ctx=browser.new_context()
            for mode in ('',' target="_blank"'):
                page=ctx.new_page()
                page.set_content('<a href="about:blank#publisher"'+mode+'>Article</a>')
                destination=r.click_article(page,page)
                self.assertIsNotNone(destination)
                self.assertIn('#publisher',destination.url)
                self.assertEqual(destination is page,not bool(mode))
                for p in list(ctx.pages):p.close()
            browser.close()

if __name__=='__main__':unittest.main()
