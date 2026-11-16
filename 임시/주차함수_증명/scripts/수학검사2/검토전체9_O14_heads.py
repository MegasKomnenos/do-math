# O14: 장 파일의 진술 머리를 뽑아 대응표·장부 4절·의존지도 1절과 대조한다.
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:/math/임시/주차함수_증명/"
CH = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
heads = []  # dict(label, type, name, status, chapter, sec, file, line, num)
counts = {}
for ch in CH:
    txt = open(BASE+"장v2/"+ch+".md", encoding='utf-8').read().split('\n')
    sec = None
    for i, line in enumerate(txt, 1):
        m = re.match(r'^### (\d+\.\d+(?:\.\d+)?)', line)
        if m: sec = m.group(1); continue
        m = re.match(r'^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([^}]+)\}\}(.*?)\.\*\*', line)
        if m:
            typ, chn, lab, rest = m.groups()
            if rest.strip().startswith('의 증명'): continue
            label = f"{{{{{chn}:{lab}}}}}"
            # name in first parentheses (balanced)
            name = None; status = None
            r = rest.strip()
            if r.startswith('('):
                depth=0
                for j,c in enumerate(r):
                    if c=='(': depth+=1
                    elif c==')':
                        depth-=1
                        if depth==0:
                            name = r[1:j]; r = r[j+1:].strip(); break
            mm = re.match(r'^\[(.*)\]$', r)
            if mm: status = mm.group(1)
            counts[chn] = counts.get(chn,0)+1
            heads.append(dict(label=label, type=typ, name=name, status=status, chn=chn, sec=sec, file=ch, line=i, num=f"{chn}.{counts[chn]}"))
print("heads:", len(heads))
H = {h['label']:h for h in heads}
# ---- 대응표
rows = {}
for line in open(BASE+"대조v2/라벨_번호_대응표_1114.md", encoding='utf-8'):
    m = re.match(r'^\| `(\{\{[^`]+\}\})` \| ([^|]+) \| (.*?) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$', line.strip())
    if m:
        rows[m.group(1)] = dict(type=m.group(2).strip(), name=m.group(3).strip(), num=m.group(4).strip(), old=m.group(5).strip(), sec=m.group(6).strip())
print("대응표 rows:", len(rows))
for lab,h in H.items():
    if lab not in rows: print("대응표에 없음:", lab, h['num'], h['file'], h['line'])
for lab,r in rows.items():
    if lab not in H: print("장 파일에 없음(대응표):", lab, r['num'])
    else:
        h=H[lab]
        if r['num']!=h['num']: print("번호 다름:", lab, "대응표", r['num'], "실제", h['num'])
        if r['type']!=h['type']: print("종류 다름:", lab, r['type'], h['type'])
        if r['sec']!=h['sec']: print("절 다름:", lab, "대응표", r['sec'], "실제", h['sec'])
        nm = h['name'] if h['name'] is not None else '—'
        if r['name']!=nm: print("이름 다름:", lab, "\n   대응표:", r['name'], "\n   실제:", nm)
# ---- 장부 4절
j4 = {}
in4=False
for line in open(BASE+"장부_v2.md", encoding='utf-8'):
    if line.startswith('## 4.'): in4=True; continue
    if line.startswith('## 5.'): in4=False
    if not in4: continue
    m = re.match(r'^\| ([^|]*) \| ([^|]*) \| (.*?) \| (.*?) \| ([^|]*) \| (\{\{[^}]+\}\}|\([^)]+\)|—) \|$', line.strip())
    if m:
        j4[m.group(6).strip()] = dict(old=m.group(1).strip(), type=m.group(2).strip(), name=m.group(3).strip(), rec=m.group(4).strip(), sec=m.group(5).strip())
print("장부4절 rows:", len(j4))
for lab,h in H.items():
    if lab not in j4: print("장부4절에 없음:", lab)
for lab,r in j4.items():
    if lab.startswith('{{'):
        if lab not in H: print("장 파일에 없음(장부4절):", lab)
        else:
            h=H[lab]
            if r['type']!=h['type']: print("4절 종류 다름:", lab, r['type'], h['type'])
            if r['sec']!=h['sec']: print("4절 절 다름:", lab, r['sec'], h['sec'])
            # name: head name = "이름; 기록 ..." ; 장부 splits into 이름 | 기록의 이름
            nm = h['name'] or ''
            parts = nm.split('; ',1)
            n1 = parts[0]; n2 = parts[1] if len(parts)>1 else ''
            if r['name']!=n1: print("4절 이름 다름:", lab, "\n   4절:", r['name'], "\n   실제:", n1)
            if r['rec']!=n2: print("4절 기록이름 다름:", lab, "\n   4절:", r['rec'], "\n   실제:", n2)
    else:
        # 뺌 행: label in parentheses -> ensure not in H
        inner = '{{'+lab[1:-1]+'}}' if lab.startswith('(') else None
        if inner and inner in H: print("뺌 행인데 장 파일에 있음:", lab)
# ---- 의존지도 1절
dj = {}
in1=False
for line in open(BASE+"의존지도_v2.md", encoding='utf-8'):
    if line.startswith('## 1.'): in1=True; continue
    if line.startswith('### 1.1'): in1=False
    if not in1: continue
    m = re.match(r'^\| `(\{\{[^`]+\}\})` \| ([^|]*) \| ([^|]*) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line.strip())
    if m:
        dj[m.group(1)] = dict(sec=m.group(2).strip(), old=m.group(3).strip(), name=m.group(4).strip(), status=m.group(5).strip(), inputs=m.group(6).strip())
print("의존지도 rows:", len(dj))
for lab,h in H.items():
    if lab not in dj: print("의존지도에 없음:", lab)
for lab,r in dj.items():
    if lab not in H: print("장 파일에 없음(의존지도):", lab); continue
    h=H[lab]
    if r['sec']!=h['sec']: print("의존지도 절 다름:", lab, r['sec'], h['sec'])
    st = h['status']
    if st is None: st_cmp='정의'
    else:
        st_cmp = st.split(';')[0].strip()
    if h['type']=='정의' and (st is None or ';' not in st): st_cmp='정의'
    if r['status']!=st_cmp: print("의존지도 지위 다름:", lab, "\n   지도:", r['status'], "\n   실제:", st_cmp)
    # declared deps
    decl = set(re.findall(r'\{\{\d+:[^}]+\}\}', st or ''))
    decl_j = set(re.findall(r'`(\{\{\d+:[^}]+\}\})`', r['inputs'].split('본문 인용:')[0]))
    if decl!=decl_j: print("의존지도 선언 의존 다름:", lab, "\n   지도:", sorted(decl_j), "\n   실제:", sorted(decl))
    nm = h['name'] or ''
    if h['type']!='정의' or True:
        if r['name']!=nm and not (nm=='' ): print("의존지도 요지 다름:", lab, "\n   지도:", r['name'], "\n   실제:", nm)
json.dump(heads, open(BASE+"scripts/수학검사2/_O14_heads.json","w",encoding='utf-8'), ensure_ascii=False, indent=0)
