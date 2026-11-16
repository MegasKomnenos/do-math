# -*- coding: utf-8 -*-
import re, os, json, glob, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
BASE = r"C:\math\임시\주차함수_증명\장v2"
B = open(os.path.join(BASE,"부록B.md"),encoding='utf-8').read()
rows=[]
for ln in B.split('\n'):
    if ln.startswith('| r'):
        c=[x.strip() for x in ln.strip().strip('|').split('|')]
        rows.append(c)
print("부록 B 행 수:", len(rows))
folders = os.listdir(REC)
ids_B = [r[0] for r in rows]
for c in rows:
    rid, tm, title, folder = c[0], c[1], c[2], c[3].strip('`')
    ok_folder = folder in folders and folder.startswith(rid)
    p = os.path.join(REC, folder)
    info = ""
    if os.path.isdir(p):
        has_review = os.path.isdir(os.path.join(p,'review'))
        has_expo = os.path.isfile(os.path.join(p,'exposition.md'))
        has_json = os.path.isfile(os.path.join(p,'record.json'))
        has_evid = os.path.isdir(os.path.join(p,'evidence'))
        jt = ""
        ts = ""
        if has_json:
            try:
                j = json.load(open(os.path.join(p,'record.json'),encoding='utf-8'))
                jt = j.get('title') or j.get('name') or ''
                for k in ('created_at','created','timestamp','time','date'):
                    if k in j: ts = str(j[k]); break
                if not ts:
                    ts = str({k:v for k,v in j.items() if isinstance(v,str) and '2026' in v})[:120]
            except Exception as e: jt = f"json err {e}"
        info = f"review={has_review} expo={has_expo} json={has_json} evid={has_evid} ts={ts}\n      json제목: {jt[:160]}\n      표 제목: {title[:160]}"
    else:
        info = "** 폴더 없음 **"
    print(f"{rid} {tm} folder_ok={ok_folder} {info}")
# 본문·부록에서 인용된 식별자 전부
cited=set()
for f in glob.glob(os.path.join(BASE,"*.md")):
    if f.endswith("부록B.md"): continue
    t=open(f,encoding='utf-8').read()
    cited |= set(re.findall(r'\br([0-9a-f]{7})\b', t))
cited = {'r'+x for x in cited}
print("\n인용되었으나 부록 B에 없음:", sorted(cited-set(ids_B)))
print("부록 B에 있으나 어디에도 인용 없음:", sorted(set(ids_B)-cited))
# 시각 순서 확인
print("\n시각 순서:", [r[1] for r in rows] == sorted(rows, key=lambda r: r[1]) and "정렬됨" or "정렬 안 됨")
