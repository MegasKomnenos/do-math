import sys
path=sys.argv[1]
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
r=PdfReader(path)
txt="\n".join((pg.extract_text() or "") for pg in r.pages)
open(sys.argv[2],"w",encoding="utf-8").write(txt)
print(len(r.pages), len(txt))
