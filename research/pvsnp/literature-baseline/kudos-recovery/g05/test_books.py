import unittest,importlib.util,json
import book_collect

class BookSourceTests(unittest.TestCase):
    def test_actual_springer_search_is_in_run_metrics(self):
        import resume
        r=json.loads((book_collect.WORK/'results/VER-0c26fc7b79631b63b132fbae.json').read_text())
        actions=[a for a in r['attempts'] if a.get('outcome','').startswith('Actual Springer search UI')]
        self.assertGreater(len(actions),0)
        self.assertEqual(resume.count_actions(actions)['searches'],len(actions))
    def test_observed_whole_book_link_is_distinct_from_front_matter(self):
        links=[{'text':'Download chapter PDF','url':'https://link-springer-com.libproxy.knu.ac.kr/content/pdf/bfm:978-3-031-92932-8/1'}, {'text':'Download book EPUB','url':'https://link-springer-com.libproxy.knu.ac.kr/download/epub/10.1007/978-3-031-92932-8.epub'}, {'text':'Download book PDF','url':'https://link-springer-com.libproxy.knu.ac.kr/content/pdf/10.1007/978-3-031-92932-8.pdf'}]
        fn=lambda xs:xs[0]
        if importlib.util.find_spec('book_collect'):
            from book_collect import book_pdf_link
            fn=book_pdf_link
        self.assertEqual(fn(links),links[2])

if __name__=='__main__':unittest.main()
