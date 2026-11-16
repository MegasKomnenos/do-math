# 검토전체6 L2: 문헌 PDF(Janson arXiv:1002.4135, Petersson 학위논문 서론)의 본문을 추출해 인용 진술을 대조한다
import sys, re
from pypdf import PdfReader
path=sys.argv[1]; pats=sys.argv[2:]
r=PdfReader(path)
txt=[]
for i,pg in enumerate(r.pages):
    try: t=pg.extract_text() or ""
    except Exception as e: t=f"<<err {e}>>"
    txt.append((i+1,t))
full="\n".join(f"@@PAGE {i}\n{t}" for i,t in txt)
for p in pats:
    for m in re.finditer(p,full):
        s=max(0,m.start()-200); e=min(len(full),m.end()+900)
        print("=== 패턴",p,"위치",m.start()); print(full[s:e]); print()
print("총 쪽수",len(r.pages))
