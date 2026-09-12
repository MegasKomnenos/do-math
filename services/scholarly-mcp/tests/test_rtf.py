import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError,extract_artifact


class RTFExtraction(unittest.TestCase):
    def extract(self,data,**options):
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            artifact=store.put(data,'application/rtf','pqdt','https://www.proquest.com/',preserve_bytes=True)
            result=extract_artifact(store,artifact['ref'],**options)
            self.assertEqual(store.read(artifact['ref'])[1],data)
            return result

    def test_codepage_raw_bytes_unicode_fallback_and_line_window(self):
        data=br"{\rtf1\ansi\ansicpg1252\uc1 Title\par caf\'e9 "+bytes([0x96])+br" \u-10916? \u-10179?\u-8704?\par Last}"
        result=self.extract(data,start=1,count=1)
        self.assertEqual(result['unit'],'lines')
        self.assertEqual(result['items'],['café – 한 😀'])
        self.assertEqual(result['total'],3)
        self.assertEqual(result['next_start'],2)

    def test_binary_picture_braces_do_not_hide_following_text(self):
        binary=b'a{b\\c}'
        data=br'{\rtf1\ansi Before\par {\pict\pngblip\bin6 '+binary+br'}After\par End}'
        result=self.extract(data,count=10)
        self.assertEqual(result['items'],['Before','After','End'])

    def test_literal_escaped_bin_text_is_not_a_binary_control(self):
        data=br'{\rtf1\ansi Literal \\bin123 and \{braces\}.}'
        self.assertEqual(self.extract(data,count=2)['items'],[r'Literal \bin123 and {braces}.'])

    def test_truncated_binary_or_wrong_format_is_rejected(self):
        for data in (b'not RTF',br'{\rtf1 {\pict\bin100 abc}',br'{\rtf1 {\pict\bin-1 x}}'):
            with self.subTest(data=data),self.assertRaises(ServiceError) as error:
                self.extract(data,count=1)
            self.assertEqual(error.exception.result['code'],'invalid_document')

    def test_unclosed_extra_or_binary_consumed_group_delimiters_are_rejected(self):
        for data in (br'{\rtf1 Text',br'{\rtf1 Text}}',br'{\rtf1{\pict\bin5 xyz}}'):
            with self.subTest(data=data),self.assertRaises(ServiceError) as error:
                self.extract(data,count=1)
            self.assertEqual(error.exception.result['code'],'invalid_document')

    def test_invalid_unicode_controls_are_rejected_without_an_invented_uc_upper_limit(self):
        for control in (br'\u70000?',br'\u-40000?',br'\uc-1\u65?',br'\u ',br'\uc '):
            with self.subTest(control=control),self.assertRaises(ServiceError) as error:
                self.extract(br'{\rtf1 '+control+b'}',count=1)
            self.assertEqual(error.exception.result['code'],'invalid_document')
        self.assertEqual(self.extract(br'{\rtf1\uc40000 Plain}',count=1)['items'],['Plain'])


if __name__=='__main__':
    unittest.main()
