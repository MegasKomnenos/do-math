import struct
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError,extract_artifact


def chunk(name,data):
    return name+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')


def document(kind=b'DJVU',children=b''):
    return b'AT&T'+chunk(b'FORM',kind+children)


class DjVuExtraction(unittest.TestCase):
    def test_external_documents_are_rejected_before_decoder_invocation(self):
        from djvu_extract import validate_document
        for data in (document(b'DJVM',chunk(b'DIRM',b'\x01\x00\x01')),
                     document(children=chunk(b'INCL',b'../private')),
                     document(children=chunk(b'NDIR',b'private.djvu'))):
            with self.subTest(data=data),self.assertRaises(ServiceError) as error:
                validate_document(data)
            self.assertEqual(error.exception.result['code'],'external_document_components')
        validate_document(document(b'DJVM',chunk(b'DIRM',b'\x81\x00\x01')))
        validate_document(document(b'DJVM',chunk(b'DIR0',b'legacy directory')))
        validate_document(document(b'PM44'))

    def test_invalid_lengths_and_non_djvu_bytes_are_not_sent_to_decoder(self):
        from djvu_extract import validate_document
        for data in (b'<html>Error</html>',document()[:-2],document(b'WAVE'),document()+b'unexpected'):
            with self.subTest(data=data),self.assertRaises(ServiceError):validate_document(data)

    def test_exact_page_window_preserves_empty_text_and_image_provenance(self):
        import pymupdf
        from djvu_extract import pages
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);artifact=store.put(document(),'image/vnd.djvu','numdam','https://www.numdam.org/item/x',preserve_bytes=True)
            def run(tool,args,folder):
                if tool=='djvused':return b'3\n'
                if tool=='djvutxt':return b'' if '--page=2' in args else '원문3'.encode()
                with pymupdf.open() as doc:
                    doc.new_page(width=10,height=10)
                    return doc[0].get_pixmap().tobytes('ppm')
            with patch('djvu_extract.run_decoder',side_effect=run) as invoke:
                result=pages(store,artifact,document(),start=1,count=2,render=False)
            self.assertEqual([row['page'] for row in result['items']],[2,3])
            self.assertEqual(result['total'],3);self.assertIsNone(result['next_start'])
            self.assertTrue(result['items'][0]['text_layer_empty'])
            image=result['items'][0]['image'];meta,_=store.read(image['ref'])
            self.assertEqual(meta['parent_ref'],artifact['ref']);self.assertEqual(meta['page'],2)
            self.assertEqual(result['items'][1]['text'],'원문3')
            self.assertEqual(invoke.call_count,4)

    def test_extractor_dispatches_djvu_and_does_not_ignore_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);artifact=store.put(document(),'image/vnd.djvu','numdam','https://www.numdam.org/item/x',preserve_bytes=True)
            with patch('djvu_extract.pages',return_value={'status':'ok','unit':'pages'}) as extract:
                self.assertEqual(extract_artifact(store,artifact['ref'],start=2,count=1)['unit'],'pages')
                self.assertEqual(extract.call_args.kwargs,{'start':2,'count':1,'render':False})
                self.assertEqual(extract.call_args.args[1]['ref'],artifact['ref'])
            for options in ({'selection':'unoffered'},{'fields':['text']}):
                with self.assertRaises(ServiceError):extract_artifact(store,artifact['ref'],**options)

    def test_later_page_failure_keeps_completed_page_and_resume_position(self):
        from djvu_extract import pages
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);artifact=store.put(document(),'image/vnd.djvu','numdam','https://www.numdam.org/item/x',preserve_bytes=True)
            with patch('djvu_extract.run_decoder',side_effect=[b'3',b'first page',ServiceError('document_decode_timeout','Timed out')]):
                result=pages(store,artifact,document(),start=0,count=2,render=False)
        self.assertEqual(result['status'],'partial');self.assertEqual(result['returned'],1)
        self.assertEqual(result['next_start'],1);self.assertEqual(result['items'][0]['text'],'first page')
        self.assertEqual(result['errors'][0]['page'],2)

    def test_timeout_and_decoder_errors_are_classified_without_raw_stderr(self):
        import subprocess
        from djvu_extract import run_decoder
        with tempfile.TemporaryDirectory() as temp,patch('djvu_extract.decoder_path',return_value=Path(temp)/'tool.exe'):
            with patch('djvu_extract.subprocess.run',side_effect=subprocess.TimeoutExpired('tool',30)):
                with self.assertRaises(ServiceError) as error:run_decoder('djvutxt',[],Path(temp))
                self.assertEqual(error.exception.result['code'],'document_decode_timeout')
            result=subprocess.CompletedProcess([],1,stdout=b'',stderr=b'PRIVATE source data')
            with patch('djvu_extract.subprocess.run',return_value=result):
                with self.assertRaises(ServiceError) as error:run_decoder('djvutxt',[],Path(temp))
                self.assertEqual(error.exception.result['code'],'invalid_document')
                self.assertNotIn('PRIVATE',str(error.exception.result))

    def test_decoder_bytes_must_match_the_local_build_manifest(self):
        from djvu_extract import decoder_path
        from setup_djvu import UPSTREAM,COMMIT,LICENSE,TOOLS
        import os
        name='djvutxt'+('.exe' if os.name=='nt' else '')
        with tempfile.TemporaryDirectory() as temp,patch('djvu_extract.RUNTIME',Path(temp)):
            root=Path(temp);tool=root/name;tool.write_bytes(b'verified build')
            manifest={'upstream':UPSTREAM,'commit':COMMIT,'license':LICENSE,'tools':{
                t+('.exe' if os.name=='nt' else ''):{'sha256':hashlib.sha256(tool.read_bytes()).hexdigest()} for t in TOOLS}}
            (root/'provenance.json').write_text(json.dumps(manifest),encoding='utf-8')
            self.assertEqual(decoder_path('djvutxt'),tool)
            for field in ('upstream','commit','license'):
                changed={**manifest,field:'unrelated'}
                (root/'provenance.json').write_text(json.dumps(changed),encoding='utf-8')
                with self.subTest(field=field),self.assertRaises(ServiceError):decoder_path('djvutxt')
            (root/'provenance.json').write_text(json.dumps(manifest),encoding='utf-8')
            tool.write_bytes(b'changed')
            with self.assertRaises(ServiceError) as error:decoder_path('djvutxt')
            self.assertEqual(error.exception.result['code'],'decoder_not_available')


if __name__=='__main__':unittest.main()
