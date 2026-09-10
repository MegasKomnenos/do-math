import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import Sanitizer

class EncodedDownloadURLContract(unittest.TestCase):
    def test_malformed_port_and_ipv6_do_not_break_the_source_page_or_expose_auth(self):
        for value in ['https://example.org:invalid/path?token=SYNTHETIC','https://[broken/path?token=SYNTHETIC']:
            result=Sanitizer().text('Reference '+value+' ends here')
            self.assertNotIn('SYNTHETIC',result)
            self.assertIn('Reference ',result)
            self.assertIn(' ends here',result)

    def test_tapestry_nested_signed_url_is_removed_from_the_path(self):
        value='https://www.proquest.com/docview.supplementalfiles.termsofusesupplementalfiles:downloadfile/example.PNG/image$2fpng/https:$2f$2fmedia.proquest.com$2ffile$3f_a$3dSYNTHETIC-AUTH$26_s$3dSYNTHETIC-SIGNATURE'
        for clean in [Sanitizer().url(value),Sanitizer().text('<a href="'+value+'">file</a>'),str(Sanitizer().value({'url':value}))]:
            self.assertNotIn('SYNTHETIC',clean)
            self.assertIn('example.PNG',clean)

    def test_percent_encoded_signed_path_and_unsigned_reference(self):
        signed='https://example.org/download/https%3A%2F%2Fexample.net%2Ffile%3Ftoken%3DSYNTHETIC'
        self.assertNotIn('SYNTHETIC',Sanitizer().url(signed))
        public='https://example.org/resolve/https:$2f$2fdoi.org$2f10.1234$2fexample'
        self.assertEqual(Sanitizer().url(public),public)

if __name__=='__main__':unittest.main()
