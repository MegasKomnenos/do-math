import sys
p=sys.argv[1]
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
r=PdfReader(p)
out=[]
for i in range(min(14,len(r.pages))):
    out.append(f"=== page {i+1} ===\n"+(r.pages[i].extract_text() or ""))
open(sys.argv[2],"w",encoding="utf-8").write("\n".join(out))
print(len(r.pages))
