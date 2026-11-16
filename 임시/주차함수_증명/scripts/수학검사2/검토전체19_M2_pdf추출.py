import sys
from pypdf import PdfReader
src, dst = sys.argv[1], sys.argv[2]
r = PdfReader(src)
with open(dst, 'w', encoding='utf-8') as f:
    for i, pg in enumerate(r.pages):
        f.write(f'\n===== PAGE {i+1} =====\n')
        try:
            f.write(pg.extract_text() or '')
        except Exception as e:
            f.write(f'[extract error {e}]')
print('pages', len(r.pages))
