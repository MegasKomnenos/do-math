# H14: 패턴 파일(한 줄에 "파일키<TAB>정규식")을 읽어 장 파일에서 찾는다. Git Bash의 역슬래시 훼손을 피하려고 패턴을 파일로 받는다.
import os, re, sys
root = r"C:\math\임시\주차함수_증명\장v2"
files = {"1":["장1.md"],"2":["장2.md"],"3":["장3.md"],"4":["장4.md"],"5A":["장5A.md"],"5B":["장5B.md"],"5":["장5A.md","장5B.md"],
         "6":["장6.md"],"7A":["장7A.md"],"7B":["장7B.md"],"7":["장7A.md","장7B.md"],"8":["장8.md"],"9":["장9.md"],"10":["장10.md"],"11":["장11.md"],
         "A":["부록A.md"],"B":["부록B.md"],"C":["부록C.md"],
         "D":[f for f in sorted(os.listdir(root)) if f.startswith("부록D")],
         "ALL":[f for f in sorted(os.listdir(root)) if f.endswith(".md")]}
pat_file = sys.argv[1]
ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 80
for line in open(pat_file, encoding='utf-8'):
    line = line.rstrip("\n")
    if not line or line.startswith("#"): continue
    key, rx = line.split("\t", 1)
    r = re.compile(rx)
    print(f"=== [{key}] {rx}")
    n = 0
    for f in files[key]:
        for ln, l in enumerate(open(os.path.join(root, f), encoding='utf-8'), 1):
            for m in r.finditer(l):
                n += 1
                if n <= 12:
                    s = max(0, m.start() - ctx // 2); e = min(len(l), m.end() + ctx // 2)
                    print(f"  {f}:{ln}: …{l[s:e].strip()}…")
    print(f"  (총 {n}건)")
