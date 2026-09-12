import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from publishers import Publisher,PROFILES
from browser_adapters import KudosGateway

class ExplicitPDFContract(unittest.TestCase):
    def test_native_download_from_another_source_is_not_read_or_preserved(self):
        gateway=MagicMock(spec=KudosGateway)
        gateway.context=MagicMock()
        gateway.pages={}
        context=gateway.context
        page=MagicMock()
        download=MagicMock()
        download.url='https://other.example/paper.pdf'
        def navigate(url):
            context.on.call_args.args[1](page)
            page.on.call_args.args[1](download)
            raise RuntimeError('Synthetic download navigation')
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            adapter=Publisher(store,gateway,next(p for p in PROFILES if p.source=='project-euclid'))
            with patch.object(adapter,'document',side_effect=navigate),self.assertRaises(ServiceError) as caught:
                adapter.explicit_pdf('https://projecteuclid.org/paper.pdf',['fulltext'])
            self.assertEqual(caught.exception.result['code'],'source_boundary')
            download.path.assert_not_called()
            context.remove_listener.assert_called_once()

if __name__=='__main__':
    unittest.main()
