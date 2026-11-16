import sys
p=sys.argv[1]
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
r=PdfReader(p)
txt="\n".join((pg.extract_text() or "") for pg in r.pages[:12])
import re
for key in ["(1.9)","Theorem 1.12","Theorem 1.13","Theorem 1.14","Probability Surveys","Probab. Surveys"]:
    for m in re.finditer(re.escape(key),txt):
        s=max(0,m.start()-200); e=min(len(txt),m.end()+700)
        print("=====",key,"@",m.start()); print(txt[s:e]); print()
        break
