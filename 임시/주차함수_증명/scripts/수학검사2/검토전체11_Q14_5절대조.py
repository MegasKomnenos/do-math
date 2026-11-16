# Q14: 장부 5절(장별 처음 정의 전역 기호·여유 글자)을 1.2(정의 절·쓰이는 장·바탕 글자)와 대조한다.
import re, os
root = r"C:\math\임시\주차함수_증명"
L = open(os.path.join(root,"장부_v2.md"), encoding="utf-8").read().splitlines()
BS = chr(92)
rows=[]
for i in range(42,339):
    m = re.match(r'^\| (\$.*?\$) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', L[i])
    if m:
        sym, base, meaning, defsec, used, old, rec = m.groups()
        rows.append((sym, base, defsec, used, i+1))
sec5={}
for i in range(1196,1208):
    m = re.match(r'^\| (\d+) \| (.*?) \| (.*?) \| (.*?) \|\s*$', L[i])
    if m: sec5[m.group(1)] = dict(globals=m.group(2), words=m.group(3), free=m.group(4))
def chapters_of_defsec(d):
    return set(re.findall(r'(?<![\d.])(\d+)\.\d', d))
for ch in map(str, range(1,12)):
    exp = [s for s,b,d,u,ln in rows if ch in chapters_of_defsec(d)]
    listed = sec5.get(ch,{}).get("globals","")
    listed_syms = [x.strip() for x in listed.split(";")] if listed and listed!="없음" else []
    missing = [s for s in exp if s not in listed_syms]
    extra = [s for s in listed_syms if s not in exp]
    if missing or extra:
        print(f"5절 {ch}장 전역 기호: 1.2 정의절 기준 기대하나 없음={missing}  5절에 있으나 1.2 정의절 불일치={extra}")
def face_of(base):
    b = base.split('·')
    return (b[0].strip(), '·'.join(b[1:]).strip())
faces_used = {ch:set() for ch in map(str,range(1,12))}
for sym,base,d,u,ln in rows:
    bf = face_of(base)
    chs = list(map(str,range(1,12))) if u.strip()=="전 장" else re.findall(r'\d+', u)
    for c in chs: faces_used[c].add(bf)
    if '1' in chapters_of_defsec(d):
        for c in faces_used: faces_used[c].add(bf)
def letters_in(txt):
    out=set()
    for t in re.findall(r'\$(.*?)\$', txt):
        t=t.strip()
        mm = re.match(r'^\\(mathcal|mathfrak|mathsf)\s*([A-Za-z])$', t)
        if mm: out.add((mm.group(2), {'mathcal':'필기체','mathfrak':'프락투어','mathsf':'산세리프'}[mm.group(1)]))
        elif re.match(r'^\\[A-Za-z]+$', t): out.add((t, '그리스'))
        elif re.match(r'^[A-Za-z]$', t): out.add((t,'이탤릭'))
    return out
for ch in map(str, range(1,12)):
    free = letters_in(sec5[ch]["free"])
    used=set()
    for (b,f) in faces_used[ch]:
        if '필기체' in f: used.add((b,'필기체'))
        elif '프락투어' in f: used.add((b,'프락투어'))
        elif '산세리프' in f: used.add((b,'산세리프'))
        elif '로마체' in f or '꼬리표' in f or '칠판체' in f: continue
        else: used.add((b, '그리스' if b.startswith(BS) else '이탤릭'))
    conflicts = sorted(free & used)
    if conflicts: print(f"5절 {ch}장 여유 글자 가운데 1.2 전역(쓰이는 장 기준)과 겹침: {conflicts}")
print("done")
