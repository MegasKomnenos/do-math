from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ServiceError
from web_documents import public_document_hosts

class PublicDocumentContract(unittest.TestCase):
    def test_public_target_rejects_local_private_and_credential_urls(self):
        for address in ('127.0.0.1','10.0.0.1','169.254.169.254','::1'):
            with patch('socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(address,443))]):
                with self.assertRaises(ServiceError) as error:
                    public_document_hosts('https://author.example/paper.pdf')
                self.assertEqual(error.exception.result['code'],'source_boundary')
        for target in ('file:///C:/math/.credentials/kudos.md','https://user:password@author.example/paper.pdf'):
            with self.assertRaises(ServiceError):
                public_document_hosts(target)

if __name__=='__main__':
    unittest.main()
