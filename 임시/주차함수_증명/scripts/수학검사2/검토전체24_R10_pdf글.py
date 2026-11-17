# 내려받은 문헌 PDF에서 지정한 낱말 둘레의 글을 뽑는다(문헌 표의 정리 번호 확인용). 인자: PDF 경로, 찾을 낱말들.
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
path = sys.argv[1]; keys = sys.argv[2:]
try:
    import fitz
    doc = fitz.open(path); pages = [p.get_text() for p in doc]; lib = 'fitz'
except ImportError:
    from pypdf import PdfReader
    pages = [p.extract_text() or '' for p in PdfReader(path).pages]; lib = 'pypdf'
print('lib', lib, 'pages', len(pages))
for k in keys:
    for i, t in enumerate(pages):
        j = t.find(k)
        while j >= 0:
            print(f'--- p{i+1} [{k}]'); print(t[max(0, j-100):j+900].replace('\n', ' ')); 
            j = t.find(k, j+1)
            break
