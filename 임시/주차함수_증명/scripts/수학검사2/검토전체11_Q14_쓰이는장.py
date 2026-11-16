# Q14: 장부 1.2 전역 기호의 「쓰이는 장」·「정의 절」을 장 파일에서 다시 센다(자리 찾기용; 판정은 손으로).
import re, os
root = r"C:\math\임시\주차함수_증명"
chap_files = {"1":["장1.md"],"2":["장2.md"],"3":["장3.md"],"4":["장4.md"],"5":["장5A.md","장5B.md"],"6":["장6.md"],"7":["장7A.md","장7B.md"],"8":["장8.md"],"9":["장9.md"],"10":["장10.md"],"11":["장11.md"]}
def norm(s): return re.sub(r'\s+', '', s)
texts = {}
for ch, fl in chap_files.items():
    t = ""
    for f in fl: t += open(os.path.join(root,"장v2",f), encoding="utf-8").read()
    texts[ch] = norm(t)
# also appendix D per chapter? not counted (장부 says 본문); keep separate
lines = open(os.path.join(root,"장부_v2.md"), encoding="utf-8").read().splitlines()
in12=False
def key_of(sym):
    s = sym.strip().strip('$')
    s = norm(s)
    # take first symbol if comma separated at top level
    depth=0; out=""
    for chh in s:
        if chh in '{(' : depth+=1
        if chh in '})' : depth-=1
        if chh==',' and depth==0: break
        out+=chh
    s=out
    # drop argument parentheses at end
    s = re.sub(r'\([^()]*\)$', '', s)
    # drop := definitions
    s = s.split(':=')[0].split('=')[0]
    return s
for ln,line in enumerate(lines,1):
    if line.startswith("### 1.2"): in12=True
    elif line.startswith("### 1.3"): in12=False
    if not in12: continue
    m = re.match(r'^\| (\$.*?\$) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
    if not m: continue
    sym, base, meaning, defsec, used, old, rec = m.groups()
    k = key_of(sym)
    if not k: continue
    found = [ch for ch in chap_files if k in texts[ch]]
    if used.strip()=="전 장": claimed = list(chap_files)
    else: claimed = re.findall(r'\d+', used)
    missing_claimed = [c for c in claimed if c not in found]
    extra_found = [c for c in found if c not in claimed]
    note=""
    if missing_claimed or extra_found:
        note = f"L{ln} {sym[:40]} key={k!r} 주장={claimed} 발견={found}"
        if missing_claimed: note += f" 주장했으나 미발견={missing_claimed}"
        if extra_found: note += f" 발견했으나 미주장={extra_found}"
        print(note)
