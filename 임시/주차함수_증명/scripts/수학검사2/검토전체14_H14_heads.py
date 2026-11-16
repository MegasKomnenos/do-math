# H14: 장 파일에서 진술 머리(라벨 포함)와 절 제목을 추출해 장별 번호를 계산한다.
import re, sys, os, json
root = r"C:\math\임시\주차함수_증명\장v2"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의|관찰|주의|예|가정|알고리즘|표|그림)\s+\{\{(\d+[AB]?):([^}]+)\}\}')
sec_re = re.compile(r'^(#+)\s+(.*)')
out = []
counters = {}
for f in files:
    p = os.path.join(root,f)
    with open(p,encoding='utf-8') as fh:
        for ln,line in enumerate(fh,1):
            m = sec_re.match(line)
            if m:
                out.append((f,ln,'SEC',m.group(1),m.group(2).strip()))
                continue
            m = head_re.match(line)
            if m:
                kind, ch, lab = m.groups()
                counters[ch] = counters.get(ch,0)+1
                # 머리 전체(첫 **...** 블록)
                mm = re.match(r'^\*\*(.*?)\*\*', line)
                head = mm.group(1) if mm else line[:200]
                out.append((f,ln,'HEAD',kind,ch,lab,counters[ch],head))
for o in out:
    print('\t'.join(str(x) for x in o))
