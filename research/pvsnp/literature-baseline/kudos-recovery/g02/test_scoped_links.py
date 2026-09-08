import json,unittest
from pathlib import Path
from scoped_links import select_links,download_kind,public_link
from test_scope_prune import frozen_record
BASE=Path(__file__).resolve().parents[2]
FX=BASE/'intake/kudos-recovery/g02/fixtures'
class ScopedLinksTests(unittest.TestCase):
 def test_actual_open_access_author_information_is_not_a_download_control(self):
  r=json.loads((FX/'degruyter-target-control-live-1d2667671617383a.json').read_text(encoding='utf-8'));selected=select_links(r['all_links'],r['url'])
  self.assertTrue(any('/9783110278606.1/pdf' in v['url'] for v in selected));self.assertFalse(any('/publishing/' in v['url'] for v in selected))
 def test_state_controls_are_excluded_and_public_query_is_redacted(self):
  v={'text':'Save chapter','url':'https://publisher.example/save?doi=10.1000%2Fpaper&_csrf=fixture-only'}
  self.assertEqual(select_links([v]),[]);clean=public_link(v);self.assertNotIn('_csrf',clean['url']);self.assertIn('doi=',clean['url'])
 def test_actual_wiley_reference_parameter_is_not_fulltext_scope(self):
  r=frozen_record('VER-04473799966c247455ae8aeb');t=next(t for t in r['work_state']['tasks'] if 'linkLocation=Reference' in t['target'])
  self.assertEqual(select_links([{'text':'Full Text','url':t['target']}]),[])
 def test_actual_springer_reference_article_links_are_excluded(self):
  r=json.loads((FX/'springer-scope-links-5f3a22b10ef1df0e.json').read_text(encoding='utf-8'));selected=select_links(r['links'],r['url'])
  self.assertFalse(any('10511970.2015.1047545' in v['url'] for v in selected));self.assertFalse(any(v.get('excluded_context') for v in selected))
 def test_actual_perlego_recommended_pdf_slugs_are_not_downloads(self):
  r=json.loads((FX/'perlego-scope-links-7f69469cc25518e4.json').read_text(encoding='utf-8'));selected=select_links(r['links'],r['url'])
  self.assertFalse(any('/book/' in v['url'] and '/737286/' not in v['url'] for v in selected));self.assertEqual(download_kind({'text':'Read this book','url':r['url']}),'source')
 def test_global_ftp_pdf_directories_and_archives_are_not_target_files(self):
  links=[{'text':'Bulk download','url':'https://europepmc.org/ftp/pdf/'},{'text':'PMC2039864.zip','url':'https://europepmc.org/ftp/pdf/PMCxxxx204/PMC2039864.zip'}]
  self.assertEqual(select_links(links,'https://europepmc.org/articles/PMC123456'),[])
 def test_target_pdf_and_doi_controls_do_not_require_pdf_extension(self):
  links=[{'text':'View PDF','url':'https://www.sciencedirect.com/science/article/pii/0022247X86903410/pdf'},{'text':'Download chapter','url':'https://www.degruyterbrill.com/document/doi/10.1515/9783110278606.1/pdf?licenseType=open-access'},{'text':'Download full issue PDF','url':'https://journal.example/issue/download?id=123'}]
  self.assertEqual(select_links(links),links)
 def test_actual_whole_book_download_is_preserved(self):
  r=json.loads((FX/'whole-book-control-dbf7894651333359.json').read_text(encoding='utf-8'))
  links=r if isinstance(r,list) else r.get('links',[])
  full=[v for v in links if 'Download book PDF' in v.get('text','')]
  self.assertTrue(full);self.assertEqual(select_links(full),full)
if __name__=='__main__':unittest.main()
