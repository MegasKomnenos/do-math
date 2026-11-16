# -*- coding: utf-8 -*-
"""S14: 장 파일의 진술 머리를 뽑아 라벨·종류·이름·지위·절·현재 번호를 TSV로 쓴다.
현재 번호는 장 안에서 머리 순서로 센다(조립기와 같은 규칙으로 가정; 대응표 머리말)."""
import re, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명\장v2")
FILES = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
HEAD = re.compile(r'^\*\*(정리|정의|보조정리|명제|따름정리) \{\{(\d+):([^}]+)\}\}(?!의 증명)(.*?)\*\*')
SEC = re.compile(r'^(#{2,4}) (\d+(?:\.\d+)*)\s*(.*)')
rows = []
counter = {}
for f in FILES:
    sec = ''
    for ln, line in enumerate((ROOT/f).read_text(encoding='utf-8').splitlines(), 1):
        m = SEC.match(line)
        if m:
            sec = m.group(2); continue
        m = HEAD.match(line)
        if m:
            kind, ch, lab, rest = m.groups()
            ch = int(ch)
            counter[ch] = counter.get(ch, 0) + 1
            name = ''
            status = ''
            r = rest.strip()
            if '[' in r:
                head_part, br = r.rsplit('[', 1)
                status = br.rstrip('.').rstrip().rstrip(']')
                head_part = head_part.strip()
            else:
                head_part = r.rstrip('.').strip()
            if head_part.startswith('(') and head_part.endswith(')'):
                name = head_part[1:-1]
            rows.append((f, ln, kind, f"{ch}:{lab}", name, status, sec, f"{ch}.{counter[ch]}"))
out = pathlib.Path(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_S14_heads.tsv")
with out.open('w', encoding='utf-8') as fh:
    for r in rows:
        fh.write('\t'.join(str(x) for x in r) + '\n')
print(len(rows), {k: v for k, v in sorted(counter.items())})
