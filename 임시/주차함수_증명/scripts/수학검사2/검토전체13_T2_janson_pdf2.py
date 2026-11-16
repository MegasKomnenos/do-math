import sys,re
from pypdf import PdfReader
r=PdfReader(sys.argv[1])
txt="\n".join((pg.extract_text() or "") for pg in r.pages)
i=txt.find("(1.8)"); print(txt[max(0,i-1500):i+100]); print("=========")
for m in re.finditer(r"\[24\]",txt):
    pass
j=txt.rfind("[24]"); print(txt[j-100:j+400]); print("=========")
k=txt.find("Probab"); print(txt[:600])
