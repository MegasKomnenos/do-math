# T14: 2–5장·11장에서 글자체 명령 없이 쓰인 대문자 N의 자리(1.1 환경 크기 N·6절 예약과의 대조)
import re, os
root = r"C:\math\임시\주차함수_증명\장v2"
pat = re.compile(r'(?<!\\mathfrak )(?<!\\mathcal )(?<!\\mathsf )(?<!\\mathrm )(?<!\\mathbb )(?<!\\mathfrak\{)(?<!\\mathcal\{)(?<![A-Za-z\\{])N(?![A-Za-z])')
for f in ["장2.md", "장3.md", "장4.md", "장5A.md", "장5B.md", "장11.md"]:
    t = open(os.path.join(root, f), encoding='utf-8').read()
    hits = [(t[:m.start()].count('\n') + 1, t[max(0, m.start() - 60):m.end() + 30].replace('\n', ' ')) for m in pat.finditer(t)]
    print(f, len(hits))
    seen = set()
    for ln, ctx in hits:
        if ln in seen: continue
        seen.add(ln); print("   ", ln, repr(ctx))
